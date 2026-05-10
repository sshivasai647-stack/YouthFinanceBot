# Purpose: Persist request audit trail to MongoDB ``audit_logs`` collection.
# Existing module dependencies: backend.extensions.get_db; JWT optional via flask-jwt-extended.

"""Register Flask hooks to record API requests for compliance and debugging."""

from __future__ import annotations

from datetime import datetime, timezone

from flask import Flask, current_app, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from backend.extensions import get_db


def _client_ip() -> str:
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or ""


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def register_audit_logger(app: Flask) -> None:
    """
    Log each ``/api/*`` request (except CORS preflight) to ``audit_logs``.

    Fields align with Section 7: user_id, action (HTTP method), endpoint (path),
    ip, timestamp. Unauthenticated requests store ``user_id`` as null.
    """

    @app.after_request
    def _audit_after_request(response):  # type: ignore[no-untyped-def]
        if request.method == "OPTIONS":
            return response
        path = request.path or ""
        if not path.startswith("/api"):
            return response

        user_id = None
        try:
            verify_jwt_in_request(optional=True)
            identity = get_jwt_identity()
            if identity is not None:
                user_id = str(identity)
        except Exception:
            user_id = None

        doc = {
            "user_id": user_id,
            "action": request.method,
            "endpoint": path,
            "ip": _client_ip(),
            "timestamp": _utc_now(),
        }
        try:
            get_db().audit_logs.insert_one(doc)
        except Exception as exc:  # noqa: BLE001 — never fail the response on audit failure
            current_app.logger.warning("audit_logs insert failed: %s", exc)
        return response
