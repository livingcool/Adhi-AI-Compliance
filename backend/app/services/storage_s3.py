"""
Amazon S3 Storage Service
Replaces local disk storage (STORAGE_PROVIDER=local → s3).
Drop-in compatible with the existing file service interface.
"""
import logging
import mimetypes
from pathlib import Path
from typing import Optional, BinaryIO
from io import BytesIO

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from app.config import get_settings

logger = logging.getLogger("adhi.storage.s3")


def _make_s3_client():
    settings = get_settings()
    kwargs = {
        "service_name": "s3",
        "region_name": settings.AWS_REGION,
        "config": Config(signature_version="s3v4"),
    }
    if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
        kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
        kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY
    return boto3.client(**kwargs)


class S3StorageService:
    """
    Handles file uploads, downloads, deletions, and pre-signed URL generation
    on Amazon S3. Mirrors the interface of the local storage service.
    """

    def __init__(self):
        settings = get_settings()
        if not settings.AWS_S3_BUCKET:
            raise ValueError("AWS_S3_BUCKET is not set in environment variables.")
        self.bucket = settings.AWS_S3_BUCKET
        self.expiry = settings.AWS_S3_PRESIGNED_URL_EXPIRY
        self.client = _make_s3_client()
        logger.info("s3_storage_initialized", extra={"bucket": self.bucket})

    # ------------------------------------------------------------------
    # Upload
    # ------------------------------------------------------------------

    def upload_file(
        self,
        file_obj: BinaryIO,
        key: str,
        content_type: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> str:
        """Upload a file-like object to S3. Returns the S3 key."""
        extra_args: dict = {}
        if content_type:
            extra_args["ContentType"] = content_type
        elif guessed := mimetypes.guess_type(key)[0]:
            extra_args["ContentType"] = guessed
        if metadata:
            extra_args["Metadata"] = {str(k): str(v) for k, v in metadata.items()}

        try:
            self.client.upload_fileobj(file_obj, self.bucket, key, ExtraArgs=extra_args or None)
            logger.info("s3_upload_success", extra={"key": key, "bucket": self.bucket})
            return key
        except ClientError as e:
            logger.error("s3_upload_error", extra={"key": key, "error": str(e)})
            raise

    def upload_bytes(self, data: bytes, key: str, content_type: Optional[str] = None) -> str:
        """Upload raw bytes to S3."""
        return self.upload_file(BytesIO(data), key, content_type=content_type)

    def upload_local_file(self, local_path: Path, key: str) -> str:
        """Upload a local file by path."""
        content_type = mimetypes.guess_type(str(local_path))[0] or "application/octet-stream"
        with open(local_path, "rb") as f:
            return self.upload_file(f, key, content_type=content_type)

    # ------------------------------------------------------------------
    # Download
    # ------------------------------------------------------------------

    def download_bytes(self, key: str) -> bytes:
        """Download an S3 object and return its bytes."""
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=key)
            return response["Body"].read()
        except ClientError as e:
            logger.error("s3_download_error", extra={"key": key, "error": str(e)})
            raise

    def download_to_path(self, key: str, local_path: Path) -> Path:
        """Download an S3 object to a local file path."""
        local_path.parent.mkdir(parents=True, exist_ok=True)
        self.client.download_file(self.bucket, key, str(local_path))
        logger.info("s3_download_success", extra={"key": key, "local": str(local_path)})
        return local_path

    # ------------------------------------------------------------------
    # Pre-signed / Public URLs
    # ------------------------------------------------------------------

    def get_presigned_url(self, key: str, expiry_seconds: Optional[int] = None) -> str:
        """Generate a time-limited pre-signed GET URL for a private S3 object."""
        url = self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expiry_seconds or self.expiry,
        )
        return url

    def get_presigned_upload_url(self, key: str, content_type: str, expiry_seconds: int = 300) -> dict:
        """
        Generate a pre-signed POST URL so the frontend can upload directly
        to S3 without routing through the backend.
        Returns: {"url": ..., "fields": {...}}
        """
        return self.client.generate_presigned_post(
            Bucket=self.bucket,
            Key=key,
            Fields={"Content-Type": content_type},
            Conditions=[{"Content-Type": content_type}],
            ExpiresIn=expiry_seconds,
        )

    # ------------------------------------------------------------------
    # Delete / Existence
    # ------------------------------------------------------------------

    def delete_file(self, key: str) -> bool:
        """Delete an object from S3. Returns True on success."""
        try:
            self.client.delete_object(Bucket=self.bucket, Key=key)
            logger.info("s3_delete_success", extra={"key": key})
            return True
        except ClientError as e:
            logger.error("s3_delete_error", extra={"key": key, "error": str(e)})
            return False

    def file_exists(self, key: str) -> bool:
        """Check if an S3 object exists without downloading it."""
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError:
            return False

    # ------------------------------------------------------------------
    # List
    # ------------------------------------------------------------------

    def list_files(self, prefix: str = "") -> list[str]:
        """Return a list of S3 keys under the given prefix."""
        try:
            paginator = self.client.get_paginator("list_objects_v2")
            keys = []
            for page in paginator.paginate(Bucket=self.bucket, Prefix=prefix):
                for obj in page.get("Contents", []):
                    keys.append(obj["Key"])
            return keys
        except ClientError as e:
            logger.error("s3_list_error", extra={"prefix": prefix, "error": str(e)})
            return []


# --- Singleton ---
_s3_service: Optional[S3StorageService] = None


def get_s3_storage() -> S3StorageService:
    global _s3_service
    if _s3_service is None:
        _s3_service = S3StorageService()
    return _s3_service
