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

    if not release_title:
        return jsonify({"error": "Release title is required."}), 400

    if release_type not in {"single", "ep", "album"}:
        return jsonify({"error": "Release type must be single, ep, or album."}), 400

    artist = (data.get("artist") or "").strip() or None

    # TODO:
    # If artist role, ignore provided artist and use session-linked artist
    # If admin/dev, allow artist param
    # Insert DB row here

    fake_release = {
        "id": 42,
        "release_title": release_title,
        "release_type": release_type,
        "language": data.get("language"),
        "preferred_release_date": data.get("preferred_release_date"),
        "pitch": data.get("pitch"),
        "lyrics": data.get("lyrics"),
        "genre_notes": data.get("genre_notes"),
        "status": "draft",
        "artist": artist,
    }

    return jsonify({
        "message": "Release draft created.",
        "release": fake_release
    }), 201


@release_bp.get("/<int:submission_id>")
def get_release(submission_id: int):
    if not _require_login():
        return jsonify({"error": "Unauthorized."}), 401

    # TODO: replace with DB lookup
    release = {
        "id": submission_id,
        "release_title": "Example Release",
        "release_type": "single",
        "language": "English",
        "preferred_release_date": "2026-05-15",
        "pitch": "A dreamy neon single.",
        "lyrics": "",
        "genre_notes": "Synthwave, Chillsynth",
        "status": "draft",
        "artist_user_id": _current_user_id(),
    }

    if _current_role() == "artist" and release["artist_user_id"] != _current_user_id():
        return jsonify({"error": "Forbidden."}), 403

    return jsonify({"release": release}), 200

@release_bp.patch("/<int:submission_id>")
def update_release(submission_id: int):
    if not _require_login():
        return jsonify({"error": "Unauthorized."}), 401

    data = request.get_json(silent=True) or {}

    # TODO: DB lookup and ownership check
    release_owner_user_id = _current_user_id()

    if _current_role() == "artist" and release_owner_user_id != _current_user_id():
        return jsonify({"error": "Forbidden."}), 403

    updated_release = {
        "id": submission_id,
        "release_title": data.get("release_title"),
        "release_type": data.get("release_type"),
        "language": data.get("language"),
        "preferred_release_date": data.get("preferred_release_date"),
        "pitch": data.get("pitch"),
        "lyrics": data.get("lyrics"),
        "genre_notes": data.get("genre_notes"),
        "status": "draft",
    }

    return jsonify({
        "message": "Release updated.",
        "release": updated_release
    }), 200

@release_bp.get("")
def list_releases():
    if not _require_login():
        return jsonify({"error": "Unauthorized."}), 401

    artist = (request.args.get("artist") or "").strip() or None

    if _current_role() == "artist":
        artist = None  # ignore artist query for normal artists

    # TODO: replace with real DB query
    releases = [
        {
            "id": 42,
            "release_title": "Example Release",
            "release_type": "single",
            "status": "draft",
        }
    ]

    return jsonify({"releases": releases}), 200

