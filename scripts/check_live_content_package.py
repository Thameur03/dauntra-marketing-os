from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:

    sys.path.insert(
        0,
        str(ROOT),
    )


from app.content_brain.package import (
    build_content_package,
)

from app.db.content_store import (
    ContentStore,
)

from app.db.supabase_rest import (
    SupabaseREST,
)

from app.llm.gemini import (
    GeminiProvider,
)

from contracts.common import (
    ContentFamily,
    Platform,
)

from contracts.content_package import (
    ContentItemEnvelope,
)

from contracts.research import (
    ResearchPacket,
)


RESEARCH_PACKET_ID = (
    "4d0fecb7-f733-4ddb-94ce-8d25a1acaee5"
)

VARIANT_KEY = (
    "section3c-live-validation-v1"
)


class NeverCallLLM:
    """
    Second-run idempotency probe.

    model_name deliberately matches the real Gemini model so the
    generation key is identical. Any generation attempt is an error.
    """

    def __init__(
        self,
        model_name: str,
    ) -> None:

        self._model_name = (
            model_name
        )


    @property
    def model_name(
        self,
    ) -> str:

        return self._model_name


    def generate_json(
        self,
        **kwargs,
    ):

        raise AssertionError(
            "IDEMPOTENCY FAILURE: "
            "LLM was called on the second build."
        )


    def generate_structured(
        self,
        **kwargs,
    ):

        raise AssertionError(
            "IDEMPOTENCY FAILURE: "
            "LLM was called on the second build."
        )


def main() -> int:

    print()
    print(
        "=========================================="
    )
    print(
        " SECTION 3C LIVE PACKAGE"
    )
    print(
        "=========================================="
    )
    print()


    with SupabaseREST() as db:

        rows = db.select(
            "research_packets",

            params={
                "select": (
                    "id,subject_id,status,packet_json"
                ),

                "id": (
                    "eq."
                    + RESEARCH_PACKET_ID
                ),
            },
        )


        if len(rows) != 1:

            print(
                "FAIL: expected exactly one "
                "ResearchPacket."
            )

            return 1


        row = rows[0]


        if row[
            "status"
        ] not in {
            "READY",
            "NEEDS_REVIEW",
        }:

            print(
                "FAIL: unusable ResearchPacket status:",
                row[
                    "status"
                ],
            )

            return 1


        packet = (
            ResearchPacket
            .model_validate(
                row[
                    "packet_json"
                ]
            )
        )


        subject_id = str(
            row[
                "subject_id"
            ]
        )


        store = ContentStore(
            db
        )


        real_llm = (
            GeminiProvider()
        )


        print(
            "Research packet:",
            RESEARCH_PACKET_ID,
        )

        print(
            "Subject:",
            subject_id,
        )

        print(
            "Platform: instagram"
        )

        print(
            "Family: C02"
        )

        print(
            "Variant:",
            VARIANT_KEY,
        )

        print(
            "Model:",
            real_llm.model_name,
        )

        print()


        print(
            "=========================================="
        )

        print(
            " FIRST BUILD"
        )

        print(
            "=========================================="
        )

        print()


        first = (
            build_content_package(

                subject_id=subject_id,

                research_packet_id=(
                    RESEARCH_PACKET_ID
                ),

                packet=packet,

                content_family=(
                    ContentFamily.C02
                ),

                platforms=[
                    Platform.INSTAGRAM
                ],

                llm=real_llm,

                store=store,

                variant_key=(
                    VARIANT_KEY
                ),
            )
        )


        first_item = (
            first.items[0]
        )


        print(
            "Package:",
            first.package_id,
        )

        print(
            "Build status:",
            first.build_status,
        )

        print(
            "Item status:",
            first_item.status,
        )

        print(
            "Content item:",
            (
                first_item.content_item_id
                or "(none)"
            ),
        )

        print(
            "DB status:",
            (
                first_item.database_status
                or "(none)"
            ),
        )

        print(
            "Human review:",
            first.requires_human_review,
        )

        print()


        if first_item.status not in {
            "NEEDS_HUMAN_REVIEW",
            "GENERATED",
            "REUSED",
        }:

            print(
                "FIRST BUILD: FAIL"
            )

            if first_item.error:

                print()
                print(
                    first_item.error
                )

            return 2


        if not first_item.content_item_id:

            print(
                "FAIL: successful first build "
                "has no content_item_id."
            )

            return 3


        content_item_id = (
            first_item
            .content_item_id
        )


        # ----------------------------------------------------
        # DATABASE READBACK
        # ----------------------------------------------------

        stored_rows = db.select(
            "content_items",

            params={
                "select": (
                    "id,subject_id,research_packet_id,"
                    "platform,format,content_family,"
                    "status,content_json,prompt_version,"
                    "model,capability_manifest_version,"
                    "brand_profile_version,"
                    "content_strategy_version"
                ),

                "id": (
                    "eq."
                    + content_item_id
                ),
            },
        )


        if len(
            stored_rows
        ) != 1:

            print(
                "FAIL: content_item readback "
                "did not return exactly one row."
            )

            return 4


        stored_row = (
            stored_rows[0]
        )


        envelope = (
            ContentItemEnvelope
            .model_validate(
                stored_row[
                    "content_json"
                ]
            )
        )


        if (
            stored_row[
                "subject_id"
            ]
            != subject_id
        ):

            print(
                "FAIL: subject_id mismatch."
            )

            return 5


        if (
            stored_row[
                "research_packet_id"
            ]
            != RESEARCH_PACKET_ID
        ):

            print(
                "FAIL: research_packet_id mismatch."
            )

            return 6


        if (
            stored_row[
                "platform"
            ]
            != "instagram"
        ):

            print(
                "FAIL: platform mismatch."
            )

            return 7


        if (
            stored_row[
                "status"
            ]
            != "NEEDS_HUMAN_REVIEW"
        ):

            print(
                "FAIL: expected "
                "NEEDS_HUMAN_REVIEW, got:",
                stored_row[
                    "status"
                ],
            )

            return 8


        if (
            envelope
            .generation_key
            != first_item
            .generation_key
        ):

            print(
                "FAIL: generation key mismatch."
            )

            return 9


        print(
            "DATABASE READBACK: PASS"
        )

        print(
            "Stored status:",
            stored_row[
                "status"
            ],
        )

        print(
            "Prompt version:",
            stored_row[
                "prompt_version"
            ],
        )

        print(
            "Model:",
            stored_row[
                "model"
            ],
        )

        print()


        # ----------------------------------------------------
        # SECOND BUILD
        #
        # NeverCallLLM proves the generation path is skipped.
        # ----------------------------------------------------

        print(
            "=========================================="
        )

        print(
            " SECOND BUILD — IDEMPOTENCY"
        )

        print(
            "=========================================="
        )

        print()


        second = (
            build_content_package(

                subject_id=subject_id,

                research_packet_id=(
                    RESEARCH_PACKET_ID
                ),

                packet=packet,

                content_family=(
                    ContentFamily.C02
                ),

                platforms=[
                    Platform.INSTAGRAM
                ],

                llm=NeverCallLLM(
                    real_llm.model_name
                ),

                store=store,

                variant_key=(
                    VARIANT_KEY
                ),
            )
        )


        second_item = (
            second.items[0]
        )


        print(
            "Package:",
            second.package_id,
        )

        print(
            "Build status:",
            second.build_status,
        )

        print(
            "Item status:",
            second_item.status,
        )

        print(
            "Content item:",
            second_item.content_item_id,
        )

        print()


        if (
            second_item.status
            != "REUSED"
        ):

            print(
                "FAIL: second build "
                "was not reused."
            )

            return 10


        if (
            second_item
            .content_item_id
            != content_item_id
        ):

            print(
                "FAIL: second build returned "
                "a different content_item."
            )

            return 11


        if (
            second.package_id
            != first.package_id
        ):

            print(
                "FAIL: package ID changed "
                "between identical builds."
            )

            return 12


        # ----------------------------------------------------
        # DUPLICATE ROW CHECK
        # ----------------------------------------------------

        sibling_rows = db.select(
            "content_items",

            params={
                "select": (
                    "id,status,content_json"
                ),

                "subject_id": (
                    "eq."
                    + subject_id
                ),

                "research_packet_id": (
                    "eq."
                    + RESEARCH_PACKET_ID
                ),

                "platform": (
                    "eq.instagram"
                ),

                "content_family": (
                    "eq.C02"
                ),

                "limit": "100",
            },
        )


        matching = []


        for candidate in sibling_rows:

            raw = candidate.get(
                "content_json"
            )


            if not isinstance(
                raw,
                dict,
            ):

                continue


            if (
                raw.get(
                    "generation_key"
                )
                == envelope
                .generation_key
            ):

                matching.append(
                    candidate
                )


        if len(
            matching
        ) != 1:

            print(
                "FAIL: expected exactly one "
                "row for generation key, found:",
                len(
                    matching
                ),
            )

            return 13


        print(
            "IDEMPOTENCY: PASS"
        )

        print(
            "Matching DB rows:",
            len(
                matching
            ),
        )

        print(
            "Additional Gemini calls "
            "during second build: 0"
        )

        print()


        # ----------------------------------------------------
        # FINAL CONTENT PREVIEW
        # ----------------------------------------------------

        content = (
            envelope.content
        )


        print(
            "=========================================="
        )

        print(
            " STORED CONTENT PREVIEW"
        )

        print(
            "=========================================="
        )

        print()


        if hasattr(
            content,
            "hook",
        ):

            print(
                "Hook:",
                content.hook,
            )

            print()


        if hasattr(
            content,
            "slides",
        ):

            for slide in (
                content.slides
            ):

                print(
                    f"[{slide.slide_number}]",
                    slide.headline
                    or "",
                )

                print(
                    slide.body
                )

                print()


        if hasattr(
            content,
            "caption",
        ):

            print(
                "Caption:"
            )

            print(
                content.caption
            )

            print()


        print(
            "Claims used:",
            len(
                content.claims_used
            ),
        )

        print(
            "Capabilities used:",
            content.capabilities_used,
        )

        print()


        print(
            "=========================================="
        )

        print(
            " SECTION 3C LIVE: PASS"
        )

        print(
            "=========================================="
        )

        print()

        print(
            "First build persisted one draft."
        )

        print(
            "Second identical build reused it."
        )

        print(
            "Publishing remains DISABLED."
        )


    return 0


if __name__ == "__main__":

    raise SystemExit(
        main()
    )
