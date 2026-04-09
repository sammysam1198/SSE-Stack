from flask import Blueprint, request, jsonify, session

news_bp = Blueprint("news", __name__)


def _current_role():
    return session.get("role")


def _is_admin_or_dev():
    return _current_role() in {"admin", "developer"}


@news_bp.get("")
def list_news_posts():
    # public, published only
    # TODO: fetch published posts
    return jsonify({"news_posts": []}), 200


@news_bp.get("/<string:slug>")
def get_news_post(slug: str):
    # public, published only
    # TODO: fetch by slug
    return jsonify({"news_post": {"slug": slug}}), 200


@news_bp.post("")
def create_news_post():
    if not _is_admin_or_dev():
        return jsonify({"error": "Forbidden."}), 403

    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    body = (data.get("body") or "").strip()

    if not title or not body:
        return jsonify({"error": "Title and body are required."}), 400

    # TODO: create draft news post
    return jsonify({"message": "News post created."}), 201


@news_bp.patch("/<int:post_id>")
def update_news_post(post_id: int):
    if not _is_admin_or_dev():
        return jsonify({"error": "Forbidden."}), 403

    data = request.get_json(silent=True) or {}
    # TODO: update news post
    return jsonify({
        "message": "News post updated.",
        "post_id": post_id,
        "updated_fields": list(data.keys())
    }), 200


@news_bp.delete("/<int:post_id>")
def delete_news_post(post_id: int):
    if not _is_admin_or_dev():
        return jsonify({"error": "Forbidden."}), 403

    # TODO: delete or hard/archive delete based on your policy
    return jsonify({"message": "News post deleted.", "post_id": post_id}), 200


@news_bp.post("/<int:post_id>/publish")
def publish_news_post(post_id: int):
    if not _is_admin_or_dev():
        return jsonify({"error": "Forbidden."}), 403

    # TODO: set status published
    return jsonify({"message": "News post published.", "post_id": post_id}), 200


@news_bp.post("/<int:post_id>/archive")
def archive_news_post(post_id: int):
    if not _is_admin_or_dev():
        return jsonify({"error": "Forbidden."}), 403

    # TODO: set status archived
    return jsonify({"message": "News post archived.", "post_id": post_id}), 200