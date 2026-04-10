from config.db import (
    execute_returning_one,
    execute_write,
    fetch_all,
    fetch_one,
)


def list_active_artists():
    query = """
        SELECT
            id,
            user_id,
            artist_name,
            legal_name,
            bio,
            primary_genre,
            primary_instrument,
            vibe_tag,
            location,
            profile_image_url,
            spotify_url,
            youtube_url,
            soundcloud_url,
            toolost_artist_id,
            is_roster_active,
            created_at,
            updated_at
        FROM artist_profiles
        WHERE is_roster_active = TRUE
        ORDER BY artist_name ASC
    """
    return fetch_all(query)


def list_all_artists():
    query = """
        SELECT *
        FROM artist_profiles
        ORDER BY created_at DESC
    """
    return fetch_all(query)


def get_artist_by_id(artist_id: int):
    query = """
        SELECT *
        FROM artist_profiles
        WHERE id = %s
    """
    return fetch_one(query, (artist_id,))


def get_artist_by_user_id(user_id: int):
    query = """
        SELECT *
        FROM artist_profiles
        WHERE user_id = %s
    """
    return fetch_one(query, (user_id,))


def get_artist_by_name(artist_name: str):
    query = """
        SELECT *
        FROM artist_profiles
        WHERE LOWER(artist_name) = LOWER(%s)
    """
    return fetch_one(query, (artist_name,))


def create_artist_profile(
    artist_name: str,
    user_id: int | None = None,
    legal_name: str | None = None,
    bio: str | None = None,
    primary_genre: str | None = None,
    primary_instrument: str | None = None,
    vibe_tag: str | None = None,
    location: str | None = None,
    profile_image_url: str | None = None,
    spotify_url: str | None = None,
    youtube_url: str | None = None,
    soundcloud_url: str | None = None,
):
    query = """
        INSERT INTO artist_profiles (
            user_id,
            artist_name,
            legal_name,
            bio,
            primary_genre,
            primary_instrument,
            vibe_tag,
            location,
            profile_image_url,
            spotify_url,
            youtube_url,
            soundcloud_url
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING *
    """
    return execute_returning_one(
        query,
        (
            user_id,
            artist_name,
            legal_name,
            bio,
            primary_genre,
            primary_instrument,
            vibe_tag,
            location,
            profile_image_url,
            spotify_url,
            youtube_url,
            soundcloud_url,
        ),
    )


def update_artist_profile(
    artist_id: int,
    bio: str | None = None,
    primary_genre: str | None = None,
    primary_instrument: str | None = None,
    vibe_tag: str | None = None,
    location: str | None = None,
    profile_image_url: str | None = None,
    spotify_url: str | None = None,
    youtube_url: str | None = None,
    soundcloud_url: str | None = None,
):
    query = """
        UPDATE artist_profiles
        SET
            bio = %s,
            primary_genre = %s,
            primary_instrument = %s,
            vibe_tag = %s,
            location = %s,
            profile_image_url = %s,
            spotify_url = %s,
            youtube_url = %s,
            soundcloud_url = %s,
            updated_at = NOW()
        WHERE id = %s
    """
    execute_write(
        query,
        (
            bio,
            primary_genre,
            primary_instrument,
            vibe_tag,
            location,
            profile_image_url,
            spotify_url,
            youtube_url,
            soundcloud_url,
            artist_id,
        ),
    )