import traceback
import re
import zipfile
import io
from io import BytesIO
from PIL import Image
from utils.r2_utils import upload_bytes_to_r2, download_bytes_from_r2
from flask import Blueprint, jsonify, request, session, send_file
from repos.artists_repo import get_artist_profile_by_user_id
from utils.release_pdf_utils import build_release_details_pdf_bytes
from utils.mail_utils import send_release_approved_email
from repos.releases_repo import (
    create_release_draft,
    get_release_artists,
    get_release_tracks,
    get_release_by_id,
    list_all_releases,
    update_release_draft_by_id,
    list_releases_for_creator,
    list_saved_release_artists_for_creator,
    update_release_pdf_object_key,
    get_release_package_by_id
)

release_bp = Blueprint("releases", __name__)


def _sanitize_filename_part(value: str) -> str:
    value = (value or "").strip()
    value = re.sub(r"[^A-Za-z0-9_-]+", "_", value)
    return value[:80] or "file"


def _allowed_audio_extension(filename: str) -> bool:
    lower = (filename or "").lower()
    return lower.endswith(".wav") or lower.endswith(".flac") or lower.endswith(".aac")


def _guess_audio_mime(filename: str, fallback: str | None = None) -> str:
    lower = (filename or "").lower()
    if lower.endswith(".wav"):
        return "audio/wav"
    if lower.endswith(".flac"):
        return "audio/flac"
    if lower.endswith(".aac"):
        return "audio/aac"
    return fallback or "application/octet-stream"


def _allowed_artwork_mime(mime_type: str | None) -> bool:
    return mime_type in {"image/jpeg", "image/png", "image/webp"}


def _current_user_id():
    user = session.get("user")
    if isinstance(user, dict) and user.get("user_id") is not None:
        return user.get("user_id")
    return session.get("user_id")


def _current_role():
    user = session.get("user")
    if isinstance(user, dict) and user.get("role"):
        return user.get("role")
    return session.get("role")


def _require_login():
    return _current_user_id() is not None


def _is_privileged():
    return _current_role() in {"admin", "developer"}


def _clean_text(value):
    value = (value or "").strip()
    return value or None


def _clean_split(value):
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValueError("Split percent must be a whole number.")

def _validate_track_payload(raw_track: dict, index: int):
    track_number = raw_track.get("track_number")
    track_title = _clean_text(raw_track.get("track_title"))
    track_artists_text = _clean_text(raw_track.get("track_artists_text"))
    track_length = _clean_text(raw_track.get("track_length"))
    language = _clean_text(raw_track.get("language"))
    is_instrumental = bool(raw_track.get("is_instrumental"))
    lyrics = _clean_text(raw_track.get("lyrics"))
    track_pitch = _clean_text(raw_track.get("track_pitch"))
    credits = raw_track.get("credits") or []

    if not track_number:
        raise ValueError(f"Track #{index}: track number is required.")
    if not track_title:
        raise ValueError(f"Track #{index}: track title is required.")
    if not track_artists_text:
        raise ValueError(f"Track #{index}: track artist(s) are required.")

    audio = raw_track.get("audio") or {}
    if not audio.get("object_key"):
        raise ValueError(f"Track #{index}: audio upload is required.")

    if not is_instrumental and not lyrics:
        raise ValueError(f"Track #{index}: lyrics are required unless the track is instrumental.")

    return {
        "track_number": int(track_number),
        "track_title": track_title,
        "track_artists_text": track_artists_text,
        "track_length": track_length,
        "language": language,
        "is_instrumental": is_instrumental,
        "lyrics": lyrics,
        "track_pitch": track_pitch,
        "audio_object_key": audio.get("object_key"),
        "audio_original_filename": audio.get("original_filename"),
        "audio_mime_type": audio.get("mime_type"),
        "audio_size_bytes": audio.get("size_bytes"),
        "sample_rate_hz": audio.get("sample_rate_hz"),
        "bit_depth": audio.get("bit_depth"),
        "credits": credits,
    }


def _validate_artist_payload(raw_artist: dict, index: int):
    display_name = _clean_text(raw_artist.get("display_name"))
    email = _clean_text(raw_artist.get("email"))
    role_type = _clean_text(raw_artist.get("role_type")) or "featured"
    split_percent = _clean_split(raw_artist.get("split_percent"))

    if role_type not in {"main", "featured"}:
        raise ValueError(f"Artist #{index}: role_type must be main or featured.")

    if not display_name:
        raise ValueError(f"Artist #{index}: artist name is required.")

    if not email:
        raise ValueError(f"Artist #{index}: email is required.")

    if split_percent is not None and (split_percent < 0 or split_percent > 100):
        raise ValueError(f"Artist #{index}: split percent must be between 0 and 100.")

    return {
        "role_type": role_type,
        "display_name": display_name,
        "email": email,
        "first_name": _clean_text(raw_artist.get("first_name")),
        "last_name": _clean_text(raw_artist.get("last_name")),
        "ipi": _clean_text(raw_artist.get("ipi")),
        "pro": _clean_text(raw_artist.get("pro")),
        "publisher": _clean_text(raw_artist.get("publisher")),
        "spotify_url": _clean_text(raw_artist.get("spotify_url")),
        "apple_music_url": _clean_text(raw_artist.get("apple_music_url")),
        "youtube_url": _clean_text(raw_artist.get("youtube_url")),
        "soundcloud_url": _clean_text(raw_artist.get("soundcloud_url")),
        "saved_featured_artist_id": raw_artist.get("saved_featured_artist_id"),
        "split_percent": split_percent,

    }


@release_bp.post("")
def create_release():
    if not _require_login():
        return jsonify({"error": "Unauthorized."}), 401

    try:
        data = request.get_json(silent=True) or {}

        release_title = _clean_text(data.get("release_title"))
        release_type = _clean_text(data.get("release_type"))
        raw_artists = data.get("artists") or []
        artwork = data.get("artwork") or {}
        raw_tracks = data.get("tracks") or []

        if not release_title:
            return jsonify({"error": "Release title is required."}), 400

        if release_type not in {"single", "ep", "album"}:
            return jsonify({"error": "Release type must be single, ep, or album."}), 400

        if not isinstance(raw_artists, list) or not raw_artists:
            return jsonify({"error": "At least one artist is required."}), 400

        if not isinstance(raw_tracks, list) or not raw_tracks:
            return jsonify({"error": "At least one track is required."}), 400

        if not artwork.get("object_key"):
            return jsonify({"error": "Release artwork is required."}), 400

        if len(raw_artists) > 5:
            return jsonify({"error": "A maximum of 5 artists is allowed for now."}), 400

        try:
            artists = [
                _validate_artist_payload(artist, index + 1)
                for index, artist in enumerate(raw_artists)
            ]

        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

        try:
            tracks = [
                _validate_track_payload(track, index + 1)
                for index, track in enumerate(raw_tracks)
            ]
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400


        artists[0]["role_type"] = "main"

        visible_splits = [a["split_percent"] for a in artists if a["split_percent"] is not None]
        if len(artists) > 1 and sum(visible_splits) != 100:
            return jsonify({"error": "Artist splits must add up to 100."}), 400

        artist_profile_id = None
        if _current_role() == "artist":
            profile = get_artist_profile_by_user_id(_current_user_id())
            if not profile:
                return jsonify({"error": "Artist profile not found."}), 404
            artist_profile_id = profile["id"]

        release = create_release_draft(
            created_by_user_id=_current_user_id(),
            artist_profile_id=artist_profile_id,
            release_title=release_title,
            release_type=release_type,
            preferred_release_date=_clean_text(data.get("preferred_release_date")),
            primary_genre=_clean_text(data.get("primary_genre")),
            other_genres=_clean_text(data.get("other_genres")),
            release_pitch=_clean_text(data.get("release_pitch")),
            artwork_object_key=artwork.get("object_key"),
            artwork_original_filename=artwork.get("original_filename"),
            artwork_mime_type=artwork.get("mime_type"),
            artwork_size_bytes=artwork.get("size_bytes"),
            artwork_width=artwork.get("width"),
            artwork_height=artwork.get("height"),
            artists=artists,
            tracks=tracks,
        )

        pdf_bytes, pdf_filename = build_release_details_pdf_bytes(release)

        pdf_object_key = f"releases/details/{pdf_filename}"

        saved_pdf_key = upload_bytes_to_r2(
            data=pdf_bytes,
            object_key=pdf_object_key,
            content_type="application/pdf",
            content_disposition=f'attachment; filename="{pdf_filename}"',
        )

        update_release_pdf_object_key(release["id"], saved_pdf_key)

        release["release_pdf_object_key"] = saved_pdf_key


        return jsonify({
            "message": "Release draft created.",
            "release": release,
        }), 201

    except Exception as exc:
        print("RELEASE CREATE FAILED:", repr(exc))
        traceback.print_exc()
        return jsonify({
            "error": "Release creation failed.",
            "details": str(exc),
        }), 500


@release_bp.get("")
def list_releases():
    if not _require_login():
        return jsonify({"error": "Unauthorized."}), 401

    if _is_privileged():
        releases = list_all_releases()
    else:
        releases = list_releases_for_creator(_current_user_id())

    for release in releases:
        release["artists"] = get_release_artists(release["id"])
        release["tracks"] = get_release_tracks(release["id"])

    return jsonify({"releases": releases}), 200

@release_bp.get("/<int:submission_id>")
def get_release(submission_id: int):
    if not _require_login():
        return jsonify({"error": "Unauthorized."}), 401

    release = get_release_by_id(submission_id)
    if not release:
        return jsonify({"error": "Release not found."}), 404

    if not _is_privileged() and release["created_by_user_id"] != _current_user_id():
        return jsonify({"error": "Forbidden."}), 403

    release["artists"] = get_release_artists(submission_id)

    return jsonify({"release": release}), 200


@release_bp.get("/artist-library")
def get_release_artist_library():
    if not _require_login():
        return jsonify({"error": "Unauthorized."}), 401

    artists = list_saved_release_artists_for_creator(_current_user_id())
    return jsonify({"artists": artists}), 200

@release_bp.patch("/<int:submission_id>")
def patch_release(submission_id: int):
    if not _require_login():
        return jsonify({"error": "Unauthorized."}), 401

    release = get_release_by_id(submission_id)
    if not release:
        return jsonify({"error": "Release not found."}), 404

    if not _is_privileged() and release["created_by_user_id"] != _current_user_id():
        return jsonify({"error": "Forbidden."}), 403

    if release.get("status") != "draft":
        return jsonify({"error": "Only draft releases can be edited."}), 400

    data = request.get_json(silent=True) or {}

    release_title = _clean_text(data.get("release_title"))
    release_type = _clean_text(data.get("release_type"))
    preferred_release_date = _clean_text(data.get("preferred_release_date"))
    primary_genre = _clean_text(data.get("primary_genre"))
    other_genres = _clean_text(data.get("other_genres"))
    release_pitch = _clean_text(data.get("release_pitch"))

    if not release_title:
        return jsonify({"error": "Release title is required."}), 400

    if release_type not in {"single", "ep", "album"}:
        return jsonify({"error": "Release type must be single, ep, or album."}), 400

    updated = update_release_draft_by_id(
        submission_id,
        _current_user_id(),
        release_title=release_title,
        release_type=release_type,
        preferred_release_date=preferred_release_date,
        primary_genre=primary_genre,
        other_genres=other_genres,
        release_pitch=release_pitch,
    )

    if not updated:
        return jsonify({"error": "Release draft could not be updated."}), 400

    updated["artists"] = get_release_artists(submission_id)
    updated["tracks"] = get_release_tracks(submission_id)

    return jsonify({
        "message": "Release draft updated successfully.",
        "release": updated,
    }), 200

@release_bp.post("/upload-artwork")
def upload_release_artwork():
    if not _require_login():
        return jsonify({"error": "Unauthorized."}), 401

    file = request.files.get("artwork")
    release_title = request.form.get("release_title", "")
    artist_name = request.form.get("artist_name", "")

    if not file:
        return jsonify({"error": "Artwork file is required."}), 400

    mime_type = file.mimetype
    if not _allowed_artwork_mime(mime_type):
        return jsonify({"error": "Artwork must be PNG, JPEG, or WEBP."}), 400

    file_bytes = file.read()
    size_bytes = len(file_bytes)

    max_size = 30 * 1024 * 1024
    if size_bytes > max_size:
        return jsonify({"error": "Artwork must be 30 MB or smaller."}), 400

    try:
        image = Image.open(BytesIO(file_bytes))
        width, height = image.size
    except Exception:
        return jsonify({"error": "Invalid artwork file."}), 400

    if width < 3000 or height < 3000:
        return jsonify({"error": "Artwork must be at least 3000x3000."}), 400

    ext_map = {
        "image/jpeg": "jpg",
        "image/png": "png",
        "image/webp": "webp",
    }
    ext = ext_map[mime_type]

    artist_part = _sanitize_filename_part(artist_name)
    title_part = _sanitize_filename_part(release_title)

    filename = f"{artist_part}_{title_part}_art.{ext}"
    object_key = f"releases/artwork/{filename}"

    try:
        saved_key = upload_bytes_to_r2(
            data=file_bytes,
            object_key=object_key,
            content_type=mime_type,
            content_disposition=f'inline; filename="{filename}"',
        )
    except Exception as exc:
        return jsonify({"error": f"Artwork upload failed: {exc}"}), 500

    return jsonify({
        "message": "Artwork uploaded successfully.",
        "artwork": {
            "object_key": saved_key,
            "original_filename": file.filename,
            "mime_type": mime_type,
            "size_bytes": size_bytes,
            "width": width,
            "height": height,
        }
    }), 201


@release_bp.post("/upload-audio")
def upload_release_audio():
    if not _require_login():
        return jsonify({"error": "Unauthorized."}), 401

    file = request.files.get("audio")
    artist_name = request.form.get("artist_name", "")
    track_title = request.form.get("track_title", "")

    if not file:
        return jsonify({"error": "Audio file is required."}), 400

    if not _allowed_audio_extension(file.filename):
        return jsonify({"error": "Audio must be WAV, FLAC, or AAC. MP3 is not allowed."}), 400

    file_bytes = file.read()
    size_bytes = len(file_bytes)

    max_size = 200 * 1024 * 1024
    if size_bytes > max_size:
        return jsonify({"error": "Audio file must be 200 MB or smaller."}), 400

    artist_part = _sanitize_filename_part(artist_name)
    track_part = _sanitize_filename_part(track_title)
    ext = file.filename.rsplit(".", 1)[-1].lower()

    filename = f"{artist_part}_{track_part}_audio.{ext}"
    object_key = f"releases/audio/{filename}"
    mime_type = _guess_audio_mime(file.filename, file.mimetype)

    try:
        saved_key = upload_bytes_to_r2(
            data=file_bytes,
            object_key=object_key,
            content_type=mime_type,
            content_disposition=f'inline; filename="{filename}"',
        )
    except Exception as exc:
        return jsonify({"error": f"Audio upload failed: {exc}"}), 500

    return jsonify({
        "message": "Audio uploaded successfully.",
        "audio": {
            "object_key": saved_key,
            "original_filename": file.filename,
            "mime_type": mime_type,
            "size_bytes": size_bytes,
            "sample_rate_hz": None,
            "bit_depth": None,
        }
    }), 201

@release_bp.post("/<int:submission_id>/approve")
def approve_release(submission_id):
    if not _is_privileged():
        return jsonify({"error": "Forbidden."}), 403

    data = request.get_json(silent=True) or {}
    release_date = _clean_text(data.get("release_date"))

    if not release_date:
        return jsonify({"error": "Release date is required."}), 400

    release = get_release_package_by_id(submission_id)
    if not release:
        return jsonify({"error": "Release not found."}), 404

    from config.db import execute_write

    execute_write(
        """
        UPDATE release_submissions
        SET status = 'approved',
            approved_at = NOW(),
            submitted_at = COALESCE(submitted_at, NOW()),
            admin_notes = %s
        WHERE id = %s
        """,
        (f"Approved for release on {release_date}", submission_id),
    )

    main_artist = (release.get("artists") or [{}])[0]
    if main_artist.get("email"):
        send_release_approved_email(
            to_email=main_artist["email"],
            artist_name=main_artist.get("display_name") or "Artist",
            release_title=release.get("release_title") or "Untitled Release",
            label_release_date=release_date,
        )

    return jsonify({"message": "Release approved."}), 200

@release_bp.post("/<int:submission_id>/reject")
def reject_release(submission_id):
    if not _is_privileged():
        return jsonify({"error": "Forbidden."}), 403

    data = request.get_json(silent=True) or {}
    reason = _clean_text(data.get("reason"))

    if not reason:
        return jsonify({"error": "Reason is required."}), 400

    from config.db import execute_write

    execute_write(
        """
        UPDATE release_submissions
        SET status = 'draft',
            artist_notes = %s,
            requested_changes_at = NOW()
        WHERE id = %s
        """,
        (reason, submission_id),
    )

    return jsonify({"message": "Release sent back to drafts."}), 200

@release_bp.get("/<int:submission_id>/package")
def download_release_package(submission_id):
    if not _is_privileged():
        return jsonify({"error": "Forbidden."}), 403

    release = get_release_package_by_id(submission_id)
    if not release:
        return jsonify({"error": "Release not found."}), 404

    buffer = io.BytesIO()

    try:
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            pdf_key = release.get("release_pdf_object_key")
            if pdf_key:
                pdf_bytes = download_bytes_from_r2(pdf_key)
                zf.writestr("release_details.pdf", pdf_bytes)

            artwork_key = release.get("artwork_object_key")
            if artwork_key:
                art_bytes = download_bytes_from_r2(artwork_key)
                art_name = release.get("artwork_original_filename") or "cover_art"
                zf.writestr(f"artwork/{art_name}", art_bytes)

            for track in release.get("tracks", []):
                audio_key = track.get("audio_object_key")
                if not audio_key:
                    continue

                audio_bytes = download_bytes_from_r2(audio_key)
                audio_name = track.get("audio_original_filename") or f"track_{track.get('track_number', 'x')}"
                zf.writestr(f"audio/{audio_name}", audio_bytes)

        buffer.seek(0)
    except Exception as exc:
        return jsonify({"error": f"Failed to build ZIP: {exc}"}), 500

    return send_file(
        buffer,
        mimetype="application/zip",
        as_attachment=True,
        download_name=f"release_{submission_id}_package.zip",
    )

@release_bp.get("/<int:submission_id>/pdf")
def download_release_pdf(submission_id):
    if not _is_privileged():
        return jsonify({"error": "Forbidden."}), 403

    release = get_release_package_by_id(submission_id)
    if not release:
        return jsonify({"error": "Release not found."}), 404

    pdf_key = release.get("release_pdf_object_key")
    if not pdf_key:
        return jsonify({"error": "Release PDF not found."}), 404

    try:
        pdf_bytes = download_bytes_from_r2(pdf_key)
    except Exception as exc:
        return jsonify({"error": f"Failed to download PDF: {exc}"}), 500

    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=False,
        download_name=f"release_{submission_id}.pdf",
    )