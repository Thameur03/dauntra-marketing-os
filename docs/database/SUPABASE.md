# DAUNTRA Marketing OS — Supabase

## Role

Supabase provides:

1. Managed PostgreSQL
2. Private object storage for rendered marketing assets

It is NOT being used as another frontend application platform in V1.

---

# Database connection

The local developer machine stores the PostgreSQL URL in:

    .env

Variable:

    DATABASE_URL

Never commit this value.

For an IPv4-only development network, use the Supabase Session pooler.

For infrastructure that supports direct IPv6 connectivity, a direct Postgres
connection may be used.

Always require SSL.

---

# Storage

Bucket:

    marketing-assets

Access:

    PRIVATE

Permanent public URLs are intentionally avoided.

Final social assets will later be:

- uploaded directly through publishing-provider APIs, or
- exposed temporarily through signed URLs if a provider requires them

---

# Access model

Marketing OS tables have Row Level Security enabled.

No anonymous/browser policies exist in V1.

Trusted server-side processes use privileged database credentials.

Never expose privileged database credentials in:

- browser JavaScript
- mobile applications
- rendered assets
- prompts
- Git repositories
- logs

---

# Migration rule

Applied migrations are immutable.

Never edit a migration after it has been applied.

Instead create:

    0003_...
    0004_...
    ...

The `marketing_schema_migrations` table stores migration checksums and prevents
an already-applied migration from silently changing.
