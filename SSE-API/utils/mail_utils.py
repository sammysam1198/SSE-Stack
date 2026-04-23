import os
import resend
from html import escape


resend.api_key = os.getenv("RESEND_API_KEY")

FROM_EMAIL = os.getenv("MAIL_FROM", "SpacedOut Studios <noreply@spacedoutstudiosent.com>")


def send_email(to_email: str, subject: str, html: str):
    return resend.Emails.send({
        "from": FROM_EMAIL,
        "to": [to_email],
        "subject": subject,
        "html": html,
    })


def _format_custom_invite_body_html(custom_body: str, setup_url: str) -> str:
    escaped_body = escape(custom_body).replace("\n", "<br>")

    return f"""
    <div style="font-family:Arial,Helvetica,sans-serif; color:#111; line-height:1.65;">
        <div style="white-space:normal; font-size:15px;">
            {escaped_body}
        </div>

        <p style="margin-top:24px;">
            <strong>Create your account here:</strong><br>
            <a href="{setup_url}">{setup_url}</a>
        </p>
    </div>
    """


def send_artist_invite_email(
    to_email: str,
    artist_name: str,
    setup_url: str,
    custom_subject: str | None = None,
    custom_body: str | None = None,
):
    subject = (custom_subject or "").strip() or "You’ve been invited to SpacedOut Studios"

    if custom_body and custom_body.strip():
        html = _format_custom_invite_body_html(custom_body.strip(), setup_url)
    else:
        html = f"""
        <h2>You’ve been invited to SpacedOut Studios</h2>
        <p>Hello {escape(artist_name)},</p>
        <p>Your artist account has been created. Click the link below to set your password and activate your account.</p>
        <p><a href="{setup_url}">Set Up Your Account</a></p>
        <p>If you were not expecting this email, you can ignore it.</p>
        """

    return send_email(to_email, subject, html)


def send_password_reset_email(to_email: str, reset_url: str):
    html = f"""
    <h2>Reset your password</h2>
    <p>You requested a password reset for your SpacedOut Studios account.</p>
    <p><a href="{reset_url}">Reset Password</a></p>
    <p>If you did not request this, you can ignore this email.</p>
    """
    return send_email(to_email, "Reset your password", html)


def build_application_email_html(application: dict) -> str:
    def row(label: str, value):
        safe_value = escape(str(value if value not in (None, "") else "—"))
        return f"""
        <tr>
            <td style="padding:8px 12px; border:1px solid #ddd; font-weight:700; width:240px; background:#f7f7f7;">
                {escape(label)}
            </td>
            <td style="padding:8px 12px; border:1px solid #ddd;">
                {safe_value}
            </td>
        </tr>
        """

    html = f"""
    <div style="font-family:Arial,Helvetica,sans-serif; color:#111;">
        <h2 style="margin-bottom:6px;">New Artist Application</h2>
        <p style="margin-top:0; color:#555;">
            A new SpacedOut Studios application was submitted.
        </p>

        <table style="border-collapse:collapse; width:100%; margin:18px 0;">
            {row("Application ID", application.get("id"))}
            {row("Submitted At", application.get("created_at"))}
            {row("Status", application.get("status"))}
        </table>

        <h3>Identity</h3>
        <table style="border-collapse:collapse; width:100%; margin:12px 0 24px;">
            {row("First Name", application.get("first_name"))}
            {row("Last Name", application.get("last_name"))}
            {row("Birthday", application.get("birthday"))}
            {row("Artist Name", application.get("artist_name"))}
            {row("Country", application.get("country"))}
            {row("City", application.get("city"))}
            {row("State / Province", application.get("state_province"))}
            {row("Email", application.get("email"))}
            {row("Phone", application.get("phone"))}
        </table>

        <h3>Professional Info</h3>
        <table style="border-collapse:collapse; width:100%; margin:12px 0 24px;">
            {row("Current Label", application.get("current_label"))}
            {row("Publisher", application.get("publisher"))}
            {row("Current Distributor", application.get("current_distributor"))}
            {row("Total Releases", application.get("total_releases"))}
            {row("Releases Last 12 Months", application.get("releases_last_12_months"))}
            {row("Spotify Monthly Listeners", application.get("spotify_monthly_listeners"))}
        </table>

        <h3>Links</h3>
        <table style="border-collapse:collapse; width:100%; margin:12px 0 24px;">
            {row("Streaming Link", application.get("streaming_link"))}
            {row("Instagram Link", application.get("instagram_link"))}
            {row("YouTube Link", application.get("youtube_link"))}
            {row("Bandcamp Link", application.get("bandcamp_link"))}
            {row("Website Link", application.get("website_link"))}
        </table>

        <h3>Application Questions</h3>
        <table style="border-collapse:collapse; width:100%; margin:12px 0 24px;">
            {row("Why do you want to work with SpacedOut Studios?", application.get("fit"))}
            {row("What makes your music stand out in your genre?", application.get("standout"))}
            {row("Strongest skill and weakest leverage point", application.get("strongest_skill_and_leverage"))}
            {row("Release Schedule", application.get("release_schedule"))}
            {row("Unreleased Music Ready", application.get("unreleased_music_ready"))}
            {row("Branding", application.get("branding"))}
            {row("Goals in 12 Months", application.get("goals_12_months"))}
            {row("Collaboration Openness", application.get("collaboration_openness"))}
            {row("How They Heard About Us", application.get("heard_about"))}
        </table>

        <h3>Financial / Operational</h3>
        <table style="border-collapse:collapse; width:100%; margin:12px 0 24px;">
            {row("Bank Account Access", application.get("bank_account_access"))}
            {row("Bank Account Explanation", application.get("bank_account_explanation"))}
            {row("Agreement", application.get("agreement"))}
        </table>
    </div>
    """
    return html


def send_artist_application_email(application: dict):
    subject = f"New Artist Application: {application.get('artist_name', 'Unknown Artist')}"
    html = build_application_email_html(application)

    # Replace this call with your existing Resend helper if its name differs
    return send_email(
        to="chromaglowmusic@gmail.com",
        subject=subject,
        html=html,
    )


def send_application_approved_email(to_email: str, artist_name: str, setup_url: str):
    subject = "Your SpacedOut Studios application has been approved"
    html = f"""
    <div style="font-family:Arial,Helvetica,sans-serif; color:#111; line-height:1.65;">
        <p>Dear {escape(artist_name)},</p>

        <p>
            On behalf of SpacedOut Studios Entertainment and its affiliates,
            it is my great pleasure to offer you a record deal with our company.
            We’re really excited to learn more about you and how you shine in music.
        </p>

        <p>
            To get started, please create your account below.
            Please note that creating an account does not bind you legally.
            It is simply the way that we manage communication and onboarding.
        </p>

        <p>
            <a href="{setup_url}">Create your account</a>
        </p>

        <p style="margin-top:24px;">
            Warmly,<br><br>
            Aliem Jumpp<br>
            Owner<br>
            SpacedOut Studios Entertainment<br><br>

            Sammi Fishbein<br>
            Chroma Glow<br>
            PR & Operations<br>
            SpacedOut Studios Entertainment
        </p>
    </div>
    """
    return send_email(to_email, subject, html)


def send_application_denied_email(to_email: str, artist_name: str):
    subject = "Update on your SpacedOut Studios application"
    html = f"""
    <div style="font-family:Arial,Helvetica,sans-serif; color:#111; line-height:1.65;">
        <p>Dear {escape(artist_name)},</p>

        <p>
            Thank you for taking the time to apply to SpacedOut Studios Entertainment.
            We truly appreciate the opportunity to review your work and learn more about your artistry.
        </p>

        <p>
            After careful consideration, we will not be moving forward at this time.
            This decision is not meant to diminish the value of your work, and we sincerely wish you continued growth and success in your music journey.
        </p>

        <p style="margin-top:24px;">
            Warm regards,<br><br>
            Aliem Jumpp<br>
            Owner<br>
            SpacedOut Studios Entertainment
        </p>
    </div>
    """
    return send_email(to_email, subject, html)

def send_release_approved_email(
    to_email: str,
    artist_name: str,
    release_title: str,
    label_release_date: str,
):
    subject = f"Release Approved: {release_title}"

    html = f"""
    <div style="font-family:Arial,Helvetica,sans-serif; color:#111; line-height:1.65;">
        <p>Hi {escape(artist_name)},</p>

        <p>
            This is SpacedOut Studios letting you know that your release
            <strong>{escape(release_title)}</strong> was approved.
        </p>

        <p>
            It will be released on <strong>{escape(label_release_date)}</strong>.
        </p>

        <p>
            If you have questions please email chromaglowmusic@gmail.com
        </p>

        <p style="margin-top:24px;">
            Thanks,<br><br>
            Aliem<br>
            Sammi
        </p>
    </div>
    """

    return send_email(to_email, subject, html)


def send_contract_ready_email(
    to_email: str,
    artist_name: str,
    contract_type: str,
    contract_view_url: str,
):
    subject = f"{contract_type.title()} Contract for {artist_name}"

    html = f"""
    <div style="font-family:Arial,Helvetica,sans-serif; color:#111; line-height:1.65;">
        <p>Hi {escape(artist_name)},</p>

        <p>
            This is SpacedOut Studios. Your
            <strong>{escape(contract_type.title())} Contract</strong>
            is ready for review.
        </p>

        <p>
            You can view and download it here:
        </p>

        <p>
            <a href="{escape(contract_view_url)}">{escape(contract_view_url)}</a>
        </p>

        <p>
            Please review, sign, and upload the signed version back through your dashboard.
        </p>

        <p>
            If you have questions please email chromaglowmusic@gmail.com
        </p>

        <p style="margin-top:24px;">
            Thanks,<br><br>
            Aliem Jumpp<br>
            Owner<br>
            SpacedOut Studios Entertainment<br><br>
            
            Sammi Fishbein<br>
            IT & Operations<br>
            SpacedOut Studios Entertainment<br>
            Chroma Glow<br>
        </p>
    </div>
    """

    print("[mail] send_contract_ready_email ->", to_email, subject)
    return send_email(to_email, subject, html)


def send_release_rejected_email(
    to_email: str,
    artist_name: str,
    release_title: str,
    reason: str,
):
    subject = f"Release Sent Back for Changes: {release_title}"

    html = f"""
    <div style="font-family:Arial,Helvetica,sans-serif; color:#111; line-height:1.65;">
        <p>Hi {escape(artist_name)},</p>

        <p>
            Your release <strong>{escape(release_title)}</strong> was reviewed and has been sent back to drafts for changes.
        </p>

        <p>
            <strong>Reason:</strong><br>
            {escape(reason)}
        </p>

        <p>
            You can return to your release drafts, edit the submission, and resubmit it once the requested changes are complete.
        </p>

        <p style="margin-top:24px;">
            Sammi Fishbein<br>
            IT & Operations<br>
            SpacedOut Studios Entertainment<br>
        </p>
    </div>
    """

    return send_email(to_email, subject, html)

import os
from html import escape

import resend

CONTACT_FORM_TO_EMAIL = os.getenv("CONTACT_FORM_TO_EMAIL", "chromaglowsynths@gmail.com")
CONTACT_FORM_FROM_EMAIL = os.getenv("CONTACT_FORM_FROM_EMAIL", "SpacedOut Studios <noreply@spacedoutstudiosent.com>")


def send_contact_form_email(
    *,
    sender_name: str,
    sender_email: str,
    subject: str,
    message: str,
):
    resend.api_key = os.environ["RESEND_API_KEY"]

    safe_name = escape(sender_name)
    safe_email = escape(sender_email)
    safe_subject = escape(subject)
    safe_message = escape(message).replace("\n", "<br>")

    params: resend.Emails.SendParams = {
        "from": CONTACT_FORM_FROM_EMAIL,
        "to": [CONTACT_FORM_TO_EMAIL],
        "subject": f"Contact Form: {subject}",
        "reply_to": sender_email,
        "html": f"""
            <div style="font-family:Arial,Helvetica,sans-serif;color:#111;line-height:1.7;">
                <h2 style="margin-bottom:16px;">New Contact Form Message</h2>

                <p><strong>Name:</strong> {safe_name}</p>
                <p><strong>Email:</strong> {safe_email}</p>
                <p><strong>Subject:</strong> {safe_subject}</p>

                <div style="margin-top:18px;">
                    <strong>Message:</strong>
                    <div style="margin-top:8px;padding:14px 16px;border:1px solid #ddd;border-radius:12px;">
                        {safe_message}
                    </div>
                </div>
            </div>
        """,
        "text": f"""New Contact Form Message

Name: {sender_name}
Email: {sender_email}
Subject: {subject}

Message:
{message}
""",
    }

    return resend.Emails.send(params)