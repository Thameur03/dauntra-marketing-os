from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

import psycopg
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS_DIR = ROOT / "migrations"

load_dotenv(ROOT / ".env")

database_url = os.getenv("DATABASE_URL")

if not database_url:
    print("ERROR: DATABASE_URL is missing from .env")
    sys.exit(1)


def checksum(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


print()
print("==========================================")
print(" DAUNTRA DATABASE MIGRATIONS")
print("==========================================")
print()

try:
    conn = psycopg.connect(
        database_url,
        autocommit=True,
        sslmode="require",
        connect_timeout=15,
    )
except Exception as exc:
    print("DATABASE CONNECTION: FAIL")
    print()
    print(type(exc).__name__ + ":", exc)
    print()
    print(
        "Check the Supabase connection string and make sure you copied "
        "the Session pooler URL correctly."
    )
    sys.exit(1)


try:
    with conn.cursor() as cur:
        cur.execute("SELECT current_database(), current_user")
        db_name, db_user = cur.fetchone()

    print("DATABASE CONNECTION: PASS")
    print(f"Database: {db_name}")
    print(f"Role:     {db_user}")
    print()

    # Migration registry lives outside application tables.
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS marketing_schema_migrations (
                filename TEXT PRIMARY KEY,
                sha256 TEXT NOT NULL,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )

    migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))

    if not migration_files:
        print("ERROR: No migrations found.")
        sys.exit(1)

    for path in migration_files:
        digest = checksum(path)

        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT sha256
                FROM marketing_schema_migrations
                WHERE filename = %s
                """,
                (path.name,),
            )
            row = cur.fetchone()

        if row:
            existing_checksum = row[0]

            if existing_checksum != digest:
                print(f"ERROR   {path.name}")
                print("        Migration was modified after being applied.")
                print("        Never rewrite an applied migration.")
                sys.exit(1)

            print(f"SKIP    {path.name} (already applied)")
            continue

        print(f"APPLY   {path.name}")

        sql = path.read_text(encoding="utf-8")

        try:
            with conn.cursor() as cur:
                cur.execute(sql)

            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO marketing_schema_migrations (
                        filename,
                        sha256
                    )
                    VALUES (%s, %s)
                    """,
                    (path.name, digest),
                )

            print(f"OK      {path.name}")

        except Exception as exc:
            try:
                conn.rollback()
            except Exception:
                pass

            print()
            print(f"FAILED  {path.name}")
            print(type(exc).__name__ + ":", exc)
            sys.exit(1)

    print()
    print("==========================================")
    print(" MIGRATIONS COMPLETE")
    print("==========================================")

finally:
    conn.close()
