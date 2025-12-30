# Azeroth Bound Discord Bot
# Copyright (C) 2025 [Paweł Kochanowicz - <github.com/pkochanowicz> ]
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

"""
Tests for Cloudflare R2 Image Storage Service

Test coverage for services/image_storage.py:
- Upload functionality
- File size validation
- Content type detection
- Error handling and fallbacks
- S3/R2 integration (mocked)
"""

import pytest
from unittest.mock import MagicMock, patch
from services.image_storage import (
    ImageStorage,
    ImageStorageError,
    ImageTooLargeError,
    BucketNotFoundError,
    UploadFailedError,
    UploadResult
)
from config.settings import settings


@pytest.fixture
def mock_r2_client():
    """Mock boto3 S3 client for R2."""
    with patch('services.image_storage.boto3.client') as mock_client:
        yield mock_client.return_value


@pytest.fixture
def image_storage(mock_r2_client):
    """Create ImageStorage instance with mocked R2 client."""
    return ImageStorage(
        account_id="test_account",
        access_key_id="test_key",
        secret_access_key="test_secret",
        bucket_name="test-bucket",
        public_url="https://test.r2.dev"
    )


class TestImageStorageUpload:
    """Test image upload functionality."""

    @pytest.mark.asyncio
    async def test_upload_success_png(self, image_storage, mock_r2_client):
        """Test successful PNG upload."""
        # 1x1 pixel PNG
        test_png = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
            b'\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde'
        )

        mock_r2_client.put_object = MagicMock()

        result = await image_storage.upload(
            image_bytes=test_png,
            filename="test.png",
            metadata={"context": "portraits"}
        )

        assert isinstance(result, UploadResult)
        assert result.url.startswith("https://test.r2.dev/")
        assert result.content_type == "image/png"
        assert result.size == len(test_png)
        assert "portraits" in result.key

    @pytest.mark.asyncio
    async def test_upload_too_large(self, image_storage):
        """Test that images exceeding size limit are rejected."""
        huge_image = b'x' * (101 * 1024 * 1024)  # 101 MB

        with pytest.raises(ImageTooLargeError) as exc_info:
            await image_storage.upload(huge_image, "huge.png")

        assert "101" in str(exc_info.value)
        assert "100MB" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_upload_unsupported_format(self, image_storage):
        """Test that unsupported image formats are rejected."""
        fake_data = b'This is not an image'

        with pytest.raises(ImageStorageError) as exc_info:
            await image_storage.upload(fake_data, "test.txt")

        assert "Unsupported image type" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_upload_with_fallback_success(self, image_storage, mock_r2_client):
        """Test upload_with_fallback returns URL on success."""
        test_png = b'\x89PNG\r\n\x1a\n' + b'\x00' * 20
        mock_r2_client.put_object = MagicMock()

        url = await image_storage.upload_with_fallback(test_png, "test.png")

        assert url.startswith("https://")
        assert url != settings.DEFAULT_PORTRAIT_URL

    @pytest.mark.asyncio
    async def test_upload_with_fallback_on_error(self, image_storage):
        """Test upload_with_fallback returns default URL on error."""
        huge_image = b'x' * (101 * 1024 * 1024)

        url = await image_storage.upload_with_fallback(huge_image, "huge.png")

        assert url == settings.DEFAULT_PORTRAIT_URL


class TestImageStorageContentTypeDetection:
    """Test content type detection from magic bytes."""

    @pytest.mark.asyncio
    async def test_detect_png(self, image_storage):
        """Test PNG detection from magic bytes."""
        png_bytes = b'\x89PNG\r\n\x1a\n' + b'\x00' * 20
        content_type = image_storage._detect_content_type(png_bytes, "unknown.bin")
        assert content_type == "image/png"

    @pytest.mark.asyncio
    async def test_detect_jpeg(self, image_storage):
        """Test JPEG detection from magic bytes."""
        jpeg_bytes = b'\xff\xd8\xff' + b'\x00' * 20
        content_type = image_storage._detect_content_type(jpeg_bytes, "unknown.bin")
        assert content_type == "image/jpeg"

    @pytest.mark.asyncio
    async def test_detect_gif(self, image_storage):
        """Test GIF detection from magic bytes."""
        gif_bytes = b'GIF89a' + b'\x00' * 20
        content_type = image_storage._detect_content_type(gif_bytes, "unknown.bin")
        assert content_type == "image/gif"


class TestImageStorageKeyGeneration:
    """Test S3 key generation."""

    def test_generate_key_with_context(self, image_storage):
        """Test key includes context from metadata."""
        key = image_storage._generate_key(
            filename="thorgar.png",
            ext="png",
            metadata={"context": "portraits"}
        )

        assert key.startswith("portraits/")
        assert "thorgar" in key
        assert key.endswith(".png")

    def test_generate_key_sanitizes_filename(self, image_storage):
        """Test that special characters are sanitized."""
        key = image_storage._generate_key(
            filename="test@#$%.png",
            ext="png",
            metadata={}
        )

        # Special chars should be replaced with underscores
        assert "@" not in key
        assert "#" not in key
        assert "$" not in key


class TestImageStorageErrorHandling:
    """Test error handling and exceptions."""

    @pytest.mark.asyncio
    async def test_bucket_not_found_error(self, image_storage, mock_r2_client):
        """Test BucketNotFoundError on missing bucket."""
        from botocore.exceptions import ClientError

        mock_r2_client.put_object.side_effect = ClientError(
            {"Error": {"Code": "NoSuchBucket"}},
            "PutObject"
        )

        test_png = b'\x89PNG\r\n\x1a\n' + b'\x00' * 20

        with pytest.raises(BucketNotFoundError):
            await image_storage.upload(test_png, "test.png")

    @pytest.mark.asyncio
    async def test_access_denied_error(self, image_storage, mock_r2_client):
        """Test UploadFailedError on access denied."""
        from botocore.exceptions import ClientError

        mock_r2_client.put_object.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied"}},
            "PutObject"
        )

        test_png = b'\x89PNG\r\n\x1a\n' + b'\x00' * 20

        with pytest.raises(UploadFailedError) as exc_info:
            await image_storage.upload(test_png, "test.png")

        assert "Access denied" in str(exc_info.value)


# TODO: Add integration tests with real R2 bucket (separate test suite)
# TODO: Add tests for delete() method
# TODO: Add tests for get_metadata() method
