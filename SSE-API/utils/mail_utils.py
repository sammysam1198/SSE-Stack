import os
from typing import Any


def send_email(
    to_email: str,
    subject: str,
    text_body: str,
    html_body: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Stub mail sender.
    Replace this with Resend / SendGrid / Mailgun later.
    """

    mail_mode = os.getenv("MAIL_MODE", "console").lower()

    payload = {
        "to_email": to_email,
        "subject": subject,
        "text_body": text_body,
        "html_body": html_body,
        "metadata": metadata or {},
    }

    if mail_mode == "console":
        print("\n=== MAIL STUB ===")
        print(f"TO: {to_email}")
        print(f"SUBJECT: {subject}")
        print("TEXT:")
        print(text_body)
        if html_body:
            print("HTML:")
            print(html_body)
        print("=================\n")

        return {
            "status": "queued",
            "provider": "console",
            "provider_message_id": None,
            "payload": payload,
        }

    return {
        "status": "failed",
        "provider": "unknown",
        "provider_message_id": None,
        "payload": payload,
        "error": f"Unsupported MAIL_MODE: {mail_mode}",
    }