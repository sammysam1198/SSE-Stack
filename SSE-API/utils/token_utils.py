import hashlib
import secrets
from datetime import datetime, timedelta, timezone


def generate_raw_token() -> str:
    return secrets.token_urlsafe(32)


def hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def expiry_from_now(minutes: int) -> datetime:
    return utc_now() + timedelta(minutes=minutes)