import asyncio
import json
import csv
import re
from playwright.async_api import async_playwright, Response
from bs4 import BeautifulSoup

OUTPUT_DIR = "data"
TALENTS_JSON_PATH = f"{OUTPUT_DIR}/talents_turtle_wow.json"
TALENTS_CSV_PATH = f"{OUTPUT_DIR}/talents_turtle_wow.csv"
TALENT_TREES_JSON_PATH = f"{OUTPUT_DIR}/talent_trees_turtle_wow.json"
TALENT_TREES_CSV_PATH = f"{OUTPUT_DIR}/talent_trees_turtle_wow.csv"

BASE_URL = "https://talent-builder.haaxor1689.dev/c/1.18.1"
ICONS_BASE_URL = "https://talent-builder.haaxor1689.dev/icons/"

# Updated CLASSES based on the notes, including full talent tree structures
# This will be used to guide the scraping and for deriving 'tree' and 'tier'
TALENT_NOTES = {
    "WARRIOR": {
        "ARMS": {
            "background_image_url": "https://i.imgur.com/dG8sqvo.jpeg",
            "tiers": [
                ["Improved Heroic Strike", "Tactical Mastery", "Improved Rend"],
                ["Improved Charge", "Deflection", "Improved Thunder Clap"],
                ["Master Strike", "Improved Overpower", "Deep Wounds"],
                ["Two-Handed Weapon Specialization", "Impale"],
                ["Master of Arms", "Sweeping Strikes", "Precision Cut", "Improved Disciplines"],
                ["Improved Slam", "Boundless Anger"],
                ["Mortal Strike"]
            ]
        },
        "FURY": {
            "background_image_url": "https://i.imgur.com/zksnzOE.jpeg",
            "tiers": [
                ["Booming Voice", "Cruelty"],
                ["Dual-Wield Specialization", "Unbridled Wrath"],
                ["Improved Shouts", "Piercing Howl", "Blood Craze"],
                ["Battlefield Mobility", "Enrage", "Improved Pummel"],
                ["Improved Whirlwind", "Death Wish", "Improved Execute"],
                ["Improved Berserker Rage", "Flurry", "Blood Drinker"],
                ["Bloodthirst"]
            ]
        },
        "PROTECTION": {
            "background_image_url": "https://i.imgur.com/nBFGuoD.jpeg",
            "tiers": [
                ["Improved Bloodrage", "Shield Specialization", "Anticipation"],
                ["Iron Will", "Toughness"],
                ["Last Stand", "Improved Intervene", "Improved Taunt", "Improved Revenge"], # Corrected typo here
                ["Gag Order", "Improved Disarm", "Defiance"],
                ["One-Handed Weapon Specialization", "Shieldslam", "Improved Shield Slam", "Reprisal"],
                ["Improved Shield Wall", "Defensive Tactics"],
                ["Concussion Blow"]
            ]
        }
    },
    "PALADIN": {
        "HOLY": {
            "background_image_url": "https://i.imgur.com/JP8Gl2N.jpeg",
            "tiers": [
                ["Divine Strength", "Divine Intellect"],
                ["Holy Judgement", "Spiritual Focus", "Improved Seal Of Righteousness"],
                ["Healing Light", "Sanctity Aura", "Improved Lay On Hands", "Unyielding Faith"],
                ["Improved Concentration Aura", "Illumination", "Ironclad"],
                ["Divine Favor", "Holy Shock"],
                ["Holy Power", "Blessed Strikes"],
                ["Daybreak"]
            ]
        },
        "PROTECTION": {
            "background_image_url": "https://i.imgur.com/tXyypuW.jpeg",
            "tiers": [
                ["Improved Devotion Aura", "Redoubt"],
                ["Precision", "Guardian's Favor", "Toughness"],
                ["Improved Righteous Fury", "Blessing of Sanctuary", "Shield Specialization", "Anticipation"], # Corrected typo
                ["Improved Hand of Reckoning", "Improved Hammer of Justice"],
                ["Righteous Defense", "Holy Shield", "Reckoning"],
                ["Righteous Strikes"],
                ["Bulwark of the Righteous"]
            ]
        },
        "RETRIBUTION": {
            "background_image_url": "https://i.imgur.com/13blQWM.jpeg",
            "tiers": [
                ["Improved Blessings", "Benediction"],
                ["Improved Judgement", "Improved Seal of The Crusader", "Deflection"],
                ["Improved Retribution Aura", "Conviction", "Blessing of Kings", "Pursuit of Justice"],
                ["Two-Handed Weapon Specialization", "Vindication"],
                ["Eye for an Eye", "Vengeance", "Seal Of Command"],
                ["Vengeful Strikes"],
                ["Repentance"]
            ]
        }
    },
    "HUNTER": {
        "BEAST MASTERY": {
            "background_image_url": "https://i.imgur.com/9IDZKjk.jpeg",
            "tiers": [
                ["Swift Aspects", "Endurance Training"],
                ["Improved Eyes Of The Beast", "Improved Primal Aspects", "Thick Hide", "Improved Revive Pet"],
                ["Pathfinding", "Coordinated Assault", "Unleashed Fury"],
                ["Bestial Discipline", "Improved Mend Pet", "Ferocity"],
                ["Intimidation", "Kill Command", "Bestial Precision"],
                ["Spirit Bond", "Frenzy"],
                ["Baited Shot"]
            ]
        },
        "MARKSMANSHIP": {
            "background_image_url": "https://i.imgur.com/imOT6iL.jpeg",
            "tiers": [
                ["Improved Concussive Shot", "Efficiency"],
                ["Improved Stings", "Lethal Shots", "Hawk Eye", "Improved Scorpid Sting"],
                ["Steady Shot", "Improved Hunter's Mark", "Swiftshot"],
                ["Mortal Shots", "Scatter Shot", "Barrage"],
                ["Piercing Shots", "Improved Steady Shot", "Endless Quiver"],
                ["Ranged Weapon Specialization", "Trueshot Aura", "Improved Slaying", "Resourcefulness"],
                ["Swift Reflexes"]
            ]
        },
        "SURVIVAL": {
            "background_image_url": "https://i.imgur.com/cehCppw.jpeg",
            "tiers": [
                ["Entrapment", "Savage Strikes"],
                ["Improved Wing Clip", "Planning Ahead", "Survivalist"],
                ["Carve", "Deterrence", "Stinging Nettle"],
                ["Surefooted", "Improved Feign Death", "Killer Instinct"],
                ["Trap Mastery", "Lacerate", "Vicious Strikes"],
                ["Lightning Reflexes", "Untamed Trapper"]
            ]
        }
    },
    "ROGUE": {
        "ASSASSINATION": {
            "background_image_url": "https://i.imgur.com/wdMMU0H.jpeg",
            "tiers": [
                ["Improved Eviscerate", "Remorseless Attacks", "Malice"],
                ["Ruthlessness", "Murder", "Improved Blade Tactics"],
                ["Relentless Strikes", "Throwing Weapon Specialization", "Lethality"],
                ["Taste for Blood", "Vile Poisons", "Improved Poisons"],
                ["Efficient Poisons", "Envenom", "Cold Blood"],
                ["Vigor", "Seal Fate", "Noxious Assault"],
                ["Opportunity"]
            ]
        },
        "COMBAT": {
            "background_image_url": "https://i.imgur.com/YwK1PZa.jpeg",
            "tiers": [
                ["Lightning Reflexes", "Deflection"],
                ["Improved Backstab", "Precision", "Riposte"],
                ["Improved Sprint", "Setup", "Improved Kick"],
                ["Concussive Blows", "Dual Wield Specialization", "Close Quarters Combat"],
                ["Surprise Attack", "Hack and Slash", "Weapon Expertise"],
                ["Blade Rush", "Aggression", "Adrenaline Rush"],
                ["Camouflage"]
            ]
        },
        "SUBTLETY": {
            "background_image_url": "https://i.imgur.com/MCiw1vw.jpeg",
            "tiers": [
                ["Improved Expose Armor", "Improved Gouge"],
                ["Improved Ambush", "Elusiveness", "Serrated Blades"],
                ["Initiative", "Improved Ghostly Strike", "Smoke Bomb"],
                ["Hemorrhage", "Cloaked in Shadows", "Blackjack"],
                ["Blinding Haze", "Dirty Deeds", "Preparation"],
                ["Shadow of Death", "Bloody Mess", "Honor Among Thieves"],
                ["Tricks of the Trade", "Mark for Death"]
            ]
        }
    },
    "PRIEST": {
        "DISCIPLINE": {
            "background_image_url": "https://i.imgur.com/jb539sB.jpeg",
            "tiers": [
                ["Wand Specialization", "Piercing Light"],
                ["Mental Agility", "Silent Resolve", "Unbreakable Will"],
                ["Blessed Concentration", "Improved Power Word: Fortitude", "Improved Inner Fire"],
                ["Inner Focus", "Improved Power Word: Shield", "Meditation"],
                ["Searing Light", "Purifying Flames", "Mental Strength"],
                ["Enlighten", "Resurgent Shield", "Force of Will"],
                ["Chastise"]
            ]
        },
        "HOLY": {
            "background_image_url": "https://i.imgur.com/Ff4JPx7.jpeg",
            "tiers": [
                ["Improved Renew", "Holy Focus"],
                ["Divinity", "Divine Fury", "Spell Warding"],
                ["Holy Reach", "Blessed Recovery", "Inspiration"],
                ["Holy Nova", "Swift Recovery", "Improved Healing"],
                ["Spiritual Guidance", "Spirit of Redemption", "Reservoir of Light"],
                ["Spiritual Healing", "Proclaim Champion"]
            ]
        },
        "SHADOW": {
            "background_image_url": "https://i.imgur.com/WdvVXDq.jpeg",
            "tiers": [
                ["Spirit Tap", "Blackout"],
                ["Shadow Affinity", "Improved Shadow Word: Pain", "Shadow Focus"],
                ["Improved Psychic Scream", "Improved Mind Blast", "Mind Flay"],
                ["Improved Mana Burn", "Improved Fade", "Shadow Reach"],
                ["Shadow Weaving", "Silence", "Vampiric Embrace"],
                ["Vampiric Touch", "Darkness", "Shadowform"]
            ]
        }
    },
    "SHAMAN": {
        "ELEMENTAL": {
            "background_image_url": "https://i.imgur.com/tZhxnJZ.jpeg",
            "tiers": [
                ["Convection", "Concussion"],
                ["Earth's Grasp", "Elemental Warding", "Elemental Devastation"],
                ["Elemental Focus", "Reverberation", "Call of Thunder"],
                ["Improved Molten Blast", "Improved Fire Totems", "Eye of the Storm"],
                ["Call of Flame", "Storm Reach", "Elemental Mastery"],
                ["Elemental Fury", "Lightning Mastery", "Earthquake"]
            ]
        },
        "ENHANCEMENT": {
            "background_image_url": "https://i.imgur.com/l5mMLXR.jpeg",
            "tiers": [
                ["Ancestral Knowledge", "Shield Specialization"],
                ["Totemic Alignment", "Thundering Strikes", "Stable Shields"],
                ["Improved Ghost Wolf", "Calming Winds", "Lightning Strike"],
                ["Ancestral Guardian", "Flurry", "Spirit Armor"],
                ["Enhancing Totems", "Elemental Weapons", "Stormstrike"],
                ["Element's Grace", "Bloodlust"]
            ]
        },
        "RESTORATION": {
            "background_image_url": "https://i.imgur.com/92yXUuM.jpeg",
            "tiers": [
                ["Improved Healing Wave", "Tidal Focus"],
                ["Improved Reincarnation", "Ancestral Healing", "Tidal Mastery"],
                ["Healing Way", "Healing Focus", "Totemic Mastery"],
                ["Nature's Grace", "Restorative Totems", "Improved Water Shield"],
                ["Tidal Surge", "Ancestral Swiftness", "Undertow"],
                ["Improved Chain Heal", "Spirit Link"]
            ]
        }
    },
    "MAGE": {
        "ARCANE": {
            "background_image_url": "https://i.imgur.com/jEEi4Sm.jpeg",
            "tiers": [
                ["Arcane Subtlety", "Magic Absorption"],
                ["Improved Arcane Missiles", "Wand Specialization", "Arcane Focus"],
                ["Arcane Concentration", "Magic Attunement", "Arcane Impact"],
                ["Arcane Rupture", "Improved Mana Shield", "Improved Counterspell"],
                ["Temporal Convergence", "Arcane Meditation", "Arcane Instability"],
                ["Presence of Mind", "Accelerated Arcana", "Arcane Potency"],
                ["Resonance Cascade", "Arcane Power"]
            ]
        },
        "FIRE": {
            "background_image_url": "https://i.imgur.com/stbVfwD.jpeg",
            "tiers": [
                ["Improved Fireball", "Impact"],
                ["Ignite", "Flame Throwing", "Improved Fire Blast"],
                ["Incinerate", "Improved Flamestrike", "Pyroblast"],
                ["Burning Soul", "Fire Vulnerability", "Improved Fire Ward"],
                ["Master of Elements", "Blast Wave", "Critical Mass"],
                ["Hot Streak", "Fire Power", "Combustion"]
            ]
        },
        "FROST": {
            "background_image_url": None, # Missing in notes
            "tiers": [
                ["Frost Warding", "Improved Frostbolt", "Elemental Precision"],
                ["Piercing Ice", "Frostbite", "Improved Frost Nova"],
                ["Permafrost", "Ice Shards", "Cold Snap"],
                ["Improved Blizzard", "Arctic Reach", "Frost Channeling"],
                ["Shatter", "Ice Block", "Icicles"],
                ["Improved Cone of Cold", "Winter's Chill", "Flash Freeze"],
                ["Ice Barrier"]
            ]
        }
    },
    "WARLOCK": {
        "AFFLICTION": {
            "background_image_url": "https://i.imgur.com/95rcgS7.jpeg",
            "tiers": [
                ["Suppression", "Improved Corruption", "Sinister Pursuit"],
                ["Improved Curse of Weakness", "Resilient Shadows", "Improved Life Tap"],
                ["Improved Drains", "Improved Curse of Agony", "Fel Concentration"],
                ["Curse of Exhaustion", "Grim Reach", "Nightfall"],
                ["Soul Siphon", "Rapid Deterioration", "Siphon Life"],
                ["Improved Curse of Exhaustion", "Malediction", "Shadow Mastery"],
                ["Dark Harvest"]
            ]
        },
        "DEMONOLOGY": {
            "background_image_url": "https://i.imgur.com/ntFjD9G.jpeg",
            "tiers": [
                ["Master Conjuror", "Demonic Embrace"],
                ["Soul Entrapment", "Soul Funnel", "Demonic Aegis"],
                ["Fel Intellect", "Fel Domination", "Fel Stamina"],
                ["Demonic Sacrifice", "Improved Stones", "Master Summoner"],
                ["Nether Studies", "Unholy Power", "Power Overwhelming"],
                ["Demonic Precision", "Master Demonologist", "Unleashed Potential"],
                ["Soul Link"]
            ]
        },
        "DESTRUCTION": {
            "background_image_url": "https://i.imgur.com/S8X1OtI.jpeg",
            "tiers": [
                ["Shadow Vulnerability", "Cataclysm", "Demonic Swiftness"],
                ["Bane", "Aftermath", "Intensity"],
                ["Shadowburn", "Devastation", "Pyroclasm"],
                ["Destructive Reach", "Improved Searing Pain", "Improved Soul Fire"],
                ["Improved Immolate", "Ruin", "Emberstorm"],
                ["Conflagrate"]
            ]
        }
    },
    "DRUID": {
        "BALANCE": {
            "background_image_url": "https://i.imgur.com/Ob3ScSl.jpeg",
            "tiers": [
                ["Improved Wrath", "Nature's Grasp", "Improved Nature's Grasp"],
                ["Sylvan Blessing", "Guidance of the Dream", "Improved Moonfire"],
                ["Natural Weapons", "Natural Shapeshifter", "Moonfury"],
                ["Omen of Clarity", "Nature's Reach", "Vengeance"],
                ["Moonglow", "Owlkin Frenzy", "Moonkin Form"],
                ["Nature's Grace", "Improved Starfire", "Balance of All Things"],
                ["Gale Winds", "Eclipse"]
            ]
        },
        "FERAL COMBAT": {
            "background_image_url": "https://i.imgur.com/TQZ5NPN.jpeg",
            "tiers": [
                ["Ferocity", "Feral Aggression"],
                ["Feral Instinct", "Brutal Impact", "Thick Hide"],
                ["Open Wounds", "Feral Swiftness", "Feral Charge"],
                ["Sharpened Claws", "Primal Fury", "Predatory Strikes"],
                ["Blood Frenzy", "Improved Shred", "Ancient Brutality"],
                ["Berserk", "Heart of the Wild", "Carnage"],
                ["Leader of the Pack"]
            ]
        },
        "RESTORATION": {
            "background_image_url": "https://i.imgur.com/ElJPrb1.jpeg",
            "tiers": [
                ["Improved Mark of the Wild", "Furor"],
                ["Improved Healing Touch", "Nature's Focus", "Subtlety"],
                ["Swiftmend", "Genesis", "Reflection"],
                ["Gift of Nature", "Tranquil Spirit", "Aessina's Bloom"],
                ["Nature's Swiftness", "Preservation", "Improved Regrowth"],
                ["Improved Tranquility", "Tree of Life Form"]
            ]
        }
    }
}


def normalize_talent_name(name: str) -> str:
    """Normalizes a talent name for consistent matching."""
    if name is None:
        return ""
    # Convert to lowercase, remove all non-alphanumeric characters (including hyphens and spaces)
    return re.sub(r'[^\w]', '', name).lower()

async def scrape_talents():
    all_talents = []
    all_talent_trees = [] # To store metadata for each talent tree
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True) # Go headless again once name matching is solid
        page = await browser.new_page()

        # Iterate through all classes in TALENT_NOTES
        for class_name_key, class_data in TALENT_NOTES.items():
            class_name = class_name_key.lower()
            
            # Store background image URLs and create talent tree metadata
            for tree_name_key, tree_details in class_data.items():
                if isinstance(tree_details, dict) and "background_image_url" in tree_details:
                    talent_tree_id = f"{class_name}_{tree_name_key.lower()}"
                    all_talent_trees.append({
                        "id": talent_tree_id,
                        "class": class_name_key,
                        "tree_name": tree_name_key,
                        "background_image_url": tree_details["background_image_url"]
                    })
                
            url = f"{BASE_URL}/{class_name}"
            print(f"Navigating to {url}")
            await page.goto(url, wait_until="networkidle", timeout=60000) 

            await page.wait_for_timeout(5000)

            html_content = await page.content()
            soup = BeautifulSoup(html_content, 'html.parser')
            
            talent_elements = soup.find_all('button', class_='group')
            
            talents_found_in_dom = []

            Y_OFFSET_START = 3
            X_OFFSET_START = 0
            GRID_STEP = 80

            for button in talent_elements:
                style_attr = button.get('style')
                x_pos, y_pos = None, None
                if style_attr:
                    match_transform = re.search(r'translate3d\(([-\d\.]+)px,\s*([-\d\.]+)px,', style_attr)
                    if match_transform:
                        x_pos = float(match_transform.group(1))
                        y_pos = float(match_transform.group(2))
                
                talent_tier = None
                talent_column = None

                if y_pos is not None:
                    talent_tier = round((y_pos - Y_OFFSET_START) / GRID_STEP) + 1
                    talent_tier = max(1, talent_tier)

                if x_pos is not None:
                    talent_column = round((x_pos - X_OFFSET_START) / GRID_STEP) + 1
                    talent_column = max(1, talent_column)

                icon_img = button.find('img')
                if icon_img and icon_img.get('src'):
                    icon_src = icon_img['src']
                    tooltip_div = button.find_next_sibling('div', class_='tw-surface')
                    
                    if tooltip_div:
                        talent_name_tag = tooltip_div.find('h4', class_='tw-color')
                        rank_tag = tooltip_div.find('p', class_='font-bold')
                        description_tag = tooltip_div.find('p', class_='whitespace-pre-wrap')

                        talent_name = talent_name_tag.text.strip() if talent_name_tag else None
                        description = description_tag.text.strip() if description_tag else None
                        
                        max_rank = 1
                        if rank_tag:
                            match_rank = re.search(r'\d+/\s*(\d+)', rank_tag.text)
                            if match_rank:
                                max_rank = int(match_rank.group(1))

                        if talent_name:
                            raw_talent = {
                                "name": talent_name,
                                "icon": icon_src,
                                "ranks": max_rank,
                                "description": description,
                                "talentTree": None,
                                "row": talent_tier,
                                "column": talent_column,
                                "prereqTalent": None
                            }
                            talents_found_in_dom.append(raw_talent)

            print(f"Found {len(talents_found_in_dom)} potential talents in DOM for {class_name}.")
            
            # After populating raw_talent["row"] from HTML, now match to TALENT_NOTES for tree verification
            for raw_talent in talents_found_in_dom:
                talent_name = raw_talent["name"]
                normalized_extracted_name = normalize_talent_name(talent_name)
                
                found_match_in_notes = False
                for tree_name_key, tree_details in class_data.items():
                    if tree_name_key == "background_image_url": # Skip metadata
                        continue
                    
                    tier_lists_from_notes = tree_details.get("tiers", [])
                    
                    for current_tier_idx, talents_in_current_tier in enumerate(tier_lists_from_notes):
                        current_tier_from_notes = current_tier_idx + 1 # Convert 0-indexed to 1-indexed tier
                        for noted_talent_name in talents_in_current_tier:
                            normalized_noted_name = normalize_talent_name(noted_talent_name)
                            if normalized_extracted_name == normalized_noted_name:
                                raw_talent["talentTree"] = tree_name_key # Assign actual tree name
                                # Prefer HTML-derived tier, but if unavailable, use tier from notes
                                if raw_talent["row"] is None:
                                    raw_talent["row"] = current_tier_from_notes
                                found_match_in_notes = True
                                break
                        if found_match_in_notes:
                            break
                    if found_match_in_notes:
                        break
                
                if not found_match_in_notes:
                    normalized_notes_for_class_list = []
                    for tree_name_debug, tree_data_debug in class_data.items():
                        if tree_name_debug == "background_image_url":
                            continue
                        for tier_list_debug in tree_data_debug.get("tiers", []):
                            for tn_debug in tier_list_debug:
                                normalized_notes_for_class_list.append(normalize_talent_name(tn_debug))

                    print(f"WARNING: Talent '{talent_name}' (Normalized: '{normalized_extracted_name}') not found in TALENT_NOTES for {class_name_key}.")
                    # print(f"  Attempted matches for (normalized TALENT_NOTES): {sorted(list(set(normalized_notes_for_class_list)))}") # Temporarily disable to reduce verbosity
                    raw_talent["talentTree"] = class_name_key.capitalize() # Default to class name
            
            for raw_talent in talents_found_in_dom:


                processed_talent = process_raw_talent_data(raw_talent, class_name)
                if processed_talent:
                    all_talents.append(processed_talent)
            
            if not talents_found_in_dom:
                print(f"No talents data found in DOM for {class_name}.")


        await browser.close()
    
    return all_talents, all_talent_trees

def process_raw_talent_data(raw_talent: dict, class_name: str) -> dict | None:
    """Processes a raw talent dictionary into the desired schema."""
    talent_name = raw_talent.get("name")
    if not talent_name:
        return None

    talent_tree = raw_talent.get("talentTree")
    if talent_tree is None:
        print(f"WARNING: Talent tree not found for '{talent_name}'. Defaulting to '{class_name.capitalize()}'")
        talent_tree = class_name.capitalize()
    
    # Use the normalized talent_tree name for sanitization
    talent_tree_sanitized = normalize_talent_name(talent_tree)

    talent_id = f"{class_name.lower()}_{talent_tree_sanitized}_{normalize_talent_name(talent_name)}"

    tier = raw_talent.get("row")
    column = raw_talent.get("column")

    # Corrected points_req formula: (tier-1)*5
    points_req = ((tier - 1) * 5) if isinstance(tier, int) and tier > 0 else 0

    prereq_name = raw_talent.get("prereqTalent")
    prerequisite_id = None
    if prereq_name is not None:
        if isinstance(prereq_name, int):
            prerequisite_id = str(prereq_name)
        else:
            prerequisite_id = f"{class_name.lower()}_{talent_tree_sanitized}_{normalize_talent_name(str(prereq_name))}"
    
    tree_background_url = raw_talent.get("tree_background_url", None)

    icon_name = raw_talent.get("icon", "")
    full_icon_url = ""
    if icon_name:
        if not (icon_name.startswith("http://") or icon_name.startswith("https://")):
            full_icon_url = f"https://talent-builder.haaxor1689.dev{icon_name}"
        else:
            full_icon_url = icon_name

    return {
        "id": talent_id,
        "name": talent_name,
        "tree": talent_tree,
        "tier": tier,
        "column": column,
        "max_rank": raw_talent.get("ranks", 1),
        "description": raw_talent.get("description", ""),
        "icon_url": full_icon_url,
        "prerequisite": prerequisite_id,
        "points_req": points_req,
        "tree_background_url": tree_background_url # Include the background image URL
    }

def save_to_json(data: list[dict], file_path: str):
    """Saves the data to a JSON file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Data saved to {file_path}")

def save_to_csv(data: list[dict], file_path: str):
    """Saves the data to a CSV file."""
    if not data:
        print("No data to save to CSV.")
        return

    all_keys = set()
    for item in data:
        all_keys.update(item.keys())
    fieldnames = list(all_keys)
    
    with open(file_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"Data saved to {file_path}")

if __name__ == "__main__":
    import os
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    talents, talent_trees = asyncio.run(scrape_talents())
    if talents:
        save_to_json(talents, TALENTS_JSON_PATH)
        save_to_csv(talents, TALENTS_CSV_PATH)
    else:
        print("No talents data scraped.")
    
    if talent_trees:
        save_to_json(talent_trees, TALENT_TREES_JSON_PATH)
        save_to_csv(talent_trees, TALENT_TREES_CSV_PATH)
    else:
        print("No talent tree metadata scraped.")