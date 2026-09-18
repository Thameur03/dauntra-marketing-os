from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:

    sys.path.insert(
        0,
        str(ROOT),
    )


from app.db.research_store import (
    ResearchStore,
)

from contracts.subject import (
    SubjectCreate,
)


print()
print("==========================================")
print(" SUPABASE HTTPS WRITE CHECK")
print("==========================================")
print()


subject = SubjectCreate(

    subject=(
        "DAUNTRA HTTPS write "
        "smoke-test fixture"
    ),

    note=(
        "Synthetic fixture. "
        "Delete immediately."
    ),

    content_family="C02",
)


subject_id = None


try:

    with ResearchStore() as store:

        subject_id = (
            store.create_subject(
                subject
            )
        )


        print(
            "INSERT: PASS"
        )


        rows = store.db.select(

            "subjects",

            params={
                "select": (
                    "id,status"
                ),

                "id": (
                    f"eq.{subject_id}"
                ),
            },
        )


        assert len(rows) == 1

        assert (
            rows[0]["status"]
            == "RESEARCHING"
        )


        print(
            "READ:   PASS"
        )


        store.db.update(

            "subjects",

            filters={
                "id": subject_id,
            },

            values={
                "status": "READY",
            },
        )


        rows = store.db.select(

            "subjects",

            params={
                "select": (
                    "id,status"
                ),

                "id": (
                    f"eq.{subject_id}"
                ),
            },
        )


        assert (
            rows[0]["status"]
            == "READY"
        )


        print(
            "UPDATE: PASS"
        )


        store.delete_subject(
            subject_id
        )


        remaining = store.db.select(

            "subjects",

            params={
                "select": "id",

                "id": (
                    f"eq.{subject_id}"
                ),
            },
        )


        assert remaining == []


        print(
            "DELETE: PASS"
        )


    print()
    print(
        "HTTPS WRITE PIPELINE: PASS"
    )


except Exception as exc:

    print()
    print(
        "HTTPS WRITE PIPELINE: FAIL"
    )

    print(
        type(exc).__name__
        + ": "
        + str(exc)
    )


    if subject_id:

        try:

            with ResearchStore() as store:

                store.delete_subject(
                    subject_id
                )

        except Exception:

            pass


    raise SystemExit(1)
