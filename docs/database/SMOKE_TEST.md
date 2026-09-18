# Section 2C — Database Smoke Test

The database smoke test validates the real Supabase/PostgreSQL database,
not merely local Python structures.

Run:

    .venv/bin/python scripts/smoke_test_database.py

The test validates:

1. Pydantic subject contract
2. Pydantic research contract
3. Pydantic platform-content contract
4. Real PostgreSQL connection
5. Subject insertion
6. Research packet insertion
7. Content test insertion
8. Content item insertion
9. Complete lineage reconstruction
10. JSONB round-trip
11. PostgreSQL CHECK constraints
12. Foreign-key cascade deletion
13. Automatic fixture cleanup

The fixture is intentionally synthetic.

It must never become publishable content.

If the test fails before cleanup, the entire transaction rolls back.

If the test succeeds, the fixture subject is deleted before transaction commit.

Therefore the test leaves no Marketing OS fixture content in the database.
