import os
import traceback
from io import BytesIO
from utils.auth_utils import get_current_user
from flask import Blueprint, jsonify, request, send_file
from utils.mail_utils import send_contract_ready_email
from repos.contracts_repo import (
    add_contract_recipient,
    create_contract,
    get_contract_by_id,
    list_contract_artists,
    list_contract_recipients,
    list_contracts,
    update_contract_status_and_files,
)
from utils.contract_utils import (
    build_contract_object_keys,
    build_docx_bytes,
    build_pdf_bytes,
)
from utils.r2_utils import (
    download_bytes_from_r2,
    upload_bytes_to_r2,
)

contracts_bp = Blueprint("contracts", __name__)
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "https://www.spacedoutstudiosent.com")


def _require_logged_in_user():
    user = get_current_user()
    if not user:
        return None, (jsonify({"error": "Unauthorized."}), 401)
    return user, None


def _require_admin_or_dev():
    user, error = _require_logged_in_user()
    if error:
        return None, error

    if user["role"] not in {"admin", "developer"}:
        return None, (jsonify({"error": "Forbidden."}), 403)

    return user, None


@contracts_bp.get("/artists")
def get_contract_artists():
    user, error = _require_admin_or_dev()
    if error:
        return error

    try:
        artists = list_contract_artists()
        return jsonify({"artists": artists}), 200
    except Exception as exc:
        print("[contracts/artists] failed:", repr(exc))
        traceback.print_exc()
        return jsonify({"error": f"Failed to load contract artists: {exc}"}), 500

@contracts_bp.get("")
def get_contracts():
    user, error = _require_admin_or_dev()
    if error:
        return error

    contracts = list_contracts()
    return jsonify({"contracts": contracts}), 200


@contracts_bp.get("/<int:contract_id>")
def get_contract(contract_id: int):
    user, error = _require_logged_in_user()
    if error:
        return error

    contract = get_contract_by_id(contract_id)
    if not contract:
        return jsonify({"error": "Contract not found."}), 404

    if user["role"] not in {"admin", "developer"}:
        return jsonify({"error": "Forbidden."}), 403

    recipients = list_contract_recipients(contract_id)
    return jsonify({
        "contract": contract,
        "recipients": recipients,
    }), 200


@contracts_bp.post("")
def create_new_contract():
    user, error = _require_admin_or_dev()
    if error:
        return error

    try:
        data = request.get_json(silent=True) or {}

        artist_profile_id = data.get("artist_profile_id")
        contract_type = (data.get("contract_type") or "").strip().lower()
        artist_name = (data.get("artist_name") or "").strip()
        body_text = (data.get("body_text") or "").strip()
        notes = (data.get("notes") or "").strip()
        send_now = bool(data.get("send_now"))
        recipient_emails = data.get("recipient_emails") or []

        if not artist_profile_id:
            return jsonify({"error": "artist_profile_id is required."}), 400

        if contract_type not in {"publishing", "distribution"}:
            return jsonify({"error": "contract_type must be publishing or distribution."}), 400

        if not artist_name:
            return jsonify({"error": "artist_name is required."}), 400

        if not body_text:
            return jsonify({"error": "Contract body is required."}), 400

        title = f"{artist_name} {contract_type.title()} Contract"

        print("[contracts] building object keys")
        object_keys = build_contract_object_keys(artist_name, contract_type)

        print("[contracts] building docx bytes")
        docx_bytes = build_docx_bytes(title, body_text)

        print("[contracts] building pdf bytes")
        pdf_bytes = build_pdf_bytes(title, body_text)

        print("[contracts] uploading docx to r2:", object_keys["docx"])
        upload_bytes_to_r2(
            data=docx_bytes,
            object_key=object_keys["docx"],
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            content_disposition=f'attachment; filename="{object_keys["docx"].split("/")[-1]}"',
        )

        print("[contracts] uploading pdf to r2:", object_keys["pdf"])
        upload_bytes_to_r2(
            data=pdf_bytes,
            object_key=object_keys["pdf"],
            content_type="application/pdf",
            content_disposition=f'attachment; filename="{object_keys["pdf"].split("/")[-1]}"',
        )

        print("[contracts] creating contract row")
        contract = create_contract(
            artist_profile_id=artist_profile_id,
            contract_type=contract_type,
            title=title,
            status="sent" if send_now else "draft",
            template_object_key=None,
            unsigned_docx_object_key=object_keys["docx"],
            unsigned_pdf_object_key=object_keys["pdf"],
            signed_object_key=object_keys["signed"],
            body_text=body_text,
            notes=notes or None,
            created_by_user_id=user["user_id"],
        )

        cleaned_recipient_emails = []
        for email in recipient_emails:
            cleaned = str(email or "").strip()
            if cleaned:
                cleaned_recipient_emails.append(cleaned)
                add_contract_recipient(contract["id"], cleaned)

        if send_now:
            print("[contracts] marking sent")
            update_contract_status_and_files(
                contract_id=contract["id"],
                status="sent",
                sent=True,
            )

            contract_view_url = f"{FRONTEND_ORIGIN}/contracts/view?id={contract['id']}"
            print("[contracts] contract_view_url:", contract_view_url)
            print("[contracts] recipients:", cleaned_recipient_emails)

            for email in cleaned_recipient_emails:
                print("[contracts] sending email to:", email)
                send_contract_ready_email(
                    to_email=email,
                    artist_name=artist_name,
                    contract_type=contract_type,
                    contract_view_url=contract_view_url,
                )

        return jsonify({
            "message": "Contract created successfully.",
            "contract": contract,
            "object_keys": object_keys,
        }), 201

    except Exception as exc:
        print("[contracts] create_new_contract failed:", repr(exc))
        traceback.print_exc()
        return jsonify({
            "error": "Failed to create/send contract.",
            "details": str(exc),
        }), 500

@contracts_bp.post("/<int:contract_id>/upload-signed")
def upload_signed_contract(contract_id: int):
    user, error = _require_logged_in_user()
    if error:
        return error

    contract = get_contract_by_id(contract_id)
    if not contract:
        return jsonify({"error": "Contract not found."}), 404

    signed_file = request.files.get("signed_contract")
    if not signed_file:
        return jsonify({"error": "signed_contract file is required."}), 400

    file_bytes = signed_file.read()
    if not file_bytes:
        return jsonify({"error": "Signed contract file is empty."}), 400

    signed_key = contract["signed_object_key"]
    if not signed_key:
        unsigned_pdf_key = contract.get("unsigned_pdf_object_key") or ""
        if unsigned_pdf_key:
            signed_key = unsigned_pdf_key.replace("/unsigned/", "/signed/").replace(".pdf", "_signed.pdf")
        else:
            return jsonify({"error": "Could not determine signed contract path."}), 500

    upload_bytes_to_r2(
        data=file_bytes,
        object_key=signed_key,
        content_type="application/pdf",
        content_disposition=f'attachment; filename="{signed_key.split("/")[-1]}"',
    )

    update_contract_status_and_files(
        contract_id=contract_id,
        status="signed_uploaded",
        signed_object_key=signed_key,
        signed_uploaded=True,
    )

    return jsonify({
        "message": "Signed contract uploaded successfully.",
        "signed_object_key": signed_key,
    }), 200


@contracts_bp.get("/<int:contract_id>/download/unsigned-docx")
def download_unsigned_docx(contract_id: int):
    user, error = _require_logged_in_user()
    if error:
        return error

    contract = get_contract_by_id(contract_id)
    if not contract or not contract.get("unsigned_docx_object_key"):
        return jsonify({"error": "Unsigned DOCX not found."}), 404

    file_bytes = download_bytes_from_r2(contract["unsigned_docx_object_key"])
    filename = contract["unsigned_docx_object_key"].split("/")[-1]

    return send_file(
        BytesIO(file_bytes),
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


@contracts_bp.get("/<int:contract_id>/download/unsigned-pdf")
def download_unsigned_pdf(contract_id: int):
    user, error = _require_logged_in_user()
    if error:
        return error

    contract = get_contract_by_id(contract_id)
    if not contract or not contract.get("unsigned_pdf_object_key"):
        return jsonify({"error": "Unsigned PDF not found."}), 404

    file_bytes = download_bytes_from_r2(contract["unsigned_pdf_object_key"])
    filename = contract["unsigned_pdf_object_key"].split("/")[-1]

    return send_file(
        BytesIO(file_bytes),
        as_attachment=True,
        download_name=filename,
        mimetype="application/pdf",
    )


@contracts_bp.get("/<int:contract_id>/download/signed")
def download_signed_pdf(contract_id: int):
    user, error = _require_logged_in_user()
    if error:
        return error

    contract = get_contract_by_id(contract_id)
    if not contract or not contract.get("signed_object_key"):
        return jsonify({"error": "Signed contract not found."}), 404

    file_bytes = download_bytes_from_r2(contract["signed_object_key"])
    filename = contract["signed_object_key"].split("/")[-1]

    return send_file(
        BytesIO(file_bytes),
        as_attachment=True,
        download_name=filename,
        mimetype="application/pdf",
    )

