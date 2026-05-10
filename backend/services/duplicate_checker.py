# Purpose: Detect duplicate investment plans / goals before MongoDB inserts (Section 6.2).
# Existing module dependencies: pymongo via caller; no domain module duplication.

"""Parameter hashing and similarity lookup for deduplicated financial records."""

from __future__ import annotations

import hashlib
from typing import Any

from bson import ObjectId
from bson.errors import InvalidId
from pymongo.collection import Collection


def investment_parameter_hash(income: float, goals_list: list[str], risk_level: str) -> str:
    """Stable hash for comparable investment-plan inputs."""
    norm_goals = "|".join(sorted(g.strip().lower() for g in goals_list))
    payload = f"{round(float(income), 2)}|{norm_goals}|{risk_level.strip().lower()}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def goal_parameter_hash(name: str, target_amount: float, deadline_months: int) -> str:
    """Stable hash for comparable goal definitions."""
    payload = f"{name.strip().lower()}|{round(float(target_amount), 2)}|{int(deadline_months)}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def find_duplicate_investment_plan(
    coll: Collection,
    user_id: ObjectId,
    parameter_hash: str,
) -> dict[str, Any] | None:
    """Return newest matching investment plan for user + hash, or None."""
    return coll.find_one(
        {"user_id": user_id, "parameter_hash": parameter_hash},
        sort=[("created_at", -1)],
    )


def find_duplicate_goal(
    coll: Collection,
    user_id: ObjectId,
    parameter_hash: str,
) -> dict[str, Any] | None:
    """Return newest matching goal for user + hash, or None."""
    return coll.find_one(
        {"user_id": user_id, "parameter_hash": parameter_hash},
        sort=[("created_at", -1)],
    )


def parse_object_id(raw: str) -> ObjectId | None:
    try:
        return ObjectId(raw)
    except (InvalidId, TypeError):
        return None
