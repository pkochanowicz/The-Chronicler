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
Domain Models
Data classes and types for character submissions.
"""
from dataclasses import dataclass
from typing import Optional, Dict
from datetime import datetime

# Status Enums
STATUS_PENDING = "PENDING"
STATUS_REGISTERED = "REGISTERED"
STATUS_REJECTED = "REJECTED"
STATUS_DECEASED = "DECEASED"
STATUS_BURIED = "BURIED"
STATUS_RETIRED = "RETIRED"

@dataclass
class ClassMetadata:
    """Metadata for a WoW character class."""

    name: str
    emoji: str
    color_hex: str
    forum_tag: Optional[str] = None

    def get_color_int(self) -> int:
        """Convert hex color to integer for Discord embeds."""
        return int(self.color_hex.replace("#", ""), 16)


# Classic+ class metadata registry
CLASS_DATA: Dict[str, ClassMetadata] = {
    "Warrior": ClassMetadata("Warrior", "⚔️", "#C69B6D", "Warrior"),
    "Paladin": ClassMetadata("Paladin", "🛡️", "#F48CBA", "Paladin"),
    "Hunter": ClassMetadata("Hunter", "🏹", "#AAD372", "Hunter"),
    "Rogue": ClassMetadata("Rogue", "🗡️", "#FFF468", "Rogue"),
    "Priest": ClassMetadata("Priest", "✨", "#FFFFFF", "Priest"),
    "Shaman": ClassMetadata("Shaman", "🌩️", "#0070DD", "Shaman"),
    "Mage": ClassMetadata("Mage", "🔮", "#3FC7EB", "Mage"),
    "Warlock": ClassMetadata("Warlock", "👹", "#8788EE", "Warlock"),
    "Druid": ClassMetadata("Druid", "🌿", "#FF7C0A", "Druid"),
}

def get_class_metadata(class_name: str) -> Optional[ClassMetadata]:
    """
    Get metadata for a character class.

    Args:
        class_name: Name of the class (case-insensitive)

    Returns:
        ClassMetadata if found, None otherwise
    """
    for key, value in CLASS_DATA.items():
        if key.lower() == class_name.lower():
            return value
    return None

def get_class_emoji(class_name: str) -> str:
    """Get emoji for a character class."""
    metadata = get_class_metadata(class_name)
    return metadata.emoji if metadata else "📜"

def get_class_color(class_name: str) -> int:
    """Get Discord color integer for a character class."""
    metadata = get_class_metadata(class_name)
    return metadata.get_color_int() if metadata else 0x808080


@dataclass
class Character:
    """Represents a character entry in the registry (27-column schema)."""

    # Identity
    discord_user_id: str  # discord_id column
    discord_name: str     # discord_name column
    
    # Character Data
    name: str             # char_name column
    race: str
    char_class: str       # class column (mapped to char_class)
    roles: str            # Comma-separated
    professions: str      # Comma-separated
    backstory: str
    personality: str = ""
    quotes: str = ""
    portrait_url: str = ""
    
    # Traits
    trait_1: str = ""
    trait_2: str = ""
    trait_3: str = ""
    
    # Talents
    talents: Dict[str, int] = field(default_factory=dict) # {talent_name: ranks_spent}
    
    # Lifecycle
    status: str = STATUS_PENDING
    confirmation: bool = False
    request_sdxl: bool = False
    
    # Approval
    recruitment_msg_id: str = ""
    forum_post_url: str = ""
    reviewed_by: str = ""
    embed_json: str = ""
    
    # Death
    death_cause: str = ""
    death_story: str = ""
    
    # Timestamps
    timestamp: Optional[datetime] = None  # Original submission time
    registered_at: Optional[datetime] = None # When registered/approved
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Admin
    notes: str = ""
    
    def get_portrait_prompt(self) -> Optional[str]:
        """
        Generates a prompt for an AI image generator if no portrait URL is provided.
        The prompt is based on the character's race, class, and physical description.
        """
        if self.portrait_url:
            return None

        prompt_parts = [
            f"A portrait of a {self.race} {self.char_class},",
            "in the style of World of Warcraft concept art.",
        ]

        description = ""
        if self.personality:
            description += f"Personality: {self.personality}. "
        if self.trait_1:
            description += f"Traits: {self.trait_1}, {self.trait_2}, {self.trait_3}. "
        
        if description:
            prompt_parts.append(f"Physical and character description: {description.strip()}")

        return " ".join(prompt_parts)

    def to_dict(self) -> dict:
        """Convert to dictionary for Google Sheets (partial, or full if needed by services)."""
        # This is a helper, though SheetsService typically constructs the row.
        return {
            "discord_id": self.discord_user_id,
            "char_name": self.name,
            # ... add others if needed by internal logic
        }
