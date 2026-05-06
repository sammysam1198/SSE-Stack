from flask import Blueprint, jsonify, session
from repos.users_repo import get_user_by_id
from repos.audit_repo import create_audit_log, list_audit_logs as repo_list_audit_logs

dev_bp = Blueprint("dev", __name__)


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

    return jsonify({
        "audit_logs": repo_list_audit_logs()
    }), 200


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

def _require_developer():
    return session.get("role") == "developer"


@dev_bp.post("/users/<int:user_id>/impersonate")
def impersonate_user(user_id: int):
    if not _require_developer():
        return jsonify({"error": "Forbidden."}), 403

    target_user = get_user_by_id(user_id)
    if not target_user:
        return jsonify({"error": "Target user not found."}), 404

    if not target_user["is_active"] or target_user["is_locked"]:
        return jsonify({"error": "Cannot impersonate inactive or locked user."}), 400

    session["impersonator_user_id"] = session.get("user_id")
    session["impersonator_role"] = session.get("role")
    session["impersonator_email"] = session.get("email")

    session["user_id"] = target_user["id"]
    session["role"] = target_user["role"]
    session["email"] = target_user["email"]
    session["is_impersonating"] = True

    create_audit_log(
        actor_user_id=session.get("impersonator_user_id"),
        actor_role=session.get("impersonator_role"),
        event_type="impersonation_started",
        entity_type="user",
        entity_id=target_user["id"],
        message=f"Developer started impersonating {target_user['email']}.",
    )

    return jsonify({
        "message": "Impersonation started.",
        "user": {
            "id": target_user["id"],
            "email": target_user["email"],
            "role": target_user["role"],
            "is_impersonating": True,
            "impersonator_user_id": session.get("impersonator_user_id"),
        }
    }), 200


@dev_bp.post("/impersonation/stop")
def stop_impersonation():
    if not session.get("is_impersonating"):
        return jsonify({"error": "Not currently impersonating."}), 400

    original_user_id = session.get("impersonator_user_id")
    original_role = session.get("impersonator_role")

    if not original_user_id or original_role != "developer":
        session.clear()
        return jsonify({"error": "Original developer session missing. Please sign in again."}), 400

    original_user = get_user_by_id(original_user_id)
    if not original_user:
        session.clear()
        return jsonify({"error": "Original developer user not found. Please sign in again."}), 404

    session["user_id"] = original_user["id"]
    session["role"] = original_user["role"]
    session["email"] = original_user["email"]

    session.pop("impersonator_user_id", None)
    session.pop("impersonator_role", None)
    session.pop("impersonator_email", None)
    session.pop("is_impersonating", None)

    create_audit_log(
        actor_user_id=original_user["id"],
        actor_role=original_user["role"],
        event_type="impersonation_stopped",
        entity_type="user",
        entity_id=session.get("user_id"),
        message=f"Developer stopped impersonation and returned to {original_user['email']}.",
    )

    return jsonify({
        "message": "Impersonation stopped.",
        "user": {
            "id": original_user["id"],
            "email": original_user["email"],
            "role": original_user["role"],
            "is_impersonating": False,
        }
    }), 200