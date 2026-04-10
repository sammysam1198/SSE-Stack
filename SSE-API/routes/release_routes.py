from flask import Blueprint, request, jsonify, session

releases_bp = Blueprint("releases", __name__)


def _current_user_id():
    return session.get("user_id")


def _current_role():
    return session.get("role")


def _is_admin_or_dev():
    return _current_role() in {"admin", "developer"}


@releases_bp.post("")
def create_release():
    user_id = _current_user_id()
    role = _current_role()

    if not user_id:
        return jsonify({"error": "Not authenticated."}), 401

    data = request.get_json(silent=True) or {}
    release_title = (data.get("release_title") or "").strip()
    release_type = (data.get("release_type") or "").strip().lower()
    artist_profile_id = data.get("artist_profile_id")

    if not release_title or release_type not in {"single", "ep", "album"}:
        return jsonify({"error": "Valid release_title and release_type are required."}), 400

    # TODO:
    # artist can create for self
    # admin/dev can create on behalf of artist
    # create release in repo

    return jsonify({
        "message": "Release draft created.",
        "created_by_user_id": user_id,
        "role": role,
        "artist_profile_id": artist_profile_id
    }), 201


@releases_bp.get("")
def list_releases():
    user_id = _current_user_id()
    role = _current_role()

    if not user_id:
        return jsonify({"error": "Not authenticated."}), 401

    # TODO:
    # admin/dev -> all releases
    # artist -> own only

    return jsonify({
        "releases": [],
        "role": role
    }), 200


@releases_bp.get("/<int:release_id>")
def get_release(release_id: int):
    user_id = _current_user_id()

    if not user_id:
        return jsonify({"error": "Not authenticated."}), 401

    # TODO: permission-check target release
    return jsonify({"release": {"id": release_id}}), 200


@releases_bp.patch("/<int:release_id>")
def update_release(release_id: int):
    user_id = _current_user_id()

    if not user_id:
        return jsonify({"error": "Not authenticated."}), 401

    data = request.get_json(silent=True) or {}

    # TODO:
    # artist -> own drafts only
    # admin/dev -> broader update permissions
    return jsonify({
        "message": "Release updated.",
        "release_id": release_id,
        "updated_fields": list(data.keys())
    }), 200


@releases_bp.delete("/<int:release_id>")
def delete_release(release_id: int):
    user_id = _current_user_id()

    if not user_id:
        return jsonify({"error": "Not authenticated."}), 401

    # TODO:
    # artist -> own draft only
    # admin/dev -> can delete
    return jsonify({
        "message": "Release deleted.",
        "release_id": release_id
    }), 200


@releases_bp.post("/<int:release_id>/submit")
def submit_release_for_review(release_id: int):
    user_id = _current_user_id()

    if not user_id:
        return jsonify({"error": "Not authenticated."}), 401

    # TODO:
    # validate required assets before submit
    # change status draft -> submitted
    return jsonify({
        "message": "Release submitted for review.",
        "release_id": release_id
    }), 200


@releases_bp.post("/<int:release_id>/assets")
def upload_release_asset(release_id: int):
    user_id = _current_user_id()

    if not user_id:
        return jsonify({"error": "Not authenticated."}), 401

    # multipart form handling placeholder
    asset_type = (request.form.get("asset_type") or "").strip()
    uploaded_file = request.files.get("file")
    external_url = (request.form.get("external_url") or "").strip()

    if not asset_type:
        return jsonify({"error": "asset_type is required."}), 400

    if not uploaded_file and not external_url:
        return jsonify({"error": "A file or external_url is required."}), 400

    # TODO:
    # validate asset type / file type / dimensions / storage upload
    # create release_assets row

    return jsonify({
        "message": "Release asset uploaded.",
        "release_id": release_id,
        "asset_type": asset_type
    }), 201


@releases_bp.delete("/<int:release_id>/assets/<int:asset_id>")
def delete_release_asset(release_id: int, asset_id: int):
    user_id = _current_user_id()
    if not user_id:
        return jsonify({"error": "Not authenticated."}), 401

    # TODO: permission check + storage delete
    return jsonify({
        "message": "Release asset deleted.",
        "release_id": release_id,
        "asset_id": asset_id
    }), 200


@releases_bp.get("/<int:release_id>/assets/<int:asset_id>/download")
def download_release_asset(release_id: int, asset_id: int):
    user_id = _current_user_id()
    if not user_id:
        return jsonify({"error": "Not authenticated."}), 401

    # TODO:
    # verify permission
    # return signed URL or proxied download
    return jsonify({
        "message": "Download route placeholder.",
        "release_id": release_id,
        "asset_id": asset_id
    }), 200


@releases_bp.post("/<int:release_id>/approve")
def approve_release(release_id: int):
    if not _is_admin_or_dev():
        return jsonify({"error": "Forbidden."}), 403

    # TODO: set status approved, send email
    return jsonify({"message": "Release approved.", "release_id": release_id}), 200


@releases_bp.post("/<int:release_id>/reject")
def reject_release(release_id: int):
    if not _is_admin_or_dev():
        return jsonify({"error": "Forbidden."}), 403

    data = request.get_json(silent=True) or {}
    admin_notes = (data.get("admin_notes") or "").strip()

    # TODO: set status rejected, store notes, send email
    return jsonify({
        "message": "Release rejected.",
        "release_id": release_id,
        "admin_notes": admin_notes
    }), 200


@releases_bp.post("/<int:release_id>/request-changes")
def request_release_changes(release_id: int):
    if not _is_admin_or_dev():
        return jsonify({"error": "Forbidden."}), 403

    data = request.get_json(silent=True) or {}
    admin_notes = (data.get("admin_notes") or "").strip()

    # TODO: set status changes_requested, store notes, send email
    return jsonify({
        "message": "Changes requested.",
        "release_id": release_id,
        "admin_notes": admin_notes
    }), 200


@releases_bp.get("/<int:release_id>/stats")
def get_release_stats(release_id: int):
    user_id = _current_user_id()
    if not user_id:
        return jsonify({"error": "Not authenticated."}), 401

    # TODO: fetch per-release stats integration or placeholder
    return jsonify({
        "release_id": release_id,
        "stats": {}
    }), 200