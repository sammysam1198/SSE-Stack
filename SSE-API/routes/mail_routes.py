from flask import Blueprint, jsonify
from utils.mail_utils import send_email

test_bp = Blueprint("test", __name__)


@test_bp.get("/test-email")
def test_email():
    send_email(
        "maidenfann1198@gmail.com",
        "SSE Email Test",
        "<h1>It works</h1><p>If you see this, email is wired.</p>"
    )
    return jsonify({"message": "Email sent"})