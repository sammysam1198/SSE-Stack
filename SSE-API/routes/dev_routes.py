from flask import Blueprint, jsonify, session

dev_bp = Blueprint("dev", __name__)


def _require_developer():
    return session.get("role") == "developer"


@dev_bp.get("/dashboard")
def dev_dashboard():
    if not _require_developer():
        return jsonify({"error": "Forbidden."}), 403

    return jsonify({
        "dashboard": {
            "status": "ok",
            "debug_mode": True
        }
    }), 200


@dev_bp.get("/audit-logs")
def list_audit_logs():
    if not _require_developer():
        return jsonify({"error": "Forbidden."}), 403

    # TODO
    return jsonify({"audit_logs": []}), 200


@dev_bp.get("/security-events")
def list_security_events():
    if not _require_developer():
        return jsonify({"error": "Forbidden."}), 403

    # TODO
    return jsonify({"security_events": []}), 200


@dev_bp.get("/mail-events")
def list_mail_events():
    if not _require_developer():
        return jsonify({"error": "Forbidden."}), 403

    # TODO
    return jsonify({"mail_events": []}), 200


@dev_bp.post("/users/<int:user_id>/impersonate")
def impersonate_user(user_id: int):
    if not _require_developer():
        return jsonify({"error": "Forbidden."}), 403

    # TODO:
    # store original identity in session
    # switch effective session identity
    return jsonify({
        "message": "Impersonation started.",
        "user_id": user_id
    }), 200


@dev_bp.post("/impersonation/stop")
def stop_impersonation():
    if not _require_developer():
        return jsonify({"error": "Forbidden."}), 403

    # TODO: restore original session identity
    return jsonify({"message": "Impersonation stopped."}), 200