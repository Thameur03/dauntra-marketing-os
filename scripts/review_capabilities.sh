#!/usr/bin/env bash

set -euo pipefail

OUTPUT="data/capability_review.txt"

mkdir -p data

cat > "$OUTPUT" <<'HEADER'
============================================================
DAUNTRA — PRODUCT CAPABILITY REVIEW
============================================================

This file describes the REAL current state of DAUNTRA.

Allowed status values:

YES      = feature exists now and works
PARTIAL  = feature exists but has limitations
NO       = feature does not exist
PLANNED  = planned but not available yet
UNKNOWN  = needs checking

Do not describe future features as current features.

HEADER


ask_feature() {

    FEATURE_ID="$1"
    FEATURE_NAME="$2"

    echo
    echo "============================================================"
    echo "$FEATURE_NAME"
    echo "============================================================"
    echo

    while true; do
        read -r -p "Status [YES/PARTIAL/NO/PLANNED/UNKNOWN]: " STATUS
        STATUS=$(echo "$STATUS" | tr '[:lower:]' '[:upper:]')

        case "$STATUS" in
            YES|PARTIAL|NO|PLANNED|UNKNOWN)
                break
                ;;
            *)
                echo "Please enter YES, PARTIAL, NO, PLANNED, or UNKNOWN."
                ;;
        esac
    done

    echo
    read -r -p "What does this feature actually do? " DESCRIPTION

    echo
    read -r -p "What can marketing safely say about it? " ALLOWED

    echo
    read -r -p "Anything marketing must NOT claim? " RESTRICTIONS

    {
        echo
        echo "------------------------------------------------------------"
        echo "FEATURE_ID: $FEATURE_ID"
        echo "FEATURE_NAME: $FEATURE_NAME"
        echo "STATUS: $STATUS"
        echo
        echo "DESCRIPTION:"
        echo "$DESCRIPTION"
        echo
        echo "SAFE_MARKETING_CLAIMS:"
        echo "$ALLOWED"
        echo
        echo "RESTRICTIONS:"
        echo "$RESTRICTIONS"
        echo
    } >> "$OUTPUT"
}


echo
echo "DAUNTRA CAPABILITY REVIEW"
echo
echo "Answer according to the app AS IT EXISTS NOW."
echo
echo "If you are unsure, use UNKNOWN."
echo "If something is coming later, use PLANNED."
echo


ask_feature \
    "workout_tracking" \
    "Workout / Training Tracking"

ask_feature \
    "nutrition_tracking" \
    "Nutrition Tracking"

ask_feature \
    "micronutrients" \
    "Micronutrient Tracking"

ask_feature \
    "lab_insights" \
    "Lab / Biomarker Insights"

ask_feature \
    "wearable_integration" \
    "Wearable Integration"

ask_feature \
    "ai_coaching" \
    "AI Coaching / AI Recommendations"

ask_feature \
    "progress_analytics" \
    "Progress Analytics / Charts / Trends"


echo
echo "============================================================"
echo "OTHER FEATURES"
echo "============================================================"
echo

read -r -p "Does DAUNTRA have other important current features? [y/N]: " MORE

MORE=$(echo "$MORE" | tr '[:upper:]' '[:lower:]')

if [[ "$MORE" == "y" || "$MORE" == "yes" ]]; then

    while true; do

        echo
        read -r -p "Feature name: " EXTRA_NAME

        [[ -z "$EXTRA_NAME" ]] && break

        read -r -p "What does it do? " EXTRA_DESCRIPTION
        read -r -p "What can marketing safely say? " EXTRA_ALLOWED
        read -r -p "What must marketing NOT claim? " EXTRA_RESTRICTIONS

        {
            echo
            echo "------------------------------------------------------------"
            echo "EXTRA_FEATURE: $EXTRA_NAME"
            echo
            echo "DESCRIPTION:"
            echo "$EXTRA_DESCRIPTION"
            echo
            echo "SAFE_MARKETING_CLAIMS:"
            echo "$EXTRA_ALLOWED"
            echo
            echo "RESTRICTIONS:"
            echo "$EXTRA_RESTRICTIONS"
            echo
        } >> "$OUTPUT"

        echo
        read -r -p "Add another feature? [y/N]: " AGAIN
        AGAIN=$(echo "$AGAIN" | tr '[:upper:]' '[:lower:]')

        if [[ "$AGAIN" != "y" && "$AGAIN" != "yes" ]]; then
            break
        fi

    done
fi


echo
echo "============================================================"
echo "GENERAL PRODUCT QUESTIONS"
echo "============================================================"
echo

read -r -p "Is DAUNTRA currently usable by real users? " PRODUCT_STATE
read -r -p "Is the app currently in App Store, TestFlight, development, or another state? " DISTRIBUTION_STATE
read -r -p "What is the main thing DAUNTRA does better/differently? " DIFFERENTIATOR
read -r -p "What feature are you personally most proud of? " HERO_FEATURE
read -r -p "What should marketing NEVER say about DAUNTRA? " NEVER_SAY

{
    echo
    echo "============================================================"
    echo "GENERAL PRODUCT INFORMATION"
    echo "============================================================"
    echo
    echo "CURRENT_PRODUCT_STATE:"
    echo "$PRODUCT_STATE"
    echo
    echo "DISTRIBUTION_STATE:"
    echo "$DISTRIBUTION_STATE"
    echo
    echo "MAIN_DIFFERENTIATOR:"
    echo "$DIFFERENTIATOR"
    echo
    echo "HERO_FEATURE:"
    echo "$HERO_FEATURE"
    echo
    echo "NEVER_SAY:"
    echo "$NEVER_SAY"
    echo
} >> "$OUTPUT"


echo
echo
echo "============================================================"
echo " REVIEW COMPLETE"
echo "============================================================"
echo
echo "Saved to:"
echo
echo "  $OUTPUT"
echo
echo "Display it with:"
echo
echo "  cat $OUTPUT"
echo

