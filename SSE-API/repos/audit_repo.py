from config.db import fetch_all, execute_returning_one


def create_audit_log(
    *,
    actor_user_id=None,
    actor_role=None,
    event_type,
    entity_type=None,
    entity_id=None,
    message=None,
    metadata=None,
    ip_address=None,
    user_agent=None,
):
    query = """
        INSERT INTO audit_logs (
            actor_user_id,
            actor_role,
            event_type,
            entity_type,
            entity_id,
            message,
            metadata,
            ip_address,
            user_agent
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s)
        RETURNING *
    """
    return execute_returning_one(query, (
        actor_user_id,
        actor_role,
        event_type,
        entity_type,
        entity_id,
        message,
        metadata or "{}",
        ip_address,
        user_agent,
    ))


def list_audit_logs(limit=100):
    query = """
        SELECT *
        FROM audit_logs
        ORDER BY created_at DESC
        LIMIT %s
    """
    return fetch_all(query, (limit,))