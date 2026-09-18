from __future__ import annotations

import os
import sys
from pathlib import Path

# Allow scripts executed directly from ./scripts to import project packages.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import psycopg
from psycopg.errors import CheckViolation
from psycopg.types.json import Jsonb
from dotenv import load_dotenv

from contracts.content import InstagramCarouselContent
from contracts.research import ResearchPacket
from contracts.subject import SubjectCreate


ROOT = Path(__file__).resolve().parents[1]

load_dotenv(ROOT / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("ERROR: DATABASE_URL is missing from .env")
    sys.exit(1)


print()
print("==========================================")
print(" DAUNTRA SECTION 2C DATABASE SMOKE TEST")
print("==========================================")
print()


# ============================================================
# 1. VALIDATE FIXTURES THROUGH PYDANTIC FIRST
# ============================================================

subject_contract = SubjectCreate(
    subject="Does protein timing matter for hypertrophy?",
    note="Section 2C database smoke-test fixture.",
    content_family="C02",
)


research_contract = ResearchPacket(
    subject=subject_contract.subject,

    summary=(
        "Protein timing should be discussed alongside total daily "
        "protein intake, meal distribution, and the user's training context."
    ),

    core_finding=(
        "Total daily protein intake remains a major consideration, "
        "while distribution and timing can matter in context."
    ),

    important_nuance=(
        "The useful conclusion is not that timing never matters."
    ),

    dauntra_relevance=(
        "This is relevant to educational nutrition content for resistance trainees."
    ),

    sources=[
        {
            "title": "Section 2C Fixture Source",
            "url": "https://example.com/research-fixture",
            "publisher": "Fixture Publisher",
            "source_type": "study",
            "notes": (
                "Synthetic source used only to validate database structure. "
                "It is not intended for publication."
            ),
        }
    ],

    claims=[
        {
            "claim": "Total daily protein intake is an important variable.",
            "sensitivity": "nutrition",
            "source_indexes": [0],
            "confidence": "high",
            "human_review_required": True,
        }
    ],

    recommended_angles=[
        "What matters more than obsessing over a perfect anabolic window?"
    ],

    prohibited_angles=[
        "Protein timing never matters."
    ],

    requires_human_review=True,
)


content_contract = InstagramCarouselContent(
    content_family="C02",

    hook="You're probably overthinking protein timing.",

    slides=[
        {
            "slide_number": 1,
            "headline": "Protein timing",
            "body": (
                "The useful answer is more nuanced than chasing "
                "a magic post-workout window."
            ),
        },
        {
            "slide_number": 2,
            "headline": "Start with the bigger picture",
            "body": (
                "Total daily intake and how protein is distributed "
                "across the day both deserve attention."
            ),
        },
    ],

    caption=(
        "A synthetic fixture used only to verify the DAUNTRA "
        "Marketing OS database."
    ),

    cta="Save this for later.",

    claims_used=[
        "Total daily protein intake is an important variable."
    ],

    capabilities_used=[],
)


print("OK      Subject contract validated")
print("OK      Research contract validated")
print("OK      Content contract validated")
print()


# ============================================================
# 2. CONNECT TO REAL SUPABASE
# ============================================================

try:
    conn = psycopg.connect(
        DATABASE_URL,
        sslmode="require",
        connect_timeout=15,
    )
except Exception as exc:
    print("DATABASE CONNECTION: FAIL")
    print(type(exc).__name__ + ":", exc)
    sys.exit(1)


print("OK      Connected to Supabase PostgreSQL")
print()


try:

    # Everything happens in ONE transaction.
    #
    # If anything fails:
    #     PostgreSQL rolls the test back.
    #
    # If everything succeeds:
    #     the test deletes its own fixture data before commit.

    with conn.transaction():

        # ====================================================
        # 3. SUBJECT
        # ====================================================

        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO subjects (
                    subject_text,
                    note,
                    source,
                    content_family,
                    market,
                    language,
                    status
                )
                VALUES (
                    %s,
                    %s,
                    'founder',
                    %s,
                    %s,
                    %s,
                    'QUEUED'
                )
                RETURNING id
                """,
                (
                    subject_contract.subject,
                    subject_contract.note,
                    subject_contract.content_family.value,
                    subject_contract.market.value,
                    subject_contract.language.value,
                ),
            )

            subject_id = cur.fetchone()[0]

        print(f"OK      subject inserted")
        print(f"        {subject_id}")


        # ====================================================
        # 4. RESEARCH PACKET
        # ====================================================

        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO research_packets (
                    subject_id,
                    status,
                    packet_json,
                    prompt_version,
                    model
                )
                VALUES (
                    %s,
                    'READY',
                    %s,
                    %s,
                    %s
                )
                RETURNING id
                """,
                (
                    subject_id,
                    Jsonb(
                        research_contract.model_dump(
                            mode="json"
                        )
                    ),
                    "fixture-research-v1",
                    "fixture-model",
                ),
            )

            research_packet_id = cur.fetchone()[0]

        print(f"OK      research packet inserted")
        print(f"        {research_packet_id}")


        # ====================================================
        # 5. CONTENT TEST
        # ====================================================

        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO content_tests (
                    subject_id,
                    research_packet_id,
                    hypothesis,
                    independent_variable,
                    primary_metric,
                    observation_window_hours,
                    minimum_impressions,
                    minimum_clicks,
                    status
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    'qualified_signups_per_1000_impressions',
                    72,
                    1000,
                    10,
                    'ACTIVE'
                )
                RETURNING id
                """,
                (
                    subject_id,
                    research_packet_id,
                    (
                        "A practical protein-timing hook may earn "
                        "qualified attention from resistance trainees."
                    ),
                    "hook framing",
                ),
            )

            content_test_id = cur.fetchone()[0]

        print(f"OK      content test inserted")
        print(f"        {content_test_id}")


        # ====================================================
        # 6. CONTENT ITEM
        # ====================================================

        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO content_items (
                    subject_id,
                    research_packet_id,
                    content_test_id,
                    platform,
                    format,
                    content_family,
                    market,
                    language,
                    status,
                    content_json,
                    prompt_version,
                    model,
                    capability_manifest_version,
                    brand_profile_version,
                    content_strategy_version
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    'instagram',
                    'carousel',
                    'C02',
                    'GLOBAL',
                    'en',
                    'GENERATED',
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                RETURNING id
                """,
                (
                    subject_id,
                    research_packet_id,
                    content_test_id,

                    Jsonb(
                        content_contract.model_dump(
                            mode="json"
                        )
                    ),

                    "fixture-instagram-v1",
                    "fixture-model",
                    "2",
                    "2",
                    "2",
                ),
            )

            content_item_id = cur.fetchone()[0]

        print(f"OK      content item inserted")
        print(f"        {content_item_id}")

        print()


        # ====================================================
        # 7. READ FULL LINEAGE BACK
        # ====================================================

        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    s.subject_text,
                    r.status,
                    r.packet_json ->> 'core_finding',
                    ct.primary_metric,
                    ct.independent_variable,
                    ci.platform,
                    ci.format,
                    ci.status,
                    ci.content_json ->> 'hook'
                FROM subjects s

                JOIN research_packets r
                  ON r.subject_id = s.id

                JOIN content_tests ct
                  ON ct.subject_id = s.id
                 AND ct.research_packet_id = r.id

                JOIN content_items ci
                  ON ci.subject_id = s.id
                 AND ci.research_packet_id = r.id
                 AND ci.content_test_id = ct.id

                WHERE s.id = %s
                  AND r.id = %s
                  AND ct.id = %s
                  AND ci.id = %s
                """,
                (
                    subject_id,
                    research_packet_id,
                    content_test_id,
                    content_item_id,
                ),
            )

            lineage = cur.fetchone()

        if not lineage:
            raise RuntimeError(
                "Could not reconstruct full content lineage."
            )

        (
            stored_subject,
            research_status,
            stored_core_finding,
            primary_metric,
            independent_variable,
            platform,
            content_format,
            content_status,
            stored_hook,
        ) = lineage


        assert stored_subject == subject_contract.subject
        assert research_status == "READY"

        assert (
            stored_core_finding
            == research_contract.core_finding
        )

        assert (
            primary_metric
            == "qualified_signups_per_1000_impressions"
        )

        assert independent_variable == "hook framing"

        assert platform == "instagram"
        assert content_format == "carousel"
        assert content_status == "GENERATED"

        assert stored_hook == content_contract.hook


        print("==========================================")
        print(" LINEAGE READBACK")
        print("==========================================")
        print()

        print("Subject:")
        print(f"  {stored_subject}")
        print()

        print("Research status:")
        print(f"  {research_status}")
        print()

        print("Primary metric:")
        print(f"  {primary_metric}")
        print()

        print("Independent variable:")
        print(f"  {independent_variable}")
        print()

        print("Content:")
        print(f"  {platform} / {content_format}")
        print()

        print("Hook:")
        print(f"  {stored_hook}")
        print()

        print("OK      Full lineage reconstructed")
        print("OK      Research JSON round-trip")
        print("OK      Content JSON round-trip")
        print()


        # ====================================================
        # 8. VERIFY SQL CONSTRAINTS REALLY WORK
        # ====================================================

        with conn.cursor() as cur:

            cur.execute("SAVEPOINT invalid_platform_test")

            try:

                cur.execute(
                    """
                    INSERT INTO content_items (
                        subject_id,
                        research_packet_id,
                        content_test_id,
                        platform,
                        format,
                        content_family,
                        market,
                        language,
                        status,
                        content_json,
                        prompt_version,
                        model,
                        capability_manifest_version,
                        brand_profile_version,
                        content_strategy_version
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        'youtube',
                        'video',
                        'C02',
                        'GLOBAL',
                        'en',
                        'GENERATED',
                        '{}'::jsonb,
                        'fixture',
                        'fixture',
                        '2',
                        '2',
                        '2'
                    )
                    """,
                    (
                        subject_id,
                        research_packet_id,
                        content_test_id,
                    ),
                )

            except CheckViolation:

                cur.execute(
                    "ROLLBACK TO SAVEPOINT invalid_platform_test"
                )

                print(
                    "OK      PostgreSQL rejected unsupported platform"
                )

            else:

                cur.execute(
                    "ROLLBACK TO SAVEPOINT invalid_platform_test"
                )

                raise RuntimeError(
                    "Database accepted unsupported platform 'youtube'."
                )

        print()


        # ====================================================
        # 9. TEST CASCADE DELETE
        # ====================================================

        with conn.cursor() as cur:

            cur.execute(
                """
                DELETE FROM subjects
                WHERE id = %s
                """,
                (subject_id,),
            )


        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT COUNT(*)
                FROM research_packets
                WHERE id = %s
                """,
                (research_packet_id,),
            )

            remaining_research = cur.fetchone()[0]


            cur.execute(
                """
                SELECT COUNT(*)
                FROM content_tests
                WHERE id = %s
                """,
                (content_test_id,),
            )

            remaining_tests = cur.fetchone()[0]


            cur.execute(
                """
                SELECT COUNT(*)
                FROM content_items
                WHERE id = %s
                """,
                (content_item_id,),
            )

            remaining_content = cur.fetchone()[0]


        assert remaining_research == 0
        assert remaining_tests == 0
        assert remaining_content == 0


        print("OK      Subject deleted")
        print("OK      Research packet cascade deleted")
        print("OK      Content test cascade deleted")
        print("OK      Content item cascade deleted")
        print()

        print("OK      Smoke-test fixture cleaned up")


    # transaction committed here
    # but test rows were already deleted.

    print()
    print("==========================================")
    print(" SECTION 2C: PASS")
    print("==========================================")
    print()
    print("Real PostgreSQL lineage is working.")
    print("No smoke-test records were left behind.")
    print()


except Exception as exc:

    print()
    print("==========================================")
    print(" SECTION 2C: FAIL")
    print("==========================================")
    print()
    print(type(exc).__name__ + ":", exc)
    print()
    print(
        "The transaction was rolled back, so partial fixture "
        "records should not remain in the database."
    )

    sys.exit(1)


finally:
    conn.close()
