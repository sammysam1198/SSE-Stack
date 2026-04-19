from typing import Any

from config.db import fetch_all, fetch_one, get_db_conn


def create_release_draft(
    *,
    submitting_user_id: int,
    artist_profile_id: int | None,
    main_artist_name: str,
    release_title: str,
    release_type: str,
    preferred_release_date: str | None = None,
    primary_genre: str | None = None,
    other_genres: str | None = None,
    release_pitch: str | None = None,
    artists: list[dict[str, Any]] | None = None,
):
    artists = artists or []

    conn = get_db_conn()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO release_submissions (
                        submitting_user_id,
                        artist_profile_id,
                        main_artist_name,
                        release_title,
                        release_type,
                        preferred_release_date,
                        primary_genre,
                        other_genres,
                        release_pitch
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING *
                    """,
                    (
                        submitting_user_id,
                        artist_profile_id,
                        main_artist_name,
                        release_title,
                        release_type,
                        preferred_release_date,
                        primary_genre,
                        other_genres,
                        release_pitch,
                    ),
                )
                release = cur.fetchone()
                release_id = release["id"]

                for index, artist in enumerate(artists, start=1):
                    cur.execute(
                        """
                        INSERT INTO release_submission_artists (
                            release_submission_id,
                            artist_order,
                            role_type,
                            display_name,
                            email,
                            first_name,
                            last_name,
                            ipi,
                            pro,
                            publisher,
                            spotify_url,
                            apple_music_url,
                            youtube_url,
                            soundcloud_url,
                            saved_featured_artist_id
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            release_id,
                            index,
                            artist.get("role_type"),
                            artist.get("display_name"),
                            artist.get("email"),
                            artist.get("first_name"),
                            artist.get("last_name"),
                            artist.get("ipi"),
                            artist.get("pro"),
                            artist.get("publisher"),
                            artist.get("spotify_url"),
                            artist.get("apple_music_url"),
                            artist.get("youtube_url"),
                            artist.get("soundcloud_url"),
                            artist.get("saved_featured_artist_id"),
                        ),
                    )

                cur.execute(
                    """
                    SELECT *
                    FROM release_submission_artists
                    WHERE release_submission_id = %s
                    ORDER BY artist_order ASC
                    """,
                    (release_id,),
                )
                release_artists = cur.fetchall()

        release["artists"] = release_artists
        return release
    finally:
        conn.close()


def list_releases_for_submitter(submitting_user_id: int):
    query = """
        SELECT *
        FROM release_submissions
        WHERE submitting_user_id = %s
        ORDER BY created_at DESC
    """
    return fetch_all(query, (submitting_user_id,))


def list_all_releases():
    query = """
        SELECT *
        FROM release_submissions
        ORDER BY created_at DESC
    """
    return fetch_all(query)


def get_release_by_id(release_id: int):
    query = """
        SELECT *
        FROM release_submissions
        WHERE id = %s
        LIMIT 1
    """
    return fetch_one(query, (release_id,))


def get_release_artists(release_id: int):
    query = """
        SELECT *
        FROM release_submission_artists
        WHERE release_submission_id = %s
        ORDER BY artist_order ASC
    """
    return fetch_all(query, (release_id,))