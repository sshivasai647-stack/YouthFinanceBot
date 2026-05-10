# Purpose: Authentication endpoints for register/login/logout/token/OTP/password reset flows.
# Existing module dependencies: None (auth infrastructure only; domain modules are wired in later steps).

"""Auth routes for YouthFinanceBot."""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import requests
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies,
)
from flask_mail import Message
from marshmallow import Schema, ValidationError, fields, validate
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from backend.extensions import get_db, limiter, mail


auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


class RegisterSchema(Schema):
    """Input schema for registration."""

    name = fields.Str(required=True, validate=validate.Length(min=2, max=80))
    age = fields.Int(required=True, validate=validate.Range(min=16, max=35))
    email = fields.Email(required=True)
    phone = fields.Str(required=True, validate=validate.Length(min=8, max=20))
    password = fields.Str(required=True, validate=validate.Length(min=8, max=128))
    role = fields.Str(load_default="citizen", validate=validate.OneOf(["citizen"]))
    captcha_token = fields.Str(required=True, validate=validate.Length(min=8))


class LoginSchema(Schema):
    """Input schema for login."""

    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8, max=128))
    captcha_token = fields.Str(required=True, validate=validate.Length(min=8))


class VerifyOtpSchema(Schema):
    """Input schema for OTP verification."""

    email = fields.Email(required=True)
    otp = fields.Str(required=True, validate=validate.Length(equal=6))


class ForgotPasswordSchema(Schema):
    """Input schema for forgot password."""

    email = fields.Email(required=True)


class ResetPasswordSchema(Schema):
    """Input schema for password reset."""

    token = fields.Str(required=True, validate=validate.Length(min=20))
    password = fields.Str(required=True, validate=validate.Length(min=8, max=128))


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _check_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def _gen_otp() -> str:
    return f"{secrets.randbelow(1000000):06d}"


def _validate_hcaptcha(captcha_token: str) -> bool:
    secret = current_app.config.get("HCAPTCHA_SECRET", "").strip()
    if not secret or current_app.config.get("DEBUG"):
        return True
    try:
        response = requests.post(
            "https://hcaptcha.com/siteverify",
            data={"secret": secret, "response": captcha_token},
            timeout=8,
        )
        payload = response.json()
        return bool(payload.get("success"))
    except Exception:
        return False


def _send_mail(subject: str, recipients: list[str], body: str) -> None:
    if not recipients:
        return
    try:
       msg = Message(subject=subject, recipients=recipients, body=body)
       mail.send(msg)
    except Exception as e:
        current_app.logger.error(f"Failed to send email to {recipients}: {e}")


def _extract_device_fingerprint() -> str:
    ip = request.headers.get("X-Forwarded-For", request.remote_addr or "")
    ua = request.headers.get("User-Agent", "")
    raw = f"{ip}|{ua}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _user_payload(user: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(user["_id"]),
        "email": user["email"],
        "name": user.get("name", ""),
        "role": user.get("role", "citizen"),
        "is_verified": user.get("is_verified", False),
    }


@auth_bp.post("/register")
@limiter.limit("10 per hour")
def register():
    """Register a new account and send OTP for verification."""

    try:
        payload = RegisterSchema().load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": "Invalid request payload", "details": err.messages}), 400

    if not _validate_hcaptcha(payload["captcha_token"]):
        return jsonify({"error": "Captcha validation failed"}), 400

    db = get_db()
    email = payload["email"].strip().lower()
    now = _utc_now()
    otp = _gen_otp()
    otp_exp = now + timedelta(minutes=current_app.config["OTP_EXP_MINUTES"])

    user_doc = {
        "email": email,
        "phone": payload["phone"].strip(),
        "name": payload["name"].strip(),
        "age": payload["age"],
        "password_hash": _hash_password(payload["password"]),
        "role": payload["role"],
        "is_active": True,
        "is_verified": False,
        "created_at": now,
        "last_login": None,
        "counsellor_id": None,
        "otp": otp,
        "otp_expires": otp_exp,
        "reset_token": None,
        "reset_expires": None,
        "last_device_hash": None,
    }
    if payload["role"] == "citizen":
        user_doc["counselling_status"] = "active"

    try:
        db.users.insert_one(user_doc)
    except DuplicateKeyError:
        return jsonify({"error": "Email already registered"}), 409

    _send_mail(
        subject="YouthFinanceBot OTP Verification",
        recipients=[email],
        body=f"Your OTP is {otp}. It expires in {current_app.config['OTP_EXP_MINUTES']} minutes.",
    )
    return jsonify({"message": "Registered successfully. Please verify OTP sent to email."}), 201


@auth_bp.post("/verify-otp")
@limiter.limit("10 per hour")
def verify_otp():
    """Verify registration OTP and activate account."""

    try:
        payload = VerifyOtpSchema().load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": "Invalid request payload", "details": err.messages}), 400

    db = get_db()
    email = payload["email"].strip().lower()
    user = db.users.find_one({"email": email})
    if not user:
        return jsonify({"error": "User not found"}), 404

    if user.get("is_verified"):
        return jsonify({"message": "User already verified"}), 200

    otp_exp = user.get("otp_expires")
    stored_otp = user.get("otp")
    submitted_otp = payload["otp"]
    
    # DEBUG LOGGING
    current_app.logger.info(f"Stored OTP: {stored_otp}")
    current_app.logger.info(f"Submitted OTP: {submitted_otp}")
    current_app.logger.info(f"OTP Match: {stored_otp == submitted_otp}")
    current_app.logger.info(f"OTP Expires: {otp_exp}")
    current_app.logger.info(f"Current Time: {_utc_now()}")
    
    if not otp_exp:
        return jsonify({"error": "Invalid or expired OTP"}), 400

    # Make timezone-aware if MongoDB returns naive datetime
    if otp_exp.tzinfo is None:
        otp_exp = otp_exp.replace(tzinfo=timezone.utc)

    if stored_otp != submitted_otp or otp_exp < _utc_now():
        return jsonify({"error": "Invalid or expired OTP"}), 400

    db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"is_verified": True}, "$unset": {"otp": "", "otp_expires": ""}},
    )
    return jsonify({"message": "OTP verified successfully"}), 200


@auth_bp.post("/login")
@limiter.limit("5 per 15 minutes")
def login():
    """Authenticate user and issue access + refresh cookies."""

    try:
        payload = LoginSchema().load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": "Invalid request payload", "details": err.messages}), 400

    if not _validate_hcaptcha(payload["captcha_token"]):
        return jsonify({"error": "Captcha validation failed"}), 400

    db = get_db()
    email = payload["email"].strip().lower()
    user = db.users.find_one({"email": email})
    if not user or not _check_password(payload["password"], user.get("password_hash", "")):
        return jsonify({"error": "Invalid credentials"}), 401

    if not user.get("is_active", True):
        return jsonify({"error": "Account is deactivated"}), 403
    if not user.get("is_verified", False):
        return jsonify({"error": "Please verify OTP before login"}), 403

    device_hash = _extract_device_fingerprint()
    last_device_hash = user.get("last_device_hash")
    if last_device_hash and last_device_hash != device_hash:
        _send_mail(
            subject="New login detected - YouthFinanceBot",
            recipients=[email],
            body="We detected a login from a new device/location. If this wasn't you, reset your password immediately.",
        )

    additional_claims = {"role": user.get("role", "citizen"), "email": user["email"]}
    identity = str(user["_id"])
    access_token = create_access_token(identity=identity, additional_claims=additional_claims)
    refresh_token = create_refresh_token(identity=identity, additional_claims=additional_claims)

    db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"last_login": _utc_now(), "last_device_hash": device_hash}},
    )

    response = jsonify({"message": "Login successful", "user": _user_payload(user)})
    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)
    return response, 200


@auth_bp.post("/logout")
def logout():
    """Clear JWT cookies."""

    response = jsonify({"message": "Logout successful"})
    unset_jwt_cookies(response)
    return response, 200


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    """Issue a new access token using a valid refresh token cookie."""

    identity = get_jwt_identity()
    db = get_db()
    user = db.users.find_one({"_id": ObjectId(identity)})
    if not user or not user.get("is_active", True):
        return jsonify({"error": "User not active"}), 403

    additional_claims = {"role": user.get("role", "citizen"), "email": user["email"]}
    access_token = create_access_token(identity=identity, additional_claims=additional_claims)
    response = jsonify({"message": "Token refreshed"})
    set_access_cookies(response, access_token)
    return response, 200


@auth_bp.post("/forgot-password")
@limiter.limit("5 per hour")
def forgot_password():
    """Generate a reset token and send password reset email."""

    try:
        payload = ForgotPasswordSchema().load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": "Invalid request payload", "details": err.messages}), 400

    db = get_db()
    email = payload["email"].strip().lower()
    user = db.users.find_one({"email": email})

    if user and user.get("is_active", True):
        token = secrets.token_urlsafe(32)
        expires = _utc_now() + timedelta(minutes=current_app.config["RESET_EXP_MINUTES"])
        db.users.update_one(
            {"_id": user["_id"]},
            {"$set": {"reset_token": token, "reset_expires": expires}},
        )
        reset_url = f"{current_app.config['PASSWORD_RESET_BASE_URL']}?token={token}"
        _send_mail(
            subject="Reset your YouthFinanceBot password",
            recipients=[email],
            body=f"Use this link to reset your password: {reset_url}\nThis link expires in {current_app.config['RESET_EXP_MINUTES']} minutes.",
        )

    return jsonify({"message": "If the account exists, a reset link has been sent."}), 200


@auth_bp.post("/reset-password")
@limiter.limit("10 per hour")
def reset_password():
    """Reset password using a valid reset token."""

    try:
        payload = ResetPasswordSchema().load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": "Invalid request payload", "details": err.messages}), 400

    db = get_db()
    user = db.users.find_one({"reset_token": payload["token"]})
    if not user:
        return jsonify({"error": "Invalid reset token"}), 400

    reset_exp = user.get("reset_expires")
    if not reset_exp or reset_exp < _utc_now():
        return jsonify({"error": "Reset token expired"}), 400

    new_hash = _hash_password(payload["password"])
    db.users.update_one(
        {"_id": user["_id"]},
        {
            "$set": {"password_hash": new_hash},
            "$unset": {"reset_token": "", "reset_expires": ""},
        },
    )
    return jsonify({"message": "Password reset successful"}), 200
