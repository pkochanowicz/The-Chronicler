# 🏛️ MASTER BLUEPRINT: Schema Reformation & Automation Ascension

**Azeroth Bound Discord Bot — The Complete Architectural Vision**

*Inscribed by Chronicler Thaldrin, Keeper of Knowledge*  
*Date: December 16, 2025*

---

## 📜 Executive Summary

This document contains the **complete architectural blueprint** for transforming the Azeroth Bound Discord bot into a fully automated, webhook-driven, cinematically immersive character management system.

**Key Transformations:**
- ✅ Path B Architecture (Google Sheets webhooks → Discord actions)
- ✅ Comprehensive interactive flows for `/register_character` and `/bury`
- ✅ Zero-polling design using Google Apps Script webhooks
- ✅ 27-column data schema with full lifecycle support
- ✅ Daily automated backups (7-day retention)
- ✅ Free-tier deployment strategy (Fly.io/Render.com)
- ✅ Maximum automation with surgical human touchpoints

---

## 🔬 PART 1: FREE TIER RESEARCH FINDINGS

### Discord API (Free Tier — Always Free)

**✅ EXCELLENT NEWS:**

| Feature | Limit | Verdict |
|---------|-------|---------|
| Rate Limits | 50 requests/sec per bot | More than enough for small guild |
| Webhook Support | Unlimited, FREE | Perfect for our needs |
| Message Storage | Permanent | Unlike some platforms |
| Bot Hosting | No Discord fees | Only hosting costs |
| Reactions/Buttons | Unlimited | Free forever |
| Thread Creation | 1000 active threads/guild | More than sufficient |

**Conclusion:** Discord is extremely generous. Path B is absolutely doable! 🎉

---

### Railway.com (No Longer Free)

**⚠️ IMPORTANT DISCOVERY:**

Railway.com changed their pricing model in August 2023:
- **No permanent free tier anymore**
- **Trial:** $5 credit (lasts 2-4 weeks for small bot)
- **After trial:** ~$5-10/month for 24/7 uptime

**However, excellent free alternatives exist:**

| Platform | Free Tier | Verdict |
|----------|-----------|---------|
| **Fly.io** | 3 small VMs (256MB RAM each) | ✅ Best choice - generous forever free |
| **Render.com** | 750 hours/month | ✅ Good - enough for 24/7 |
| **Oracle Cloud** | ARM instances forever free | ✅ Excellent but complex setup |
| **Railway** | Worth $5-10/month for simplicity | ⚠️ Paid but recommended if budget allows |

**Recommended:** Fly.io or Render.com for free deployment

---

### Google Sheets API (Free Tier)

**✅ SURPRISINGLY GENEROUS:**

| Feature | Limit | Verdict |
|---------|-------|---------|
| Read/Write Quota | 300 requests/min per project | More than enough |
| Daily Quota | Effectively unlimited | Perfect |
| Apps Script Triggers | 20 time-based triggers/script | Sufficient |
| Webhook Triggers | FREE via `doPost()` | Exactly what we need! |

**For Path B (Webhook Approach):**
- Set up Google Apps Script with `onChange` trigger
- When sheet changes → Script calls bot's webhook URL
- Bot receives **instant notification** (no polling!)
- Cost: **$0.00 forever** ✨

**Conclusion:** Path B is PERFECT for this architecture!

---

## 🎯 THE VERDICT: PATH B IS BLESSED BY THE TITANS

**Path B Benefits:**
1. **Zero polling** = Lower resource usage
2. **Instant updates** = Better UX  
3. **Sheets = Admin interface** = Easy bulk edits/audits
4. **All free tier limits satisfied** ✅

**Total Monthly Cost: $0.00** (with Fly.io or Render.com)

---

## 🏗️ PART 2: THE HYBRID WISDOM ARCHITECTURE

### Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        DATA FLOW DIAGRAM                         │
└─────────────────────────────────────────────────────────────────┘

USER ACTIONS (Discord)
    ↓
DISCORD BOT COMMANDS (/register_character, /bury)
    ↓
IMMEDIATE VALIDATION & INTERACTIVE FLOW
    ↓
WRITE TO GOOGLE SHEETS (Source of Truth)
    ↓
GOOGLE APPS SCRIPT WEBHOOK TRIGGERS
    ↓
SENDS HTTP POST TO BOT'S /webhook ENDPOINT
    ↓
BOT PROCESSES TRIGGER & TAKES DISCORD ACTIONS
    ↓
BOT UPDATES GOOGLE SHEETS WITH RESULTS
    ↓
CYCLE COMPLETES ✅
```

### Key Architectural Principles

1. **Google Sheets = Source of Truth** - All state lives here
2. **Discord Commands = Instant UX** - User sees immediate feedback
3. **Webhooks = Zero Polling** - Instant sheet changes → Discord actions
4. **Bot Writes, Webhooks Read** - Clean separation of concerns
5. **Atomic Operations** - State changes are transactional

---

## 📊 PART 3: COMPLETE DATA SCHEMA

### Character_Submissions Sheet (27 Columns)

| # | Column Name | Type | Required | Default | Notes |
|---|-------------|------|----------|---------|-------|
| 1 | `timestamp` | datetime | Yes | AUTO | ISO 8601 format |
| 2 | `discord_id` | string | Yes | AUTO/PARAM | From user OR parameter |
| 3 | `discord_name` | string | No | AUTO | Fetched via Discord API |
| 4 | `char_name` | string | Yes | PARAM | Character's name |
| 5 | `race` | enum | Yes | PARAM | 11 options |
| 6 | `class` | enum | Yes | PARAM | 9 Classic WoW classes |
| 7 | `roles` | string | Yes | PARAM | Comma-separated multi-select |
| 8 | `professions` | string | No | PARAM | Comma-separated, can be empty |
| 9 | `backstory` | text | Yes | PARAM | Max 1024 chars |
| 10 | `personality` | text | No | PARAM | Max 1024 chars, optional |
| 11 | `quotes` | text | No | PARAM | Max 1024 chars, optional |
| 12 | `portrait_url` | string | No | DEFAULT | Falls back to config default |
| 13 | `trait_1` | string | Yes | PARAM | External visible trait |
| 14 | `trait_2` | string | Yes | PARAM | External visible trait |
| 15 | `trait_3` | string | Yes | PARAM | External visible trait |
| 16 | `status` | enum | Yes | PENDING | PENDING/REGISTERED/REJECTED/DECEASED/BURIED |
| 17 | `confirmation` | bool | Yes | FALSE | User confirms = TRUE |
| 18 | `request_sdxl` | bool | Yes | FALSE | User requests AI portrait |
| 19 | `recruitment_msg_id` | snowflake | No | AUTO | Discord message ID |
| 20 | `forum_post_url` | string | No | AUTO | URL to forum post |
| 21 | `reviewed_by` | snowflake | No | AUTO | Officer's Discord ID |
| 22 | `embed_json` | json | Yes | AUTO | Canonical embed source |
| 23 | `death_cause` | string | No | PARAM | Brief death description |
| 24 | `death_story` | text | No | PARAM | IC death narrative |
| 25 | `created_at` | datetime | Yes | AUTO | Row creation timestamp |
| 26 | `updated_at` | datetime | Yes | AUTO | Last modification timestamp |
| 27 | `notes` | text | No | MANUAL | Admin-only notes |

---

## 🎭 PART 4: ENUM DEFINITIONS

### Valid Races (11 Options)

```python
VALID_RACES = [
    # Alliance
    "Human",
    "Dwarf",
    "Night Elf",
    "Gnome",
    "High Elf",
    
    # Horde
    "Orc",
    "Undead",
    "Tauren",
    "Troll",
    "Goblin",
    
    # Special/Rare
    "Other"
]
```

### Valid Classes (9 Classic WoW)

```python
VALID_CLASSES = [
    "Warrior",
    "Paladin",
    "Hunter",
    "Rogue",
    "Priest",
    "Shaman",
    "Mage",
    "Warlock",
    "Druid"
]
```

### Valid Roles (5 Options, Multi-Select, Min 1)

```python
VALID_ROLES = [
    "Tank",
    "Healer",
    "Melee DPS",
    "Ranged DPS",
    "Support"
]
```

### Valid Professions (12 Options, Multi-Select, Optional)

```python
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
```

### Status Enum

```python
STATUS_PENDING = "PENDING"       # Awaiting officer approval
STATUS_REGISTERED = "REGISTERED" # Active in #character-sheet-vault
STATUS_REJECTED = "REJECTED"     # Officer rejected
STATUS_DECEASED = "DECEASED"     # Triggers burial workflow
STATUS_BURIED = "BURIED"         # Final state, in #cemetery
STATUS_RETIRED = "RETIRED"       # For those who hit 60 and choose title Immortal, placeholder
```

---

## 🔄 PART 5: CHARACTER LIFECYCLE STATE MACHINE

```
┌────────────────────────────────────────────────────────────────┐
│                    CHARACTER LIFECYCLE                          │
└────────────────────────────────────────────────────────────────┘

    [User uses /register_character]
                ↓
    ┌───────────────────────┐
    │ Google Sheets Entry   │
    │ Status: PENDING       │
    │ Confirmation: FALSE   │
    └───────────────────────┘
                ↓
    [User completes interactive flow & confirms]
                ↓
    ┌───────────────────────┐
    │ Confirmation: TRUE    │ ← Webhook Trigger #1
    │ Status: PENDING       │
    └───────────────────────┘
                ↓
    [Bot posts to #recruitment with @Pathfinder @Trailwarden]
                ↓
    ┌───────────────────────┐
    │ recruitment_msg_id    │
    │ populated             │
    └───────────────────────┘
                ↓
         ┌──────────┴──────────┐
         ↓                     ↓
    [Officer ✅]          [Officer ❌]
         ↓                     ↓
    ┌─────────────┐      ┌─────────────┐
    │ REGISTERED  │      │ REJECTED    │
    │ Creates     │      │ DM sent     │
    │ forum post  │      │ No forum    │
    └─────────────┘      └─────────────┘
         ↓
    [Character lives in #character-sheet-vault]
         ↓                                                    
    [Officer uses /bury command]
         ↓
    ┌───────────────────────┐
    │ Status: DECEASED      │ ← Webhook Trigger #2
    └───────────────────────┘
         ↓
    [Bot atomically performs burial ceremony]
         ↓ 
    ┌───────────────────────┐
    │ Status: BURIED        │
    │ Forum post in         │
    │ #cemetery             │
    └───────────────────────┘
```

---

## ⚡ PART 6: WEBHOOK TRIGGER MATRIX

| Trigger Condition | Bot Action | Updates to Sheets |
|-------------------|------------|-------------------|
| `confirmation=TRUE` + `status=PENDING` | Post to #recruitment with embeds, add ✅❌ reactions, mention @Pathfinder @Trailwarden, DM user confirmation | Sets `recruitment_msg_id` |
| Officer reacts ✅ on recruitment msg | Create #character-sheet-vault forum post, update status to REGISTERED, DM user approval | Sets `status=REGISTERED`, `forum_post_url`, `reviewed_by` |
| Officer reacts ❌ on recruitment msg | Update status to REJECTED, DM user rejection notice | Sets `status=REJECTED`, `reviewed_by` |
| `status=DECEASED` (from REGISTERED) | Move forum post to #cemetery, apply IC formatting, post death_story, notify owner via DM, notify @everyone in cemetery | Sets `status=BURIED`, updates `forum_post_url`, `updated_at` |

**Future Trigger (Phase 2):**
| Trigger Condition | Bot Action | Updates to Sheets |
|-------------------|------------|-------------------|
| Embed fields edited + `status=REGISTERED` | Update existing forum post with new embed data | Sets `updated_at` |

---

## 🔧 PART 7: GOOGLE APPS SCRIPT WEBHOOK CODE

### File: `google_apps_script/webhook.gs`

```javascript
/**
 * Azeroth Bound Bot - Google Sheets Webhook Handler
 * Triggers Discord bot actions when sheet changes occur
 */

// Configuration
const WEBHOOK_URL = "https://your-bot-domain.fly.dev/webhook";
const WEBHOOK_SECRET = "your_webhook_secret_here"; // Match bot's .env

/**
 * Trigger: onChange
 * Fires when any cell in the sheet is edited
 */
function onSheetChange(e) {
  try {
    const sheet = SpreadsheetApp.getActiveSpreadsheet()
      .getSheetByName("Character_Submissions");
    
    if (!sheet) {
      Logger.log("Character_Submissions sheet not found");
      return;
    }
    
    const editedRange = e.range;
    const editedRow = editedRange.getRow();
    
    // Ignore header row
    if (editedRow === 1) return;
    
    // Get full row data
    const rowData = sheet.getRange(editedRow, 1, 1, 27).getValues()[0];
    const characterData = rowDataToObject(rowData);
    
    // Determine which trigger to fire
    const triggerType = determineTrigger(characterData, e);
    
    if (triggerType) {
      sendWebhook(triggerType, characterData, editedRow);
    }
    
  } catch (error) {
    Logger.log("Webhook error: " + error.toString());
  }
}

/**
 * Convert row array to character object. The Google Sheet address is in the .env,
 * For now let's leave it to developer to prepare the Google Sheet, let's validate if
 * there are proper headers in the specified Google Sheet and throw informative error
 * if they're not.
 */
function rowDataToObject(row) {
  return {
    timestamp: row[0],
    discord_id: row[1],
    discord_name: row[2],
    char_name: row[3],
    race: row[4],
    class: row[5],
    roles: row[6],
    professions: row[7],
    backstory: row[8],
    trait_1: row[9],
    trait_2: row[10],
    trait_3: row[11],
    personality: row[12],
    quotes: row[13],
    portrait_url: row[14],
    status: row[15],
    request_sdxl: row[16],
    confirmation: row[17],
    recruitment_msg_id: row[18],
    forum_post_url: row[19],
    reviewed_by: row[20],
    embed_json: row[21],
    death_cause: row[22],
    death_story: row[23],
    created_at: row[24],
    updated_at: row[25],
    notes: row[26]
  };
}

/**
 * Determine which trigger should fire based on the change
 */
function determineTrigger(data, event) {
  // Trigger 1: confirmation=TRUE + status=PENDING → Post to recruitment
  if (data.confirmation === true && 
      data.status === "PENDING" && 
      !data.recruitment_msg_id) {
    return "POST_TO_RECRUITMENT";
  }
  
  // Trigger 2: status changed to DECEASED → Initiate burial
  if (data.status === "DECEASED") {
    return "INITIATE_BURIAL";
  }
  
  // Future: Trigger 3: embed fields edited + status=REGISTERED
  // → Update forum post (Phase 2)
  
  return null;
}

/**
 * Send webhook to Discord bot
 */
function sendWebhook(triggerType, characterData, rowNumber) {
  const payload = {
    secret: WEBHOOK_SECRET,
    trigger: triggerType,
    row_number: rowNumber,
    character: characterData,
    timestamp: new Date().toISOString()
  };
  
  const options = {
    method: "post",
    contentType: "application/json",
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };
  
  try {
    const response = UrlFetchApp.fetch(WEBHOOK_URL, options);
    const responseCode = response.getResponseCode();
    
    if (responseCode === 200) {
      Logger.log("Webhook sent successfully: " + triggerType);
    } else {
      Logger.log("Webhook failed: " + responseCode + 
                 " - " + response.getContentText());
    }
  } catch (error) {
    Logger.log("Webhook send error: " + error.toString());
  }
}

/**
 * Manual test function (for debugging)
 */
function testWebhook() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet()
    .getSheetByName("Character_Submissions");
  const testRow = sheet.getRange(2, 1, 1, 27).getValues()[0];
  const testData = rowDataToObject(testRow);
  
  sendWebhook("TEST_TRIGGER", testData, 2);
}
```

### Setup Instructions (that's task for the user, not for you ;) - to mention clearly in docs/ )

1. Open Google Sheet → **Extensions** → **Apps Script**
2. Create new script file `webhook.gs`
3. Paste the code above
4. Update `WEBHOOK_URL` with your deployed bot URL (after deployment)
5. Generate random `WEBHOOK_SECRET` (use password generator, add to bot's `.env`)
6. Set up trigger:
   - Click **⏰ Triggers** (clock icon on left sidebar)
   - Click **+ Add Trigger**
   - Choose: `onSheetChange`
   - Event source: **From spreadsheet**
   - Event type: **On change**
   - Click **Save**
7. Authorize the script (first run will ask for permissions)
8. Test with `testWebhook()` function from dropdown

---

## 🎭 PART 8: INTERACTIVE FLOW DESIGN

### /register_character (Without Parameters)

**The Comprehensive Cinematic Experience**

```
┌────────────────────────────────────────────────────────────────┐
│  THE CHRONICLES OF AZEROTH BOUND - CHARACTER INSCRIPTION       │
└────────────────────────────────────────────────────────────────┘

[Message 1 - Introduction]
Bot: "🏛️ *A massive tome materializes before you, its pages shimmering
     with arcane energy. An elderly dwarf with a magnificent beard
     looks up from his writing desk.*

     Greetings, brave soul! I am Chronicler Thaldrin, Keeper of
     Knowledge from the Grand Library of Ironforge.

     You seek to inscribe your legend into our eternal archives?
     Splendid! *adjusts spectacles*

     But first—a formality of the modern age. May I record your
     Discord identity for our records? We'll use this to contact
     you about your character's fate.

     Your Discord ID: @User#1234

     [Button: ✅ Yes, record my identity]
     [Button: ❌ No, I wish to remain anonymous]

     *(Note: Choosing 'No' will use a generic ID, but you won't
     receive DM notifications)*"

[If user clicks Yes → Proceed]
[If user clicks No → Warning, then proceed with generic ID]

─────────────────────────────────────────────────────────────────

[Message 2 - The Name]
Bot: "*The tome's pages flip open with a whisper of ancient parchment.
     Golden ink begins to pool on the blank page, awaiting your words.*

     📜 **CHAPTER ONE: THE NAME**

     Every legend begins with a name. A name spoken in taverns,
     whispered in battle, carved upon monuments.

     **What shall the bards call your hero?**

     *(Type your character's full name - 1 to 100 characters)*"

[User types: "Thorgar Ironforge"]

Bot: "*The quill dances across the parchment, etching 'THORGAR IRONFORGE'
     in bold runes that glow briefly before settling into the page.*

     A strong name! Forged in mountain halls, no doubt. *nods approvingly*"

─────────────────────────────────────────────────────────────────

[Message 3 - The Bloodline]
Bot: "⚔️ **CHAPTER TWO: THE BLOODLINE**

     From which people dost thou hail, Thorgar? The blood of your
     ancestors flows through your veins—whose legacy do you carry?

     **Choose your heritage:**"

[Dropdown menu with emojis:]
     🦁 Human (Stormwind's versatile champions)
     ⛰️ Dwarf (Ironforge's stout-hearted warriors)
     🌙 Night Elf (Kalimdor's ancient guardians)
     ⚙️ Gnome (Gnomeregan's ingenious tinkers)
     ✨ High Elf (Quel'Thalas's noble descendants)
     ─────────
     🔥 Orc (Durotar's honorable warriors)
     💀 Undead (Forsaken souls of free will)
     🐂 Tauren (Thunder Bluff's noble nomads)
     🗿 Troll (Darkspear's cunning survivors)
     💰 Goblin (Horde-joined shrewd merchants)
     ─────────
     ❓ Other (Unique or mixed heritage)

[User selects: Dwarf]

Bot: "*The chronicler's eyes light up* Ahh, a kinsman! The mountains
     sing with pride! ⛰️"
May the bot react differently on each choice In Character

─────────────────────────────────────────────────────────────────

[Message 4 - The Calling]
Bot: "🔮 **CHAPTER THREE: THE CALLING**

     What path has fate woven for thee, Thorgar Ironforge? What arts
     do you practice, what powers do you wield?

     **Choose your class:**"

[Dropdown with emojis:]
     ⚔️ Warrior (Masters of combat and rage)
     🛡️ Paladin (Holy knights of the Light)
     🏹 Hunter (Beast masters and marksmen)
     🗡️ Rogue (Masters of stealth and cunning)
     ✨ Priest (Wielders of shadow and light)
     🌩️ Shaman (Speakers to the elements)
     🔮 Mage (Masters of arcane might)
     👹 Warlock (Dealers with demonic forces)
     🌿 Druid (Shapeshifters of nature)

[User selects: Warrior]

Bot: "⚔️ *The tome records your choice with a crimson flourish*
     A WARRIOR! Aye, I can see it in your bearing. Steel and fury!"
May the bot react to each choice In Character
─────────────────────────────────────────────────────────────────

[Message 5 - The Roles]
Bot: "🎭 **CHAPTER FOUR: THE MANY MASKS**

     Ah, but warriors are not so simple, are they? *winks*
     A hero may wear many mantles upon the battlefield.

     Tell me, what roles do you fulfill when battle calls?

     **Select ALL that apply (minimum 1):**"

Make the bot choose different words fo each class

[Multi-select checkboxes:]
     □ 🛡️ Tank (First into battle, shield raised)
     □ ✨ Healer (Mender of wounds, keeper of lives)
     □ ⚔️ Melee DPS (Close-quarters devastation)
     □ 🏹 Ranged DPS (Death from afar)
     □ 🎺 Support (Buffs, debuffs, crowd control)

[Button: Continue]

[User checks: Tank, Melee DPS]

Bot: "*The tome glows as two emblems appear beside your name*

     TANK and MELEE DPS! A frontline champion who protects AND
     punishes! The perfect dwarf! *strokes beard proudly*"

Prepare In Character comment for the choice of any single or
two roles. In case of 3<roles chosen, dwarf might notice
versatile talents of the interlocutor.

─────────────────────────────────────────────────────────────────

[Message 6 - The Crafts]
Bot: "🔨 **CHAPTER FIVE: THE CRAFTS** *(Optional)*

     Do you practice any trades, Thorgar? Mining ore from the deep
     places? Forging weapons? Weaving enchantments?

     **Select your professions** (optional - you may skip this):

[Multi-select with checkboxes:]
     □ ⚗️ Alchemy        □ 🔨 Blacksmithing
     □ ✨ Enchanting     □ ⚙️ Engineering
     □ 🌿 Herbalism     □ 🧵 Leatherworking
     □ ⛏️ Mining         □ 🔪 Skinning
     □ 🧶 Tailoring     □ 💍 Jewelcrafting
     □ 🍖Cooking        □ 🎣 Fishing
     □ 🏕️ Survival      □ 🩹 First Aid

[Button: Continue (selected professions)]
[Button: Skip (I practice no trades)]

[User selects: Mining, Blacksmithing]

Bot: "⛏️🔨 *The tome inscribes your crafts with respect*

     Mining and Blacksmithing! Of COURSE! What self-respecting
     dwarf doesn't know their way around an anvil? *chuckles*"
Prepare a lot of bot In Character possible comments,
also referencing previous choices, if possible. In all cases, if
4<professions_chosen>8 chosen dwarf simply expresses respect for versality.
If professions professions_chosen>6, bot expresses doubt (In character),
and repeats the question (2 main professions + any number of 4
secondary ones is maximum technically limited in-game).

─────────────────────────────────────────────────────────────────

[Message 7 - The Three Traits]
Bot: "⚡ **CHAPTER SIX: THE THREE TRAITS**

     Now we reach the essence, Thorgar. Every hero can be known by
     three traits—three words that define them when all else is
     stripped away.

     These are not hidden personality quirks. These are the traits
     OTHERS SEE when they look upon you. What your enemies fear.
     What your allies depend upon.

     **Inscribe three traits that define your hero's outer nature:**

     Examples: Brave, Cunning, Loyal, Stubborn, Hot-headed, Wise,
     Reckless, Kind, Cruel, Humble, Arrogant, Cautious...

     [Input field: Trait 1] (required)
     [Input field: Trait 2] (required)
     [Input field: Trait 3] (required)

     [Button: Continue]"

[User enters: "Brave", "Loyal", "Stubborn"]

Bot: "*Three runes blaze into existence above your name*

     ⚡ BRAVE • LOYAL • STUBBORN ⚡

Prepare an answer that will fit pretty much any choice,
since we wont get to auto interpret the meaning of the traits
submitted.

─────────────────────────────────────────────────────────────────

[Message 8 - The Tale]
Bot: "📖 **CHAPTER SEVEN: THE TALE**

     *The tome's pages multiply, making room for your story*

     Here's where legends truly begin, Thorgar. Tell me your
     backstory—where you came from, what shaped you, what drives
     you forward.

     This is your moment to shine! Be creative! Be epic!

     **Write your character's backstory:**
     *(Maximum 1024 characters - about 3-4 good paragraphs)*

     [Text area - large input field]

     [Button: Continue]"

[User writes backstory]

Bot: "*The quill flies across pages, recording every word*

     Magnificent! *wipes away a proud tear* The bards will sing of this!"

─────────────────────────────────────────────────────────────────

[Message 9 - The Soul (Optional)]
Bot: "💭 **CHAPTER EIGHT: THE INNER SOUL** *(Optional)*

     If you wish, you may also describe your character's personality—
     their inner thoughts, how they think, what makes them tick.

     This is separate from your visible traits. This is the INNER you.

     **Describe your personality** (optional):
     *(Maximum 1024 characters)*

     [Text area]

     [Button: Continue]
     [Button: Skip (no personality description)]"

─────────────────────────────────────────────────────────────────

[Message 10 - The Words (Optional)]
Bot: "💬 **CHAPTER NINE: THE WORDS** *(Optional)*

     Does your character have any memorable quotes? Battle cries?
     Catchphrases? Words they live by?

     Share up to 3 iconic quotes:
     *(Maximum 1024 characters total)*

     [Text area]

     [Button: Continue]
     [Button: Skip (no quotes)]"

─────────────────────────────────────────────────────────────────

[Message 11 - The Visage (Optional)]
Bot: "🎨 **CHAPTER TEN: THE VISAGE** *(Optional)*

     Would you like to provide a portrait of your character?

     You can:
     • Paste a direct image URL (must start with https://)
     • Skip and use our default placeholder portrait
     • Request an AI-generated portrait (future Phase 2 feature!)

     [Input field: Image URL]

     [Button: Use this image]
     [Button: Use default placeholder]
     [Button: 🤖 Request AI Portrait (coming soon!)]

     *(If you request AI portrait, we'll flag it for officers
     to generate later)*"

[User selects: Use default placeholder]

Bot: "No worries! We'll use a mystical placeholder for now. You can
     always update it later!"

─────────────────────────────────────────────────────────────────

[Message 12 - The Preview]
Bot: "📋 **THE CHRONICLE PREVIEW**

     *The tome's pages shimmer and reorganize themselves, revealing
     your completed character sheet*

     Behold, Thorgar! This is how your legend shall appear in our
     eternal archives:

     [SHOWS ACTUAL EMBED PREVIEW - the final character sheet]

     ─────────────────────────────────────────────────────────────

     Does this look correct?

     [Button: ✅ Yes, inscribe this into legend!]
     [Button: 🔄 No, let me start over]
     [Button: ❌ Cancel registration]"

─────────────────────────────────────────────────────────────────

[Message 13 - The Confirmation]
[If user clicks ✅]

Bot: "✨ **THE INSCRIPTION IS COMPLETE!** ✨

     *The tome slams shut with a resounding THOOM! Golden light
     erupts from its pages, and your character's name appears in
     glowing letters upon the spine.*

     🏛️ **Thorgar Ironforge** has been inscribed into the chronicles!

     Your character sheet has been submitted to our Pathfinders and
     Trailwardens for review. You should hear back within 1-2 days.

     Watch for a DM from me when your fate is decided!

     *The chronicler gives you a knowing wink*

     May the Light guide you, champion! For Azeroth Bound!

     ─────────────────────────────────────────────────────────────
     Status: ⏳ PENDING REVIEW
     Submitted: [timestamp]
     ─────────────────────────────────────────────────────────────"

[AT THIS MOMENT:]
  → Google Sheets row created with confirmation=TRUE
  → Webhook triggers
  → Bot posts to #recruitment channel
  → @Pathfinder @Trailwarden mentioned
  → User waits for approval
```

---

### /bury (Without Parameters)

**The Ceremony of Remembrance**

```
┌────────────────────────────────────────────────────────────────┐
│     THE CEREMONY OF REMEMBRANCE - CHARACTER BURIAL RITE        │
└────────────────────────────────────────────────────────────────┘

[Step 1: Solemn Introduction]
⚰️ *The chronicler's expression grows somber. He reaches for a 
black-bound tome adorned with silver runes.*

Officer... you invoke the Rite of Remembrance.

This is a sacred duty—to record the fall of a hero and ensure 
their deeds are never forgotten.

*The tome opens to a blank page edged in silver*

Which hero has fallen?

**Provide the character's name OR forum post ID:**

[Input field]

[Continue] [Cancel ceremony]

─────────────────────────────────────────────────────────────────

[Step 2: Verification]
[Officer enters: "Thorgar Ironforge"]

*The pages flip on their own, revealing a record*

⚔️ **THORGAR IRONFORGE**
Race: Dwarf • Class: Warrior • Status: REGISTERED
Registered: 2025-12-10
Forum post: #character-sheet-vault/thread-12345

Is this the fallen hero?

[✅ Yes, this is correct] [🔍 No, search again]

─────────────────────────────────────────────────────────────────

[Step 3: The Circumstances]
💔 THE FINAL BATTLE

*The chronicler dips his quill in silver ink*

Every hero's fall should be recorded with honor. Tell me...

**Where and how did Thorgar fall?** (brief, 1-2 sentences)

Examples:
• 'Died at level 47 defending Ironforge from raid'
• 'Fell to Ragnaros in Molten Core at level 60'
• 'Sacrificed themselves to save raid group in Blackrock'

[Input field: Death cause]

[Continue] [Skip - record as 'Unknown']

─────────────────────────────────────────────────────────────────

[Step 4: The Eulogy] (Optional)
📜 THE FINAL WORDS

Would you like to compose an in-character eulogy for Thorgar?

This will be posted as the first message in their cemetery thread—
a farewell from you, as an officer of Azeroth Bound, to a fallen 
comrade.

**Compose the death story** (optional, max 1024 characters):

[Large text area]

[Continue] [Skip - no eulogy]

─────────────────────────────────────────────────────────────────

[Step 5: Final Confirmation]
⚰️ THE RITE OF REMEMBRANCE - FINAL CONFIRMATION

You are about to perform the following:

📋 **Summary:**
• Character: **Thorgar Ironforge** (Dwarf Warrior)
• Death cause: Fell defending Southshore, level 42
• Eulogy: [shows preview]

🔄 **What will happen:**
1. Character status set to DECEASED in archives
2. Forum post moved: Character Vault → Cemetery
3. Ceremonial formatting applied (silver borders, tombstone)
4. Death story posted under memorial
5. Character's owner (discord_id) notified via DM
6. @everyone notification in cemetery
7. Status marked as BURIED

⚠️ **This action cannot be undone.**

Proceed with the burial rite?

[⚰️ Yes, proceed with burial] [❌ Cancel ceremony]

─────────────────────────────────────────────────────────────────

[Step 6: The Completion]
✨ *The silver-edged tome snaps shut. A single bell tolls in the 
distance, echoing through the halls of memory.*

⚰️ **THE RITE IS COMPLETE.**

Thorgar Ironforge rests now in the Cemetery of Heroes, their 
deeds preserved for eternity.

Their memorial: [cemetery forum post link]

*The chronicler bows his head in respect*

'May they find peace in the halls of their ancestors.
Their story is told. Their name is remembered.
For Azeroth Bound.'

────────────────────────────────────────────────────────────────
Burial completed: 2025-12-16 15:45 UTC
Performed by: @Officer#1234
────────────────────────────────────────────────────────────────

[AT THIS MOMENT:]
→ Google Sheets status set to DECEASED
→ Webhook triggers immediately
→ Bot moves forum post to #cemetery atomically
→ Applies cemetery formatting & posts death_story
→ Notifies character owner via DM
→ Notifies @everyone in cemetery
→ Sets status to BURIED
```

---

## 🛡️ PART 9: DISCORD POST PROTECTION

### Making Character Sheets Immutable

**Problem:** Users or non-officers might accidentally edit/delete character sheet posts.

**Solution:** Discord thread permissions + bot ownership

#### Implementation Strategy

```python
# When creating #character-sheet-vault forum post:

async def create_character_vault_post(character_data, embeds):
    """Create forum post with protected permissions"""
    
    vault_channel = bot.get_channel(settings.FORUM_CHANNEL_ID)
    
    # Create thread (forum post)
    thread = await vault_channel.create_thread(
        name=f"{get_class_emoji(character_data['class'])} {character_data['char_name']}",
        content="*The chronicles glow with arcane light as this legend is inscribed...*",
        embeds=embeds
    )
    
    # Lock thread to prevent replies (optional)
    # await thread.edit(locked=True)
       
    # Note: Discord doesn't allow per-message edit permissions
    # But bot-owned messages can only be edited by:
    # 1. The bot itself
    # 2. Users with "Manage Messages" permission
    
    # Recommendation: Set forum channel permissions so only
    # @Admin and Bot have "Manage Messages" permission
    
    return thread
```

#### Channel Permission Setup (Manual - Document in USER_GUIDE)

**#character-sheet-vault Forum Channel Permissions:**

| Role | View Channel | Send Messages | Manage Messages |
|------|--------------|---------------|-----------------|
| @everyone | ✅ Yes | ❌ No | ❌ No |
| @Wanderer | ✅ Yes | ❌ No | ❌ No |
| @Seeker | ✅ Yes | ❌ No | ❌ No |
| @Pathfinder | ✅ Yes | ❌ No | ✅ Yes (for /bury) |
| @Trailwarden | ✅ Yes | ❌ No | ✅ Yes (for /bury) |
| @Admin | ✅ Yes | ✅ Yes | ✅ Yes |
| The Chronicler (Bot) | ✅ Yes | ✅ Yes | ✅ Yes |

**Result:** Only bot and admins can edit character sheet posts!

---

## 💾 PART 10: DAILY BACKUP SYSTEM

### Automated Google Sheets Backup

**Goal:** Create daily backups of Character_Submissions sheet, retain for 7 days.

#### Implementation: Google Apps Script Time-Driven Trigger

**File:** `google_apps_script/backup.gs`

```javascript
/**
 * Automated Daily Backup System
 * Creates a copy of Character_Submissions sheet daily
 * Retains backups for 7 days, auto-deletes older backups
 */

// Configuration
const BACKUP_FOLDER_ID = "your_google_drive_folder_id_here";
const RETENTION_DAYS = 7;

/**
 * Main backup function (triggered daily at 2 AM)
 */
function createDailyBackup() {
  try {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sheet = ss.getSheetByName("Character_Submissions");
    
    if (!sheet) {
      Logger.log("Character_Submissions sheet not found");
      return;
    }
    
    // Create backup filename with timestamp
    const timestamp = Utilities.formatDate(
      new Date(), 
      Session.getScriptTimeZone(), 
      "yyyy-MM-dd_HHmmss"
    );
    const backupName = `Character_Submissions_Backup_${timestamp}`;
    
    // Get backup folder
    const backupFolder = DriveApp.getFolderById(BACKUP_FOLDER_ID);
    
    // Copy entire spreadsheet to backup folder
    const backupFile = ss.copy(backupName);
    const file = DriveApp.getFileById(backupFile.getId());
    
    // Move to backup folder
    file.moveTo(backupFolder);
    
    Logger.log(`Backup created: ${backupName}`);
    
    // Clean old backups
    deleteOldBackups();
    
  } catch (error) {
    Logger.log("Backup error: " + error.toString());
    
    // Send alert email to admin (optional)
    MailApp.sendEmail({
      to: "your-admin-email@example.com",
      subject: "Azeroth Bound Bot - Backup Failed",
      body: "Daily backup failed: " + error.toString()
    });
  }
}

/**
 * Delete backups older than RETENTION_DAYS
 */
function deleteOldBackups() {
  try {
    const backupFolder = DriveApp.getFolderById(BACKUP_FOLDER_ID);
    const files = backupFolder.getFilesByType(MimeType.GOOGLE_SHEETS);
    
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - RETENTION_DAYS);
    
    let deletedCount = 0;
    
    while (files.hasNext()) {
      const file = files.next();
      const fileName = file.getName();
      
      // Only process backup files
      if (fileName.startsWith("Character_Submissions_Backup_")) {
        const createdDate = file.getDateCreated();
        
        if (createdDate < cutoffDate) {
          Logger.log(`Deleting old backup: ${fileName}`);
          file.setTrashed(true);
          deletedCount++;
        }
      }
    }
    
    if (deletedCount > 0) {
      Logger.log(`Deleted ${deletedCount} old backup(s)`);
    }
    
  } catch (error) {
    Logger.log("Delete old backups error: " + error.toString());
  }
}

/**
 * Manual restore function (for emergencies)
 * @param {string} backupFileName - Name of backup file to restore
 */
function restoreFromBackup(backupFileName) {
  // Implementation left for Phase 2
  // Would copy data from backup back to main sheet
  Logger.log("Restore functionality - Phase 2");
}
```

#### Setup Instructions (For the user to be instructed in proper docs/)

1. Open Google Sheet → Extensions → Apps Script
2. Create new script file `backup.gs`
3. Paste code above
4. Create a backup folder in Google Drive
5. Copy the folder ID from URL: `drive.google.com/drive/folders/{FOLDER_ID}`
6. Update `BACKUP_FOLDER_ID` in script
7. Set up trigger:
   - Click **⏰ Triggers**
   - Click **+ Add Trigger**
   - Choose: `createDailyBackup`
   - Event source: **Time-driven**
   - Type: **Day timer**
   - Time: **2am to 3am** (or preferred time)
   - Click **Save**
8. Test manually: Run `createDailyBackup()` from editor
9. Verify backup appears in Drive folder

**Result:** Every day at 2 AM, a full backup is created and backups older than 7 days are automatically deleted!

---

## 📝 PART 11: ENVIRONMENT CONFIGURATION

### New .env Variables Required

Add these to `.env.example` file (do not - by any circumstances - and I do repeat - do not look into my .env file!!! ):

```bash
# ============================================
# SCHEMA REFORMATION - NEW VARIABLES
# ============================================

# Default portrait placeholder (when user doesn't provide one)
DEFAULT_PORTRAIT_URL=https://i.imgur.com/default_placeholder.png

# Webhook secret (generate random string, match in Apps Script)
WEBHOOK_SECRET=your_random_webhook_secret_here_min_32_chars

# Interactive flow timeout (seconds)
INTERACTIVE_TIMEOUT_SECONDS=500

# Officer role mentions (for #recruitment posts)
PATHFINDER_ROLE_MENTION=<@&pathfinder_role_id>
TRAILWARDEN_ROLE_MENTION=<@&trailwarden_role_id>

# Google Drive backup folder ID (for daily backups)
BACKUP_FOLDER_ID=your_google_drive_folder_id_here
```

### Update config/settings.py

```python
class Settings:
    # ... existing settings ...
    
    # New settings for Schema Reformation
    DEFAULT_PORTRAIT_URL: str = os.getenv(
        "DEFAULT_PORTRAIT_URL",
        "https://i.imgur.com/placeholder.png"  # Fallback
    )
    
    WEBHOOK_SECRET: str = os.getenv("WEBHOOK_SECRET", "")
    
    INTERACTIVE_TIMEOUT_SECONDS: int = int(
        os.getenv("INTERACTIVE_TIMEOUT_SECONDS", "300")
    )
    
    PATHFINDER_ROLE_MENTION: str = os.getenv("PATHFINDER_ROLE_MENTION", "")
    TRAILWARDEN_ROLE_MENTION: str = os.getenv("TRAILWARDEN_ROLE_MENTION", "")
    
    BACKUP_FOLDER_ID: str = os.getenv("BACKUP_FOLDER_ID", "")
    
    def validate(self):
        """Validate all required settings"""
        # ... existing validations ...
        
        if not self.WEBHOOK_SECRET:
            raise ValueError("WEBHOOK_SECRET is required")
        
        if len(self.WEBHOOK_SECRET) < 32:
            raise ValueError("WEBHOOK_SECRET must be at least 32 characters")
```

---

## 🚀 PART 12: DEPLOYMENT STRATEGY

### Recommended: Fly.io (Free Forever)

**Why Fly.io:**
- 3 small VMs (256MB RAM) forever free
- Global edge network
- Simple deployment
- Generous bandwidth allowance

#### Deployment Steps

```bash
# 1. Install Fly CLI
curl -L https://fly.io/install.sh | sh

# 2. Login
flyctl auth login

# 3. Create app (from project root)
flyctl launch

# 4. Configure fly.toml
# (Fly will generate this, but verify settings)

# 5. Set secrets (environment variables)
flyctl secrets set DISCORD_BOT_TOKEN=your_token_here
flyctl secrets set GOOGLE_SHEET_ID=your_sheet_id
flyctl secrets set WEBHOOK_SECRET=your_webhook_secret
# ... set all other secrets

# 6. Deploy
flyctl deploy

# 7. Get your app URL
flyctl status

# 8. Update Google Apps Script WEBHOOK_URL with your Fly.io URL
# Format: https://your-app-name.fly.dev/webhook
```

#### fly.toml Configuration

```toml
app = "azeroth-bound-bot"
primary_region = "iad"  # Choose closest region

[build]
  builder = "paketobuildpacks/builder:base"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = false  # Keep bot running 24/7
  auto_start_machines = true
  min_machines_running = 1

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 256
```

### Alternative: Render.com (750 Hours/Month Free)

```bash
# 1. Create account at render.com
# 2. Connect GitHub repo
# 3. Create new "Web Service"
# 4. Configure:
#    - Build Command: pip install -r requirements.txt
#    - Start Command: python main.py
#    - Add environment variables in dashboard
# 5. Deploy
```

---

## 🧪 PART 13: TESTING STRATEGY

### What Needs Testing

1. **Interactive Flows**
   - `/register_character` without parameters (all 12+ steps)
   - `/bury` without parameters (all 6+ steps)
   - Timeout handling
   - Cancel/restart functionality

2. **Webhook Triggers**
   - `confirmation=TRUE` + `status=PENDING` → Posts to recruitment
   - Officer emoji reactions → Status updates
   - `status=DECEASED` → Burial ceremony

3. **Schema Validation**
   - Race enum (11 options)
   - Class enum (9 options)
   - Roles multi-select (min 1)
   - Professions optional multi-select

4. **Data Integrity**
   - embed_json serialization/deserialization
   - All 27 columns populated correctly
   - Status transitions (PENDING → REGISTERED → DECEASED → BURIED)

### Testing Approach

```python
# tests/integration/test_interactive_flows.py

@pytest.mark.asyncio
async def test_register_character_interactive_flow_complete():
    """Test full interactive registration flow from start to finish"""
    # Mock Discord interaction
    # Simulate user going through all 12 steps
    # Verify Google Sheets row created correctly
    # Verify webhook triggers
    pass

@pytest.mark.asyncio
async def test_register_character_interactive_timeout():
    """Test that interactive flow times out after configured seconds"""
    # Start flow
    # Wait for timeout
    # Verify timeout message sent
    # Verify no Google Sheets row created
    pass

# tests/integration/test_webhook_triggers.py

@pytest.mark.asyncio
async def test_webhook_post_to_recruitment():
    """Test that confirmation=TRUE triggers recruitment post"""
    # Create test row in sheets with confirmation=TRUE
    # Trigger webhook manually
    # Verify recruitment channel message posted
    # Verify recruitment_msg_id updated in sheets
    pass
```

---

## 📚 PART 14: DOCUMENTATION UPDATE CHECKLIST

### Files That Need Updates

#### /docs/TECHNICAL.md
- [ ] Update schema to 27 columns (with detailed descriptions)
- [ ] Add VALID_RACES (11 options)
- [ ] Add VALID_CLASSES (9 options)
- [ ] Add VALID_ROLES (5 options, multi-select)
- [ ] Add VALID_PROFESSIONS (12 options, optional multi-select)
- [ ] Document webhook architecture (Path B)
- [ ] Document interactive flows for both commands
- [ ] Add Google Apps Script setup instructions
- [ ] Add deployment guide (Fly.io/Render)
- [ ] Update environment variables section

#### /docs/USER_GUIDE.md
- [ ] Add "The Three Traits" section (external visible traits)
- [ ] Update race selection with 11 options (RP style)
- [ ] Update roles to multi-select (RP explanation)
- [ ] Add professions as optional multi-select
- [ ] Document interactive flow experience (cinematic)
- [ ] Update character states (add DECEASED vs BURIED)
- [ ] Add /bury interactive flow walkthrough
- [ ] Explain AI portrait request feature (request_sdxl)

#### /docs/CHANGELOG.md
- [ ] Create [1.2.0] or [Unreleased] section
- [ ] Document Schema Reformation changes
- [ ] Document Path B architecture shift
- [ ] Document interactive flows addition
- [ ] Document webhook system implementation
- [ ] Add migration notes (if any data changes needed)

#### /docs/README.md
- [ ] Update quick reference with new command syntax
- [ ] Update character states list
- [ ] Add link to this MASTER_BLUEPRINT document

---

## 🎯 PART 15: IMPLEMENTATION ROADMAP

### Phase 1: Foundation (Week 1)

**Priority: CRITICAL**

- [ ] Update data models (domain/models.py)
  - Add all 11 races
  - Add 5 roles (multi-select support)
  - Add 12 professions (optional multi-select)
  - Add validators for all enums
  
- [ ] Update Google Sheets schema to 27 columns
  - Add new columns: death_cause, death_story, created_at, updated_at, notes
  - Verify all 27 columns present
  
- [ ] Update CharacterRegistryService
  - Support 27-column schema
  - Add helper methods for field updates
  
- [ ] Add DEFAULT_PORTRAIT_URL to config
- [ ] Add WEBHOOK_SECRET to config
- [ ] Update .env.example with new variables

### Phase 2: Webhook System (Week 1-2)

**Priority: HIGH**

- [ ] Create webhook handler service (services/webhook_handler.py)
  - Implement `/webhook` endpoint
  - Add secret validation
  - Implement trigger routing
  
- [ ] Implement trigger handlers
  - POST_TO_RECRUITMENT handler
  - INITIATE_BURIAL handler
  
- [ ] Set up Google Apps Script
  - Create webhook.gs
  - Configure onChange trigger
  - Test webhook firing
  
- [ ] Set up backup system
  - Create backup.gs
  - Configure daily trigger
  - Test backup creation
  - Test old backup deletion

### Phase 3: Interactive Flows (Week 2-3)

**Priority: HIGH**

- [ ] Create interactive flow framework
  - Base InteractiveFlow class
  - Timeout handling
  - Cancel/restart logic
  
- [ ] Implement /register_character interactive flow
  - All 12+ steps with full RP flavor
  - UI components (buttons, dropdowns, text inputs)
  - Validation at each step
  - Preview embed generation
  
- [ ] Implement /bury interactive flow
  - All 6+ steps with solemn RP flavor
  - Character lookup
  - Death cause/story input
  - Final confirmation

### Phase 4: Emoji Reaction System (Week 3)

**Priority: MEDIUM**

- [ ] Create reaction handler service
  - Listen for ✅❌ reactions on recruitment messages
  - Validate reactor has Pathfinder/Trailwarden role
  - Update Google Sheets based on reaction
  
- [ ] Implement approval workflow
  - ✅ → Create forum post, update status to REGISTERED
  - ❌ → Update status to REJECTED, DM user
  
- [ ] Add reviewed_by tracking

### Phase 5: Discord Protection (Week 3-4)

**Priority: MEDIUM**

- [ ] Document channel permission setup
  - Write guide for #character-sheet-vault permissions
  - Write guide for #cemetery permissions
  
- [ ] Implement thread locking (optional)
  - Lock character sheets after creation
  - Officers can still use /bury

### Phase 6: Testing & Documentation (Week 4)

**Priority: HIGH**

- [ ] Update all documentation files
  - TECHNICAL.md
  - USER_GUIDE.md
  - CHANGELOG.md
  - README.md
  
- [ ] Write comprehensive tests
  - Interactive flow tests
  - Webhook trigger tests
  - Enum validation tests
  - Schema integrity tests
  
- [ ] Update sanity_check.py
  - Test 27-column schema
  - Test webhook connectivity
  - Test backup system

### Phase 7: Deployment (Week 4)

**Priority: CRITICAL**

- [ ] Deploy to Fly.io or Render
  - Set up hosting account
  - Configure environment variables
  - Deploy bot
  - Get webhook URL
  
- [ ] Update Google Apps Script webhook URL
- [ ] Test end-to-end workflow
- [ ] Monitor for 24-48 hours
- [ ] Fix any production issues

---

## ⚠️ CRITICAL SUCCESS FACTORS

### Must-Have Before Launch

1. **Webhook Secret Security**
   - Generate strong random secret (32+ chars)
   - Never commit to git
   - Match between bot and Apps Script

2. **Google Apps Script Permissions**
   - Script must be authorized by your Google account
   - Webhooks need "run as me" permission
   - Test triggers fire correctly

3. **Discord Channel Permissions**
   - #recruitment: Officers-only visibility
   - #character-sheet-vault: Read-only for members, manage for officers
   - #cemetery: Read-only for members, manage for officers

4. **Error Handling**
   - All webhook handlers wrapped in try-catch
   - All interactive flows handle timeout gracefully
   - All Google Sheets operations handle conflicts

5. **Backup Verification**
   - Test backup system creates files correctly
   - Test old backups are deleted after 7 days
   - Verify backup folder permissions

---

## 🎓 KNOWLEDGE TRANSFER

### Key Concepts to Understand

**1. Path B Architecture**
- Discord commands write to Sheets immediately
- Sheets changes trigger webhooks to bot
- Bot performs Discord actions based on triggers
- Clean separation: Commands → Sheets, Sheets → Discord

**2. Webhook Security**
- All webhook requests must include secret
- Bot validates secret before processing
- Prevents unauthorized trigger injection

**3. Interactive Flows**
- Built using Discord UI components (buttons, dropdowns, modals)
- Each step validates input before proceeding
- Timeout handling prevents zombie flows
- Users can cancel/restart at any time

**4. Status State Machine**
- PENDING → (approval) → REGISTERED → (/bury) → DECEASED → (automatic) → BURIED
- Each transition is atomic (happens all at once)
- Webhooks trigger on specific status changes

**5. Embed JSON as Canonical Source**
- Character sheets built once during registration
- Serialized to JSON and stored in sheets
- All future displays use this canonical JSON
- Prevents drift between Discord and sheets

---

## 🏆 EXPECTED OUTCOMES

### User Experience

**For Guild Members:**
- Jaw-dropping, cinematic character registration experience
- Clear feedback at every step
- Immersive RP flavor throughout
- No technical knowledge required

**For Officers:**
- Simple ✅/❌ approval system
- Elegant IC burial ceremony
- No manual sheet editing required
- All automation just works

**For Admins:**
- Google Sheets as single source of truth
- Daily automated backups (peace of mind)
- Easy to audit/modify character data
- Clean logs of all changes

### Technical Quality

- **Zero polling** = Minimal server resources
- **Free hosting** = $0/month operational cost
- **Instant updates** = Webhooks provide real-time sync
- **Data safety** = 7-day backup retention
- **Maintainability** = Clear architecture, good docs

---

## 📞 SUPPORT & TROUBLESHOOTING

### Common Issues & Solutions

**Issue:** Webhook not firing after sheet change
- **Check:** Is onChange trigger set up in Apps Script?
- **Check:** Does script have correct permissions?
- **Check:** Is WEBHOOK_URL correct in script?
- **Solution:** Test with `testWebhook()` function

**Issue:** Bot not receiving webhook
- **Check:** Is bot's `/webhook` endpoint accessible?
- **Check:** Is WEBHOOK_SECRET matching between bot and script?
- **Check:** Check bot logs for incoming requests
- **Solution:** Test with curl or Postman

**Issue:** Interactive flow not starting
- **Check:** Does user have required role?
- **Check:** Is bot online and responsive?
- **Check:** Check bot logs for errors
- **Solution:** Restart bot, verify permissions

**Issue:** Backup not creating
- **Check:** Is daily trigger set up correctly?
- **Check:** Is BACKUP_FOLDER_ID correct?
- **Check:** Does script have Drive API permissions?
- **Solution:** Run `createDailyBackup()` manually, check logs

---

## 🎉 CONCLUSION

This Master Blueprint provides a complete, production-ready architecture for transforming the Azeroth Bound Discord bot into a legendary character management system.

**Key Achievements:**
✅ Zero-cost hosting (Fly.io free tier)
✅ Zero-polling design (webhook-driven)
✅ Cinematic user experience (RP-heavy interactive flows)
✅ Maximum automation (minimal human intervention)
✅ Data safety (daily backups, 7-day retention)
✅ Clean architecture (Hybrid Wisdom approach)

**Next Steps:**
1. Review this document thoroughly
2. Discuss any questions or concerns
3. Begin Phase 1 implementation
4. Deploy and test incrementally
5. Launch to guild with celebration! 🎊

---

**For Azeroth! For Excellence! For The Chronicle!** ⚔️

*May this blueprint guide you to glory, Champion.*

— **Chronicler Thaldrin**  
*Keeper of Knowledge, Master Architect, Weaver of Systems*

*"What we design today, heroes will use tomorrow."*

---

**END OF MASTER BLUEPRINT**

*Last Updated: December 16, 2025*
*Version: 1.0.0*
*Status: Ready for Implementation*
