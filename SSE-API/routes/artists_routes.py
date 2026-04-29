import os
import re
from pathlib import Path
from typing import Any
import traceback

from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

from repos.artists_repo import (
    get_artist_profile_by_slug,
    get_artist_profile_by_user_id,
    list_artist_profiles,
    update_artist_profile_by_user_id,
)
from utils.auth_utils import get_current_user
from utils.r2_utils import upload_bytes_to_r2, list_object_keys_with_prefix


artists_bp = Blueprint("artist", __name__)

MAX_ARTIST_ASSET_SIZE_BYTES = 10 * 1024 * 1024

ARTIST_ASSET_CONFIG = {
    "banner": {
        "folder": "banners",
        "db_field": "dashboard_banner_key",
        "label": "banner",
    },
    "logo": {
        "folder": "logos",
        "db_field": "artist_logo_key",
        "label": "logo",
    },
    "portrait": {
        "folder": "portraits",
        "db_field": "profile_portrait_key",
        "label": "portrait",
    },
}

ALLOWED_IMAGE_EXTENSIONS = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "webp": "image/webp",
    "gif": "image/gif",
}

def _normalize_optional_date(value: Any):
    value = _normalize_string(value)
    return value or None

def _normalize_artist_token(value: Any) -> str:
    value = str(value or "").strip()
    value = re.sub(r"\s+", "", value)
    value = re.sub(r"[^A-Za-z0-9]", "", value)
    return value or "Artist"


def _normalize_optional_int(value):
    if value is None:
        return None

    if isinstance(value, int):
        return value

    value = str(value).strip()
    if value == "":
        return None

    try:
        return int(value)
    except ValueError:
        raise ValueError(f"Invalid integer value: {value}")


def _get_file_extension(filename: str) -> str:
    if "." not in filename:
        raise ValueError("File must include a valid extension.")

    ext = filename.rsplit(".", 1)[-1].lower().strip()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValueError("Unsupported image type. Use JPG, JPEG, PNG, WEBP, or GIF.")

    return ext


def _next_artist_asset_number(*, artist_name: str, asset_type: str, folder: str) -> int:
    artist_token = _normalize_artist_token(artist_name)
    prefix = f"artist_uploads/{folder}/{artist_token}_{asset_type}_"

    keys = list_object_keys_with_prefix(prefix)
    numbers = []

    for key in keys:
        filename = Path(key).name
        match = re.match(
            rf"^{re.escape(artist_token)}_{re.escape(asset_type)}_(\d+)\.[A-Za-z0-9]+$",
            filename,
        )
        if match:
            numbers.append(int(match.group(1)))

    return (max(numbers) + 1) if numbers else 1


def _build_artist_asset_key(*, artist_name: str, asset_type: str, folder: str, ext: str) -> str:
    artist_token = _normalize_artist_token(artist_name)
    next_number = _next_artist_asset_number(
        artist_name=artist_name,
        asset_type=asset_type,
        folder=folder,
    )
    return f"artist_uploads/{folder}/{artist_token}_{asset_type}_{next_number:02d}.{ext}"


def _validate_uploaded_image(file_storage):
    if not file_storage:
        raise ValueError("No file was provided.")

    filename = secure_filename(file_storage.filename or "")
    if not filename:
        raise ValueError("File name is missing.")

    ext = _get_file_extension(filename)
    content_type = ALLOWED_IMAGE_EXTENSIONS[ext]

    file_storage.stream.seek(0, os.SEEK_END)
    file_size = file_storage.stream.tell()
    file_storage.stream.seek(0)

    if file_size <= 0:
        raise ValueError("Uploaded file is empty.")

    if file_size > MAX_ARTIST_ASSET_SIZE_BYTES:
        raise ValueError("Image must be 10 MB or smaller.")

    return {
        "filename": filename,
        "ext": ext,
        "content_type": content_type,
        "size": file_size,
    }


def _normalize_string(value: Any) -> str:
    return str(value or "").strip()


def _normalize_optional_url(value: Any) -> str:
    value = _normalize_string(value)
    if not value:
        return ""

    if not re.match(r"^https://", value, re.IGNORECASE):
        raise ValueError("All links must start with https://")

    return value


def _normalize_slug(value: Any) -> str:
    value = _normalize_string(value).lower()
    value = re.sub(r"[^a-z0-9]+", "", value)
    return value


def _serialize_artist_profile(profile: dict | None):
    if not profile:
        return None

    return {
        "id": profile.get("id"),
        "user_id": profile.get("user_id"),
        "artist_name": profile.get("artist_name") or "",
        "bio": profile.get("bio") or "",
        "primary_genre": profile.get("primary_genre") or "",
        "primary_instrument": profile.get("primary_instrument") or "",
        "primary_vibe": profile.get("primary_vibe") or "",
        "location": profile.get("location") or "",
        "spotify_url": profile.get("spotify_url") or "",
        "soundcloud_url": profile.get("soundcloud_url") or "",
        "is_roster_active": bool(profile.get("is_roster_active")),
        "created_at": profile.get("created_at").isoformat() if profile.get("created_at") else None,
        "updated_at": profile.get("updated_at").isoformat() if profile.get("updated_at") else None,
        "tagline": profile.get("tagline") or "",
        "publisher": profile.get("publisher") or "",
        "first_name": profile.get("first_name") or "",
        "last_name": profile.get("last_name") or "",
        "artist_page": profile.get("artist_page") or "",
        "dashboard_banner_key": profile.get("dashboard_banner_key") or "",
        "artist_logo_key": profile.get("artist_logo_key") or "",
        "profile_portrait_key": profile.get("profile_portrait_key") or "",
        "apple_music_url": profile.get("apple_music_url") or "",
        "youtube_music_url": profile.get("youtube_music_url") or "",
        "youtube_channel_url": profile.get("youtube_channel_url") or "",
        "tidal_url": profile.get("tidal_url") or "",
        "threads_url": profile.get("threads_url") or "",
        "instagram_url": profile.get("instagram_url") or "",
        "bandcamp_url": profile.get("bandcamp_url") or "",
        "tiktok_url": profile.get("tiktok_url") or "",
        "twitter_url": profile.get("twitter_url") or "",
        "deezer_url": profile.get("deezer_url") or "",
        "beatport_url": profile.get("beatport_url") or "",
        "amazon_music_url": profile.get("amazon_music_url") or "",
        "facebook_url": profile.get("facebook_url") or "",
        "website_url": profile.get("website_url") or "",
         "birthday": profile.get("birthday") or "",
         "city": profile.get("city") or "",
         "state": profile.get("state") or "",
         "country": profile.get("country"),
         "ipi": profile.get("ipi") or "",
         "pro": profile.get("pro") or "",
        "spotify_embed": profile.get("spotify_embed") or "",
        "featured_video_embed": profile.get("featured_video_embed") or "",
        "featured_video_name": profile.get("featured_video_name") or "",
        "video2_embed": profile.get("video2_embed") or "",
        "video2_name": profile.get("video2_name") or "",
        "video3_embed": profile.get("video3_embed") or "",
        "video3_name": profile.get("video3_name") or "",
        "genre2": profile.get("genre2") or "",
        "genre3": profile.get("genre3") or "",
        "role2": profile.get("role2") or "",
        "role3": profile.get("role3") or "",
    }


def _require_logged_in_user():
    user = get_current_user()
    if not user:
        return None, (jsonify({"error": "Unauthorized."}), 401)
    return user, None


def _can_view_or_edit_own_profile(user: dict | None) -> bool:
    if not user:
        return False
    return user.get("role") in {"artist", "admin", "developer"}


@artists_bp.get("/public")
def get_public_artist_profiles():
    profiles = list_artist_profiles()

    visible_profiles = [
        profile for profile in profiles
        if profile.get("is_roster_active") is True
        and (profile.get("artist_name") or "").strip()
        and (profile.get("artist_page") or "").strip()
    ]

    return jsonify({
        "artist_profiles": [
            _serialize_artist_profile(profile)
            for profile in visible_profiles
        ]
    }), 200

@artists_bp.get("/me")
def get_my_artist_profile():
    user, error_response = _require_logged_in_user()
    if error_response:
        return error_response

    if not _can_view_or_edit_own_profile(user):
        return jsonify({"error": "Forbidden."}), 403

    profile = get_artist_profile_by_user_id(user["user_id"])
    if not profile:
        return jsonify({"error": "Artist profile not found."}), 404

    return jsonify({"artist_profile": _serialize_artist_profile(profile)}), 200


@artists_bp.patch("/me")
def patch_my_artist_profile():
    user, error_response = _require_logged_in_user()
    if error_response:
        return error_response

    if not _can_view_or_edit_own_profile(user):
        return jsonify({"error": "Forbidden."}), 403

    existing_profile = get_artist_profile_by_user_id(user["user_id"])
    if not existing_profile:
        return jsonify({"error": "Artist profile not found."}), 404

    data = request.get_json(silent=True) or {}

    try:
        updates = {
            "artist_name": _normalize_string(data.get("artist_name")),
            "bio": _normalize_string(data.get("bio")),
            "primary_genre": _normalize_string(data.get("primary_genre")),
            "primary_instrument": _normalize_string(data.get("primary_instrument")),
            "primary_vibe": _normalize_string(data.get("primary_vibe")),
            "location": _normalize_string(data.get("location")),
            "spotify_url": _normalize_optional_url(data.get("spotify_url")),
            "soundcloud_url": _normalize_optional_url(data.get("soundcloud_url")),
            "tagline": _normalize_string(data.get("tagline")),
            "publisher": _normalize_string(data.get("publisher")),
            "first_name": _normalize_string(data.get("first_name")),
            "last_name": _normalize_string(data.get("last_name")),
            "artist_page": _normalize_slug(data.get("artist_page")),
            "dashboard_banner_key": _normalize_string(data.get("dashboard_banner_key")),
            "artist_logo_key": _normalize_string(data.get("artist_logo_key")),
            "profile_portrait_key": _normalize_string(data.get("profile_portrait_key")),
            "apple_music_url": _normalize_optional_url(data.get("apple_music_url")),
            "youtube_music_url": _normalize_optional_url(data.get("youtube_music_url")),
            "youtube_channel_url": _normalize_optional_url(data.get("youtube_channel_url")),
            "tidal_url": _normalize_optional_url(data.get("tidal_url")),
            "threads_url": _normalize_optional_url(data.get("threads_url")),
            "instagram_url": _normalize_optional_url(data.get("instagram_url")),
            "bandcamp_url": _normalize_optional_url(data.get("bandcamp_url")),
            "tiktok_url": _normalize_optional_url(data.get("tiktok_url")),
            "twitter_url": _normalize_optional_url(data.get("twitter_url")),
            "deezer_url": _normalize_optional_url(data.get("deezer_url")),
            "beatport_url": _normalize_optional_url(data.get("beatport_url")),
            "amazon_music_url": _normalize_optional_url(data.get("amazon_music_url")),
            "facebook_url": _normalize_optional_url(data.get("facebook_url")),
            "website_url": _normalize_string(data.get("website_url")),
            "birthday": _normalize_optional_date(data.get("birthday")),
            "city": _normalize_string(data.get("city")),
            "state": _normalize_string(data.get("state")),
            "country": _normalize_string(data.get("country")),
            "ipi": _normalize_optional_int(data.get("ipi")),
            "pro": _normalize_string(data.get("pro")),
            "spotify_embed": _normalize_string(data.get("spotify_embed")),
            "featured_video_embed": _normalize_string(data.get("featured_video_embed")),
            "featured_video_name": _normalize_string(data.get("featured_video_name")),
            "video2_embed": _normalize_string(data.get("video2_embed")),
            "video2_name": _normalize_string(data.get("video2_name")),
            "video3_embed": _normalize_string(data.get("video3_embed")),
            "video3_name": _normalize_string(data.get("video3_name")),
            "genre2": _normalize_string(data.get("genre2")),
            "genre3": _normalize_string(data.get("genre3")),
            "role2": _normalize_string(data.get("role2")),
            "role3": _normalize_string(data.get("role3")),
        }
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    artist_name_for_slug = updates["artist_name"] or existing_profile.get("artist_name") or ""
    if not updates["artist_page"]:
        updates["artist_page"] = existing_profile.get("artist_page") or _normalize_slug(artist_name_for_slug)

    try:
        print("RAW DATA:", data)
        print("UPDATES:", updates)

        updated = update_artist_profile_by_user_id(user["user_id"], updates)
        if not updated:
            return jsonify({"error": "Failed to update artist profile."}), 500

        return jsonify({"artist_profile": updated}), 200

    except Exception as exc:
        print("PATCH FAILED:", repr(exc))
        traceback.print_exc()
        return jsonify({"error": "Patch failed.", "details": str(exc)}), 500

@artists_bp.post("/me/upload-asset")
def upload_my_artist_asset():
    user, error_response = _require_logged_in_user()
    if error_response:
        return error_response

    if not _can_view_or_edit_own_profile(user):
        return jsonify({"error": "Forbidden."}), 403

    profile = get_artist_profile_by_user_id(user["user_id"])
    if not profile:
        return jsonify({"error": "Artist profile not found."}), 404

    asset_type = _normalize_string(request.form.get("asset_type")).lower()
    if asset_type not in ARTIST_ASSET_CONFIG:
        return jsonify({"error": "Invalid asset type. Use banner, logo, or portrait."}), 400

    file = request.files.get("file")
    try:
        file_info = _validate_uploaded_image(file)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    asset_config = ARTIST_ASSET_CONFIG[asset_type]
    artist_name = profile.get("artist_name") or "Artist"

    object_key = _build_artist_asset_key(
        artist_name=artist_name,
        asset_type=asset_config["label"],
        folder=asset_config["folder"],
        ext=file_info["ext"],
    )

    try:
        file_bytes = file.read()

        saved_key = upload_bytes_to_r2(
            data=file_bytes,
            object_key=object_key,
            content_type=file_info["content_type"],
            content_disposition=f'inline; filename="{Path(object_key).name}"',
        )
    except Exception as exc:
        return jsonify({"error": f"Upload failed: {exc}"}), 500

    try:
        updated_profile = update_artist_profile_by_user_id(
            user["user_id"],
            {
                asset_config["db_field"]: saved_key
            },
        )
    except Exception as exc:
        return jsonify({"error": f"Profile update failed after upload: {exc}"}), 500

    return jsonify({
        "message": f"{asset_type.capitalize()} uploaded successfully.",
        "asset_type": asset_type,
        "db_field": asset_config["db_field"],
        "object_key": saved_key,
        "artist_profile": _serialize_artist_profile(updated_profile),
    }), 200


@artists_bp.get("/slug/<artist_page>")
def get_artist_profile_by_page_slug(artist_page: str):
    profile = get_artist_profile_by_slug(artist_page)
    if not profile:
        return jsonify({"error": "Artist profile not found."}), 404

    return jsonify({"artist_profile": _serialize_artist_profile(profile)}), 200


@artists_bp.get("")
def get_all_artist_profiles():
    user, error_response = _require_logged_in_user()
    if error_response:
        return error_response

    if user.get("role") not in {"admin", "developer"}:
        return jsonify({"error": "Forbidden."}), 403

    profiles = list_artist_profiles()
    return jsonify({
        "artist_profiles": [_serialize_artist_profile(profile) for profile in profiles]
    }), 200