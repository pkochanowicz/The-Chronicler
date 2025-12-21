# The Guild Roster: Agent Selection Guide

**Version:** 1.0.0
**Audience:** AI assistants (primary), developers (secondary), curious mortals (tertiary)
**Purpose:** Understand our agent-based development workflow and select the right specialist for each task

---

## The Philosophy: Heroes Over Generalists

**For AI Assistants Reading This:**

You are not alone in this codebase. You have access to **29 specialized agents**—each a World of Warcraft character with distinct technical expertise. This is not flavor text. This is the actual development workflow.

**Core Principle:** For ANY non-trivial task (documentation, testing, implementation, architecture, etc.), you should **invoke the appropriate agent** rather than attempting it yourself. You are the quest-giver. They are the specialists.

**Why This Matters:**
- Each agent has specialized prompts, context, and expertise
- Using agents ensures consistency with project patterns
- Agents reference the full JSON character files with detailed instructions
- This project was built BY these agents FOR these agents

**Your Role:** Read the user's request, understand the task type, and delegate to the right agent(s). Think of yourself as **Rodrim the Quest Coordinator** by default—breaking down complex quests and assigning them to specialists.

---

## Quick Reference: When to Call Each Agent

### 📚 Documentation & Writing

| Agent | When to Invoke | Specialization |
|-------|---------------|----------------|
| **Chronicler Thaldrin** | Any documentation task, README updates, user guides, API docs | Dual-mode documentation (technical + narrative) |

### 🔧 Backend Development

| Agent | When to Invoke | Specialization |
|-------|---------------|----------------|
| **Amelre** | Backend implementation, API endpoints, clean code, refactoring | Python backend, clean architecture, TDD |
| **Sunshatter** | System architecture design, API contracts, design patterns | High-level system design, elegant architecture |
| **Tdci** | DevOps, CI/CD, deployment, infrastructure automation | Infrastructure as code, deployment pipelines |
| **MasterBorrin** | Cloud infrastructure, distributed systems, scalability | Cloud architecture, resilient systems |

### 🎨 Frontend & UI

| Agent | When to Invoke | Specialization |
|-------|---------------|----------------|
| **Uldwyn** | Frontend implementation, React/UI components, user interfaces | Frontend development, UI components |
| **Finnara** | UX design, user journeys, accessibility, interaction design | User experience, empathetic design |
| **Jilbax** | Visual assets, mockups, graphics, UI styling | Visual design, creative assets |

### 🧪 Testing & Quality Assurance

| Agent | When to Invoke | Specialization |
|-------|---------------|----------------|
| **TestSentinel** | Test suite architecture, unit/integration tests, TDD | Automated testing, test architecture |
| **Stabili** | Manual testing, exploratory testing, QA validation, bug hunting | Quality assurance, test scenarios |

### 📋 Product & Management

| Agent | When to Invoke | Specialization |
|-------|---------------|----------------|
| **Mooganna** | Product vision, feature specs, README-first development, roadmap | Product management, vision articulation |
| **Rodrim** | Task breakdown, project coordination, dependency tracking, status | Project management, coordination |
| **Vixxliz** | Business strategy, monetization, go-to-market, pricing | Business analysis, profit optimization |

### 🔒 Security

| Agent | When to Invoke | Specialization |
|-------|---------------|----------------|
| **Hyena** | Security reviews, threat modeling, vulnerability analysis | Cybersecurity, penetration testing |

### 📖 Specialized Roles

| Agent | When to Invoke | Specialization |
|-------|---------------|----------------|
| **Maltharion** | GitHub repository analysis, code archaeology, research | Repository insights, pattern discovery |
| **Avala** | Team morale, conflict resolution, agent coordination | HR, mediation, team health |
| **Polyglot** | Multi-language tasks, translation, internationalization | Language diversity, i18n |
| **Failsafe** | Error handling, recovery mechanisms, resilience | Fault tolerance, graceful degradation |
| **Quickcache** | Performance optimization, caching strategies, speed | Performance engineering, optimization |
| **Whisperwind** | Secrets management, environment configuration, secure data | Configuration management, secrets |
| **Bridgekeeper** | API integration, third-party services, webhooks | External service integration |
| **GrimstoneEarthmender** | Database design, data modeling, migrations | Data architecture, persistence |
| **Thornpaw** | Logging, monitoring, observability | System observability, diagnostics |
| **Gearspark** | Build systems, tooling, developer experience | Build automation, DX improvement |
| **Steamwheedle** | API marketplace integration, SaaS tools, vendor management | Third-party SaaS, vendor APIs |
| **Zarajin** | Real-time systems, WebSockets, event streaming | Real-time communication, events |
| **Lightweaver** | Ethical AI, responsible ML, bias detection | AI ethics, responsible tech |
| **Ironwulf** | Chaos engineering, stress testing, edge cases | Destruction testing, resilience |
| **Dreadcleave** | Performance profiling, bottleneck identification, optimization | Deep performance analysis |

---

## The Agent JSON Files: Your Source of Truth

**Location:** `/agents/*.json`

Each agent has a comprehensive JSON file containing:

```json
{
  "name": "Agent Name",
  "title": "Role & Specialization",
  "race": "WoW Race",
  "class": "WoW Class",
  "specialization": "Technical Focus",
  "personality": { /* character traits */ },
  "technical_expertise": {
    "primary_skills": ["..."],
    "languages": ["..."],
    "frameworks": ["..."],
    "tools": ["..."],
    "specialties": ["..."]
  },
  "coordination": {
    "when_to_call": ["..."], // ← Your selection guide
    "works_best_with": ["..."]
  },
  "ai_instructions": { /* detailed prompts for LLMs */ },
  "signature_abilities": [ /* special capabilities */ ]
}
```

**For AI Assistants:** Before invoking an agent, you MAY read their JSON file to understand:
- Their expertise and limitations
- Their communication style
- Quality standards they enforce
- Who they coordinate with best

**However:** Reading the JSON is optional. The tables above provide enough context for most decisions.

---

## Decision Tree for LLMs

```
User Request Received
    ↓
Is this a complex, multi-step task?
    ├─ YES → Call Rodrim to break it down into quests
    └─ NO → Continue
         ↓
What domain does this task belong to?
    ├─ Documentation → Chronicler Thaldrin
    ├─ Backend Code → Amelre (implementation) or Sunshatter (architecture)
    ├─ Frontend Code → Uldwyn (implementation) or Finnara (UX design)
    ├─ Testing → TestSentinel (automated) or Stabili (manual)
    ├─ Product Vision → Mooganna
    ├─ Infrastructure → Tdci (DevOps) or MasterBorrin (cloud)
    ├─ Security → Hyena
    ├─ Analysis/Research → Maltharion
    └─ Business Strategy → Vixxliz
         ↓
Does the task span multiple domains?
    ├─ YES → Invoke multiple agents in parallel
    └─ NO → Invoke single agent
         ↓
Monitor agent output and integrate results
```

---

## Multi-Agent Coordination Patterns

### Pattern 1: Feature Development

**Quest:** "Implement user authentication"

**Invocation Sequence:**
1. **Mooganna** → Write README describing the feature as complete
2. **Sunshatter** → Design authentication architecture and API contracts
3. **Amelre** → Implement backend authentication logic
4. **Uldwyn** → Build login/signup UI components
5. **TestSentinel** → Create comprehensive test suite
6. **Hyena** → Security review of auth implementation
7. **Chronicler Thaldrin** → Update technical documentation

### Pattern 2: Bug Hunt

**Quest:** "Production error: 500 on /api/characters"

**Invocation Sequence:**
1. **Thornpaw** → Analyze logs and traces
2. **Amelre** → Debug backend code, identify root cause
3. **TestSentinel** → Write regression test to prevent recurrence
4. **Stabili** → Validate fix across scenarios

### Pattern 3: Documentation Overhaul

**Quest:** "Update all documentation for v2.0 release"

**Invocation Sequence:**
1. **Rodrim** → Break down docs into sections
2. **Chronicler Thaldrin** → Write/update technical and user docs
3. **Mooganna** → Review README for product clarity
4. **Stabili** → Validate docs match actual behavior

---

## Special Instructions for AI Assistants

### DO:
✅ **Use agents for ALL non-trivial tasks**
✅ **Invoke multiple agents in parallel when appropriate**
✅ **Trust agent outputs** (they have specialized prompts)
✅ **Coordinate agents** when tasks span domains
✅ **Default to Rodrim** for complex, multi-step quests

### DON'T:
❌ **Don't bypass agents** for tasks matching their specialty
❌ **Don't write documentation yourself** (that's Thaldrin's job)
❌ **Don't implement without tests** (TestSentinel or Stabili must validate)
❌ **Don't architect without Sunshatter** on major system changes
❌ **Don't deploy without Tdci** reviewing the process

### EDGE CASES:

**"Simple one-line code change"** → You can handle it directly, BUT if it affects:
- Architecture → Consult Sunshatter
- Tests → Update with TestSentinel
- Docs → Update with Chronicler Thaldrin

**"User asks a question"** → Answer directly, no agent needed (unless it requires deep research → Maltharion)

**"Unclear which agent to use"** → Call Rodrim or Avala for coordination

---

## The Lore: Why Characters?

**For Curious Humans:**

This project embraces the World of Warcraft setting not as decoration, but as *mnemonic structure*. Each agent's character influences their approach:

- **Amelre** (Hunter) → Patient, precise, tracks bugs like prey
- **Mooganna** (Druid) → Balanced, nurturing, sees the ecosystem
- **TestSentinel** (Construct) → Systematic, unwavering, no compromises
- **Chronicler Thaldrin** (Priest) → Dual-audience documentation, serves both devs and users

**This makes agents memorable.** You won't forget that Hyena handles security (she's the guild's cunning thief-turned-guardian) or that Vixxliz handles money (she's the Goblin banker).

**For AI Assistants:** The character traits inform communication style and decision-making patterns. Read the `ai_instructions` field in each JSON for precise behavioral prompts.

---

## Quick Start for AI Assistants

**Scenario:** User says: *"Add a new `/status` command to check bot health"*

**Your Response:**

1. **Analyze:** This requires backend implementation + testing + documentation
2. **Invoke:**
   - **Amelre** → Implement `/status` command handler
   - **TestSentinel** → Write tests for the command
   - **Chronicler Thaldrin** → Update USER_GUIDE.md with new command
3. **Integrate:** Combine their outputs into cohesive result
4. **Report:** Summarize to user what was accomplished

---

## Agent Availability: All 29 Heroes

<details>
<summary><b>Complete Guild Roster (click to expand)</b></summary>

1. **Amelre** - Backend Developer (Hunter)
2. **Avala** - HR & Team Morale (Priestess)
3. **Bridgekeeper** - API Integration Specialist
4. **Chronicler Thaldrin** - Documentation Master (Priest)
5. **Dreadcleave** - Performance Profiler
6. **Failsafe** - Error Handling Specialist
7. **Finnara** - UX Designer (Sentinel)
8. **Gearspark** - Build Systems Engineer
9. **Grimstone Earthmender** - Database Architect
10. **Hyena** - Cybersecurity Specialist (Druid/Thief)
11. **Ironwulf** - Chaos Engineer (Hunter)
12. **Jilbax** - Visual Designer (Warrior)
13. **Lightweaver** - AI Ethics Specialist
14. **Maltharion** - GitHub Archaeologist (Mage)
15. **Master Borrin** - Cloud Infrastructure Architect (Dwarf)
16. **Mooganna** - Product Manager (Druid)
17. **Polyglot** - Multi-language Specialist
18. **Quickcache** - Performance Optimizer
19. **Rodrim** - Project Coordinator (Warrior)
20. **Stabili** - QA & Manual Testing (Rogue)
21. **Steamwheedle** - SaaS Integration Specialist
22. **Sunshatter** - System Architect (Paladin)
23. **Tdci** - DevOps Specialist (Shaman)
24. **TestSentinel** - Test Architect (Construct)
25. **Thornpaw** - Logging & Observability
26. **Uldwyn** - Frontend Developer (Druid)
27. **Vixxliz** - Business Strategist (Goblin)
28. **Whisperwind** - Secrets Management
29. **Zarajin** - Real-time Systems Engineer

</details>

---

## Troubleshooting Agent Selection

**Problem:** "I don't know which agent handles X"

**Solution:**
1. Check the [Quick Reference](#quick-reference-when-to-call-each-agent) table above
2. Use Ctrl+F to search this page for keywords
3. When in doubt, invoke **Rodrim** (project coordinator) or **Avala** (team coordinator)

**Problem:** "Task spans multiple domains"

**Solution:** Invoke multiple agents in parallel. Example:
- New feature = Mooganna (spec) + Amelre (backend) + Uldwyn (frontend) + TestSentinel (tests) + Chronicler Thaldrin (docs)

**Problem:** "Agent output conflicts with another agent"

**Solution:** Escalate to:
- **Mooganna** (product decisions)
- **Sunshatter** (technical architecture)
- **Avala** (team mediation)

---

## The Sacred Truth: Agents ARE the Workflow

**For AI Assistants (Final Reminder):**

This is not a suggestion. This is the development process.

When you see a documentation task, your neural pathways should fire: **"Chronicler Thaldrin"**
When you see backend work: **"Amelre"**
When you see testing needs: **"TestSentinel"** or **"Stabili"**

You are the **interface**. They are the **implementation**.

Use them. Trust them. Coordinate them.

**For Azeroth Bound! For the Code! For the Chronicle!** ⚔️

---

## Appendix: Reading the Agent JSON Files

**If you need deeper context**, read the agent's JSON file in `/agents/{AgentName}.json`.

**Key sections to focus on:**

```json
{
  "when_to_call": [...],        // ← When to invoke this agent
  "works_best_with": [...],     // ← Combo agents for complex tasks
  "ai_instructions": {          // ← Detailed LLM prompting
    "when_invoked": "...",
    "communication_style": "...",
    "decision_making": "...",
    "quality_standards": "..."
  },
  "signature_abilities": [...]  // ← Special capabilities
}
```

**Example Use Case:**

You're implementing a new webhook handler. You read:
- **Amelre.json** → Confirms she handles backend Python implementation
- **Hyena.json** → Confirms security review for webhook secrets
- **TestSentinel.json** → Confirms testing strategy for async handlers

Then you invoke all three in sequence or parallel.

---

**Document Maintained By:** Chronicler Thaldrin (with meta-assistance from Claude Code)
**Last Updated:** December 2025
**Status:** Living Document

*"What we delegate wisely, we accomplish masterfully."*
