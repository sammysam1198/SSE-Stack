import os
import re
from flask import Blueprint, request, jsonify, session
from repos.users_repo import update_last_login, get_user_by_email, update_user_password_hash, mark_email_verified
from utils.auth_utils import verify_password
from utils.auth_utils import hash_password
from utils.token_utils import generate_raw_token, hash_token, expiry_from_now
from utils.mail_utils import send_password_reset_email
from utils.security_utils import get_request_ip
from repos.user_action_tokens_repo import (
    create_user_action_token,
    get_valid_user_action_token,
    invalidate_user_tokens,
    mark_user_action_token_used,
)

auth_bp = Blueprint("auth", __name__)

@auth_bp.post("/signin")
def signin():
    data = request.get_json(silent=True) or {}

    raw_email = data.get("email")
    email = (raw_email or "").strip().lower()
    password = data.get("password") or ""

    print("DEBUG SIGNIN raw_email =", repr(raw_email))
    print("DEBUG SIGNIN normalized_email =", repr(email))

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    user = get_user_by_email(email)

    print("DEBUG SIGNIN db_user =", user)

    if not user:
        return jsonify({
            "error": "User not found.",
            "debug_email": email
        }), 404

    if not user["is_active"]:
        return jsonify({"error": "Account is inactive."}), 403

    if user["is_locked"]:
        return jsonify({"error": "Account is locked."}), 403

    password_ok = verify_password(password, user["password_hash"])
    print("DEBUG SIGNIN password_ok =", password_ok)

    if not password_ok:
        return jsonify({"error": "Invalid credentials."}), 401

    session["user_id"] = user["id"]
    session["role"] = user["role"]

    ip = get_request_ip()
    update_last_login(user["id"], ip)

    return jsonify({
        "message": "Signed in successfully.",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "role": user["role"],
        }
    }), 200

@auth_bp.post("/signout")
def signout():
    session.clear()
    return jsonify({"message": "Signed out successfully."}), 200


@auth_bp.get("/me")
def me():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Not authenticated."}), 401

    from repos.users_repo import get_user_by_id

    user = get_user_by_id(user_id)

    if not user:
        return jsonify({"error": "User not found."}), 404

    return jsonify({
        "user": {
            "id": user["id"],
            "email": user["email"],
            "role": user["role"],
            "is_impersonating": bool(session.get("is_impersonating")),
            "impersonator_user_id": session.get("impersonator_user_id"),
            "impersonator_role": session.get("impersonator_role"),
        }
    }), 200


@auth_bp.post("/request-email-change")
def request_email_change():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated."}), 401

    data = request.get_json(silent=True) or {}
    new_email = (data.get("new_email") or "").strip().lower()

    if not new_email:
        return jsonify({"error": "New email is required."}), 400

    # TODO:
    # 1. generate email change token
    # 2. store hashed token in email_change_tokens
    # 3. send confirmation email to new email

    return jsonify({"message": "Email change confirmation sent."}), 200


@auth_bp.post("/confirm-email-change")
def confirm_email_change():
    data = request.get_json(silent=True) or {}
    token = (data.get("token") or "").strip()

    if not token:
        return jsonify({"error": "Token is required."}), 400

    # TODO:
    # 1. verify token
    # 2. update user email
    # 3. mark token used

    return jsonify({"message": "Email changed successfully."}), 200


@auth_bp.post("/verify-email")
def verify_email():
    data = request.get_json(silent=True) or {}
    token = (data.get("token") or "").strip()

    if not token:
        return jsonify({"error": "Token is required."}), 400

    # TODO: verify email token when you add that flow
    return jsonify({"message": "Email verified successfully."}), 200


@auth_bp.post("/challenge/start")
def start_login_challenge():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()

    if not email:
        return jsonify({"error": "Email is required."}), 400

    # TODO:
    # 1. identify user
    # 2. create login challenge
    # 3. send email code or prepare TOTP step

    return jsonify({"message": "Challenge started."}), 200


@auth_bp.post("/challenge/verify")
def verify_login_challenge():
    data = request.get_json(silent=True) or {}

    email = (data.get("email") or "").strip().lower()
    code = (data.get("code") or "").strip()

    if not email or not code:
        return jsonify({"error": "Email and code are required."}), 400

    # TODO:
    # 1. verify login challenge
    # 2. complete login session

    return jsonify({"message": "Challenge verified."}), 200

@auth_bp.post("/request-password-reset")
def request_password_reset():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()

    if not email:
        return jsonify({
            "message": "If that email exists, a reset link has been sent."
        }), 200

    user = get_user_by_email(email)

    if user:
        invalidate_user_tokens(user["id"], "password_reset")

        raw_token = generate_raw_token()
        token_hash = hash_token(raw_token)
        expires_at = expiry_from_now(30)

        create_user_action_token(
            user_id=user["id"],
            email=email,
            token_hash=token_hash,
            token_type="password_reset",
            expires_at=expires_at,
        )

        frontend_base = os.getenv("FRONTEND_ORIGIN", "https://www.spacedoutstudiosent.com")
        reset_url = f"{frontend_base}/reset-password?token={raw_token}"

        send_password_reset_email(email, reset_url)

    return jsonify({
        "message": "If that email exists, a reset link has been sent."
    }), 200

@auth_bp.post("/reset-password")
def reset_password():
    data = request.get_json(silent=True) or {}

    raw_token = (data.get("token") or "").strip()
    new_password = data.get("new_password") or ""

    if not raw_token or not new_password:
        return jsonify({"error": "Token and new password are required."}), 400

    if len(new_password) < 8:
        return jsonify({"error": "Password must be at least 8 characters."}), 400

    if not re.search(r"[A-Z]", new_password):
        return jsonify({"error": "Password must include at least one uppercase letter."}), 400

    if not re.search(r"\d", new_password):
        return jsonify({"error": "Password must include at least one number."}), 400

    token_hash = hash_token(raw_token)
    token_record = get_valid_user_action_token(token_hash, "password_reset")

    if not token_record:
        return jsonify({"error": "Invalid or expired token."}), 400

    new_password_hash = hash_password(new_password)

    update_user_password_hash(token_record["user_id"], new_password_hash)

    mark_user_action_token_used(token_record["id"])
    invalidate_user_tokens(token_record["user_id"], "password_reset")

    return jsonify({"message": "Password has been reset successfully."}), 200


@auth_bp.post("/setup-account")
def setup_account():
    data = request.get_json(silent=True) or {}

    raw_token = (data.get("token") or "").strip()
    new_password = data.get("new_password") or ""

    if not raw_token or not new_password:
        return jsonify({"error": "Token and new password are required."}), 400

    if len(new_password) < 8:
        return jsonify({"error": "Password must be at least 8 characters."}), 400

    if not re.search(r"[A-Z]", new_password):
        return jsonify({"error": "Password must include at least one uppercase letter."}), 400

    if not re.search(r"\d", new_password):
        return jsonify({"error": "Password must include at least one number."}), 400

    token_hash = hash_token(raw_token)
    token_record = get_valid_user_action_token(token_hash, "setup_account")

    if not token_record:
        return jsonify({"error": "Invalid or expired token."}), 400

    new_password_hash = hash_password(new_password)

    update_user_password_hash(token_record["user_id"], new_password_hash)
    mark_email_verified(token_record["user_id"])

    mark_user_action_token_used(token_record["id"])
    invalidate_user_tokens(token_record["user_id"], "setup_account")

    return jsonify({"message": "Account setup complete."}), 200


@auth_bp.get("/validate-setup-token")
def validate_setup_token():
    raw_token = (request.args.get("token") or "").strip()

    if not raw_token:
        return jsonify({"valid": False, "error": "Missing token."}), 400

    token_hash = hash_token(raw_token)
    token_record = get_valid_user_action_token(token_hash, "setup_account")

    if not token_record:
        return jsonify({"valid": False, "error": "Invalid or expired token."}), 400

    return jsonify({"valid": True}), 200