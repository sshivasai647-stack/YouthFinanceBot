# Purpose: Initialize MongoDB collections and indexes for YouthFinanceBot.
# Existing module dependencies: None (database bootstrap utility).

"""MongoDB setup utility for Step 1 of the build order."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from pymongo import ASCENDING, DESCENDING, MongoClient


load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/youth_finance_bot")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "youth_finance_bot")

COLLECTIONS = [
    "users",
    "investment_plans",
    "debts",
    "goals",
    "spending_logs",
    "chat_sessions",
    "mental_health_logs",
    "notifications",
    "counsellor_notes",
    "audit_logs",
    "scheme_matches",
    "ai_usage",
]


def init_collections_and_indexes() -> None:
    """Create required collections and indexes."""

    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB_NAME]

    for collection_name in COLLECTIONS:
        if collection_name not in db.list_collection_names():
            db.create_collection(collection_name)

    # Required indexes from build order Step 1
    db.users.create_index([("email", ASCENDING)], unique=True, name="uniq_users_email")
    db.chat_sessions.create_index(
        [("user_id", ASCENDING), ("updated_at", DESCENDING)],
        name="idx_chat_user_updated_desc",
    )
    db.goals.create_index([("user_id", ASCENDING)], name="idx_goals_user_id")

    # Useful support indexes for upcoming routes
    db.notifications.create_index([("user_id", ASCENDING), ("read", ASCENDING)], name="idx_notif_user_read")
    db.audit_logs.create_index([("timestamp", DESCENDING)], name="idx_audit_timestamp_desc")
    db.investment_plans.create_index([("user_id", ASCENDING), ("updated_at", DESCENDING)], name="idx_inv_user_updated")
    db.investment_plans.create_index(
        [("user_id", ASCENDING), ("parameter_hash", ASCENDING)],
        name="idx_inv_user_param_hash",
    )
    db.goals.create_index(
        [("user_id", ASCENDING), ("parameter_hash", ASCENDING)],
        name="idx_goals_user_param_hash",
    )
    db.ai_usage.create_index([("created_at", DESCENDING)], name="idx_ai_usage_created")
    db.users.create_index([("counsellor_id", ASCENDING)], name="idx_users_counsellor")

    client.close()


if __name__ == "__main__":
    init_collections_and_indexes()
    print("MongoDB collections and indexes initialized.")
