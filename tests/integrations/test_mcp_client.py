# Azeroth Bound Discord Bot
# Copyright (C) 2025 [Paweł Kochanowicz - <github.com/pkochanowicz> ]
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

"""
Tests for MCP Server Integration Client

Test coverage for integrations/mcp_client.py:
- Workflow trigger methods (character welcome, events, summaries, portraits)
- Error handling (connection, authentication, workflow failures)
- Health check functionality
- Async context manager behavior
- Request authentication
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from aiohttp import ClientError
from integrations.mcp_client import MCPWorkflowTrigger, WorkflowResponse, get_mcp_client


def create_mock_response(status=200, json_data=None, text_data=None):
    """Helper to create a properly mocked aiohttp response with context manager support."""
    mock_response = AsyncMock()
    mock_response.status = status
    if json_data is not None:
        mock_response.json = AsyncMock(return_value=json_data)
    if text_data is not None:
        mock_response.text = AsyncMock(return_value=text_data)
    # Set up async context manager protocol
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    # __aexit__ should return None/False to NOT suppress exceptions
    mock_response.__aexit__ = AsyncMock(return_value=None)
    return mock_response


@pytest.fixture
def mock_aiohttp_session():
    """Mock aiohttp ClientSession."""
    with patch("integrations.mcp_client.aiohttp.ClientSession") as mock_session:
        session_instance = AsyncMock()
        mock_session.return_value = session_instance
        yield session_instance


@pytest.fixture
def mcp_client():
    """Create MCPWorkflowTrigger instance."""
    return MCPWorkflowTrigger(
        base_url="http://localhost:8000", api_key="test_api_key", timeout=30
    )


class TestMCPWorkflowTriggerInit:
    """Test MCP client initialization."""

    def test_init_default_settings(self):
        """Test initialization with default settings."""
        with patch("integrations.mcp_client.settings") as mock_settings:
            mock_settings.MCP_PORT = 8000
            mock_settings.MCP_API_KEY = "default_key"

            client = MCPWorkflowTrigger()

            assert client.base_url == "http://localhost:8000"
            assert client.api_key == "default_key"

    def test_init_custom_settings(self):
        """Test initialization with custom settings."""
        client = MCPWorkflowTrigger(
            base_url="http://custom:9000", api_key="custom_key", timeout=60
        )

        assert client.base_url == "http://custom:9000"
        assert client.api_key == "custom_key"
        assert client.timeout.total == 60


class TestMCPWorkflowTriggerCharacterWelcome:
    """Test character welcome workflow triggering."""

    @pytest.mark.asyncio
    async def test_trigger_character_welcome_success(
        self, mcp_client, mock_aiohttp_session
    ):
        """Test successful character welcome trigger."""
        mock_response = create_mock_response(
            status=200,
            json_data={
                "workflow_id": "wf_123456",
                "message": "Welcome workflow triggered",
            },
        )

        # Use MagicMock (not AsyncMock) since session.request() needs to return the context manager directly
        mock_aiohttp_session.request = MagicMock(return_value=mock_response)
        mcp_client.session = mock_aiohttp_session

        result = await mcp_client.trigger_character_welcome(
            member_id="123456789",
            guild_id="987654321",
            character_data={
                "name": "Thorgar",
                "race": "Orc",
                "class": "Warrior",
                "backstory": "A veteran warrior...",
            },
        )

        assert isinstance(result, WorkflowResponse)
        assert result.success is True
        assert result.workflow_id == "wf_123456"
        assert result.error is None

    @pytest.mark.asyncio
    async def test_trigger_character_welcome_connection_error(
        self, mcp_client, mock_aiohttp_session
    ):
        """Test character welcome with connection error."""
        mock_aiohttp_session.request = MagicMock(
            side_effect=ClientError("Connection refused")
        )
        mcp_client.session = mock_aiohttp_session

        result = await mcp_client.trigger_character_welcome(
            member_id="123456789",
            guild_id="987654321",
            character_data={"name": "Thorgar"},
        )

        assert result.success is False
        assert result.error is not None
        assert "Failed to connect" in result.error


class TestMCPWorkflowTriggerEventAnnouncement:
    """Test event announcement workflow triggering."""

    @pytest.mark.asyncio
    async def test_trigger_event_announcement_success(
        self, mcp_client, mock_aiohttp_session
    ):
        """Test successful event announcement trigger."""
        mock_response = create_mock_response(
            status=200,
            json_data={
                "workflow_id": "wf_event_001",
                "message": "Event announcement triggered",
            },
        )

        mock_aiohttp_session.request = MagicMock(return_value=mock_response)
        mcp_client.session = mock_aiohttp_session

        result = await mcp_client.trigger_event_announcement(
            event_data={
                "title": "Molten Core Raid",
                "description": "First guild raid!",
                "date": "2025-01-15",
                "time": "19:00 ST",
            },
            generate_banner=True,
        )

        assert result.success is True
        assert result.workflow_id == "wf_event_001"

    @pytest.mark.asyncio
    async def test_trigger_event_announcement_workflow_error(
        self, mcp_client, mock_aiohttp_session
    ):
        """Test event announcement with workflow error."""
        mock_response = create_mock_response(
            status=500, text_data="Internal server error"
        )

        mock_aiohttp_session.request = MagicMock(return_value=mock_response)
        mcp_client.session = mock_aiohttp_session

        result = await mcp_client.trigger_event_announcement(
            event_data={"title": "Test Event"}, generate_banner=False
        )

        assert result.success is False
        assert result.error is not None


class TestMCPWorkflowTriggerChannelSummary:
    """Test channel summary request."""

    @pytest.mark.asyncio
    async def test_request_channel_summary_success(
        self, mcp_client, mock_aiohttp_session
    ):
        """Test successful channel summary request."""
        mock_response = create_mock_response(
            status=200,
            json_data={
                "workflow_id": "wf_summary_001",
                "summary": "• User A posted about raid\n• User B asked about talents",
            },
        )

        mock_aiohttp_session.request = MagicMock(return_value=mock_response)
        mcp_client.session = mock_aiohttp_session

        result = await mcp_client.request_channel_summary(
            channel_id="123456789", hours=24, format="bullet"
        )

        assert result.success is True
        assert "User A" in result.message


class TestMCPWorkflowTriggerPortraitGeneration:
    """Test portrait generation workflow."""

    @pytest.mark.asyncio
    async def test_trigger_portrait_generation_success(
        self, mcp_client, mock_aiohttp_session
    ):
        """Test successful portrait generation trigger."""
        mock_response = create_mock_response(
            status=200,
            json_data={
                "workflow_id": "wf_portrait_001",
                "portrait_url": "https://r2.dev/portraits/thorgar.png",
            },
        )

        mock_aiohttp_session.request = MagicMock(return_value=mock_response)
        mcp_client.session = mock_aiohttp_session

        result = await mcp_client.trigger_portrait_generation(
            character_id=42,
            character_data={"name": "Thorgar", "race": "Orc", "class": "Warrior"},
        )

        assert result.success is True
        assert "thorgar.png" in result.message


class TestMCPWorkflowTriggerErrorHandling:
    """Test error handling and exceptions."""

    @pytest.mark.asyncio
    async def test_authentication_error_401(self, mcp_client, mock_aiohttp_session):
        """Test 401 authentication error."""
        mock_response = create_mock_response(status=401)

        mock_aiohttp_session.request = MagicMock(return_value=mock_response)
        mcp_client.session = mock_aiohttp_session

        result = await mcp_client.trigger_character_welcome(
            member_id="123", guild_id="456", character_data={"name": "Test"}
        )

        assert result.success is False
        assert "authentication failed" in result.error.lower()

    @pytest.mark.asyncio
    async def test_authentication_error_403(self, mcp_client, mock_aiohttp_session):
        """Test 403 authentication error."""
        mock_response = create_mock_response(status=403)

        mock_aiohttp_session.request = MagicMock(return_value=mock_response)
        mcp_client.session = mock_aiohttp_session

        result = await mcp_client.trigger_character_welcome(
            member_id="123", guild_id="456", character_data={"name": "Test"}
        )

        assert result.success is False
        assert "authentication failed" in result.error.lower()


class TestMCPWorkflowTriggerHealthCheck:
    """Test health check functionality."""

    @pytest.mark.asyncio
    async def test_health_check_success(self, mcp_client, mock_aiohttp_session):
        """Test successful health check."""
        mock_response = create_mock_response(status=200, json_data={"status": "ok"})

        mock_aiohttp_session.request = MagicMock(return_value=mock_response)
        mcp_client.session = mock_aiohttp_session

        result = await mcp_client.health_check()

        assert result is True

    @pytest.mark.asyncio
    async def test_health_check_failure(self, mcp_client, mock_aiohttp_session):
        """Test health check failure."""
        mock_aiohttp_session.request = MagicMock(
            side_effect=ClientError("Connection failed")
        )
        mcp_client.session = mock_aiohttp_session

        result = await mcp_client.health_check()

        assert result is False


class TestMCPWorkflowTriggerContextManager:
    """Test async context manager behavior."""

    @pytest.mark.asyncio
    async def test_context_manager_creates_session(self, mcp_client):
        """Test that context manager creates session."""
        mock_session_instance = AsyncMock()
        mock_session_instance.close = AsyncMock()

        with patch(
            "integrations.mcp_client.aiohttp.ClientSession",
            return_value=mock_session_instance,
        ) as mock_session_class:
            async with mcp_client as client:
                assert client.session is not None
                mock_session_class.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_manager_closes_session(self, mcp_client):
        """Test that context manager closes session."""
        mock_session = AsyncMock()
        mock_session.close = AsyncMock()

        with patch(
            "integrations.mcp_client.aiohttp.ClientSession", return_value=mock_session
        ):
            async with mcp_client:
                pass

            mock_session.close.assert_called_once()


class TestMCPWorkflowTriggerSingleton:
    """Test singleton client getter."""

    def test_get_mcp_client_creates_instance(self):
        """Test get_mcp_client creates singleton instance."""
        # Reset singleton
        import integrations.mcp_client as mcp_module

        mcp_module._mcp_client = None

        client = get_mcp_client()

        assert isinstance(client, MCPWorkflowTrigger)

    def test_get_mcp_client_returns_same_instance(self):
        """Test get_mcp_client returns same instance."""
        import integrations.mcp_client as mcp_module

        mcp_module._mcp_client = None

        client1 = get_mcp_client()
        client2 = get_mcp_client()

        assert client1 is client2


# TODO: Add integration tests with real MCP server (separate test suite)
# TODO: Add tests for request headers and authentication details
# TODO: Add tests for timeout behavior
