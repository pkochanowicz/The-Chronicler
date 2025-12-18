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
Validators for domain models and fields.
"""
from typing import List, Optional
import re
from domain.models import CLASS_DATA

class ValidationError(Exception):
    """Raised when validation fails."""
    pass

VALID_RACES = [
    # Alliance
    "Human", "Dwarf", "Night Elf", "Gnome", "High Elf",
    # Horde
    "Orc", "Undead", "Tauren", "Troll", "Goblin",
    # Special/Rare
    "Other"
]

VALID_CLASSES = list(CLASS_DATA.keys())

VALID_ROLES = [
    "Tank",
    "Healer",
    "Melee DPS",
    "Ranged DPS",
    "Support"
]

VALID_PROFESSIONS = [
    "Alchemy",
    "Blacksmithing",
    "Enchanting",
    "Engineering",
    "Herbalism",
    "Leatherworking",
    "Mining",
    "Skinning",
    "Tailoring",
    "Jewelcrafting",
    "First Aid",
    "Cooking",
    "Fishing",
    "Survival"
]

def validate_race(race: str) -> bool:
    """Validate race is in the allowed list."""
    if race not in VALID_RACES:
        raise ValidationError(f"Invalid race: {race}. Must be one of: {', '.join(VALID_RACES)}")
    return True

def validate_class(char_class: str) -> bool:
    """Validate class is in the allowed list."""
    # CLASS_DATA keys match VALID_CLASSES
    if char_class not in CLASS_DATA:
         raise ValidationError(f"Invalid class: {char_class}. Must be one of: {', '.join(VALID_CLASSES)}")
    return True

def validate_roles(roles: List[str]) -> bool:
    """Validate roles list (min 1, all valid)."""
    if not roles:
        raise ValidationError("At least one role must be selected.")
    
    for role in roles:
        if role not in VALID_ROLES:
            raise ValidationError(f"Invalid role: {role}. Must be one of: {', '.join(VALID_ROLES)}")
    return True

def validate_professions(professions: List[str]) -> bool:
    """Validate professions list (all valid, can be empty).

    Enforces World of Warcraft profession limits:
    - Maximum 2 primary professions (gathering/crafting)
    - Maximum 4 secondary professions (utility)

    Per TECHNICAL.md:
    Primary: Alchemy, Blacksmithing, Enchanting, Engineering,
             Herbalism, Leatherworking, Mining, Skinning,
             Tailoring, Jewelcrafting
    Secondary: First Aid, Cooking, Fishing, Survival
    """
    # Define profession categories
    PRIMARY_PROFESSIONS = {
        "Alchemy", "Blacksmithing", "Enchanting", "Engineering",
        "Herbalism", "Leatherworking", "Mining", "Skinning",
        "Tailoring", "Jewelcrafting"
    }

    SECONDARY_PROFESSIONS = {
        "First Aid", "Cooking", "Fishing", "Survival"
    }

    # Validate each profession exists
    for prof in professions:
        if prof not in VALID_PROFESSIONS:
            raise ValidationError(f"Invalid profession: {prof}. Must be one of: {', '.join(VALID_PROFESSIONS)}")

    # Count professions by category
    primary_count = sum(1 for p in professions if p in PRIMARY_PROFESSIONS)
    secondary_count = sum(1 for p in professions if p in SECONDARY_PROFESSIONS)

    # Enforce limits
    if primary_count > 2:
        primary_selected = [p for p in professions if p in PRIMARY_PROFESSIONS]
        raise ValidationError(
            f"Cannot have more than 2 primary professions. "
            f"Selected {primary_count}: {', '.join(primary_selected)}"
        )

    if secondary_count > 4:
        secondary_selected = [p for p in professions if p in SECONDARY_PROFESSIONS]
        raise ValidationError(
            f"Cannot have more than 4 secondary professions. "
            f"Selected {secondary_count}: {', '.join(secondary_selected)}"
        )

    return True

def validate_url(url: str) -> bool:
    """Validate URL format (http/https)."""
    if not url:
        return True # Empty URL is often allowed as optional, or handled by default
        
    regex = re.compile(
        r'^https?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' # domain...
        r'localhost|' # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    if not re.match(regex, url):
        raise ValidationError(f"Invalid URL format: {url}")
    return True

def sanitize_input(text: str) -> str:
    """
    Sanitize input string.
    
    - Trims leading/trailing whitespace.
    - Preserves apostrophes (O'Brien).
    - Prevents basic injection/formatting issues (implementation details depend on threat model).
    
    For this context, we mainly ensure it's a clean string.
    """
    if not text:
        return ""
    
    # Strip whitespace
    sanitized = str(text).strip()
    
    # Additional sanitization can be added here if needed (e.g. escaping HTML/Markdown)
    
    return sanitized

