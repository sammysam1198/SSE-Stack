from config.db import fetch_all, fetch_one, execute_write


def list_contract_artists():
    query = """
        SELECT
            ap.id,
            ap.artist_name,
            ap.artist_page,
            CASE
                WHEN u.email IS NOT NULL THEN ARRAY[u.email]
                ELSE ARRAY[]::TEXT[]
            END AS emails
        FROM artist_profiles ap
        LEFT JOIN users u
            ON u.id = ap.user_id
        WHERE COALESCE(TRIM(ap.artist_name), '') <> ''
        ORDER BY LOWER(ap.artist_name) ASC
    """
    return fetch_all(query)


def create_contract(
    *,
    artist_profile_id,
    contract_type,
    title,
    status,
    template_object_key,
    unsigned_docx_object_key,
    unsigned_pdf_object_key,
    signed_object_key,
    body_text,
    notes,
    created_by_user_id,
):
    query = """
        INSERT INTO contracts (
            artist_profile_id,
            contract_type,
            title,
            status,
            template_object_key,
            unsigned_docx_object_key,
            unsigned_pdf_object_key,
            signed_object_key,
            body_text,
            notes,
            created_by_user_id
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING *
    """
    return fetch_one(query, (
        artist_profile_id,
        contract_type,
        title,
        status,
        template_object_key,
        unsigned_docx_object_key,
        unsigned_pdf_object_key,
        signed_object_key,
        body_text,
        notes,
        created_by_user_id,
    ))


def get_contract_by_id(contract_id: int):
    query = """
        SELECT
            c.*,
            ap.artist_name,
            ap.artist_page
        FROM contracts c
        JOIN artist_profiles ap
            ON ap.id = c.artist_profile_id
        WHERE c.id = %s
    """
    return fetch_one(query, (contract_id,))


def list_contracts():
    query = """
        SELECT
            c.*,
            ap.artist_name,
            ap.artist_page
        FROM contracts c
        JOIN artist_profiles ap
            ON ap.id = c.artist_profile_id
        ORDER BY c.created_at DESC
    """
    return fetch_all(query)


def list_contracts_for_artist_profile(artist_profile_id: int):
    query = """
        SELECT
            c.*,
            ap.artist_name,
            ap.artist_page
        FROM contracts c
        JOIN artist_profiles ap
            ON ap.id = c.artist_profile_id
        WHERE c.artist_profile_id = %s
        ORDER BY c.created_at DESC
    """
    return fetch_all(query, (artist_profile_id,))


def update_contract_status_and_files(
    *,
    contract_id,
    status=None,
    unsigned_docx_object_key=None,
    unsigned_pdf_object_key=None,
    signed_object_key=None,
    notes=None,
    sent=False,
    signed_uploaded=False,
    completed=False,
):
    fields = []
    values = []

    if status is not None:
        fields.append("status = %s")
        values.append(status)

    if unsigned_docx_object_key is not None:
        fields.append("unsigned_docx_object_key = %s")
        values.append(unsigned_docx_object_key)

    if unsigned_pdf_object_key is not None:
        fields.append("unsigned_pdf_object_key = %s")
        values.append(unsigned_pdf_object_key)

    if signed_object_key is not None:
        fields.append("signed_object_key = %s")
        values.append(signed_object_key)

    if notes is not None:
        fields.append("notes = %s")
        values.append(notes)

    if sent:
        fields.append("sent_at = NOW()")

    if signed_uploaded:
        fields.append("signed_uploaded_at = NOW()")

    if completed:
        fields.append("completed_at = NOW()")

    fields.append("updated_at = NOW()")

    query = f"""
        UPDATE contracts
        SET {", ".join(fields)}
        WHERE id = %s
    """
    values.append(contract_id)
    execute_write(query, tuple(values))


def add_contract_recipient(contract_id: int, email: str):
    query = """
        INSERT INTO contract_recipients (contract_id, email)
        VALUES (%s, %s)
    """
    execute_write(query, (contract_id, email))


def list_contract_recipients(contract_id: int):
    query = """
        SELECT id, contract_id, email, created_at
        FROM contract_recipients
        WHERE contract_id = %s
        ORDER BY id ASC
    """
    return fetch_all(query, (contract_id,))