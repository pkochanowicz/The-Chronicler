# 📖 The Chronicler's User Guide

**Version 2.0 - The Ascension**

Greetings, hero. This tome serves as your guide to interacting with **The Chronicler**, the arcane construct that manages our guild's records.

---

## 🖋️ Character Registration

To join the ranks of Azeroth Bound, you must inscribe your name in the archives.

**Command:** `/register_character`

### The Ritual
1. **Introduction:** Chronicler Thaldrin will greet you. You can choose to link your Discord identity or remain anonymous.
2. **Identity:** Enter your character's full name.
3. **Heritage:** Choose your **Race** (e.g., Human, Dwarf, Orc, Undead).
4. **Calling:** Choose your **Class** (e.g., Warrior, Mage, Druid).
5. **Roles:** Select your combat roles (Tank, Healer, Melee DPS, etc.).
6. **Crafts:** (Optional) Select your professions.
7. **Traits:** Enter 3 defining traits (e.g., "Brave", "Stubborn", "Kind").
8. **The Tale:** Write your backstory (max 1024 chars).
9. **Visage:** Upload a portrait image directly to the chat!
10. **Confirmation:** Review your character sheet and confirm.

**Note:** Your registration is private until approved by an officer.

---

## 🏦 The Guild Bank

The guild bank is open for business!

### Depositing Items
Have spare loot?
**Command:** `/bank deposit [item] [quantity] [category] [notes]`
*Example:* `/bank deposit "Linen Cloth" 20 "Material" "Farmed in Westfall"`

### Checking Your Stash
See what you've contributed.
**Command:** `/bank mydeposits`

### Viewing the Vault
See what's available for withdrawal.
**Command:** `/bank view`

### Withdrawing Items
Found something you need? (Requires Officer approval IRL usually, but technically open)
**Command:** `/bank withdraw [item_id]`
*(Get the Item ID from `/bank view` or `/bank mydeposits`)*

---

## ⚔️ Talent Audits

Ensure your build follows the Classic+ laws.

**Command:** `/talent audit [character_name] [level] [talents_json]`

*Example JSON:* `{"Improved Heroic Strike": 3, "Tactical Mastery": 5}`

The Chronicler will check:
- Are these valid talents for your class?
- Do you have enough points at your level?
- Have you met the prerequisites?
- Are you trying to cheat the tiers?

---

## ⚰️ The Rite of Remembrance

*For Officers Only*

When a hero falls, we honor them.

**Command:** `/bury`

This solemn interactive ceremony will:
1. Identify the fallen hero.
2. Record the cause of death.
3. Allow for a final eulogy.
4. Move their record to the **#cemetery**.
5. Notify the guild of their passing.

---

*For the Guild! For the Code!*