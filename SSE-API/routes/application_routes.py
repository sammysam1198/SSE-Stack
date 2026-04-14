from utils.mail_utils import send_artist_application_email
from repos.applications_repo import update_application_pdf_path
from utils.application_pdf_utils import generate_application_pdf
from datetime import datetime
from urllib.parse import urlparse
from pathlib import Path
from flask import send_file

from flask import Blueprint, request, jsonify, session

from repos.applications_repo import (
    approve_application as repo_approve_application,
    create_application as repo_create_application,
    deny_application as repo_deny_application,
    get_application_by_id,
    list_applications as repo_list_applications,
)

applications_bp = Blueprint("applications", __name__)


def _current_role():
    return session.get("role")


def _current_user_id():
    return session.get("user_id")


def _require_admin_or_dev():
    return _current_role() in {"admin", "developer"}


def _clean(value):
    if value is None:
        return None
    value = str(value).strip()
    return value or None


def _parse_birthday(value: str):
    return datetime.strptime(value, "%m/%d/%Y").date()


def _parse_optional_int(value, field_name: str):
    cleaned = _clean(value)
    if cleaned is None:
        return None

    try:
        number = int(cleaned)
    except ValueError:
        raise ValueError(f"{field_name} must be a whole number.")

    if number < 0:
        raise ValueError(f"{field_name} cannot be negative.")

    return number


def _is_https_url(value: str) -> bool:
    try:
        parsed = urlparse(value)
        return parsed.scheme == "https" and bool(parsed.netloc)
    except Exception:
        return False


def _validate_application_payload(data: dict):
    required_identity_fields = [
        "first_name",
        "last_name",
        "birthday",
        "artist_name",
        "country",
        "city",
        "state_province",
        "email",
    ]

    missing = [field for field in required_identity_fields if not _clean(data.get(field))]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

    birthday_raw = _clean(data.get("birthday"))
    try:
        birthday = _parse_birthday(birthday_raw)
    except ValueError:
        raise ValueError("Birthday must use MM/DD/YYYY format.")

    streaming_link = _clean(data.get("streaming_link"))
    instagram_link = _clean(data.get("instagram_link"))
    youtube_link = _clean(data.get("youtube_link"))
    bandcamp_link = _clean(data.get("bandcamp_link"))
    website_link = _clean(data.get("website_link"))

    if not streaming_link or not any(token in streaming_link.lower() for token in ("spotify", "soundcloud")):
        raise ValueError("Streaming link must contain spotify or soundcloud.")

    if not instagram_link or "instagram" not in instagram_link.lower():
        raise ValueError("Instagram link must contain instagram.")

    if not youtube_link or "youtube" not in youtube_link.lower():
        raise ValueError("YouTube link must contain youtube.")

    if bandcamp_link and "bandcamp" not in bandcamp_link.lower():
        raise ValueError("Bandcamp link must contain bandcamp.")

    for label, link in [
        ("streaming_link", streaming_link),
        ("instagram_link", instagram_link),
        ("youtube_link", youtube_link),
        ("bandcamp_link", bandcamp_link),
        ("website_link", website_link),
    ]:
        if link and not _is_https_url(link):
            raise ValueError(f"{label} must begin with https://")

    agreement = (_clean(data.get("agreement")) or "").lower()
    if agreement != "yes":
        raise ValueError("You must accept the terms to submit an application.")

    unreleased_music_ready = _clean(data.get("unreleased_music_ready"))
    if unreleased_music_ready and unreleased_music_ready not in {"Yes", "No", "In progress"}:
        raise ValueError("unreleased_music_ready must be Yes, No, or In progress.")

    collaboration_openness = _clean(data.get("collaboration_openness"))
    if collaboration_openness and collaboration_openness not in {"Yes", "No", "Depends"}:
        raise ValueError("collaboration_openness must be Yes, No, or Depends.")

    bank_account_access = _clean(data.get("bank_account_access"))
    if bank_account_access and bank_account_access not in {"Yes", "No", "Other"}:
        raise ValueError("bank_account_access must be Yes, No, or Other.")

    return {
        "first_name": _clean(data.get("first_name")),
        "last_name": _clean(data.get("last_name")),
        "birthday": birthday,
        "artist_name": _clean(data.get("artist_name")),
        "country": _clean(data.get("country")),
        "city": _clean(data.get("city")),
        "state_province": _clean(data.get("state_province")),
        "email": _clean(data.get("email")),
        "phone": _clean(data.get("phone")),
        "current_label": _clean(data.get("current_label")),
        "publisher": _clean(data.get("publisher")),
        "current_distributor": _clean(data.get("current_distributor")),
        "total_releases": _parse_optional_int(data.get("total_releases"), "total_releases"),
        "releases_last_12_months": _parse_optional_int(
            data.get("releases_last_12_months"),
            "releases_last_12_months",
        ),
        "spotify_monthly_listeners": _parse_optional_int(
            data.get("spotify_monthly_listeners"),
            "spotify_monthly_listeners",
        ),
        "streaming_link": streaming_link,
        "instagram_link": instagram_link,
        "youtube_link": youtube_link,
        "bandcamp_link": bandcamp_link,
        "website_link": website_link,
        "fit": _clean(data.get("fit")),
        "standout": _clean(data.get("standout")),
        "strongest_skill_and_leverage": _clean(data.get("strongest_skill_and_leverage")),
        "release_schedule": _clean(data.get("release_schedule")),
        "unreleased_music_ready": unreleased_music_ready,
        "branding": _clean(data.get("branding")),
        "goals_12_months": _clean(data.get("goals_12_months")),
        "collaboration_openness": collaboration_openness,
        "heard_about": _clean(data.get("heard_about")),
        "bank_account_access": bank_account_access,
        "bank_account_explanation": _clean(data.get("bank_account_explanation")),
        "agreement": "yes",
    }

@applications_bp.get("")
def list_applications():
    if not _require_admin_or_dev():
        return jsonify({"error": "Forbidden."}), 403

    applications = repo_list_applications()
    return jsonify({"applications": applications}), 200


@applications_bp.get("/<int:application_id>")
def get_application(application_id: int):
    if not _require_admin_or_dev():
        return jsonify({"error": "Forbidden."}), 403

    application = get_application_by_id(application_id)
    if not application:
        return jsonify({"error": "Application not found."}), 404

    return jsonify({"application": application}), 200


@applications_bp.post("/<int:application_id>/approve")
def approve_application(application_id: int):
    if not _require_admin_or_dev():
        return jsonify({"error": "Forbidden."}), 403

    application = get_application_by_id(application_id)
    if not application:
        return jsonify({"error": "Application not found."}), 404

    repo_approve_application(application_id, _current_user_id())

    return jsonify({
        "message": "Application approved.",
        "application_id": application_id
    }), 200


@applications_bp.post("/<int:application_id>/deny")
def deny_application(application_id: int):
    if not _require_admin_or_dev():
        return jsonify({"error": "Forbidden."}), 403

    application = get_application_by_id(application_id)
    if not application:
        return jsonify({"error": "Application not found."}), 404

    data = request.get_json(silent=True) or {}
    review_notes = _clean(data.get("review_notes"))

    repo_deny_application(application_id, _current_user_id(), review_notes)

    return jsonify({
        "message": "Application denied.",
        "application_id": application_id,
        "review_notes": review_notes
    }), 200


@applications_bp.post("")
def create_application():
    data = request.get_json(silent=True) or {}

    try:
        payload = _validate_application_payload(data)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    created_user_id = _current_user_id()

    application = repo_create_application(
        **payload,
        created_user_id=created_user_id,
    )

    pdf_path = None
    pdf_error = None

    try:
        full_application = {
            **payload,
            **application,
        }
        pdf_path = generate_application_pdf(full_application)
        update_application_pdf_path(application["id"], pdf_path)
        application["application_pdf_path"] = pdf_path
    except Exception as exc:
        pdf_error = str(exc)
        print(f"[application pdf] failed: {exc}")

    email_sent = True
    email_error = None

    try:
        send_artist_application_email({
            **payload,
            **application,
        })
    except Exception as exc:
        email_sent = False
        email_error = str(exc)
        print(f"[artist application email] failed: {exc}")

    return jsonify({
        "message": "Artist application submitted successfully.",
        "application": application,
        "email_sent": email_sent,
        "email_error": email_error,
        "pdf_created": pdf_path is not None,
        "pdf_error": pdf_error,
    }), 201

@applications_bp.get("/<int:application_id>/pdf")
def download_application_pdf(application_id: int):
    if not _require_admin_or_dev():
        return jsonify({"error": "Forbidden."}), 403

    application = get_application_by_id(application_id)
    if not application:
        return jsonify({"error": "Application not found."}), 404

    pdf_path = application.get("application_pdf_path")
    if not pdf_path:
        return jsonify({"error": "Application PDF not found."}), 404

    base_dir = Path(__file__).resolve().parent.parent
    absolute_path = base_dir / pdf_path

    if not absolute_path.exists() or not absolute_path.is_file():
        return jsonify({"error": "Application PDF file is missing."}), 404

    download_name = f"{application.get('artist_name', 'artist')}_application.pdf"

    return send_file(
        absolute_path,
        as_attachment=True,
        download_name=download_name,
        mimetype="application/pdf",
    )