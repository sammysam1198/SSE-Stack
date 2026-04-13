import os
import resend

resend.api_key = os.getenv("RESEND_API_KEY")


def send_email(to_email: str, subject: str, html: str):
    return resend.Emails.send({
        "from": "Spaced Out Studios <onboarding@resend.dev>",  # temp sender
        "to": [to_email],
        "subject": subject,
        "html": html,
    })

