from typing import Any

from config.db import execute_write


ARTIST_PROFILE_COLUMNS = """
    id,
    user_id,
    artist_name,
    bio,
    primary_genre,
    primary_instrument,
    primary_vibe,
    location,
    spotify_url,
    soundcloud_url,
    is_roster_active,
    created_at,
    updated_at,
    tagline,
    publisher,
    first_name,
    last_name,
    artist_page,
    dashboard_banner_key,
    artist_logo_key,
    profile_portrait_key,
    apple_music_url,
    youtube_music_url,
    youtube_channel_url,
    tidal_url,
    threads_url,
    instagram_url,
    bandcamp_url,
    tiktok_url,
    twitter_url,
    deezer_url,
    beatport_url,
    amazon_music_url,
    facebook_url,
    birthday,
    city,
    state,
    country,
    ipi,
    pro
"""


def get_artist_profile_by_user_id(user_id: int):
    query = f"""
        SELECT {ARTIST_PROFILE_COLUMNS}
        FROM artist_profiles
        WHERE user_id = %s
        LIMIT 1
    """
    rows = execute_write(query, (user_id,))
    return rows[0] if rows else None


def get_artist_profile_by_id(artist_profile_id: int):
    query = f"""
        SELECT {ARTIST_PROFILE_COLUMNS}
        FROM artist_profiles
        WHERE id = %s
        LIMIT 1
    """
    rows = execute_write(query, (artist_profile_id,))
    return rows[0] if rows else None


def get_artist_profile_by_slug(artist_page: str):
    query = f"""
        SELECT {ARTIST_PROFILE_COLUMNS}
        FROM artist_profiles
        WHERE LOWER(artist_page) = LOWER(%s)
        LIMIT 1
    """
    rows = execute_write(query, (artist_page,))
    return rows[0] if rows else None


def create_artist_profile_for_user(
    *,
    user_id: int,
    artist_name: str,
    artist_page: str,
    first_name: str = "",
    last_name: str = "",
):
    query = f"""
        INSERT INTO artist_profiles (
            user_id,
            artist_name,
            artist_page,
            first_name,
            last_name
        )
        VALUES (%s, %s, %s, %s, %s)
        RETURNING {ARTIST_PROFILE_COLUMNS}
    """
    rows = execute_write(
        query,
        (
            user_id,
            artist_name,
            artist_page,
            first_name,
            last_name,
        ),
    )
    return rows[0] if rows else None


def update_artist_profile_by_user_id(user_id: int, updates: dict[str, Any]):
    if not updates:
        return get_artist_profile_by_user_id(user_id)

    allowed_fields = {
        "artist_name",
        "bio",
        "primary_genre",
        "primary_instrument",
        "primary_vibe",
        "location",
        "spotify_url",
        "soundcloud_url",
        "tagline",
        "publisher",
        "first_name",
        "last_name",
        "artist_page",
        "dashboard_banner_key",
        "artist_logo_key",
        "profile_portrait_key",
        "apple_music_url",
        "youtube_music_url",
        "youtube_channel_url",
        "tidal_url",
        "threads_url",
        "instagram_url",
        "bandcamp_url",
        "tiktok_url",
        "twitter_url",
        "deezer_url",
        "beatport_url",
        "amazon_music_url",
        "facebook_url",
        "birthday",
        "city",
        "state",
        "country",
        "ipi",
        "pro",
    }

    filtered = {k: v for k, v in updates.items() if k in allowed_fields}
    if not filtered:
        return get_artist_profile_by_user_id(user_id)

    set_clauses = []
    values = []

    for field, value in filtered.items():
        set_clauses.append(f"{field} = %s")
        values.append(value)

    set_clauses.append("updated_at = NOW()")
    values.append(user_id)

    query = f"""
        UPDATE artist_profiles
        SET {", ".join(set_clauses)}
        WHERE user_id = %s
        RETURNING {ARTIST_PROFILE_COLUMNS}
    """
    rows = execute_write(query, tuple(values))
    return rows[0] if rows else None


def assign_artist_profile_to_user(artist_profile_id: int, user_id: int):
    query = f"""
        UPDATE artist_profiles
        SET
            user_id = %s,
            updated_at = NOW()
        WHERE id = %s
        RETURNING {ARTIST_PROFILE_COLUMNS}
    """
    rows = execute_write(query, (user_id, artist_profile_id))
    return rows[0] if rows else None


def list_artist_profiles():
    query = f"""
        SELECT {ARTIST_PROFILE_COLUMNS}
        FROM artist_profiles
        ORDER BY artist_name ASC
    """
    return execute_write(query)