import os
from flask import Blueprint, jsonify, request, session
from repos.users_repo import get_user_by_email, create_user
from repos.user_action_tokens_repo import (
    create_user_action_token,
    invalidate_user_tokens,
)
from utils.token_utils import generate_raw_token, hash_token, expiry_from_now
from utils.auth_utils import hash_password
from utils.mail_utils import send_artist_invite_email

admin_bp = Blueprint("admin", __name__)


def _current_role():
    return session.get("role")


def _require_admin_or_dev():
    return _current_role() in {"admin", "developer"}


@admin_bp.get("/dashboard")
def admin_dashboard():
    if not _require_admin_or_dev():
        return jsonify({"error": "Forbidden."}), 403

    # TODO: aggregate counts for dashboard cards
    return jsonify({
        "dashboard": {
            "pending_applications": 0,
            "submitted_releases": 0,
            "open_contact_requests": 0,
            "pending_merch_requests": 0,
        }
    }), 200


@admin_bp.get("/artists")
def admin_list_artists():
    if not _require_admin_or_dev():
        return jsonify({"error": "Forbidden."}), 403

    # TODO
    return jsonify({"artists": []}), 200


@admin_bp.get("/users")
def admin_list_users():
    if not _require_admin_or_dev():
        return jsonify({"error": "Forbidden."}), 403

    # TODO
    return jsonify({"users": []}), 200


@admin_bp.get("/releases")
def admin_list_releases():
    if not _require_admin_or_dev():
        return jsonify({"error": "Forbidden."}), 403

    # TODO
    return jsonify({"releases": []}), 200


@admin_bp.get("/applications")
def admin_list_applications():
    if not _require_admin_or_dev():
        return jsonify({"error": "Forbidden."}), 403

    # TODO
    return jsonify({"applications": []}), 200


@admin_bp.get("/mail-events")
def admin_list_mail_events():
    if not _require_admin_or_dev():
        return jsonify({"error": "Forbidden."}), 403

    # TODO
    return jsonify({"mail_events": []}), 200


@admin_bp.post("/users/<int:user_id>/lock")
def lock_user_account(user_id: int):
    if not _require_admin_or_dev():
        return jsonify({"error": "Forbidden."}), 403

    # TODO: lock account + audit log
    return jsonify({"message": "User account locked.", "user_id": user_id}), 200


@admin_bp.post("/users/<int:user_id>/unlock")
def unlock_user_account(user_id: int):
    if not _require_admin_or_dev():
        return jsonify({"error": "Forbidden."}), 403

    # TODO: unlock account + audit log
    return jsonify({"message": "User account unlocked.", "user_id": user_id}), 200


@admin_bp.post("/users/<int:user_id>/send-password-reset")
def send_user_password_reset(user_id: int):
    if not _require_admin_or_dev():
        return jsonify({"error": "Forbidden."}), 403

    # TODO: generate reset flow + email
    return jsonify({"message": "Password reset email sent.", "user_id": user_id}), 200


@admin_bp.post("/users/create-artist")
def create_artist_user():
    role = session.get("role")
    if role not in ("admin", "developer"):
        return jsonify({"error": "Forbidden."}), 403

    data = request.get_json(silent=True) or {}

    email = (data.get("email") or "").strip().lower()
    artist_name = (data.get("artist_name") or "").strip()
    artist_page = (data.get("artist_page") or "").strip()

    if not email or not artist_name or not artist_page:
        return jsonify({
            "error": "Email, artist_name, and artist_page are required."
        }), 400

    existing_user = get_user_by_email(email)
    if existing_user:
        return jsonify({"error": "A user with that email already exists."}), 409

    temp_password_hash = hash_password(generate_raw_token())

    new_user = create_user(
        email=email,
        password_hash=temp_password_hash,
        role="artist",
        username=None,
        email_verified=False,
        artist_name=artist_name,
        artist_page=artist_page,
    )

    invalidate_user_tokens(new_user["id"], "setup_account")

    raw_token = generate_raw_token()
    token_hash = hash_token(raw_token)
    expires_at = expiry_from_now(60 * 24 * 3)  # 3 days

    create_user_action_token(
        user_id=new_user["id"],
        email=email,
        token_hash=token_hash,
        token_type="setup_account",
        expires_at=expires_at,
    )

    frontend_base = os.getenv("FRONTEND_BASE_URL", "http://localhost:3000")
    setup_url = f"{frontend_base}/setup-account.html?token={raw_token}"

    send_artist_invite_email(email, artist_name, setup_url)

    return jsonify({
        "message": "Artist user created and invite email sent.",
        "user": {
            "id": new_user["id"],
            "email": new_user["email"],
            "role": new_user["role"],
            "artist_name": new_user["artist_name"],
            "artist_page": new_user["artist_page"],
        }
    }), 201