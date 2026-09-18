# DAUNTRA Marketing OS — Data Model

## Principle

The database is the system of record.

n8n, Postiz, renderers, LLM calls, and dashboards are workers/consumers.
None of them owns canonical state.

## Design priorities

1. Simple enough for one developer.
2. Every content item traceable back to a subject.
3. Every claim traceable back to research evidence.
4. Every published post traceable back to generated content.
5. Every click/conversion attributable when possible.
6. Unknown states are represented explicitly.
7. Raw provider payloads are preserved where useful.
8. No unnecessary microservice-style complexity.

---

# Main lineage

    subject
       ↓
    research_packet
       ↓
    content_test
       ↓
    content_item
       ├── asset
       ├── qa_result
       └── publication_job
                ↓
               post
                ↓
         metric_snapshot

Marketing attribution:

    content_item
       ↓
    campaign
       ↓
    click_event
       ↓
    conversion

---

# Why research is stored as JSONB

For V1, research evidence and claims are stored inside a structured
`research_packets` JSONB document.

We intentionally do NOT normalize every source and claim into separate
tables yet.

Reason:

- much less implementation complexity
- one research packet is naturally one unit
- Pydantic validates its internal structure
- we can normalize later if scale demands it

---

# Why status columns use TEXT + CHECK

We intentionally avoid PostgreSQL ENUM types.

TEXT + CHECK constraints are easier to migrate when statuses change.

---

# Why publication jobs are separate from posts

A scheduled/publishing attempt is not the same thing as a published post.

A job can be:

    PENDING
    SUBMITTING
    SCHEDULED
    PUBLISHED
    FAILED
    UNKNOWN
    CANCELLED

A `post` row exists only when an external platform/provider identity
is known.

`UNKNOWN` exists to prevent blind retries after network failures.

---

# Idempotency

Every publication job has a unique idempotency key.

This prevents:

    publish succeeded
    ↓
    network timeout
    ↓
    retry
    ↓
    duplicate social post

---

# Metrics

Cross-platform normalized metrics are stored in dedicated columns.

The complete provider response is also preserved in:

    raw_metrics_json

because platforms expose different metrics.

---

# Attribution

The database supports:

- campaign codes
- click IDs
- anonymous visitor IDs
- first-touch attribution
- last-touch attribution
- direct / unknown conversion

The Marketing OS does NOT need to store the user's email address.

The DAUNTRA/waitlist system can send a pseudonymous conversion identifier.

---

# Security

All Marketing OS tables are intended to be private.

V1 application access should happen from trusted server-side code.

Supabase service-role credentials must never be placed in browser/client code.
