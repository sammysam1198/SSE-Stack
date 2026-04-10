from flask import Blueprint, request, jsonify, session
from repos.users_repo import get_user_by_email, update_last_login
from utils.auth_utils import verify_password
from utils.security_utils import get_request_ip

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/signin")
def signin():
    data = request.get_json(silent=True) or {}

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    user = get_user_by_email(email)

    if not user:
        return jsonify({"error": "Invalid credentials."}), 401

    if not user["is_active"]:
        return jsonify({"error": "Account is inactive."}), 403

    if user["is_locked"]:
        return jsonify({"error": "Account is locked."}), 403

    if not verify_password(password, user["password_hash"]):
        return jsonify({"error": "Invalid credentials."}), 401

    #  Create session
    session["user_id"] = user["id"]
    session["role"] = user["role"]

    # Update login info
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
        }
    }), 200


@auth_bp.post("/request-password-reset")
def request_password_reset():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()

    if not email:
        return jsonify({"error": "Email is required."}), 400

    # TODO:
    # 1. find user by email
    # 2. generate reset token
    # 3. store hashed token in password_reset_tokens
    # 4. send email via mail utility

    return jsonify({
        "message": "If that account exists, a password reset email has been sent."
    }), 200


@auth_bp.post("/reset-password")
def reset_password():
    data = request.get_json(silent=True) or {}

    token = (data.get("token") or "").strip()
    new_password = data.get("new_password") or ""

    if not token or not new_password:
        return jsonify({"error": "Token and new password are required."}), 400

    # TODO:
    # 1. verify token
    # 2. hash new password
    # 3. update users.password_hash
    # 4. mark token used

    return jsonify({"message": "Password reset successfully."}), 200


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