# Marketing OS Contracts

All boundaries between Marketing OS components use validated structured data.

## Why

We do not want:

    LLM text
      ↓
    random parsing
      ↓
    renderer failure

Instead:

    LLM
      ↓
    JSON
      ↓
    Pydantic validation
      ↓
    accepted data
      ↓
    next stage

If validation fails, the item does not proceed.

---

# Current contracts

## SubjectCreate

Founder input.

## ResearchPacket

Structured factual evidence package.

Contains:

- summary
- core finding
- nuance
- DAUNTRA relevance
- sources
- claims
- safe angles
- prohibited angles
- human review requirement

## Platform content

Separate contracts exist for:

- Instagram carousel
- TikTok video
- X
- Facebook
- Reddit

The platforms share research.

They do NOT share one master caption.

## QA

Every gate returns a structured result.

## Rendering

Renderer receives validated structured input.

It never receives arbitrary model-generated HTML/CSS.

## Publishing

Every publishing operation carries a unique idempotency key.

## Analytics

Normalized metrics are validated while provider-specific metrics remain
available as raw JSON.

## Conversion

Marketing attribution deliberately does not require storing user email.
