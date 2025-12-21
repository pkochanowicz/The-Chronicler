# DEPRECATED: This document is obsolete as the project is migrating away from Google Apps Script.
# Please refer to updated deployment and architectural documentation for the new FastAPI/Supabase stack.

# Google Apps Script Setup Guide

**Purpose:** Configure webhook triggers and automated backups for the Azeroth Bound Bot
**Version:** 2.0.0 (Schema Reformation)
**Required for:** Path B (Webhook-Driven Architecture)

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Script 1: Webhook Trigger (webhook.gs)](#script-1-webhook-trigger-webhookgs)
4. [Script 2: Daily Backup (backup.gs)](#script-2-daily-backup-backupgs)
5. [Setting Up Triggers](#setting-up-triggers)
6. [Testing Your Setup](#testing-your-setup)
7. [Troubleshooting](#troubleshooting)

---

## Overview

Google Apps Script powers the **webhook-driven architecture** (Path B) by:

1. **Monitoring Google Sheets** for changes (`onChange` trigger)
2. **Sending HTTP webhooks** to the Discord bot when specific conditions are met
3. **Automating daily backups** to Google Drive (7-day retention)

**Why use Apps Script?**
- ✅ Zero polling = Instant updates
- ✅ Free (no cost for triggers or API calls)
- ✅ Runs in Google's cloud (no server needed)
- ✅ Easy to modify trigger logic

---

## Prerequisites

Before setting up Apps Script:

- ✅ Google Sheets with `Character_Submissions` sheet (27 columns)
- ✅ Discord bot deployed with `/webhook` endpoint
- ✅ Webhook secret generated (32+ character random string)
- ✅ Google Drive folder for backups (optional but recommended)

---

## Script 1: Webhook Trigger (webhook.gs)

### Purpose

Monitors `Character_Submissions` sheet for changes and triggers webhooks when:

1. **Confirmation + Pending** - User completes registration → Post to #recruitment
2. **Status changes to DECEASED** - Officer uses `/bury` → Initiate burial ceremony

### Installation

1. Open your Google Sheet
2. **Extensions** → **Apps Script**
3. Delete default `Code.gs` content
4. Create new file: **webhook.gs**
5. Paste the following code:

```javascript
// ============================================
// WEBHOOK TRIGGER SCRIPT
// ============================================
// Monitors Character_Submissions sheet and sends webhooks
// to Discord bot when specific conditions are met.
//
// Version: 2.0.0 (Schema Reformation)
// Architecture: Path B (Webhook-Driven)
// ============================================

// ==================== CONFIGURATION ====================

// Your Discord bot's webhook endpoint
const WEBHOOK_URL = "https://azeroth-bound-bot.fly.dev/webhook";

// Shared secret (must match bot's WEBHOOK_SECRET env var)
const WEBHOOK_SECRET = "your_random_32_char_secret_here";

// Sheet name to monitor
const SHEET_NAME = "Character_Submissions";

// Column indices (zero-based)
const COL_STATUS = 15;           // Column 16 (status)
const COL_CONFIRMATION = 16;     // Column 17 (confirmation)
const COL_RECRUITMENT_MSG_ID = 18; // Column 19 (recruitment_msg_id)

// ==================== TRIGGER HANDLERS ====================

/**
 * onChange trigger - Fires when sheet is edited
 * Can also be called manually for testing (event parameter optional)
 */
function onSheetChange(e) {
  Logger.log("=== onSheetChange START ===");

  try {
    Logger.log("Sheet changed detected, analyzing...");
    Logger.log("Looking for sheet: '" + SHEET_NAME + "'");

    // Get the active spreadsheet and target sheet by name
    // This works both for real onChange events and manual testing
    var spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
    Logger.log("✅ Active spreadsheet retrieved: " + spreadsheet.getName());

    var sheet = spreadsheet.getSheetByName(SHEET_NAME);

    if (!sheet) {
      Logger.log("❌ ERROR: Sheet '" + SHEET_NAME + "' not found!");

      // List all available sheets for debugging
      var allSheets = spreadsheet.getSheets();
      Logger.log("Available sheets (" + allSheets.length + " total):");
      for (var i = 0; i < allSheets.length; i++) {
        Logger.log("  " + (i + 1) + ". \"" + allSheets[i].getName() + "\"");
      }

      Logger.log("=== onSheetChange END - SHEET NOT FOUND ===");
      return;
    }

    Logger.log("✅ Sheet found: '" + sheet.getName() + "'");

    var data = sheet.getDataRange().getValues();
    Logger.log("✅ Data retrieved: " + data.length + " rows (including header)");

    var headers = data[0];
    Logger.log("✅ Headers: " + headers.join(", "));

    // Process each row (skip header)
    var rowsProcessed = 0;
    for (var i = 1; i < data.length; i++) {
      var row = data[i];
      Logger.log("Processing row " + (i + 1) + "...");
      processRow(row, i + 1, headers);
      rowsProcessed++;
    }

    Logger.log("✅ Processed " + rowsProcessed + " data rows");
    Logger.log("=== onSheetChange END - SUCCESS ===");

  } catch (error) {
    Logger.log("❌ ERROR in onSheetChange: " + error.toString());
    Logger.log("❌ Error name: " + error.name);
    Logger.log("❌ Error message: " + error.message);
    if (error.stack) {
      Logger.log("❌ Stack trace: " + error.stack);
    }
    Logger.log("=== onSheetChange END - ERROR ===");
  }
}

/**
 * Process a single row and determine if webhook should fire
 */
function processRow(row, rowNumber, headers) {
  Logger.log("  → Analyzing row " + rowNumber);

  var status = row[COL_STATUS];
  var confirmation = row[COL_CONFIRMATION];
  var recruitmentMsgId = row[COL_RECRUITMENT_MSG_ID];

  Logger.log("    Status: " + status + ", Confirmation: " + confirmation + ", RecruitmentMsgId: " + (recruitmentMsgId || "(empty)"));

  // Trigger 1: User completed registration (confirmation=TRUE + status=PENDING + no recruitment post yet)
  if (confirmation === true && status === "PENDING" && !recruitmentMsgId) {
    Logger.log("  ✅ Trigger detected: POST_TO_RECRUITMENT (row " + rowNumber + ")");
    sendWebhook("POST_TO_RECRUITMENT", row, rowNumber, headers);
    return;
  }

  // Trigger 2: Officer set status to DECEASED → Initiate burial
  if (status === "DECEASED") {
    Logger.log("  ✅ Trigger detected: INITIATE_BURIAL (row " + rowNumber + ")");
    sendWebhook("INITIATE_BURIAL", row, rowNumber, headers);
    return;
  }

  Logger.log("  ⊝ No trigger conditions met for row " + rowNumber);
}

/**
 * Send webhook to Discord bot
 */
function sendWebhook(triggerType, row, rowNumber, headers) {
  try {
    // Build character object from row
    var character = {};
    for (var i = 0; i < headers.length; i++) {
      character[headers[i]] = row[i];
    }

    // Build webhook payload
    var payload = {
      "secret": WEBHOOK_SECRET,
      "trigger": triggerType,
      "row_number": rowNumber,
      "character": character,
      "timestamp": new Date().toISOString()
    };

    // Send HTTP POST
    var options = {
      "method": "post",
      "contentType": "application/json",
      "payload": JSON.stringify(payload),
      "muteHttpExceptions": true
    };

    var response = UrlFetchApp.fetch(WEBHOOK_URL, options);
    var responseCode = response.getResponseCode();

    if (responseCode === 200) {
      Logger.log("Webhook sent successfully: " + triggerType);
    } else {
      Logger.log("Webhook failed with code " + responseCode + ": " + response.getContentText());
    }

  } catch (error) {
    Logger.log("Error sending webhook: " + error.toString());
  }
}

// ==================== TESTING ====================

/**
 * Manual test function - Run this to test webhook connectivity
 */
function testWebhook() {
  Logger.log("Testing webhook connection...");

  var payload = {
    "secret": WEBHOOK_SECRET,
    "trigger": "TEST",
    "character": {},
    "timestamp": new Date().toISOString()
  };

  var options = {
    "method": "post",
    "contentType": "application/json",
    "payload": JSON.stringify(payload),
    "muteHttpExceptions": true
  };

  var response = UrlFetchApp.fetch(WEBHOOK_URL, options);

  Logger.log("Response code: " + response.getResponseCode());
  Logger.log("Response text: " + response.getContentText());

  if (response.getResponseCode() === 200) {
    Logger.log("✅ Webhook test PASSED");
  } else {
    Logger.log("❌ Webhook test FAILED");
  }
}

/**
 * Test the onChange trigger logic without requiring a real sheet change
 * This tests the trigger detection and webhook sending logic
 */
function testTriggerLogic() {
  Logger.log("=== Testing trigger logic ===");

  // Call onSheetChange without event object (now supported!)
  // This will process all rows in Character_Submissions sheet
  onSheetChange();

  Logger.log("=== Trigger logic test complete ===");
  Logger.log("Note: Check logs above for detailed execution trace");
  Logger.log("Note: Real webhooks are sent if trigger conditions are met!");
}

/**
 * Debugging helper - Lists all sheets in the spreadsheet
 * Run this if you're getting "Sheet not found" errors
 */
function listAllSheets() {
  Logger.log("=== Available Sheets in Spreadsheet ===");

  var spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  Logger.log("Spreadsheet: " + spreadsheet.getName());

  var sheets = spreadsheet.getSheets();
  Logger.log("Total sheets: " + sheets.length);
  Logger.log("");

  for (var i = 0; i < sheets.length; i++) {
    var sheet = sheets[i];
    Logger.log((i + 1) + ". \"" + sheet.getName() + "\"");
    Logger.log("   - Rows: " + sheet.getLastRow());
    Logger.log("   - Columns: " + sheet.getLastColumn());
    Logger.log("   - ID: " + sheet.getSheetId());
    Logger.log("");
  }

  Logger.log("=== End of sheet list ===");
  Logger.log("Looking for: \"" + SHEET_NAME + "\"");
  Logger.log("Make sure the name matches exactly (case-sensitive, space-sensitive)");
}
```

### Configuration

**Edit these constants at the top:**

```javascript
const WEBHOOK_URL = "https://your-bot.fly.dev/webhook";  // Your bot's URL
const WEBHOOK_SECRET = "your_random_32_char_secret";     // MUST match bot .env
```

**To generate a strong secret:**

```bash
openssl rand -hex 32
```

Copy the output and use it in BOTH:
- Google Apps Script `WEBHOOK_SECRET`
- Bot's `.env` file `WEBHOOK_SECRET`

### Configuring the Target Sheet

The webhook script must know which sheet to monitor. **Always use explicit sheet naming:**

```javascript
const SHEET_NAME = "Character_Submissions"; // Explicitly defined at top of script
var sheet = e.source.getSheetByName(SHEET_NAME); // Get sheet by name
```

**⚠️ CRITICAL WARNING:** Do NOT use `e.source.getActiveSheet().getName()`

**Why this fails:**
- The `onChange` trigger fires for **all sheet modifications**, including programmatic changes
- When Discord bot or Apps Script itself modifies the sheet, there is **no active user session**
- `getActiveSheet()` returns `null` or throws an error in these scenarios
- Your webhook will silently fail or crash

**Correct approach:**
1. Define `SHEET_NAME` constant at the top of the script
2. Use `e.source.getSheetByName(SHEET_NAME)` to explicitly fetch the sheet
3. Add null check: `if (!sheet) { return; }`

**Verification checklist:**
- ✅ Sheet tab name matches `SHEET_NAME` exactly (check for spaces, capitalization)
- ✅ Script uses `getSheetByName()` instead of `getActiveSheet()`
- ✅ Null check prevents crashes if sheet is renamed or deleted

**Optional advanced approach (Script Properties):**

For multi-environment setups, store configuration in Script Properties:

```javascript
function getSheetName() {
  var properties = PropertiesService.getScriptProperties();
  return properties.getProperty('TARGET_SHEET') || 'Character_Submissions';
}

// Then in onSheetChange:
var sheetName = getSheetName();
var sheet = e.source.getSheetByName(sheetName);
```

Set properties via: **Project Settings → Script Properties → Add property**

---

## Script 2: Daily Backup (backup.gs)

### Purpose

Automatically creates daily backups of `Character_Submissions` sheet to Google Drive with:
- 7-day retention (old backups auto-deleted)
- Timestamped backup files
- Runs at 2 AM daily (configurable)

### Installation

1. In same Apps Script project, create new file: **backup.gs**
2. Paste the following code:

```javascript
// ============================================
// DAILY BACKUP SCRIPT
// ============================================
// Creates daily backups of Character_Submissions
// to Google Drive with 7-day retention
//
// Version: 2.0.0
// ============================================

// ==================== CONFIGURATION ====================

// Google Drive folder ID for backups
// Get this by opening the folder in Drive and copying ID from URL
// URL format: https://drive.google.com/drive/folders/{FOLDER_ID}
const BACKUP_FOLDER_ID = "your_google_drive_folder_id_here";

// Sheet to backup
const BACKUP_SHEET_NAME = "Character_Submissions";

// Retention period (days)
const RETENTION_DAYS = 7;

// Backup file name prefix
const BACKUP_PREFIX = "AzerothBound_Backup_";

// ==================== BACKUP FUNCTION ====================

/**
 * Daily backup function - Set up time trigger for this
 */
function dailyBackup() {
  try {
    Logger.log("Starting daily backup...");

    // Get active spreadsheet
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName(BACKUP_SHEET_NAME);

    if (!sheet) {
      Logger.log("ERROR: Sheet '" + BACKUP_SHEET_NAME + "' not found!");
      return;
    }

    // Get backup folder
    var folder = DriveApp.getFolderById(BACKUP_FOLDER_ID);

    // Create backup filename with timestamp
    var timestamp = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "yyyy-MM-dd_HHmm");
    var backupName = BACKUP_PREFIX + timestamp;

    // Copy spreadsheet to backup folder
    var backup = ss.copy(backupName);
    var backupFile = DriveApp.getFileById(backup.getId());

    // Move to backup folder
    backupFile.moveTo(folder);

    Logger.log("✅ Backup created: " + backupName);

    // Clean up old backups
    deleteOldBackups(folder);

  } catch (error) {
    Logger.log("ERROR in dailyBackup: " + error.toString());
  }
}

/**
 * Delete backups older than RETENTION_DAYS
 */
function deleteOldBackups(folder) {
  try {
    var files = folder.getFilesByName();
    var cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - RETENTION_DAYS);

    var deletedCount = 0;

    while (files.hasNext()) {
      var file = files.next();
      var fileName = file.getName();

      // Only process backup files
      if (fileName.startsWith(BACKUP_PREFIX)) {
        var fileDate = file.getDateCreated();

        if (fileDate < cutoffDate) {
          Logger.log("Deleting old backup: " + fileName);
          file.setTrashed(true);
          deletedCount++;
        }
      }
    }

    Logger.log("Deleted " + deletedCount + " old backup(s)");

  } catch (error) {
    Logger.log("ERROR in deleteOldBackups: " + error.toString());
  }
}

// ==================== TESTING ====================

/**
 * Manual test - Run this to test backup functionality
 */
function testBackup() {
  Logger.log("Running backup test...");
  dailyBackup();
  Logger.log("Check your Google Drive backup folder!");
}
```

### Configuration

1. **Create Google Drive folder** for backups
2. **Copy folder ID** from URL: `https://drive.google.com/drive/folders/{THIS_IS_THE_ID}`
3. **Edit configuration** in script:

```javascript
const BACKUP_FOLDER_ID = "your_actual_folder_id_here";
```

---

## Setting Up Triggers

### Trigger 1: onChange (Webhook)

1. In Apps Script editor, click **clock icon** (Triggers)
2. Click **+ Add Trigger**
3. Configure:
   - **Function:** `onSheetChange`
   - **Deployment:** Head
   - **Event source:** From spreadsheet
   - **Event type:** On change
4. Click **Save**
5. **Authorize** (Google will ask for permissions)

**Expected behavior:**
- Trigger fires whenever sheet is edited
- Webhooks sent instantly when conditions met

---

### Trigger 2: Time-driven (Daily Backup)

1. Click **+ Add Trigger** again
2. Configure:
   - **Function:** `dailyBackup`
   - **Deployment:** Head
   - **Event source:** Time-driven
   - **Type:** Day timer
   - **Time of day:** 2am to 3am (or your preference)
3. Click **Save**

**Expected behavior:**
- Backup runs once per day at specified time
- Old backups deleted after 7 days

---

## Testing Your Setup

### Test 1: Webhook Connectivity

Tests basic webhook endpoint connectivity without processing sheet data.

1. In Apps Script editor, select **testWebhook** function
2. Click **Run** (play button)
3. Check **Execution log** (View → Logs)

**Expected output:**
```
Testing webhook connection...
Response code: 200
Response text: OK
✅ Webhook test PASSED
```

**If failed:**
- Check WEBHOOK_URL is correct
- Check WEBHOOK_SECRET matches bot's .env
- Check bot is running and accessible

---

### Test 2: Trigger Logic (NEW!)

Tests the onChange trigger logic without requiring manual sheet edits. This verifies that your trigger detection and webhook sending logic works correctly.

1. In Apps Script editor, select **testTriggerLogic** function
2. Click **Run** (play button)
3. Check **Execution log** (View → Logs)

**What this does:**
- Processes all rows in Character_Submissions sheet
- Checks each row for trigger conditions (PENDING + confirmation, DECEASED status, etc.)
- Sends real webhooks if conditions are met
- Works without needing a mock event object (thanks to refactored `onSheetChange()`)

**Expected output (with enhanced logging):**
```
=== Testing trigger logic ===
=== onSheetChange START ===
Sheet changed detected, analyzing...
Looking for sheet: 'Character_Submissions'
✅ Active spreadsheet retrieved: Your Spreadsheet Name
✅ Sheet found: 'Character_Submissions'
✅ Data retrieved: 3 rows (including header)
✅ Headers: timestamp, discord_id, char_name, ...
Processing row 2...
  → Analyzing row 2
    Status: PENDING, Confirmation: TRUE, RecruitmentMsgId: (empty)
  ✅ Trigger detected: POST_TO_RECRUITMENT (row 2)
✅ Processed 2 data rows
=== onSheetChange END - SUCCESS ===
=== Trigger logic test complete ===
```

**If logs stop mid-execution or you see "Sheet not found" error:**

1. **Run `listAllSheets()` first:**
   - Select **listAllSheets** function
   - Click **Run**
   - This shows exact names of all sheets in your spreadsheet

2. **Compare the output to `SHEET_NAME` constant:**
   - Sheet names are case-sensitive and space-sensitive
   - Update either the sheet name or the constant to match

3. **See [Troubleshooting: Silent failures](#silent-failures-or-incomplete-logs) for detailed guidance**

**⚠️ IMPORTANT:**
- This will send **real webhooks** if trigger conditions are met in your sheet
- Use on test data only, or ensure your bot is ready to handle the webhooks
- Having multiple sheet tabs (like Character_Registry alongside Character_Submissions) is perfectly fine—only Character_Submissions is processed

**Enhanced logging benefits:**
- See exactly where execution stops if there's an issue
- Detailed trace shows each row being analyzed
- Trigger conditions and their values are logged
- Full error details with stack traces if crashes occur
- Available sheet enumeration if target sheet not found

---

### Test 3: Backup Functionality

1. Select **testBackup** function
2. Click **Run**
3. Check **Google Drive** backup folder

**Expected:**
- New file: `AzerothBound_Backup_2025-12-16_1430`
- Contains copy of spreadsheet

---

### Test 4: End-to-End Webhook Flow

1. In Discord, use `/register_character`
2. Complete the flow and confirm
3. Check Google Sheets - row added with `status=PENDING`, `confirmation=TRUE`
4. **Within 1-2 seconds**, bot should post to #recruitment

**Expected:**
- Character posted to #recruitment channel
- ✅ and ❌ reactions added
- @Pathfinder @Trailwarden mentioned
- `recruitment_msg_id` updated in sheets

**If nothing happens:**
- Check **Apps Script Executions** (View → Executions)
- Look for errors in logs
- Verify onChange trigger is active

---

## Troubleshooting

### Silent failures or incomplete logs

**Symptoms:**
- `testTriggerLogic()` executes but logs stop mid-execution
- Only see "Sheet changed detected, analyzing..." but nothing after
- Function completes without error but missing expected logs

**Most common cause: Sheet name mismatch**

The script is looking for a sheet named `"Character_Submissions"` but your sheet has a different name.

**Diagnosis steps:**

1. **Run `listAllSheets()` function:**
   ```
   Apps Script editor → Select listAllSheets() → Click Run
   ```
   This will show you the exact names of all sheets in your spreadsheet.

2. **Compare sheet names exactly:**
   - Sheet names are **case-sensitive**: `"Character_Submissions"` ≠ `"character_submissions"`
   - Sheet names are **space-sensitive**: `"Character_Submissions"` ≠ `"Character Submissions"`
   - Watch for trailing spaces: `"Character_Submissions "` ≠ `"Character_Submissions"`

3. **Check the logs for detailed trace:**
   - With the enhanced logging, you'll see exactly where execution stops
   - Look for `❌ ERROR: Sheet not found` message
   - The log will list all available sheets for comparison

**Solution:**

Option A: **Rename your sheet to match the constant**
- In Google Sheets, double-click the sheet tab
- Rename it to exactly: `Character_Submissions`

Option B: **Update the constant to match your sheet**
- In Apps Script, change line 85:
  ```javascript
  const SHEET_NAME = "YourActualSheetName";  // Use exact name from listAllSheets()
  ```

**Verification:**
After fixing, run `testTriggerLogic()` again. You should now see:
```
=== onSheetChange START ===
Sheet changed detected, analyzing...
Looking for sheet: 'Character_Submissions'
✅ Active spreadsheet retrieved: [Your Spreadsheet Name]
✅ Sheet found: 'Character_Submissions'
✅ Data retrieved: X rows (including header)
```

**Note about multiple sheets:**
Having multiple sheet tabs (like `Character_Registry`, `Backups`, etc.) is perfectly fine. The script only processes the sheet specified in `SHEET_NAME`. Other sheets are ignored.

---

### Webhook not firing

**Check Apps Script Executions:**
1. Apps Script editor → View → Executions
2. Look for `onSheetChange` executions
3. Check if errors occurred

**Common issues:**

1. **Trigger not installed**
   - Go to Triggers (clock icon)
   - Verify "On change" trigger exists for `onSheetChange`

2. **Wrong sheet name**
   - Verify `SHEET_NAME = "Character_Submissions"` matches exactly
   - Sheet names are case-sensitive!

3. **Column indices wrong**
   - If you modified schema, update `COL_STATUS`, `COL_CONFIRMATION`, etc.
   - Indices are zero-based (Column A = 0, Column B = 1, etc.)

---

### Webhook returns 400 Bad Request

**Cause:** Secret mismatch

**Solution:**
- Verify `WEBHOOK_SECRET` in Apps Script matches `WEBHOOK_SECRET` in bot's .env exactly
- No extra spaces or quotes
- Case-sensitive!

---

### Backup not creating files

**Check:**

1. **Folder ID correct?**
   - Open Google Drive folder
   - Check URL contains the ID you used

2. **Permissions**
   - Apps Script must have Drive access
   - Re-authorize if needed

3. **Trigger installed?**
   - Check Triggers (clock icon)
   - Verify "Day timer" trigger exists for `dailyBackup`

---

### Backups not auto-deleting

**Check:**

1. **RETENTION_DAYS** set correctly (default: 7)
2. **File naming** - only files starting with `BACKUP_PREFIX` are deleted
3. **deleteOldBackups** function runs without errors (check logs)

---

## Advanced: Customizing Trigger Logic

### Example: Add trigger for officer approval

Want a webhook when officer approves a character?

**Add to `processRow()` function:**

```javascript
// Trigger 3: Officer approved character
if (status === "REGISTERED" && !character.forum_post_url) {
  Logger.log("Trigger detected: CREATE_FORUM_POST (row " + rowNumber + ")");
  sendWebhook("CREATE_FORUM_POST", row, rowNumber, headers);
  return;
}
```

**Then handle in bot's webhook_handler.py:**

```python
elif trigger_type == "CREATE_FORUM_POST":
    await handle_create_forum_post(character_data)
```

---

## Security Best Practices

1. **Never commit secrets to Git**
   - WEBHOOK_SECRET should only exist in:
     - Google Apps Script
     - Bot's .env file (on server)

2. **Rotate webhook secret quarterly**
   - Generate new secret
   - Update both Apps Script and bot
   - Test before removing old secret

3. **Limit sheet access**
   - Only officers should edit `Character_Submissions`
   - Use Google Sheets permissions

4. **Monitor execution logs**
   - Check Apps Script Executions weekly
   - Look for suspicious activity

---

## Support

**Issues with Apps Script?**

1. Check Execution logs (View → Executions)
2. Run test functions manually
3. Verify trigger configuration
4. Review bot logs for webhook errors
5. Ask in guild's tech support channel

---

**For Azeroth Bound! For Automation! For Zero Latency!** ⚡

*Last updated: December 16, 2025*
*Version: 2.0.0*
*Status: Production Ready*
