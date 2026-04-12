from flask import Blueprint, request, jsonify, session
from repos.artists_repo import (
    list_active_artists,
    get_artist_by_id,
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
        "legal_name": profile.get("legal_name") or "",
        "tagline": profile.get("tagline") or "",
        "bio": profile.get("bio") or "",
        "primary_genre": profile.get("primary_genre") or "",
        "primary_instrument": profile.get("primary_instrument") or "",
        "primary_vibe": profile.get("primary_vibe") or "",
        "publisher": profile.get("publisher") or "",
        "location": profile.get("location") or "",
        "profile_image_url": profile.get("profile_image_url") or "",
        "spotify_url": profile.get("spotify_url") or "",
        "youtube_url": profile.get("youtube_url") or "",
        "soundcloud_url": profile.get("soundcloud_url") or "",
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
def get_artist_by_slug(slug: str):
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
        primary_genre = _normalize_text(
            data.get("primary_genre", existing_profile.get("primary_genre")),
            max_length=60,
        )
        primary_instrument = _normalize_text(
            data.get("primary_instrument", existing_profile.get("primary_instrument")),
            max_length=60,
        )
        primary_vibe = _normalize_text(
            data.get("primary_vibe", existing_profile.get("primary_vibe")),
            max_length=60,
        )
        publisher = _normalize_text(
            data.get("publisher", existing_profile.get("publisher")),
            max_length=120,
        )
        location = _normalize_text(
            data.get("location", existing_profile.get("location")),
            max_length=120,
        )

        profile_image_url = _normalize_url(
            data.get("profile_image_url", existing_profile.get("profile_image_url", ""))
        )
        spotify_url = _normalize_url(
            data.get("spotify_url", existing_profile.get("spotify_url", ""))
        )
        youtube_url = _normalize_url(
            data.get("youtube_url", existing_profile.get("youtube_url", ""))
        )
        soundcloud_url = _normalize_url(
            data.get("soundcloud_url", existing_profile.get("soundcloud_url", ""))
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
        primary_genre=primary_genre,
        primary_instrument=primary_instrument,
        primary_vibe=primary_vibe,
        publisher=publisher,
        location=location,
        profile_image_url=profile_image_url,
        spotify_url=spotify_url,
        youtube_url=youtube_url,
        soundcloud_url=soundcloud_url,
    )

    return jsonify({
        "message": "Artist profile updated.",
        "artist_profile": _serialize_artist_profile(updated),
    }), 200