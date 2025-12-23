# domain/game_data.py
from typing import Dict, Optional
from dataclasses import dataclass

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
    for key, value in CLASS_DATA.items():
        if key.lower() == class_name.lower():
            return value
    return None

def get_class_emoji(class_name: str) -> str:
    metadata = get_class_metadata(class_name)
    return metadata.emoji if metadata else "📜"

def get_class_color(class_name: str) -> int:
    metadata = get_class_metadata(class_name)
    return metadata.get_color_int() if metadata else 0x808080
