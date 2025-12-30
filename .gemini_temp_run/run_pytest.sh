#!/bin/bash
poetry run pytest tests/schema/test_schema_integrity.py > ./test_output.log 2>&1
