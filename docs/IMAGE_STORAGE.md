# Image Storage Architecture — Cloudflare R2

**Version:** 2.0.0
**Backend:** Cloudflare R2 (S3-compatible, Free Tier)
**Status:** Production Ready
**Last Updated:** 2025-12-30

---

## Solution: Cloudflare R2 Free Tier

**Why Cloudflare R2:**
- ✅ **10 GB/month free storage** (永久免費)
- ✅ **Zero egress fees** (unlimited downloads for free)
- ✅ **S3-compatible API** (use boto3)
- ✅ **Production-grade CDN** (Cloudflare's global network)
- ✅ **1M Class A ops/month free** (uploads, lists)
- ✅ **10M Class B ops/month free** (downloads, reads)
- ✅ **No credit card required** for free tier

**Free Tier Limits:**
- Storage: 10 GB/month
- Class A operations (writes): 1,000,000/month
- Class B operations (reads): 10,000,000/month
- Egress: **FREE (unlimited)**

**Expected Usage for Azeroth Bound:**
- ~1000 character portraits × 500KB avg = ~500 MB
- ~100 uploads/month
- Well within free tier limits ✅

---

## Setup Guide

### 1. Create Cloudflare Account & R2 Bucket

```bash
# 1. Sign up at https://dash.cloudflare.com/sign-up (free, no credit card)

# 2. Navigate to R2 in dashboard
# https://dash.cloudflare.com/?to=/:account/r2

# 3. Click "Create bucket"
# Name: azeroth-bound-images
# Location: Automatic (nearest to your users)

# 4. Create API Token
# R2 > Manage R2 API Tokens > Create API Token
# Permissions: Object Read & Write
# Bucket: azeroth-bound-images
# Copy: Access Key ID, Secret Access Key, Account ID
```

### 2. Configure Public Access (Optional)

```bash
# In bucket settings, enable public access for CDN URLs
# Settings > Public Access > Allow Access

# Get your public bucket URL:
# https://pub-<hash>.r2.dev
```

### 3. Environment Variables

Add to `.env`:
```bash
# Cloudflare R2 Configuration
R2_ACCOUNT_ID=your_account_id
R2_ACCESS_KEY_ID=your_access_key
R2_SECRET_ACCESS_KEY=your_secret_key
R2_BUCKET_NAME=azeroth-bound-images
R2_PUBLIC_URL=https://pub-<hash>.r2.dev
```

Add to Fly.io secrets:
```bash
flyctl secrets set \
  R2_ACCOUNT_ID=your_account_id \
  R2_ACCESS_KEY_ID=your_access_key \
  R2_SECRET_ACCESS_KEY=your_secret_key \
  R2_BUCKET_NAME=azeroth-bound-images \
  R2_PUBLIC_URL=https://pub-<hash>.r2.dev
```

---

## Dependencies

### Install boto3

```bash
# Add to pyproject.toml
[tool.poetry.dependencies]
boto3 = "^1.34.0"

# Install
poetry add boto3
```

---

## Implementation

### File: `services/image_storage.py`

```python
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
        'image/jpeg': 'jpg',
        'image/png': 'png',
        'image/gif': 'gif',
        'image/webp': 'webp',
        'image/svg+xml': 'svg'
    }

    def __init__(
        self,
        account_id: str,
        access_key_id: str,
        secret_access_key: str,
        bucket_name: str,
        public_url: str
    ):
        self.bucket_name = bucket_name
        self.public_url = public_url.rstrip('/')

        # Create S3 client configured for R2
        self.s3_client = boto3.client(
            's3',
            endpoint_url=f'https://{account_id}.r2.cloudflarestorage.com',
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name='auto'  # R2 uses 'auto' region
        )

    async def upload(
        self,
        image_bytes: bytes,
        filename: str,
        metadata: Optional[Dict] = None
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
                CacheControl='public, max-age=31536000'  # 1 year cache
            )

            # Construct public URL
            url = f"{self.public_url}/{key}"

            logger.info(
                f"Image uploaded to R2: {filename} ({size_mb:.2f}MB) -> {url}"
            )

            return UploadResult(
                url=url,
                key=key,
                size=len(image_bytes),
                filename=filename,
                content_type=content_type
            )

        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')

            if error_code == 'NoSuchBucket':
                raise BucketNotFoundError(
                    f"Bucket '{self.bucket_name}' not found. Check R2 configuration."
                )

            if error_code == 'AccessDenied':
                raise UploadFailedError(
                    f"Access denied. Check R2 API credentials and permissions."
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
                self.s3_client.delete_object,
                Bucket=self.bucket_name,
                Key=key
            )
            logger.info(f"Deleted image from R2: {key}")
            return True

        except ClientError as e:
            logger.error(f"Failed to delete {key} from R2: {e}")
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
                self.s3_client.head_object,
                Bucket=self.bucket_name,
                Key=key
            )

            return {
                'size': response.get('ContentLength'),
                'content_type': response.get('ContentType'),
                'last_modified': response.get('LastModified'),
                'metadata': response.get('Metadata', {})
            }

        except ClientError:
            return None

    async def upload_with_fallback(
        self,
        image_bytes: bytes,
        filename: str,
        metadata: Optional[Dict] = None
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
        if image_bytes.startswith(b'\xff\xd8\xff'):
            return 'image/jpeg'
        elif image_bytes.startswith(b'\x89PNG'):
            return 'image/png'
        elif image_bytes.startswith(b'GIF87a') or image_bytes.startswith(b'GIF89a'):
            return 'image/gif'
        elif image_bytes.startswith(b'RIFF') and b'WEBP' in image_bytes[:12]:
            return 'image/webp'
        elif image_bytes.startswith(b'<svg') or image_bytes.startswith(b'<?xml'):
            return 'image/svg+xml'

        # Fallback to filename extension
        ext = filename.lower().rsplit('.', 1)[-1]
        ext_map = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp',
            'svg': 'image/svg+xml'
        }
        return ext_map.get(ext, 'application/octet-stream')

    def _get_extension(self, filename: str, content_type: str) -> str:
        """Get file extension from filename or content type."""
        if '.' in filename:
            return filename.lower().rsplit('.', 1)[-1]
        return self.ALLOWED_CONTENT_TYPES.get(content_type, 'bin')

    def _generate_key(self, filename: str, ext: str, metadata: Optional[Dict]) -> str:
        """
        Generate unique S3 key for image.

        Pattern: {context}/{year}/{month}/{uuid}_{sanitized_filename}.{ext}
        Example: portraits/2025/12/a1b2c3d4-e5f6_thorgar.png
        """
        context = metadata.get('context', 'general') if metadata else 'general'
        now = datetime.utcnow()

        # Sanitize filename (keep only alphanumeric and underscores)
        safe_name = ''.join(c if c.isalnum() or c in '_-' else '_' for c in filename.rsplit('.', 1)[0])
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
            public_url=settings.R2_PUBLIC_URL
        )
    return _storage_instance
```

---

## Configuration Updates

### `config/settings.py`

```python
class Settings:
    # ... existing settings ...

    # Cloudflare R2 Image Storage
    self.R2_ACCOUNT_ID: str = os.getenv("R2_ACCOUNT_ID", "")
    self.R2_ACCESS_KEY_ID: str = os.getenv("R2_ACCESS_KEY_ID", "")
    self.R2_SECRET_ACCESS_KEY: str = os.getenv("R2_SECRET_ACCESS_KEY", "")
    self.R2_BUCKET_NAME: str = os.getenv("R2_BUCKET_NAME", "azeroth-bound-images")
    self.R2_PUBLIC_URL: str = os.getenv("R2_PUBLIC_URL", "")

    # Validate on startup
    def validate_r2_config(self):
        """Validate R2 configuration."""
        if not all([self.R2_ACCOUNT_ID, self.R2_ACCESS_KEY_ID,
                    self.R2_SECRET_ACCESS_KEY, self.R2_PUBLIC_URL]):
            logger.warning(
                "R2 configuration incomplete - image uploads will use fallback"
            )
```

---

## Usage in Registration Flow

### Update `flows/registration_flow.py`

```python
from services.image_storage import get_image_storage, ImageStorageError

async def handle_portrait_upload(self, msg: discord.Message):
    """Handle portrait image upload to R2."""
    if not msg.attachments:
        await self.interaction.followup.send("❌ No image attached", ephemeral=True)
        return False

    attachment = msg.attachments[0]

    # Validate image type
    if not attachment.content_type or not attachment.content_type.startswith('image/'):
        await self.interaction.followup.send(
            "❌ Invalid file type. Please upload an image (PNG, JPG, WEBP, etc.)",
            ephemeral=True
        )
        return False

    # Download image
    try:
        image_bytes = await attachment.read()
    except Exception as e:
        logger.error(f"Failed to download attachment: {e}")
        await self.interaction.followup.send("❌ Failed to download image", ephemeral=True)
        return False

    # Upload to R2
    storage = get_image_storage()

    permanent_url = await storage.upload_with_fallback(
        image_bytes=image_bytes,
        filename=attachment.filename,
        metadata={
            "uploader_id": str(self.user.id),
            "context": "portraits",
            "character_name": self.data.get("name", "unknown"),
            "uploaded_at": datetime.utcnow().isoformat()
        }
    )

    self.data["portrait_url"] = permanent_url

    if permanent_url == settings.DEFAULT_PORTRAIT_URL:
        await self.interaction.followup.send(
            "⚠️ Upload failed, using default portrait. You can update it later.",
            ephemeral=True
        )
    else:
        await self.interaction.followup.send(
            f"✅ Portrait uploaded successfully to CDN!",
            ephemeral=True
        )

    return True
```

---

## Cost Monitoring

### Free Tier Usage Tracking

```python
# Monitor R2 usage in Cloudflare dashboard
# https://dash.cloudflare.com/:account/r2/usage

# Expected monthly usage for Azeroth Bound:
# - Storage: ~500 MB (well under 10 GB)
# - Class A ops (uploads): ~100/month (well under 1M)
# - Class B ops (views): ~10,000/month (well under 10M)
# - Egress: FREE (unlimited)
```

### Cost Alerts

```python
# Set up Cloudflare email alerts
# Dashboard > R2 > Settings > Usage Alerts
# Alert at: 80% of storage (8 GB)
# Alert at: 80% of Class A ops (800K)
```

---

## Testing

```python
# tests/unit/test_image_storage.py

import pytest
from services.image_storage import ImageStorage, ImageTooLargeError
from config.settings import settings

@pytest.fixture
def r2_storage():
    return ImageStorage(
        account_id=settings.R2_ACCOUNT_ID,
        access_key_id=settings.R2_ACCESS_KEY_ID,
        secret_access_key=settings.R2_SECRET_ACCESS_KEY,
        bucket_name=settings.R2_BUCKET_NAME,
        public_url=settings.R2_PUBLIC_URL
    )

@pytest.mark.asyncio
async def test_upload_success(r2_storage):
    # 1x1 pixel PNG
    test_png = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
        b'\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00'
        b'\x00\x0cIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4'
        b'\x00\x00\x00\x00IEND\xaeB`\x82'
    )

    result = await r2_storage.upload(test_png, "test.png", {"context": "test"})

    assert result.url.startswith("https://")
    assert "test.png" in result.key
    assert result.content_type == "image/png"

@pytest.mark.asyncio
async def test_image_too_large(r2_storage):
    huge_image = b'x' * (101 * 1024 * 1024)  # 101 MB

    with pytest.raises(ImageTooLargeError):
        await r2_storage.upload(huge_image, "huge.png")

@pytest.mark.asyncio
async def test_fallback_on_error(r2_storage):
    # Invalid credentials should fallback
    bad_storage = ImageStorage(
        account_id="bad",
        access_key_id="bad",
        secret_access_key="bad",
        bucket_name="nonexistent",
        public_url="https://example.com"
    )

    url = await bad_storage.upload_with_fallback(b"test", "test.png")
    assert url == settings.DEFAULT_PORTRAIT_URL
```

---

## Migration from Discord CDN

```python
# scripts/migrate_portraits_to_r2.py

import asyncio
import aiohttp
from db.database import get_db
from schemas.db_schemas import Character
from services.image_storage import get_image_storage
import logging

logger = logging.getLogger(__name__)

async def migrate_portraits():
    """One-time migration of Discord CDN URLs to R2."""
    async with get_db() as db:
        # Find characters with Discord CDN URLs
        characters = db.query(Character).filter(
            Character.portrait_url.like('%cdn.discord%')
        ).all()

        storage = get_image_storage()
        migrated = 0
        failed = 0

        async with aiohttp.ClientSession() as session:
            for char in characters:
                try:
                    # Download from Discord
                    async with session.get(char.portrait_url) as resp:
                        if resp.status == 200:
                            image_bytes = await resp.read()

                            # Upload to R2
                            result = await storage.upload(
                                image_bytes,
                                f"{char.name}_portrait.png",
                                metadata={
                                    "context": "portraits",
                                    "character_id": str(char.id),
                                    "migrated_from": "discord_cdn"
                                }
                            )

                            # Update database
                            char.portrait_url = result.url
                            migrated += 1
                            logger.info(f"Migrated {char.name}: {result.url}")

                        else:
                            logger.warning(f"Failed to download {char.name} portrait")
                            failed += 1

                except Exception as e:
                    logger.error(f"Migration failed for {char.name}: {e}")
                    failed += 1

                # Rate limit: wait between uploads
                await asyncio.sleep(0.5)

        await db.commit()
        logger.info(f"Migration complete: {migrated} success, {failed} failed")

if __name__ == "__main__":
    asyncio.run(migrate_portraits())
```

---

## Security & Best Practices

### 1. R2 Bucket Configuration

```bash
# Enable CORS (if needed for direct uploads from web)
# Dashboard > R2 > Your Bucket > Settings > CORS Policy

[
  {
    "AllowedOrigins": ["https://yourdomain.com"],
    "AllowedMethods": ["GET", "HEAD"],
    "AllowedHeaders": ["*"],
    "ExposeHeaders": ["ETag"],
    "MaxAgeSeconds": 3600
  }
]
```

### 2. API Key Rotation

```python
# Rotate R2 API keys every 90 days
# Generate new key in Cloudflare dashboard
# Update Fly.io secrets
# Old keys remain valid during transition
```

### 3. Access Control

```python
# R2 bucket permissions:
# - Public read (for CDN access)
# - Write only via API key (bot only)
# - Delete only via API key (bot only)
```

---

## Monitoring & Alerts

```python
# Add to bot metrics
from prometheus_client import Counter, Histogram

r2_uploads_total = Counter('r2_uploads_total', 'Total R2 uploads')
r2_upload_errors = Counter('r2_upload_errors_total', 'R2 upload failures', ['error_type'])
r2_upload_size = Histogram('r2_upload_size_bytes', 'R2 upload sizes')
r2_upload_latency = Histogram('r2_upload_latency_seconds', 'R2 upload latency')
```

---

*Production-Ready Implementation*
*Cloudflare R2 Free Tier — 10GB storage, unlimited egress, zero costs*

