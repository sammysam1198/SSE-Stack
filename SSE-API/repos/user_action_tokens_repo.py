from config.db import execute_write, fetch_one


def create_user_action_token(
    user_id: int,
    email: str,
    token_hash: str,
    token_type: str,
    expires_at,
):
    query = """
        INSERT INTO user_action_tokens (
            user_id,
            email,
            token_hash,
            token_type,
            expires_at
        )
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id, user_id, email, token_type, expires_at, used_at, created_at
    """
    return fetch_one(query, (user_id, email, token_hash, token_type, expires_at))


def get_valid_user_action_token(token_hash: str, token_type: str):
    query = """
        SELECT *
        FROM user_action_tokens
        WHERE token_hash = %s
          AND token_type = %s
          AND used_at IS NULL
          AND expires_at > NOW()
        ORDER BY created_at DESC
        LIMIT 1
    """
    return fetch_one(query, (token_hash, token_type))


def mark_user_action_token_used(token_id: int):
    query = """
        UPDATE user_action_tokens
        SET used_at = NOW()
        WHERE id = %s
    """
    execute_write(query, (token_id,))


def invalidate_user_tokens(user_id: int, token_type: str):
    query = """
        UPDATE user_action_tokens
        SET used_at = NOW()
        WHERE user_id = %s
          AND token_type = %s
          AND used_at IS NULL
    """
    execute_write(query, (user_id, token_type))