from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:

    sys.path.insert(
        0,
        str(ROOT),
    )


from app.db.supabase_rest import (
    SupabaseREST,
)


print()
print("==========================================")
print(" SUPABASE HTTPS DATA API CHECK")
print("==========================================")
print()


try:

    with SupabaseREST() as db:

        rows = db.select(

            "subjects",

            params={
                "select": "id,status",
                "limit": "1",
            },
        )


    print(
        "HTTPS CONNECTION: PASS"
    )

    print(
        "DATA API AUTH: PASS"
    )

    print(
        "SUBJECTS TABLE: PASS"
    )

    print(
        f"Rows returned: {len(rows)}"
    )


except Exception as exc:

    print(
        "SUPABASE HTTPS CHECK: FAIL"
    )

    print()

    print(
        type(exc).__name__
        + ": "
        + str(exc)
    )

    raise SystemExit(1)
