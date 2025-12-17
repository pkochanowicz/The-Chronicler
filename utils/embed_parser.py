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
Embed Parser
Utilities for parsing and creating Discord embeds from JSON data.
"""
import json
import logging
from typing import List, Optional
import discord
from domain.models import Character, get_class_emoji, get_class_color

logger = logging.getLogger(__name__)


def serialize_embeds(embeds: List[discord.Embed]) -> str:
    """
    Serialize Discord Embed objects to JSON string.

    Converts embeds to their dictionary representation and serializes
    as a JSON array. This JSON can be stored as the canonical source
    of truth and later deserialized with parse_embed_json().

    Args:
        embeds: List of Discord Embed objects

    Returns:
        JSON string containing embed data (array of objects)

    Example:
        >>> embeds = build_character_embeds(character)
        >>> json_str = serialize_embeds(embeds)
        >>> # Later...
        >>> restored_embeds = parse_embed_json(json_str)
    """
    try:
        # Convert each embed to dictionary using Discord's to_dict method
        embeds_data = [embed.to_dict() for embed in embeds]

        # Serialize to JSON string
        return json.dumps(embeds_data, ensure_ascii=False)

    except Exception as e:
        logger.error(f"Error serializing embeds: {e}")
        raise ValueError(f"Error serializing embeds: {str(e)}")


def parse_embed_json(embed_json: str) -> List[discord.Embed]:
    """
    Parse JSON string into Discord Embed objects.

    The JSON should be either:
    - A single embed object
    - An array of embed objects

    Args:
        embed_json: JSON string containing embed data

    Returns:
        List of Discord Embed objects

    Raises:
        ValueError: If JSON is invalid or cannot be parsed
    """
    try:
        data = json.loads(embed_json)

        # Handle both single embed and array of embeds
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

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in embed data: {e}")
        raise ValueError(f"Invalid JSON: {str(e)}")
    except Exception as e:
        logger.error(f"Error parsing embed: {e}")
        raise ValueError(f"Error parsing embed: {str(e)}")


def create_simple_embed(
    title: str,
    description: str,
    color: discord.Color = discord.Color.blue()
) -> discord.Embed:
    """
    Create a simple Discord embed.

    Args:
        title: Embed title
        description: Embed description
        color: Embed color (default: blue)

    Returns:
        Discord Embed object
    """
    return discord.Embed(
        title=title,
        description=description,
        color=color
    )


def create_error_embed(
    title: str,
    description: str,
    error_type: str = "warning"
) -> discord.Embed:
    """
    Create a lore-flavored error embed.

    Args:
        title: Error title
        description: Error description
        error_type: "warning" (amber) or "error" (red)

    Returns:
        Discord Embed object
    """
    color = 0xFFA500 if error_type == "warning" else 0xFF0000

    embed = discord.Embed(
        title=f"⚠️ {title}",
        description=description,
        color=color
    )
    embed.set_footer(text="Azeroth Bound • The Chroniclers reject this entry")

    return embed


def stylize_name(name: str) -> str:
    """
    Apply Unicode styling to character names for a more cinematic feel.
    Uses mathematical bold characters for emphasis.

    Args:
        name: Character name

    Returns:
        Styled name string
    """
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
    """
    Truncate text to fit Discord field limits.

    Args:
        text: Text to truncate
        max_length: Maximum length (default: 1024 for embed fields)

    Returns:
        Truncated text with ellipsis if needed
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def split_quotes(quotes: str) -> List[str]:
    """
    Split quotes string into individual quotes (max 3).

    Args:
        quotes: Raw quotes string (newline or pipe-separated)

    Returns:
        List of individual quotes
    """
    if not quotes:
        return []

    # Try pipe separator first, then newlines
    if "|" in quotes:
        quote_list = [q.strip() for q in quotes.split("|") if q.strip()]
    else:
        quote_list = [q.strip() for q in quotes.split("\n") if q.strip()]

    # Limit to 3 quotes
    return quote_list[:3]


def build_character_embeds(character: Character) -> List[discord.Embed]:
    """
    Build multi-embed character sheet for a registered character.

    Creates up to 3 embeds:
    1. Quick Reference (header, stats, at-a-glance)
    2. Lore (backstory, personality)
    3. Quotes (optional, if quotes provided)

    Args:
        character: Character model instance

    Returns:
        List of Discord embeds (2-3 embeds)
    """
    embeds = []

    # Get class styling
    emoji = get_class_emoji(character.char_class)
    color = get_class_color(character.char_class)

    # Embed 1: Quick Reference
    quick_ref = discord.Embed(
        title=f"{emoji} {stylize_name(character.name)}",
        color=color
    )

    # Set thumbnail to portrait
    if character.portrait_url:
        quick_ref.set_thumbnail(url=character.portrait_url)

    # Header info
    quick_ref.add_field(
        name="━━━━━━━━━━━━━━━━━━━━",
        value=(
            f"**Race:** {character.race}\n"
            f"**Class:** {character.char_class}\n"
            f"**Role:** {character.role}\n"
            f"**Professions:** {character.professions}"
        ),
        inline=False
    )

    quick_ref.set_footer(text="Azeroth Bound • Character Registry")
    embeds.append(quick_ref)

    # Embed 2: Lore
    lore_embed = discord.Embed(color=color)

    # Backstory
    backstory = truncate_field(character.backstory, 1024)
    lore_embed.add_field(
        name="📜 Backstory",
        value=backstory,
        inline=False
    )

    # Personality
    personality = truncate_field(character.personality, 1024)
    lore_embed.add_field(
        name="✨ Personality",
        value=personality,
        inline=False
    )

    embeds.append(lore_embed)

    # Embed 3: Quotes (optional)
    if character.quotes:
        quotes_list = split_quotes(character.quotes)
        if quotes_list:
            quotes_embed = discord.Embed(
                title="💬 Memorable Quotes",
                color=color
            )

            for i, quote in enumerate(quotes_list, 1):
                quote_text = truncate_field(quote, 1024)
                quotes_embed.add_field(
                    name=f"Quote {i}",
                    value=f"*\"{quote_text}\"*",
                    inline=False
                )

            embeds.append(quotes_embed)

    return embeds


def build_cemetery_embed(character_name: str, char_class: str) -> discord.Embed:
    """
    Build ceremonial embed for buried characters.

    Args:
        character_name: Name of the fallen character
        char_class: Character's class

    Returns:
        Discord Embed with cemetery styling
    """
    embed = discord.Embed(
        title=f"⚰️ {stylize_name(character_name)}",
        description=(
            f"*Here rests {character_name}, whose tale has reached its end.*\n\n"
            f"May their deeds echo through the ages,\n"
            f"and may the Light embrace them in eternal rest."
        ),
        color=0x4A4A4A  # Gray
    )

    embed.add_field(
        name="Status",
        value="**FALLEN**",
        inline=True
    )

    embed.add_field(
        name="Class",
        value=f"{get_class_emoji(char_class)} {char_class}",
        inline=True
    )

    embed.set_footer(text="Azeroth Bound • The Cemetery")

    return embed
