"""
betting_alternative.py
======================
Gambling / betting alternative module for Youth Financial Guardian Chatbot.

This module provides assessment and recovery guidance for young users who
have been struggling with fantasy sports, betting, or gambling losses.

It is designed to be called from the path router and to return a plain
serializable dictionary for Streamlit or other interfaces.
"""

import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class BettingAlternativeResult:
    risk_level: RiskLevel
    triggers: List[str]
    confidence: float
    primary_message: str
    recommended_actions: List[str]
    alternative_activities: List[str]
    financial_recovery_tips: List[str]
    support_resources: List[str]
    next_step_prompt: str


BETTING_KEYWORDS = [
    "bet", "betting", "gambling", "fantasy", "dream11", "mpl", "my11circle",
    "satta", "matka", "cricket bet", "ipl bet", "poker", "rummy", "casino",
    "ludo real money", "real money game", "daily fantasy", "sports bet",
    "winzo", "zupee", "halaplay", "ballebaazi", "gamezy",
]

LOSS_KEYWORDS = [
    "lost", "losing", "loss", "chasing losses", "lost all", "went bankrupt",
    "can't stop", "never stop", "can't stop betting", "keep losing",
    "money gone", "ruined", "hole", "debt because of betting", "betting loss",
]

FREQUENCY_KEYWORDS = [
    "every day", "daily", "night", "all night", "all day", "often", "again and again",
    "many times", "multiple times", "too much", "too often", "habit",
]

CONTROL_KEYWORDS = [
    "cannot stop", "can't stop", "unable to stop", "need help", "addicted", "addiction",
    "out of control", "control", "self control", "urge", "strong urge",
]

ALTERNATIVE_ACTIVITIES = [
    "Play a free skill-based game or sport with friends instead of betting.",
    "Learn a new competitive hobby like coding contests, chess or quiz apps.",
    "Use your energy to build a small side hustle or creative project.",
    "Practice deep breathing or short exercise when the urge appears.",
    "Track your wins from safe habits like study, exercise, or skill growth.",
]

SUPPORT_RESOURCE_TEXTS = [
    "Talk to a trusted friend or family member about what happened.",
    "Use self-exclusion and deposit-limit tools in your gaming apps.",
    "Set up a simple spending tracker so losses are visible and real.",
    "If you feel overwhelmed, reach out to a local counsellor or helpline.",
]


def _normalize_text(user_input: str) -> str:
    text = user_input.lower().strip()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


def _match_keywords(text: str, keywords: List[str]) -> List[str]:
    return [keyword for keyword in keywords if keyword in text]


def assess_betting_behavior(user_input: str) -> BettingAlternativeResult:
    if not user_input or not user_input.strip():
        return BettingAlternativeResult(
            risk_level=RiskLevel.LOW,
            triggers=[],
            confidence=0.0,
            primary_message=(
                "It sounds like you want help with betting or fantasy sports. "
                "Tell me a little more so I can suggest the best alternatives."
            ),
            recommended_actions=[
                "Describe how often you are using betting or fantasy sports apps.",
                "Share whether you are losing money or chasing losses.",
            ],
            alternative_activities=ALTERNATIVE_ACTIVITIES,
            financial_recovery_tips=[
                "Keep a simple daily log of every rupee spent on betting.",
                "Start moving a small amount into savings each week instead.",
            ],
            support_resources=SUPPORT_RESOURCE_TEXTS,
            next_step_prompt=(
                "Can you tell me if this is happening every day, and how much money "
                "you usually lose?"
            ),
        )

    text = _normalize_text(user_input)
    betting_hits = _match_keywords(text, BETTING_KEYWORDS)
    loss_hits = _match_keywords(text, LOSS_KEYWORDS)
    frequency_hits = _match_keywords(text, FREQUENCY_KEYWORDS)
    control_hits = _match_keywords(text, CONTROL_KEYWORDS)

    trigger_hits = list({*betting_hits, *loss_hits, *frequency_hits, *control_hits})
    score = len(betting_hits) + len(loss_hits) * 2 + len(frequency_hits) + len(control_hits)

    if score >= 6 or (len(loss_hits) >= 2 and len(frequency_hits) >= 1):
        risk_level = RiskLevel.HIGH
    elif score >= 3:
        risk_level = RiskLevel.MEDIUM
    else:
        risk_level = RiskLevel.LOW

    confidence = min(score / 6.0, 1.0)
    if not trigger_hits:
        confidence = 0.1

    if risk_level == RiskLevel.HIGH:
        primary_message = (
            "This looks like a high-risk betting pattern. "
            "Let's build a recovery plan and give your money a safer direction."
        )
    elif risk_level == RiskLevel.MEDIUM:
        primary_message = (
            "I see signs of regular betting and loss — you may be moving toward a risky habit. "
            "I can help you take control before it gets worse."
        )
    else:
        primary_message = (
            "You may be curious about betting or worried about recent losses. "
            "I can show you safer ways to keep your competitive energy working for you."
        )

    return BettingAlternativeResult(
        risk_level=risk_level,
        triggers=trigger_hits,
        confidence=round(confidence, 2),
        primary_message=primary_message,
        recommended_actions=_build_recommended_actions(risk_level),
        alternative_activities=ALTERNATIVE_ACTIVITIES,
        financial_recovery_tips=_build_financial_tips(risk_level),
        support_resources=SUPPORT_RESOURCE_TEXTS,
        next_step_prompt=(
            "Would you like a step-by-step plan to stop betting, recover your losses, "
            "and start saving again?"
        ),
    )


def _build_recommended_actions(risk_level: RiskLevel) -> List[str]:
    actions = [
        "Pause all deposits to betting or fantasy sports apps for at least 7 days.",
        "Write down the exact amount you have lost and how often it is happening.",
        "Set a small daily budget for yourself and keep that amount in a locked savings folder.",
        "Use app-blocking or parental-control tools to make it harder to open betting apps.",
        "Talk to one trusted person about your experience so you don't carry it alone.",
    ]

    if risk_level == RiskLevel.HIGH:
        actions.insert(
            0,
            "If you are losing more money than you can afford, stop immediately and ask for help."
        )
    elif risk_level == RiskLevel.MEDIUM:
        actions.insert(
            0,
            "Recognize this pattern now and create a stronger limit before it becomes a habit."
        )

    return actions


def _build_financial_tips(risk_level: RiskLevel) -> List[str]:
    tips = [
        "Treat betting losses as money that should not be recovered by more betting.",
        "Move any spare change into a separate savings envelope or bank account.",
        "Use the money you would have bet to build an emergency buffer instead.",
    ]

    if risk_level == RiskLevel.HIGH:
        tips.append(
            "If your losses are linked to debt or loan pressure, talk to a financial counsellor."
        )
    else:
        tips.append(
            "Replace one betting session with one learning session or a healthier hobby."
        )

    return tips


def run_betting_alternative(user_input: str, user_profile: Optional[dict] = None) -> dict:
    result = assess_betting_behavior(user_input)
    monthly_income = None
    if user_profile and isinstance(user_profile, dict):
        monthly_income = user_profile.get("income")

    recovery_message = (
        "Here is a safer, money-smart plan you can start with today." if result.risk_level != RiskLevel.LOW
        else "Here are healthier choices you can use instead of betting."
    )

    if monthly_income and isinstance(monthly_income, (int, float)) and monthly_income > 0:
        savings_tip = (
            f"Consider moving ₹{max(100, int(monthly_income * 0.05))} each month into a separate savings account."
        )
    else:
        savings_tip = "Consider keeping even a small amount each week in a safe savings place."

    return {
        "risk_level": result.risk_level.value,
        "confidence": result.confidence,
        "primary_message": result.primary_message,
        "recovery_message": recovery_message,
        "recommended_actions": result.recommended_actions,
        "alternative_activities": result.alternative_activities,
        "financial_recovery_tips": result.financial_recovery_tips + [savings_tip],
        "support_resources": result.support_resources,
        "triggers": result.triggers,
        "next_step_prompt": result.next_step_prompt,
    }


if __name__ == "__main__":
    examples = [
        "I keep losing money on Dream11 and can't stop.",
        "My MPL bets are crushing my savings, I feel addicted.",
        "I play fantasy cricket every day but I am not sure if it's a problem.",
        "I have lost 10k on betting and want to stop.",
        "How can I use my competitive energy in a safer way?",
    ]

    print("=" * 60)
    print("BETTING ALTERNATIVE - TEST RUN")
    print("=" * 60)
    for text in examples:
        result = run_betting_alternative(text, {"income": 15000})
        print(f"\nInput: {text}")
        print(f"Risk: {result['risk_level']} | Confidence: {result['confidence']}")
        print(f"Message: {result['primary_message']}")
        print(f"Actions: {result['recommended_actions'][:3]}...")
        print("-" * 40)
