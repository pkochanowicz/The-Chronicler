from typing import Dict, Any
import aiohttp
import io

class MCPTools:
    def __init__(self, settings, discord_client, sheets_service):
        self.settings = settings
        self.discord_client = discord_client
        self.sheets_service = sheets_service
        self.tools = {
            "get_character_sheet": self.get_character_sheet,
            "send_discord_message": self.send_discord_message,
            "list_discord_channels": self.list_discord_channels,
            "post_image_to_graphics_storage": self.post_image_to_graphics_storage,
        }

    async def post_image_to_graphics_storage(self, image_url: str, filename: str = None) -> Dict[str, Any]:
        """
        Fetches an image from a URL and posts it to the #graphics-storage channel.
        Returns the Discord CDN URL of the posted image.
        """
        channel_id = self.settings.GRAPHICS_STORAGE_CHANNEL_ID
        if not channel_id:
            return {"success": False, "error": "GRAPHICS_STORAGE_CHANNEL_ID is not configured in settings."}

        channel = self.discord_client.get_channel(channel_id)
        if not channel:
            return {"success": False, "error": f"Graphics storage channel with ID '{channel_id}' not found."}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as resp:
                    resp.raise_for_status() # Raise an exception for bad status codes
                    image_bytes = io.BytesIO(await resp.read())
            
            discord_file = discord.File(image_bytes, filename=filename or image_url.split('/')[-1])
            message = await channel.send(file=discord_file)
            
            if message.attachments:
                return {"success": True, "cdn_url": message.attachments[0].url}
            else:
                return {"success": False, "error": "No attachment found in the sent message."}
        except aiohttp.ClientError as e:
            return {"success": False, "error": f"Failed to fetch image from URL: {e}"}
        except Exception as e:
            return {"success": False, "error": f"Failed to post image to Discord: {e}"}


    async def get_character_sheet(self, character_name: str) -> Dict[str, Any]:
        character = self.sheets_service.get_character_by_name(character_name)
        if character:
            return character
        else:
            return {"error": f"Character '{character_name}' not found."}

    async def send_discord_message(self, channel_id: int, message: str) -> Dict[str, Any]:
        try:
            channel = self.discord_client.get_channel(channel_id)
            if channel:
                await channel.send(message)
                return {"status": "Message sent successfully."}
            else:
                return {"error": f"Channel with ID '{channel_id}' not found."}
        except Exception as e:
            return {"error": str(e)}

    async def list_discord_channels(self) -> Dict[str, Any]:
        try:
            guild = self.discord_client.get_guild(self.settings.GUILD_ID)
            if guild:
                channels = [{"id": channel.id, "name": channel.name, "type": str(channel.type)} for channel in guild.channels]
                return {"channels": channels}
            else:
                return {"error": f"Guild with ID '{self.settings.GUILD_ID}' not found."}
        except Exception as e:
            return {"error": str(e)}

    async def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found.")
        
        tool_func = self.tools[tool_name]
        if args:
            return await tool_func(**args)
        else:
            return await tool_func()
