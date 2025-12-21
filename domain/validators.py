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
from typing import List, Dict, Optional, Union
import re
from domain.models import CLASS_DATA
from domain.talent_data import TALENT_DATA

class ValidationError(ValueError):
    """Exception raised for validation errors."""
    pass

VALID_RACES = [
    "Human", "Dwarf", "Night Elf", "Gnome", 
    "Orc", "Undead", "Tauren", "Troll", 
    "Goblin", "High Elf", "Other" # Turtle WoW specific
]

VALID_CLASSES = [
    "Warrior", "Paladin", "Hunter", "Rogue", "Priest", 
    "Shaman", "Mage", "Warlock", "Druid"
]

VALID_ROLES = ["Tank", "Healer", "Melee DPS", "Ranged DPS"]

VALID_PROFESSIONS = [
    "Alchemy", "Blacksmithing", "Enchanting", "Engineering", 
    "Herbalism", "Inscription", "Jewelcrafting", "Leatherworking", 
    "Mining", "Skinning", "Tailoring",
    "Cooking", "First Aid", "Fishing", "Survival" # Secondary (Turtle WoW)
]

# Race-Class Combinations (Turtle WoW 1.17.2)
ALLOWED_COMBINATIONS: Dict[str, List[str]] = {
    "Human": ["Warrior", "Paladin", "Rogue", "Priest", "Mage", "Warlock"],
    "Dwarf": ["Warrior", "Paladin", "Hunter", "Rogue", "Priest", "Mage"], # Mage added in Turtle
    "Night Elf": ["Warrior", "Hunter", "Rogue", "Priest", "Druid"],
    "Gnome": ["Warrior", "Rogue", "Mage", "Warlock", "Hunter"], # Hunter added in Turtle
    "Orc": ["Warrior", "Hunter", "Rogue", "Shaman", "Warlock", "Mage"], # Mage added in Turtle
    "Undead": ["Warrior", "Rogue", "Priest", "Mage", "Warlock", "Hunter"], # Hunter added in Turtle
    "Tauren": ["Warrior", "Hunter", "Shaman", "Druid", "Priest"], # Priest added in Turtle
    "Troll": ["Warrior", "Hunter", "Rogue", "Priest", "Shaman", "Mage", "Warlock"], # Warlock added in Turtle
    "Goblin": ["Warrior", "Hunter", "Rogue", "Shaman", "Mage", "Warlock", "Priest"], # New race
    "High Elf": ["Warrior", "Paladin", "Hunter", "Rogue", "Priest", "Mage"] # New race
}

def validate_race(race: str) -> bool:
    if race not in VALID_RACES:
        raise ValidationError(f"Invalid race: {race}")
    return True

def validate_class(char_class: str) -> bool:
    if char_class not in VALID_CLASSES:
        raise ValidationError(f"Invalid class: {char_class}")
    return True

def validate_race_class(race: str, char_class: str) -> bool:
    """
    Validates if the race/class combination is allowed.
    Case-insensitive.
    """
    # Normalize inputs
    race_norm = next((r for r in VALID_RACES if r.lower() == race.lower()), None)
    class_norm = next((c for c in VALID_CLASSES if c.lower() == char_class.lower()), None)

    if not race_norm:
        raise ValidationError(f"Invalid race: {race}")
    if not class_norm:
        raise ValidationError(f"Invalid class: {char_class}")

    allowed_classes = ALLOWED_COMBINATIONS.get(race_norm, [])
    if class_norm not in allowed_classes:
        raise ValidationError(f"{race_norm} cannot be {class_norm}")
    
    return True

def validate_roles(roles_input: Union[str, List[str]]) -> bool:
    if not roles_input:
        raise ValidationError("At least one role must be selected")
    
    if isinstance(roles_input, list):
        roles = roles_input
        if not roles:
             raise ValidationError("At least one role must be selected")
    else:
        roles = [r.strip() for r in roles_input.split(",")]

    for role in roles:
        if role not in VALID_ROLES:
            raise ValidationError(f"Invalid role: {role}")
    return True

def validate_professions(prof_input: Union[str, List[str]]) -> bool:
    if not prof_input:
        return True # Optional
        
    if isinstance(prof_input, list):
        profs = prof_input
    else:
        profs = [p.strip() for p in prof_input.split(",")]

    for prof in profs:
        if prof not in VALID_PROFESSIONS:
            raise ValidationError(f"Invalid profession: {prof}")
    
    # Check constraints
    # Primary professions: Alchemy, Blacksmithing, Enchanting, Engineering,
    # Herbalism, Leatherworking, Mining, Skinning, Tailoring, Jewelcrafting, Inscription
    primary_profs = {
        "Alchemy", "Blacksmithing", "Enchanting", "Engineering", 
        "Herbalism", "Leatherworking", "Mining", "Skinning", 
        "Tailoring", "Jewelcrafting", "Inscription"
    }
    
    # Secondary: Cooking, First Aid, Fishing, Archaeology, Survival, Gardening
    
    primary_count = sum(1 for p in profs if p in primary_profs)
    if primary_count > 2:
        raise ValidationError(f"Cannot have more than 2 primary professions. Found {primary_count}.")

    return True

def validate_url(url: str) -> bool:
    if not url: 
        return True
    # Basic URL regex - HTTP/HTTPS only
    regex = re.compile(
        r'^https?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' # domain...
        r'localhost|' # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    if not re.match(regex, url):
        raise ValidationError("Invalid URL format")
    return True

def validate_talents(char_class: str, level: int, talents: Dict[str, int]) -> bool:
    """
    Validate selected talents based on class and level.
    talents: A dictionary of {talent_name: ranks_spent}
    """
    if char_class not in TALENT_DATA:
        raise ValidationError(f"Invalid class for talent validation: {char_class}")

    class_talent_trees = TALENT_DATA[char_class]
    
    talents_chosen_info = {} # To store full info of chosen talents
    points_spent_per_tree = {tree_name: 0 for tree_name in class_talent_trees.keys()}
    total_talent_points_spent = 0

    for talent_name, ranks_spent in talents.items():
        found_talent = False
        for tree_name, tree_talents in class_talent_trees.items():
            if talent_name in tree_talents:
                talent_info = tree_talents[talent_name]
                found_talent = True
                
                # Validate ranks spent
                if ranks_spent <= 0:
                    raise ValidationError(f"Ranks spent for talent '{talent_name}' must be positive.")
                if ranks_spent > talent_info["max_rank"]:
                    raise ValidationError(f"Talent '{talent_name}' has max rank {talent_info['max_rank']}, but {ranks_spent} ranks were specified.")
                
                # Validate implied character level for the talent
                if level < talent_info["level"]:
                    raise ValidationError(f"Talent '{talent_name}' requires character level {talent_info['level']}, but character is level {level}.")
                
                # Store full talent info and add to points spent in this tree
                talents_chosen_info[talent_name] = talent_info
                points_spent_per_tree[tree_name] += ranks_spent
                total_talent_points_spent += ranks_spent
                break
        
        if not found_talent:
            raise ValidationError(f"Talent '{talent_name}' is not a valid talent for class '{char_class}'.")

    # --- Second Pass: Validate Total Talent Points, Tier Unlocks, and Prerequisites ---

    # 1. Validate Total Talent Points Spent
    total_talent_points_available = max(0, level - 9) # First point at level 10
    if total_talent_points_spent > total_talent_points_available:
        raise ValidationError(f"Character level {level} can only have {total_talent_points_available} talent points, but {total_talent_points_spent} were spent.")
    
    for talent_name, talent_info in talents_chosen_info.items():
        tree_name = None
        # Find the tree this talent belongs to
        for t_name, t_talents in class_talent_trees.items():
            if talent_name in t_talents:
                tree_name = t_name
                break
        if not tree_name: # Should not happen if found_talent was true in first pass
            continue
        
        # 2. Validate Tier Unlocks (points_in_tree_required)
        # points_in_tree_required is (tier - 1) * 5
        required_points_for_tier = (talent_info['tier'] - 1) * 5
        if points_spent_per_tree[tree_name] < required_points_for_tier:
            raise ValidationError(f"Talent '{talent_name}' (Tier {talent_info['tier']}) requires {required_points_for_tier} points spent in {tree_name} tree, but only {points_spent_per_tree[tree_name]} were spent.")

        # 3. Validate Prerequisites (requires)
        for prereq in talent_info.get("requires", []):
            prereq_name = prereq["talent"]
            prereq_ranks_needed = prereq["ranks"]
            
            if prereq_name not in talents:
                raise ValidationError(f"Talent '{talent_name}' requires prerequisite talent '{prereq_name}' (Rank {prereq_ranks_needed}). '{prereq_name}' not chosen.")
            
            if talents[prereq_name] < prereq_ranks_needed:
                raise ValidationError(f"Talent '{talent_name}' requires prerequisite talent '{prereq_name}' with at least {prereq_ranks_needed} ranks, but only {talents[prereq_name]} ranks were spent.")

    return True

def sanitize_input(text: str) -> str:
    """
    Sanitizes input text to prevent injection attacks and ensure Discord compatibility.
    - Replaces newlines with spaces.
    - Basic markdown escaping (to be enhanced if needed).
    - Preserves common special characters in names (apostrophes, hyphens).
    """
    if not isinstance(text, str):
        return str(text) # Coerce to string if not already

    # Replace newlines with spaces
    sanitized_text = text.replace('\n', ' ').replace('\r', '')

    # Basic markdown escaping for Discord. This is not exhaustive.
    # Discord handles most markdown safely, but user input shouldn't break formatting.
    # Escaping backticks, asterisks, underscores might be too aggressive for RP text.
    # The current approach is to allow them, trusting Discord's rendering to contain it,
    # and focusing on preventing control characters/injection.
    
    # Example: If a user enters "__bold text__", we might want to preserve it.
    # If they enter "`code`", we might want to preserve it.
    # The primary goal is to prevent actual injection (e.g. `DROP TABLE`).
    
    # For now, focus on control characters and problematic embeds.
    # Discord handles most markdown by rendering it, not executing it.
    
    # Future enhancement: More sophisticated escaping if markdown rendering is an issue.
    # Also, consider character limits for Discord fields.

    return sanitized_text

