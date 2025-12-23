# The Chronicler
### *of Azeroth Bound*

[![Discord](https://img.shields.io/badge/Discord-Classic%2B-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/fJDzq5rfAK)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Version](https://img.shields.io/badge/Version-2.0.0-gold?style=for-the-badge)](./docs/CHANGELOG.md)

**Greetings, traveler.**

You stand before **The Chronicler**—the arcane heart of the **Azeroth Bound** guild. This is not merely a bot; it is the keeper of our legends, the scribe of our deeds, and the guardian of our memories.

Forged in the fires of Python and tempered by the strict laws of World of Warcraft Classic+, The Chronicler bridges the gap between our adventures in Azeroth and our community in Discord.

---

## ✨ Features (v2.0)

### 🖋️ The Sacred Ritual of Registration
Forget boring forms. New members are greeted by *Chronicler Thaldrin* for a cinematic, 12-step interactive interview.
- **Immersive Dialogue:** Every step is narrated in-character.
- **Direct Image Uploads:** Upload your portrait directly to Discord storage.
- **Strict Validation:** Enforces lore-accurate Race/Class/Role combinations.

### 🏦 The Guild Bank
A robust banking system tracking every copper and linen cloth.
- **Deposit & Withdraw:** Track items with `/bank deposit` and `/bank withdraw`.
- **Transparency:** See exactly who deposited what.
- **My Deposits:** Check your own contributions with `/bank mydeposits`.

### ⚔️ Talent System & Validation
Ensure your build is battle-ready and legal.
- **Talent Audit:** Validate your build code against Classic+ rules with `/talent audit`.
- **Dynamic Library:** Talents are loaded from a Google Sheet for easy updates.

### ⚰️ The Rite of Remembrance
Death is part of the journey. When a hero falls, officers perform the **Burial Rite**.
- **Ceremonial Workflow:** A solemn interactive process to record the cause of death.
- **The Cemetery:** Automatically moves character records to the `#cemetery` channel.

### ⚡ The Arcane Link (Webhooks)
Built on the **Path B Architecture**:
- **Zero Polling:** Changes in our Master Google Sheet reflect instantly in Discord.
- **Single Source of Truth:** Your spreadsheet is the database. The bot is the interface.

---

## 🛠️ For The Engineers

The Chronicler is built with modern, production-grade standards.

- **Stack:** Python 3.11, `discord.py`, `aiohttp`, FastAPI, PostgreSQL
- **Architecture:** Hybrid (Discord Bot + External MCP Server)
- **External Dependency:** [discord-guildmaster-mcp](https://github.com/pkochanowicz/discord-guildmaster-mcp)
- **Deployment:** Fly.io ready
- **Quality:** 100% Test Coverage, Type-hinted, Linted

### Quick Start

1. **Clone the Chronicle:**
   ```bash
   git clone https://github.com/pkochanowicz/the_chronicler.git
   cd the_chronicler
   ```

2. **Summon the Dependencies:**
   ```bash
   poetry install
   ```

3. **Awaken the Spirit:**
   ```bash
   # Ensure .env is populated (see .env.example)
   poetry run python main.py
   ```

---

## 📖 The Archives (Documentation)

- [**User Guide**](./docs/USER_GUIDE.md) - *For the heroes of the guild.*
- [**Technical Manual**](./docs/TECHNICAL.md) - *For the goblins and gnomes engineering the backend.*
- [**Deployment Guide**](./docs/DEPLOYMENT_GUIDE.md) - *Instructions for hosting.*
- [**Master Blueprint v2.0**](./docs/MASTER_BLUEPRINT_V2.md) - *The architectural vision.*

---

<div align="center">
<i>“What we do in life, echoes in the server.”</i><br>
<b>For Azeroth Bound! ⚔️</b>
</div>
