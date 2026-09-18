from __future__ import annotations

import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from dotenv import load_dotenv

from app.db.research_store import ResearchStore
from app.retrieval.pubmed import PubMedRetriever
from app.retrieval.query_builder import build_pubmed_queries
from contracts.research import ResearchPacket
from contracts.subject import SubjectCreate


load_dotenv(ROOT / ".env")


print()
print("==========================================")
print(" SECTION 3A FINAL ZERO-COST PREFLIGHT")
print("==========================================")
print()


# ============================================================
# 1. ENVIRONMENT
# ============================================================

model = os.getenv(
    "GEMINI_MODEL",
    "",
).strip()

print("1. Runtime configuration")
print("------------------------")
print("Gemini model:", model or "MISSING")

MODEL_STATUS = (
    0
    if model == "gemini-3.8-flash"
    else 1
)

print(
    "Model config:",
    "PASS" if MODEL_STATUS == 0 else "FAIL",
)

print()


# ============================================================
# 2. COMPLETE DATABASE PERSISTENCE TEST
# ============================================================

print("2. Complete research-packet persistence")
print("---------------------------------------")

subject_id = None
packet_id = None
DB_STATUS = 1


subject = SubjectCreate(
    subject=(
        "DAUNTRA Section 3A complete "
        "persistence fixture"
    ),
    note=(
        "Synthetic fixture. "
        "Must be deleted immediately."
    ),
    content_family="C02",
)


packet = ResearchPacket(
    subject=subject.subject,

    evidence_status="sufficient",

    summary=(
        "Synthetic packet used only to test "
        "database persistence."
    ),

    core_finding=(
        "HTTPS research packet persistence "
        "is under test."
    ),

    important_nuance=(
        "This is not scientific evidence."
    ),

    limitations=[
        "Synthetic fixture only."
    ],

    dauntra_relevance=(
        "Infrastructure validation only."
    ),

    sources=[
        {
            "title": "Synthetic fixture source",

            "url": (
                "https://example.com/"
                "dauntra-section3a-fixture"
            ),

            "publisher": (
                "DAUNTRA infrastructure test"
            ),

            "source_type": "other",

            "notes": (
                "Synthetic source; "
                "not scientific evidence."
            ),
        }
    ],

    claims=[
        {
            "claim": (
                "This is a synthetic "
                "persistence test."
            ),

            "sensitivity": "general",

            "source_indexes": [0],

            "confidence": "high",

            "human_review_required": False,
        }
    ],

    recommended_angles=[
        "Do not publish this fixture."
    ],

    prohibited_angles=[
        "Any public use."
    ],

    requires_human_review=False,
)


try:
    with ResearchStore() as store:

        subject_id = store.create_subject(
            subject
        )

        print("Subject insert: PASS")


        packet_id = store.save_packet(
            subject_id=subject_id,
            packet=packet,
            model="fixture-model",
        )

        print("Packet insert:  PASS")
        print("Subject update: PASS")


        subjects = store.db.select(
            "subjects",
            params={
                "select": "id,status",
                "id": f"eq.{subject_id}",
            },
        )


        packets = store.db.select(
            "research_packets",
            params={
                "select": (
                    "id,status,model,"
                    "prompt_version"
                ),
                "id": f"eq.{packet_id}",
            },
        )


        assert len(subjects) == 1
        assert subjects[0]["status"] == "READY"

        assert len(packets) == 1
        assert packets[0]["id"] == packet_id
        assert packets[0]["model"] == "fixture-model"

        print("Readback:       PASS")


        store.delete_subject(
            subject_id
        )


        remaining_subjects = store.db.select(
            "subjects",
            params={
                "select": "id",
                "id": f"eq.{subject_id}",
            },
        )


        remaining_packets = store.db.select(
            "research_packets",
            params={
                "select": "id",
                "id": f"eq.{packet_id}",
            },
        )


        assert remaining_subjects == []
        assert remaining_packets == []

        print("Delete subject: PASS")
        print("Cascade packet: PASS")

        DB_STATUS = 0


except Exception as exc:

    print()
    print("DATABASE PREFLIGHT: FAIL")
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


if DB_STATUS == 0:
    print("DATABASE PREFLIGHT: PASS")

print()


# ============================================================
# 3. ACTUAL PUBMED PREVIEW
# ============================================================

print("3. Actual PubMed evidence preview")
print("---------------------------------")

PUBMED_STATUS = 1


research_subject = (
    "Does training to muscular failure "
    "produce more muscle hypertrophy than "
    "stopping a few reps before failure?"
)


try:
    queries = build_pubmed_queries(
        research_subject
    )

    print()
    print("Queries:")

    for query in queries:
        print(" -", query)


    print()


    with PubMedRetriever() as retriever:

        sources = retriever.search(
            queries,
            per_query=6,
            maximum_sources=12,
        )


    print(
        "Usable abstracts:",
        len(sources),
    )

    print()


    for index, source in enumerate(
        sources
    ):

        print(
            f"[{index}] "
            f"{source.title[:160]}"
        )


    if len(sources) >= 2:

        PUBMED_STATUS = 0

        print()
        print("PUBMED PREFLIGHT: PASS")

    else:

        print()
        print(
            "PUBMED PREFLIGHT: FAIL"
        )


except Exception as exc:

    print()
    print("PUBMED PREFLIGHT: FAIL")

    print(
        type(exc).__name__
        + ": "
        + str(exc)
    )


print()
print("==========================================")
print(" PREFLIGHT SUMMARY")
print("==========================================")
print()

print(
    "Model config:       ",
    MODEL_STATUS,
)

print(
    "Full DB persistence:",
    DB_STATUS,
)

print(
    "PubMed evidence:    ",
    PUBMED_STATUS,
)

print()
print("Gemini calls made: 0")


if (
    MODEL_STATUS == 0
    and DB_STATUS == 0
    and PUBMED_STATUS == 0
):

    print()
    print(
        "SECTION 3A READY FOR ONE LIVE CALL"
    )

    raise SystemExit(0)


print()
print(
    "DO NOT RUN GEMINI YET."
)

raise SystemExit(1)
