import traceback
import os
import re
from io import BytesIO

from PIL import Image
from utils.r2_utils import upload_bytes_to_r2
from flask import Blueprint, jsonify, request, session
from repos.artists_repo import get_artist_profile_by_user_id
from repos.releases_repo import (
    create_release_draft,
    get_release_artists,
    get_release_by_id,
    list_all_releases,
    list_releases_for_creator,
)

release_bp = Blueprint("releases", __name__)


def _sanitize_filename_part(value: str) -> str:
    value = (value or "").strip()
    value = re.sub(r"[^A-Za-z0-9_-]+", "_", value)
    return value[:80] or "release"


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

        if not release_title:
            return jsonify({"error": "Release title is required."}), 400

        if release_type not in {"single", "ep", "album"}:
            return jsonify({"error": "Release type must be single, ep, or album."}), 400

        if not isinstance(raw_artists, list) or not raw_artists:
            return jsonify({"error": "At least one artist is required."}), 400

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
        )
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