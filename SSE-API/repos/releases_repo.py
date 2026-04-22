from typing import Any

from config.db import fetch_all, fetch_one, execute_write, get_db_conn


from config.db import execute_write, fetch_one


def update_release_draft_by_id(
    release_id: int,
    created_by_user_id: int,
    *,
    release_title=None,
    release_type=None,
    preferred_release_date=None,
    primary_genre=None,
    other_genres=None,
    release_pitch=None,
):
    execute_write(
        """
        UPDATE release_submissions
        SET
            release_title = %s,
            release_type = %s,
            preferred_release_date = %s,
            primary_genre = %s,
            other_genres = %s,
            release_pitch = %s,
            updated_at = NOW()
        WHERE id = %s
          AND created_by_user_id = %s
          AND status = 'draft'
        """,
        (
            release_title,
            release_type,
            preferred_release_date,
            primary_genre,
            other_genres,
            release_pitch,
            release_id,
            created_by_user_id,
        ),
    )

    return fetch_one(
        "SELECT * FROM release_submissions WHERE id = %s",
        (release_id,)
    )

def create_release_draft(
    *,
    created_by_user_id: int,
    artist_profile_id: int | None,
    release_title: str,
    release_type: str,
    preferred_release_date: str | None = None,
    primary_genre: str | None = None,
    other_genres: str | None = None,
    release_pitch: str | None = None,
    artwork_object_key: str | None = None,
    artwork_original_filename: str | None = None,
    artwork_mime_type: str | None = None,
    artwork_size_bytes: int | None = None,
    artwork_width: int | None = None,
    artwork_height: int | None = None,
    artists: list[dict[str, Any]] | None = None,
    tracks: list[dict[str, Any]] | None = None,
):
    artists = artists or []
    tracks = tracks or []

    conn = get_db_conn()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO release_submissions (
                        artist_profile_id,
                        created_by_user_id,
                        release_title,
                        release_type,
                        preferred_release_date,
                        primary_genre,
                        other_genres,
                        release_pitch,
                        artwork_object_key,
                        artwork_original_filename,
                        artwork_mime_type,
                        artwork_size_bytes,
                        artwork_width,
                        artwork_height,
                        status
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'draft')
                    RETURNING *
                    """,
                    (
                        artist_profile_id,
                        created_by_user_id,
                        release_title,
                        release_type,
                        preferred_release_date,
                        primary_genre,
                        other_genres,
                        release_pitch,
                        artwork_object_key,
                        artwork_original_filename,
                        artwork_mime_type,
                        artwork_size_bytes,
                        artwork_width,
                        artwork_height,
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
                            first_name,
                            last_name,
                            ipi,
                            pro,
                            publisher,
                            spotify_url,
                            apple_music_url,
                            youtube_url,
                            soundcloud_url,
                            saved_featured_artist_id,
                            email,
                            split_percent
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            release_id,
                            index,
                            artist.get("role_type"),
                            artist.get("display_name"),
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
                            artist.get("email"),
                            artist.get("split_percent"),
                        ),
                    )

                for track in tracks:
                    cur.execute(
                        """
                        INSERT INTO release_tracks (
                            release_submission_id,
                            track_number,
                            track_title,
                            track_artists_text,
                            track_length,
                            language,
                            is_instrumental,
                            lyrics,
                            track_pitch,
                            audio_object_key,
                            audio_original_filename,
                            audio_mime_type,
                            audio_size_bytes,
                            sample_rate_hz,
                            bit_depth
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                        """,
                        (
                            release_id,
                            track.get("track_number"),
                            track.get("track_title"),
                            track.get("track_artists_text"),
                            track.get("track_length"),
                            track.get("language"),
                            track.get("is_instrumental", False),
                            track.get("lyrics"),
                            track.get("track_pitch"),
                            track.get("audio_object_key"),
                            track.get("audio_original_filename"),
                            track.get("audio_mime_type"),
                            track.get("audio_size_bytes"),
                            track.get("sample_rate_hz"),
                            track.get("bit_depth"),
                        ),
                    )
                    track_row = cur.fetchone()
                    track_id = track_row["id"]

                    for credit_index, credit in enumerate(track.get("credits", []), start=1):
                        cur.execute(
                            """
                            INSERT INTO release_track_credits (
                                release_track_id,
                                credit_order,
                                credit_type,
                                artist_name,
                                first_name,
                                last_name,
                                email,
                                ipi,
                                pro,
                                publisher
                            )
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """,
                            (
                                track_id,
                                credit_index,
                                credit.get("credit_type"),
                                credit.get("artist_name"),
                                credit.get("first_name"),
                                credit.get("last_name"),
                                credit.get("email"),
                                credit.get("ipi"),
                                credit.get("pro"),
                                credit.get("publisher"),
                            ),
                        )

        return get_release_package_by_id(release["id"])
    finally:
        conn.close()

def list_releases_for_creator(created_by_user_id: int):
    query = """
        SELECT *
        FROM release_submissions
        WHERE created_by_user_id = %s
        ORDER BY created_at DESC
    """
    return fetch_all(query, (created_by_user_id,))


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




def update_release_pdf_object_key(release_id: int, object_key: str):
    execute_write(
        """
        UPDATE release_submissions
        SET release_pdf_object_key = %s,
            updated_at = NOW()
        WHERE id = %s
        """,
        (object_key, release_id),
    )


def get_release_tracks(release_id: int):
    return fetch_all(
        """
        SELECT *
        FROM release_tracks
        WHERE release_submission_id = %s
        ORDER BY track_number ASC, created_at ASC
        """,
        (release_id,),
    )


def get_track_credits_for_release(release_id: int):
    return fetch_all(
        """
        SELECT
            rtc.*,
            rt.release_submission_id,
            rt.track_number,
            rt.track_title
        FROM release_track_credits rtc
        JOIN release_tracks rt ON rt.id = rtc.release_track_id
        WHERE rt.release_submission_id = %s
        ORDER BY rt.track_number ASC, rtc.credit_order ASC
        """,
        (release_id,),
    )


def get_release_package_by_id(release_id: int):
    release = fetch_one(
        """
        SELECT *
        FROM release_submissions
        WHERE id = %s
        LIMIT 1
        """,
        (release_id,),
    )

    if not release:
        return None

    release["artists"] = fetch_all(
        """
        SELECT *
        FROM release_submission_artists
        WHERE release_submission_id = %s
        ORDER BY artist_order ASC
        """,
        (release_id,),
    )

    release["tracks"] = get_release_tracks(release_id)
    release["track_credits"] = get_track_credits_for_release(release_id)

    return release


def list_saved_release_artists_for_creator(created_by_user_id: int):
    query = """
        SELECT DISTINCT ON (
            LOWER(COALESCE(rsa.email, '')),
            LOWER(COALESCE(rsa.display_name, ''))
        )
            rsa.id,
            rsa.display_name,
            rsa.email,
            rsa.first_name,
            rsa.last_name,
            rsa.ipi,
            rsa.pro,
            rsa.publisher,
            rsa.spotify_url,
            rsa.apple_music_url,
            rsa.youtube_url,
            rsa.soundcloud_url
        FROM release_submission_artists rsa
        JOIN release_submissions rs
            ON rs.id = rsa.release_submission_id
        WHERE rs.created_by_user_id = %s
          AND COALESCE(TRIM(rsa.display_name), '') <> ''
        ORDER BY
            LOWER(COALESCE(rsa.email, '')),
            LOWER(COALESCE(rsa.display_name, '')),
            rsa.id DESC
    """
    return fetch_all(query, (created_by_user_id,))