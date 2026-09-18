#!/usr/bin/env bash

set -euo pipefail

echo
echo "=========================================="
echo " DAUNTRA FOUNDATION CHECK"
echo "=========================================="
echo

FILES=(
  "README.md"
  "BUILD_STATUS.md"
  ".gitignore"
  ".env.example"

  "brand/product_truth.yaml"
  "brand/brand_profile.yaml"
  "brand/audience_profile.yaml"
  "brand/capability_manifest.yaml"
  "brand/content_strategy.yaml"

  "config/settings.yaml"
  "config/platforms.yaml"
  "config/versions.yaml"

  "docs/DECISIONS.md"
  "docs/PRODUCT_TRUTH_SUMMARY.md"
  "docs/SECTION_1_CHECKLIST.md"
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

if grep -q "publishing:" config/settings.yaml &&
   grep -A4 "publishing:" config/settings.yaml | grep -q "enabled: false"; then
    echo "OK      Publishing defaults to disabled"
else
    echo "ERROR   Publishing safety setting not found"
    FAILED=1
fi

if grep -q "kill_switch: true" config/settings.yaml; then
    echo "OK      Kill switch defaults to ON"
else
    echo "ERROR   Kill switch is not ON"
    FAILED=1
fi

if grep -q 'default_if_unknown: "BLOCK"' brand/capability_manifest.yaml; then
    echo "OK      Unknown capabilities default to BLOCK"
else
    echo "ERROR   Capability default BLOCK rule missing"
    FAILED=1
fi

if grep -q "marketing_allowed: false" brand/capability_manifest.yaml; then
    echo "OK      Blocked capabilities are present"
else
    echo "ERROR   No blocked capabilities found"
    FAILED=1
fi

if grep -q 'display_name: "Conversational AI Coach"' \
   brand/capability_manifest.yaml; then
    echo "OK      AI coach truth explicitly recorded"
else
    echo "ERROR   AI coach capability entry missing"
    FAILED=1
fi

if grep -q 'status: "PRE_LAUNCH"' brand/product_truth.yaml; then
    echo "OK      Product state is PRE_LAUNCH"
else
    echo "ERROR   Product release state missing"
    FAILED=1
fi

echo

if [[ "$FAILED" -eq 0 ]]; then
    echo "=========================================="
    echo " SECTION 1: PASS"
    echo "=========================================="
    echo
    echo "Foundation and product truth are ready."
    exit 0
else
    echo "=========================================="
    echo " SECTION 1: FAIL"
    echo "=========================================="
    exit 1
fi
