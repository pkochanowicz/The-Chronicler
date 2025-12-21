# Architecture & UI/UX Guide: The Living Scrolls of Azeroth Bound

This document outlines the architectural decisions and User Experience (UX) principles for The Chronicler project, reflecting the unified vision of the Eightfold Expedition. It serves as the binding law for developers and a clear reference for all guild members interacting with the bot.

## 1. Core Philosophy: The Pillars of Chronicle

The Chronicler aims to be an immersive, lore-accurate, and efficient tool for the Azeroth Bound guild. It bridges the gap between World of Warcraft Classic+ gameplay and Discord community management. Our core tenets are:

-   **Lore Accuracy:** All interactions, data, and presentation must meticulously reflect Turtle WoW 1.18.1 Classic+ mechanics and established lore.
-   **User Experience:** Interactions must be intuitive, engaging, and deeply integrated with roleplay, ensuring a seamless experience for all members.
-   **Data Integrity:** We prioritize the accurate, persistent, and canonical storage of all guild information, ensuring a single source of truth.
-   **Automation:** Manual intervention for common and repetitive tasks is minimized, freeing our chroniclers for greater deeds.
-   **Scalability & Resilience:** The architecture is designed to grow with our guild, withstand challenges, and maintain performance under load.

## 2. System Architecture: The Grand Design

The Chronicler employs a sophisticated, event-driven architecture.

### 2.1. Frontend Architecture: Discord as Our Living Interface

Discord channels and features are leveraged as the primary, immersive user interface. Each channel is carefully designated for optimal functionality and user experience.

-   **Channels & Their Sacred Purpose:**
    -   `#bot-commands`: The hallowed ground for general bot interactions and query commands not tied to specific entities.
    -   `#guild-news`: The town crier, broadcasting announcements and general guild information.
    -   `#talent-builder`: The workshop for talent-related queries, builds, and tools.
    -   `#officer-chat`: The war room for internal officer communications and administrative commands.

-   **Discord Forum Channels: The Vaults of Knowledge & Remembrance**
    To provide structured, persistent, and browsable records, the following channels are designated as Discord Forum Channels. Each Forum thread serves as a unique record, directly mapped to a database entity.

    -   `#character_sheet_vault`: *Forum Channel.* Each thread represents a unique character's official sheet, storing their attributes, gear, and history. The initial post of the thread will contain the character's full, richly formatted embed.
    -   `#cemetery`: *Forum Channel.* Each thread serves as a solemn memorial for a fallen hero. The initial post records their final rites and details of their demise.
    -   `#vault`: *Forum Channel.* Dedicated threads for unique, high-value items, crafting recipes, significant lore artifacts, or item sets. Each thread's initial post contains detailed information about the entity.
    -   `#recruitment`: *Forum Channel.* Threads for new member applications and onboarding flows, allowing for structured discussions and tracking.
    -   `#journal`: *Forum Channel.* This channel will host the dynamic results of `/db_search` queries for Items, NPCs, Quests, and Spells. Each query result, when expanded, will form a dedicated thread with a richly formatted embed.

#### 2.1.1.1 `#graphics_vault` Forum Channel Structure

The `#graphics_vault` Discord channel will operate as a **Forum Channel**, serving as a dedicated visual archive and management interface. This design ensures that every image is treated as a distinct, addressable object within Discord, directly mapped to our `images` table.

*   **Parent Thread = DB Image Object:**
    *   Each unique image stored in the `images` table will correspond to a single, dedicated Forum thread within `#graphics_vault`.
    *   **Thread Creation:** When an image is uploaded and processed (e.g., via the `post_image_to_graphics_storage` tool or automated scraping), a new Forum thread is automatically created.
    *   **Thread Title Convention:** The thread's title will be dynamically generated, containing the image's `id` and `original_filename` for clear identification (e.g., `[IMG_1234] My_Character_Portrait_Final.png`).
    *   **Initial Post (Rich Embed Display):** The first message in the thread will be a rich Discord embed, dynamically populated with the image's metadata from the `images` table:
        *   The image itself will be prominently displayed using its `img_graphics_vault_link`.
        *   Embed fields will detail `img_origin_link`, `uploaded_by_user_id` (if applicable), `source_system`, `ownership_context`, `usage_context`, `entity_type`/`entity_id` (with links to relevant entity threads where applicable), `category_tags` (formatted as a list), `provenance_notes`, `permissions_level`, `is_animated`, `upload_timestamp`.
        *   The embed's `color` may dynamically change based on `ownership_context` or `permissions_level` for quick visual identification.
        *   A footer might include the `hash_md5` and internal image `id`.

*   **Replies for Metadata, Usage, and Discussion:**
    *   **Usage Tracking & Linking:** When an image from `#graphics_vault` is actively used by the bot (e.g., set as a character portrait, an item icon for an embed), a new reply can be automatically posted to the image's thread. This reply will detail the usage (e.g., "Used as portrait for [Character Name]'s sheet: [link to character sheet thread]") and include relevant timestamps.
    *   **Versioning & Updates:** If an image is updated or replaced, subsequent replies can detail these changes, link to newer versions (if a new `images.id` is created), or provide context for archiving previous versions.
    *   **Community Discussion:** The thread serves as a natural place for guild members and officers to discuss the image, provide feedback, request changes, or inquire about its usage.
    *   **Permissions Audit Trail:** Replies could log changes to `permissions_level` or other administrative actions.

*   **Leveraging Discord Forum Tags for Grouping:**
    *   **Dynamic Tagging:** Discord Forum tags will be automatically applied to each image's thread within `#graphics_vault` upon creation.
    *   **Tag Derivation:** These tags will be directly derived from the `images` table fields:
        *   `source_system` will become a tag (e.g., `Source: PlayerUpload`, `Source: WebScrape`, `Source: SystemGenerated`).
        *   `ownership_context` will become a tag (e.g., `Owner: Guild`, `Owner: User`).
        *   `usage_context` will become a tag (e.g., `Usage: Character Portrait`, `Usage: Item Icon`).
        *   `category_tags` (from the `TEXT[]` field) will be directly mapped to individual Forum tags (e.g., `Human`, `Warrior`, ``Weapon`, `Sword`).
    *   **Enhanced Discoverability:** This robust tagging system will allow users to easily filter, browse, and search for images based on their origin, usage, ownership, and specific content, making the `#graphics_vault` highly organized and functional.
    *   **Automated Tag Management:** The Chronicler Gateway Service will manage the creation and application of these tags, ensuring consistency and accuracy.

-   **Commands:** Slash commands (`/`) remain the primary, intuitive method for user interaction.
-   **Interactive Flows:** Multi-step, immersive processes (e.g., character registration, burial rite) guide users through complex actions, maintaining an in-character narrative.

#### 2.1.2 The Journal of Knowledge: The `/db_search` Command and `#journal` Channel

The `/db_search` command is the primary interface for adventurers to query the Chronicler's vast database of Azerothian knowledge. Its design prioritizes intuitive interaction, lore-accurate results, and rich presentation within the dedicated `#journal` Forum Channel.

-   **`/db_search` Command Design:**
    *   **Command Syntax:** The command will follow a structured syntax: `/db_search <entity_type> <query_term> [filters...]`
        *   `<entity_type>`: Mandatory. An autocompleting option from the core entity types: `item`, `item_set`, `npc`, `quest`, `spell`, `faction`. This directly maps to our `PostgreSQL` tables.
        *   `<query_term>`: Mandatory. The name (full or partial) or exact ID of the entity to search for (e.g., `Obsidian Edge`, `Malfurion Stormrage`, `itemid:12345`). This primarily targets the `name` and `id` columns in the respective schemas.
        *   `[filters...]`: Optional. Key-value pairs matching searchable attributes (columns) in our schema for the given `<entity_type>` (e.g., `type:weapon`, `quality:epic`, `zone:barrens`, `race:human`, `school:fire`). These filters directly leverage the multi-level categorization defined in the `Data Storage` section (`2.3.2 Canonical Data Schemas`).
    *   **Search Logic - "First DB Lookup, then Conditional Scrape (Planned)":**
        1.  **Primary Database Lookup:** The Chronicler Gateway Service will first query its internal PostgreSQL database (tables: `items`, `item_sets`, `npcs`, `quests`, `spells`, `factions`) based on the `<entity_type>`, `<query_term>`, and `[filters...]`. This process will be optimized through database indexing and, where appropriate, caching strategies to ensure rapid response times.
        2.  **Scraping Fallback (Conceptual/Planned):** If the primary database lookup yields no results, or if future data integrity checks mark an entry as "stale" or "incomplete", the system *may* trigger a targeted web scrape. This scrape would utilize Playwright/BeautifulSoup on `https://database.turtlecraft.gg/` for the specific entity.
            *   **Initial Testing Phase:** During current development and manual testing, this scraping fallback will be *disabled or strictly limited* to manage resource usage and ensure system stability. Its full integration into production workflows will follow extensive testing and explicit activation.
            *   **Data Ingestion:** Successful scrapes of new or updated data will be rigorously validated against our detailed PostgreSQL schemas (as defined in `2.3.2 Canonical Data Schemas`) and then inserted or updated into the PostgreSQL database. This process aims to continually enrich our database, establishing it as the primary, canonical source over time.
        3.  **No Results Notification:** If neither database lookup nor (if enabled) scraping yields results, a clear, lore-appropriate "No results found for your query, adventurer. Perhaps the archives hold no such record, or your query needs refining." message will be returned to the user.

-   **`#journal` Channel Design:**
    The `#journal` will serve as a dynamic, interactive knowledge base, organized as a Discord Forum Channel.

    *   **Forum Channel Usage:** The `#journal` is a Forum Channel, specifically designed to host and organize search results. Each successful `/db_search` command that yields a significant primary result will trigger the creation of a new thread dedicated to that entity.
    *   **Thread Creation & Title:**
        *   Upon a successful search, a new thread is automatically created in `#journal`.
        *   The thread title will be dynamically generated, containing the `entity_type`, `DB_ID` (if applicable), and `name` of the primary search result (e.g., `[ITEM_12345] Obsidian Edge - 2H Axe`, `[NPC_6789] Malfurion Stormrage`). This provides immediate context and a stable identifier for easy reference.
    *   **Embed Presentation (Initial Post):**
        *   The first message in the newly created thread will be a rich Discord embed, dynamically populated using the detailed schemas (`2.3.2 Canonical Data Schemas`) and image assets (`2.3.2.10 images` table) from our `architecture_UI_UX.md`.
        *   **Thematic Coloring:** Embed `color` will be dynamically set based on the `quality` (for items), `spell_school` (for spells), or `faction_alignment` (for NPCs/Factions) data, derived directly from the corresponding schemas. This ensures visual consistency and thematic relevance.
        *   **Icons & Images:** `icon_url` (from `items`, `spells`, `talents`) and `model_url`/`crest_url` (from `npcs`, `factions`) will populate embed `thumbnail` or `image` fields, with assets sourced directly from our `#graphics_vault` (via `images.img_graphics_vault_link`).
        *   **Fields:** All relevant data points from the entity's schema (e.g., stats, descriptions, relationships, categorization) will be parsed from `JSONB` or direct columns and presented as clearly labeled embed fields, facilitating easy digestion of information.
        *   **Accessibility:** Embeds will be designed with accessibility in mind, ensuring proper alt text for images (derived from entity names/descriptions), clear field labels, and a logical reading order for screen reader compatibility. Text alternatives for graphical representations will be prioritized.
        *   **External Links:** An embed footer will consistently include a direct link (`turtle_db_url`) back to the entity's original page on `https://database.turtlecraft.gg/`, providing traceability and external verification.
    *   **Replies & Thread Grouping:**
        *   **Related Entities/Context:** If a search result has strong relationships (e.g., an Item that is part of an Item Set, a Quest given by an NPC), subsequent replies within the thread could link to or provide summary embeds for these related entities. This enriches the context without cluttering the initial result.
        *   **Community Discussion & Follow-up:** The thread serves as a dedicated space for guild members to discuss the search result, ask follow-up questions, share personal insights, or request additional information related to the entity.
        *   **Archival Strategy:** An automated policy for thread expiry or archiving in `#journal` will be implemented to prevent clutter. This could involve moving older, inactive threads to an 'Archived Journal' category or automatically closing them after a defined period of inactivity.

### 2.2. Backend Architecture: The Chronicler Gateway Service & MCP Platform

Our backend architecture now clearly distinguishes between the production-critical synchronization service and the LLM-enabled development/testing platform.

#### 2.2.1 The Chronicler Gateway Service (Production Data Synchronization)

This is a dedicated, production-ready Python/FastAPI application. Its sole purpose is to serve as the reliable, non-LLM bridge between our PostgreSQL database and the Discord frontend. It operates in production without any direct LLM dependencies or external LLM API key requirements.

-   **Role:** Orchestrates all routine, high-volume data synchronization from PostgreSQL (triggered by Event Triggers) to Discord. This includes constructing Discord embeds, managing rate limits, creating/updating Discord threads and messages, and performing essential Discord API interactions.
-   **Operation:** Listens for PostgreSQL events (via a secure mechanism), processes the changes, and dispatches them to Discord.
-   **Security:** Designed for production security, including secure credentials management (environment variables), robust input validation, and adherence to Discord API best practices.
-   **LLM Integration:** Explicitly **does not** integrate with or require LLM API keys for its core DB-Discord synchronization functions.

#### 2.2.2 The MCP (Multi-Agent Control Plane) Platform (Development & LLM Operations)

The MCP Platform retains its original, well-defined scope as a flexible, LLM-enabled environment strictly for **development, testing, and specific Trailwarden-driven operations**. It is not part of the critical production path for daily DB-Discord synchronization.

-   **Role:**
    -   **Trailwarden-Driven Operations:** Facilitates complex, pre-planned operations orchestrated by the Trailwarden (via an LLM interface) that may involve database interaction and Discord updates.
    -   **LLM-Driven Features:** Hosts and tests LLM-enabled features (e.g., 'Portrait Forge', AI agents) in a controlled environment.
    -   **Development & Testing Infrastructure:** Provides a flexible platform for testing the Chronicler Gateway Service, new features, and architectural components.
-   **LLM Integration:** This component *may* integrate with LLM APIs (e.g., Gemini API) when explicitly required for its LLM-driven features or Trailwarden operations.
-   **Token Consumption:** LLM tokens are *only* consumed when specific LLM features of the MCP Platform are actively engaged by the Trailwarden in this development/testing context.

#### 2.2.3 Shared Backend Components

These components are utilized by both the Chronicler Gateway Service and the MCP Platform as needed.

-   **Webhook Handler:** Primarily for ingesting events or data from external sources, utilizing the FastAPI gateway for robust handling.
-   **Services:** Modular components for interacting with external systems (Discord API, PostgreSQL database).
-   **Models:** Pydantic models for rigorous data validation and structured data exchange.

### 2.3. Data Storage: The Heart of Truth

PostgreSQL, hosted via Supabase, is our single, canonical source of truth, ensuring data integrity, scalability, and complex querying capabilities.

#### 2.3.1 Canonical Data Enums (PostgreSQL Blueprint)

These enumerations represent standardized, lore-accurate values used across the Chronicler's database, ensuring data integrity and consistency. They directly inform Discord embed styling and categorization.

| Enum Name          | PostgreSQL Type | Values                                                                                              | Discord Reflection / Usage                                     |
| :----------------- | :-------------- | :-------------------------------------------------------------------------------------------------- | :------------------------------------------------------------- |
| `item_quality_enum`| `SMALLINT`      | `0` (Poor), `1` (Common), `2` (Uncommon), `3` (Rare), `4` (Epic), `5` (Legendary)                     | Defines Discord embed color, rarity display.                    |
| `character_race`   | `VARCHAR(20)`   | `Human`, `Dwarf`, `Night Elf`, `Gnome`, `Orc`, `Troll`, `Tauren`, `Undead`, `Goblin`, `High Elf`, `Other` | For character sheet embeds, filtering.                          |
| `character_class`  | `VARCHAR(20)`   | `Warrior`, `Paladin`, `Hunter`, `Rogue`, `Priest`, `Shaman`, `Mage`, `Warlock`, `Druid`                 | For character sheet embeds, talent tree validation.             |
| `character_role`   | `VARCHAR(20)`   | `Tank`, `Healer`, `DPS`                                                                             | For character sheet embeds, recruitment filtering.              |
| `character_status` | `VARCHAR(20)`   | `PENDING`, `REGISTERED`, `REJECTED`, `DECEASED`, `BURIED`                                           | Defines character lifecycle state, channel placement.           |
| `creature_type`    | `VARCHAR(30)`   | `Beast`, `Demon`, `Dragonkin`, `Elemental`, `Giant`, `Humanoid`, `Mechanical`, `Undead`, `Critter`, `Totem`, `Other` | For NPC embeds, search filtering.                               |
| `spell_school`     | `VARCHAR(20)`   | `Physical`, `Arcane`, `Fire`, `Frost`, `Nature`, `Shadow`, `Holy`                                   | Defines spell embed color, search filtering.                    |
| `faction_alignment`| `VARCHAR(20)`   | `Alliance`, `Horde`, `Neutral`, `Hostile`                                                           | Defines embed color for NPCs/Quests, relationship display.      |
| `quest_type`       | `VARCHAR(30)`   | `Normal`, `Daily`, `Dungeon`, `Raid`, `Profession`, `Class Quest`, `Legendary`                      | For quest embeds, categorization.                               |

#### 2.3.2 Core Entity Schemas (PostgreSQL Blueprint)

These blueprints detail the PostgreSQL table structures for the Chronicler's core entities, informed by our web scraping strategy and designed for seamless Discord frontend integration.

#### 2.3.2.1 `characters` Table

This table stores comprehensive data for every registered character, designed as a robust PostgreSQL structure.

| Column                | Type                       | Nullable | Default   | Constraints / Notes                                                                                                                                                                                                                                    | Discord Frontend Reflection                                                                                                    |
| :-------------------- | :------------------------- | :------- | :-------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------- |
| `id`                  | `SERIAL`                   | `FALSE`  | `AUTO`    | Primary Key. Auto-incrementing unique identifier.                                                                                                                                                                                        | Internal ID, often prefixed in Discord thread titles (e.g., `[CHAR_123]`)                                                      |
| `discord_user_id`     | `BIGINT`                   | `FALSE`  |           | Discord Snowflake ID of the user who owns the character. Foreign Key to a `users` table (future).                                                                                                                                        | Links character to owner, for DMs and permissions.                                                                             |
| `discord_username`    | `VARCHAR(64)`              | `FALSE`  |           | Discord username of the owner (cached, denormalized for convenience).                                                                                                                                                                  | Displayed in embeds for ownership.                                                                                             |
| `name`                | `VARCHAR(64)`              | `FALSE`  |           | Character's in-game name. `UNIQUE` constraint.                                                                                                                                                                                           | Main title of character sheet embed, Discord thread title.                                                                     |
| `race`                | `character_race`           | `FALSE`  |           | Character's race (ENUM: Human, Dwarf, etc.).                                                                                                                                                                                           | Displayed in character sheet embed.                                                                                            |
| `class`               | `character_class`          | `FALSE`  |           | Character's class (ENUM: Warrior, Paladin, etc.).                                                                                                                                                                                      | Displayed in character sheet embed, used for talent lookup.                                                                    |
| `roles`               | `TEXT[]`                   | `FALSE`  | `{}`      | Array of character's primary roles (e.g., `{'Tank', 'Healer', 'DPS'}`).                                                                                                                                                                | Displayed in character sheet embed, recruitment filtering.                                                                     |
| `professions`         | `TEXT[]`                   | `TRUE`   | `{}`      | Array of character's professions. Can be empty.                                                                                                                                                                                          | Displayed in character sheet embed.                                                                                            |
| `backstory`           | `TEXT`                     | `FALSE`  |           | Character's detailed backstory. Max 1024 chars.                                                                                                                                                                                        | Embed field content.                                                                                                           |
| `personality`         | `TEXT`                     | `TRUE`   |           | Character's personality description. Max 1024 chars.                                                                                                                                                                                   | Embed field content.                                                                                                           |
| `quotes`              | `TEXT`                     | `TRUE`   |           | Memorable character quotes. Max 1024 chars.                                                                                                                                                                                            | Embed field content.                                                                                                           |
| `portrait_url`        | `TEXT`                     | `TRUE`   |           | URL to character's portrait image. Defaults to `DEFAULT_PORTRAIT_URL` if not provided.                                                                                                                                                 | Embed `thumbnail` or `image` field. Source for `#graphics-storage`.                                                            |
| `trait_1`             | `VARCHAR(128)`             | `FALSE`  |           | External visible trait 1.                                                                                                                                                                                                              | Embed field content.                                                                                                           |
| `trait_2`             | `VARCHAR(128)`             | `FALSE`  |           | External visible trait 2.                                                                                                                                                                                                              | Embed field content.                                                                                                           |
| `trait_3`             | `VARCHAR(128)`             | `FALSE`  |           | External visible trait 3.                                                                                                                                                                                                              | Embed field content.                                                                                                           |
| `status`              | `character_status`         | `FALSE`  | `PENDING` | Current status of the character (ENUM: PENDING, REGISTERED, REJECTED, DECEASED, BURIED).                                                                                                                                               | Determines visibility, channel placement (`#recruitment`, `#character_sheet_vault`, `#cemetery`).                             |
| `is_confirmed`        | `BOOLEAN`                  | `FALSE`  | `FALSE`   | Flag if user has confirmed registration.                                                                                                                                                                                               | Internal, affects `status` transitions.                                                                                        |
| `request_sdxl`        | `BOOLEAN`                  | `FALSE`  | `FALSE`   | Flag if user requested AI portrait generation.                                                                                                                                                                                         | Internal, triggers AI agent.                                                                                                   |
| `recruitment_msg_id`  | `BIGINT`                   | `TRUE`   |           | Discord Snowflake ID of the recruitment message in `#recruitment`.                                                                                                                                                                     | Links to initial recruitment post for context.                                                                                 |
| `forum_post_id`       | `BIGINT`                   | `TRUE`   |           | Discord Snowflake ID of the main forum post for this character (in `#character_sheet_vault` or `#cemetery`). `UNIQUE` constraint.                                                                                                    | Primary link to Discord character sheet/memorial.                                                                              |
| `reviewed_by_user_id` | `BIGINT`                   | `TRUE`   |           | Discord Snowflake ID of the officer who approved/rejected the character. Foreign Key to `users` table.                                                                                                                                 | Displayed in embeds (e.g., 'Approved by:').                                                                                    |
| `embed_json`          | `JSONB`                    | `FALSE`  | `{}`      | Canonical JSON representation of the last Discord embed sent for this character. Ensures atomic updates.                                                                                                                               | Directly populates Discord embed.                                                                                              |
| `death_cause`         | `VARCHAR(256)`             | `TRUE`   |           | Brief description of the cause of death (for `/bury`).                                                                                                                                                                                 | Displayed in `#cemetery` embed.                                                                                                |
| `death_story`         | `TEXT`                     | `TRUE`   |           | In-character narrative of the character's demise (for `/bury`). Defaults to "unknown".                                                                                                                                                 | Detailed content for `#cemetery` embed.                                                                                        |
| `talents_json`        | `JSONB`                    | `TRUE`   | `{}`      | JSON representation of the character's current talent build.                                                                                                                                                                           | Used by `/talent audit` and for character sheet embed display.                                                                 |
| `created_at`          | `TIMESTAMP WITH TIME ZONE` | `FALSE`  | `NOW()`   | Timestamp of character registration.                                                                                                                                                                                                   | Displayed in embeds.                                                                                                           |
| `updated_at`          | `TIMESTAMP WITH TIME ZONE` | `FALSE`  | `NOW()`   | Last modification timestamp of the character record.                                                                                                                                                                                   | Displayed in embeds (e.g., 'Last updated:').                                                                                   |
| `notes`               | `TEXT`                     | `TRUE`   |           | Administrative notes for officers (not visible to general members).                                                                                                                                                                    | Internal use only.                                                                                                             |

#### 2.3.2.2 `talents` Table

This table stores detailed information for each individual talent in Turtle WoW (1.18.1+), acquired via web scraping.

| Column           | Type                       | Nullable | Default | Constraints / Notes                                                                   | Discord Frontend Reflection                                    |
| :--------------- | :------------------------- | :------- | :------ | :------------------------------------------------------------------------------------ | :------------------------------------------------------------- |
| `id`             | `VARCHAR(128)`             | `FALSE`  |         | Primary Key. Unique identifier, e.g., `warrior_arms_improvedheroicstrike`.           | Used in `/talent audit` feedback, talent tree embeds.          |
| `name`           | `VARCHAR(64)`              | `FALSE`  |         | Display name of the talent.                                                           | Displayed in embeds.                                           |
| `tree_id`        | `VARCHAR(64)`              | `FALSE`  |         | Foreign Key to `talent_trees.id`. E.g., `warrior_arms`.                               | Links talent to its tree for contextual display.               |
| `tier`           | `SMALLINT`                 | `FALSE`  |         | The tier (row) in the talent tree (1-7). `CHECK (tier >= 1 AND tier <= 7)`.          | Positional data for visual representation.                     |
| `column`         | `SMALLINT`                 | `TRUE`   | `NULL`  | The column in the talent tree (1-4). `CHECK (column >= 1 AND column <= 4)`.          | Positional data for visual representation.                     |
| `max_rank`       | `SMALLINT`                 | `FALSE`  | `1`     | Maximum purchasable ranks for the talent. `CHECK (max_rank >= 1)`.                   | Displayed in embeds, used for validation.                      |
| `description`    | `TEXT`                     | `FALSE`  |         | Base rank description of the talent.                                                  | Displayed in embeds (e.g., tooltip).                           |
| `icon_url`       | `TEXT`                     | `FALSE`  |         | Direct URL to the talent's icon image.                                                | Embed thumbnail, source for `#graphics-storage`.               |
| `prerequisite_id`| `VARCHAR(128)`             | `TRUE`   | `NULL`  | Foreign Key to `talents.id`. ID of the talent required to unlock this one.             | Used for validation in `/talent audit`.                        |
| `points_req`     | `SMALLINT`                 | `FALSE`  | `0`     | Points required in the talent tree to unlock this tier. Calculated as `(tier-1)*5`.  | Used for validation in `/talent audit`.                        |
| `created_at`     | `TIMESTAMP WITH TIME ZONE` | `FALSE`  | `NOW()` | Timestamp of record creation.                                                         | Internal.                                                      |
| `updated_at`     | `TIMESTAMP WITH TIME ZONE` | `FALSE`  | `NOW()` | Last modification timestamp.                                                          | Internal.                                                      |

#### 2.3.2.3 `talent_trees` Table

This table stores metadata for each talent tree in Turtle WoW (1.18.1+), acquired via web scraping.

| Column           | Type                       | Nullable | Default | Constraints / Notes                                         | Discord Frontend Reflection                                |
| :--------------- | :------------------------- | :------- | :------ | :---------------------------------------------------------- | :--------------------------------------------------------- |
| `id`             | `VARCHAR(64)`              | `FALSE`  |         | Primary Key. Unique identifier, e.g., `warrior_arms`.       | Used in talent tree selection.                             |
| `class`          | `character_class`          | `FALSE`  |         | Class this talent tree belongs to (ENUM).                   | Links tree to class.                                       |
| `name`           | `VARCHAR(64)`              | `FALSE`  |         | Display name of the talent tree (e.g., `ARMS`, `FURY`).     | Displayed in talent tree embeds.                           |
| `background_image_url` | `TEXT`               | `TRUE`   | `NULL`  | Direct URL to the background image for the talent tree.     | Embed background, source for `#graphics-storage`.          |
| `created_at`     | `TIMESTAMP WITH TIME ZONE` | `FALSE`  | `NOW()` | Timestamp of record creation.                               | Internal.                                                  |
| `updated_at`     | `TIMESTAMP WITH TIME ZONE` | `FALSE`  | `NOW()` | Last modification timestamp.                                | Internal.                                                  |

#### 2.3.2.4 `items` Table

Stores detailed information for every item, acquired via web scraping, for `/db_search` and `#vault` integration.

| Column           | Type                       | Nullable | Default | Constraints / Notes                                                                        | Discord Frontend Reflection                                                              |
| :--------------- | :------------------------- | :------- | :------ | :----------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------- |
| `id`             | `BIGINT`                   | `FALSE`  |         | Primary Key. Item ID from Turtle DB.                                                       | Used in `/db_search` results, `[ITEM_ID]` in titles.                                     |
| `name`           | `VARCHAR(256)`             | `FALSE`  |         | Item's display name. `UNIQUE`.                                                             | Embed title, search results.                                                             |
| `turtle_db_url`  | `TEXT`                     | `FALSE`  |         | Direct URL to the item's page on Turtle DB.                                                | Embed footer link.                                                                       |
| `icon_url`       | `TEXT`                     | `FALSE`  |         | Direct URL to the item's icon image.                                                       | Embed thumbnail. Source for `#graphics-storage`.                                         |
| `quality`        | `item_quality_enum`        | `FALSE`  |         | Item quality (ENUM).                                                                       | **Embed `color`**, displayed text (e.g., `Rare`).                                        |
| `item_type`      | `VARCHAR(64)`              | `FALSE`  |         | Categorization: e.g., 'Armor', 'Weapon', 'Consumable'.                                     | Embed field, search filter (`type:`).                                                    |
| `item_subtype`   | `VARCHAR(64)`              | `TRUE`   | `NULL`  | Categorization: e.g., 'Cloth', 'One-Handed Sword'.                                         | Embed field, search filter (`subtype:`).                                                 |
| `inventory_slot` | `VARCHAR(64)`              | `TRUE`   | `NULL`  | Categorization: e.g., 'Head', 'Main Hand', 'Trinket'.                                      | Embed field, search filter (`slot:`).                                                    |
| `item_level`     | `SMALLINT`                 | `TRUE`   | `NULL`  | Item's effective level.                                                                    | Embed field.                                                                             |
| `required_level` | `SMALLINT`                 | `TRUE`   | `NULL`  | Minimum character level to equip/use. `CHECK (required_level >= 1 AND required_level <= 60)`. | Embed field.                                                                             |
| `binding`        | `VARCHAR(32)`              | `TRUE`   | `NULL`  | e.g., 'Binds when picked up', 'Binds when equipped'.                                       | Embed field.                                                                             |
| `armor`          | `INTEGER`                  | `TRUE`   | `NULL`  | Armor value (if applicable).                                                               | Embed field.                                                                             |
| `min_damage`     | `INTEGER`                  | `TRUE`   | `NULL`  | Minimum weapon damage (if applicable).                                                     | Embed field.                                                                             |
| `max_damage`     | `INTEGER`                  | `TRUE`   | `NULL`  | Maximum weapon damage (if applicable).                                                     | Embed field.                                                                             |
| `speed`          | `NUMERIC(4,2)`             | `TRUE`   | `NULL`  | Weapon speed (if applicable).                                                              | Embed field.                                                                             |
| `durability`     | `SMALLINT`                 | `TRUE`   | `NULL`  | Durability (if applicable).                                                                | Embed field.                                                                             |
| `sell_price_copper` | `INTEGER`               | `TRUE`   | `NULL`  | Sell price in copper.                                                                      | Embed field (converted to G/S/C).                                                        |
| `buy_price_copper`  | `INTEGER`               | `TRUE`   | `NULL`  | Buy price in copper.                                                                       | Embed field (converted to G/S/C).                                                        |
| `stats_json`     | `JSONB`                    | `TRUE`   | `{}`    | Flexible storage for variable stats (Str, Agi, Int, Stam, Spi, Crit, Haste, SP, AP, Resistances). | Parsed into multiple embed fields.                                                       |
| `use_effect_description` | `TEXT`             | `TRUE`   | `NULL`  | Description of item's 'Use:' effect.                                                       | Embed field.                                                                             |
| `equip_effect_description` | `TEXT`           | `TRUE`   | `NULL`  | Description of item's 'Equip:' effect.                                                     | Embed field.                                                                             |
| `set_id`         | `BIGINT`                   | `TRUE`   | `NULL`  | Foreign Key to `item_sets.id` if item is part of a set.                                    | Links to item set, used for set bonuses.                                                 |
| `source_type`    | `VARCHAR(64)`              | `TRUE`   | `NULL`  | e.g., 'Drop', 'Quest Reward', 'Vendor', 'Crafted'.                                         | Embed field.                                                                             |
| `source_details_json` | `JSONB`               | `TRUE`   | `{}`    | Flexible storage for source details (e.g., NPC ID, Quest ID, Vendor ID, Recipe ID).      | Parsed into embed fields (e.g., 'Dropped by: [NPC Name]').                               |
| `created_at`     | `TIMESTAMP WITH TIME ZONE` | `FALSE`  | `NOW()` | Timestamp of record creation.                                                              | Internal.                                                                                |
| `updated_at`     | `TIMESTAMP WITH TIME ZONE` | `FALSE`  | `NOW()` | Last modification timestamp.                                                               | Internal.                                                                                |

#### 2.3.2.5 `item_sets` Table

Stores metadata for item sets, linked to individual items.

| Column           | Type                       | Nullable | Default | Constraints / Notes                                                              | Discord Frontend Reflection                                      |
| :--------------- | :------------------------- | :------- | :------ | :------------------------------------------------------------------------------- | :--------------------------------------------------------------- |
| `id`             | `BIGINT`                   | `FALSE`  |         | Primary Key. Item Set ID from Turtle DB.                                         | Used in `/db_search` for sets.                                   |
| `name`           | `VARCHAR(256)`             | `FALSE`  |         | Item set's display name. `UNIQUE`.                                               | Embed title, search results.                                     |
| `turtle_db_url`  | `TEXT`                     | `FALSE`  |         | Direct URL to the item set's page on Turtle DB.                                  | Embed footer link.                                               |
| `icon_url`       | `TEXT`                     | `TRUE`   | `NULL`  | Icon for the set (if distinct from individual item icons).                       | Embed thumbnail. Source for `#graphics-storage`.                 |
| `required_level` | `SMALLINT`                 | `TRUE`   | `NULL`  | Minimum character level for the set bonus.                                       | Embed field.                                                     |
| `set_bonuses_json` | `JSONB`                  | `FALSE`  | `{}`    | Flexible storage for bonuses at 2, 4, 6, 8 pieces (e.g., `{'2': 'Bonus 1', '4': 'Bonus 2'}`). | Parsed into multiple embed fields.                               |
| `items_in_set_ids` | `BIGINT[]`               | `FALSE`  | `{}`    | Array of `items.id` belonging to this set.                                       | Links to individual item embeds, used for completion tracking.   |
| `created_at`     | `TIMESTAMP WITH TIME ZONE` | `FALSE`  | `NOW()` | Timestamp of record creation.                                                    | Internal.                                                        |
| `updated_at`     | `TIMESTAMP WITH TIME ZONE` | `FALSE`  | `NOW()` | Last modification timestamp.                                                     | Internal.                                                        |

#### 2.3.2.6 `npcs` Table

Stores data for Non-Player Characters (NPCs), for `/db_search` and contextual information.

| Column           | Type                       | Nullable | Default | Constraints / Notes                                                                        | Discord Frontend Reflection                                                    |
| :--------------- | :------------------------- | :------- | :------ | :----------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------- |
| `id`             | `BIGINT`                   | `FALSE`  |         | Primary Key. NPC ID from Turtle DB.                                                        | Used in `/db_search` results.                                                  |
| `name`           | `VARCHAR(256)`             | `FALSE`  |         | NPC's display name. `UNIQUE`.                                                              | Embed title, search results.                                                   |
| `turtle_db_url`  | `TEXT`                     | `FALSE`  |         | Direct URL to the NPC's page on Turtle DB.                                                 | Embed footer link.                                                             |
| `creature_type`  | `creature_type`            | `FALSE`  |         | Categorization: e.g., 'Humanoid', 'Beast'.                                                 | Embed field, search filter (`type:`).                                          |
| `race`           | `VARCHAR(64)`              | `TRUE`   | `NULL`  | NPC's specific race (e.g., 'Orc', 'Human').                                                | Embed field.                                                                   |
| `faction_id`     | `BIGINT`                   | `FALSE`  |         | Foreign Key to `factions.id`. NPC's primary faction.                                       | Links to faction info, determines embed `color` (via `factions` table).        |
| `level`          | `SMALLINT`                 | `TRUE`   | `NULL`  | NPC's level. `CHECK (level >= 1 AND level <= 63)`.                                         | Embed field.                                                                   |
| `classification` | `VARCHAR(64)`              | `TRUE`   | `NULL`  | e.g., 'Normal', 'Elite', 'Boss'.                                                           | Embed field.                                                                   |
| `zone`           | `VARCHAR(128)`             | `TRUE`   | `NULL`  | Primary zone where the NPC is found.                                                       | Embed field.                                                                   |
| `coordinates_json` | `JSONB`                  | `TRUE`   | `NULL`  | Flexible storage for coordinates (e.g., `{'x': [10, 20], 'y': [30, 40]}`).                | Parsed for map links or coordinate display.                                    |
| `role`           | `VARCHAR(64)`              | `TRUE`   | `NULL`  | e.g., 'Vendor', 'Quest Giver', 'Trainer'.                                                  | Embed field.                                                                   |
| `model_url`      | `TEXT`                     | `TRUE`   | `NULL`  | URL to NPC's 3D model or detailed image.                                                   | Embed `image`. Source for `#graphics-storage`.                                 |
| `abilities_json` | `JSONB`                    | `TRUE`   | `{}`    | Flexible storage for NPC abilities/spells.                                                 | Parsed for embed fields.                                                       |
| `is_vendor`      | `BOOLEAN`                  | `FALSE`  | `FALSE` | Flag if NPC sells items.                                                                   | Internal, search filter.                                                       |
| `is_quest_giver` | `BOOLEAN`                  | `FALSE`  | `FALSE` | Flag if NPC gives quests.                                                                  | Internal, search filter.                                                       |
| `created_at`     | `TIMESTAMP WITH TIME ZONE` | `FALSE`  | `NOW()` | Timestamp of record creation.                                                              | Internal.                                                                      |
| `updated_at`     | `TIMESTAMP WITH TIME ZONE` | `FALSE`  | `NOW()` | Last modification timestamp.                                                               | Internal.                                                                      |

#### 2.3.2.7 `quests` Table

Stores details for every quest, for `/db_search` and contextual linking.

| Column             | Type                       | Nullable | Default | Constraints / Notes                                                                        | Discord Frontend Reflection                                             |
| :----------------- | :------------------------- | :------- | :------ | :----------------------------------------------------------------------------------------- | :---------------------------------------------------------------------- |
| `id`               | `BIGINT`                   | `FALSE`  |         | Primary Key. Quest ID from Turtle DB.                                                      | Used in `/db_search` results.                                           |
| `title`            | `VARCHAR(256)`             | `FALSE`  |         | Quest's display title. `UNIQUE`.                                                           | Embed title, search results.                                            |
| `turtle_db_url`    | `TEXT`                     | `FALSE`  |         | Direct URL to the quest's page on Turtle DB.                                               | Embed footer link.                                                      |
| `quest_type`       | `quest_type`               | `FALSE`  |         | Categorization: e.g., 'Normal', 'Dungeon', 'Profession'.                                   | Embed field, search filter (`type:`).                                   |
| `required_level`   | `SMALLINT`                 | `FALSE`  | `1`     | Minimum character level to accept quest. `CHECK (required_level >= 1 AND required_level <= 60)`. | Embed field.                                                            |
| `zone`             | `VARCHAR(128)`             | `FALSE`  |         | Primary zone where the quest originates.                                                   | Embed field.                                                            |
| `quest_giver_npc_id` | `BIGINT`                 | `TRUE`   | `NULL`  | Foreign Key to `npcs.id`. NPC who gives the quest.                                         | Links to NPC embed, displayed as 'Giver:'.                               |
| `quest_turnin_npc_id` | `BIGINT`                | `TRUE`   | `NULL`  | Foreign Key to `npcs.id`. NPC who completes the quest.                                     | Links to NPC embed, displayed as 'Turn In:'.                             |
| `description`      | `TEXT`                     | `FALSE`  |         | Quest description/flavor text.                                                             | Embed field.                                                            |
| `objectives_json`  | `JSONB`                    | `FALSE`  | `{}`    | Flexible storage for objectives (e.g., `[{'type': 'kill', 'target_npc_id': 123, 'count': 5}]`). | Parsed into multiple embed fields.                                      |
| `completion_text`  | `TEXT`                     | `TRUE`   | `NULL`  | Text displayed upon quest completion.                                                      | Embed field.                                                            |
| `xp_reward`        | `INTEGER`                  | `FALSE`  | `0`     | Experience reward.                                                                         | Embed field.                                                            |
| `gold_reward_copper` | `INTEGER`                | `FALSE`  | `0`     | Gold reward in copper.                                                                     | Embed field (converted to G/S/C).                                       |
| `item_rewards_json` | `JSONB`                   | `TRUE`   | `{}`    | Flexible storage for item rewards (array of `{'item_id': 123, 'quantity': 1}`).          | Parsed into item links/embeds.                                          |
| `reputation_rewards_json` | `JSONB`             | `TRUE`   | `{}`    | Flexible storage for reputation rewards (array of `{'faction_id': 123, 'value': 500}`).  | Parsed into faction links/embeds.                                       |
| `created_at`       | `TIMESTAMP WITH TIME ZONE` | `FALSE`  | `NOW()` | Timestamp of record creation.                                                              | Internal.                                                               |
| `updated_at`       | `TIMESTAMP WITH TIME ZONE` | `FALSE`  | `NOW()` | Last modification timestamp.                                                               | Internal.                                                               |

#### 2.3.2.8 `spells` Table

Stores details for every spell, for `/db_search` and character abilities.

| Column           | Type                       | Nullable | Default | Constraints / Notes                                                                        | Discord Frontend Reflection                                     |
| :--------------- | :------------------------- | :------- | :------ | :----------------------------------------------------------------------------------------- | :-------------------------------------------------------------- |
| `id`             | `BIGINT`                   | `FALSE`  |         | Primary Key. Spell ID from Turtle DB.                                                      | Used in `/db_search` results.                                   |
| `name`           | `VARCHAR(128)`             | `FALSE`  |         | Spell's display name. `UNIQUE`.                                                            | Embed title, search results.                                    |
| `turtle_db_url`  | `TEXT`                     | `FALSE`  |         | Direct URL to the spell's page on Turtle DB.                                               | Embed footer link.                                              |
| `icon_url`       | `TEXT`                     | `FALSE`  |         | Direct URL to the exact spell's icon image.                                                | Embed thumbnail. Source for `#graphics-storage`.                |
| `spell_school`   | `spell_school`             | `FALSE`  |         | Spell's school (ENUM).                                                                     | **Embed `color`**, embed field, search filter.                  |
| `spell_type`     | `VARCHAR(64)`              | `TRUE`   | `NULL`  | Categorization: e.g., 'Direct Damage', 'Heal over Time'.                                   | Embed field, search filter.                                     |
| `rank`           | `VARCHAR(32)`              | `TRUE`   | `NULL`  | Spell rank (e.g., 'Rank 1', 'Master').                                                     | Embed field.                                                    |
| `cast_time`      | `VARCHAR(64)`              | `FALSE`  |         | Cast time (e.g., 'Instant', '2.5 sec cast').                                              | Embed field.                                                    |
| `cooldown`       | `VARCHAR(64)`              | `TRUE`   | `NULL`  | Cooldown duration (e.g., '30 sec', '5 min').                                               | Embed field.                                                    |
| `mana_cost`      | `VARCHAR(64)`              | `TRUE`   | `NULL`  | Mana cost or other resource cost.                                                          | Embed field.                                                    |
| `range`          | `VARCHAR(64)`              | `TRUE`   | `NULL`  | Spell range (e.g., '30 yd', 'Melee').                                                      | Embed field.                                                    |
| `duration`       | `VARCHAR(64)`              | `TRUE`   | `NULL`  | Spell duration (e.g., '30 sec', '2 min').                                                  | Embed field.                                                    |
| `target_type`    | `VARCHAR(64)`              | `TRUE`   | `NULL`  | e.g., 'Single Target', 'Area of Effect', 'Self'.                                           | Embed field.                                                    |
| `description`    | `TEXT`                     | `FALSE`  |         | Spell's detailed description.                                                              | Embed field.                                                    |
| `effect_details_json` | `JSONB`               | `TRUE`   | `{}`    | Flexible storage for spell effects (e.g., `[{'type': 'damage', 'value': 100, 'school': 'Fire'}]`). | Parsed into multiple embed fields.                                |
| `talent_id`      | `VARCHAR(128)`             | `TRUE`   | `NULL`  | Foreign Key to `talents.id` if spell is tied to a talent.                                  | Links to talent info.                                           |
| `created_at`     | `TIMESTAMP WITH TIME ZONE` | `FALSE`  | `NOW()` | Timestamp of record creation.                                                              | Internal.                                                       |
| `updated_at`     | `TIMESTAMP WITH TIME ZONE` | `FALSE`  | `NOW()` | Last modification timestamp.                                                               | Internal.                                                       |

#### 2.3.2.9 `factions` Table

Stores metadata for game factions, for contextual linking and theming.

| Column           | Type                       | Nullable | Default | Constraints / Notes                                                                        | Discord Frontend Reflection                                |
| :--------------- | :------------------------- | :------- | :------ | :----------------------------------------------------------------------------------------- | :--------------------------------------------------------- |
| `id`             | `BIGINT`                   | `FALSE`  |         | Primary Key. Faction ID from Turtle DB.                                                    | Used for linking, search filtering.                        |
| `name`           | `VARCHAR(128)`             | `FALSE`  |         | Faction's display name. `UNIQUE`.                                                          | Embed field.                                               |
| `turtle_db_url`  | `TEXT`                     | `TRUE`   | `NULL`  | Direct URL to the faction's page on Turtle DB.                                             | Embed footer link.                                         |
| `alignment`      | `faction_alignment`        | `FALSE`  |         | Faction's alignment (ENUM: Alliance, Horde, Neutral, Hostile).                             | **Embed `color`**, embed field.                            |
| `description`    | `TEXT`                     | `TRUE`   | `NULL`  | Faction description.                                                                       | Embed field.                                               |
| `crest_url`      | `TEXT`                     | `TRUE`   | `NULL`  | URL to faction's crest image.                                                              | Embed thumbnail. Source for `#graphics-storage`.           |
| `primary_color_hex` | `VARCHAR(7)`            | `TRUE`   | `NULL`  | Hex color code for thematic display (e.g., '#0070DD' for Alliance).                      | **Embed `color`** for related entities (NPCs, Quests).   |
| `created_at`     | `TIMESTAMP WITH TIME ZONE` | `FALSE`  | `NOW()` | Timestamp of record creation.                                                              | Internal.                                                  |
| `updated_at`     | `TIMESTAMP WITH TIME ZONE` | `FALSE`  | `NOW()` | Last modification timestamp.                                                               | Internal.                                                  |

#### 2.3.2.10 `images` Table (Enhanced)

This table stores comprehensive metadata for all images used by The Chronicler, serving as the central registry for the `#graphics_vault`.

| Column                  | Type                       | Nullable | Default     | Constraints / Notes                                                                         | Discord Frontend Reflection                                                              |
| :---------------------- | :------------------------- | :------- | :---------- | :------------------------------------------------------------------------------------------ | :--------------------------------------------------------------------------------------- |
| `id`                    | `SERIAL`                   | `FALSE`  | `AUTO`      | Primary Key. Auto-incrementing unique identifier.                                           | Internal ID, often prefixed in `#graphics_vault` thread titles (e.g., `[IMG_123]`).      |
| `img_origin_link`       | `TEXT`                     | `FALSE`  |             | The original URL where the image was sourced (e.g., Turtle DB icon URL, Imgur link).        | Displayed in `#graphics_vault` embed.                                                    |
| `img_graphics_vault_link` | `TEXT`                   | `FALSE`  |             | The CDN URL from Discord's `#graphics-storage` channel after upload. `UNIQUE`.              | **Main image URL for Discord embeds.** Source for `#graphics-storage` content.           |
| `original_filename`     | `VARCHAR(256)`             | `FALSE`  |             | The original filename of the image as uploaded or sourced.                                  | Displayed in `#graphics_vault` embed, thread title.                                      |
| `uploaded_by_user_id`   | `BIGINT`                   | `TRUE`   | `NULL`      | Discord Snowflake ID of the user who initiated the image upload (if `source_system='PlayerUpload'`). (FK to `users` table, future). | Displayed in `#graphics_vault` embed.                                                    |
| `source_system`         | `VARCHAR(64)`              | `FALSE`  |             | The system/method by which the image entered the vault (e.g., 'PlayerUpload', 'WebScrape', 'SystemGenerated', 'AdminUpload'). | Key for grouping and origin tracking. Displayed in embed, maps to Forum tag.             |
| `ownership_context`     | `VARCHAR(64)`              | `FALSE`  |             | Defines broader image ownership (e.g., 'Guild', 'User', 'System', 'Open Source').         | Displayed in `#graphics_vault` embed, potentially influences embed color, maps to Forum tag. |
| `usage_context`         | `VARCHAR(64)`              | `FALSE`  |             | Defines primary usage (e.g., 'Character Portrait', 'Item Icon', 'NPC Model', 'Spell Icon', 'Lore Asset', 'Tool Background'). | Displayed in `#graphics_vault` embed, used for filtering, maps to Forum tag.             |
| `entity_type`           | `VARCHAR(64)`              | `TRUE`   | `NULL`      | The type of entity this image is associated with (e.g., 'character', 'item', 'npc', 'spell'). | Used for generic linking.                                                                |
| `entity_id`             | `BIGINT`                   | `TRUE`   | `NULL`      | The `id` of the specific entity (e.g., `character.id`, `item.id`) this image is associated with. (FK to respective tables). | Links image to specific entity.                                                          |
| `category_tags`         | `TEXT[]`                   | `FALSE`  | `{}`        | Array of flexible tags for multi-dimensional grouping and search (e.g., `{'portrait', 'human', 'warrior'}`, `{'item_icon', 'weapon'}`). | Directly maps to Discord Forum tags for filtering and discoverability. Displayed in embed. |
| `provenance_notes`      | `TEXT`                     | `TRUE`   | `NULL`      | Notes on source, artist, generation (e.g., 'AI Generated by Midjourney', 'Official Blizzard Art'). | Displayed in `#graphics_vault` embed.                                                    |
| `permissions_level`     | `VARCHAR(32)`              | `FALSE`  | `Public`    | Defines who can use/view/modify this image (e.g., 'Public', 'Guild Only', 'Officer Only', 'Private'). | Influences embed visibility/usage, displayed in `#graphics_vault` embed.                 |
| `is_animated`           | `BOOLEAN`                  | `FALSE`  | `FALSE`     | Flag for GIF/animated images.                                                               | Displayed in `#graphics_vault` embed.                                                    |
| `hash_md5`              | `VARCHAR(32)`              | `TRUE`   | `NULL`      | MD5 hash of the image content for duplication detection. `UNIQUE`.                          | Internal, ensures unique image storage.                                                  |
| `upload_timestamp`      | `TIMESTAMP WITH TIME ZONE` | `FALSE`  | `NOW()`     | Timestamp of image upload to the vault.                                                     | Displayed in `#graphics_vault` embed.                                                    |
| `last_accessed_timestamp` | `TIMESTAMP WITH TIME ZONE` | `TRUE`   | `NULL`      | Last time the image was retrieved/used by the bot.                                          | Internal, for usage tracking.                                                            |
| `metadata_json`         | `JSONB`                    | `TRUE`   | `{}`        | Flexible storage for additional, unstructured metadata (e.g., AI prompt, specific sizing info). | Parsed into additional `#graphics_vault` embed fields.                                   |
| `status`                | `VARCHAR(32)`              | `FALSE`  | `active`    | 'active', 'archived', 'deleted', 'pending_review'.                                          | Controls image availability/visibility.                                                  |
| `created_at`            | `TIMESTAMP WITH TIME ZONE` | `FALSE`  | `NOW()`     | Timestamp of record creation.                                                               | Internal.                                                                                |
| `updated_at`            | `TIMESTAMP WITH TIME ZONE` | `FALSE`  | `NOW()`     | Last modification timestamp.                                                                | Internal.                                                                                |

### 2.5. Data Synchronization: The Flow of Truth

The mechanism for propagating data changes from our source of truth (PostgreSQL) to our frontend (Discord) is pivotal.

-   **PostgreSQL Database Event Triggers:** This is the primary, real-time, and robust mechanism. Triggers on database tables will fire upon `INSERT`, `UPDATE`, or `DELETE` operations.
-   **Chronicler Gateway Service as Event Orchestrator:** These database events will signal the Chronicler Gateway Service. This service will then process these events, identify the relevant Discord entities (threads, messages), and execute the necessary Discord API calls.
-   **Safe Update Strategy (Rate Limit Mitigation):**
    *   **Edits vs. Replies:** Updates to existing data primarily involve editing the original Forum parent post. New, distinct events (e.g., a character's death, a quest update) will generate new replies.
    *   **Batched & Debounced Updates:** To respect Discord API rate limits, the Chronicler Gateway Service will queue and consolidate multiple database-triggered updates into fewer, batched Discord API calls. This ensures responsiveness without overwhelming Discord's infrastructure.

### 2.6. MCP Platform: The Testing Crucible

As defined in `2.2.2 The MCP (Multi-Agent Control Plane) Platform (Development & LLM Operations)`, this platform serves as a **robust, trustworthy testing environment**. It is strictly for development and testing, and will not be deployed to production for core DB-Discord synchronization. This allows for rigorous validation of all architectural components, especially the complex data flows, Event Triggers, and Discord interactions, before live deployment. User-driven operations (via LLM) will leverage this testing framework to achieve complex Discord operations.

## 3. User Experience (UX) Design Principles: Crafting Immersion

-   **Immersive Roleplay:** All commands, responses, and bot interactions will maintain an in-character tone consistent with the world of Azeroth.
-   **Clarity and Guidance:** Interactive flows will be intuitive, providing clear instructions at each step.
-   **Feedback:** Users will receive immediate and contextual confirmation or status updates for their actions.
-   **Accessibility:** Information will be presented in an easily digestible, visually rich format (e.g., Discord embeds, clear categorizations).

## 4. Future Considerations & Migrations: The Unwritten Chapters

-   **Supabase PostgreSQL:** The ongoing, critical establishment of PostgreSQL via Supabase as the primary data store for enhanced scalability and reliability.
-   **Enhanced Image Handling:** Building upon the `#graphics-storage` foundation for even more sophisticated asset management and delivery.
-   **Scalability:** Continuous optimization of the Chronicler Gateway Service and Discord interactions for our growing guild.

## 5. Open Questions & Debates: Now Settled Laws

-   **Forum Channels:** Definitive use of Forum channels for `#character_sheet_vault`, `#cemetery`, `#vault`, `#recruitment`, and `#journal` is established.
-   **Data Synchronization:** PostgreSQL Database Event Triggers are the chosen robust mechanism for real-time data propagation from the database to Discord.
-   **Database Triggers:** Confirmed as the reliable backbone for Discord updates, integrated with the Chronicler Gateway Service for smart, rate-limited interactions.
-   **Data-Driven Design:** Web scraping is now integrated into the architectural plan to inform DB schemas and Discord frontend dynamically.

---
© 2024 Azeroth Bound Guild. All rights reserved.