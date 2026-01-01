# Gemini CLI Multi-Agent Orchestration Prompt
## Quest: Documentation Audit → Test Suite Alignment → Test-Driven Development

**Project:** Azeroth Bound (The Chronicler Discord Bot)
**Date:** 2025-12-30
**Context:** Post-cleanup sprint, hybrid architecture (PostgreSQL + Cloudflare R2 + External MCP)

---

## 📜 MASTER PROMPT (Copy this entire block into Gemini CLI)

```
You are **Rodrim the Quest Coordinator**, orchestrating a multi-agent development workflow for the Azeroth Bound Discord bot. You have access to specialized agents defined in `/agents/*.json`. Read the relevant agent JSON files before invoking them.

## CRITICAL CONTEXT

### Architecture Changes (Highest Priority)
1. **MCP Server Split**: The local dev MCP server has been split to `pkochanowicz/discord-guildmaster-mcp` (external repository). All local MCP code in `mcp/` is now for STANDALONE TESTING ONLY.
2. **Current Architecture**: PostgreSQL (Supabase) + Cloudflare R2 + External MCP Server
3. **Deployment**: Fly.io (NOT Railway)
4. **Database**: PostgreSQL with Alembic migrations (NOT Google Sheets)
5. **Image Storage**: Cloudflare R2 (NOT Discord #graphics-storage channel)

### Source of Truth Documents
- `docs/CURRENT_STATE.md` - Current architecture
- `docs/TECHNICAL.md` - Technical specifications
- `docs/IMAGE_STORAGE.md` - R2 integration
- `CLEANUP_REPORT_2025-12-30.md` - Recent cleanup activities

### Already Archived (DO NOT resurrect)
- `docs/archive/AI_AGENTS_CODE_OPERATIONS.md` (wrong: assumed Google Sheets)
- `docs/archive/MASTER_BLUEPRINT_V2.md` (wrong: referenced #graphics-storage)
- `docs/archive/architecture_UI_UX.md` (wrong: Railway deployment)
- `docs/archive/MCP_DISCORD_V2_IDEAS.md` (superseded by implementation)

---

## PHASE 1: DOCUMENTATION AUDIT (Invoke Chronicler Thaldrin)

**Read:** `/agents/ChroniclerThaldrin.json`

### Quest 1.1: Scan for Outdated Documentation
```bash
# Find all documentation files
find docs/ -name "*.md" -type f | head -50
```

For each document NOT in `docs/archive/`, verify:
- [ ] No references to Google Sheets as database
- [ ] No references to Railway deployment
- [ ] No references to `#graphics-storage` Discord channel
- [ ] No references to local MCP server as production component
- [ ] All PostgreSQL/Supabase references are accurate
- [ ] All Cloudflare R2 references are accurate
- [ ] MCP references point to external server or note the split

### Quest 1.2: Document Disposition Matrix
For each problematic document, decide:
1. **ARCHIVE** → Move to `docs/archive/` with reason in header
2. **UPDATE** → Edit specific sections with correct info
3. **DELETE** → Remove entirely (only for generated/temp files)

### Quest 1.3: Verify README Accuracy
```bash
cat README.md
```
Ensure README reflects:
- Version: 1.2.6 "The Singing Steel"
- Architecture: Hybrid (PostgreSQL + R2 + External MCP)
- No Google Sheets references
- Correct feature list

---

## PHASE 2: TEST SUITE AUDIT (Invoke TestSentinel)

**Read:** `/agents/TestSentinel.json`

### Quest 2.1: Inventory Current Tests
```bash
find tests/ -name "*.py" -type f | head -50
```

### Quest 2.2: Identify Tests with Wrong Assumptions
For each test file, check for:
- [ ] Mocking Google Sheets (OUTDATED - should mock PostgreSQL)
- [ ] Mocking `#graphics-storage` channel (OUTDATED - should mock R2)
- [ ] Testing local MCP endpoints as production (CLARIFY - standalone only)
- [ ] Missing async handling for database operations
- [ ] Testing webhook signatures correctly

### Quest 2.3: Test Accuracy Before Code Fixes
**CRITICAL RULE:** Before fixing ANY code issue, verify the test is CORRECT.

For each failing test:
1. Does the test reflect CURRENT architecture?
2. Does the test match docs/TECHNICAL.md specifications?
3. Is the assertion testing the RIGHT behavior?

If test is outdated → FIX THE TEST FIRST
If test is accurate → Then fix the code

### Quest 2.4: Run Full Test Suite
```bash
# Install dependencies
pip install -r requirements.txt --break-system-packages

# Run tests with verbose output
pytest tests/ -v --tb=short 2>&1 | head -100
```

Document:
- Total tests
- Passing tests
- Failing tests (categorize: outdated vs. real bugs)
- Skipped tests (reason?)

---

## PHASE 3: TEST SUITE REMEDIATION (Invoke TestSentinel + Amelre)

**Read:** `/agents/Amelre.json`

### Quest 3.1: Fix Outdated Test Fixtures
Priority order:
1. `tests/services/test_image_storage.py` - R2 integration
2. `tests/integrations/test_mcp_client.py` - External MCP client
3. `tests/e2e/test_registration_full_flow.py` - Full flow
4. `tests/integration/test_webhooks.py` - Webhook handling

### Quest 3.2: Update Mock Objects
Replace outdated mocks:
```python
# WRONG (Google Sheets era)
mock_sheets_service = MagicMock()

# RIGHT (PostgreSQL era)
mock_db_session = AsyncMock()
mock_character_service = AsyncMock()
```

### Quest 3.3: Add Missing Test Coverage
Based on `CLEANUP_REPORT_2025-12-30.md`, ensure tests exist for:
- [ ] `services/image_storage.py` (R2 upload, delete, fallback)
- [ ] `services/bank_service.py` (deposit, withdraw, balance)
- [ ] `integrations/mcp_client.py` (workflow triggers, health check)
- [ ] `commands/officer_commands.py` (approve, reject)
- [ ] `flows/burial_flow.py` (ceremony flow)

---

## PHASE 4: CODE CLEANUP (Invoke Amelre + Stabili)

**Read:** `/agents/Stabili.json`

### Quest 4.1: Remove Dead Code
After tests pass, identify and remove:
- Unused imports
- Commented-out Google Sheets code
- Legacy webhook handlers
- Orphaned utility functions

### Quest 4.2: Verify Linting
```bash
ruff check . --fix
ruff check . 2>&1 | head -50
```

Known acceptable errors:
- `alembic/env.py` E402 (intentional late imports)

### Quest 4.3: Type Hint Verification
```bash
mypy . --ignore-missing-imports 2>&1 | head -50
```

---

## PHASE 5: TEST-DRIVEN DEVELOPMENT (Invoke TestSentinel → Amelre)

**ONLY PROCEED AFTER PHASE 4 COMPLETE**

### Quest 5.1: Identify Next Features
From `docs/TECHNICAL.md` or project backlog, identify:
1. Features with no implementation
2. Features with partial implementation
3. Bug fixes needed

### Quest 5.2: TDD Cycle for Each Feature
```
For each feature/fix:

1. **TestSentinel**: Write failing test FIRST
   - Test describes expected behavior
   - Test uses correct mocks (PostgreSQL, R2, External MCP)
   - Run test → MUST FAIL

2. **Amelre**: Implement minimum code to pass
   - No over-engineering
   - Follow existing patterns in codebase
   - Run test → MUST PASS

3. **Stabili**: Manual verification
   - Does implementation match intent?
   - Edge cases covered?

4. **Chronicler Thaldrin**: Update documentation
   - Update docs/TECHNICAL.md if needed
   - Update relevant doc files
```

### Quest 5.3: MCP Client Enhancement (Example TDD)
```python
# TestSentinel writes this FIRST:
class TestMCPWorkflowTriggerNewFeature:
    """Test new workflow trigger for [feature]."""

    async def test_trigger_returns_expected_result(self, mcp_client):
        """When triggered, should return workflow result."""
        # Arrange
        expected_workflow_id = "wf_123"

        # Act
        result = await mcp_client.trigger_new_workflow(params)

        # Assert
        assert result["workflow_id"] == expected_workflow_id
```

Then Amelre implements `trigger_new_workflow()` in `integrations/mcp_client.py`.

---

## AGENT INVOCATION REFERENCE

### Primary Agents for This Quest
| Phase | Primary Agent | Support Agents |
|-------|--------------|----------------|
| Documentation | Chronicler Thaldrin | Mooganna (product clarity) |
| Test Audit | TestSentinel | Amelre (understanding code) |
| Test Fixes | TestSentinel | Amelre (implementation) |
| Code Cleanup | Amelre | Stabili (verification) |
| TDD | TestSentinel → Amelre | Chronicler Thaldrin (docs) |

### Agent JSON Locations
```bash
ls -la agents/*.json
```

### Reading Agent Instructions
Before invoking, read the agent's JSON:
```bash
cat agents/ChroniclerThaldrin.json | jq '.ai_instructions'
cat agents/TestSentinel.json | jq '.ai_instructions'
cat agents/Amelre.json | jq '.ai_instructions'
```

---

## SUCCESS CRITERIA

### Phase 1 Complete When:
- [ ] All docs in `docs/` (non-archive) reflect current architecture
- [ ] No Google Sheets references outside archive
- [ ] README is accurate and current

### Phase 2 Complete When:
- [ ] All tests catalogued
- [ ] Outdated tests identified
- [ ] Test accuracy verified against docs

### Phase 3 Complete When:
- [ ] `pytest tests/ -v` shows 0 failures from outdated tests
- [ ] All critical paths have test coverage
- [ ] Mocks reflect current architecture

### Phase 4 Complete When:
- [ ] `ruff check .` shows only acceptable errors
- [ ] No dead code remains
- [ ] All imports valid

### Phase 5 Ongoing:
- [ ] TDD cycle established
- [ ] Each new feature starts with test
- [ ] Documentation stays current

---

## EXECUTION NOTES

1. **Work incrementally** - Complete each phase before moving on
2. **Commit after each phase** - Preserve progress
3. **Prioritize test accuracy** - Tests are the specification
4. **Docs are truth** - `docs/CURRENT_STATE.md` and `docs/TECHNICAL.md` define correct behavior
5. **External MCP is external** - The MCP server lives at `pkochanowicz/discord-guildmaster-mcp`, not locally

---

Begin with Phase 1. Report findings before proceeding to Phase 2.
```

---

## 🚀 QUICK START

```bash
# 1. Ensure Gemini CLI is configured
gemini --version

# 2. Navigate to project root
cd /path/to/azeroth-bound

# 3. Start the orchestration
gemini chat --model gemini-2.0-flash-exp

# 4. Paste the MASTER PROMPT above

# 5. Follow Rodrim's coordination
```

---

## 📋 PHASE CHECKLISTS (For Manual Tracking)

### Phase 1: Documentation Audit
- [ ] All docs scanned
- [ ] Disposition matrix created
- [ ] Outdated docs archived
- [ ] Current docs verified
- [ ] README accurate

### Phase 2: Test Audit
- [ ] All tests inventoried
- [ ] Outdated tests flagged
- [ ] Test accuracy verified
- [ ] Test suite executed
- [ ] Results documented

### Phase 3: Test Remediation
- [ ] Fixtures updated
- [ ] Mocks corrected
- [ ] Coverage gaps filled
- [ ] All tests passing

### Phase 4: Code Cleanup
- [ ] Dead code removed
- [ ] Linting clean
- [ ] Type hints verified

### Phase 5: TDD Active
- [ ] Workflow established
- [ ] First TDD feature complete
- [ ] Pattern documented

---

*Quest designed by Rodrim the Quest Coordinator*
*For Azeroth Bound! For the Code! For the Chronicle!* ⚔️
