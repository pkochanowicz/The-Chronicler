# Azeroth Bound Bot - Test Suite (Phase 2)

This directory contains the comprehensive test suite for the Azeroth Bound Discord Bot (Schema Reformation 2.0).

## 🧪 Testing Philosophy

This suite follows **Documentation-Driven Development**. 
Tests are written based strictly on `docs/MASTER_BLUEPRINT_SCHEMA_REFORMATION.md` and `docs/TECHNICAL.md`.

## 📂 Organization

- **unit/**: Tests for models, validators, and pure utilities. Fast, no I/O.
- **integration/**: Tests for services, flows, and webhooks. Mocks external APIs (Discord, Google Sheets).

## 🚀 Running Tests (Phase 3)

Tests are currently implemented but will fail until implementation matches the specifications.

To run tests:
```bash
pytest
```

To run a specific category:
```bash
pytest tests/unit
pytest tests/integration
```

## 📊 Coverage Goals

- **100% enum validation coverage**
- **100% interactive flow step coverage**
- **100% webhook trigger coverage**
- **100% state machine transition coverage**

## ⚠️ Important

Do NOT modify these tests to match the code. Modify the code to match these tests. 
These tests are the contract.