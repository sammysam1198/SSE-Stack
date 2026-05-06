import os
from pathlib import Path
from typing import Optional

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

r2_bucket_name = os.getenv("R2_BUCKET_NAME")

def _get_r2_client():
    r2_account_id = os.getenv("R2_ACCOUNT_ID")
    r2_access_key = os.getenv("R2_ACCESS_KEY")
    r2_secret_key = os.getenv("R2_SECRET_KEY")
    r2_bucket_name = os.getenv("R2_BUCKET_NAME")
    r2_endpoint = os.getenv("R2_ENDPOINT")

    missing = [
        name for name, value in [
            ("R2_ACCOUNT_ID", r2_account_id),
            ("R2_ACCESS_KEY", r2_access_key),
            ("R2_SECRET_KEY", r2_secret_key),
            ("R2_BUCKET_NAME", r2_bucket_name),
            ("R2_ENDPOINT", r2_endpoint),
        ]
        if not value
    ]
    if missing:
        raise RuntimeError(f"Missing R2 environment variables: {', '.join(missing)}")

    client = boto3.client(
        "s3",
        endpoint_url=r2_endpoint,
        aws_access_key_id=r2_access_key,
        aws_secret_access_key=r2_secret_key,
        region_name="auto",
        config=Config(signature_version="s3v4"),
    )

    return client, r2_bucket_name


def upload_bytes_to_r2(
    *,
    data: bytes,
    object_key: str,
    content_type: str,
    content_disposition: Optional[str] = None,
) -> str:
    client, bucket_name = _get_r2_client()

    extra_args = {
        "ContentType": content_type,
    }
    if content_disposition:
        extra_args["ContentDisposition"] = content_disposition

    try:
        client.put_object(
            Bucket=bucket_name,
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

    client, bucket_name = _get_r2_client()

    extra_args = {
        "ContentType": content_type,
    }
    if content_disposition:
        extra_args["ContentDisposition"] = content_disposition

    try:
        client.upload_file(
            str(path),
            bucket_name,
            object_key,
            ExtraArgs=extra_args,
        )
    except (BotoCoreError, ClientError) as exc:
        raise RuntimeError(f"Failed to upload file to R2: {exc}") from exc

    return object_key


def download_bytes_from_r2(object_key: str) -> bytes:
    client, bucket_name = _get_r2_client()

    try:
        response = client.get_object(Bucket=bucket_name, Key=object_key)
        return response["Body"].read()
    except (BotoCoreError, ClientError) as exc:
        raise RuntimeError(f"Failed to download object from R2: {exc}") from exc


def delete_object_from_r2(object_key: str) -> None:
    client, bucket_name = _get_r2_client()

    try:
        client.delete_object(Bucket=bucket_name, Key=object_key)
    except (BotoCoreError, ClientError) as exc:
        raise RuntimeError(f"Failed to delete object from R2: {exc}") from exc


def list_object_keys_with_prefix(prefix: str) -> list[str]:
    client, bucket_name = _get_r2_client()

    keys: list[str] = []
    continuation_token = None

    try:
        while True:
            kwargs = {
                "Bucket": bucket_name,
                "Prefix": prefix,
                "MaxKeys": 1000,
            }

            if continuation_token:
                kwargs["ContinuationToken"] = continuation_token

            response = client.list_objects_v2(**kwargs)

            for item in response.get("Contents", []):
                key = item.get("Key")
                if key:
                    keys.append(key)

            if not response.get("IsTruncated"):
                break

            continuation_token = response.get("NextContinuationToken")

    except (BotoCoreError, ClientError) as exc:
        raise RuntimeError(f"Failed to list objects from R2: {exc}") from exc

    return keys

def create_presigned_put_url(
    *,
    object_key: str,
    content_type: str,
    expires_in: int = 900,
) -> str:
    client, bucket_name = _get_r2_client()

    return client.generate_presigned_url(
        ClientMethod="put_object",
        Params={
            "Bucket": bucket_name,
            "Key": object_key,
            "ContentType": content_type,
        },
        ExpiresIn=expires_in,
    )