# crisis_detector.py
# Purpose: Multi-signal crisis assessment for financial and mental health distress

import logging
from typing import Any, Dict, List, Mapping, Optional, Tuple

logger = logging.getLogger(__name__)

# ─── Escalation Tiers ────────────────────────────────────────
# Ordinal for merging: higher = more severe
_LEVEL_ORDER = {"Low Risk": 0, "Medium Risk": 1, "Immediate Crisis": 2}


def _merge_level(a: str, b: str) -> str:
    return a if _LEVEL_ORDER[a] >= _LEVEL_ORDER[b] else b


def _normalize_text(text: Optional[str]) -> str:
    if not text:
        return ""
    return text.casefold()


# ─── Keyword Groups ───────────────────────────────────────────
# Broad nets: prefer sensitivity over specificity (zero false negatives for crisis)
_IMMEDIATE_KEYWORD_GROUPS: Tuple[Tuple[str, Tuple[str, ...]], ...] = (
    (
        "self_harm_or_suicide_intent",
        (
            # English
            "suicide",
            "kill myself",
            "killing myself",
            "end my life",
            "end it all",
            "want to die",
            "better off dead",
            "no reason to live",
            "self harm",
            "self-harm",
            "cut myself",
            "hurt myself",
            "overdose",
            "hang myself",
            "jump off",
            "slit ",   # trailing space intentional: avoids partial matches (slitting, splits)
            # Hinglish / Roman Hindi
            "khudkhushi",
            "khud ko maar",
            "mar jaana",
            "marna hai",
            "jeene ka mann nahi",
            "zindagi khatam",
            "apni jaan",
            "khud par haath",
        ),
    ),
    (
        "indigenous_cultural_crisis_language",
        (
            "izzat mitti",
            "naak kat",
            "family ki izzat",
            "log kya kahenge",
            "society mein",
            "maa baap ko dukh",
            "parents ko shame",
            "loan default suicide",
            "recovery agents",
            "recovery agent",
            "threatening calls",
            "court notice loan",
            "ghar bech",
            "sell the house",
        ),
    ),
)

_MEDIUM_KEYWORD_GROUPS: Tuple[Tuple[str, Tuple[str, ...]], ...] = (
    (
        "hopelessness_and_shame",
        (
            "hopeless",
            "can't cope",
            "cannot cope",
            "worthless",
            "burden",
            "ashamed",
            "shame",
            "trapped",
            "helpless",
            "giving up",
            "no point",
            "empty inside",
            "drowning in debt",
            "emi stress",
            "can't pay emi",
            "loan shame",
            "secret debt",
            "maa ko nahi bata",
            "family ko batana mushkil",
            "family pressure",
            "expectations family",
            "marriage pressure",
            "majboor",
            "majburi",
            "bezati",
            "beizzati",
        ),
    ),
)

# ─── Behavioral Flags ─────────────────────────────────────────
_IMMEDIATE_BEHAVIOR_FLAGS = frozenset({
    "suicide_plan_or_means",
    "self_harm_recent",
    "giving_away_valuables",
    "writing_goodbye_messages",
    "sudden_calm_after_severe_distress",
})

_MEDIUM_BEHAVIOR_FLAGS = frozenset({
    "social_withdrawal_weeks",
    "sleep_disturbance_severe",
    "substance_increase",
    "work_or_academic_collapse",
    "panic_or_dissociation_spells",
})

# ─── Alert Text ───────────────────────────────────────────────
# ✅ Fixed — module-level constant, not rebuilt on every call
_FIN_ALERT_TEXT: Dict[str, str] = {
    "financial:expenses_meet_or_exceed_income": (
        "Immediate Crisis: Monthly spending meets or exceeds income — "
        "high financial and mental strain."
    ),
    "financial:spending_without_positive_income": (
        "Immediate Crisis: Spending with no positive income — "
        "urgent stabilisation needed."
    ),
    "financial:savings_rate_below_10_percent": (
        "Medium Risk: Savings below 10% — very little buffer for shocks "
        "(including family or social stress)."
    ),
    "financial:debt_exceeds_twice_monthly_income": (
        "Immediate Crisis: Debt is more than twice monthly income — "
        "repayment pressure can feel unbearable "
        "(including shame or fear of family knowing)."
    ),
    "financial:negative_cashflow_with_outstanding_debt": (
        "Immediate Crisis: Negative monthly cash flow with outstanding debt — "
        "compounding distress risk."
    ),
}

# ✅ Added — Indian helplines shown on Immediate Crisis
_HELPLINE_FOOTER = (
    "📞 Free helplines (India): "
    "iCall 9152987821 | "
    "Vandrevala Foundation 1860-2662-345 (24x7)"
)


# ─── Internal Evaluators ──────────────────────────────────────
def _scan_keywords(text_norm: str) -> Tuple[str, List[str]]:
    level = "Low Risk"
    hits : List[str] = []

    for gid, phrases in _IMMEDIATE_KEYWORD_GROUPS:
        for p in phrases:
            if p in text_norm:
                level = _merge_level(level, "Immediate Crisis")
                hits.append(f"keyword:{gid}:{p}")
                break   # one hit per group is enough for level; avoids duplicate escalation

    for gid, phrases in _MEDIUM_KEYWORD_GROUPS:
        for p in phrases:
            if p in text_norm:
                level = _merge_level(level, "Medium Risk")
                hits.append(f"keyword:{gid}:{p}")
                break

    return level, hits


def _evaluate_behavioral(
    behavioral_signals: Optional[Mapping[str, Any]],
) -> Tuple[str, List[str]]:
    if not behavioral_signals:
        return "Low Risk", []

    level = "Low Risk"
    hits : List[str] = []

    for k, v in behavioral_signals.items():
        if not v:
            continue
        key = str(k)
        if key in _IMMEDIATE_BEHAVIOR_FLAGS:
            level = _merge_level(level, "Immediate Crisis")
            hits.append(f"behavior:immediate:{key}")
        elif key in _MEDIUM_BEHAVIOR_FLAGS:
            level = _merge_level(level, "Medium Risk")
            hits.append(f"behavior:medium:{key}")

    # Stacking: multiple medium behavioral flags escalate to Immediate
    medium_only = [h for h in hits if h.startswith("behavior:medium:")]
    if len(medium_only) >= 2:
        level = _merge_level(level, "Immediate Crisis")
        hits.append("behavior:pattern:multiple_medium_flags")

    return level, hits


def _evaluate_financial(
    income  : float,
    expenses: Mapping[str, float],
    debt    : float,
) -> Tuple[str, List[str], float, float]:
    """Preserves all legacy financial triggers with no softening."""
    total_expenses = sum(expenses.values())
    savings        = income - total_expenses
    savings_rate   = (savings / income) * 100 if income > 0 else 0.0
    level          = "Low Risk"
    signals        : List[str] = []

    if income > 0 and total_expenses >= income:
        level = _merge_level(level, "Immediate Crisis")
        signals.append("financial:expenses_meet_or_exceed_income")

    if income <= 0 and total_expenses > 0:
        level = _merge_level(level, "Immediate Crisis")
        signals.append("financial:spending_without_positive_income")

    if income > 0 and savings_rate < 10:
        level = _merge_level(level, "Medium Risk")
        signals.append("financial:savings_rate_below_10_percent")

    if income > 0 and debt > income * 2:
        level = _merge_level(level, "Immediate Crisis")
        signals.append("financial:debt_exceeds_twice_monthly_income")

    if income > 0 and debt > 0 and savings < 0:
        level = _merge_level(level, "Immediate Crisis")
        signals.append("financial:negative_cashflow_with_outstanding_debt")

    return level, signals, savings, savings_rate


# ─── Public API ───────────────────────────────────────────────
def detect_crisis(
    income             : float,
    expenses           : Mapping[str, float],
    debt               : float = 0,
    text               : Optional[str] = None,
    behavioral_signals : Optional[Mapping[str, Any]] = None,
) -> Dict:
    """
    Multi-signal crisis assessment: financial, keyword, and behavioral.
    Defaults keep legacy financial-only usage safe when text/behavior omitted.

    Returns:
        dict with keys: level, alerts, savings, savings_rate, signals
    """
    fin_level,  fin_signals, savings, savings_rate = _evaluate_financial(
        income, expenses, debt
    )
    kw_level,  kw_hits  = _scan_keywords(_normalize_text(text))
    beh_level, beh_hits = _evaluate_behavioral(behavioral_signals)

    # Merge all three domains
    combined = "Low Risk"
    for part in (fin_level, kw_level, beh_level):
        combined = _merge_level(combined, part)

    # Cross-signal escalation: medium in 2+ domains → Immediate (sensitivity-first)
    domains_at_medium_or_worse = sum(
        1 for lbl in (fin_level, kw_level, beh_level)
        if _LEVEL_ORDER[lbl] >= _LEVEL_ORDER["Medium Risk"]
    )
    if domains_at_medium_or_worse >= 2:
        combined = _merge_level(combined, "Immediate Crisis")

    # ✅ Fixed — log every escalation for safety audit trail
    if combined == "Immediate Crisis":
        logger.warning(
            f"IMMEDIATE CRISIS DETECTED — "
            f"financial={fin_signals} | "
            f"keywords={kw_hits} | "
            f"behavioral={beh_hits}"
        )
    elif combined == "Medium Risk":
        logger.info(
            f"Medium Risk flagged — "
            f"financial={fin_signals} | "
            f"keywords={kw_hits} | "
            f"behavioral={beh_hits}"
        )
    else:
        logger.debug("Crisis check passed — Low Risk")

    # Build alert messages
    alerts: List[str] = []

    if fin_signals:
        alerts.extend(_FIN_ALERT_TEXT[s] for s in fin_signals)

    if kw_hits:
        alerts.append(
            "Language matched crisis-related patterns — "
            "treat as serious until assessed by a qualified professional."
        )

    if beh_hits:
        alerts.append(
            "Behavioral risk signals present — "
            "escalate per your safety protocol."
        )

    # ✅ Added — helpline footer for Immediate Crisis
    if combined == "Immediate Crisis":
        alerts.append(_HELPLINE_FOOTER)

    if combined == "Low Risk" and not alerts:
        alerts.append(
            "Low Risk: No crisis signals detected from finance, "
            "text, and behavior in this pass."
        )

    return {
        "level"      : combined,
        "alerts"     : alerts,
        "savings"    : savings,
        "savings_rate": round(savings_rate, 2),
        "signals"    : {
            "financial" : fin_signals,
            "keywords"  : kw_hits,
            "behavioral": beh_hits,
        },
    }


# ─── Standalone Test ─────────────────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Test 1: Financial stress only
    result = detect_crisis(
        income   = 10000,
        expenses = {
            "Food"         : 3000,
            "Transport"    : 500,
            "Education"    : 1000,
            "Entertainment": 3000,
            "Others"       : 1000,
        },
        debt = 500,
    )
    print(f"Test 1 — Level: {result['level']}")
    for a in result["alerts"]:
        print(f"  {a}")

    # Test 2: Keyword escalation
    result2 = detect_crisis(
        income   = 15000,
        expenses = {"Food": 5000, "Others": 3000},
        debt     = 0,
        text     = "I feel so hopeless, can't cope with this loan shame anymore",
    )
    print(f"\nTest 2 — Level: {result2['level']}")
    for a in result2["alerts"]:
        print(f"  {a}")

    # Test 3: Immediate crisis via keywords
    result3 = detect_crisis(
        income   = 10000,
        expenses = {"Food": 3000},
        text     = "I want to end my life because of this debt",
    )
    print(f"\nTest 3 — Level: {result3['level']}")
    for a in result3["alerts"]:
        print(f"  {a}")

    # Test 4: Cross-domain escalation (2x medium → immediate)
    result4 = detect_crisis(
        income   = 10000,
        expenses = {"Food": 9500},   # savings_rate < 10 → medium financial
        text     = "feeling so ashamed and helpless",  # medium keyword
    )
    print(f"\nTest 4 — Level: {result4['level']} (expected: Immediate Crisis)")