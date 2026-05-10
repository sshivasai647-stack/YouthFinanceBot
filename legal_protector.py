"""
legal_protector.py
==================
Legal guidance module for Youth Financial Guardian Chatbot.

This module helps young users understand their rights when they face
loan harassment, unfair lending practices, or confusing contract terms.
It returns a clear action plan, legal rights summary, and next steps.
"""

import logging
import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class LegalIssueType(Enum):
    HARASSMENT = "harassment"
    UNFAIR_PRACTICE = "unfair_practice"
    LOAN_APP_RISK = "loan_app_risk"
    CONTRACT_QUERY = "contract_query"
    UNKNOWN = "unknown"


@dataclass
class LegalProtectorResult:
    issue_type: LegalIssueType
    confidence: float
    triggers: List[str]
    primary_message: str
    summary: str
    legal_rights: List[str]
    action_plan: List[str]
    contact_options: List[str]
    next_step_prompt: str
    last_updated: str


HARASSMENT_KEYWORDS = [
    "harassment", "threat", "abuse", "call me", "recovery agent", "agent called",
    "scared", "blackmail", "shame", "family", "photos", "privacy", "illegal loan",
    "bad words", "threatening", "physical", "abusive", "intimidate",
]

UNFAIR_PRACTICE_KEYWORDS = [
    "hidden charge", "extra fee", "high interest", "no agreement", "no paperwork",
    "wrong interest", "not told", "false promise", "misleading", "ghost loan",
    "loan app", "instant loan app", "kyc", "no kyc", "unfair", "trap",
]

LOAN_APP_KEYWORDS = [
    "loan app", "instant loan", "quick loan", "phone loan", "app loan", "mumbai app",
    "emi app", "apna loan", "easy loan", "sahukaar app", "online loan app",
]

CONTRACT_KEYWORDS = [
    "agreement", "contract", "terms", "interest rate", "penalty", "closure charge",
    "prepayment", "document", "signature", "loan papers", "loan agreement",
]

LEGAL_RIGHTS = [
    "Lenders must not harass you or your family with abusive calls or messages.",
    "You have the right to receive a clear loan agreement in language you understand.",
    "No lender can share your debt information with unauthorized people.",
    "If you are a borrower, you can complain to the Banking Ombudsman for unfair practices.",
    "You are entitled to a 60-day notice before your account is declared a non-performing asset.",
]

PROHIBITED_ACTIONS = [
    "No calls before 8 AM or after 7 PM.",
    "No abusive, threatening or obscene language.",
    "No disclosure of debt details to relatives or neighbors.",
    "No physical intimidation or violence.",
    "No seizure of essential household items or tools of trade without due notice.",
]

CONTACT_OPTIONS = [
    "Bank's grievance officer: first contact for any loan dispute.",
    "Banking Ombudsman: free complaint resolution service for RBI-regulated lenders.",
    "National Consumer Helpline: call 1915 for consumer rights support.",
    "Cyber Crime Helpline: call 1930 if an app is misusing your data or photos.",
]


def _normalize_text(user_input: str) -> str:
    text = user_input.lower().strip()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


def _match_keywords(text: str, keywords: List[str]) -> List[str]:
    return [kw for kw in keywords if kw in text]


def get_legal_protection_info() -> Dict[str, object]:
    return {
        "last_updated": datetime.now().strftime("%d %B %Y"),
        "legal_rights": LEGAL_RIGHTS,
        "prohibited_actions": PROHIBITED_ACTIONS,
        "contact_options": CONTACT_OPTIONS,
        "summary": (
            "You are protected by RBI fair practice guidelines. "
            "Keep records, ask for written terms, and escalate if you face harassment."
        ),
        "action_plan": [
            "Document all calls, messages and app interactions.",
            "Ask the lender for a written loan agreement immediately.",
            "If harassment continues, file a complaint with the Banking Ombudsman.",
        ],
    }


def assess_legal_situation(user_input: str) -> LegalProtectorResult:
    if not user_input or not user_input.strip():
        legal_info = get_legal_protection_info()
        return LegalProtectorResult(
            issue_type=LegalIssueType.UNKNOWN,
            confidence=0.0,
            triggers=[],
            primary_message=(
                "Tell me more about your loan or legal worry so I can point you to the right protection."
            ),
            summary=legal_info["summary"],
            legal_rights=legal_info["legal_rights"],
            action_plan=legal_info["action_plan"],
            contact_options=legal_info["contact_options"],
            next_step_prompt=(
                "Are you facing harassment, hidden charges, or confusing loan terms?"
            ),
            last_updated=legal_info["last_updated"],
        )

    text = _normalize_text(user_input)
    harassment_hits = _match_keywords(text, HARASSMENT_KEYWORDS)
    unfair_hits = _match_keywords(text, UNFAIR_PRACTICE_KEYWORDS)
    loan_app_hits = _match_keywords(text, LOAN_APP_KEYWORDS)
    contract_hits = _match_keywords(text, CONTRACT_KEYWORDS)

    triggers = list({*harassment_hits, *unfair_hits, *loan_app_hits, *contract_hits})
    score = len(harassment_hits) * 3 + len(unfair_hits) * 2 + len(loan_app_hits) + len(contract_hits)

    if harassment_hits and score >= 4:
        issue_type = LegalIssueType.HARASSMENT
    elif unfair_hits and score >= 3:
        issue_type = LegalIssueType.UNFAIR_PRACTICE
    elif loan_app_hits and score >= 2:
        issue_type = LegalIssueType.LOAN_APP_RISK
    elif contract_hits and score >= 2:
        issue_type = LegalIssueType.CONTRACT_QUERY
    else:
        issue_type = LegalIssueType.UNKNOWN

    confidence = min(score / 6.0, 1.0)
    if issue_type == LegalIssueType.UNKNOWN:
        confidence = 0.2

    legal_info = get_legal_protection_info()

    if issue_type == LegalIssueType.HARASSMENT:
        primary_message = (
            "This sounds like harassment or unfair collection behaviour. "
            "You have legal protections — I will show you what to do next."
        )
        next_step_prompt = (
            "Did the lender contact your family, threaten you, or share your details?"
        )
    elif issue_type == LegalIssueType.UNFAIR_PRACTICE:
        primary_message = (
            "I see signs of hidden charges or unfair loan practices. "
            "You should compare what was promised with what is being charged."
        )
        next_step_prompt = (
            "Can you share the exact fee, interest rate, or loan term that seems wrong?"
        )
    elif issue_type == LegalIssueType.LOAN_APP_RISK:
        primary_message = (
            "Instant loan apps can be risky. "
            "Let's check whether the app is using unfair practices or unsafe data policies."
        )
        next_step_prompt = (
            "Which app are you using, and what kind of messages or demands did they send?"
        )
    elif issue_type == LegalIssueType.CONTRACT_QUERY:
        primary_message = (
            "Loan agreements should be clear and fair. "
            "I can help you understand the key points to watch for."
        )
        next_step_prompt = (
            "Do you want me to explain interest, penalties, or the repayment schedule?"
        )
    else:
        primary_message = (
            "I can help with borrower rights and legal protection. "
            "Describe the issue in a little more detail so I can guide you correctly."
        )
        next_step_prompt = (
            "Are you worried about harassment, hidden fees, or loan app behaviour?"
        )

    summary = (
        "You are protected by RBI fair practice guidelines. "
        "Document everything and raise a complaint if the lender crosses the line."
    )

    return LegalProtectorResult(
        issue_type=issue_type,
        confidence=round(confidence, 2),
        triggers=triggers,
        primary_message=primary_message,
        summary=summary,
        legal_rights=legal_info["legal_rights"],
        action_plan=legal_info["action_plan"],
        contact_options=legal_info["contact_options"],
        next_step_prompt=next_step_prompt,
        last_updated=legal_info["last_updated"],
    )


def run_legal_protector(user_input: str, user_profile: Optional[dict] = None) -> dict:
    result = assess_legal_situation(user_input)
    return {
        "issue_type": result.issue_type.value,
        "confidence": result.confidence,
        "triggers": result.triggers,
        "primary_message": result.primary_message,
        "summary": result.summary,
        "legal_rights": result.legal_rights,
        "action_plan": result.action_plan,
        "contact_options": result.contact_options,
        "next_step_prompt": result.next_step_prompt,
        "last_updated": result.last_updated,
    }


if __name__ == "__main__":
    tests = [
        "Recovery agents are calling me every day and my family is getting involved.",
        "The loan app charged me hidden fees and I do not have a proper agreement.",
        "I took an instant loan app and now they keep threatening me.",
        "I don't understand the interest rate and prepayment penalty in the contract.",
        "The lender is calling me before 8 AM and using abusive language.",
    ]

    print("=" * 60)
    print("LEGAL PROTECTOR - TEST RUN")
    print("=" * 60)

    for text in tests:
        result = run_legal_protector(text)
        print(f"\nInput: {text}")
        print(f"Issue Type: {result['issue_type']} | Confidence: {result['confidence']}")
        print(f"Primary: {result['primary_message']}")
        print(f"Next Step: {result['next_step_prompt']}")
        print(f"Rights: {result['legal_rights'][:2]}...")
        print("-" * 40)
