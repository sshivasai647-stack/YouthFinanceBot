# Purpose: Financial counsellor API — assigned citizens, notes, alerts (Section 4C).
# Existing module dependencies: backend.services.priority_scorer; pymongo.

"""Counsellor routes (role: counsellor)."""

from __future__ import annotations

from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity
from marshmallow import Schema, ValidationError, fields, validate

from backend.extensions import get_db
from backend.middleware.role_required import role_required
from backend.services.priority_scorer import alerts_for_assigned_users
from backend.services.serialize import to_jsonable

counsellor_bp = Blueprint("counsellor", __name__, url_prefix="/api/counsellor")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _counsellor_oid() -> ObjectId:
    return ObjectId(get_jwt_identity())


class NoteSchema(Schema):
    note = fields.Str(required=True, validate=validate.Length(min=3, max=4000))


class StatusSchema(Schema):
    counselling_status = fields.Str(
        required=True,
        validate=validate.OneOf(["active", "follow_up", "closed", "needs_attention"]),
    )


@counsellor_bp.get("/citizens")
@role_required("counsellor")
def list_citizens():
    db = get_db()
    cid = _counsellor_oid()
    page = max(int(request.args.get("page", "1")), 1)
    limit = min(max(int(request.args.get("limit", "20")), 1), 100)
    skip = (page - 1) * limit
    q = {"role": "citizen", "counsellor_id": cid}
    total = db.users.count_documents(q)
    items = []
    for u in db.users.find(q).sort("_id", -1).skip(skip).limit(limit):
        items.append(
            {
                "id": str(u["_id"]),
                "name": u.get("name", ""),
                "email": u.get("email", ""),
                "phone": u.get("phone", ""),
                "age": u.get("age"),
                "counselling_status": u.get("counselling_status", "active"),
                "created_at": u.get("created_at"),
                "last_login": u.get("last_login"),
            }
        )
    return jsonify({"total": total, "page": page, "citizens": items}), 200


@counsellor_bp.get("/citizens/<citizen_id>")
@role_required("counsellor")
def citizen_detail(citizen_id: str):
    try:
        oid = ObjectId(citizen_id)
    except InvalidId:
        return jsonify({"error": "Invalid citizen id"}), 400
    db = get_db()
    if not db.users.find_one({"_id": oid, "counsellor_id": _counsellor_oid()}):
        return jsonify({"error": "Not found or not assigned"}), 404
    u = db.users.find_one({"_id": oid})
    payload: dict = {
        "profile": {
            "id": str(u["_id"]),
            "name": u.get("name"),
            "email": u.get("email"),
            "phone": u.get("phone"),
            "age": u.get("age"),
            "counselling_status": u.get("counselling_status", "active"),
        },
        "investment_plans": [],
        "debts": [],
        "goals": [],
        "spending_logs": [],
        "chat_sessions": None,
        "recent_notes": [],
    }
    payload["investment_plans"] = to_jsonable(
        list(db.investment_plans.find({"user_id": oid}).sort("created_at", -1).limit(5))
    )
    payload["debts"] = to_jsonable(list(db.debts.find({"user_id": oid}).sort("created_at", -1).limit(5)))
    payload["goals"] = to_jsonable(list(db.goals.find({"user_id": oid}).sort("created_at", -1).limit(20)))
    payload["spending_logs"] = to_jsonable(
        list(db.spending_logs.find({"user_id": oid}).sort("created_at", -1).limit(5))
    )
    cs = db.chat_sessions.find_one({"user_id": oid})
    if cs:
        payload["chat_sessions"] = {
            "message_count": len(cs.get("messages") or []),
            "updated_at": cs.get("updated_at"),
        }
    payload["recent_notes"] = to_jsonable(
        list(db.counsellor_notes.find({"citizen_id": oid}).sort("created_at", -1).limit(30))
    )
    return jsonify(payload), 200


@counsellor_bp.post("/citizens/<citizen_id>/note")
@role_required("counsellor")
def add_note(citizen_id: str):
    try:
        oid = ObjectId(citizen_id)
    except InvalidId:
        return jsonify({"error": "Invalid citizen id"}), 400
    try:
        body = NoteSchema().load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "details": err.messages}), 400
    db = get_db()
    if not db.users.find_one({"_id": oid, "counsellor_id": _counsellor_oid()}):
        return jsonify({"error": "Not found or not assigned"}), 404
    now = _utc_now()
    doc = {
        "counsellor_id": _counsellor_oid(),
        "citizen_id": oid,
        "note": body["note"].strip(),
        "created_at": now,
    }
    ins = db.counsellor_notes.insert_one(doc)
    # Notify citizen (import here to avoid circular imports at module load)
    from backend.services.notification_service import get_user_email, notify_user

    email = get_user_email(db.users, oid)
    notify_user(
        db.notifications,
        user_id=oid,
        notif_type="counsellor_note",
        message="Your counsellor left a new note on your profile.",
        send_email=True,
        email_subject="YouthFinanceBot — Counsellor update",
        recipient_email=email,
    )
    return jsonify({"id": str(ins.inserted_id), "message": "Note saved"}), 201


@counsellor_bp.patch("/citizens/<citizen_id>/status")
@role_required("counsellor")
def patch_status(citizen_id: str):
    try:
        oid = ObjectId(citizen_id)
    except InvalidId:
        return jsonify({"error": "Invalid citizen id"}), 400
    try:
        body = StatusSchema().load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "details": err.messages}), 400
    db = get_db()
    res = db.users.update_one(
        {"_id": oid, "counsellor_id": _counsellor_oid()},
        {"$set": {"counselling_status": body["counselling_status"]}},
    )
    if res.matched_count == 0:
        return jsonify({"error": "Not found or not assigned"}), 404
    return jsonify({"message": "Status updated"}), 200


@counsellor_bp.get("/alerts")
@role_required("counsellor")
def counsellor_alerts():
    db = get_db()
    items = alerts_for_assigned_users(db.users, db, _counsellor_oid(), min_score=50)
    return jsonify({"alerts": items}), 200
