# crisis_detector.py
# Purpose: Multi-signal crisis assessment for financial and mental health distress
# Enhanced: Predatory Loan Blacklist, Behavioral Loop Detection, Temporal Risk Check

import logging
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Mapping, Optional, Tuple

logger = logging.getLogger(__name__)

# ─── Escalation Tiers (4-tier system) ────────────────────────
# Normal → Watch → Alert → Emergency
_LEVEL_ORDER = {
    "Normal": 0, "Watch": 1, "Alert": 2, "Emergency": 3,
    # Backward compat aliases
    "Low Risk": 0, "Medium Risk": 1, "Immediate Crisis": 3,
}

# Canonical tier names for new code
TIER_NORMAL = "Normal"
TIER_WATCH = "Watch"
TIER_ALERT = "Alert"
TIER_EMERGENCY = "Emergency"


def _merge_level(a: str, b: str) -> str:
    return a if _LEVEL_ORDER.get(a, 0) >= _LEVEL_ORDER.get(b, 0) else b


# ─── Load Predatory Loan Blacklist ────────────────────────────
_BLACKLIST_PATH = os.path.join(os.path.dirname(__file__), "data", "loan_blacklist.json")
_LOAN_BLACKLIST: List[Dict] = []
try:
    with open(_BLACKLIST_PATH, "r", encoding="utf-8") as f:
        _LOAN_BLACKLIST = json.load(f)
    logger.info(f"Loaded {len(_LOAN_BLACKLIST)} predatory loan entries from blacklist.")
except FileNotFoundError:
    logger.warning(f"loan_blacklist.json not found at {_BLACKLIST_PATH}")
except Exception as e:
    logger.warning(f"Failed to load loan blacklist: {e}")


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


# ─── Desperation Keywords ─────────────────────────────────────
_DESPERATION_KEYWORDS = (
    "threats", "threatening", "contacts calling", "blackmail",
    "morphed photos", "betting loss", "gambling loss", "hopeless",
    "harassment", "agents calling", "calling my family", "calling my contacts",
    "sharing my photos", "defaming me", "nude photos", "leaked photos",
)

# ─── NEW: Predatory Loan Blacklist Scanner ────────────────────
def _check_blacklist_and_desperation(text_norm: str) -> Tuple[str, List[str], List[Dict]]:
    """Scan text against loan_blacklist.json and desperation keywords."""
    level = TIER_NORMAL
    hits: List[str] = []
    matched_apps: List[Dict] = []

    # Check against blacklist
    for entry in _LOAN_BLACKLIST:
        app_lower = entry["app_name"].casefold()
        if app_lower in text_norm:
            level = _merge_level(level, TIER_ALERT)
            hits.append(f"blacklist:app_match:{entry['app_name']}")
            matched_apps.append(entry)

    # Check desperation keywords
    desp_count = 0
    for kw in _DESPERATION_KEYWORDS:
        if kw in text_norm:
            desp_count += 1
            hits.append(f"desperation:{kw}")

    if desp_count >= 2:
        level = _merge_level(level, TIER_EMERGENCY)
    elif desp_count >= 1:
        level = _merge_level(level, TIER_ALERT)

    # Blacklist + desperation combo → Emergency
    if matched_apps and desp_count >= 1:
        level = _merge_level(level, TIER_EMERGENCY)
        hits.append("combo:blacklist_app_with_desperation")

    return level, hits, matched_apps


# ─── NEW: Behavioral Debt-Loop Parser ────────────────────────
_LOOP_PHRASES = (
    "took a loan to pay a loan",
    "new loan to clear old loan",
    "borrowing to repay",
    "loan to pay loan",
    "one loan to pay another",
    "another loan to cover",
    "borrowed to pay back",
    "taking loan to pay emi",
    "loan se loan",
    "ek loan doosra loan",
    "naya loan purana loan",
    "loan cycle",
    "debt cycle",
    "debt trap",
    "loan pe loan",
    "loan par loan",
)

def _check_behavioral_loop(text_norm: str) -> Tuple[str, List[str]]:
    """Detect debt-cycling behavior from user text."""
    level = TIER_NORMAL
    hits: List[str] = []

    for phrase in _LOOP_PHRASES:
        if phrase in text_norm:
            level = _merge_level(level, TIER_ALERT)
            hits.append(f"loop:{phrase}")

    # Multiple loop phrases → Emergency
    if len(hits) >= 2:
        level = _merge_level(level, TIER_EMERGENCY)
        hits.append("loop:multiple_debt_cycle_indicators")

    return level, hits


# ─── NEW: Temporal Risk Check ─────────────────────────────────
_PANIC_GAMBLING_KEYWORDS = (
    "panic", "panicking", "scared", "terrified", "can't sleep",
    "gambling", "betting", "lost money", "lost everything",
    "dream11", "fantasy app", "satta", "matka", "casino",
    "what do i do", "help me", "kya karu", "dar lag raha",
)

def _check_temporal(text_norm: str, timestamp: Optional[datetime] = None) -> Tuple[str, List[str]]:
    """Flag late-night (11 PM - 3 AM) panic or gambling interactions."""
    now = timestamp or datetime.now()
    hour = now.hour
    is_high_risk_hour = (hour >= 23 or hour < 3)

    level = TIER_NORMAL
    hits: List[str] = []

    if not is_high_risk_hour:
        return level, hits

    for kw in _PANIC_GAMBLING_KEYWORDS:
        if kw in text_norm:
            hits.append(f"temporal:late_night:{kw}")

    if len(hits) >= 2:
        level = _merge_level(level, TIER_EMERGENCY)
        hits.append("temporal:high_risk_hour_with_multiple_panic_keywords")
    elif len(hits) >= 1:
        level = _merge_level(level, TIER_ALERT)
        hits.append("temporal:high_risk_hour_with_panic_keyword")

    return level, hits


# ─── Crisis Hotlines (Emergency tier) ─────────────────────────
_CRISIS_HOTLINES = [
    {"name": "iCall", "number": "9152987821", "hours": "Mon-Sat 8AM-10PM"},
    {"name": "Vandrevala Foundation", "number": "1860-2662-345", "hours": "24x7"},
    {"name": "AASRA", "number": "9820466726", "hours": "24x7"},
    {"name": "National Cyber Crime", "number": "1930", "hours": "24x7"},
    {"name": "NALSA Legal Aid", "number": "15100", "hours": "24x7"},
]

# ─── Public API ───────────────────────────────────────────────
def detect_crisis(
    income             : float,
    expenses           : Mapping[str, float],
    debt               : float = 0,
    text               : Optional[str] = None,
    behavioral_signals : Optional[Mapping[str, Any]] = None,
    timestamp          : Optional[datetime] = None,
) -> Dict:
    """
    Multi-signal crisis assessment: financial, keyword, behavioral,
    predatory loan blacklist, debt-loop detection, and temporal risk.

    Returns:
        dict with keys: level, alerts, savings, savings_rate, signals,
                        hotlines (on Emergency), matched_apps (if any)
    """
    text_norm = _normalize_text(text)

    # Legacy evaluators
    fin_level,  fin_signals, savings, savings_rate = _evaluate_financial(
        income, expenses, debt
    )
    kw_level,  kw_hits  = _scan_keywords(text_norm)
    beh_level, beh_hits = _evaluate_behavioral(behavioral_signals)

    # NEW scanners
    bl_level, bl_hits, matched_apps = _check_blacklist_and_desperation(text_norm)
    loop_level, loop_hits = _check_behavioral_loop(text_norm)
    temp_level, temp_hits = _check_temporal(text_norm, timestamp)

    # Merge all six domains
    combined = TIER_NORMAL
    for part in (fin_level, kw_level, beh_level, bl_level, loop_level, temp_level):
        combined = _merge_level(combined, part)

    # Cross-signal escalation: 2+ domains at Watch or worse → Emergency
    domains_at_watch_or_worse = sum(
        1 for lbl in (fin_level, kw_level, beh_level, bl_level, loop_level, temp_level)
        if _LEVEL_ORDER.get(lbl, 0) >= _LEVEL_ORDER[TIER_WATCH]
    )
    if domains_at_watch_or_worse >= 2:
        combined = _merge_level(combined, TIER_EMERGENCY)

    # Logging
    if combined == TIER_EMERGENCY:
        logger.warning(
            f"EMERGENCY DETECTED — "
            f"financial={fin_signals} | keywords={kw_hits} | "
            f"behavioral={beh_hits} | blacklist={bl_hits} | "
            f"loops={loop_hits} | temporal={temp_hits}"
        )
    elif combined in (TIER_ALERT, TIER_WATCH):
        logger.info(
            f"{combined} flagged — "
            f"financial={fin_signals} | keywords={kw_hits} | "
            f"blacklist={bl_hits} | loops={loop_hits} | temporal={temp_hits}"
        )
    else:
        logger.debug("Crisis check passed — Normal")

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

    if bl_hits:
        app_names = [a["app_name"] for a in matched_apps]
        if app_names:
            alerts.append(f"Predatory loan app detected: {', '.join(app_names)}. "
                          "Do NOT pay additional fees. Report immediately.")
        else:
            alerts.append("Desperation language detected — user may be under coercion.")

    if loop_hits:
        alerts.append("Debt-cycling behavior detected — user may be trapped in a loan loop.")

    if temp_hits:
        alerts.append("Late-night distress interaction detected — elevated risk window.")

    # Helpline footer for Emergency
    if combined == TIER_EMERGENCY:
        alerts.append(_HELPLINE_FOOTER)

    if combined == TIER_NORMAL and not alerts:
        alerts.append(
            "Normal: No crisis signals detected from finance, "
            "text, and behavior in this pass."
        )

    result = {
        "level"      : combined,
        "alerts"     : alerts,
        "savings"    : savings,
        "savings_rate": round(savings_rate, 2),
        "signals"    : {
            "financial" : fin_signals,
            "keywords"  : kw_hits,
            "behavioral": beh_hits,
            "blacklist" : bl_hits,
            "loops"     : loop_hits,
            "temporal"  : temp_hits,
        },
    }

    # Attach hotlines and matched apps on Emergency
    if combined == TIER_EMERGENCY:
        result["hotlines"] = _CRISIS_HOTLINES
    if matched_apps:
        result["matched_apps"] = matched_apps

    return result


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