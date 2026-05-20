# Purpose: Role-based access control decorator for protected API routes.
# Existing module dependencies: flask-jwt-extended (JWT claims set in backend.routes.auth).

"""Require JWT authentication and one of the allowed user roles."""

from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

from flask import jsonify
from flask_jwt_extended import get_jwt, jwt_required

F = TypeVar("F", bound=Callable[..., Any])


def role_required(*allowed_roles: str) -> Callable[[F], F]:
    """Restrict a view to users whose JWT ``role`` claim is in ``allowed_roles``."""

    allowed = frozenset(allowed_roles)

    def decorator(fn: F) -> F:
        @jwt_required()
        @wraps(fn)
        def wrapped(*args: Any, **kwargs: Any):
            claims = get_jwt()
            role = claims.get("role", "")
            if role not in allowed:
                return jsonify({"error": "Forbidden: insufficient role"}), 403
            return fn(*args, **kwargs)

        return wrapped  # type: ignore[return-value]

    return decorator