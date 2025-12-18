<div align="center">

<img src="https://drive.google.com/thumbnail?id=1iMOKN2XY6MgisjPVA0cY5H6ZisIYW6Tm&sz=w200" alt="Azeroth Bound Logo" width="200"/>

# The Chronicler
### *of Azeroth Bound*

<img src="https://drive.google.com/thumbnail?id=1RiYCBfOk8YED5chlcnPBX_Oo3NBVTgkh&sz=w1000" alt="Azeroth Bound Banner" width="100%"/>

[![Discord](https://img.shields.io/badge/Discord-Classic%2B-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/your-invite-link)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg?style=for-the-badge)](https://www.gnu.org/licenses/agpl-3.0)

</div>

---

## 📜 Introduction

**Greetings, traveler.**

You stand before **The Chronicler**—the arcane heart of the **Azeroth Bound** guild. This is not merely a bot; it is the keeper of our legends, the scribe of our deeds, and the guardian of our memories.

Forged in the fires of Python and tempered by the strict laws of World of Warcraft Classic+, The Chronicler bridges the gap between our adventures in Azeroth and our community in Discord. It transforms mundane tasks into immersive rituals, ensuring that every hero's story is told, remembered, and—when the time comes—honored.

---

## ✨ Features

### 🖋️ The Sacred Ritual of Registration
Forget boring forms. New members are greeted by *Chronicler Thaldrin* for a cinematic, 12-step interactive interview.
- **Immersive Dialogue:** Every step is narrated in-character.
- **Strict Validation:** Enforces lore-accurate Race/Class/Role combinations.
- **Rich Character Sheets:** Generates beautiful, standardized embeds for the Vault.

### ⚰️ The Rite of Remembrance
Death is part of the journey. When a hero falls, officers perform the **Burial Rite**.
- **Ceremonial Workflow:** A solemn interactive process to record the cause of death.
- **The Cemetery:** Automatically moves character records to the `#cemetery` channel.
- **Eulogies:** Allows officers to inscribe final words for the fallen.

### ⚡ The Arcane Link (Webhooks)
Built on the **Path B Architecture**:
- **Zero Polling:** Changes in our Master Google Sheet reflect instantly in Discord.
- **Single Source of Truth:** Your spreadsheet is the database. The bot is the interface.
- **Reliable Automation:** Powered by Google Apps Script triggers.

---

## 🛠️ For The Engineers

The Chronicler is built with modern, production-grade standards.

- **Stack:** Python 3.11, `discord.py`, `aiohttp`
- **Dependency Management:** `poetry` (primary), `uv` (fast), or `pip`.
- **Infrastructure:** Docker multi-stage builds, `docker-compose` for dev.
- **Quality:** 100% Test Coverage (Unit & Integration), Type-hinted, Linted.

### Quick Start

1.  **Clone the Chronicle:**
    ```bash
    git clone https://github.com/pkochanowicz/the_chronicler.git
    cd the_chronicler
    ```

2.  **Summon the Dependencies:**
    ```bash
    poetry install
    # OR
    uv pip install -r pyproject.toml
    ```

3.  **Awaken the Spirit:**
    ```bash
    # Ensure .env is populated (see .env.example)
    poetry run python main.py
    ```

[**📚 Read the Full DevOps Guide**](./docs/DEVOPS_GUIDE.md)

---

## 📖 The Archives (Documentation)

- [**User Guide**](./docs/USER_GUIDE.md) - *For the heroes of the guild.*
- [**Technical Manual**](./docs/TECHNICAL.md) - *For the goblins and gnomes engineering the backend.*
- [**Deployment Guide**](./docs/DEPLOYMENT_GUIDE.md) - *Instructions for hosting on Fly.io.*

---

<div align="center">

*“What we do in life, echoes in the server.”*

**For Azeroth Bound!** ⚔️

</div>