from config.db import (
    execute_returning_one,
    execute_write,
    fetch_all,
    fetch_one,
)


def create_application(
    first_name: str,
    last_name: str,
    artist_name: str,
    email: str,
    phone: str | None = None,
    bio: str | None = None,
    primary_genre: str | None = None,
    links=None,
    notes: str | None = None,
    created_user_id: int | None = None,
):
    if links is None:
        links = []

    query = """
        INSERT INTO artist_applications (
            first_name,
            last_name,
            artist_name,
            email,
            phone,
            bio,
            primary_genre,
            links,
            notes,
            created_user_id
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s)
        RETURNING
            id,
            first_name,
            last_name,
            artist_name,
            email,
            status,
            created_at,
            updated_at
    """
    import json
    return execute_returning_one(
        query,
        (
            first_name,
            last_name,
            artist_name,
            email,
            phone,
            bio,
            primary_genre,
            json.dumps(links),
            notes,
            created_user_id,
        ),
    )


def list_applications():
    query = """
        SELECT
            id,
            first_name,
            last_name,
            artist_name,
            email,
            phone,
            primary_genre,
            status,
            reviewed_by_user_id,
            reviewed_at,
            review_notes,
            created_user_id,
            created_at,
            updated_at
        FROM artist_applications
        ORDER BY created_at DESC
    """
    return fetch_all(query)


def get_application_by_id(application_id: int):
    query = """
        SELECT *
        FROM artist_applications
        WHERE id = %s
    """
    return fetch_one(query, (application_id,))


def approve_application(application_id: int, reviewed_by_user_id: int):
    query = """
        UPDATE artist_applications
        SET
            status = 'approved',
            reviewed_by_user_id = %s,
            reviewed_at = NOW(),
            updated_at = NOW()
        WHERE id = %s
    """
    execute_write(query, (reviewed_by_user_id, application_id))


def deny_application(application_id: int, reviewed_by_user_id: int, review_notes: str | None = None):
    query = """
        UPDATE artist_applications
        SET
            status = 'denied',
            reviewed_by_user_id = %s,
            reviewed_at = NOW(),
            review_notes = %s,
            updated_at = NOW()
        WHERE id = %s
    """
    execute_write(query, (reviewed_by_user_id, review_notes, application_id))