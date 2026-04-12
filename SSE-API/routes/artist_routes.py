from flask import Blueprint, request, jsonify, session

from repos.artists_repo import (
    list_active_artists,
    get_artist_by_id,
    get_artist_by_slug,
    get_artist_by_user_id,
    create_artist_profile_for_user,
    update_artist_profile_by_user_id,
)
from repos.users_repo import get_user_by_id

artists_bp = Blueprint("artists", __name__)


def _current_user_id():
    return session.get("user_id")


def _current_role():
    return session.get("role")


def _normalize_text(value, max_length=None):
    value = (value or "").strip()
    if max_length is not None:
        value = value[:max_length]
    return value


def _normalize_url(value, max_length=500):
    value = (value or "").strip()
    if not value:
        return ""

    if not (value.startswith("https://") or value.startswith("/static/")):
        raise ValueError("Links must start with https:// or /static/")

    return value[:max_length]


def _serialize_artist_profile(profile: dict):
    return {
        "id": profile["id"],
        "user_id": profile["user_id"],
        "artist_name": profile.get("artist_name") or "",
        "tagline": profile.get("tagline") or "",
        "bio": profile.get("bio") or "",
        "hero_image_url": profile.get("hero_image_url") or "",
        "portrait_image_url": profile.get("portrait_image_url") or "",
        "tag_1": profile.get("tag_1") or "",
        "tag_2": profile.get("tag_2") or "",
        "tag_3": profile.get("tag_3") or "",
        "spotify_url": profile.get("spotify_url") or "",
        "youtube_url": profile.get("youtube_url") or "",
        "instagram_url": profile.get("instagram_url") or "",
        "slug": profile.get("slug"),
        "is_roster_active": profile.get("is_roster_active"),
        "created_at": profile.get("created_at"),
        "updated_at": profile.get("updated_at"),
    }


@artists_bp.get("")
def list_artists():
    artists = list_active_artists()
    return jsonify({"artists": artists}), 200


@artists_bp.get("/<int:artist_id>")
def get_artist(artist_id: int):
    artist = get_artist_by_id(artist_id)

    if not artist:
        return jsonify({"error": "Artist not found."}), 404

    return jsonify({"artist": _serialize_artist_profile(artist)}), 200


@artists_bp.get("/slug/<string:slug>")
def get_artist_by_slug_route(slug: str):
    artist = get_artist_by_slug(slug)

    if not artist:
        return jsonify({"error": "Artist not found."}), 404

    return jsonify({"artist": _serialize_artist_profile(artist)}), 200


@artists_bp.get("/me")
def get_my_artist_profile():
    user_id = _current_user_id()
    role = _current_role()

    if not user_id:
        return jsonify({"error": "Not authenticated."}), 401

    if role not in {"artist", "developer"}:
        return jsonify({"error": "Forbidden."}), 403

    profile = get_artist_by_user_id(user_id)

    if not profile:
        user = get_user_by_id(user_id)
        fallback_name = None

        if user:
            fallback_name = user.get("username") or user.get("email", "").split("@")[0]

        profile = create_artist_profile_for_user(user_id, fallback_name)

    return jsonify({"artist_profile": _serialize_artist_profile(profile)}), 200


@artists_bp.patch("/me")
def update_my_artist_profile():
    user_id = _current_user_id()
    role = _current_role()

    if not user_id:
        return jsonify({"error": "Not authenticated."}), 401

    if role not in {"artist", "developer"}:
        return jsonify({"error": "Forbidden."}), 403

    existing_profile = get_artist_by_user_id(user_id)

    if not existing_profile:
        user = get_user_by_id(user_id)
        fallback_name = None

        if user:
            fallback_name = user.get("username") or user.get("email", "").split("@")[0]

        existing_profile = create_artist_profile_for_user(user_id, fallback_name)

    data = request.get_json(silent=True) or {}

    try:
        artist_name = _normalize_text(
            data.get("artist_name", existing_profile.get("artist_name")),
            max_length=120,
        )
        tagline = _normalize_text(
            data.get("tagline", existing_profile.get("tagline")),
            max_length=180,
        )
        bio = _normalize_text(
            data.get("bio", existing_profile.get("bio")),
            max_length=4000,
        )

        hero_image_url = _normalize_url(
            data.get("hero_image_url", existing_profile.get("hero_image_url", ""))
        )
        portrait_image_url = _normalize_url(
            data.get("portrait_image_url", existing_profile.get("portrait_image_url", ""))
        )

        tag_1 = _normalize_text(data.get("tag_1", existing_profile.get("tag_1")), max_length=60)
        tag_2 = _normalize_text(data.get("tag_2", existing_profile.get("tag_2")), max_length=60)
        tag_3 = _normalize_text(data.get("tag_3", existing_profile.get("tag_3")), max_length=60)

        spotify_url = _normalize_url(
            data.get("spotify_url", existing_profile.get("spotify_url", ""))
        )
        youtube_url = _normalize_url(
            data.get("youtube_url", existing_profile.get("youtube_url", ""))
        )
        instagram_url = _normalize_url(
            data.get("instagram_url", existing_profile.get("instagram_url", ""))
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    if not artist_name:
        return jsonify({"error": "Artist name is required."}), 400

    updated = update_artist_profile_by_user_id(
        user_id=user_id,
        artist_name=artist_name,
        tagline=tagline,
        bio=bio,
        hero_image_url=hero_image_url,
        portrait_image_url=portrait_image_url,
        tag_1=tag_1,
        tag_2=tag_2,
        tag_3=tag_3,
        spotify_url=spotify_url,
        youtube_url=youtube_url,
        instagram_url=instagram_url,
    )

    return jsonify({
        "message": "Artist profile updated.",
        "artist_profile": _serialize_artist_profile(updated),
    }), 200