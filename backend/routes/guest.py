# Purpose: Anonymous “Try as guest” chat — server session storage only (no MongoDB PII).
# Existing module dependencies: backend.services.chat_router (same LLM pipeline as citizens).

"""Guest API routes — session-backed chat history, no JWT."""

from __future__ import annotations

from datetime import datetime, timezone

from flask import Blueprint, jsonify, request, session
from marshmallow import Schema, ValidationError, fields, validate

from backend.extensions import limiter
from backend.services.chat_router import run_chat_pipeline
from backend.services.serialize import to_jsonable

guest_bp = Blueprint("guest", __name__, url_prefix="/api/guest")

SESSION_MESSAGES_KEY = "yfb_guest_chat_messages"
MAX_GUEST_MESSAGES = 200


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class GuestChatSchema(Schema):
    message = fields.Str(required=True, validate=validate.Length(min=1, max=8000))
    chat_history = fields.List(fields.Dict(), load_default=lambda: [])
    income = fields.Float(load_default=0.0)
    savings_rate = fields.Float(load_default=0.0)
    age = fields.Int(load_default=22)
    risk_appetite = fields.Str(load_default="medium")
    goal = fields.Str(load_default="retirement")
    expenses = fields.Dict(keys=fields.Str(), values=fields.Float(), load_default=lambda: {})
    debts = fields.List(fields.Dict(), load_default=lambda: [])
    skills = fields.List(fields.Str(), load_default=lambda: [])
    debt_monthly = fields.Float(load_default=0.0)
    goal_target_amount = fields.Float(load_default=None, allow_none=True)
    goal_months = fields.Int(load_default=None, allow_none=True)
    goal_monthly_saving = fields.Float(load_default=None, allow_none=True)


@guest_bp.post("/chat")
@limiter.limit("20 per minute")
def guest_chat():
    try:
        body = GuestChatSchema().load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "details": err.messages}), 400

    hist_raw = body.get("chat_history") or []
    hist: list[dict[str, str]] = []
    for m in hist_raw:
        if isinstance(m, dict) and m.get("role") and m.get("content") is not None:
            hist.append({"role": str(m["role"]), "content": str(m["content"])})

    pipeline = run_chat_pipeline(
        user_message=body["message"].strip(),
        chat_history=hist,
        income=float(body.get("income", 0)),
        savings_rate=float(body.get("savings_rate", 0)),
        age=int(body.get("age", 22)),
        risk_appetite=str(body.get("risk_appetite", "medium")),
        goal=str(body.get("goal", "retirement")),
        expenses=body.get("expenses") or {},
        debts_payload=body.get("debts") or [],
        skills=body.get("skills") or [],
        monthly_debt_payment=float(body.get("debt_monthly", 0)),
        goal_target_amount=body.get("goal_target_amount"),
        goal_months=body.get("goal_months"),
        goal_monthly_saving=body.get("goal_monthly_saving"),
    )

    now = _utc_now()
    store = session.get(SESSION_MESSAGES_KEY) or []
    store.extend(
        [
            {"role": "user", "content": body["message"].strip(), "timestamp": now.isoformat()},
            {
                "role": "assistant",
                "content": pipeline["reply"],
                "timestamp": now.isoformat(),
                "route": pipeline["route"],
            },
        ]
    )
    session[SESSION_MESSAGES_KEY] = store[-MAX_GUEST_MESSAGES:]
    session.modified = True

    return jsonify(
        {
            "reply": pipeline["reply"],
            "route": pipeline["route"],
            "suggestions": pipeline["suggestions"],
            "detection": pipeline["detection"],
            "context": to_jsonable(pipeline.get("context") or {}),
            "skip_llm": bool(pipeline.get("skip_llm")),
            "llm_error": pipeline.get("llm_error"),
        }
    ), 200


@guest_bp.get("/chat/history")
def guest_chat_history():
    msgs = session.get(SESSION_MESSAGES_KEY) or []
    return jsonify({"messages": msgs[-50:]}), 200


@guest_bp.post("/session/clear")
def guest_clear_session():
    """Clear guest chat from the server session cookie."""
    session.pop(SESSION_MESSAGES_KEY, None)
    session.modified = True
    return jsonify({"message": "Guest chat cleared"}), 200
