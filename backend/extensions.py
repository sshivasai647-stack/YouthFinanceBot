# Purpose: Initialize and expose shared Flask extensions for app factory usage.
# Existing module dependencies: None (infrastructure-only extension wiring).

"""Extension instances and MongoDB helpers."""

from __future__ import annotations

from flask import Flask, current_app, g
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail
from pymongo import MongoClient
from pymongo.database import Database


jwt = JWTManager()
mail = Mail()
limiter = Limiter(key_func=get_remote_address)


def init_extensions(app: Flask) -> None:
    """Bind all configured extensions to the Flask app."""

    jwt.init_app(app)  # Re-enabled but will bypass in role_required
    mail.init_app(app)
    limiter.init_app(app)


def get_mongo_client(app: Flask) -> MongoClient:
    """Create a MongoDB client instance using Flask config."""

    return MongoClient(app.config["MONGO_URI"], serverSelectionTimeoutMS=2000)


def get_db() -> Database:
    """
    Return request-scoped MongoDB database connection.

    The connection is memoized in Flask's `g` object to avoid duplicate clients
    during a request lifecycle.
    """

    if "mongo_db" not in g:
        client = MongoClient(current_app.config["MONGO_URI"], serverSelectionTimeoutMS=2000)
        g.mongo_client = client
        g.mongo_db = client[current_app.config["MONGO_DB_NAME"]]
    return g.mongo_db


def close_mongo(error: BaseException | None = None) -> None:
    """Close the request-scoped MongoDB client if it exists."""

    _ = error
    client = g.pop("mongo_client", None)
    g.pop("mongo_db", None)
    if client is not None:
        client.close()
