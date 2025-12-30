# Multi-Agent Workflows for The Chronicler

**Date:** 2025-12-30
**Purpose:** Define patterns for coordinating Claude Code + Gemini CLI + MCP Server
**Status:** Implementation Guide

---

## Overview

The Chronicler development uses a **multi-agent architecture** where different AI agents collaborate on complex tasks:

- **Claude Code:** Primary development agent (implementation, testing, architecture)
- **Gemini CLI:** Research agent (parallel investigation, documentation, reviews)
- **MCP Server (discord-guildmaster-mcp):** Production agent (executes Discord workflows from LLM tools)

---

## Agent Roles & Capabilities

### Claude Code (Primary Development Agent)

**Strengths:**
- ✅ Deep codebase understanding
- ✅ Complex refactoring and architecture
- ✅ Test-driven development
- ✅ Database migrations
- ✅ Async Python expertise

**Best Used For:**
- Writing production code
- Database schema changes
- Bug fixing and debugging
- API integration implementation
- Test suite creation

**Tools Available:**
- Read, Write, Edit files
- Bash command execution
- Git operations
- Task management
- Web search/fetch

**Example Workflows:**
```bash
# Claude Code implements image storage service
Claude> Implementing services/image_storage.py with R2 backend...
Claude> Creating unit tests in tests/unit/test_image_storage.py...
Claude> Updating config/settings.py with R2 credentials...
```

---

### Gemini CLI (Research & Review Agent)

**Strengths:**
- ✅ Parallel research tasks
- ✅ Alternative perspectives
- ✅ Documentation generation
- ✅ Code review
- ✅ Data analysis

**Best Used For:**
- Researching external APIs/libraries
- Analyzing large Lua/JSON data structures
- Writing user-facing documentation
- Reviewing Claude's architectural decisions
- Investigating Turtle WoW game data sources

**Available via Command:**
```bash
gemini "Your research question or task here"
```

**Example Workflows:**
```bash
# Parallel research while Claude implements
$ gemini "Research Turtle WoW database availability. Check turtle-wow.org, \
GitHub repos, and Discord for official API or data dumps. Summarize findings."

# Code review
$ gemini "Review this proposed Cloudflare R2 integration for edge cases. \
File: services/image_storage.py"

# Documentation from different angle
$ gemini "Write beginner-friendly guide for setting up R2 bucket based on \
docs/IMAGE_STORAGE.md. Focus on screenshots and step-by-step."
```

---

### MCP Server (Production Workflow Agent)

**Strengths:**
- ✅ Direct Discord API access (local MCP tools)
- ✅ LLM-powered workflows (via Claude Desktop or API)
- ✅ Channel management
- ✅ Message posting
- ✅ Role assignment

**Best Used For:**
- AI-powered character welcomes
- ComfyUI image generation workflows
- Channel activity summaries
- Automated announcements
- Complex multi-step Discord operations

**Integration Pattern:**
```python
# The Chronicler triggers workflow
await mcp_client.trigger_character_welcome(
    member_id=new_member.id,
    character_name=character.name
)

# MCP Server executes (via local tools)
# 1. Generate welcome message with AI
# 2. Create character portrait with ComfyUI
# 3. Post to #recruitment channel
# 4. Assign Seeker role
```

---

## Multi-Agent Workflow Patterns

### Pattern 1: Parallel Research + Implementation

**Use Case:** Need to research pfUI data while implementing image storage

**Workflow:**
```bash
# Terminal 1: Claude Code (Implementation)
Claude> Starting implementation of services/image_storage.py...
Claude> Adding R2 configuration to config/settings.py...

# Terminal 2: Gemini CLI (Research)
$ gemini "Analyze pfUI-turtle repository structure. Find all Lua data files \
containing item, NPC, or quest databases. Export findings as JSON summary."

# Result: Both agents work in parallel
# Claude delivers code, Gemini delivers research
# Combine findings in next iteration
```

**Benefits:**
- ⚡ 2x faster than sequential work
- 🧠 Multiple perspectives on problem
- 📊 Research informs implementation

---

### Pattern 2: Code → Review → Iterate

**Use Case:** Claude implements feature, Gemini reviews for issues

**Workflow:**
```bash
# Step 1: Claude implements
Claude> Implemented chronicler/integrations/mcp_client.py
Claude> Created trigger methods for character welcome, event announcement

# Step 2: Gemini reviews
$ gemini "Review chronicler/integrations/mcp_client.py for:\
1. Error handling edge cases\
2. Rate limiting considerations\
3. Async/await best practices\
4. Missing type hints\
Provide specific line-by-line feedback."

# Step 3: Claude iterates
Claude> Addressing Gemini's feedback:
Claude> - Added exponential backoff for rate limits (line 45)
Claude> - Improved error handling with custom exceptions (line 78)
Claude> - Added missing type hints for return values
```

**Benefits:**
- 🔍 Catches bugs before testing
- 📚 Knowledge transfer between agents
- ✨ Higher code quality

---

### Pattern 3: Architecture Decision with Multiple Agents

**Use Case:** Deciding on database scope for game data

**Workflow:**
```bash
# Step 1: Claude analyzes current state
Claude> Analyzing schemas/db_schemas.py...
Claude> Found 6 game data tables (items, npcs, quests, spells, factions)
Claude> Database bloat risk: ~145MB if fully populated

# Step 2: Gemini researches alternatives
$ gemini "Research Turtle WoW database APIs. Check:\
- database.turtle-wow.org\
- turtle-wow.org API documentation\
- Community GitHub repos with data dumps\
- Discord channels mentioning API access\
Summarize availability, rate limits, and data freshness."

# Step 3: Claude documents decision
Claude> Creating docs/DATA_ARCHITECTURE_DECISION.md...
Claude> Recommendation: External API + caching (based on Gemini's findings)
```

**Benefits:**
- 🎯 Data-driven decisions
- 🌐 Comprehensive research
- 📝 Well-documented rationale

---

### Pattern 4: Chronicler → MCP Server Workflow

**Use Case:** New character registration triggers AI-powered welcome

**Sequence Diagram:**
```
User                The Chronicler       MCP Client          MCP Server       Discord
 |                         |                 |                   |              |
 |---/register_character-->|                 |                   |              |
 |                         |                 |                   |              |
 |                         |--Store to DB--->|                   |              |
 |                         |                 |                   |              |
 |                         |--trigger_welcome-->|                |              |
 |                         |                 |                   |              |
 |                         |                 |--POST /webhooks/-->              |
 |                         |                 |   character-welcome|              |
 |                         |                 |                   |              |
 |                         |                 |                   |--AI generate |
 |                         |                 |                   |  welcome msg |
 |                         |                 |                   |              |
 |                         |                 |                   |--Post msg--->|
 |                         |                 |                   |              |
 |<----------------------Welcome message posted in #recruitment---------------|
```

**Implementation:**
```python
# The Chronicler (hosted bot)
from chronicler.integrations.mcp_client import MCPWorkflowTrigger

async def on_character_registered(character: Character):
    """Triggered after character passes approval."""
    mcp = MCPWorkflowTrigger()

    await mcp.trigger_character_welcome(
        member_id=character.discord_user_id,
        guild_id=settings.GUILD_ID,
        character_data={
            "name": character.name,
            "race": character.race,
            "class": character.char_class,
            "backstory": character.backstory
        }
    )

# MCP Server (local tools)
# Receives webhook, executes workflow via Claude Desktop or API:
# 1. Generate personalized welcome using character backstory
# 2. (Optional) Generate portrait with ComfyUI
# 3. Post to #recruitment channel
# 4. Assign Seeker role to member
```

**Benefits:**
- 🤖 AI-powered personalization
- 🎨 Automated asset generation
- ⚡ No blocking operations in main bot
- 🔄 Workflow orchestration via MCP tools

---

## Handoff Patterns Between Agents

### Pattern A: Sequential Handoff

```bash
# Claude does heavy lifting
Claude> Implemented feature X in 3 files
Claude> Ready for review

# Handoff to Gemini
$ gemini "Review feature X implementation in files A, B, C. \
Check for edge cases and security issues."

# Gemini returns findings
Gemini> Found 3 issues:
1. Missing null check on line 42
2. SQL injection risk on line 108
3. Race condition in async operation

# Claude fixes
Claude> Addressing all 3 issues...
```

### Pattern B: Parallel Collaboration

```bash
# Launch both agents simultaneously
Claude> Implementing database migration for R2 integration...

$ gemini "Write user guide for configuring Cloudflare R2 bucket \
with step-by-step screenshots placeholders"

# Both complete in parallel
# Merge deliverables in single PR
```

### Pattern C: Iterative Refinement

```bash
# Round 1: Claude draft
Claude> Created initial docs/IMAGE_STORAGE.md

# Round 2: Gemini improves
$ gemini "Enhance docs/IMAGE_STORAGE.md with:\
- Troubleshooting section\
- Cost calculator\
- Common mistakes section"

# Round 3: Claude integrates
Claude> Merged Gemini's enhancements into IMAGE_STORAGE.md
```

---

## Context Sharing Strategies

### Strategy 1: File-Based Context

**When:** Agents need to share large documents or code

**Method:**
```bash
# Claude writes file
Claude> Created docs/ARCHITECTURE_DECISION.md

# Gemini reads same file
$ gemini "Read docs/ARCHITECTURE_DECISION.md and create a \
5-slide presentation summary for non-technical stakeholders"
```

### Strategy 2: Command Output Piping

**When:** Gemini needs to analyze Claude's findings

**Method:**
```bash
# Claude generates report
Claude> Analysis complete. Summary in /tmp/db_analysis.txt

# Pipe to Gemini
$ gemini "$(cat /tmp/db_analysis.txt) \
Based on this analysis, recommend 3 optimization strategies"
```

### Strategy 3: Shared Documentation

**When:** Building knowledge base collaboratively

**Method:**
```bash
# Claude documents technical details
Claude> Added implementation notes to docs/TECHNICAL.md

# Gemini adds user perspective
$ gemini "Read docs/TECHNICAL.md and add a 'Common Questions' \
section answering the top 5 questions users might ask"
```

---

## Example Workflows for Common Tasks

### Workflow 1: Add New Slash Command

**Agent Responsibilities:**
| Task | Agent | Rationale |
|------|-------|-----------|
| Research Discord.py best practices | Gemini | Parallel research |
| Implement command handler | Claude | Code implementation |
| Write unit tests | Claude | TDD expertise |
| Create user documentation | Gemini | User-facing writing |
| Review for edge cases | Gemini | Fresh perspective |

**Execution:**
```bash
# Step 1: Research (Gemini)
$ gemini "Research Discord.py app_commands best practices for \
slash commands with complex interactions. Focus on error handling, \
deferred responses, and ephemeral messages."

# Step 2: Implement (Claude)
Claude> Creating commands/new_feature_commands.py...
Claude> Adding tests in tests/unit/test_new_feature_commands.py...

# Step 3: Document (Gemini)
$ gemini "Write user guide for new /command based on \
implementation in commands/new_feature_commands.py"

# Step 4: Review (Gemini)
$ gemini "Review commands/new_feature_commands.py for:\
- Permission edge cases\
- Timeout handling\
- User error messages clarity"

# Step 5: Refine (Claude)
Claude> Implementing Gemini's suggestions...
```

---

### Workflow 2: Database Migration

**Agent Responsibilities:**
| Task | Agent | Rationale |
|------|-------|-----------|
| Analyze current schema | Claude | Deep codebase knowledge |
| Research external data sources | Gemini | API/data research |
| Create Alembic migration | Claude | Database expertise |
| Document migration plan | Claude | Technical writing |
| Write rollback procedure | Gemini | Different perspective |

**Execution:**
```bash
# Parallel work
Claude> Analyzing current database schema...
$ gemini "Research Turtle WoW API availability and data freshness"

# Claude synthesizes
Claude> Creating migration based on findings...
Claude> Writing docs/MIGRATION_GUIDE.md...

# Gemini adds safety
$ gemini "Review migration plan and add rollback procedures \
for each step. Include SQL commands for manual rollback."
```

---

### Workflow 3: MCP Integration Feature

**Agent Responsibilities:**
| Task | Agent | Rationale |
|------|-------|-----------|
| Design MCP API contract | Claude | Architecture design |
| Implement Chronicler client | Claude | Async Python |
| Document MCP server setup | Gemini | User-facing docs |
| Test end-to-end workflow | Claude | Integration testing |
| Create troubleshooting guide | Gemini | Support documentation |

**Execution:**
```bash
# Claude designs & implements
Claude> Creating chronicler/integrations/mcp_client.py...
Claude> Defining workflow trigger interface...
Claude> Writing integration tests...

# Gemini documents user journey
$ gemini "Write step-by-step guide for setting up MCP server \
to work with The Chronicler. Include:\
- Prerequisites\
- Installation steps\
- Configuration\
- Testing the connection\
- Troubleshooting common issues"
```

---

## Communication Protocols

### Protocol 1: Issue Discovery

```bash
# If Gemini finds issues during review
$ gemini "ISSUE FOUND in services/image_storage.py line 45:\
Missing error handling for R2 bucket not found. \
Recommend adding BucketNotFoundError exception."

# Claude addresses
Claude> Acknowledged. Adding BucketNotFoundError handling...
```

### Protocol 2: Research Findings

```bash
# Gemini completes research
$ gemini "RESEARCH COMPLETE: Turtle WoW has official database at \
database.turtle-wow.org with REST API. Rate limit: 100 req/min. \
Documentation: [URL]. Recommend implementing caching layer."

# Claude incorporates
Claude> Implementing TurtleWoWDataLookup service based on findings...
```

### Protocol 3: Blocker Escalation

```bash
# If either agent is blocked
Claude> BLOCKED: Need Turtle WoW API authentication method. \
Gemini, can you research auth requirements?

$ gemini "Researching Turtle WoW API authentication..."
```

---

## Best Practices

### DO:
✅ Use Claude for implementation, Gemini for research
✅ Run agents in parallel when tasks are independent
✅ Have Gemini review Claude's architectural decisions
✅ Use file-based context sharing for large documents
✅ Document all inter-agent workflows for future reference

### DON'T:
❌ Have both agents edit the same file simultaneously (conflicts!)
❌ Use Gemini for complex code implementation (Claude is better)
❌ Use Claude for pure research tasks (Gemini is faster)
❌ Forget to commit agent-generated documentation
❌ Skip code review step (Gemini catches what Claude misses)

---

## Tool Access Matrix

| Tool | Claude Code | Gemini CLI | MCP Server |
|------|-------------|------------|------------|
| **Read files** | ✅ | ✅ | ❌ |
| **Write files** | ✅ | ✅ | ❌ |
| **Execute bash** | ✅ | ✅ | ❌ |
| **Git operations** | ✅ | ✅ | ❌ |
| **Web search** | ✅ | ✅ | ❌ |
| **Discord API (direct)** | ❌ | ❌ | ✅ (via MCP tools) |
| **LLM generation** | ✅ (Sonnet 4.5) | ✅ (Gemini) | ✅ (via Claude API) |
| **Image generation** | ❌ | ❌ | ✅ (via ComfyUI tools) |
| **Database access** | ✅ (via code) | ❌ | ❌ |

---

## Success Metrics

**Measure multi-agent effectiveness:**
- ⏱️ Time to complete complex features (expect 30-50% reduction)
- 🐛 Bug detection rate (Gemini review catches +15% more issues)
- 📚 Documentation quality (user satisfaction scores)
- 🔄 Iteration cycles needed (fewer with parallel work)
- 💡 Alternative solutions considered (Gemini provides options)

---

## Future Enhancements

### Planned Agent Additions:
1. **Test Agent:** Specialized in test generation and quality assurance
2. **Security Agent:** Focused on vulnerability scanning and secure coding
3. **Performance Agent:** Profile code and suggest optimizations

### Advanced Patterns:
- **Agent Swarm:** Multiple Gemini instances researching different aspects
- **Consensus Building:** 3+ agents vote on architectural decisions
- **Continuous Review:** Gemini monitors commits and flags potential issues

---

*Multi-Agent Workflow Guide — Orchestrating Claude Code + Gemini CLI + MCP Server*
*Created 2025-12-30*
