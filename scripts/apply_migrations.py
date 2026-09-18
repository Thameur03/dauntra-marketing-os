from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

import psycopg
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS_DIR = ROOT / "migrations"

load_dotenv(
    ROOT / ".env"
)


database_url = os.getenv(
    "DATABASE_URL"
)


if not database_url:

    print(
        "ERROR: DATABASE_URL is missing from .env"
    )

    raise SystemExit(1)


def checksum(
    path: Path,
) -> str:

    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def ensure_migration_registry(
    conn: psycopg.Connection,
) -> None:
    """
    Create and immediately harden the internal migration
    registry.

    This runs before migration discovery so a fresh database
    never exposes the registry through normal application roles.
    """

    with conn.cursor() as cur:

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS
                public.marketing_schema_migrations (
                    filename TEXT PRIMARY KEY,
                    sha256 TEXT NOT NULL,
                    applied_at TIMESTAMPTZ
                        NOT NULL
                        DEFAULT NOW()
                )
            """
        )


        cur.execute(
            """
            ALTER TABLE
                public.marketing_schema_migrations
            ENABLE ROW LEVEL SECURITY
            """
        )


        cur.execute(
            """
            REVOKE ALL
            ON TABLE
                public.marketing_schema_migrations
            FROM PUBLIC
            """
        )


        # Supabase application roles.
        #
        # Use a role-existence guard so this runner remains
        # usable in PostgreSQL environments where one of these
        # roles does not exist.

        cur.execute(
            """
            DO $$
            DECLARE
                role_name TEXT;
            BEGIN
                FOREACH role_name IN ARRAY ARRAY[
                    'anon',
                    'authenticated',
                    'service_role'
                ]
                LOOP
                    IF EXISTS (
                        SELECT 1
                        FROM pg_roles
                        WHERE rolname = role_name
                    ) THEN
                        EXECUTE format(
                            'REVOKE ALL ON TABLE '
                            'public.marketing_schema_migrations '
                            'FROM %I',
                            role_name
                        );
                    END IF;
                END LOOP;
            END
            $$;
            """
        )


        cur.execute(
            """
            COMMENT ON TABLE
                public.marketing_schema_migrations
            IS
                'Internal DAUNTRA migration registry. '
                'Accessible only through privileged direct '
                'database administration.'
            """
        )


print()
print(
    "=========================================="
)
print(
    " DAUNTRA DATABASE MIGRATIONS"
)
print(
    "=========================================="
)
print()


try:

    conn = psycopg.connect(
        database_url,
        autocommit=True,
        sslmode="require",
        connect_timeout=15,
    )


except Exception as exc:

    print(
        "DATABASE CONNECTION: FAIL"
    )

    print()

    print(
        type(exc).__name__
        + ": "
        + str(exc)
    )

    print()

    print(
        "Check the Supabase connection string "
        "and network access to the PostgreSQL "
        "pooler."
    )

    raise SystemExit(1)


try:

    with conn.cursor() as cur:

        cur.execute(
            """
            SELECT
                current_database(),
                current_user
            """
        )

        db_name, db_user = (
            cur.fetchone()
        )


    print(
        "DATABASE CONNECTION: PASS"
    )

    print(
        f"Database: {db_name}"
    )

    print(
        f"Role:     {db_user}"
    )

    print()


    # --------------------------------------------------------
    # MIGRATION REGISTRY
    #
    # Created and secured before processing migration files.
    # --------------------------------------------------------

    ensure_migration_registry(
        conn
    )


    migration_files = sorted(
        MIGRATIONS_DIR.glob(
            "*.sql"
        )
    )


    if not migration_files:

        print(
            "ERROR: No migrations found."
        )

        raise SystemExit(1)


    # --------------------------------------------------------
    # APPLY MIGRATIONS
    # --------------------------------------------------------

    for path in migration_files:

        digest = checksum(
            path
        )


        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT sha256
                FROM public.marketing_schema_migrations
                WHERE filename = %s
                """,
                (
                    path.name,
                ),
            )

            row = (
                cur.fetchone()
            )


        if row:

            existing_checksum = (
                row[0]
            )


            if (
                existing_checksum
                != digest
            ):

                print(
                    f"ERROR   {path.name}"
                )

                print(
                    "        Migration was modified "
                    "after being applied."
                )

                print(
                    "        Never rewrite an "
                    "applied migration."
                )

                raise SystemExit(1)


            print(
                f"SKIP    {path.name} "
                "(already applied)"
            )

            continue


        print(
            f"APPLY   {path.name}"
        )


        sql = path.read_text(
            encoding="utf-8"
        )


        try:

            with conn.cursor() as cur:

                cur.execute(
                    sql
                )


            with conn.cursor() as cur:

                cur.execute(
                    """
                    INSERT INTO
                        public.marketing_schema_migrations (
                            filename,
                            sha256
                        )
                    VALUES (%s, %s)
                    """,
                    (
                        path.name,
                        digest,
                    ),
                )


            print(
                f"OK      {path.name}"
            )


        except Exception as exc:

            try:

                conn.rollback()

            except Exception:

                pass


            print()

            print(
                f"FAILED  {path.name}"
            )

            print(
                type(exc).__name__
                + ": "
                + str(exc)
            )

            raise SystemExit(1)


    print()

    print(
        "=========================================="
    )

    print(
        " MIGRATIONS COMPLETE"
    )

    print(
        "=========================================="
    )


finally:

    conn.close()
