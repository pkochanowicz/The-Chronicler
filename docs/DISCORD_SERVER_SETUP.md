# Discord Server Setup Guide for The Chronicler (FastAPI/Supabase Edition)

This guide provides instructions for setting up your Discord server to work with The Chronicler bot, powered by a FastAPI backend and Supabase PostgreSQL. Following these steps is crucial for the bot to function correctly and for the FastAPI application to receive Discord interactions.

---

## Step 1: Enable Developer Mode in Discord

Before you can get the necessary IDs for channels and roles, you must enable Developer Mode in your Discord client.

1.  Open your Discord settings by clicking the **User Settings** gear icon (⚙️) next to your username.
2.  Go to the **Advanced** tab.
3.  Toggle **Developer Mode** on.
4.  Click **Esc** to close settings.

With Developer Mode enabled, you can right-click on servers, channels, and roles to get a "Copy ID" option.

## Step 2: Create the Discord Bot Application

The Chronicler needs a bot identity to connect to Discord and process slash commands/interactions.

1.  Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2.  Click **New Application** in the top right corner and give it a name (e.g., "The Chronicler").
3.  Navigate to the **Bot** tab on the left menu.
4.  Click **Add Bot**, then **Yes, do it!**.
5.  **Get the Token:** Under the bot's username, click **Reset Token**. Copy this token immediately and save it. This is your `DISCORD_TOKEN` for the `.env` file. **Never share this token!**
6.  **Enable Privileged Gateway Intents:** Scroll down and enable the following intents:
    *   **PRESENCE INTENT** (If your bot needs to track user presence)
    *   **SERVER MEMBERS INTENT** (Required for the bot to see guild members and their roles).
    *   **MESSAGE CONTENT INTENT** (Required for the bot to read commands and user messages).

## Step 3: Invite The Bot to Your Server

Now, you need to generate an invitation link to add the bot to your server.

1.  In the Developer Portal, go to the **OAuth2** -> **URL Generator** tab.
2.  Under **SCOPES**, select:
    *   `bot`
    *   `applications.commands` (to allow slash commands)
3.  Under **BOT PERMISSIONS**, select the following permissions:
    *   `Read Message History`
    *   `Send Messages`
    *   `Send Messages in Threads`
    *   `Create Public Threads`
    *   `Embed Links`
    *   `Attach Files`
    *   `Use External Emojis`
    *   `Add Reactions`
    *   `Manage Messages` (for cleaning up posts, e.g., in recruitment)
    *   `Manage Threads` (for archiving burial threads)
    *   `Manage Channels` (if the bot needs to create/manage channels, e.g., forum posts)
    *   `Mention @everyone, @here, and All Roles`
4.  Copy the **Generated URL** at the bottom of the page.
5.  Paste the URL into your browser, select the server you want to add the bot to, and click **Authorize**.

## Step 4: Set Up Server Channels

The bot requires specific channels to operate.

1.  **Get Server ID:** Right-click on your server icon in the server list and select **Copy ID**. This is your `GUILD_ID`.
2.  **Create Channels:**
    *   **Recruitment Channel:** Create a standard text channel (e.g., `#recruitment`). Right-click on it and **Copy ID**. This is your `RECRUITMENT_CHANNEL_ID`.
    *   **Character Vault Forum Channel:** Create a **Forum Channel** (e.g., `#character-sheet-vault`). This is where approved character sheets will live. Right-click on the category or the forum channel itself and **Copy ID**. This is your `CHARACTER_SHEET_VAULT_CHANNEL_ID`.
    *   **Cemetery Channel:** Create a standard text channel (e.g., `#cemetery`). This is where buried characters are memorialized. Right-click and **Copy ID**. This is your `CEMETERY_CHANNEL_ID`.

## Step 5: Set Up Server Roles

The bot uses a role-based system for permissions.

1.  Go to **Server Settings** -> **Roles**.
2.  Create the following roles (you can name them whatever you want, but these are suggested):
    *   `Wanderer` (Basic member role)
    *   `Seeker` (Established member role)
    *   `Pathfinder` (Officer role)
    *   `Trailwarden` (Senior Officer role)
3.  For each role you create, right-click on it in the roles list and select **Copy ID**. These are your `WANDERER_ROLE_ID`, `SEEKER_ROLE_ID`, `PATHFINDER_ROLE_ID`, and `TRAILWARDEN_ROLE_ID`.

## Step 6: Configure Discord Application for Interactions (FastAPI Webhooks)

This is a critical step for linking your FastAPI application to Discord's interaction system (e.g., for slash commands, buttons, and modals).

1.  In the Discord Developer Portal, navigate to your application.
2.  Go to the **General Information** tab.
3.  **Interactions Endpoint URL:**
    *   In the `Interactions Endpoint URL` field, enter the full URL to your FastAPI application's `/webhooks/discord` endpoint.
    *   **Important:** This must be a publicly accessible URL where your FastAPI application is deployed (e.g., `https://your-chronicler-app.fly.dev/webhooks/discord` or `https://your-ngrok-tunnel.ngrok.io/webhooks/discord` for local testing).
    *   **Save Changes.**
4.  **Public Key:** Discord will use the `Public Key` shown on this page to verify the authenticity of interactions. Your FastAPI application's `/webhooks/discord` endpoint will use this for signature verification.
    *   You **do not** need to copy this key into your `.env` as FastAPI frameworks handle it internally.

## Step 7: Update Your `.env` File (FastAPI/Supabase)

Open your `.env` file (or create one by copying `.env.example`) and populate it with the IDs and credentials you just collected, plus your database configuration.

```env
# .env (Example - Copy from .env.example)

# --- Discord Configuration ---
DISCORD_TOKEN="YOUR_BOT_TOKEN_HERE" # From Step 2
GUILD_ID="YOUR_SERVER_ID_HERE"      # From Step 4

# Channel IDs (From Step 4)
RECRUITMENT_CHANNEL_ID="ID_OF_RECRUITMENT_CHANNEL"
CHARACTER_SHEET_VAULT_CHANNEL_ID="ID_OF_CHARACTER_SHEET_VAULT_CHANNEL"
CEMETERY_CHANNEL_ID="ID_OF_CEMETERY_CHANNEL"

# Guild Member Role IDs (From Step 5)
WANDERER_ROLE_ID="ID_OF_WANDERER_ROLE"
SEEKER_ROLE_ID="ID_OF_SEEKER_ROLE"
PATHFINDER_ROLE_ID="ID_OF_PATHFINDER_ROLE"
TRAILWARDEN_ROLE_ID="ID_OF_TRAILWARDEN_ROLE"

# Officer Role Mentions (for notifications on new characters)
# To get the mention string, type \@<RoleName> in Discord and copy the output.
# It should look like <@&ROLE_ID>.
PATHFINDER_ROLE_MENTION="<@&PATHFINDER_ROLE_ID>"
TRAILWARDEN_ROLE_MENTION="<@&TRAILWARDEN_ROLE_ID>"

# --- Supabase / PostgreSQL Configuration ---
# The full connection string for your PostgreSQL database (e.g., from Supabase)
DATABASE_URL="postgresql+asyncpg://user:password@host:port/database_name" # From Supabase project settings

# Your Supabase Project URL (e.g., https://abcde12345.supabase.co)
SUPABASE_URL="your_supabase_project_url_here"

# Your Supabase Anon Key (public key for client-side use, if applicable)
SUPABASE_KEY="your_supabase_anon_key_here"

# --- Webhook Security (FastAPI) ---
# Secret key for Discord webhook authentication (min 32 characters)
# Generate with: python -c 'import secrets; print(secrets.token_urlsafe(32))'
WEBHOOK_SECRET="generate_a_random_32_character_secret_here" # Used by your FastAPI app to verify incoming webhooks

# --- Bot Behavior ---
INTERACTIVE_TIMEOUT_SECONDS=300

# --- Visual Defaults ---
DEFAULT_PORTRAIT_URL="https://i.imgur.com/default_placeholder.png"

# --- Production Deployment (Optional) ---
# PORT=8080 # Port for webhook server (auto-set by hosting platforms)
```

---

Once your Discord server is set up, your Discord application is configured for interactions, and your `.env` file is complete, you are ready to deploy and run The Chronicler!