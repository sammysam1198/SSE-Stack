from config.db import execute_returning_one, fetch_all, fetch_one


def list_active_artists():
    query = """
        SELECT *
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


def create_artist_profile_for_user(user_id: int, artist_name: str | None = None):
    query = """
        INSERT INTO artist_profiles (
            user_id,
            artist_name,
            legal_name,
            tagline,
            bio,
            primary_genre,
            primary_instrument,
            primary_vibe,
            publisher,
            location,
            profile_image_url,
            spotify_url,
            youtube_url,
            soundcloud_url,
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
            '',
            '',
            TRUE
        )
        RETURNING *
    """
    return execute_returning_one(query, (user_id, artist_name or "Untitled Artist"))


def update_artist_profile_by_user_id(
    user_id: int,
    artist_name: str,
    tagline: str,
    bio: str,
    primary_genre: str,
    primary_instrument: str,
    primary_vibe: str,
    publisher: str,
    location: str,
    profile_image_url: str,
    spotify_url: str,
    youtube_url: str,
    soundcloud_url: str,
):
    query = """
        UPDATE artist_profiles
        SET
            artist_name = %s,
            tagline = %s,
            bio = %s,
            primary_genre = %s,
            primary_instrument = %s,
            primary_vibe = %s,
            publisher = %s,
            location = %s,
            profile_image_url = %s,
            spotify_url = %s,
            youtube_url = %s,
            soundcloud_url = %s,
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
            primary_genre,
            primary_instrument,
            primary_vibe,
            publisher,
            location,
            profile_image_url,
            spotify_url,
            youtube_url,
            soundcloud_url,
            user_id,
        ),
    )


def get_artist_by_slug(artist_page: str):
    query = """
        SELECT
            id,
            user_id,
            artist_name,
            artist_page,
            location,
            bio,
            profile_image_url,
            spotify_url,
            youtube_url,
            instagram_url,
            soundcloud_url,
            apple_music_url,
            primary_genre,
            primary_instrument,
            primary_vibe,
            updated_at
        FROM artist_profiles
        WHERE artist_page = %s
        LIMIT 1
    """
    return execute_returning_one(query, (artist_page,))