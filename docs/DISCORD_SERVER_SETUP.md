# Discord Server Setup Guide for The Chronicler

This guide will walk you through the process of setting up a Discord server to work with The Chronicler bot. Following these steps is crucial for the bot to function correctly.

---

## Step 1: Enable Developer Mode in Discord

Before you can get the necessary IDs for channels and roles, you must enable Developer Mode in your Discord client.

1.  Open your Discord settings by clicking the **User Settings** gear icon (⚙️) next to your username.
2.  Go to the **Advanced** tab.
3.  Toggle **Developer Mode** on.
4.  Click **Esc** to close settings.

With Developer Mode enabled, you can right-click on servers, channels, and roles to get a "Copy ID" option.

## Step 2: Create the Discord Bot Application

The Chronicler needs a bot identity to connect to Discord.

1.  Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2.  Click **New Application** in the top right corner and give it a name (e.g., "The Chronicler").
3.  Navigate to the **Bot** tab on the left menu.
4.  Click **Add Bot**, then **Yes, do it!**.
5.  **Get the Token:** Under the bot's username, click **Reset Token**. Copy this token immediately and save it. This is your `DISCORD_BOT_TOKEN` for the `.env` file. **Never share this token!**
6.  **Enable Privileged Intents:** Scroll down and enable the following intents:
    *   **SERVER MEMBERS INTENT** (Required for the bot to see guild members and their roles).
    *   **MESSAGE CONTENT INTENT** (Required for the bot to read commands and user messages).

## Step 3: Invite The Bot to Your Server

Now, you need to generate an invitation link to add the bot to your server.

1.  In the Developer Portal, go to the **OAuth2** -> **URL Generator** tab.
2.  Under **SCOPES**, select:
    *   `bot`
    *   `applications.commands` (to allow slash commands)
3.  Under **BOT PERMISSIONS**, select the following permissions:
    *   `Send Messages`
    *   `Send Messages in Threads`
    *   `Create Public Threads`
    *   `Embed Links`
    *   `Attach Files`
    *   `Read Message History`
    *   `Use External Emojis`
    *   `Add Reactions`
    *   `Manage Messages` (for cleaning up posts)
    *   `Manage Threads` (for archiving burial threads)
    *   `Mention @everyone, @here, and All Roles`
4.  Copy the **Generated URL** at the bottom of the page.
5.  Paste the URL into your browser, select the server you want to add the bot to, and click **Authorize**.

## Step 4: Set Up Server Channels

The bot requires specific channels to operate.

1.  **Get Server ID:** Right-click on your server icon in the server list and select **Copy ID**. This is your `GUILD_ID`.
2.  **Create Channels:**
    *   **Recruitment Channel:** Create a standard text channel (e.g., `#recruitment`). Right-click on it and **Copy ID**. This is your `RECRUITMENT_CHANNEL_ID`.
    *   **Character Vault Channel:** Create a **Forum Channel** (e.g., `#character-sheet-vault`). This is where approved character sheets will live. Right-click and **Copy ID**. This is your `FORUM_CHANNEL_ID`.
    *   **Cemetery Channel:** Create a standard text channel (e.g., `#cemetery`). This is where buried characters are memorialized. Right-click and **Copy ID**. This is your `CEMETERY_CHANNEL_ID`.

## Step 5: Set Up Server Roles

The bot uses a role-based system for permissions.

1.  Go to **Server Settings** -> **Roles**.
2.  Create the following roles (you can name them whatever you want, but these are the defaults):
    *   `Wanderer` (Basic member role)
    *   `Seeker` (Established member role)
    *   `Pathfinder` (Officer role)
    *   `Trailwarden` (Senior Officer role)
3.  For each role you create, right-click on it in the roles list and select **Copy ID**. These are your `WANDERER_ROLE_ID`, `SEEKER_ROLE_ID`, `PATHFINDER_ROLE_ID`, and `TRAILWARDEN_ROLE_ID`.

## Step 6: Configure Your `.env` File

Open your `.env` file and populate it with the IDs you just collected.

```env
# .env example

# --- Discord Configuration ---
DISCORD_BOT_TOKEN="YOUR_BOT_TOKEN_HERE"
GUILD_ID="YOUR_SERVER_ID_HERE"

# Channel IDs
RECRUITMENT_CHANNEL_ID="ID_OF_RECRUITMENT_CHANNEL"
FORUM_CHANNEL_ID="ID_OF_FORUM_CHANNEL"
CEMETERY_CHANNEL_ID="ID_OF_CEMETERY_CHANNEL"

# Guild Member Role IDs (for /register_character access)
WANDERER_ROLE_ID="ID_OF_WANDERER_ROLE"
SEEKER_ROLE_ID="ID_OF_SEEKER_ROLE"

# Officer Role IDs (for /bury and approvals)
PATHFINDER_ROLE_ID="ID_OF_PATHFINDER_ROLE"
TRAILWARDEN_ROLE_ID="ID_OF_TRAILWARDEN_ROLE"

# Officer Role Mentions (for notifications on new characters)
# To get the mention string, type \@<RoleName> in Discord and copy the output.
# It should look like <@&ROLE_ID>.
PATHFINDER_ROLE_MENTION="<@&PATHFINDER_ROLE_ID>"
TRAILWARDEN_ROLE_MENTION="<@&TRAILWARDEN_ROLE_ID>"

# ... (other settings like Google Sheets, etc.)
```

---

Once your server is set up and your `.env` file is complete, you are ready to run The Chronicler!
