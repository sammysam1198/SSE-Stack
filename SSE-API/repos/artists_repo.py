from typing import Any
from config.db import fetch_all, fetch_one, execute_returning_one


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
    website_url,
    birthday,
    city,
    state,
    country,
    ipi,
    pro,
    spotify_embed,
    featured_video_embed,
    featured_video_name,
    video2_embed,
    video2_name,
    video3_embed,
    video3_name,
    genre2,
    genre3,
    role2,
    role3
"""


def get_artist_profile_by_user_id(user_id: int):
    query = f"""
        SELECT {ARTIST_PROFILE_COLUMNS}
        FROM artist_profiles
        WHERE user_id = %s
        LIMIT 1
    """
    return fetch_one(query, (user_id,))


def get_artist_profile_by_id(artist_profile_id: int):
    query = f"""
        SELECT {ARTIST_PROFILE_COLUMNS}
        FROM artist_profiles
        WHERE id = %s
        LIMIT 1
    """
    return fetch_one(query, (artist_profile_id,))


def get_artist_profile_by_slug(artist_page: str):
    query = f"""
        SELECT {ARTIST_PROFILE_COLUMNS}
        FROM artist_profiles
        WHERE LOWER(artist_page) = LOWER(%s)
        LIMIT 1
    """
    return fetch_one(query, (artist_page,))


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
    return execute_returning_one(
        query,
        (
            user_id,
            artist_name,
            artist_page,
            first_name,
            last_name,
        ),
    )


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
        "website_url",
        "birthday",
        "city",
        "state",
        "country",
        "ipi",
        "pro",
        "spotify_embed",
        "featured_video_embed",
        "featured_video_name",
        "video2_embed",
        "video2_name",
        "video3_embed",
        "video3_name",
        "genre2",
        "genre3",
        "role2",
        "role3",
    }

    filtered = {k: v for k, v in updates.items() if k in allowed_fields}
    if not filtered:
        return get_artist_profile_by_user_id(user_id)

    set_clauses = []
    values: list[Any] = []

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
    return execute_returning_one(query, tuple(values))


def assign_artist_profile_to_user(artist_profile_id: int, user_id: int):
    query = f"""
        UPDATE artist_profiles
        SET
            user_id = %s,
            updated_at = NOW()
        WHERE id = %s
        RETURNING {ARTIST_PROFILE_COLUMNS}
    """
    return execute_returning_one(query, (user_id, artist_profile_id))


def list_artist_profiles():
    query = f"""
        SELECT {ARTIST_PROFILE_COLUMNS}
        FROM artist_profiles
        ORDER BY artist_name ASC
    """
    return fetch_all(query)