# The Chronicler
### *of Azeroth Bound*

[![Discord](https://img.shields.io/badge/Discord-Classic%2B-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/fJDzq5rfAK)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Version](https://img.shields.io/badge/Version-1.2.6-blue?style=for-the-badge)](./docs/CHANGELOG.md)

**Greetings, traveler.**

You stand before **The Chronicler**—the arcane heart of the **Azeroth Bound** guild. This is not merely a bot; it is the keeper of our legends, the scribe of our deeds, and the guardian of our memories.

Forged in the fires of Python and tempered by the strict laws of World of Warcraft Classic+, The Chronicler bridges the gap between our adventures in Azeroth and our community in Discord.

---

## ✨ Features (v1.2.6 "The Singing Steel")

### 🖋️ The Sacred Ritual of Registration
Forget boring forms. New members are greeted by *Chronicler Thaldrin* for a cinematic, 12-step interactive interview.
- **Immersive Dialogue:** Every step is narrated in-character.
- **Direct Image Uploads:** Upload your portrait directly; stored securely on Cloudflare R2.
- **Strict Validation:** Enforces lore-accurate Race/Class/Role combinations.

### 🏦 The Guild Bank
A robust banking system tracking every copper and linen cloth.
- **Deposit & Withdraw:** Track items with `/bank deposit` and `/bank withdraw`.
- **Transparency:** See exactly who deposited what.
- **My Deposits:** Check your own contributions with `/bank mydeposits`.

### ⚔️ Talent System & Validation
Ensure your build is battle-ready and legal.
- **Talent Audit:** Validate your build code against Classic+ rules with `/talent audit`.
- **Dynamic Library:** Talents are loaded dynamically for easy updates.

### ⚰️ The Rite of Remembrance
Death is part of the journey. When a hero falls, officers perform the **Burial Rite**.
- **Ceremonial Workflow:** A solemn interactive process to record the cause of death.
- **The Cemetery:** Automatically moves character records to the `#cemetery` channel.

### ⚡ The Arcane Link (PostgreSQL + MCP)

Built on a robust, event-driven hybrid architecture:

- **PostgreSQL Database:** Primary source of truth for characters, guild bank, and talents.
- **Zero Polling:** Changes in our database reflect instantly in Discord via webhooks.
- **MCP Integration:** External server enables AI-powered workflows via LLM agents.
- **Reliable Automation:** Powered by FastAPI webhooks for seamless, real-time integration.

---

## 🛠️ For The Engineers

The Chronicler is built with modern, production-grade standards.

- **Stack:** Python 3.11, `discord.py`, `aiohttp`, `FastAPI`
- **Database:** PostgreSQL (Supabase)
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
- [**Deployment Guide**](./docs/DEPLOYMENT_GUIDE.md) - *Instructions for hosting on Fly.io.*
- [**R2 Setup Guide**](./docs/R2_SETUP.md) - *Simple setup for Cloudflare R2 image storage.*
- [**Test Suite**](./docs/TEST_SUITE.md) - *Protocols for quality assurance.*

---

<div align="center">
<i>“What we do in life, echoes in the server.”</i><br>
<b>For Azeroth Bound! ⚔️</b>
</div>
