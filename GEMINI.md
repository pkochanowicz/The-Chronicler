# 🛡️ AZEROTH BOUND - ARCHITECTURAL CONTEXT

## 🎯 Project Mission
We are building a scalable **Discord Bot** integrated with **Google Sheets** as a lightweight database.
**Focus:** robust architecture, type safety, clean code, and zero technical debt.

## 🛠️ Tech Stack & Standards
- **Language:** Python 3.10+ (Type Hints REQUIRED)
- **Framework:** `discord.py` (latest)
- **Database:** Google Sheets via `gspread` (Service Account Auth)
- **Async:** STRICT adherence to `async/await` patterns. No blocking calls.
- **Docs:** Google-style docstrings for all functions.

## ⚡ Architectural Rules (The "Iron Laws")
1.  **Service Layer Pattern:** The Bot logic (`cogs`) must NEVER talk to the API directly.
    * ✅ `Bot Command` -> `SheetService` -> `Google API`
    * ❌ `Bot Command` -> `Google API`
2.  **Error Handling:** All external calls (Discord/Google) must be wrapped in `try/except` with specific error logging.
3.  **Config:** No hardcoded IDs. Use `os.getenv` for everything.
4.  **Webhooks:** Use webhooks for low-latency updates from Sheets -> Discord.

## 📝 Documentation Style
- When generating code, always include a brief "Why" explaining the architectural decision.
- Update `CHANGELOG.md` automatically if the user asks for a feature completion.

## ⚠️ Known Hazards
- Google API Rate Limits: Always implement exponential backoff.
- Discord Interaction Timeouts: All commands > 3s must use `defer()`.
