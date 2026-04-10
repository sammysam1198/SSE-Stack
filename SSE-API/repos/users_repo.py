from config.db import (
    execute_returning_one,
    execute_write,
    fetch_all,
    fetch_one,
)


def get_user_by_id(user_id: int):
    query = """
        SELECT
            id,
            email,
            username,
            password_hash,
            role,
            is_active,
            is_locked,
            lock_reason,
            failed_login_count,
            last_login_at,
            last_login_ip,
            email_verified,
            created_at,
            updated_at
        FROM users
        WHERE id = %s
    """
    return fetch_one(query, (user_id,))


def get_user_by_email(email: str):
    query = """
        SELECT
            id,
            email,
            username,
            password_hash,
            role,
            is_active,
            is_locked,
            lock_reason,
            failed_login_count,
            last_login_at,
            last_login_ip,
            email_verified,
            created_at,
            updated_at
        FROM users
        WHERE LOWER(email) = LOWER(%s)
    """
    return fetch_one(query, (email,))


def list_users():
    query = """
        SELECT
            id,
            email,
            username,
            role,
            is_active,
            is_locked,
            lock_reason,
            failed_login_count,
            last_login_at,
            last_login_ip,
            email_verified,
            created_at,
            updated_at
        FROM users
        ORDER BY created_at DESC
    """
    return fetch_all(query)


def create_user(
    email: str,
    password_hash: str,
    role: str,
    username: str | None = None,
    email_verified: bool = False,
):
    query = """
        INSERT INTO users (
            email,
            username,
            password_hash,
            role,
            email_verified
        )
        VALUES (%s, %s, %s, %s, %s)
        RETURNING
            id,
            email,
            username,
            role,
            is_active,
            is_locked,
            email_verified,
            created_at,
            updated_at
    """
    return execute_returning_one(
        query,
        (email, username, password_hash, role, email_verified),
    )


def update_user_password(user_id: int, password_hash: str):
    query = """
        UPDATE users
        SET
            password_hash = %s,
            updated_at = NOW(),
            failed_login_count = 0
        WHERE id = %s
    """
    execute_write(query, (password_hash, user_id))


def update_user_email(user_id: int, new_email: str):
    query = """
        UPDATE users
        SET
            email = %s,
            updated_at = NOW(),
            email_verified = FALSE
        WHERE id = %s
    """
    execute_write(query, (new_email, user_id))


def mark_email_verified(user_id: int):
    query = """
        UPDATE users
        SET
            email_verified = TRUE,
            updated_at = NOW()
        WHERE id = %s
    """
    execute_write(query, (user_id,))


def increment_failed_login_count(user_id: int):
    query = """
        UPDATE users
        SET
            failed_login_count = failed_login_count + 1,
            updated_at = NOW()
        WHERE id = %s
    """
    execute_write(query, (user_id,))


def reset_failed_login_count(user_id: int):
    query = """
        UPDATE users
        SET
            failed_login_count = 0,
            updated_at = NOW()
        WHERE id = %s
    """
    execute_write(query, (user_id,))


def update_last_login(user_id: int, ip_address: str | None):
    query = """
        UPDATE users
        SET
            last_login_at = NOW(),
            last_login_ip = %s,
            failed_login_count = 0,
            updated_at = NOW()
        WHERE id = %s
    """
    execute_write(query, (ip_address, user_id))


def lock_user(user_id: int, lock_reason: str | None = None):
    query = """
        UPDATE users
        SET
            is_locked = TRUE,
            lock_reason = %s,
            updated_at = NOW()
        WHERE id = %s
    """
    execute_write(query, (lock_reason, user_id))


def unlock_user(user_id: int):
    query = """
        UPDATE users
        SET
            is_locked = FALSE,
            lock_reason = NULL,
            failed_login_count = 0,
            updated_at = NOW()
        WHERE id = %s
    """
    execute_write(query, (user_id,))