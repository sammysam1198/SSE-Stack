from flask import Blueprint, jsonify, request, session
from utils.mail_utils import send_contact_form_email
from repos.requests_repo import create_contact_request

contact_bp = Blueprint("contact", __name__)


def _clean_text(value):
    value = (value or "").strip()
    return value or None


def _department_for_issue(issue_type: str) -> str:
    issue = (issue_type or "general").lower()

    if issue in {"advertising", "legal", "business"}:
        return "OWNER"

    if issue in {"website", "login"}:
        return "IT"

    return "Operations"


@contact_bp.post("")
def submit_contact_form():
    data = request.get_json(silent=True) or {}

    name = _clean_text(data.get("name"))
    email = _clean_text(data.get("email"))
    subject = _clean_text(data.get("subject"))
    message = _clean_text(data.get("message"))
    issue_type = _clean_text(data.get("issue_type")) or "general"
    department_tag = _department_for_issue(issue_type)

    if not name:
        return jsonify({"error": "Name is required."}), 400
    if not email:
        return jsonify({"error": "Email is required."}), 400
    if not subject:
        return jsonify({"error": "Subject is required."}), 400
    if not message:
        return jsonify({"error": "Message is required."}), 400

    contact_request = create_contact_request(
        requester_name=name,
        requester_email=email,
        issue_type=issue_type,
        department_tag=department_tag,
        subject=subject,
        message=message,
        created_user_id=session.get("user_id"),
    )

    try:
        send_contact_form_email(
            sender_name=name,
            sender_email=email,
            subject=f"[{department_tag}] {subject}",
            message=message,
        )
    except Exception as exc:
        return jsonify({
            "message": "Contact request saved, but email failed.",
            "contact_request": contact_request,
            "email_error": str(exc),
        }), 201

    return jsonify({
        "message": "Message sent successfully.",
        "contact_request": contact_request,
    }), 201