import logging

import boto3
from app.core.config import settings
from app.interfaces.storage_service import IStorageService
from botocore.config import Config

logger = logging.getLogger(__name__)


def _initials_url(key: str) -> str:
    parts = key.split("/")
    name = parts[-1] if parts else key
    initials = "".join(word[0].upper() for word in name.split() if word)[:2] or "U"
    return f"https://ui-avatars.com/api/?name={initials}&background=2d8eff&color=fff"


class StorageService(IStorageService):
    def __init__(self):
        self._client = None
        try:
            self._client = boto3.client(
                "s3",
                endpoint_url=(
                    f"https://{settings.R2_ACCOUNT_ID}" ".r2.cloudflarestorage.com"
                ),
                aws_access_key_id=settings.R2_ACCESS_KEY_ID,
                aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
                config=Config(signature_version="s3v4"),
                region_name="auto",
            )
        except Exception as error:
            logger.warning(f"R2 not configured, using initials fallback: {error}")

    async def upload(self, key: str, file_bytes: bytes, content_type: str) -> str:
        if self._client is None:
            return _initials_url(key)
        try:
            self._client.put_object(
                Bucket=settings.R2_BUCKET_NAME,
                Key=key,
                Body=file_bytes,
                ContentType=content_type,
            )
            return f"{settings.R2_PUBLIC_URL}/{key}"
        except Exception as error:
            logger.warning(f"R2 upload failed, using fallback: {error}")
            return _initials_url(key)

    async def delete(self, key: str) -> None:
        if self._client is None:
            return
        try:
            self._client.delete_object(Bucket=settings.R2_BUCKET_NAME, Key=key)
        except Exception as error:
            logger.warning(f"Failed to delete from R2: {error}")
