# DAUNTRA Marketing OS

Internal marketing automation system for DAUNTRA.

## Goal

The founder supplies useful marketing subjects.

The Marketing OS eventually handles:

    subject
      ↓
    research
      ↓
    evidence
      ↓
    content generation
      ↓
    platform adaptation
      ↓
    rendering
      ↓
    QA
      ↓
    human review where required
      ↓
    scheduling
      ↓
    publishing
      ↓
    attribution
      ↓
    analytics

without becoming a second full-time software product.

---

## Current build status

Section 1 — COMPLETE

Section 2 — COMPLETE

Next:

Section 3 — Content Brain

---

## Product truth

Marketing claims are controlled by:

    brand/capability_manifest.yaml

Unknown capabilities are blocked.

Future features are not considered current product capabilities.

---

## Primary V1 market

    GLOBAL English

Primary audience:

    data-oriented gym / resistance-training users

---

## Important files

    brand/product_truth.yaml
    brand/capability_manifest.yaml
    brand/brand_profile.yaml
    brand/audience_profile.yaml
    brand/content_strategy.yaml

    config/settings.yaml
    config/platforms.yaml
    config/versions.yaml

    docs/PRODUCT_TRUTH_SUMMARY.md
    docs/DECISIONS.md
    BUILD_STATUS.md

---

## Safety rule

A DAUNTRA product capability may be marketed only when:

    marketing_allowed: true

in:

    brand/capability_manifest.yaml

If the system is uncertain:

    BLOCK
