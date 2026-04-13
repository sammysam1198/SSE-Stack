import os
import resend

resend.api_key = os.getenv("RESEND_API_KEY")

FROM_EMAIL = os.getenv("MAIL_FROM", "Spaced Out Studios <noreply@spacedoutstudiosent.com>")


def send_email(to_email: str, subject: str, html: str):
    return resend.Emails.send({
        "from": FROM_EMAIL,
        "to": [to_email],
        "subject": subject,
        "html": html,
    })


def send_password_reset_email(to_email: str, reset_url: str):
    html = f"""
    <h2>Reset your password</h2>
    <p>You requested a password reset for your Spaced Out Studios account.</p>
    <p><a href="{reset_url}">Reset Password</a></p>
    <p>If you did not request this, you can ignore this email.</p>
    """
    return send_email(to_email, "Reset your password", html)


def send_artist_invite_email(to_email: str, artist_name: str, setup_url: str):
    html = f"""
    <h2>You’ve been invited to Spaced Out Studios</h2>
    <p>Hello {artist_name},</p>
    <p>Your artist account has been created. Click the link below to set your password and activate your account.</p>
    <p><a href="{setup_url}">Set Up Your Account</a></p>
    <p>If you were not expecting this email, you can ignore it.</p>
    """
    return send_email(to_email, "You’ve been invited to Spaced Out Studios", html)