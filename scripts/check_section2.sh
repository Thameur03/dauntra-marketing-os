#!/usr/bin/env bash

set -euo pipefail

echo
echo "=========================================="
echo " DAUNTRA SECTION 2A CHECK"
echo "=========================================="
echo

FILES=(
  "migrations/0001_marketing_os_core.sql"
  "contracts/__init__.py"
  "contracts/common.py"
  "contracts/subject.py"
  "contracts/research.py"
  "contracts/content.py"
  "contracts/qa.py"
  "contracts/render.py"
  "contracts/publishing.py"
  "contracts/analytics.py"
  "docs/database/DATA_MODEL.md"
  "docs/database/CONTRACTS.md"
  "requirements.txt"
  "requirements-dev.txt"
)

FAILED=0

for FILE in "${FILES[@]}"; do
    if [[ -s "$FILE" ]]; then
        printf "OK      %s\n" "$FILE"
    else
        printf "MISSING %s\n" "$FILE"
        FAILED=1
    fi
done

echo

TABLES=(
  subjects
  research_packets
  content_tests
  content_items
  assets
  qa_results
  campaigns
  publication_jobs
  posts
  metric_snapshots
  click_events
  conversions
  decisions
  system_errors
)

for TABLE in "${TABLES[@]}"; do
    if grep -q "CREATE TABLE $TABLE" migrations/0001_marketing_os_core.sql; then
        printf "OK      table: %s\n" "$TABLE"
    else
        printf "MISSING table: %s\n" "$TABLE"
        FAILED=1
    fi
done

echo

if grep -q "idempotency_key TEXT NOT NULL UNIQUE" \
    migrations/0001_marketing_os_core.sql; then
    echo "OK      Publishing idempotency enforced"
else
    echo "ERROR   Publishing idempotency missing"
    FAILED=1
fi

if grep -q "'UNKNOWN'" migrations/0001_marketing_os_core.sql; then
    echo "OK      UNKNOWN state supported"
else
    echo "ERROR   UNKNOWN state missing"
    FAILED=1
fi

if grep -q "raw_metrics_json JSONB" \
    migrations/0001_marketing_os_core.sql; then
    echo "OK      Raw provider metrics preserved"
else
    echo "ERROR   Raw metrics storage missing"
    FAILED=1
fi

if grep -q "first_touch_click_id" \
    migrations/0001_marketing_os_core.sql &&
   grep -q "last_touch_click_id" \
    migrations/0001_marketing_os_core.sql; then
    echo "OK      First/last-touch attribution supported"
else
    echo "ERROR   Attribution fields missing"
    FAILED=1
fi

echo

if [[ "$FAILED" -ne 0 ]]; then
    echo "SECTION 2A: FAIL"
    exit 1
fi

echo "SECTION 2A STRUCTURE: PASS"

if [[ -x ".venv/bin/python" ]]; then
    echo
    echo "Running Python contract tests..."
    .venv/bin/python -m pytest -q tests/contracts
else
    echo
    echo "Python virtual environment not created yet."
    echo "Structure validation passed."
fi
