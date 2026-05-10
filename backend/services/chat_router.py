# Purpose: Smart chat — Section 6.1 routing: ``detect_situation`` → domain modules → LLM synthesis.
# Existing module dependencies: situation_detector, analyzer, crisis_detector, debt_handler,
# investment_guide (create_investment_plan, recommend_investments), goal_tracker (create_goal,
# check_progress), mental_health_gaurdian, betting_alternative, legal_protector,
# earn_suggester, llm_engine (build_messages_with_history, generate_with_retry, get_advice).

"""Route a user message through detectors, call the right finance modules, then synthesize via LLM."""

from __future__ import annotations

import json
import logging
from typing import Any

from analyzer import analyze_spending, get_saving_tip
from crisis_detector import detect_crisis
from debt_handler import (
    Debt,
    DebtType,
    calculate_debt_burden,
    calculate_emi,
    create_repayment_plan,
    detect_debt_trap,
    get_legal_protection_info,
)
from earn_suggester import suggest_earning
from goal_tracker import check_progress, create_goal
from investment_guide import create_investment_plan, recommend_investments
from legal_protector import assess_legal_situation
from llm_engine import DEFAULT_MODEL, DEFAULT_PROVIDER, LLMError, build_messages_with_history, generate_with_retry
from mental_health_gaurdian import CrisisLevel, assess_mental_health
from betting_alternative import assess_betting_behavior

from backend.services.serialize import to_jsonable
from situation_detector import (
    PATH_BETTING,
    PATH_DEBT,
    PATH_EXPENSE,
    PATH_INVEST,
    PATH_LEGAL,
    PATH_MENTAL_HEALTH,
    PATH_UNKNOWN,
    PATH_ZERO_INVESTMENT,
    detect_situation,
)

logger = logging.getLogger(__name__)

GOAL_FOCUS_KEYWORDS = (
    "goal",
    "target",
    "save for",
    "saving for",
    "wedding",
    "marriage",
    "vacation",
    "trip",
    "education fee",
    "exam",
    "bike",
    "car",
    "house",
    "flat",
    "down payment",
    "fd for",
)

SUGGESTIONS: dict[str, list[str]] = {
    "crisis": ["I need emergency help", "Helpline numbers"],
    "earning": ["How can I earn with no upfront cost?", "Side hustle ideas for students"],
    "debt": ["How do I negotiate EMI?", "What is debt trap?"],
    "betting": ["How to recover money habits?", "Alternatives to fantasy apps"],
    "mental_health": ["I'm anxious about money", "Breathing exercise suggestion"],
    "spending": ["How to cut food spend?", "50-30-20 rule explained"],
    "investment": ["PPF vs SIP", "Start with ₹500/month"],
    "goal": ["How much to save monthly?", "Adjust my goal timeline"],
    "legal": ["Recovery agent harassment", "Hidden loan charges"],
    "general": ["Build emergency fund", "Track my expenses"],
}


def _goal_focused(text: str) -> bool:
    t = text.lower()
    return any(k in t for k in GOAL_FOCUS_KEYWORDS)


def path_to_route(top_path: str, user_message: str) -> str:
    """Map ``DetectionResult.path`` to API route string (Section 6.1 labels)."""
    if top_path == PATH_INVEST:
        return "goal" if _goal_focused(user_message) else "investment"
    return {
        PATH_ZERO_INVESTMENT: "earning",
        PATH_DEBT: "debt",
        PATH_BETTING: "betting",
        PATH_MENTAL_HEALTH: "mental_health",
        PATH_EXPENSE: "spending",
        PATH_LEGAL: "legal",
        PATH_UNKNOWN: "general",
    }.get(top_path, "general")


def _map_debt_type(raw: str) -> DebtType:
    s = (raw or "").strip().lower()
    for dt in DebtType:
        if s == dt.name.lower() or s in dt.value.lower():
            return dt
    return DebtType.PERSONAL_LOAN


def _debts_from_payload(rows: list[dict[str, Any]]) -> list[Debt]:
    out: list[Debt] = []
    for d in rows:
        p = float(d.get("principal", 0))
        r = float(d.get("rate", 0))
        tenure = int(d.get("tenure", 36))
        name = str(d.get("name", "Loan"))
        emi_raw = d.get("emi")
        if emi_raw is not None and emi_raw != "":
            emi = float(emi_raw)
        else:
            emi = calculate_emi(p, r, tenure)
        out.append(Debt(name, _map_debt_type(str(d.get("type", "Personal Loan"))), p, r, monthly_emi=emi))
    return out


def _trap_history_from_totals(total_debt: float, income: float) -> list[dict[str, Any]]:
    repay = min(max(total_debt * 0.02, 1.0), income * 0.3) if income > 0 else 200.0
    hist: list[dict[str, Any]] = []
    td = total_debt
    for i in range(4):
        hist.append(
            {
                "month": f"M{i + 1}",
                "total_debt": td,
                "new_debt": 0,
                "monthly_repayment": repay,
            }
        )
        td = max(0.0, td - repay * 0.5)
    return hist


def _build_system_addon(module_ctx: dict[str, Any], route: str) -> str:
    """Extra system guidance so the LLM cites module outputs accurately."""
    if not module_ctx:
        return ""
    tail = json.dumps(module_ctx, default=str)[:4500]
    return f"\n\nUse the structured CONTEXT below. Prefer its numbers; explain simply.\nCONTEXT_JSON:\n{tail}"


def gather_route_modules(
    *,
    route: str,
    user_message: str,
    income: float,
    savings_rate: float,
    age: int,
    risk_appetite: str,
    goal: str,
    expenses: dict[str, float] | None,
    debts_payload: list[dict[str, Any]] | None,
    skills: list[str] | None,
    monthly_debt_payment: float,
    goal_target_amount: float | None,
    goal_months: int | None,
    goal_monthly_saving: float | None,
) -> dict[str, Any]:
    """
    Section 6.1 module dispatch — each branch calls existing project functions only.
    """
    expenses = expenses or {}
    debts_payload = debts_payload or []
    skills = skills or ["writing"]
    ctx: dict[str, Any] = {}

    if route == "betting":
        ctx["betting"] = to_jsonable(assess_betting_behavior(user_message))
        return ctx

    if route == "legal":
        ctx["legal"] = to_jsonable(assess_legal_situation(user_message))
        return ctx

    if route == "spending":
        if income > 0 and expenses:
            sp = analyze_spending(income, expenses, monthly_debt_payment)
            ctx["spending"] = sp
            ctx["saving_tip"] = get_saving_tip(float(sp["savings_rate"]))
        else:
            ctx["note"] = "For a full spending breakdown, add monthly income and category expenses in the request body."
        return ctx

    if route == "debt":
        if debts_payload:
            dlist = _debts_from_payload(debts_payload)
            total_princ = sum(d.principal for d in dlist)
            total_emi = sum(d.monthly_emi for d in dlist)
            inc_use = income if income > 0 else 1.0
            ctx["burden"] = calculate_debt_burden(inc_use, total_princ, total_emi)
            month_exp = sum(expenses.values()) if expenses else (income * 0.6 if income > 0 else 0)
            if income > 0:
                ctx["repayment_plan"] = create_repayment_plan(income, month_exp, dlist)
            hist = _trap_history_from_totals(total_princ, inc_use)
            ctx["debt_trap"] = detect_debt_trap(hist, inc_use)
        else:
            ctx["legal_basics"] = {"summary": str(get_legal_protection_info().get("summary", ""))[:500]}
        return ctx

    if route == "investment":
        surplus = max((income * (savings_rate / 100)) if savings_rate else income * 0.1, 0)
        ctx["recommend_investments"] = recommend_investments(surplus, risk_appetite, age, goal)
        goals_list = [g.strip() for g in (goal or "long-term growth").split(",") if g.strip()]
        if not goals_list:
            goals_list = ["Emergency fund"]
        if income > 0:
            try:
                ctx["investment_plan"] = create_investment_plan(income, age, goals_list, risk_appetite)
            except ValueError as exc:
                ctx["investment_plan_error"] = str(exc)
        return ctx

    if route == "goal":
        months = int(goal_months) if goal_months and goal_months > 0 else 12
        if goal_target_amount and float(goal_target_amount) > 0:
            target = float(goal_target_amount)
        else:
            target = max(income * 6, 50_000.0) if income > 0 else 100_000.0
        monthly_save = (
            float(goal_monthly_saving)
            if goal_monthly_saving is not None and float(goal_monthly_saving) >= 0
            else (income * 0.15 if income > 0 else 2_000.0)
        )
        gname = (goal or "my goal").strip() or "my goal"
        g = create_goal(gname, target, months)
        ctx["goal"] = to_jsonable(g)
        ctx["goal_progress"] = check_progress(g, monthly_save)
        return ctx

    if route == "earning":
        ctx["earning_ideas"] = to_jsonable(suggest_earning(age, skills)[:5])
        return ctx

    return ctx


def run_chat_pipeline(
    *,
    user_message: str,
    chat_history: list[dict[str, str]],
    income: float = 0.0,
    savings_rate: float = 0.0,
    age: int = 22,
    risk_appetite: str = "medium",
    goal: str = "retirement",
    expenses: dict[str, float] | None = None,
    debts_payload: list[dict[str, Any]] | None = None,
    skills: list[str] | None = None,
    monthly_debt_payment: float = 0.0,
    goal_target_amount: float | None = None,
    goal_months: int | None = None,
    goal_monthly_saving: float | None = None,
) -> dict[str, Any]:
    """
    1) ``detect_situation`` → 2) resolve route (invest vs goal when PATH_H) →
    3) suicidal helpline OR financial ``Immediate Crisis`` helpline (no LLM) →
    4) module outputs → 5) ``build_messages_with_history`` + ``generate_with_retry``.

    Returns: reply, route, suggestions, detection (includes ``route`` alias), context,
    llm_error, skip_llm.
    """
    det = detect_situation(user_message)
    route = path_to_route(det.path, user_message)

    if det.is_crisis or det.path == PATH_MENTAL_HEALTH:
        route = "mental_health"

    exp = expenses or {}
    crisis = detect_crisis(
        income=max(income, 0.0),
        expenses=exp,
        debt=monthly_debt_payment,
        text=user_message,
    )

    mh = None
    if route == "mental_health":
        mh = assess_mental_health(user_message)
        if mh.crisis_level == CrisisLevel.SUICIDAL:
            reply = f"{mh.primary_message}\n\n{mh.helpline_message}"
            return {
                "reply": reply,
                "route": "crisis",
                "suggestions": SUGGESTIONS["crisis"],
                "detection": _detection_payload(det, "crisis"),
                "context": {"mental_health": to_jsonable(mh), "crisis": crisis},
                "llm_error": None,
                "skip_llm": True,
            }

    # Financial / keyword Immediate Crisis (not mental_health route) → helpline text, no LLM
    if crisis.get("level") == "Immediate Crisis" and route != "mental_health":
        alerts = crisis.get("alerts") or []
        reply = "\n\n".join(alerts) if alerts else "Please reach out to local emergency or crisis support."
        return {
            "reply": reply,
            "route": "crisis",
            "suggestions": SUGGESTIONS["crisis"],
            "detection": _detection_payload(det, "crisis"),
            "context": {"crisis": crisis},
            "llm_error": None,
            "skip_llm": True,
        }

    if route == "mental_health":
        assert mh is not None
        module_ctx = {
            "mental_health": to_jsonable(mh),
        }
        if mh.crisis_level != CrisisLevel.STABLE:
            module_ctx["crisis_scan"] = crisis
    else:
        module_ctx = gather_route_modules(
            route=route,
            user_message=user_message,
            income=income,
            savings_rate=savings_rate,
            age=age,
            risk_appetite=risk_appetite,
            goal=goal,
            expenses=expenses,
            debts_payload=debts_payload,
            skills=skills,
            monthly_debt_payment=monthly_debt_payment,
            goal_target_amount=goal_target_amount,
            goal_months=goal_months,
            goal_monthly_saving=goal_monthly_saving,
        )

    addon = _build_system_addon(module_ctx, route)
    enriched_user = f"{user_message.strip()}{addon}"

    messages = build_messages_with_history(
        enriched_user,
        chat_history,
        income=income,
        savings_rate=savings_rate,
    )

    reply = ""
    llm_err: str | None = None
    try:
        reply = generate_with_retry(
            provider=DEFAULT_PROVIDER,
            model=DEFAULT_MODEL,
            messages=messages,
            max_tokens=500,
            temperature=0.35,
        )
    except (LLMError, ValueError) as exc:
        llm_err = str(exc)
        logger.warning("LLM failed for chat: %s", exc)
        reply = (
            f"I could not reach the AI service right now. Route: {route}. "
            "Try again shortly or open the matching tool in the app."
        )

    return {
        "reply": reply,
        "route": route,
        "suggestions": SUGGESTIONS.get(route, SUGGESTIONS["general"]),
        "detection": _detection_payload(det, route),
        "context": module_ctx,
        "llm_error": llm_err,
        "skip_llm": False,
    }


def _detection_payload(det: Any, route: str) -> dict[str, Any]:
    """Shape returned to API clients; adds ``route`` (alias) beside ``path``."""
    return {
        "path": det.path,
        "route": route,
        "confidence": det.confidence,
        "triggers": det.triggers,
        "display_message": det.display_message,
        "is_crisis": det.is_crisis,
        "clarification_needed": getattr(det, "clarification_needed", False),
        "suggested_question": getattr(det, "suggested_question", None),
        "secondary_path": getattr(det, "secondary_path", None),
    }
