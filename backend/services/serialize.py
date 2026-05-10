# Purpose: Convert API payloads to JSON-safe structures (Mongo ObjectId, enums, dataclasses).
# Existing module dependencies: None (utility only).

"""Serialization helpers for Flask JSON responses."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from enum import Enum
from typing import Any

from bson import ObjectId


def to_jsonable(obj: Any) -> Any:
    """Recursively convert values so ``jsonify`` / Mongo extended JSON works."""

    if obj is None:
        return None
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, date):
        return obj.isoformat()
    if isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, float):
        return obj if obj == obj else None  # NaN -> None
    if isinstance(obj, (str, int, bool)):
        return obj
    if isinstance(obj, dict):
        return {str(k): to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_jsonable(x) for x in obj]
    if is_dataclass(obj) and not isinstance(obj, type):
        return to_jsonable(asdict(obj))
    return str(obj)
