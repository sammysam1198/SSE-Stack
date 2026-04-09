from flask import Blueprint, request, jsonify, session

artists_bp = Blueprint("artists", __name__)


def _current_user_id():
    return session.get("user_id")


def _current_role():
    return session.get("role")


def _is_admin_or_dev():
    return _current_role() in {"admin", "developer"}


@artists_bp.get("")
def list_artists():
    # public
    # TODO: fetch active artist directory records from repo
    return jsonify({"artists": []}), 200


@artists_bp.get("/<int:artist_id>")
def get_artist(artist_id: int):
    # public
    # TODO: fetch artist profile
    return jsonify({"artist": {"id": artist_id}}), 200


@artists_bp.get("/slug/<string:slug>")
def get_artist_by_slug(slug: str):
    # public
    # TODO: fetch artist profile by slug when you add slug column
    return jsonify({"artist": {"slug": slug}}), 200


@artists_bp.patch("/<int:artist_id>")
def update_artist(artist_id: int):
    user_id = _current_user_id()
    role = _current_role()

    if not user_id:
        return jsonify({"error": "Not authenticated."}), 401

    # TODO:
    # 1. fetch target artist profile
    # 2. if artist role, confirm this is their own profile
    # 3. update allowed fields only

    data = request.get_json(silent=True) or {}
    return jsonify({
        "message": "Artist profile updated.",
        "artist_id": artist_id,
        "updated_fields": list(data.keys()),
        "role": role
    }), 200