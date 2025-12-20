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
Webhook Handler
Handles incoming webhooks from Google Apps Script.
"""
import logging
import json
import asyncio
from aiohttp import web
from config.settings import settings
from utils.embed_parser import parse_embed_json, build_cemetery_embed
from services.sheets_service import CharacterRegistryService
from datetime import datetime

logger = logging.getLogger(__name__)

bot = None
registry = None

def get_registry():
    global registry
    if not registry:
        registry = CharacterRegistryService()
    return registry

async def health_handler(request):
    """Health check endpoint for Fly.io and other platforms."""
    return web.Response(text="OK", status=200)

async def start_webhook_server(discord_bot):
    """Start the aiohttp webhook server."""
    global bot
    bot = discord_bot
    app = web.Application()
    app.router.add_post('/webhook', handle_webhook)
    app.router.add_get('/health', health_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', settings.PORT)
    await site.start()
    logger.info(f"Webhook server started on port {settings.PORT}")

async def handle_webhook(request):
    """Handle incoming webhook requests."""
    try:
        data = await request.json()
    except json.JSONDecodeError:
        return web.Response(status=400, text="Invalid JSON")

    if data.get("secret") != settings.WEBHOOK_SECRET:
        logger.warning("Invalid webhook secret attempt")
        return web.Response(status=400, text="Invalid secret")

    trigger = data.get("trigger")
    character = data.get("character")
    
    if not trigger:
        return web.Response(status=400, text="Missing trigger")

    logger.info(f"Received webhook trigger: {trigger}")

    if trigger == "POST_TO_RECRUITMENT":
        await handle_post_to_recruitment(character)
    elif trigger == "INITIATE_BURIAL":
        await handle_initiate_burial(character)
    else:
        return web.Response(status=400, text="Unknown trigger")

    return web.Response(status=200, text="OK")

async def handle_post_to_recruitment(character_data):
    """
    Handle POST_TO_RECRUITMENT trigger.
    """
    if not bot:
        logger.error("Bot not initialized")
        return

    try:
        channel_id = settings.RECRUITMENT_CHANNEL_ID
        channel = bot.get_channel(channel_id) or await bot.fetch_channel(channel_id)
        
        embed_json = character_data.get("embed_json", "[]")
        embeds = parse_embed_json(embed_json)
        
        mentions = []
        if settings.PATHFINDER_ROLE_MENTION:
            mentions.append(settings.PATHFINDER_ROLE_MENTION)
        if settings.TRAILWARDEN_ROLE_MENTION:
            mentions.append(settings.TRAILWARDEN_ROLE_MENTION)
            
        content = f"New Character Registration: {character_data.get('char_name')} ({character_data.get('discord_name')})\n{' '.join(mentions)}"
        
        message = await channel.send(content=content, embeds=embeds)

        await message.add_reaction(settings.APPROVE_EMOJI)
        await asyncio.sleep(0.5)  # 500ms delay to avoid burst rate limits
        await message.add_reaction(settings.REJECT_EMOJI)
        
        # Update sheets with msg ID
        get_registry().update_character_status(
            character_data.get("char_name"),
            character_data.get("status"), # Keep existing status
            recruitment_msg_id=str(message.id)
        )
        
        try:
            user_id = int(character_data.get("discord_id", 0))
            if user_id:
                user = bot.get_user(user_id) or await bot.fetch_user(user_id)
                await user.send(f"Your character **{character_data.get('char_name')}** has been submitted for review!")
        except Exception as e:
            logger.warning(f"Failed to DM user: {e}")

    except Exception as e:
        logger.error(f"Error in handle_post_to_recruitment: {e}")

async def handle_initiate_burial(character_data):
    """
    Handle INITIATE_BURIAL trigger.
    Moves character from Character Vault to Cemetery with full ceremony.
    """
    if not bot:
        logger.error("Bot not initialized")
        return

    try:
        # 1. Get original vault thread
        url = character_data.get("forum_post_url", "")
        thread_id = None
        if url:
            try:
                thread_id = int(url.split("/")[-1])
            except ValueError:
                logger.error(f"Invalid forum URL format: {url}")
                return

        if not thread_id:
            logger.error("No forum post URL found for burial")
            return

        vault_thread = bot.get_channel(thread_id) or await bot.fetch_channel(thread_id)

        # 2. Get cemetery forum channel
        cemetery_channel = bot.get_channel(settings.CEMETERY_CHANNEL_ID)
        if not cemetery_channel:
            cemetery_channel = await bot.fetch_channel(settings.CEMETERY_CHANNEL_ID)

        # 3. Create NEW cemetery thread with memorial embed
        char_name = character_data.get("char_name")
        char_class = character_data.get("class", "Unknown")

        cemetery_embed = build_cemetery_embed(char_name, char_class)

        cemetery_thread_msg = await cemetery_channel.create_thread(
            name=f"⚰️ {char_name}",
            content=f"**Here rests {char_name}, whose tale has reached its end.**",
            embed=cemetery_embed
        )

        # 4. Copy original character embeds to cemetery
        embed_json = character_data.get("embed_json", "[]")
        original_embeds = parse_embed_json(embed_json)
        if original_embeds:
            await cemetery_thread_msg.thread.send(embeds=original_embeds)

        # 5. Post death story in cemetery
        death_story = character_data.get("death_story", "Fell in battle.")
        if death_story:
            await cemetery_thread_msg.thread.send(content=f"**The End of a Legend**\n\n{death_story}")

        # 6. Archive old vault thread
        if vault_thread:
            try:
                await vault_thread.edit(archived=True, locked=True)
                logger.info(f"Archived vault thread for {char_name}")
            except Exception as e:
                logger.warning(f"Could not archive vault thread: {e}")

        # 7. Update sheets with new cemetery URL and BURIED status
        get_registry().update_character_status(
            char_name,
            "BURIED",
            forum_post_url=cemetery_thread_msg.thread.jump_url,
            updated_at=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        )

        # 8. Notify character owner via DM
        user_id = character_data.get("discord_id")
        if user_id:
            try:
                user_id = int(user_id)
                user = bot.get_user(user_id) or await bot.fetch_user(user_id)
                await user.send(
                    f"⚰️ Your character **{char_name}** has been laid to rest in the Cemetery.\n"
                    f"Memorial: {cemetery_thread_msg.thread.jump_url}\n\n"
                    f"*May their legend live on in the hearts of those who knew them.*"
                )
            except Exception as e:
                logger.warning(f"Failed to DM user {user_id}: {e}")

        # 9. Notify @everyone in cemetery thread
        await cemetery_thread_msg.thread.send("@everyone A hero has fallen. Pay your respects.")

        logger.info(f"Burial ceremony completed for {char_name}")

    except Exception as e:
        logger.error(f"Error in handle_initiate_burial: {e}", exc_info=True)
