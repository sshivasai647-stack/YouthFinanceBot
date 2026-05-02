"""
situation_detector.py
=====================
Entry point router for Youth Financial Guardian Chatbot.
Detects user's financial situation and routes to the correct path.

Paths:
    A/B/C → zero_investment_path.py   (Earning with no/small/medium money)
    D     → debt_handler.py           (In debt / struggling)
    E     → betting_alternative.py    (Gambling / betting addiction)
    F     → mental_health_guardian.py (Mental health crisis)
    G     → statement_analyzer.py     (Expense tracking)
    H     → investment_guide.py       (Ready to invest)

Author: Youth Financial Guardian Project
Compliance: DPDPA 2023 — no PII stored beyond session
"""

import re
from dataclasses import dataclass
from typing import Optional

# ─────────────────────────────────────────────
# 1. PATH CONSTANTS
# ─────────────────────────────────────────────

PATH_ZERO_INVESTMENT = "PATH_A_B_C"   # No/small/medium money — earn first
PATH_DEBT            = "PATH_D"        # In debt / loan trap
PATH_BETTING         = "PATH_E"        # Gambling / betting addiction
PATH_MENTAL_HEALTH   = "PATH_F"        # Crisis / overwhelmed / shame
PATH_EXPENSE         = "PATH_G"        # Track & manage expenses
PATH_INVEST          = "PATH_H"        # Stable income, ready to grow
PATH_UNKNOWN         = "PATH_UNKNOWN"  # Needs clarification

# ─────────────────────────────────────────────
# 2. KEYWORD BANKS
# ─────────────────────────────────────────────

# PATH F — Mental health crisis (checked FIRST — always top priority)
CRISIS_KEYWORDS = [
    # English
    "want to die", "end my life", "kill myself", "suicide", "no point living",
    "can't go on", "worthless", "hopeless", "i give up", "nothing left",
    "can't take it anymore", "rather be dead", "disappear forever",
    # Hindi transliterated
    "marna chahta", "marna chahti", "jeena nahi", "zindagi nahi chahiye",
    "khatam karna chahta", "khatam karna chahti",
    # Telugu transliterated
    "chachipovalanam", "badukuteledhu", "naku em ledu",
    # Shame + financial despair combo signals
    "family will hate me", "ruined everything", "destroyed my family",
    "can't face anyone", "too ashamed", "no way out"
]

# PATH E — Betting / gambling
BETTING_KEYWORDS = [
    "dream11", "mpl", "my11circle", "fantasy cricket", "fantasy football",
    "betting", "gambling", "satta", "matka", "cricket bet", "ipl bet",
    "sports bet", "losing on games", "lost on dream", "fantasy team",
    "daily fantasy", "winzo loss", "real money game loss",
    "jua", "jugad bet", "online casino", "teen patti real money",
    "rummy cash", "losing streaks", "can't stop betting", "addicted to fantasy",
    # ✅ Added: popular Indian real-money gaming apps
    "rummy", "poker", "ludo real money", "zupee", "gamezy", "ballebaazi",
    "halaplay", "8ball pool", "qudos",
]

# PATH D — Debt / loan trap
DEBT_KEYWORDS = [
    "loan", "emi", "debt", "borrow", "borrowed", "interest", "installment",
    "due date", "overdue", "loan app", "instant loan", "personal loan",
    "unable to pay", "can't pay", "defaulted", "recovery agent", "harassment",
    "threatening", "nbfc", "moneylender", "sahukaar", "karz", "udhar",
    "qarz", "debt trap", "loan shark", "illegal loan", "rbi sachet",
    "cheating by loan app", "data misuse by app", "contacts threatened",
    "photos threatened", "blackmail loan"
]

# PATH G — Expense tracking
EXPENSE_KEYWORDS = [
    "track", "spending", "expense", "budget", "bank statement", "upi",
    "where did my money go", "overspending", "monthly expenses",
    "categorize", "upload statement", "pdf statement", "paytm history",
    "gpay history", "phonepe history", "money going", "leaking money",
    "wasting money", "salary finish", "salary khatam"
]

# PATH H — Ready to invest
INVEST_KEYWORDS = [
    "invest", "sip", "mutual fund", "nifty", "sensex", "stocks", "shares",
    "zerodha", "groww", "upstox", "crypto", "bitcoin", "nft", "gold bond",
    "fd", "fixed deposit", "ppf", "elss", "index fund", "portfolio",
    "wealth", "grow money", "long term", "retirement", "passive income",
    "dividend", "equity", "debt fund", "asset allocation"
]

# PATH A/B/C — Earning / no money
EARN_KEYWORDS = [
    "no money", "earn online", "side hustle", "freelance",
    "no job", "unemployed", "student", "broke", "paisa nahi", "paise nahi",
    "need money", "make money", "work from home",
    "part time", "gig", "resell", "dropship", "youtube", "content creator",
    "hackathon", "zero investment", "no investment", "small investment",
    "500 rupees", "1000 rupees", "2000 rupees", "meesho", "shopsy"
]

# ─────────────────────────────────────────────
# 3. RESULT DATACLASS
# ─────────────────────────────────────────────

@dataclass
class DetectionResult:
    path                 : str
    confidence           : float           # 0.0 – 1.0
    triggers             : list[str]       # keywords that fired
    is_crisis            : bool = False    # True if PATH_F detected
    clarification_needed : bool = False
    suggested_question   : Optional[str] = None
    display_message      : str = ""        # Human-readable routing message
    secondary_path       : Optional[str] = None  # If dual signals detected


# ─────────────────────────────────────────────
# 4. CORE DETECTOR
# ─────────────────────────────────────────────

def detect_situation(user_input: str) -> DetectionResult:
    """
    Analyse user's free-text input and route to the correct path.

    Priority order (hard-coded for safety):
        1. Mental health crisis  (PATH F)
        2. Debt / loan trap      (PATH D)
        3. Betting / gambling    (PATH E)
        4. Expense tracking      (PATH G)
        5. Investment ready      (PATH H)
        6. Earning / no money    (PATH A/B/C)
        7. Unknown               (needs clarification)

    Args:
        user_input: Raw text from user (any language, transliterated OK)

    Returns:
        DetectionResult with path, confidence, triggers
    """
    if not user_input or not user_input.strip():
        return DetectionResult(
            path                 = PATH_UNKNOWN,
            confidence           = 0.0,
            triggers             = [],
            clarification_needed = True,
            suggested_question   = _get_onboarding_question(),
            display_message      = "Let me understand your situation first."
        )

    # ✅ Input length cap — prevents abuse / slow scans
    user_input = user_input[:2000]

    text = user_input.lower().strip()
    # Remove special characters but keep spaces
    text = re.sub(r"[^\w\s]", " ", text)
    # ✅ Normalize whitespace — "want  to  die" still matches
    text = re.sub(r"\s+", " ", text).strip()

    # ── PRIORITY 1: Crisis check (always first) ──────────────────────
    crisis_hits = _match_keywords(text, CRISIS_KEYWORDS)
    if crisis_hits:
        return DetectionResult(
            path            = PATH_MENTAL_HEALTH,
            confidence      = 1.0,
            triggers        = crisis_hits,
            is_crisis       = True,
            display_message = (
                "I hear you. Before anything else — you matter more than any "
                "financial problem. Let me connect you with support right now."
            )
        )

    # ── Score all other paths ─────────────────────────────────────────
    scores = {
        PATH_DEBT            : _score(text, DEBT_KEYWORDS),
        PATH_BETTING         : _score(text, BETTING_KEYWORDS),
        PATH_EXPENSE         : _score(text, EXPENSE_KEYWORDS),
        PATH_INVEST          : _score(text, INVEST_KEYWORDS),
        PATH_ZERO_INVESTMENT : _score(text, EARN_KEYWORDS),
    }

    top_path  = max(scores, key=lambda k: scores[k]["score"])
    top_score = scores[top_path]["score"]
    top_hits  = scores[top_path]["hits"]

    # ── Dual signal detection ─────────────────────────────────────────
    sorted_scores  = sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True)
    secondary_path = None
    if len(sorted_scores) >= 2:
        second_score = sorted_scores[1][1]["score"]
        # ✅ Flag ANY two high-scoring paths — not just debt+betting
        if second_score > 0 and top_score > 0:
            secondary_path = sorted_scores[1][0]

    # ── No match ─────────────────────────────────────────────────────
    if top_score == 0:
        return DetectionResult(
            path                 = PATH_UNKNOWN,
            confidence           = 0.0,
            triggers             = [],
            clarification_needed = True,
            suggested_question   = _get_onboarding_question(),
            display_message      = "Tell me a bit more so I can help you better."
        )

    # ── Confidence ───────────────────────────────────────────────────
    confidence          = min(top_score / 5.0, 1.0)   # 5+ hits = 100%
    needs_clarification = confidence < 0.4

    return DetectionResult(
        path                 = top_path,
        confidence           = round(confidence, 2),
        triggers             = top_hits,
        is_crisis            = False,
        clarification_needed = needs_clarification,
        suggested_question   = _get_clarification_question(top_path) if needs_clarification else None,
        secondary_path       = secondary_path,
        display_message      = _get_routing_message(top_path, needs_clarification)
    )


# ─────────────────────────────────────────────
# 5. HELPER FUNCTIONS
# ─────────────────────────────────────────────

def _match_keywords(text: str, keywords: list[str]) -> list[str]:
    """Return list of keywords found in text."""
    return [kw for kw in keywords if kw in text]


def _score(text: str, keywords: list[str]) -> dict:
    """Return hit count and matched keywords for a keyword bank."""
    hits = _match_keywords(text, keywords)
    return {"score": len(hits), "hits": hits}


def _get_routing_message(path: str, needs_clarification: bool) -> str:
    """Return a warm, human routing message for each path."""
    messages = {
        PATH_DEBT: (
            "It sounds like you're dealing with a debt situation. "
            "You're not alone — let's find a way out together."
        ),
        PATH_BETTING: (
            "I noticed some mentions of betting or fantasy sports. "
            "Let me show you smarter ways to use that competitive energy."
        ),
        PATH_EXPENSE: (
            "Let's take a clear look at where your money is going. "
            "Upload your bank statement and I'll break it down for you."
        ),
        PATH_INVEST: (
            "Great — you're ready to grow your money. "
            "Let's build a safe, smart investment plan for you."
        ),
        PATH_ZERO_INVESTMENT: (
            "Let's find you real earning opportunities — "
            "whether you're starting from zero or have a little to invest."
        ),
        PATH_MENTAL_HEALTH: (
            "I hear you. You matter more than any financial problem right now."
        ),
        PATH_UNKNOWN: (
            "Tell me a bit more about your situation so I can help you best."
        ),
    }
    base = messages.get(path, "Let me help you with that.")
    if needs_clarification:
        base += " Just to make sure I guide you correctly — can I ask one quick question?"
    return base


def _get_clarification_question(path: str) -> str:
    """Return a single clarifying question when confidence is low."""
    questions = {
        PATH_DEBT            : "Are you currently struggling to repay a loan or EMI?",
        PATH_BETTING         : "Have you been spending money on fantasy sports or betting apps recently?",
        PATH_EXPENSE         : "Would you like to upload your bank statement to track your spending?",
        PATH_INVEST          : "Do you currently have savings set aside that you'd like to invest?",
        PATH_ZERO_INVESTMENT : "Are you looking for ways to earn money, starting from little or nothing?",
        PATH_UNKNOWN         : "What's the main financial challenge you're facing right now?",
    }
    return questions.get(path, "Can you tell me more about your situation?")


def _get_onboarding_question() -> str:
    """First question shown to a brand-new user."""
    return (
        "Hi! I'm your Financial Guardian. To help you best, "
        "can you tell me — what's your biggest money challenge right now? "
        "(e.g. debt, saving, earning, investing, or something else)"
    )


# ─────────────────────────────────────────────
# 6. STREAMLIT-READY ROUTER FUNCTION
# ─────────────────────────────────────────────

def route_user(user_input: str) -> dict:
    """
    Streamlit-friendly wrapper. Returns a plain dict for easy st.session_state use.

    Usage in app.py:
        from situation_detector import route_user
        result = route_user(user_message)
        st.session_state["current_path"] = result["path"]
    """
    result = detect_situation(user_input)
    return {
        "path"                : result.path,
        "confidence"          : result.confidence,
        "triggers"            : result.triggers,
        "is_crisis"           : result.is_crisis,
        "clarification_needed": result.clarification_needed,
        "suggested_question"  : result.suggested_question,
        "secondary_path"      : result.secondary_path,
        "display_message"     : result.display_message,
    }


# ─────────────────────────────────────────────
# 7. QUICK TEST (run directly: python situation_detector.py)
# ─────────────────────────────────────────────

if __name__ == "__main__":
    test_inputs = [
        "I have a loan I can't repay and recovery agents are calling me",
        "I keep losing money on Dream11 and MPL, can't stop",
        "I want to die, I've ruined everything with my debt",
        "Can you help me track my expenses and upload my bank statement?",
        "I have ₹5000 saved, want to start SIP on Groww",
        "I'm a student with no money, how do I earn online?",
        "Hello",
        "मेरे पास loan है और EMI नहीं भर पा रहा",
    ]

    print("=" * 60)
    print("SITUATION DETECTOR — TEST RUN")
    print("=" * 60)

    for inp in test_inputs:
        result = detect_situation(inp)
        print(f"\nInput     : {inp[:60]}")
        print(f"Path      : {result.path}")
        print(f"Confidence: {result.confidence:.0%}")
        print(f"Crisis    : {result.is_crisis}")
        print(f"Triggers  : {result.triggers[:3]}")
        print(f"Message   : {result.display_message[:80]}")
        if result.secondary_path:
            print(f"Secondary : {result.secondary_path}")
        if result.clarification_needed:
            print(f"Ask       : {result.suggested_question}")
        print("-" * 40)