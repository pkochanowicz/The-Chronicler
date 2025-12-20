# The Chronicler - Deployment Checklist
**Version:** 1.0.0 (Pre-2.0.0)
**Environment:** Fly.io Production

This checklist should be used after every deployment to ensure the bot is fully operational.

---

## Post-Deployment Verification

### 1. Bot Deployment ✅

- [ ] **Bot Online:** The Chronicler appears as "Online" in Discord.
- [ ] **Slash Commands:** The `/register_character` and `/bury` commands are visible and accessible in Discord.
- [ ] **Channel Access:** The bot can send messages in all configured channels (`#recruitment`, `#character-sheet-vault`, `#cemetery`).
- [ ] **Permissions Check:** The bot has the following required permissions:
  - `Send Messages`
  - `Send Messages in Threads`
  - `Create Public Threads`
  - `Embed Links`
  - `Attach Files`
  - `Read Message History`
  - `Use External Emojis`
  - `Add Reactions`
  - `Manage Messages`
  - `Manage Threads`
  - `Mention @everyone, @here, and All Roles` (in the cemetery channel)

### 2. Webhook System ✅

- [ ] **Webhook URL:** The webhook URL (`https://<your-app-name>.fly.dev/webhook`) is accessible.
- [ ] **Secret Validation:** A `POST` request with an invalid secret is correctly rejected with a `400` or `401` error.
- [ ] **Google Apps Script:** The Apps Script can successfully `POST` to the webhook URL.
- [ ] **Sheet Trigger:** A change in the Google Sheet (e.g., setting `confirmation` to `TRUE`) correctly fires the webhook.

### 3. Interactive Flows (E2E Test) ✅

- [ ] **`/register_character`:** The 12-step registration flow can be started and completed successfully.
  - [ ] Input validation (race, class, roles) works correctly.
  - [ ] The embed preview is displayed correctly.
  - [ ] The final submission is written to the Google Sheet.
- [ ] **`/bury`:** The burial ceremony can be initiated by an officer.
  - [ ] Non-officers are correctly denied access.
  - [ ] The flow correctly identifies the character to be buried.

### 4. Data Flow & Automation ✅

- [ ] **Sheet to Discord:** A new character entry in the Google Sheet (with `status=PENDING` and `confirmation=TRUE`) results in a new post in the `#recruitment` channel.
- [ ] **Officer Approval:** Reacting with ✅ to a recruitment post:
  - Creates a new thread in the `#character-sheet-vault`.
  - Updates the character's `status` to `REGISTERED` in the sheet.
- [ ] **Officer Rejection:** Reacting with ❌ to a recruitment post sends a DM to the user.
- [ ] **Burial Automation:** Setting a character's `status` to `DECEASED` in the sheet triggers the full burial ceremony.
  - [ ] A new thread is created in the `#cemetery`.
  - [ ] The original character thread in the vault is archived.
  - [ ] The character's owner receives a DM notification.

---

## Troubleshooting Quick-Reference

- **Bot Offline?**
  - `flyctl logs`
  - `flyctl status`
- **Webhooks Failing?**
  - Check Apps Script execution logs.
  - `curl` the webhook endpoint manually to test for errors.
- **Commands Missing?**
  - Wait 1-2 minutes for Discord cache to update.
  - Re-invite the bot with the correct scopes (`bot`, `applications.commands`).
