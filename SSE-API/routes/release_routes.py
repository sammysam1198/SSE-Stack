from flask import Blueprint, jsonify, request, session

release_bp = Blueprint("releases", __name__)


def _current_user_id():
    return session.get("user_id")


def _current_role():
    return session.get("role")


def _require_login():
    return _current_user_id() is not None


def _is_privileged():
    return _current_role() in {"admin", "developer"}


@release_bp.post("")
def create_release():
    if not _require_login():
        return jsonify({"error": "Unauthorized."}), 401

    data = request.get_json(silent=True) or {}

    release_title = (data.get("release_title") or "").strip()
    release_type = (data.get("release_type") or "").strip()
    language = (data.get("language") or "").strip() or None
    preferred_release_date = (data.get("preferred_release_date") or "").strip() or None
    pitch = (data.get("pitch") or "").strip() or None
    lyrics = (data.get("lyrics") or "").strip() or None
    genre_notes = (data.get("genre_notes") or "").strip() or None
    artist = (data.get("artist") or "").strip() or None

    if not release_title:
        return jsonify({"error": "Release title is required."}), 400

    if release_type not in {"single", "ep", "album"}:
        return jsonify({"error": "Release type must be single, ep, or album."}), 400

    if _current_role() == "artist":
        artist = None

    fake_release = {
        "id": 42,
        "release_title": release_title,
        "release_type": release_type,
        "language": language,
        "preferred_release_date": preferred_release_date,
        "pitch": pitch,
        "lyrics": lyrics,
        "genre_notes": genre_notes,
        "status": "draft",
        "artist": artist,
        "owner_user_id": _current_user_id(),
    }

    return jsonify({
        "message": "Release draft created.",
        "release": fake_release
    }), 201


@release_bp.get("")
def list_releases():
    if not _require_login():
        return jsonify({"error": "Unauthorized."}), 401

    artist = (request.args.get("artist") or "").strip() or None

    if _current_role() == "artist":
        artist = None

    fake_releases = [
        {
            "id": 42,
            "release_title": "Example Release",
            "release_type": "single",
            "status": "draft",
            "artist": artist,
        }
    ]

    return jsonify({"releases": fake_releases}), 200


@release_bp.get("/<int:submission_id>")
def get_release(submission_id: int):
    if not _require_login():
        return jsonify({"error": "Unauthorized."}), 401

    fake_release = {
        "id": submission_id,
        "release_title": "Example Release",
        "release_type": "single",
        "language": "English",
        "preferred_release_date": "2026-05-15",
        "pitch": "A dreamy neon single.",
        "lyrics": "",
        "genre_notes": "Synthwave, Chillsynth",
        "status": "draft",
        "owner_user_id": _current_user_id(),
    }

    if _current_role() == "artist" and fake_release["owner_user_id"] != _current_user_id():
        return jsonify({"error": "Forbidden."}), 403

    return jsonify({"release": fake_release}), 200


@release_bp.patch("/<int:submission_id>")
def update_release(submission_id: int):
    if not _require_login():
        return jsonify({"error": "Unauthorized."}), 401

    data = request.get_json(silent=True) or {}

    release_title = (data.get("release_title") or "").strip()
    release_type = (data.get("release_type") or "").strip()
    language = (data.get("language") or "").strip() or None
    preferred_release_date = (data.get("preferred_release_date") or "").strip() or None
    pitch = (data.get("pitch") or "").strip() or None
    lyrics = (data.get("lyrics") or "").strip() or None
    genre_notes = (data.get("genre_notes") or "").strip() or None

    if not release_title:
        return jsonify({"error": "Release title is required."}), 400

    if release_type not in {"single", "ep", "album"}:
        return jsonify({"error": "Release type must be single, ep, or album."}), 400

    fake_owner_user_id = _current_user_id()

    if _current_role() == "artist" and fake_owner_user_id != _current_user_id():
        return jsonify({"error": "Forbidden."}), 403

    updated_release = {
        "id": submission_id,
        "release_title": release_title,
        "release_type": release_type,
        "language": language,
        "preferred_release_date": preferred_release_date,
        "pitch": pitch,
        "lyrics": lyrics,
        "genre_notes": genre_notes,
        "status": "draft",
    }

    return jsonify({
        "message": "Release updated.",
        "release": updated_release
    }), 200