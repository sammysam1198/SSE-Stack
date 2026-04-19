from flask import Blueprint, jsonify, request, session

from repos.artists_repo import get_artist_profile_by_user_id
from repos.releases_repo import (
    create_release_draft,
    get_release_artists,
    get_release_by_id,
    list_all_releases,
    list_releases_for_submitter,
)

release_bp = Blueprint("releases", __name__)


def _current_user_id():
    return session.get("user_id")


def _current_role():
    return session.get("role")


def _require_login():
    return _current_user_id() is not None


def _is_privileged():
    return _current_role() in {"admin", "developer"}


def _clean_text(value):
    value = (value or "").strip()
    return value or None


def _validate_artist_payload(raw_artist: dict, index: int):
    display_name = _clean_text(raw_artist.get("display_name"))
    email = _clean_text(raw_artist.get("email"))
    role_type = _clean_text(raw_artist.get("role_type")) or "featured"

    if role_type not in {"main", "featured"}:
        raise ValueError(f"Artist #{index}: role_type must be main or featured.")

    if not display_name:
        raise ValueError(f"Artist #{index}: artist name is required.")

    if not email:
        raise ValueError(f"Artist #{index}: email is required.")

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
    }


@release_bp.post("")
def create_release():
    if not _require_login():
        return jsonify({"error": "Unauthorized."}), 401

    data = request.get_json(silent=True) or {}

    release_title = _clean_text(data.get("release_title"))
    release_type = _clean_text(data.get("release_type"))
    preferred_release_date = _clean_text(data.get("preferred_release_date"))
    primary_genre = _clean_text(data.get("primary_genre"))
    other_genres = _clean_text(data.get("other_genres"))
    release_pitch = _clean_text(data.get("release_pitch"))
    raw_artists = data.get("artists") or []

    if not release_title:
        return jsonify({"error": "Release title is required."}), 400

    if release_type not in {"single", "ep", "album"}:
        return jsonify({"error": "Release type must be single, ep, or album."}), 400

    if not isinstance(raw_artists, list) or not raw_artists:
        return jsonify({"error": "At least one artist is required."}), 400

    if len(raw_artists) > 5:
        return jsonify({"error": "A maximum of 5 artists is allowed for now."}), 400

    try:
        artists = [
            _validate_artist_payload(artist, index + 1)
            for index, artist in enumerate(raw_artists)
        ]
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    main_artist = artists[0]
    main_artist["role_type"] = "main"

    artist_profile_id = None
    if _current_role() == "artist":
        profile = get_artist_profile_by_user_id(_current_user_id())
        if not profile:
            return jsonify({"error": "Artist profile not found."}), 404
        artist_profile_id = profile["id"]

    release = create_release_draft(
        submitting_user_id=_current_user_id(),
        artist_profile_id=artist_profile_id,
        main_artist_name=main_artist["display_name"],
        release_title=release_title,
        release_type=release_type,
        preferred_release_date=preferred_release_date,
        primary_genre=primary_genre,
        other_genres=other_genres,
        release_pitch=release_pitch,
        artists=artists,
    )

    return jsonify({
        "message": "Release draft created.",
        "release": release,
    }), 201


@release_bp.get("")
def list_releases():
    if not _require_login():
        return jsonify({"error": "Unauthorized."}), 401

    if _is_privileged():
        releases = list_all_releases()
    else:
        releases = list_releases_for_submitter(_current_user_id())

    return jsonify({"releases": releases}), 200


@release_bp.get("/<int:submission_id>")
def get_release(submission_id: int):
    if not _require_login():
        return jsonify({"error": "Unauthorized."}), 401

    release = get_release_by_id(submission_id)
    if not release:
        return jsonify({"error": "Release not found."}), 404

    if not _is_privileged() and release["submitting_user_id"] != _current_user_id():
        return jsonify({"error": "Forbidden."}), 403

    release["artists"] = get_release_artists(submission_id)

    return jsonify({"release": release}), 200