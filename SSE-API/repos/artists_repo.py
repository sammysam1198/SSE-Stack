from config.db import (
    execute_returning_one,
    fetch_all,
    fetch_one,
)


def list_active_artists():
    query = """
        SELECT
            id,
            user_id,
            artist_name,
            tagline,
            bio,
            hero_image_url,
            portrait_image_url,
            tag_1,
            tag_2,
            tag_3,
            spotify_url,
            youtube_url,
            instagram_url,
            slug,
            is_roster_active,
            created_at,
            updated_at
        FROM artist_profiles
        WHERE is_roster_active = TRUE
        ORDER BY artist_name ASC
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


def get_artist_by_slug(slug: str):
    query = """
        SELECT *
        FROM artist_profiles
        WHERE slug = %s
    """
    return fetch_one(query, (slug,))


def create_artist_profile_for_user(user_id: int, artist_name: str | None = None):
    query = """
        INSERT INTO artist_profiles (
            user_id,
            artist_name,
            tagline,
            bio,
            hero_image_url,
            portrait_image_url,
            tag_1,
            tag_2,
            tag_3,
            spotify_url,
            youtube_url,
            instagram_url,
            is_roster_active
        )
        VALUES (
            %s,
            %s,
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            TRUE
        )
        RETURNING *
    """
    return execute_returning_one(
        query,
        (
            user_id,
            artist_name or "Untitled Artist",
        ),
    )


def update_artist_profile_by_user_id(
    user_id: int,
    artist_name: str,
    tagline: str,
    bio: str,
    hero_image_url: str,
    portrait_image_url: str,
    tag_1: str,
    tag_2: str,
    tag_3: str,
    spotify_url: str,
    youtube_url: str,
    instagram_url: str,
):
    query = """
        UPDATE artist_profiles
        SET
            artist_name = %s,
            tagline = %s,
            bio = %s,
            hero_image_url = %s,
            portrait_image_url = %s,
            tag_1 = %s,
            tag_2 = %s,
            tag_3 = %s,
            spotify_url = %s,
            youtube_url = %s,
            instagram_url = %s,
            updated_at = NOW()
        WHERE user_id = %s
        RETURNING *
    """
    return execute_returning_one(
        query,
        (
            artist_name,
            tagline,
            bio,
            hero_image_url,
            portrait_image_url,
            tag_1,
            tag_2,
            tag_3,
            spotify_url,
            youtube_url,
            instagram_url,
            user_id,
        ),
    )