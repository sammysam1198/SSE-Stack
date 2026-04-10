import os
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt


def hash_password(password: str) -> str:
    if not password or len(password) < 8:
        raise ValueError("Password must be at least 8 characters long.")

    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    if not password or not password_hash:
        return False

    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8")
        )
    except ValueError:
        return False


def generate_urlsafe_token(length_bytes: int = 32) -> str:
    return secrets.token_urlsafe(length_bytes)


def hash_token(token: str) -> str:
    token_bytes = token.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(token_bytes, salt)
    return hashed.decode("utf-8")


def verify_token(token: str, token_hash: str) -> bool:
    if not token or not token_hash:
        return False

    try:
        return bcrypt.checkpw(
            token.encode("utf-8"),
            token_hash.encode("utf-8")
        )
    except ValueError:
        return False


def token_expiry(minutes: int = 30) -> datetime:
    return datetime.now(timezone.utc) + timedelta(minutes=minutes)


def session_user_payload(user_row: dict) -> dict:
    return {
        "user_id": user_row["id"],
        "role": user_row["role"],
        "email": user_row["email"],
    }


def get_reset_link(token: str) -> str:
    frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://127.0.0.1:5500")
    return f"{frontend_origin}/reset-password?token={token}"


def get_email_change_link(token: str) -> str:
    frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://127.0.0.1:5500")
    return f"{frontend_origin}/confirm-email-change?token={token}"