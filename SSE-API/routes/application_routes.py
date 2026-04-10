from flask import Blueprint, request, jsonify, session

applications_bp = Blueprint("applications", __name__)


def _current_role():
    return session.get("role")


def _require_admin_or_dev():
    role = _current_role()
    return role in {"admin", "developer"}


@applications_bp.post("")
def create_application():
    data = request.get_json(silent=True) or {}

    required_fields = [
        "first_name",
        "last_name",
        "artist_name",
        "email",
    ]

    missing = [field for field in required_fields if not str(data.get(field) or "").strip()]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    # TODO: create application in applications_repo
    return jsonify({
        "message": "Application submitted successfully."
    }), 201


@applications_bp.get("")
def list_applications():
    if not _require_admin_or_dev():
        return jsonify({"error": "Forbidden."}), 403

    # TODO: list applications from repo
    return jsonify({"applications": []}), 200


@applications_bp.get("/<int:application_id>")
def get_application(application_id: int):
    if not _require_admin_or_dev():
        return jsonify({"error": "Forbidden."}), 403

    # TODO: fetch application from repo
    return jsonify({"application": {"id": application_id}}), 200


@applications_bp.post("/<int:application_id>/approve")
def approve_application(application_id: int):
    if not _require_admin_or_dev():
        return jsonify({"error": "Forbidden."}), 403

    # TODO:
    # 1. mark application approved
    # 2. create user account
    # 3. create artist profile
    # 4. send onboarding email

    return jsonify({
        "message": "Application approved.",
        "application_id": application_id
    }), 200


@applications_bp.post("/<int:application_id>/deny")
def deny_application(application_id: int):
    if not _require_admin_or_dev():
        return jsonify({"error": "Forbidden."}), 403

    data = request.get_json(silent=True) or {}
    review_notes = (data.get("review_notes") or "").strip()

    # TODO:
    # 1. mark application denied
    # 2. store review notes
    # 3. optionally send denial email

    return jsonify({
        "message": "Application denied.",
        "application_id": application_id,
        "review_notes": review_notes
    }), 200