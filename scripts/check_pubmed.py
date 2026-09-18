from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(ROOT),
    )


from app.retrieval.pubmed import (
    PubMedRetriever,
)


print()
print("==========================================")
print(" PUBMED RETRIEVAL CHECK")
print("==========================================")
print()


query = (
    '"resistance training"[Title/Abstract] '
    'AND hypertrophy[Title/Abstract]'
)


try:

    with PubMedRetriever() as retriever:

        print(
            "Rate mode: "
            + (
                "NCBI API key"
                if retriever.api_key
                else "NCBI no-key safe mode"
            )
        )

        print(
            "Minimum request interval: "
            f"{retriever.minimum_interval:.2f}s"
        )

        print()


        sources = retriever.search(

            [query],

            per_query=3,

            maximum_sources=3,
        )


except Exception as exc:

    print(
        "PUBMED RETRIEVAL: FAIL"
    )

    print(
        type(exc).__name__
        + ": "
        + str(exc)
    )

    raise SystemExit(1)


if not sources:

    print(
        "PUBMED RETRIEVAL: FAIL"
    )

    print(
        "No abstracts returned."
    )

    raise SystemExit(1)


print(
    "PUBMED RETRIEVAL: PASS"
)

print(
    f"SOURCES WITH ABSTRACTS: "
    f"{len(sources)}"
)

print()


for source in sources:

    print(
        "- "
        + source.title[:120]
    )
