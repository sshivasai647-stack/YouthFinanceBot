"""
mental_health_guardian.py
=========================
Mental Health & Crisis Support Module for Youth Financial Guardian Chatbot.

Handles:
    - Suicidal ideation / crisis (PATH F — highest priority)
    - Financial shame & despair (separate gentler response)
    - Multilingual: English + Hindi + Telugu transliterated
    - Post-crisis gentle re-routing back to financial help

Helplines:
    iCall        — 9152987821       (TISS, free, Mon–Sat 8am–10pm)
    Vandrevala   — 1860-2662-345    (24/7, free)
    AASRA        — 9820466627       (24/7)

Author: Youth Financial Guardian Project
Compliance: DPDPA 2023 — no PII stored beyond session
Safety Note: This module uses pre-written scripts for crisis,
             AI only for post-stabilization follow-up.
"""

import logging
from dataclasses import dataclass
from typing import Optional
from enum import Enum

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# 1. CRISIS LEVEL ENUM
# ─────────────────────────────────────────────

class CrisisLevel(Enum):
    SUICIDAL      = "suicidal"       # Immediate danger — helplines first
    SHAME_DESPAIR = "shame_despair"  # Financial shame — gentler response
    OVERWHELMED   = "overwhelmed"    # Stressed but stable — supportive
    STABLE        = "stable"         # Emotional, ready to talk finances


# ─────────────────────────────────────────────
# 2. KEYWORD BANKS
# ─────────────────────────────────────────────

SUICIDAL_KEYWORDS = [
    # English
    "want to die", "end my life", "kill myself", "suicide", "no point living",
    "can't go on", "rather be dead", "disappear forever", "end it all",
    "not worth living", "wish i was dead", "better off dead",
    # Hindi transliterated
    "marna chahta", "marna chahti", "jeena nahi", "zindagi nahi chahiye",
    "khatam karna chahta", "khatam karna chahti", "mar jaana chahta",
    "mar jaana chahti", "jeene ki ichha nahi",
    # Telugu transliterated
    "chachipovalani", "bathukuteledhu", "naku em ledu",
    "chaavu kavali", "paripovadam better",
]

SHAME_KEYWORDS = [
    # English
    "family will hate me", "ruined everything", "destroyed my family",
    "can't face anyone", "too ashamed", "everyone will know",
    "i'm a failure", "let everyone down", "embarrassed", "disgraced",
    "my parents will disown me", "my wife will leave me",
    "my husband will leave me", "how do i face them",
    "can't tell anyone", "hiding from family", "hiding debt",
    # Hindi transliterated
    "sharam aati hai", "munh dikhane layak nahi", "ghar wale maaf nahi karenge",
    "izzat chali gayi", "log kya kahenge", "maa baap ko batana mushkil hai",
    # Telugu transliterated
    "sigguga undi", "intlo cheppalekapotunanu", "family ki telusthe chastaru",
]

OVERWHELMED_KEYWORDS = [
    # English
    "can't take it anymore", "too much pressure", "breaking down",
    "can't sleep", "anxiety", "panicking", "panic attack",
    "mental breakdown", "crying all day", "can't eat", "lost hope",
    "nothing left", "i give up", "exhausted", "burned out",
    # Hindi transliterated
    "bahut takaan hai", "himmat nahi", "rona aa raha hai",
    "neend nahi aati", "dar lag raha hai", "bahut tension hai",
    # Telugu transliterated
    "chala stress ga undi", "tapinchukolakapotunanu", "nidra raatledu",
    "bhayam ga undi", "anni poyaayi",
]


# ─────────────────────────────────────────────
# 3. HELPLINE CONSTANTS
# ─────────────────────────────────────────────

HELPLINES = {
    "iCall": {
        "number"  : "9152987821",
        "hours"   : "Mon–Sat, 8am–10pm",
        "language": "English, Hindi",
        "cost"    : "Free",
        "org"     : "TISS (Tata Institute of Social Sciences)",
    },
    "Vandrevala Foundation": {
        "number"  : "1860-2662-345",
        "hours"   : "24/7",
        "language": "English, Hindi, regional languages",
        "cost"    : "Free",
        "org"     : "Vandrevala Foundation",
    },
    "AASRA": {
        "number"  : "9820466627",
        "hours"   : "24/7",
        "language": "English, Hindi",
        "cost"    : "Free",
        "org"     : "AASRA",
    },
}


# ─────────────────────────────────────────────
# 4. RESULT DATACLASS
# ─────────────────────────────────────────────

@dataclass
class MentalHealthResult:
    crisis_level          : CrisisLevel
    triggers              : list[str]
    primary_message       : str          # First thing shown to user
    helpline_message      : str          # Formatted helpline block
    followup_prompt       : str          # What to ask after stabilization
    use_ai_response       : bool         # True = safe to use Groq for follow-up
    ready_for_finances    : bool = False # True = user said they're ready
    suggested_path        : Optional[str] = None  # Path to route back to


# ─────────────────────────────────────────────
# 5. CORE DETECTOR
# ─────────────────────────────────────────────

def assess_mental_health(user_input: str) -> MentalHealthResult:
    """
    Assess the user's emotional state and return appropriate support response.

    Crisis levels (priority order):
        1. SUICIDAL      — immediate helplines, pre-written script only
        2. SHAME_DESPAIR — gentle validation, then helplines softly
        3. OVERWHELMED   — empathy + breathing, AI can assist
        4. STABLE        — warm check-in, route back to finances

    Args:
        user_input: Raw text from user

    Returns:
        MentalHealthResult with crisis level, messages, and routing info
    """
    if not user_input or not user_input.strip():
        return _stable_response([])

    text = user_input.lower().strip()

    # ── Level 1: Suicidal ────────────────────────────────────────────
    suicidal_hits = _match(text, SUICIDAL_KEYWORDS)
    if suicidal_hits:
        logger.critical(f"[CRISIS] Suicidal keywords detected — triggers={suicidal_hits[:3]}")
        return _suicidal_response(suicidal_hits)

    # ── Level 2: Shame / Despair ─────────────────────────────────────
    shame_hits = _match(text, SHAME_KEYWORDS)
    if shame_hits:
        logger.warning(f"[CRISIS] Shame/despair keywords detected — triggers={shame_hits[:3]}")
        return _shame_response(shame_hits)

    # ── Level 3: Overwhelmed ─────────────────────────────────────────
    overwhelmed_hits = _match(text, OVERWHELMED_KEYWORDS)
    if overwhelmed_hits:
        logger.info(f"[SUPPORT] Overwhelmed keywords detected — triggers={overwhelmed_hits[:3]}")
        return _overwhelmed_response(overwhelmed_hits)

    # ── Level 4: Stable ──────────────────────────────────────────────
    return _stable_response([])


def handle_followup(user_input: str, crisis_level: CrisisLevel) -> dict:
    """
    Called after the initial crisis response is shown.
    Checks if user is ready to return to financial guidance.

    Args:
        user_input   : User's reply after seeing crisis response
        crisis_level : The level that was initially detected

    Returns:
        dict with keys: ready_for_finances, message, suggested_path
    """
    text = user_input.lower().strip()

    # Readiness signals
    ready_signals = [
        "yes", "okay", "ok", "i'm okay", "i'm fine", "feeling better",
        "ready", "let's continue", "continue", "help me", "go ahead",
        "theek hoon", "theek hai", "haan", "chalte hain",
        "괜찮아", "nenu sare", "proceed",
    ]

    not_ready_signals = [
        "no", "not yet", "still upset", "not okay", "nahi", "abhi nahi",
        "give me time", "not ready", "later",
    ]

    is_ready   = any(sig in text for sig in ready_signals)
    not_ready  = any(sig in text for sig in not_ready_signals)

    if is_ready:
        return {
            "ready_for_finances": True,
            "message"           : (
                "I'm glad you're feeling a bit better. "
                "Whenever you're ready, I'm here to help you with your finances. "
                "Remember — no problem is too big to solve step by step. 💙"
            ),
            "suggested_path": None,  # caller decides based on original detection
        }
    elif not_ready:
        return {
            "ready_for_finances": False,
            "message"           : (
                "That's completely okay. Take all the time you need. "
                "I'll be right here whenever you want to talk — "
                "about anything, finances or just to vent. 💙"
            ),
            "suggested_path": None,
        }
    else:
        # Ambiguous — gently check in
        return {
            "ready_for_finances": False,
            "message"           : (
                "I hear you. How are you feeling right now? "
                "Are you okay to take a look at your financial situation together, "
                "or would you like more time?"
            ),
            "suggested_path": None,
        }


# ─────────────────────────────────────────────
# 6. RESPONSE BUILDERS
# ─────────────────────────────────────────────

def _suicidal_response(triggers: list[str]) -> MentalHealthResult:
    return MentalHealthResult(
        crisis_level    = CrisisLevel.SUICIDAL,
        triggers        = triggers,
        primary_message = (
            "I hear you, and I'm really glad you're talking to me right now.\n\n"
            "What you're feeling is real — and it matters deeply.\n"
            "You are not alone in this, even if it feels that way.\n\n"
            "Please reach out to one of these free helplines right now. "
            "They are trained to help and they genuinely care:"
        ),
        helpline_message = _format_helplines(all=True),
        followup_prompt  = (
            "I'm right here with you. Would you like to talk about "
            "what's been happening? You don't have to face this alone."
        ),
        use_ai_response  = False,   # Pre-written scripts only for suicidal crisis
        ready_for_finances = False,
    )


def _shame_response(triggers: list[str]) -> MentalHealthResult:
    return MentalHealthResult(
        crisis_level    = CrisisLevel.SHAME_DESPAIR,
        triggers        = triggers,
        primary_message = (
            "First — what you're feeling right now is completely understandable.\n\n"
            "Financial problems can make us feel like we've failed the people we love. "
            "But you haven't. You're here, trying to find a way out — "
            "and that takes real courage.\n\n"
            "Your family loves you more than any debt or mistake. "
            "You are not defined by your financial situation."
        ),
        helpline_message = _format_helplines(all=True),
        followup_prompt  = (
            "When you feel ready, I can help you make a real plan "
            "to fix the financial situation — step by step, together. "
            "Would you like that?"
        ),
        use_ai_response  = True,   # AI can assist after initial message
        ready_for_finances = False,
    )


def _overwhelmed_response(triggers: list[str]) -> MentalHealthResult:
    return MentalHealthResult(
        crisis_level    = CrisisLevel.OVERWHELMED,
        triggers        = triggers,
        primary_message = (
            "Hey — take a breath. Seriously, just one slow breath. 🌬️\n\n"
            "It sounds like you're carrying a lot right now, "
            "and that's exhausting. What you're feeling is valid.\n\n"
            "You don't have to solve everything today. "
            "We'll break it into small, manageable steps together."
        ),
        helpline_message = _format_helplines(all=False),  # Soft mention only
        followup_prompt  = (
            "Are you feeling a little steadier? "
            "Whenever you're ready, tell me what's weighing on you most "
            "and we'll tackle it together."
        ),
        use_ai_response  = True,
        ready_for_finances = False,
    )


def _stable_response(triggers: list[str]) -> MentalHealthResult:
    return MentalHealthResult(
        crisis_level     = CrisisLevel.STABLE,
        triggers         = triggers,
        primary_message  = (
            "I'm here with you. It's okay to feel stressed about money — "
            "most people do at some point.\n\n"
            "Let's work through this together. "
            "The fact that you're reaching out is already the hardest step."
        ),
        helpline_message = "",
        followup_prompt  = (
            "What would you like to focus on first? "
            "We can look at your debt, your spending, or how to start earning more."
        ),
        use_ai_response    = True,
        ready_for_finances = True,
    )


# ─────────────────────────────────────────────
# 7. HELPER FUNCTIONS
# ─────────────────────────────────────────────

def _match(text: str, keywords: list[str]) -> list[str]:
    """Return matched keywords found in text."""
    return [kw for kw in keywords if kw in text]


def _format_helplines(all: bool) -> str:
    """
    Format helpline block for display.

    Args:
        all: True = show all 3 helplines, False = soft single mention
    """
    if not all:
        return (
            "If things ever feel too heavy, "
            "iCall (9152987821) is a free, confidential helpline — "
            "they're really good listeners."
        )

    lines = ["📞 Free & Confidential Mental Health Helplines (India):\n"]
    for name, info in HELPLINES.items():
        lines.append(
            f"• {name}: {info['number']}\n"
            f"  {info['hours']} | {info['language']} | {info['cost']}"
        )
    lines.append(
        "\nYou can also text if calling feels too hard. "
        "They are trained, non-judgmental, and completely confidential."
    )
    return "\n".join(lines)


def get_crisis_level_from_string(level_str: str) -> CrisisLevel:
    """Convert string back to CrisisLevel enum (for session state storage)."""
    mapping = {
        "suicidal"      : CrisisLevel.SUICIDAL,
        "shame_despair" : CrisisLevel.SHAME_DESPAIR,
        "overwhelmed"   : CrisisLevel.OVERWHELMED,
        "stable"        : CrisisLevel.STABLE,
    }
    return mapping.get(level_str, CrisisLevel.STABLE)


# ─────────────────────────────────────────────
# 8. STREAMLIT-READY WRAPPER
# ─────────────────────────────────────────────

def run_mental_health_guardian(user_input: str) -> dict:
    """
    Streamlit-friendly wrapper.

    Usage in app.py:
        from mental_health_guardian import run_mental_health_guardian
        result = run_mental_health_guardian(user_message)
        st.session_state["crisis_level"] = result["crisis_level"]
    """
    result = assess_mental_health(user_input)
    return {
        "crisis_level"       : result.crisis_level.value,
        "triggers"           : result.triggers,
        "primary_message"    : result.primary_message,
        "helpline_message"   : result.helpline_message,
        "followup_prompt"    : result.followup_prompt,
        "use_ai_response"    : result.use_ai_response,
        "ready_for_finances" : result.ready_for_finances,
        "suggested_path"     : result.suggested_path,
    }


# ─────────────────────────────────────────────
# 9. QUICK TEST
# ─────────────────────────────────────────────

if __name__ == "__main__":
    test_inputs = [
        # Suicidal
        ("I want to die, my debt has ruined everything",          "EXPECT: SUICIDAL"),
        ("marna chahta hoon, koi raasta nahi",                    "EXPECT: SUICIDAL"),
        ("chachipovalani, anni poyaayi",                         "EXPECT: SUICIDAL"),
        # Shame
        ("I'm too ashamed, my family will hate me for this debt", "EXPECT: SHAME"),
        ("munh dikhane layak nahi raha main",                     "EXPECT: SHAME"),
        # Overwhelmed
        ("I can't sleep, too much pressure, anxiety is killing",  "EXPECT: OVERWHELMED"),
        ("bahut tension hai, neend nahi aati",                    "EXPECT: OVERWHELMED"),
        # Stable
        ("I'm worried about my finances",                         "EXPECT: STABLE"),
        ("how to manage debt?",                                   "EXPECT: STABLE"),
    ]

    print("=" * 65)
    print("MENTAL HEALTH GUARDIAN — TEST RUN")
    print("=" * 65)

    for inp, label in test_inputs:
        result = assess_mental_health(inp)
        print(f"\n{label}")
        print(f"Input        : {inp[:60]}")
        print(f"Crisis Level : {result.crisis_level.value}")
        print(f"Triggers     : {result.triggers[:2]}")
        print(f"Use AI       : {result.use_ai_response}")
        print(f"Ready Finance: {result.ready_for_finances}")
        print(f"Message      : {result.primary_message[:80]}...")
        if result.helpline_message:
            print(f"Helplines    : {result.helpline_message[:60]}...")
        print("-" * 45)