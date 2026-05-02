from config.db import fetch_all, fetch_one, execute_returning_one


def create_contact_request(
    *,
    requester_name,
    requester_email,
    issue_type,
    department_tag,
    subject,
    message,
    created_user_id=None,
):
    query = """
        INSERT INTO contact_requests (
            requester_name,
            requester_email,
            issue_type,
            department_tag,
            subject,
            message,
            status,
            created_user_id
        )
        VALUES (%s, %s, %s, %s, %s, %s, 'open', %s)
        RETURNING *
    """
    return execute_returning_one(query, (
        requester_name,
        requester_email,
        issue_type,
        department_tag,
        subject,
        message,
        created_user_id,
    ))


def list_contact_requests():
    query = """
        SELECT *
        FROM contact_requests
        ORDER BY created_at DESC
    """
    return fetch_all(query)


def get_contact_request_by_id(request_id: int):
    query = """
        SELECT *
        FROM contact_requests
        WHERE id = %s
    """
    return fetch_one(query, (request_id,))


def update_contact_request_status(request_id: int, status: str):
    query = """
        UPDATE contact_requests
        SET status = %s,
            updated_at = NOW()
        WHERE id = %s
        RETURNING *
    """
    return execute_returning_one(query, (status, request_id))