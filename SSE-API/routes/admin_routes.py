import os
from flask import Blueprint, jsonify, request, session
from repos.users_repo import get_user_by_email, create_user
from repos.requests_repo import list_contact_requests
from repos.artists_repo import create_artist_profile_for_user, assign_artist_profile_to_user, get_artist_profile_by_slug
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

ALLOWED_INVITE_ROLES = {"artist", "admin", "developer"}

@admin_bp.post("/users/create-artist")
def create_artist_user():
    session_role = session.get("role")
    if session_role not in ("admin", "developer"):
        return jsonify({"error": "Forbidden."}), 403

    data = request.get_json(silent=True) or {}

    email = (data.get("email") or "").strip().lower()
    role = (data.get("role") or "artist").strip().lower()
    artist_name = (data.get("artist_name") or "").strip()
    artist_page = (data.get("artist_page") or "").strip()
    email_subject = (data.get("email_subject") or "").strip()
    email_body = (data.get("email_body") or "").strip()

    if not email:
        return jsonify({"error": "Email is required."}), 400

    if role not in ALLOWED_INVITE_ROLES:
        return jsonify({"error": "Invalid role."}), 400

    if role == "artist":
        if not artist_name or not artist_page:
            return jsonify({
                "error": "Artist name and artist page are required for artist accounts."
            }), 400
    else:
        artist_name = None
        artist_page = None

    existing_user = get_user_by_email(email)
    if existing_user:
        return jsonify({"error": "A user with that email already exists."}), 409

    temp_password_hash = hash_password(generate_raw_token())

    new_user = create_user(
        email=email,
        password_hash=temp_password_hash,
        role=role,
        username=None,
        email_verified=False,
        artist_name=artist_name,
        artist_page=artist_page,
    )

    artist_profile = None

    if role == "artist":
        existing_artist = get_artist_profile_by_slug(artist_page)

        if existing_artist:
            artist_profile = assign_artist_profile_to_user(
                artist_profile_id=existing_artist["id"],
                user_id=new_user["id"],
            )
        else:
            artist_profile = create_artist_profile_for_user(
                user_id=new_user["id"],
                artist_name=artist_name,
                artist_page=artist_page,
            )

    invalidate_user_tokens(new_user["id"], "setup_account")

    raw_token = generate_raw_token()
    token_hash = hash_token(raw_token)
    expires_at = expiry_from_now(60 * 24 * 3)

    create_user_action_token(
        user_id=new_user["id"],
        email=email,
        token_hash=token_hash,
        token_type="setup_account",
        expires_at=expires_at,
    )

    frontend_base = os.getenv("FRONTEND_ORIGIN", "https://www.spacedoutstudiosent.com")
    if not frontend_base:
        return jsonify({"error": "FRONTEND_ORIGIN is not set."}), 500

    setup_url = f"{frontend_base}/setup-account?token={raw_token}"

    send_artist_invite_email(
        to_email=email,
        artist_name=artist_name or role.title(),
        setup_url=setup_url,
        custom_subject=email_subject or None,
        custom_body=email_body or None,
    )

    return jsonify({
        "message": "Invite sent successfully.",
        "user": {
            "id": new_user["id"],
            "email": new_user["email"],
            "role": new_user["role"],
            "artist_name": new_user.get("artist_name"),
            "artist_page": new_user.get("artist_page"),
        },
        "artist_profile": artist_profile,
    }), 201


@admin_bp.get("/contact-requests")
def admin_list_contact_requests():
    if not _require_admin_or_dev():
        return jsonify({"error": "Forbidden."}), 403

    return jsonify({
        "contact_requests": list_contact_requests()
    }), 200