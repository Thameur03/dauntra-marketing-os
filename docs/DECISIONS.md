# DAUNTRA Marketing OS — V1 Decisions

This file records intentional architecture decisions.

Do not silently change these decisions while implementing the system.

---

## 1. Solo-developer principle

DAUNTRA itself is the priority.

The Marketing OS must save founder time rather than become a second product
that requires constant maintenance.

---

## 2. Global English first

V1 supports:

- Market: GLOBAL
- Language: English

Arabic and GCC-specific localization are deferred until the GLOBAL_EN
pipeline works reliably.

---

## 3. Product capabilities are allowlisted

Marketing may claim a product capability only when:

    status: available
    marketing_allowed: true

in:

    brand/capability_manifest.yaml

Unknown capabilities are blocked by default.

---

## 4. Publishing is disabled during early development

We first build:

subject
→ research
→ content
→ rendering
→ QA

Only after those stages work do we connect publishing providers.

---

## 5. Reddit stays manual

V1 creates Reddit-ready drafts.

It does not automatically publish Reddit submissions.

---

## 6. TikTok custom API integration is not a V1 requirement

Use a compliant existing publishing integration later where possible.

Otherwise generate publish-ready assets and finish posting manually.

---

## 7. No infrastructure for infrastructure's sake

Do not add:

- Kubernetes
- message brokers
- distributed microservices
- Redis unless genuinely required
- Cloudflare Tunnel unless a concrete remote-access need appears
- extra databases
- multi-tenant architecture

The simplest implementation that satisfies the requirements wins.

---

## 8. Database timestamps use UTC

User-facing scheduling will eventually use the target market's local timezone.

Stored timestamps use UTC.

---

## 9. Deterministic rendering

AI writes structured content.

AI does not write arbitrary HTML/CSS or redesign templates.

Templates control:

- layout
- colors
- typography
- dimensions
- logo placement
- safe zones

---

## 10. Sensitive claims require evidence

Specific fitness, nutrition, supplement, health, or physiological claims must
carry evidence.

Automated QA does not replace human review for sensitive claims.

---

## 11. Fail safely

When the system does not know:

- capability → BLOCK
- evidence → BLOCK
- publication status → UNKNOWN
- analytics conclusion → INSUFFICIENT_DATA

Never guess in order to keep automation moving.

---

## 12. n8n comes later

Business logic is implemented and tested in code first.

n8n will eventually orchestrate already-working components.

It must not become the only place where core business logic exists.


---

## 13. Audited product positioning

The initial Marketing OS audience is:

    data-oriented resistance-training / gym users

This is based on the existing DAUNTRA product rather than a hypothetical
future roadmap.

Do not broaden the primary marketing position to endurance, wearables,
medical health, or body-transformation tracking unless the product changes.


---

## 14. "Lab Insights" is blocked from V1 marketing

Although a training/nutrition consistency feature exists under the historical
name "Lab Insights", it is excluded from V1 marketing until:

1. production backend availability is verified, and
2. the naming is intentionally reviewed.

This avoids confusion with medical laboratory analysis.


---

## 15. No AI-coach positioning

DAUNTRA currently has no conversational AI coach, interactive LLM chat,
AI workout generator, adaptive training engine, or AI meal planner.

The Marketing OS must not use "AI coach" positioning.


---

## 16. Pre-launch subscription claims are blocked

Do not advertise:

- live Premium purchasing
- weekly/monthly/yearly prices
- free trials
- 30-day rewards
- 60-day rewards

until implementation and store configuration are separately verified.


---

## 17. Marketing uses the audited product, not the roadmap

Future plans are not capabilities.

A feature becomes marketable only after:

1. it exists,
2. it works end-to-end,
3. its manifest entry is updated,
4. `marketing_allowed` is explicitly set to `true`.
