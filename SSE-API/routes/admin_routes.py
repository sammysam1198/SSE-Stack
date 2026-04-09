from flask import Blueprint, jsonify, session

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