# Purpose: Counsellor alert priority scoring (Section 6.3).
# Existing module dependencies: crisis_detector, debt_handler, mental_health_gaurdian,
# betting_alternative; reads MongoDB for latest citizen signals.

"""Compute a simple risk score for dashboarding assigned citizens."""

from __future__ import annotations

from typing import Any

from bson import ObjectId
from pymongo.collection import Collection
from pymongo.database import Database

from betting_alternative import RiskLevel, assess_betting_behavior
from crisis_detector import detect_crisis
from debt_handler import detect_debt_trap
from mental_health_gaurdian import assess_mental_health, CrisisLevel


def _latest_user_chat_text(db: Database, user_id: ObjectId) -> str:
    doc = db.chat_sessions.find_one({"user_id": user_id}, sort=[("updated_at", -1)])
    if not doc or not doc.get("messages"):
        return ""
    for m in reversed(doc["messages"]):
        if m.get("role") == "user" and m.get("content"):
            return str(m["content"])
    return ""


def _synthetic_trap_history(total_debt: float, income: float) -> list[dict[str, Any]]:
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


def score_citizen(db: Database, user_id: ObjectId) -> tuple[int, dict[str, Any]]:
    """
    Return (score, detail) using Section 6.3 weights:
       crisis CRITICAL / Immediate -> +50
       debt trap -> +30
       mental health crisis flags -> +40
       betting HIGH -> +20
    """
    score = 0
    detail: dict[str, Any] = {}

    text = _latest_user_chat_text(db, user_id)
    if text:
        crisis = detect_crisis(0, {}, 0, text=text)
        lvl = str(crisis.get("level", ""))
        if "Immediate" in lvl or "Crisis" in lvl:
            score += 50
            detail["crisis_detector"] = lvl
        mh = assess_mental_health(text)
        if mh.crisis_level in (CrisisLevel.SUICIDAL, CrisisLevel.SHAME_DESPAIR):
            score += 40
            detail["mental_health"] = mh.crisis_level.value
        bet = assess_betting_behavior(text)
        if bet.risk_level == RiskLevel.HIGH:
            score += 20
            detail["betting"] = bet.risk_level.value

    debt_doc = db.debts.find_one({"user_id": user_id}, sort=[("created_at", -1)])
    if debt_doc and debt_doc.get("trap"):
        trap = debt_doc["trap"]
        st = str(trap.get("status", ""))
        if "Trap" in st or trap.get("spiral_detected"):
            score += 30
            detail["debt_trap"] = st
    elif debt_doc and debt_doc.get("burden"):
        # Re-run trap detector from last saved totals if trap blob missing
        debts = debt_doc.get("debts") or []
        income = 25_000.0
        princ = sum(float(d.get("principal", 0)) for d in debts)
        if princ > 0 and debts:
            income = max(float(debt_doc.get("monthly_income", 25_000)), 1.0)
            hist = _synthetic_trap_history(princ, income)
            trap = detect_debt_trap(hist, income)
            if str(trap.get("status", "")).startswith("Debt Trap") or trap.get("spiral_detected"):
                score += 30
                detail["debt_trap"] = trap.get("status")

    mh_log = db.mental_health_logs.find_one({"user_id": user_id}, sort=[("created_at", -1)])
    if mh_log and mh_log.get("flagged") and "mental_health" not in detail:
        if mh_log.get("crisis_level") in ("suicidal", "shame_despair"):
            score += 40
            detail["mental_health_log"] = mh_log.get("crisis_level")

    return score, detail


def alerts_for_assigned_users(
    users_coll: Collection,
    db: Database,
    counsellor_id: ObjectId,
    min_score: int = 50,
) -> list[dict[str, Any]]:
    """Citizens assigned to this counsellor with score > threshold."""
    out: list[dict[str, Any]] = []
    for u in users_coll.find({"counsellor_id": counsellor_id, "role": "citizen"}):
        uid = u["_id"]
        s, detail = score_citizen(db, uid)
        if s > min_score:
            out.append(
                {
                    "user_id": str(uid),
                    "name": u.get("name", ""),
                    "email": u.get("email", ""),
                    "score": s,
                    "detail": detail,
                }
            )
    out.sort(key=lambda x: -x["score"])
    return out
