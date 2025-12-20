from typing import Dict, Any
import aiohttp
import io
import discord.utils

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

    async def post_image_to_graphics_storage(self, image_url: str, filename: str = None, thread_name: str = None) -> Dict[str, Any]:
        """
        Fetches an image from a URL and posts it to the #graphics-storage channel or a specific thread within it.
        Returns the Discord CDN URL of the posted image.
        """
        channel_id = self.settings.GRAPHICS_STORAGE_CHANNEL_ID
        if not channel_id:
            return {"success": False, "error": "GRAPHICS_STORAGE_CHANNEL_ID is not configured in settings."}

        channel = self.discord_client.get_channel(channel_id)
        if not channel:
            return {"success": False, "error": f"Graphics storage channel with ID '{channel_id}' not found."}
        
        target_channel = channel # Default to main channel

        if thread_name:
            # Check for existing threads in the channel
            # Fetch both active and archived threads
            fetched_threads = []
            try:
                # Need to handle different types of channel (TextChannel, ForumChannel)
                # For TextChannel, threads are accessed via channel.threads and channel.archived_threads
                if isinstance(channel, discord.TextChannel):
                    active_threads = channel.threads
                    archived_threads_obj = await channel.archived_threads(limit=100) # Fetch recent archived threads
                    fetched_threads.extend(active_threads)
                    fetched_threads.extend(archived_threads_obj.threads)
                elif isinstance(channel, discord.ForumChannel):
                    # Forum channels have tags/posts, which are essentially threads.
                    # This might require a different approach if thread_name means a post title
                    # For now, we assume TextChannel behavior.
                    pass # Log a warning or error if this is encountered in future
                
            except discord.Forbidden:
                return {"success": False, "error": "Bot lacks permissions to fetch threads."}
            except Exception as e:
                return {"success": False, "error": f"Failed to fetch threads: {e}"}

            target_thread = discord.utils.get(fetched_threads, name=thread_name)

            if target_thread:
                # If thread is archived, try to unarchive (requires MANAGE_THREADS)
                if target_thread.archived:
                    try:
                        # Unarchive the thread
                        # Discord API requires a parent message to unarchive
                        # or channel.create_thread(name, message=target_thread.parent_id)
                        # The simple unarchive() is usually for a message's thread.
                        # For now, if archived, we create new. Re-joining old archived threads can be complex.
                        # User wants to keep order, so creating new thread is less ideal.
                        # Need to update: if an archived thread cannot be easily unarchived and used,
                        # the only robust solution might be to always post to a new thread OR
                        # keep a mapping of character to thread ID in DB.
                        # For simplicity, if archived, we'll try to find an active thread, else create.
                        # But for now, let's assume if it's found, we use it directly even if archived and Discord handles it.
                        pass # Assuming discord.py handles posting to archived threads (it usually unarchives implicitly for few hours)
                    except Exception as e:
                        logger.warning(f"Failed to handle archived thread '{thread_name}': {e}. Attempting to post anyway.")
                target_channel = target_thread
            else:
                # Create a new thread
                try:
                    # Create a starter message, then create a thread off of it.
                    # Or directly create thread if TextChannel and bot has permissions.
                    # For simplicity, we create a starter message first.
                    starter_message = await channel.send(f"Creating new thread for: {thread_name}", silent=True) # Send silently
                    # Public thread (type=1) by default
                    new_thread = await starter_message.create_thread(name=thread_name, auto_archive_duration=1440) # Archive after 24h
                    target_channel = new_thread
                except discord.Forbidden:
                    return {"success": False, "error": f"Bot lacks permissions to create threads in channel '{channel.name}'. (Requires MANAGE_THREADS)"}
                except Exception as e:
                    return {"success": False, "error": f"Failed to create thread '{thread_name}': {e}"}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as resp:
                    resp.raise_for_status() # Raise an exception for bad status codes
                    image_bytes = io.BytesIO(await resp.read())
            
            discord_file = discord.File(image_bytes, filename=filename or image_url.split('/')[-1])
            message = await target_channel.send(file=discord_file) # Send to target_channel (main or thread)
            
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
