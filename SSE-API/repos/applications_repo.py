
from config.db import (
    execute_returning_one,
    execute_write,
    fetch_all,
    fetch_one,
)


def create_application(
    *,
    first_name: str,
    last_name: str,
    birthday,
    artist_name: str,
    country: str,
    city: str,
    state_province: str,
    email: str,
    phone: str | None = None,
    current_label: str | None = None,
    publisher: str | None = None,
    current_distributor: str | None = None,
    total_releases: int | None = None,
    releases_last_12_months: int | None = None,
    spotify_monthly_listeners: int | None = None,
    streaming_link: str = "",
    instagram_link: str = "",
    youtube_link: str = "",
    bandcamp_link: str | None = None,
    website_link: str | None = None,
    fit: str | None = None,
    standout: str | None = None,
    strongest_skill_and_leverage: str | None = None,
    release_schedule: str | None = None,
    unreleased_music_ready: str | None = None,
    branding: str | None = None,
    goals_12_months: str | None = None,
    collaboration_openness: str | None = None,
    heard_about: str | None = None,
    bank_account_access: str | None = None,
    bank_account_explanation: str | None = None,
    agreement: str = "yes",
    created_user_id: int | None = None,
):
    query = """
        INSERT INTO artist_applications (
            first_name,
            last_name,
            birthday,
            artist_name,
            country,
            city,
            state_province,
            email,
            phone,
            current_label,
            publisher,
            current_distributor,
            total_releases,
            releases_last_12_months,
            spotify_monthly_listeners,
            streaming_link,
            instagram_link,
            youtube_link,
            bandcamp_link,
            website_link,
            fit,
            standout,
            strongest_skill_and_leverage,
            release_schedule,
            unreleased_music_ready,
            branding,
            goals_12_months,
            collaboration_openness,
            heard_about,
            bank_account_access,
            bank_account_explanation,
            agreement,
            created_user_id
        )
        VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s
        )
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
    return execute_returning_one(
        query,
        (
            first_name,
            last_name,
            birthday,
            artist_name,
            country,
            city,
            state_province,
            email,
            phone,
            current_label,
            publisher,
            current_distributor,
            total_releases,
            releases_last_12_months,
            spotify_monthly_listeners,
            streaming_link,
            instagram_link,
            youtube_link,
            bandcamp_link,
            website_link,
            fit,
            standout,
            strongest_skill_and_leverage,
            release_schedule,
            unreleased_music_ready,
            branding,
            goals_12_months,
            collaboration_openness,
            heard_about,
            bank_account_access,
            bank_account_explanation,
            agreement,
            created_user_id,
        ),
    )



def list_applications():
    query = """
        SELECT
            id,
            first_name,
            last_name,
            birthday,
            artist_name,
            country,
            city,
            state_province,
            email,
            phone,
            current_label,
            publisher,
            current_distributor,
            total_releases,
            releases_last_12_months,
            spotify_monthly_listeners,
            streaming_link,
            instagram_link,
            youtube_link,
            bandcamp_link,
            website_link,
            fit,
            standout,
            strongest_skill_and_leverage,
            release_schedule,
            unreleased_music_ready,
            branding,
            goals_12_months,
            collaboration_openness,
            heard_about,
            bank_account_access,
            bank_account_explanation,
            agreement,
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

def update_application_pdf_path(application_id: int, application_pdf_path: str):
    query = """
            UPDATE artist_applications
            SET
                application_pdf_path = %s,
                updated_at = NOW()
            WHERE id = %s
        """
    execute_write(query, (application_pdf_path, application_id))