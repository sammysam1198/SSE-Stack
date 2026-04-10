from config.db import (
    execute_returning_one,
    execute_write,
    fetch_all,
    fetch_one,
)


def create_release_submission(
    artist_profile_id: int,
    created_by_user_id: int,
    release_title: str,
    release_type: str,
    artist_notes: str | None = None,
):
    query = """
        INSERT INTO release_submissions (
            artist_profile_id,
            created_by_user_id,
            release_title,
            release_type,
            artist_notes
        )
        VALUES (%s, %s, %s, %s, %s)
        RETURNING *
    """
    return execute_returning_one(
        query,
        (
            artist_profile_id,
            created_by_user_id,
            release_title,
            release_type,
            artist_notes,
        ),
    )


def list_all_releases():
    query = """
        SELECT *
        FROM release_submissions
        ORDER BY created_at DESC
    """
    return fetch_all(query)


def list_releases_for_artist(artist_profile_id: int):
    query = """
        SELECT *
        FROM release_submissions
        WHERE artist_profile_id = %s
        ORDER BY created_at DESC
    """
    return fetch_all(query, (artist_profile_id,))


def get_release_by_id(release_id: int):
    query = """
        SELECT *
        FROM release_submissions
        WHERE id = %s
    """
    return fetch_one(query, (release_id,))


def update_release_submission(
    release_id: int,
    release_title: str,
    release_type: str,
    artist_notes: str | None = None,
):
    query = """
        UPDATE release_submissions
        SET
            release_title = %s,
            release_type = %s,
            artist_notes = %s,
            updated_at = NOW()
        WHERE id = %s
    """
    execute_write(query, (release_title, release_type, artist_notes, release_id))


def delete_release_submission(release_id: int):
    query = """
        DELETE FROM release_submissions
        WHERE id = %s
    """
    execute_write(query, (release_id,))


def submit_release_submission(release_id: int):
    query = """
        UPDATE release_submissions
        SET
            status = 'submitted',
            submitted_at = NOW(),
            updated_at = NOW()
        WHERE id = %s
    """
    execute_write(query, (release_id,))


def approve_release_submission(release_id: int, reviewed_by_user_id: int):
    query = """
        UPDATE release_submissions
        SET
            status = 'approved',
            reviewed_by_user_id = %s,
            reviewed_at = NOW(),
            approved_at = NOW(),
            updated_at = NOW()
        WHERE id = %s
    """
    execute_write(query, (reviewed_by_user_id, release_id))


def reject_release_submission(release_id: int, reviewed_by_user_id: int, admin_notes: str | None = None):
    query = """
        UPDATE release_submissions
        SET
            status = 'rejected',
            reviewed_by_user_id = %s,
            reviewed_at = NOW(),
            rejected_at = NOW(),
            admin_notes = %s,
            updated_at = NOW()
        WHERE id = %s
    """
    execute_write(query, (reviewed_by_user_id, admin_notes, release_id))


def request_release_changes(release_id: int, reviewed_by_user_id: int, admin_notes: str | None = None):
    query = """
        UPDATE release_submissions
        SET
            status = 'changes_requested',
            reviewed_by_user_id = %s,
            reviewed_at = NOW(),
            requested_changes_at = NOW(),
            admin_notes = %s,
            updated_at = NOW()
        WHERE id = %s
    """
    execute_write(query, (reviewed_by_user_id, admin_notes, release_id))


def create_release_asset(
    release_submission_id: int,
    asset_type: str,
    file_name: str | None = None,
    mime_type: str | None = None,
    storage_url: str | None = None,
    external_url: str | None = None,
    byte_size: int | None = None,
    width_px: int | None = None,
    height_px: int | None = None,
    duration_seconds: float | None = None,
    uploaded_by_user_id: int | None = None,
):
    query = """
        INSERT INTO release_assets (
            release_submission_id,
            asset_type,
            file_name,
            mime_type,
            storage_url,
            external_url,
            byte_size,
            width_px,
            height_px,
            duration_seconds,
            uploaded_by_user_id
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING *
    """
    return execute_returning_one(
        query,
        (
            release_submission_id,
            asset_type,
            file_name,
            mime_type,
            storage_url,
            external_url,
            byte_size,
            width_px,
            height_px,
            duration_seconds,
            uploaded_by_user_id,
        ),
    )


def list_release_assets(release_submission_id: int):
    query = """
        SELECT *
        FROM release_assets
        WHERE release_submission_id = %s
        ORDER BY created_at ASC
    """
    return fetch_all(query, (release_submission_id,))


def get_release_asset_by_id(asset_id: int):
    query = """
        SELECT *
        FROM release_assets
        WHERE id = %s
    """
    return fetch_one(query, (asset_id,))


def delete_release_asset(asset_id: int):
    query = """
        DELETE FROM release_assets
        WHERE id = %s
    """
    execute_write(query, (asset_id,))