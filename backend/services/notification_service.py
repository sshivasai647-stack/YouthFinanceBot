# Purpose: In-app notifications + optional email alerts (Sections 10–11).
# Existing module dependencies: backend.extensions.mail, Flask-Mail.

"""Create notification documents and send user emails when configured."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from bson import ObjectId
from flask import current_app
from flask_mail import Message
from pymongo.collection import Collection

from backend.extensions import mail


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def notify_user(
    coll: Collection,
    *,
    user_id: ObjectId,
    notif_type: str,
    message: str,
    send_email: bool = True,
    email_subject: str | None = None,
    recipient_email: str | None = None,
    dedup_key: str | None = None,
    dedup_hours: int = 24,
) -> dict[str, Any] | None:
    """
    Insert a notification. If ``dedup_key`` is set, skip when an identical
    unread/any notification exists within ``dedup_hours`` for that user.
    Returns inserted doc with ``_id`` as str, or None if skipped.
    """
    if dedup_key:
        since = _utc_now() - timedelta(hours=dedup_hours)
        exists = coll.find_one(
            {
                "user_id": user_id,
                "dedup_key": dedup_key,
                "created_at": {"$gte": since},
            }
        )
        if exists:
            return None

    doc: dict[str, Any] = {
        "user_id": user_id,
        "type": notif_type,
        "message": message,
        "read": False,
        "created_at": _utc_now(),
    }
    if dedup_key:
        doc["dedup_key"] = dedup_key
    ins = coll.insert_one(doc)
    doc["_id"] = ins.inserted_id

    if send_email and recipient_email:
        try:
            subject = email_subject or f"YouthFinanceBot — {notif_type.replace('_', ' ').title()}"
            body = message + "\n\n— YouthFinanceBot"
            msg = Message(subject=subject, recipients=[recipient_email], body=body)
            mail.send(msg)
        except Exception as exc:  # noqa: BLE001 — never fail API on mail errors
            current_app.logger.warning("notification email failed: %s", exc)

    return doc


def get_user_email(users: Collection, user_id: ObjectId) -> str | None:
    u = users.find_one({"_id": user_id}, {"email": 1})
    return str(u["email"]) if u and u.get("email") else None
