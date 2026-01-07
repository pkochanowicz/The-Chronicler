# Azeroth Bound Discord Bot
# Copyright (C) 2025 [Paweł Kochanowicz - <github.com/pkochanowicz> ]
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Image Storage Service using Cloudflare R2 (S3-compatible)
Provides permanent, production-grade image hosting with zero egress fees.
"""

import boto3
from botocore.exceptions import ClientError
import asyncio
import logging
import uuid
from typing import Optional, Dict
from dataclasses import dataclass
from datetime import datetime
from config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class UploadResult:
    """Result of an image upload."""

    url: str
    key: str
    size: int
    filename: str
    content_type: str


class ImageStorageError(Exception):
    """Base exception for image storage errors."""

    pass


class ImageTooLargeError(ImageStorageError):
    """Image exceeds reasonable size limit."""

    pass


class BucketNotFoundError(ImageStorageError):
    """R2 bucket not found or inaccessible."""

    pass


class UploadFailedError(ImageStorageError):
    """Upload to R2 failed."""

    pass


class ImageStorage:
    """
    Cloudflare R2 image storage service.

    Free tier limits:
    - Storage: 10 GB/month
    - Class A operations (writes): 1,000,000/month
    - Class B operations (reads): 10,000,000/month
    - Egress: FREE (unlimited)
    """

    MAX_SIZE_MB = 100  # Conservative limit (R2 supports up to 5TB per object)
    MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024

    ALLOWED_CONTENT_TYPES = {
        "image/jpeg": "jpg",
        "image/png": "png",
        "image/gif": "gif",
        "image/webp": "webp",
        "image/svg+xml": "svg",
    }

    def __init__(
        self,
        account_id: str,
        access_key_id: str,
        secret_access_key: str,
        bucket_name: str,
        public_url: str,
    ):
        self.bucket_name = bucket_name
        self.public_url = public_url.rstrip("/")

        # Create S3 client configured for R2
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name="auto",  # R2 uses 'auto' region
        )

    async def upload(
        self, image_bytes: bytes, filename: str, metadata: Optional[Dict] = None
    ) -> UploadResult:
        """
        Upload image to R2 and return permanent URL.

        Args:
            image_bytes: Raw image data
            filename: Original filename (used for extension detection)
            metadata: Optional metadata to store with object

        Returns:
            UploadResult with permanent CDN URL

        Raises:
            ImageTooLargeError: If image exceeds size limit
            BucketNotFoundError: If R2 bucket is inaccessible
            UploadFailedError: If upload fails
        """
        # Validate size
        size_mb = len(image_bytes) / (1024 * 1024)
        if len(image_bytes) > self.MAX_SIZE_BYTES:
            raise ImageTooLargeError(
                f"Image size {size_mb:.2f}MB exceeds {self.MAX_SIZE_MB}MB limit"
            )

        # Detect content type
        content_type = self._detect_content_type(image_bytes, filename)
        if content_type not in self.ALLOWED_CONTENT_TYPES:
            raise ImageStorageError(f"Unsupported image type: {content_type}")

        # Generate unique key
        ext = self._get_extension(filename, content_type)
        key = self._generate_key(filename, ext, metadata)

        # Prepare metadata
        s3_metadata = self._prepare_metadata(metadata)

        # Upload to R2 (run in thread pool to avoid blocking)
        try:
            await asyncio.to_thread(
                self.s3_client.put_object,
                Bucket=self.bucket_name,
                Key=key,
                Body=image_bytes,
                ContentType=content_type,
                Metadata=s3_metadata,
                CacheControl="public, max-age=31536000",  # 1 year cache
            )

            # Construct public URL
            url = f"{self.public_url}/{key}"

            logger.info(f"Image uploaded to R2: {filename} ({size_mb:.2f}MB) -> {url}")

            return UploadResult(
                url=url,
                key=key,
                size=len(image_bytes),
                filename=filename,
                content_type=content_type,
            )

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")

            if error_code == "NoSuchBucket":
                raise BucketNotFoundError(
                    f"Bucket '{self.bucket_name}' not found. Check R2 configuration."
                )

            if error_code == "AccessDenied":
                raise UploadFailedError(
                    "Access denied. Check R2 API credentials and permissions."
                )

            raise UploadFailedError(f"R2 upload failed: {error_code} - {e}")

        except Exception as e:
            raise UploadFailedError(f"Unexpected upload error: {e}")

    async def delete(self, key: str) -> bool:
        """
        Delete image from R2 by key.

        Args:
            key: The object key in R2

        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            await asyncio.to_thread(
                self.s3_client.delete_object, Bucket=self.bucket_name, Key=key
            )
            logger.info(f"Deleted image from R2: {key}")
            return True

        except ClientError as e:
            logger.error(f"Failed to delete {key} from R2: {e}")  # nosec B608
            return False

    async def get_metadata(self, key: str) -> Optional[Dict]:
        """
        Retrieve metadata for an object in R2.

        Args:
            key: The object key

        Returns:
            Dictionary of metadata or None if not found
        """
        try:
            response = await asyncio.to_thread(
                self.s3_client.head_object, Bucket=self.bucket_name, Key=key
            )

            return {
                "size": response.get("ContentLength"),
                "content_type": response.get("ContentType"),
                "last_modified": response.get("LastModified"),
                "metadata": response.get("Metadata", {}),
            }

        except ClientError:
            return None

    async def upload_with_fallback(
        self, image_bytes: bytes, filename: str, metadata: Optional[Dict] = None
    ) -> str:
        """
        Upload with graceful fallback to default portrait.

        Returns:
            Permanent URL or default portrait URL if upload fails
        """
        try:
            result = await self.upload(image_bytes, filename, metadata)
            return result.url

        except ImageTooLargeError as e:
            logger.warning(f"Image too large for {filename}: {e}")
            return settings.DEFAULT_PORTRAIT_URL

        except (BucketNotFoundError, UploadFailedError) as e:
            logger.error(f"R2 upload failed for {filename}: {e}")
            return settings.DEFAULT_PORTRAIT_URL

        except Exception as e:
            logger.error(f"Unexpected error uploading {filename}: {e}")
            return settings.DEFAULT_PORTRAIT_URL

    def _detect_content_type(self, image_bytes: bytes, filename: str) -> str:
        """Detect content type from magic bytes or filename."""
        # Check magic bytes
        if image_bytes.startswith(b"\xff\xd8\xff"):
            return "image/jpeg"
        elif image_bytes.startswith(b"\x89PNG"):
            return "image/png"
        elif image_bytes.startswith(b"GIF87a") or image_bytes.startswith(b"GIF89a"):
            return "image/gif"
        elif image_bytes.startswith(b"RIFF") and b"WEBP" in image_bytes[:12]:
            return "image/webp"
        elif image_bytes.startswith(b"<svg") or image_bytes.startswith(b"<?xml"):
            return "image/svg+xml"

        # Fallback to filename extension
        ext = filename.lower().rsplit(".", 1)[-1]
        ext_map = {
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "png": "image/png",
            "gif": "image/gif",
            "webp": "image/webp",
            "svg": "image/svg+xml",
        }
        return ext_map.get(ext, "application/octet-stream")

    def _get_extension(self, filename: str, content_type: str) -> str:
        """Get file extension from filename or content type."""
        if "." in filename:
            return filename.lower().rsplit(".", 1)[-1]
        return self.ALLOWED_CONTENT_TYPES.get(content_type, "bin")

    def _generate_key(self, filename: str, ext: str, metadata: Optional[Dict]) -> str:
        """
        Generate unique S3 key for image.

        Pattern: {context}/{year}/{month}/{uuid}_{sanitized_filename}.{ext}
        Example: portraits/2025/12/a1b2c3d4-e5f6_thorgar.png
        """
        context = metadata.get("context", "general") if metadata else "general"
        now = datetime.utcnow()

        # Sanitize filename (keep only alphanumeric and underscores)
        safe_name = "".join(
            c if c.isalnum() or c in "_-" else "_" for c in filename.rsplit(".", 1)[0]
        )
        safe_name = safe_name[:50]  # Limit length

        # Generate unique ID
        unique_id = str(uuid.uuid4())[:8]

        return f"{context}/{now.year}/{now.month:02d}/{unique_id}_{safe_name}.{ext}"

    def _prepare_metadata(self, metadata: Optional[Dict]) -> Dict[str, str]:
        """Prepare metadata for S3 storage (must be string values)."""
        if not metadata:
            return {}

        s3_metadata = {}
        for key, value in metadata.items():
            if value is not None:
                s3_metadata[key] = str(value)

        return s3_metadata


# Singleton instance
_storage_instance: Optional[ImageStorage] = None


def get_image_storage() -> ImageStorage:
    """Get or create the global ImageStorage instance."""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = ImageStorage(
            account_id=settings.R2_ACCOUNT_ID,
            access_key_id=settings.R2_ACCESS_KEY_ID,
            secret_access_key=settings.R2_SECRET_ACCESS_KEY,
            bucket_name=settings.R2_BUCKET_NAME,
            public_url=settings.R2_PUBLIC_URL,
        )
    return _storage_instance
