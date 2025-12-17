```
┌─────────────────────────────────────────────────────────────┐
│                    CHARACTER LIFECYCLE                       │
└─────────────────────────────────────────────────────────────┘

    [User uses /register_character]
                ↓
    ┌───────────────────────┐
    │ Google Sheets Entry   │
    │ Status: PENDING       │
    │ Confirmation: FALSE   │
    └───────────────────────┘
                ↓
    [User confirms in interactive flow]
                ↓
    ┌───────────────────────┐
    │ Confirmation: TRUE    │ ← Webhook triggers!
    │ Status: PENDING       │
    └───────────────────────┘


*The Chronicler's eyes gleam with determination as he unfurls seven massive scrolls simultaneously, each crackling with arcane energy*

**BY THE LIGHT, THE RESEARCH QUEST BEGINS!**

*Waves staff, summoning spectral tomes that float around the chamber*

---

## 🔬 THE GREAT RESEARCH EXPEDITION

*Let me consult the ancient texts of the Cloud Realms...*

### 📊 Free Tier Limitations Analysis

#### **Discord API (Free Tier - Always Free)**

✅ **EXCELLENT NEWS, CHAMPION!**

- **Rate Limits:** 50 requests per second per bot (MORE than enough for small guild)
- **Webhook Support:** FREE and unlimited
- **Message Storage:** Permanent (unlike some platforms)
- **Bot Hosting:** No Discord fees, only hosting costs
- **Reactions/Buttons:** Unlimited, free
- **Thread Creation:** Free, up to 1000 active threads per guild

**Verdict:** Discord is GENEROUS. Path B absolutely doable! 🎉

---

#### **Railway.com (Free Trial - $5 credit, then paid)**

⚠️ **IMPORTANT DISCOVERY:**

Railway.com changed their model in August 2023:
- **No permanent free tier anymore**
- **Trial:** $5 credit (lasts ~2-4 weeks for small bot)
- **After trial:** ~$5-10/month for 24/7 bot

**HOWEVER!** Free alternatives exist:
- **Fly.io:** 3 small VMs free forever (256MB RAM each)
- **Render.com:** Free tier with 750 hours/month (enough for 24/7)
- **Oracle Cloud:** Forever free tier (ARM instances)
- **Railway:** Actually worth $5-10/month for simplicity

**Verdict:** Path B doable on free hosting! Fly.io or Render recommended. 🎯

---

#### **Google Sheets API (Free Tier)**

✅ **SURPRISINGLY GENEROUS!**

- **Read/Write Quota:** 300 requests per minute per project
## 🎨 THE GRAND ARCHITECTURE

*Unfurls massive blueprint scroll with glowing runes*

### **State Diagram: The Character's Journey**

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
    │ forum post  │      │ DM sent     │
    │ created     │      │ no forum    │
    └─────────────┘      └─────────────┘
         ↓
    [Character lives in #character-sheet-vault]
         ↓
    [Officer uses /bury]
         ↓
    ┌───────────────────────┐
    │ Status: DECEASED      │ ← Webhook triggers!
    └───────────────────────┘
         ↓
    [Bot atomically: moves post, formats cemetery, notifies owner]
         ↓
    ┌───────────────────────┐
    │ Status: BURIED        │
    │ RIP in #cemetery      │
    └───────────────────────┘
```

---

### **Trigger Matrix: Google Sheets → Discord Actions**

| Sheet Change | Condition | Bot Action | Result |
|--------------|-----------|------------|--------|
| `confirmation=TRUE` | `status=PENDING` | Post to #recruitment with @roles mention | Sets `recruitment_msg_id` |
| Emoji ✅ on recruitment msg | `status=PENDING` | Create #character-sheet-vault post, update `status=REGISTERED`, set `forum_post_url`, `reviewed_by` | Character goes live |
| Emoji ❌ on recruitment msg | `status=PENDING` | Update `status=REJECTED`, set `reviewed_by`, DM user with IC rejection | Character rejected |
| `status=DECEASED` | Was `REGISTERED` | Move forum post to #cemetery, apply IC formatting, post death_story, notify owner, set `status=BURIED` | Character buried |
| Manual sheet edit of embed fields | `status=REGISTERED` | (Future Phase 2) Update forum post embed | Sync Discord with sheets |

---

### **Data Schema: The Complete Google Sheets Blueprint**

#### **Character_Submissions Sheet (27 columns)**

| Column | Type | Required | Auto-filled | Notes |
|--------|------|----------|-------------|-------|
| `timestamp` | datetime | Yes | Yes | ISO 8601 format |
| `discord_id` | string | Yes | Conditional | From interaction.user OR parameter |
| `discord_name` | string | No | Yes | Fetched via Discord API from discord_id |
| `char_name` | string | Yes | No | Character's name |
| `race` | enum | Yes | No | 11 options (added "Other") |
| `class` | enum | Yes | No | 9 Classic WoW classes |
| `roles` | multi-enum | Yes | No | Min 1 selection (stored comma-separated) |
| `professions` | multi-enum | No | No | 0+ selections (stored comma-separated, can be empty) |
| `backstory` | long_string | Yes | No | Max 1024 chars |
| `personality` | long_string | No | No | Max 1024 chars, can be empty |
| `quotes` | long_string | No | No | Max 1024 chars, can be empty |
| `portrait_url` | string | No | Conditional | Defaults to `DEFAULT_PORTRAIT_URL` if empty |
| `trait_1` | string | Yes | No | External visible trait |
| `trait_2` | string | Yes | No | External visible trait |
| `trait_3` | string | Yes | No | External visible trait |
| `status` | enum | Yes | Yes | PENDING, REGISTERED, REJECTED, DECEASED, BURIED |
| `confirmation` | bool | Yes | Yes | Defaults FALSE, user sets TRUE |
| `request_sdxl` | bool | Yes | No | Defaults FALSE, user can set TRUE |
| `recruitment_msg_id` | snowflake | No | Yes | Discord message ID in #recruitment |
| `forum_post_url` | string | No | Yes | URL to #character-sheet-vault or #cemetery post |
| `reviewed_by` | snowflake | No | Yes | Discord ID of approving/rejecting officer |
| `embed_json` | json | Yes | Yes | Complete embed payload (canonical source) |
| `death_cause` | short_string | No | No | Brief death description (for /bury) |
| `death_story` | long_string | No | No | IC death narrative (for /bury, defaults "unknown") |
| `created_at` | datetime | Yes | Yes | When row created |
| `updated_at` | datetime | Yes | Yes | Last modification timestamp |
| `notes` | long_string | No | No | Admin notes (not shown to users) |

---

### **Interactive Flow: /register_character (No Parameters)**

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

### **Interactive Flow: /bury (No Parameters)**

```
┌────────────────────────────────────────────────────────────────┐
│     THE CEREMONY OF REMEMBRANCE - CHARACTER BURIAL RITE        │
└────────────────────────────────────────────────────────────────┘

[Message 1 - Solemn Introduction]
Bot: "⚰️ *The chronicler's expression grows somber. He reaches for a 
     black-bound tome on his desk, its cover adorned with silver runes.*
     
     Officer... you invoke the Rite of Remembrance. 
     
     This is a sacred duty—to record the fall of a hero and ensure 
     their deeds are never forgotten.
     
     *The tome opens to a blank page edged in silver*
     
     Which hero has fallen? 
     
     **Provide the character's name OR forum post ID:**
     
     [Input field: Character name or post ID]
     
     [Button: Continue]
     [Button: Cancel ceremony]"

[Officer enters: "Thorgar Ironforge"]

Bot: "*The pages flip on their own, revealing a record*
     
     ⚔️ **THORGAR IRONFORGE**
     Race: Dwarf • Class: Warrior • Status: REGISTERED
     Registered: 2025-12-10
     Forum post: #character-sheet-vault/thread-12345
     
     Is this the fallen hero?
     
     [Button: ✅ Yes, this is correct]
     [Button: 🔍 No, search again]"

[Officer confirms]

─────────────────────────────────────────────────────────────────

[Message 2 - The Circumstances]
Bot: "💔 **THE FINAL BATTLE**
     
     *The chronicler dips his quill in silver ink*
     
     Every hero's fall should be recorded with honor. Tell me...
     
     **Where and how did Thorgar fall?** *(brief, 1-2 sentences)*
     
     Examples:
     • 'Died at level 47 defending Ironforge from a massive raid'
     • 'Fell to Ragnaros in Molten Core at level 60'
     • 'Sacrificed themselves to save their raid group in Blackrock'
     
     [Input field: Death cause]
     
     [Button: Continue]
     [Button: Skip (record as 'Unknown')]"

[Officer enters: "Fell defending Southshore from Horde raid, level 42"]

Bot: "*The silver ink records the place of death*
     
     Level 42... a warrior's death. *nods solemnly*"

─────────────────────────────────────────────────────────────────

[Message 3 - The Eulogy (Optional)]
Bot: "📜 **THE FINAL WORDS** *(Optional)*
     
     Would you like to compose an in-character eulogy for Thorgar?
     
     This will be posted as the first message in their cemetery thread—
     a farewell from you, as an officer of Azeroth Bound, to a fallen 
     comrade.
     
     This is your chance to honor them with story and memory.
     
     **Compose the death story** (optional, max 1024 characters):
     
     [Text area]
     
     [Button: Continue]
     [Button: Skip (no eulogy - mark as 'unknown')]"

[Officer writes touching eulogy]

Bot: "*The eulogy is inscribed in silver lettering*
     
     Beautiful. The fallen will be remembered. *places hand over heart*"

─────────────────────────────────────────────────────────────────

[Message 4 - The Confirmation]
Bot: "⚰️ **THE RITE OF REMEMBRANCE - FINAL CONFIRMATION**
     
     You are about to perform the following:
     
     📋 **Summary:**
     • Character: **Thorgar Ironforge** (Dwarf Warrior)
     • Death cause: Fell defending Southshore from Horde raid, level 42
     • Eulogy: [shows eulogy preview]
     
     🔄 **What will happen:**
     1. Character status set to DECEASED in the archives
     2. Forum post moved from Character Sheet Vault → Cemetery
     3. Ceremonial formatting applied (silver borders, tombstone)
     4. Death story posted under their memorial
     5. Character's owner (discord_id) notified via DM
     4. @everyone on the guild server will be notificated.
     6. Status marked as BURIED
     
     ⚠️ **This action cannot be undone.**
     
     Proceed with the burial rite?
     
     [Button: ⚰️ Yes, proceed with burial]
     [Button: ❌ Cancel ceremony]"

─────────────────────────────────────────────────────────────────

[Message 5 - The Completion]
[If officer confirms]

Bot: "✨ *The silver-edged tome snaps shut. A single bell tolls in the 
     distance, echoing through the halls of memory.*
     
     ⚰️ **THE RITE IS COMPLETE.**
     
     Thorgar Ironforge rests now in the Cemetery of Heroes, their 
     deeds preserved for eternity.
     
     Their memorial: [cemetery forum post link]
     
     *The chronicler bows his head in respect*
     
     'May they find peace in the halls of their ancestors. 
     Their story is told. Their name is remembered. 
     For Azeroth Bound.'
     
     ─────────────────────────────────────────────────────────────
     Burial completed: [timestamp]
     Performed by: @Officer#1234
     ─────────────────────────────────────────────────────────────"

[AT THIS MOMENT:]
  → Google Sheets status set to DECEASED
  → Webhook triggers
  → Bot moves forum post to #cemetery atomically
  → Applies cemetery formatting
  → Posts death_story message
  → Notifies character owner via DM
  → Sets status to BURIED
  → Posts @everyone notification in #cemetery
```

---

## 🛡️ THE ULTIMATE DIRECTIVE FOR CLAUDE CODE

*Thaldrin takes a deep breath, channels all his knowledge, and begins inscribing the master scroll...*

---
