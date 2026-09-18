from __future__ import annotations

import os
import sys

import psycopg
from dotenv import load_dotenv


load_dotenv()

database_url = os.getenv("DATABASE_URL")

if not database_url:
    print("ERROR: DATABASE_URL missing.")
    sys.exit(1)


EXPECTED_TABLES = {
    "subjects",
    "research_packets",
    "content_tests",
    "content_items",
    "assets",
    "qa_results",
    "campaigns",
    "publication_jobs",
    "posts",
    "metric_snapshots",
    "click_events",
    "conversions",
    "decisions",
    "system_errors",
}


def fail(message: str) -> None:
    print(f"ERROR   {message}")
    sys.exit(1)


conn = psycopg.connect(
    database_url,
    sslmode="require",
    connect_timeout=15,
)

try:
    print()
    print("==========================================")
    print(" REAL SUPABASE DATABASE CHECK")
    print("==========================================")
    print()

    with conn.cursor() as cur:
        cur.execute("SELECT version()")
        version = cur.fetchone()[0]

    print("OK      PostgreSQL connection")
    print(f"        {version.split(',')[0]}")
    print()

    # --------------------------------------------------------
    # Application tables
    # --------------------------------------------------------

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            """
        )

        actual_tables = {row[0] for row in cur.fetchall()}

    missing = EXPECTED_TABLES - actual_tables

    for table in sorted(EXPECTED_TABLES):
        if table in actual_tables:
            print(f"OK      table: {table}")
        else:
            print(f"MISSING table: {table}")

    if missing:
        fail(
            "Missing application tables: "
            + ", ".join(sorted(missing))
        )

    print()

    # --------------------------------------------------------
    # RLS
    # --------------------------------------------------------

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                c.relname,
                c.relrowsecurity
            FROM pg_class c
            JOIN pg_namespace n
              ON n.oid = c.relnamespace
            WHERE n.nspname = 'public'
              AND c.relname = ANY(%s)
            """,
            (list(EXPECTED_TABLES),),
        )

        rls_rows = dict(cur.fetchall())

    bad_rls = []

    for table in sorted(EXPECTED_TABLES):
        enabled = rls_rows.get(table, False)

        if enabled:
            print(f"OK      RLS: {table}")
        else:
            print(f"ERROR   RLS disabled: {table}")
            bad_rls.append(table)

    if bad_rls:
        fail("RLS is not enabled on every Marketing OS table.")

    print()

    # --------------------------------------------------------
    # Storage bucket
    # --------------------------------------------------------

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                id,
                public,
                file_size_limit,
                allowed_mime_types
            FROM storage.buckets
            WHERE id = 'marketing-assets'
            """
        )

        bucket = cur.fetchone()

    if not bucket:
        fail("marketing-assets bucket does not exist.")

    bucket_id, is_public, limit_bytes, mime_types = bucket

    if is_public:
        fail("marketing-assets bucket is PUBLIC.")

    print("OK      storage bucket: marketing-assets")
    print("OK      bucket is private")
    print(f"OK      max file size: {limit_bytes} bytes")
    print(f"OK      allowed MIME types: {', '.join(mime_types)}")

    print()

    # --------------------------------------------------------
    # Migration history
    # --------------------------------------------------------

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT filename, applied_at
            FROM marketing_schema_migrations
            ORDER BY filename
            """
        )

        migrations = cur.fetchall()

    if not migrations:
        fail("Migration history is empty.")

    for filename, applied_at in migrations:
        print(f"OK      migration: {filename}")
        print(f"        applied: {applied_at}")

    print()
    print("==========================================")
    print(" SECTION 2B: PASS")
    print("==========================================")
    print()

finally:
    conn.close()
