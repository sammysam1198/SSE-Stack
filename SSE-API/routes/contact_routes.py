from flask import Blueprint, jsonify, request
from utils.mail_utils import send_contact_form_email

contact_bp = Blueprint("contact", __name__)


def _clean_text(value):
    value = (value or "").strip()
    return value or None


@contact_bp.post("")
def submit_contact_form():
    data = request.get_json(silent=True) or {}

    name = _clean_text(data.get("name"))
    email = _clean_text(data.get("email"))
    subject = _clean_text(data.get("subject"))
    message = _clean_text(data.get("message"))

    if not name:
        return jsonify({"error": "Name is required."}), 400

    if not email:
        return jsonify({"error": "Email is required."}), 400

    if not subject:
        return jsonify({"error": "Subject is required."}), 400

    if not message:
        return jsonify({"error": "Message is required."}), 400

    try:
        send_contact_form_email(
            sender_name=name,
            sender_email=email,
            subject=subject,
            message=message,
        )
    except Exception as exc:
        return jsonify({
            "error": "Failed to send message.",
            "details": str(exc),
        }), 500

    return jsonify({"message": "Message sent successfully."}), 200