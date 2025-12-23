# utils/embed_parser.py
import json
import logging
from typing import List, Union, Any
import discord
from domain.game_data import get_class_emoji, get_class_color
from schemas.db_schemas import CharacterClassEnum

logger = logging.getLogger(__name__)

def serialize_embeds(embeds: List[discord.Embed]) -> str:
    """Serialize Discord Embed objects to JSON string."""
    try:
        embeds_data = [embed.to_dict() for embed in embeds]
        return json.dumps(embeds_data, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error serializing embeds: {e}")
        raise ValueError(f"Error serializing embeds: {str(e)}")

def parse_embed_json(embed_json: str) -> List[discord.Embed]:
    """Parse JSON string into Discord Embed objects."""
    try:
        data = json.loads(embed_json)
        if isinstance(data, dict):
            embeds_data = [data]
        elif isinstance(data, list):
            embeds_data = data
        else:
            raise ValueError("Embed JSON must be an object or array")

        embeds = []
        for embed_data in embeds_data:
            embed = discord.Embed.from_dict(embed_data)
            embeds.append(embed)
        return embeds
    except Exception as e:
        logger.error(f"Error parsing embed: {e}")
        raise ValueError(f"Error parsing embed: {str(e)}")

def create_simple_embed(title: str, description: str, color: discord.Color = discord.Color.blue()) -> discord.Embed:
    return discord.Embed(title=title, description=description, color=color)

def stylize_name(name: str) -> str:
    # Unicode Mathematical Bold mapping
    bold_map = {
        'A': '𝐀', 'B': '𝐁', 'C': '𝐂', 'D': '𝐃', 'E': '𝐄', 'F': '𝐅', 'G': '𝐆', 'H': '𝐇',
        'I': '𝐈', 'J': '𝐉', 'K': '𝐊', 'L': '𝐋', 'M': '𝐌', 'N': '𝐍', 'O': '𝐎', 'P': '𝐏',
        'Q': '𝐐', 'R': '𝐑', 'S': '𝐒', 'T': '𝐓', 'U': '𝐔', 'V': '𝐕', 'W': '𝐖', 'X': '𝐗',
        'Y': '𝐘', 'Z': '𝐙',
        'a': '𝐚', 'b': '𝐛', 'c': '𝐜', 'd': '𝐝', 'e': '𝐞', 'f': '𝐟', 'g': '𝐠', 'h': '𝐡',
        'i': '𝐢', 'j': '𝐣', 'k': '𝐤', 'l': '𝐥', 'm': '𝐦', 'n': '𝐧', 'o': '𝐨', 'p': '𝐩',
        'q': '𝐪', 'r': '𝐫', 's': '𝐬', 't': '𝐭', 'u': '𝐮', 'v': '𝐯', 'w': '𝐰', 'x': '𝐱',
        'y': '𝐲', 'z': '𝐳'
    }
    return ''.join(bold_map.get(c, c) for c in name)

def truncate_field(text: str, max_length: int = 1024) -> str:
    if not text: return ""
    if len(text) <= max_length: return text
    return text[:max_length - 3] + "..."

def split_quotes(quotes: str) -> List[str]:
    if not quotes: return []
    if "|" in quotes:
        quote_list = [q.strip() for q in quotes.split("|") if q.strip()]
    else:
        quote_list = [q.strip() for q in quotes.split("\n") if q.strip()]
    return quote_list[:3]

def build_character_embeds(character: Any) -> List[discord.Embed]:
    """
    Build character sheet. Accepts Pydantic model (CharacterCreate/InDB) or SQLAlchemy object.
    """
    embeds = []

    # Handle Class Name (Enum or String)
    # Pydantic field is 'class_name', SQLAlchemy is 'class_name'
    char_class = getattr(character, "class_name", "Unknown")
    if hasattr(char_class, "value"): # Enum
        char_class_str = char_class.value
    else:
        char_class_str = str(char_class)

    # Handle Race (Enum or String)
    char_race = getattr(character, "race", "Unknown")
    if hasattr(char_race, "value"):
        char_race_str = char_race.value
    else:
        char_race_str = str(char_race)

    # Handle Roles (List of Enum/String)
    roles = getattr(character, "roles", [])
    roles_str = ""
    if roles:
        # Pydantic or SQL Array
        role_list = []
        for r in roles:
            if hasattr(r, "value"): role_list.append(r.value)
            else: role_list.append(str(r))
        roles_str = ", ".join(role_list)
    else:
        roles_str = "None"

    # Handle Professions (List of String)
    profs = getattr(character, "professions", [])
    profs_str = ", ".join(profs) if profs else "None"

    emoji = get_class_emoji(char_class_str)
    color = get_class_color(char_class_str)

    # Embed 1: Quick Reference
    quick_ref = discord.Embed(title=f"{emoji} {stylize_name(character.name)}", color=color)
    if character.portrait_url:
        quick_ref.set_thumbnail(url=character.portrait_url)

    quick_ref.add_field(
        name="━━━━━━━━━━━━━━━━━━━━",
        value=(
            f"**Race:** {char_race_str}\n"
            f"**Class:** {char_class_str}\n"
            f"**Role:** {roles_str}\n"
            f"**Professions:** {profs_str}"
        ),
        inline=False
    )

    if character.trait_1 and character.trait_2 and character.trait_3:
        traits_display = f"⚡ {character.trait_1} • {character.trait_2} • {character.trait_3} ⚡"
        quick_ref.add_field(name="━━━━━━━━━━━━━━━━━━━━", value=traits_display, inline=False)

    quick_ref.set_footer(text="Azeroth Bound • Character Registry")
    embeds.append(quick_ref)

    # Embed 2: Lore
    lore_embed = discord.Embed(color=color)
    lore_embed.add_field(name="📜 Backstory", value=truncate_field(character.backstory), inline=False)
    
    if character.personality:
        lore_embed.add_field(name="✨ Personality", value=truncate_field(character.personality), inline=False)
    
    embeds.append(lore_embed)

    # Embed 3: Quotes
    if character.quotes:
        quotes_list = split_quotes(character.quotes)
        if quotes_list:
            quotes_embed = discord.Embed(title="💬 Memorable Quotes", color=color)
            for i, quote in enumerate(quotes_list, 1):
                quotes_embed.add_field(name=f"Quote {i}", value=f"*\"{truncate_field(quote)}\"*", inline=False)
            embeds.append(quotes_embed)

    return embeds

def build_cemetery_embed(character_name: str, char_class: str) -> discord.Embed:
    embed = discord.Embed(
        title=f"⚰️ {stylize_name(character_name)}",
        description=(
            f"*Here rests {character_name}, whose tale has reached its end.*\n\n"
            f"May their deeds echo through the ages,\n"
            f"and may the Light embrace them in eternal rest."
        ),
        color=0x4A4A4A
    )
    embed.add_field(name="Status", value="**FALLEN**", inline=True)
    embed.add_field(name="Class", value=f"{get_class_emoji(char_class)} {char_class}", inline=True)
    embed.set_footer(text="Azeroth Bound • The Cemetery")
    return embed