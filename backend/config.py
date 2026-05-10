# Purpose: Centralized Flask configuration for YouthFinanceBot backend.
# Existing module dependencies: None (infrastructure-only configuration).

"""Configuration objects for Flask application setup."""

from __future__ import annotations

import os
from datetime import timedelta

from dotenv import load_dotenv


load_dotenv()


class Config:
    """Base configuration loaded from environment variables."""

    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/youth_finance_bot")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "youth_finance_bot")

    FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-jwt-secret")
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_COOKIE_SECURE = os.getenv("JWT_COOKIE_SECURE", "false").lower() == "true"
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    JWT_COOKIE_SAMESITE = os.getenv("JWT_COOKIE_SAMESITE", "Lax")

    RATELIMIT_STORAGE_URI = os.getenv("RATELIMIT_STORAGE_URI", "memory://")
    RATELIMIT_DEFAULT = "100 per hour"

    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "false").lower() == "true"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "noreply@youthfinancebot.local")

    HCAPTCHA_SECRET = os.getenv("HCAPTCHA_SECRET", "")
    OTP_EXP_MINUTES = int(os.getenv("OTP_EXP_MINUTES", "10"))
    RESET_EXP_MINUTES = int(os.getenv("RESET_EXP_MINUTES", "30"))
    PASSWORD_RESET_BASE_URL = os.getenv("PASSWORD_RESET_BASE_URL", "http://localhost:3000/reset-password")


class DevelopmentConfig(Config):
    """Local development settings."""

    DEBUG = True


class ProductionConfig(Config):
    """Production settings."""

    DEBUG = False
