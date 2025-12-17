# Azeroth Bound Bot - Changelog

All notable changes to the **Azeroth Bound** project (also known as *The Chronicle*) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2025-12-17

### 🚀 Initial Release: The Chronicle Begins

The first major release of the Azeroth Bound Discord Bot, establishing the foundation for the guild's character management and roleplay immersion.

#### ✨ Key Features
- **Interactive Registration Flow:** A cinematic, 12-step character creation process led by *Chronicler Thaldrin*, featuring in-character dialogue, validation, and rich embeds.
- **The Rite of Remembrance:** A solemn, officer-led `/bury` ceremony to honor fallen heroes, moving their records to the Cemetery.
- **Google Sheets Integration:** A robust 27-column schema serving as the single source of truth for all character data.
- **Webhook Automation (Path B):** Instant, event-driven architecture. Updates in Sheets trigger immediate Discord actions without polling.
- **Portrait Management:** Support for custom image URLs, default class placeholders, and future AI generation hooks.
- **Role & Class Validation:** Strict enforcement of WoW Classic+ races, classes, and role combinations.

#### 🛡️ Infrastructure & DevOps
- **Multi-Tool Support:** Fully compatible with **Poetry**, **uv**, and standard **pip**.
- **Docker Ready:** Production-optimized Dockerfiles and local `docker-compose` setup.
- **Security Hardened:** Strict file permissions and environment variable management for secrets.
- **Testing Suite:** Comprehensive unit and integration tests covering the entire lifecycle state machine.

#### 📚 Documentation
- **The Archives:** Complete documentation suite including:
  - `USER_GUIDE.md`: Immersive guide for guild members.
  - `TECHNICAL.md`: Deep dive into the architecture and schema.
  - `DEVOPS_GUIDE.md`: Infrastructure and deployment manual.
  - `DEPLOYMENT_GUIDE.md`: Hosting setup for Fly.io/Render.

---

*“History is not written by the victors, but by those who take the time to hold the quill.”*
— Chronicler Thaldrin