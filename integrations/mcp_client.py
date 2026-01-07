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
MCP Server Integration Client

The Chronicler (hosted bot) triggers workflows that the MCP server (local) executes.
Communication via webhooks or HTTP requests with API key authentication.

MCP Server Repository: https://github.com/pkochanowicz/discord-guildmaster-mcp
"""

import aiohttp
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
from config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class WorkflowResponse:
    """Response from MCP workflow trigger."""

    success: bool
    workflow_id: Optional[str] = None
    message: str = ""
    error: Optional[str] = None


class MCPConnectionError(Exception):
    """Failed to connect to MCP server."""

    pass


class MCPAuthenticationError(Exception):
    """API key authentication failed."""

    pass


class MCPWorkflowError(Exception):
    """Workflow execution failed."""

    pass


class MCPWorkflowTrigger:
    """
    Client for triggering workflows on the external MCP server.

    The Chronicler (hosted) uses this to delegate complex AI workflows to
    the MCP server (local), which has access to:
    - Discord API tools (via discord-guildmaster-mcp)
    - LLM agents (via Claude Desktop or API)
    - ComfyUI (for image generation)
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: int = 30,
    ):
        """
        Initialize MCP client.

        Args:
            base_url: MCP server URL (default: from settings)
            api_key: API key for authentication (default: from settings)
            timeout: Request timeout in seconds
        """
        self.base_url = (base_url or f"http://localhost:{settings.MCP_PORT}").rstrip(
            "/"
        )
        self.api_key = api_key or settings.MCP_API_KEY
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    async def _make_request(
        self, endpoint: str, payload: Dict[str, Any], method: str = "POST"
    ) -> Dict[str, Any]:
        """
        Make authenticated request to MCP server.

        Args:
            endpoint: API endpoint (e.g., "/webhooks/character-welcome")
            payload: Request payload
            method: HTTP method

        Returns:
            Response JSON

        Raises:
            MCPConnectionError: If connection fails
            MCPAuthenticationError: If API key is invalid
            MCPWorkflowError: If workflow execution fails
        """
        if not self.session:
            self.session = aiohttp.ClientSession(timeout=self.timeout)

        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json", "X-API-Key": self.api_key}

        try:
            async with self.session.request(
                method, url, json=payload, headers=headers
            ) as resp:
                # Handle authentication errors
                if resp.status == 401 or resp.status == 403:
                    raise MCPAuthenticationError(
                        f"MCP authentication failed (status {resp.status}). "
                        f"Check MCP_API_KEY configuration."
                    )

                # Handle workflow errors
                if resp.status >= 400:
                    error_text = await resp.text()
                    raise MCPWorkflowError(
                        f"MCP workflow failed (status {resp.status}): {error_text}"
                    )

                return await resp.json()

        except aiohttp.ClientError as e:
            raise MCPConnectionError(f"Failed to connect to MCP server at {url}: {e}")

    async def trigger_character_welcome(
        self, member_id: str, guild_id: str, character_data: Dict[str, Any]
    ) -> WorkflowResponse:
        """
        Trigger AI-powered welcome message workflow for new character.

        MCP Server will:
        1. Generate personalized welcome using character backstory
        2. (Optional) Generate character portrait with ComfyUI
        3. Post to #recruitment channel
        4. Assign Seeker role

        Args:
            member_id: Discord member ID
            guild_id: Discord guild ID
            character_data: Character details (name, race, class, backstory, etc.)

        Returns:
            WorkflowResponse with workflow ID and status

        Example:
            async with MCPWorkflowTrigger() as mcp:
                response = await mcp.trigger_character_welcome(
                    member_id="123456789",
                    guild_id="987654321",
                    character_data={
                        "name": "Thorgar",
                        "race": "Orc",
                        "class": "Warrior",
                        "backstory": "A battle-hardened veteran..."
                    }
                )
        """
        try:
            result = await self._make_request(
                endpoint="/webhooks/character-welcome",
                payload={
                    "member_id": member_id,
                    "guild_id": guild_id,
                    "character": character_data,
                },
            )

            logger.info(
                f"Character welcome workflow triggered for {character_data.get('name')} "
                f"(member {member_id}): {result.get('workflow_id')}"
            )

            return WorkflowResponse(
                success=True,
                workflow_id=result.get("workflow_id"),
                message=result.get("message", "Workflow triggered successfully"),
            )

        except (MCPConnectionError, MCPAuthenticationError, MCPWorkflowError) as e:
            logger.error(f"Failed to trigger character welcome: {e}")
            return WorkflowResponse(success=False, error=str(e))

    async def trigger_event_announcement(
        self, event_data: Dict[str, Any], generate_banner: bool = False
    ) -> WorkflowResponse:
        """
        Trigger AI-powered event announcement with optional ComfyUI banner.

        MCP Server will:
        1. Generate announcement text from event details
        2. (Optional) Generate event banner image with ComfyUI
        3. Post to appropriate channel(s)
        4. Ping relevant roles (@Pathfinder, @Trailwarden, etc.)

        Args:
            event_data: Event details (title, description, date, time, location)
            generate_banner: Whether to generate ComfyUI banner image

        Returns:
            WorkflowResponse with workflow ID and status

        Example:
            async with MCPWorkflowTrigger() as mcp:
                response = await mcp.trigger_event_announcement(
                    event_data={
                        "title": "Molten Core Raid",
                        "description": "First guild raid! Be there or be square.",
                        "date": "2025-01-15",
                        "time": "19:00 ST",
                        "location": "Blackrock Mountain"
                    },
                    generate_banner=True
                )
        """
        try:
            result = await self._make_request(
                endpoint="/webhooks/event-announcement",
                payload={"event": event_data, "generate_banner": generate_banner},
            )

            logger.info(
                f"Event announcement triggered for '{event_data.get('title')}': "
                f"{result.get('workflow_id')}"
            )

            return WorkflowResponse(
                success=True,
                workflow_id=result.get("workflow_id"),
                message=result.get("message", "Event announcement triggered"),
            )

        except (MCPConnectionError, MCPAuthenticationError, MCPWorkflowError) as e:
            logger.error(f"Failed to trigger event announcement: {e}")
            return WorkflowResponse(success=False, error=str(e))

    async def request_channel_summary(
        self, channel_id: str, hours: int = 24, format: str = "bullet"
    ) -> WorkflowResponse:
        """
        Request AI summary of channel activity.

        MCP Server will:
        1. Fetch messages from channel (last N hours)
        2. Generate AI summary with key points
        3. Return summary text or post to channel

        Args:
            channel_id: Discord channel ID
            hours: Hours of history to summarize
            format: Summary format ("bullet", "paragraph", "tldr")

        Returns:
            WorkflowResponse with summary text

        Example:
            async with MCPWorkflowTrigger() as mcp:
                response = await mcp.request_channel_summary(
                    channel_id="123456789",
                    hours=24,
                    format="bullet"
                )
                summary = response.message
        """
        try:
            result = await self._make_request(
                endpoint="/webhooks/channel-summary",
                payload={"channel_id": channel_id, "hours": hours, "format": format},
            )

            logger.info(
                f"Channel summary requested for {channel_id} (last {hours}h): "
                f"{result.get('workflow_id')}"
            )

            return WorkflowResponse(
                success=True,
                workflow_id=result.get("workflow_id"),
                message=result.get("summary", ""),
            )

        except (MCPConnectionError, MCPAuthenticationError, MCPWorkflowError) as e:
            logger.error(f"Failed to request channel summary: {e}")
            return WorkflowResponse(success=False, error=str(e))

    async def trigger_portrait_generation(
        self, character_id: int, character_data: Dict[str, Any]
    ) -> WorkflowResponse:
        """
        Trigger ComfyUI portrait generation via MCP server.

        MCP Server will:
        1. Generate portrait using ComfyUI workflow
        2. Upload to R2 storage (via Chronicler's image_storage service)
        3. Update character portrait_url in database
        4. Return permanent CDN URL

        Args:
            character_id: Character database ID
            character_data: Character details for prompt generation

        Returns:
            WorkflowResponse with portrait URL

        Example:
            async with MCPWorkflowTrigger() as mcp:
                response = await mcp.trigger_portrait_generation(
                    character_id=42,
                    character_data={
                        "name": "Thorgar",
                        "race": "Orc",
                        "class": "Warrior",
                        "personality": "Gruff but honorable",
                        "trait_1": "Battle-scarred",
                        "trait_2": "Graying hair",
                        "trait_3": "Missing left eye"
                    }
                )
                portrait_url = response.message
        """
        try:
            result = await self._make_request(
                endpoint="/webhooks/portrait-generation",
                payload={"character_id": character_id, "character": character_data},
            )

            logger.info(
                f"Portrait generation triggered for character {character_id} "
                f"({character_data.get('name')}): {result.get('workflow_id')}"
            )

            return WorkflowResponse(
                success=True,
                workflow_id=result.get("workflow_id"),
                message=result.get("portrait_url", ""),
            )

        except (MCPConnectionError, MCPAuthenticationError, MCPWorkflowError) as e:
            logger.error(f"Failed to trigger portrait generation: {e}")
            return WorkflowResponse(success=False, error=str(e))

    async def health_check(self) -> bool:
        """
        Check if MCP server is accessible.

        Returns:
            True if server responds, False otherwise
        """
        try:
            result = await self._make_request(
                endpoint="/health", payload={}, method="GET"
            )
            return result.get("status") == "ok"

        except (MCPConnectionError, MCPAuthenticationError, MCPWorkflowError):
            return False


# Singleton instance for convenience
_mcp_client: Optional[MCPWorkflowTrigger] = None


def get_mcp_client() -> MCPWorkflowTrigger:
    """Get or create global MCP client instance."""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPWorkflowTrigger()
    return _mcp_client
