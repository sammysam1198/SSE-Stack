import re
from typing import Any
from flask import Blueprint, jsonify, request
from utils.auth_utils import get_current_user
from repos.artists_repo import (
    get_artist_profile_by_slug,
    get_artist_profile_by_user_id,
    list_artist_profiles,
    update_artist_profile_by_user_id,
)



artist_bp = Blueprint("artist", __name__, url_prefix="/api/artists")


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
        "birthday": profile.get("birthday").isoformat() if profile.get("birthday") else "",
        "city": profile.get("city") or "",
        "state": profile.get("state") or "",
        "country": profile.get("country") or "",
        "ipi": profile.get("ipi") or "",
        "pro": profile.get("pro") or "",
    }


def _can_manage_artist_profile(user: dict | None) -> bool:
    if not user:
        return False
    return user["role"] in {"artist", "admin", "developer"}


def _require_logged_in_user():
    user = get_current_user()
    if not user:
        return None, (jsonify({"error": "Unauthorized."}), 401)
    return user, None


@artist_bp.get("/me")
def get_my_artist_profile():
    user, error_response = _require_logged_in_user()
    if error_response:
        return error_response

    if not _can_manage_artist_profile(user):
        return jsonify({"error": "Forbidden."}), 403

    profile = get_artist_profile_by_user_id(user["user_id"])
    if not profile:
        return jsonify({"error": "Artist profile not found."}), 404

    return jsonify({"artist_profile": _serialize_artist_profile(profile)}), 200


@artist_bp.patch("/me")
def patch_my_artist_profile():
    user, error_response = _require_logged_in_user()
    if error_response:
        return error_response

    if not _can_manage_artist_profile(user):
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
            "birthday": _normalize_string(data.get("birthday")),
            "city": _normalize_string(data.get("city")),
            "state": _normalize_string(data.get("state")),
            "country": _normalize_string(data.get("country")),
            "ipi": _normalize_string(data.get("ipi")),
            "pro": _normalize_string(data.get("pro")),
        }
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    if not updates["artist_page"]:
        updates["artist_page"] = existing_profile.get("artist_page") or _normalize_slug(
            updates["artist_name"] or existing_profile.get("artist_name")
        )

    updated = update_artist_profile_by_user_id(user["user_id"], updates)
    if not updated:
        return jsonify({"error": "Failed to update artist profile."}), 500

    return jsonify({
        "message": "Artist profile updated successfully.",
        "artist_profile": _serialize_artist_profile(updated),
    }), 200


@artist_bp.get("/slug/<artist_page>")
def get_artist_profile_by_page_slug(artist_page: str):
    profile = get_artist_profile_by_slug(artist_page)
    if not profile:
        return jsonify({"error": "Artist profile not found."}), 404

    return jsonify({"artist_profile": _serialize_artist_profile(profile)}), 200


@artist_bp.get("")
def get_all_artist_profiles():
    user, error_response = _require_logged_in_user()
    if error_response:
        return error_response

    if user.get("role") not in {"admin", "developer"}:
        return jsonify({"error": "Forbidden."}), 403

    profiles = list_artist_profiles()
    return jsonify(
        {"artist_profiles": [_serialize_artist_profile(profile) for profile in profiles]}
    ), 200