#!/usr/bin/env bash

set -u

cd "$(dirname "$0")/.."

echo
echo "=========================================="
echo " DAUNTRA SECTION 3A LOCAL CHECK"
echo "=========================================="
echo

FILES=(
  "app/llm/base.py"
  "app/llm/factory.py"
  "app/llm/gemini.py"
  "app/retrieval/pubmed.py"
  "app/research_models.py"
  "app/research_engine.py"
  "prompts/research_system.txt"
  "scripts/configure_gemini.py"
  "scripts/check_gemini.py"
  "scripts/check_pubmed.py"
  "scripts/research_subject.py"
  "contracts/research.py"
)

FAILED=0

for FILE in "${FILES[@]}"
do

    if [[ -s "$FILE" ]]
    then
        printf "OK      %s\n" "$FILE"
    else
        printf "MISSING %s\n" "$FILE"
        FAILED=1
    fi

done

echo

if grep -q '^google-genai' requirements.txt
then
    echo "OK      Google Gen AI SDK"
else
    echo "ERROR   Google Gen AI SDK missing"
    FAILED=1
fi

if grep -q 'store=False' app/llm/gemini.py
then
    echo "OK      Gemini server storage disabled"
else
    echo "ERROR   store=False missing"
    FAILED=1
fi

if grep -q 'model_json_schema' app/llm/gemini.py
then
    echo "OK      Structured-output schema enforcement"
else
    echo "ERROR   Structured-output enforcement missing"
    FAILED=1
fi

if grep -q 'eutils.ncbi.nlm.nih.gov' app/retrieval/pubmed.py
then
    echo "OK      PubMed scientific retrieval"
else
    echo "ERROR   PubMed retrieval missing"
    FAILED=1
fi

echo
echo "Running tests..."
echo

.venv/bin/python -m pytest -q \
    tests/contracts \
    tests/content_brain

TEST_STATUS=$?

if [[ "$TEST_STATUS" -ne 0 ]]
then
    FAILED=1
fi

echo

if [[ "$FAILED" -eq 0 ]]
then

    echo "=========================================="
    echo " SECTION 3A LOCAL: PASS"
    echo "=========================================="

    exit 0

else

    echo "=========================================="
    echo " SECTION 3A LOCAL: FAIL"
    echo "=========================================="

    exit 1

fi
