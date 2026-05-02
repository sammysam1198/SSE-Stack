from flask import Blueprint, request, jsonify, session
from repos.requests_repo import get_contact_request_by_id, update_contact_request_status

requests_bp = Blueprint("requests", __name__)


def _current_user_id():
    return session.get("user_id")


def _current_role():
    return session.get("role")


def _is_admin_or_dev():
    return _current_role() in {"admin", "developer"}


@requests_bp.post("/collaborations")
def create_collaboration_request():
    user_id = _current_user_id()
    if not user_id:
        return jsonify({"error": "Not authenticated."}), 401

    data = request.get_json(silent=True) or {}

    required_fields = ["from_artist_profile_id", "to_artist_profile_id", "subject", "message"]
    missing = [field for field in required_fields if not str(data.get(field) or "").strip()]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    # TODO: create collaboration request
    return jsonify({"message": "Collaboration request created."}), 201


@requests_bp.get("/collaborations")
def list_collaboration_requests():
    user_id = _current_user_id()
    role = _current_role()

    if not user_id:
        return jsonify({"error": "Not authenticated."}), 401

    # TODO:
    # admin/dev -> all
    # artist -> own related only
    return jsonify({"collaborations": [], "role": role}), 200


@requests_bp.get("/collaborations/<int:request_id>")
def get_collaboration_request(request_id: int):
    user_id = _current_user_id()
    if not user_id:
        return jsonify({"error": "Not authenticated."}), 401

    # TODO: permission-check target request
    return jsonify({"collaboration_request": {"id": request_id}}), 200


@requests_bp.patch("/collaborations/<int:request_id>")
def update_collaboration_request(request_id: int):
    user_id = _current_user_id()
    if not user_id:
        return jsonify({"error": "Not authenticated."}), 401

    data = request.get_json(silent=True) or {}
    # TODO: permission-check + update
    return jsonify({
        "message": "Collaboration request updated.",
        "request_id": request_id,
        "updated_fields": list(data.keys())
    }), 200


@requests_bp.post("/collaborations/<int:request_id>/accept")
def accept_collaboration_request(request_id: int):
    user_id = _current_user_id()
    if not user_id:
        return jsonify({"error": "Not authenticated."}), 401

    # TODO: accept request
    return jsonify({"message": "Collaboration request accepted.", "request_id": request_id}), 200


@requests_bp.post("/collaborations/<int:request_id>/decline")
def decline_collaboration_request(request_id: int):
    user_id = _current_user_id()
    if not user_id:
        return jsonify({"error": "Not authenticated."}), 401

    # TODO: decline request
    return jsonify({"message": "Collaboration request declined.", "request_id": request_id}), 200


@requests_bp.post("/collaborations/<int:request_id>/cancel")
def cancel_collaboration_request(request_id: int):
    user_id = _current_user_id()
    if not user_id:
        return jsonify({"error": "Not authenticated."}), 401

    # TODO: cancel request
    return jsonify({"message": "Collaboration request cancelled.", "request_id": request_id}), 200


@requests_bp.post("/contact")
def create_contact_request():
    user_id = _current_user_id()
    if not user_id:
        return jsonify({"error": "Not authenticated."}), 401

    data = request.get_json(silent=True) or {}
    subject = (data.get("subject") or "").strip()
    message = (data.get("message") or "").strip()

    if not subject or not message:
        return jsonify({"error": "Subject and message are required."}), 400

    # TODO: create contact request + optional mail event
    return jsonify({"message": "Contact request submitted."}), 201


@requests_bp.get("/contact")
def list_contact_requests():
    user_id = _current_user_id()
    role = _current_role()

    if not user_id:
        return jsonify({"error": "Not authenticated."}), 401

    # TODO:
    # admin/dev -> all
    # artist -> own only
    return jsonify({"contact_requests": [], "role": role}), 200


@requests_bp.get("/contact/<int:request_id>")
def get_contact_request(request_id: int):
    user_id = _current_user_id()
    if not user_id:
        return jsonify({"error": "Not authenticated."}), 401

    # TODO
    return jsonify({"contact_request": {"id": request_id}}), 200


@requests_bp.patch("/contact/<int:request_id>")
def update_contact_request(request_id: int):
    if not _is_admin_or_dev():
        return jsonify({"error": "Forbidden."}), 403

    data = request.get_json(silent=True) or {}
    # TODO: update status / notes
    return jsonify({
        "message": "Contact request updated.",
        "request_id": request_id,
        "updated_fields": list(data.keys())
    }), 200


@requests_bp.post("/merch")
def create_merch_request():
    user_id = _current_user_id()
    if not user_id:
        return jsonify({"error": "Not authenticated."}), 401

    data = request.get_json(silent=True) or {}
    subject = (data.get("subject") or "").strip()
    description = (data.get("description") or "").strip()

    if not subject or not description:
        return jsonify({"error": "Subject and description are required."}), 400

    # TODO: create merch request
    return jsonify({"message": "Merch request submitted."}), 201


@requests_bp.get("/merch")
def list_merch_requests():
    user_id = _current_user_id()
    role = _current_role()

    if not user_id:
        return jsonify({"error": "Not authenticated."}), 401

    # TODO
    return jsonify({"merch_requests": [], "role": role}), 200


@requests_bp.get("/merch/<int:request_id>")
def get_merch_request(request_id: int):
    user_id = _current_user_id()
    if not user_id:
        return jsonify({"error": "Not authenticated."}), 401

    # TODO
    return jsonify({"merch_request": {"id": request_id}}), 200


@requests_bp.patch("/merch/<int:request_id>")
def update_merch_request(request_id: int):
    if not _is_admin_or_dev():
        return jsonify({"error": "Forbidden."}), 403

    data = request.get_json(silent=True) or {}
    # TODO
    return jsonify({
        "message": "Merch request updated.",
        "request_id": request_id,
        "updated_fields": list(data.keys())
    }), 200

@requests_bp.patch("/contact/<int:request_id>")
def patch_contact_request_status(request_id: int):
    if not _is_admin_or_dev():
        return jsonify({"error": "Forbidden."}), 403

    existing = get_contact_request_by_id(request_id)
    if not existing:
        return jsonify({"error": "Contact request not found."}), 404

    data = request.get_json(silent=True) or {}
    status = (data.get("status") or "").strip()

    if status not in {"open", "in_progress", "closed"}:
        return jsonify({"error": "Invalid status."}), 400

    updated = update_contact_request_status(request_id, status)

    return jsonify({
        "message": "Contact request updated.",
        "contact_request": updated,
    }), 200