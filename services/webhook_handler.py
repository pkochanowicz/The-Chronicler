# services/webhook_handler.py
import logging
import json
from aiohttp import web
from config.settings import get_settings
from utils.embed_parser import parse_embed_json, build_cemetery_embed
from services.character_service import CharacterService
from db.database import get_engine_and_session_maker
import discord
from views.officer_view import OfficerControlView
from models.pydantic_models import CharacterUpdate

logger = logging.getLogger(__name__)

bot = None


async def health_handler(request):
    return web.Response(text="OK", status=200)


async def start_webhook_server(discord_bot):
    global bot
    bot = discord_bot
    app = web.Application()
    app.router.add_post("/webhook", handle_webhook)
    app.router.add_get("/health", health_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", get_settings().PORT)  # nosec B104
    await site.start()
    logger.info(f"Webhook server started on port {get_settings().PORT}")


async def handle_webhook(request):
    try:
        data = await request.json()
    except json.JSONDecodeError:
        return web.Response(status=400, text="Invalid JSON")

    if data.get("secret") != get_settings().WEBHOOK_SECRET:
        logger.warning("Invalid webhook secret attempt")
        return web.Response(status=400, text="Invalid secret")

    trigger = data.get("trigger")
    character = data.get("character")

    if not trigger:
        return web.Response(status=400, text="Missing trigger")

    if trigger == "POST_TO_RECRUITMENT":
        await handle_post_to_recruitment(character)
    elif trigger == "INITIATE_BURIAL":
        await handle_initiate_burial(character)
    else:
        return web.Response(status=400, text="Unknown trigger")

    return web.Response(status=200, text="OK")


async def handle_post_to_recruitment(character_data, discord_bot=None):
    bot_instance = discord_bot or bot
    if not bot_instance:
        logger.error("Bot not initialized")
        return

    try:
        channel_id = get_settings().RECRUITMENT_CHANNEL_ID
        channel = bot_instance.get_channel(
            channel_id
        ) or await bot_instance.fetch_channel(channel_id)

        embed_json = character_data.get("embed_json", [])
        if isinstance(embed_json, str):
            embeds = parse_embed_json(embed_json)
        elif isinstance(embed_json, list):
            embeds = [discord.Embed.from_dict(d) for d in embed_json]
        else:
            embeds = []

        mentions = []
        if get_settings().PATHFINDER_ROLE_MENTION:
            mentions.append(get_settings().PATHFINDER_ROLE_MENTION)
        if get_settings().TRAILWARDEN_ROLE_MENTION:
            mentions.append(get_settings().TRAILWARDEN_ROLE_MENTION)

        char_name = character_data.get("name") or character_data.get("char_name")
        discord_name = character_data.get("discord_username") or character_data.get(
            "discord_name"
        )
        content = f"New Character Registration: {char_name} ({discord_name})\n{' '.join(mentions)}"

        message = None
        if isinstance(channel, discord.ForumChannel):
            thread_name = f"[PENDING] {char_name}"
            thread_with_message = await channel.create_thread(
                name=thread_name, content=content, embed=embeds[0] if embeds else None
            )
            message = thread_with_message.message
            if len(embeds) > 1:
                await thread_with_message.thread.send(embeds=embeds[1:])
        else:
            message = await channel.send(content=content, embeds=embeds)
            if hasattr(message, "create_thread"):
                await message.create_thread(name=f"Discussion: {char_name}")

        char_id = character_data.get("id")
        if char_id:
            view = OfficerControlView(bot_instance, int(char_id))
            await message.edit(view=view)

            # Update DB with recruitment message ID if needed
            _, session_maker = get_engine_and_session_maker()
            async with session_maker() as session:
                service = CharacterService(session)
                await service.update_character(
                    int(char_id), CharacterUpdate(recruitment_msg_id=message.id)
                )

        logger.info(f"✅ Recruitment post created for {char_name}, msg_id={message.id}")

    except Exception as e:
        logger.error(f"Error in handle_post_to_recruitment: {e}", exc_info=True)


async def handle_initiate_burial(character_data):
    if not bot:
        logger.error("Bot not initialized")
        return

    try:
        url = character_data.get("forum_post_url", "")
        thread_id = None

        # Try to parse ID from dummy URL "dummy/123" or full discord URL
        if url:
            parts = url.split("/")
            if parts:
                try:
                    thread_id = int(parts[-1])
                except ValueError:
                    pass

        if not thread_id:
            # Try to get from forum_post_id field directly if passed
            thread_id = character_data.get("forum_post_id")

        if not thread_id:
            logger.error("No forum post ID found for burial")
            # We can still post to cemetery, just can't lock the old thread

        vault_thread = None
        if thread_id:
            try:
                vault_thread = bot.get_channel(
                    int(thread_id)
                ) or await bot.fetch_channel(int(thread_id))
            except Exception:
                logger.warning(f"Could not fetch vault thread {thread_id}")

        cemetery_channel = bot.get_channel(
            get_settings().CEMETERY_CHANNEL_ID
        ) or await bot.fetch_channel(get_settings().CEMETERY_CHANNEL_ID)

        char_name = character_data.get("char_name") or character_data.get("name")
        char_class = character_data.get("class") or character_data.get("class_name")
        if hasattr(char_class, "value"):
            char_class = char_class.value

        cemetery_embed = build_cemetery_embed(char_name, str(char_class))

        cemetery_thread_msg = await cemetery_channel.create_thread(
            name=f"⚰️ {char_name}",
            content=f"**Here rests {char_name}, whose tale has reached its end.**",
            embed=cemetery_embed,
        )

        embed_json = character_data.get("embed_json", [])
        if isinstance(embed_json, str):
            original_embeds = parse_embed_json(embed_json)
        elif isinstance(embed_json, list):
            original_embeds = [discord.Embed.from_dict(d) for d in embed_json]
        else:
            original_embeds = []

        if original_embeds:
            await cemetery_thread_msg.thread.send(embeds=original_embeds)

        death_story = character_data.get("death_story", "Fell in battle.")
        if death_story:
            await cemetery_thread_msg.thread.send(
                content=f"**The End of a Legend**\n\n{death_story}"
            )

        if vault_thread:
            try:
                await vault_thread.edit(archived=True, locked=True)
            except Exception as e:
                logger.warning(f"Could not archive vault thread: {e}")

        # Notify Owner
        user_id = character_data.get("discord_user_id") or character_data.get(
            "discord_id"
        )
        if user_id:
            try:
                user = bot.get_user(int(user_id)) or await bot.fetch_user(int(user_id))
                await user.send(
                    f"⚰️ Your character **{char_name}** has been laid to rest in the Cemetery."
                )
            except Exception as e:
                logger.warning(f"Failed to DM user: {e}")

        await cemetery_thread_msg.thread.send(
            "@everyone A hero has fallen. Pay your respects."
        )
        logger.info(f"Burial ceremony completed for {char_name}")

    except Exception as e:
        logger.error(f"Error in handle_initiate_burial: {e}", exc_info=True)
