from flask import request, session


def get_request_ip() -> str | None:
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.remote_addr


def get_user_agent() -> str:
    return request.headers.get("User-Agent", "")


def is_authenticated() -> bool:
    return bool(session.get("user_id"))


def get_current_user_id() -> int | None:
    return session.get("user_id")


def get_current_role() -> str | None:
    return session.get("role")


def require_roles(*allowed_roles: str) -> bool:
    current_role = get_current_role()
    return current_role in allowed_roles


def build_security_event_metadata(extra: dict | None = None) -> dict:
    payload = {
        "ip_address": get_request_ip(),
        "user_agent": get_user_agent(),
    }
    if extra:
        payload.update(extra)
    return payload