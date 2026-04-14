import os
from pathlib import Path
from typing import Optional

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError


R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
R2_ACCESS_KEY = os.getenv("R2_ACCESS_KEY")
R2_SECRET_KEY = os.getenv("R2_SECRET_KEY")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME")
R2_ENDPOINT = os.getenv("R2_ENDPOINT")


def _get_r2_client():
    missing = [
        name for name, value in [
            ("R2_ACCOUNT_ID", R2_ACCOUNT_ID),
            ("R2_ACCESS_KEY", R2_ACCESS_KEY),
            ("R2_SECRET_KEY", R2_SECRET_KEY),
            ("R2_BUCKET_NAME", R2_BUCKET_NAME),
            ("R2_ENDPOINT", R2_ENDPOINT),
        ]
        if not value
    ]
    if missing:
        raise RuntimeError(f"Missing R2 environment variables: {', '.join(missing)}")

    return boto3.client(
        "s3",
        endpoint_url=R2_ENDPOINT,
        aws_access_key_id=R2_ACCESS_KEY,
        aws_secret_access_key=R2_SECRET_KEY,
        region_name="auto",
        config=Config(signature_version="s3v4"),
    )


def upload_bytes_to_r2(
    *,
    data: bytes,
    object_key: str,
    content_type: str,
    content_disposition: Optional[str] = None,
) -> str:
    client = _get_r2_client()

    extra_args = {
        "ContentType": content_type,
    }
    if content_disposition:
        extra_args["ContentDisposition"] = content_disposition

    try:
        client.put_object(
            Bucket=R2_BUCKET_NAME,
            Key=object_key,
            Body=data,
            **extra_args,
        )
    except (BotoCoreError, ClientError) as exc:
        raise RuntimeError(f"Failed to upload object to R2: {exc}") from exc

    return object_key


def upload_file_to_r2(
    *,
    local_path: str | Path,
    object_key: str,
    content_type: str,
    content_disposition: Optional[str] = None,
) -> str:
    path = Path(local_path)
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Local file not found: {path}")

    client = _get_r2_client()

    extra_args = {
        "ContentType": content_type,
    }
    if content_disposition:
        extra_args["ContentDisposition"] = content_disposition

    try:
        client.upload_file(
            str(path),
            R2_BUCKET_NAME,
            object_key,
            ExtraArgs=extra_args,
        )
    except (BotoCoreError, ClientError) as exc:
        raise RuntimeError(f"Failed to upload file to R2: {exc}") from exc

    return object_key


def download_bytes_from_r2(object_key: str) -> bytes:
    client = _get_r2_client()

    try:
        response = client.get_object(Bucket=R2_BUCKET_NAME, Key=object_key)
        return response["Body"].read()
    except (BotoCoreError, ClientError) as exc:
        raise RuntimeError(f"Failed to download object from R2: {exc}") from exc


def delete_object_from_r2(object_key: str) -> None:
    client = _get_r2_client()

    try:
        client.delete_object(Bucket=R2_BUCKET_NAME, Key=object_key)
    except (BotoCoreError, ClientError) as exc:
        raise RuntimeError(f"Failed to delete object from R2: {exc}") from exc