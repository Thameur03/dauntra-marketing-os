from __future__ import annotations

import sys
from copy import deepcopy
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
    "section3c-db-replay-validation-v1"
)

MODEL_NAME = (
    "gemini-3.8-flash-replay-from-3b"
)


CLAIM_0 = (
    "Pooled meta-analytic evidence indicates no "
    "statistically significant difference in muscle "
    "hypertrophy between resistance training performed "
    "to momentary muscular failure and non-failure "
    "training in broad populations."
)

CLAIM_1 = (
    "In resistance-trained individuals, subgroup "
    "meta-analysis and single-set study data show a "
    "small or modest hypertrophic advantage when "
    "training to failure."
)

CLAIM_2 = (
    "An exploratory multilevel meta-regression found "
    "that muscle hypertrophy increased as sets were "
    "terminated closer to failure (lower estimated "
    "repetitions in reserve)."
)

CLAIM_3 = (
    "A randomized trial in trained individuals found "
    "similar quadriceps hypertrophy between sets taken "
    "to momentary failure and sets stopped at 1–2 "
    "repetitions in reserve, but failure caused greater "
    "repetition and velocity loss."
)


REPLAY_OUTPUT = {
    "hook": (
        "Do you actually need to hit muscular failure "
        "to maximize muscle growth?"
    ),

    "slides": [
        {
            "slide_number": 1,

            "headline": (
                "Do you need to hit failure?"
            ),

            "body": (
                "It is widely assumed that maximizing "
                "hypertrophy requires pushing every set "
                "until the weight cannot move. The evidence "
                "shows a more balanced trade-off between "
                "proximity to failure and acute fatigue."
            ),

            "emphasis": (
                "Proximity matters, but absolute failure "
                "comes with trade-offs."
            ),
        },

        {
            "slide_number": 2,

            "headline": (
                "What broad data shows"
            ),

            "body": (
                "When analyzing general populations, "
                "pooled meta-analytic evidence indicates "
                "no statistically significant difference "
                "in muscle hypertrophy between resistance "
                "training performed to momentary muscular "
                "failure and non-failure training."
            ),

            "emphasis": (
                "Taking every set to failure is not "
                "an absolute requirement."
            ),
        },

        {
            "slide_number": 3,

            "headline": (
                "Proximity to failure matters"
            ),

            "body": (
                "Stopping too far from failure reduces "
                "the stimulus. An exploratory multilevel "
                "meta-regression found that muscle "
                "hypertrophy increased as sets were "
                "terminated closer to failure (lower "
                "estimated repetitions in reserve)."
            ),

            "emphasis": (
                "Closer proximity to failure generally "
                "increases the growth stimulus."
            ),
        },

        {
            "slide_number": 4,

            "headline": (
                "Trained lifters and low volume"
            ),

            "body": (
                "Context shapes the outcome. In "
                "resistance-trained individuals, subgroup "
                "meta-analysis and single-set study data "
                "show a small or modest hypertrophic "
                "advantage when training to failure."
            ),

            "emphasis": (
                "Failure may offer small advantages in "
                "specific low-volume contexts."
            ),
        },

        {
            "slide_number": 5,

            "headline": (
                "The acute fatigue trade-off"
            ),

            "body": (
                "A randomized trial in trained individuals "
                "found similar quadriceps hypertrophy "
                "between sets taken to momentary failure "
                "and sets stopped at 1–2 repetitions in "
                "reserve, but failure caused greater "
                "repetition and velocity loss."
            ),

            "emphasis": (
                "Stopping 1–2 reps shy of failure achieved "
                "similar growth with less acute "
                "performance loss."
            ),
        },

        {
            "slide_number": 6,

            "headline": (
                "A practical takeaway"
            ),

            "body": (
                "Terminating most sets at 1–2 repetitions "
                "in reserve provides a strong hypertrophic "
                "stimulus while reducing acute velocity "
                "and repetition loss. Full failure can be "
                "applied selectively rather than as a "
                "baseline rule."
            ),

            "emphasis": (
                "Train hard enough to stimulate growth "
                "without unnecessary fatigue."
            ),
        },
    ],

    "caption": (
        "Does every set need to go to momentary failure?\n\n"

        "Pooled meta-analytic evidence indicates no "
        "statistically significant difference in muscle "
        "hypertrophy between training to failure and "
        "non-failure training across broad populations.\n\n"

        "At the same time, proximity to failure is a key "
        "driver of adaptation: exploratory meta-regression "
        "demonstrates that muscle growth increases as sets "
        "end closer to failure. In resistance-trained "
        "individuals, subgroup analyses and single-set "
        "research show a small or modest hypertrophic "
        "advantage when pushing all the way to failure.\n\n"

        "However, full failure carries acute costs. In "
        "trained individuals, sets taken to momentary "
        "failure produced similar quadriceps hypertrophy "
        "compared to leaving 1–2 repetitions in reserve, "
        "but failure resulted in greater repetition and "
        "velocity loss.\n\n"

        "A practical interpretation of this literature: "
        "keeping most sets within 1–2 repetitions in "
        "reserve captures the hypertrophy stimulus while "
        "managing acute fatigue."
    ),

    "cta": (
        "Save this for later."
    ),

    "claims_used": [
        CLAIM_0,
        CLAIM_2,
        CLAIM_1,
        CLAIM_3,
    ],

    "capabilities_used": [],
}


class ReplayLLM:

    def __init__(self):
        self.calls = 0


    @property
    def model_name(self) -> str:
        return MODEL_NAME


    def generate_json(
        self,
        *,
        prompt,
        schema,
        system_instruction=None,
    ):
        self.calls += 1

        if self.calls > 1:
            raise AssertionError(
                "ReplayLLM called more than once."
            )

        return deepcopy(
            REPLAY_OUTPUT
        )


    def generate_structured(
        self,
        **kwargs,
    ):
        raise AssertionError(
            "Replay validation must use generate_json."
        )


class NeverCallLLM:

    @property
    def model_name(self) -> str:
        return MODEL_NAME


    def generate_json(
        self,
        **kwargs,
    ):
        raise AssertionError(
            "IDEMPOTENCY FAILURE: writer was called "
            "during second package build."
        )


    def generate_structured(
        self,
        **kwargs,
    ):
        raise AssertionError(
            "IDEMPOTENCY FAILURE: model was called."
        )


def main() -> int:

    print()
    print(
        "=========================================="
    )
    print(
        " SECTION 3C — DB REPLAY VALIDATION"
    )
    print(
        "=========================================="
    )
    print()

    print(
        "Gemini network calls: 0"
    )

    print(
        "Replay source: previously validated "
        "3B Gemini output"
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
                "FAIL: ResearchPacket not found."
            )
            return 1


        row = rows[0]

        packet = (
            ResearchPacket.model_validate(
                row["packet_json"]
            )
        )

        subject_id = str(
            row["subject_id"]
        )

        store = ContentStore(
            db
        )


        # ====================================================
        # FIRST BUILD
        # ====================================================

        print(
            "=========================================="
        )
        print(
            " FIRST BUILD — VALIDATE + PERSIST"
        )
        print(
            "=========================================="
        )
        print()


        replay_llm = ReplayLLM()


        first = build_content_package(

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

            llm=replay_llm,

            store=store,

            variant_key=(
                VARIANT_KEY
            ),
        )


        first_item = first.items[0]


        print(
            "Package ID:",
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
            "DB status:",
            first_item.database_status,
        )

        print(
            "Content item ID:",
            first_item.content_item_id,
        )

        print(
            "Replay writer calls:",
            replay_llm.calls,
        )

        print()


        if first_item.status == "REUSED":

            print(
                "Existing replay validation row found."
            )

            print(
                "This is valid for an idempotent rerun."
            )


        elif first_item.status not in {
            "NEEDS_HUMAN_REVIEW",
            "GENERATED",
        }:

            print(
                "FAIL: first build did not persist/reuse."
            )

            if first_item.error:
                print(
                    first_item.error
                )

            return 2


        if not first_item.content_item_id:
            print(
                "FAIL: no content_item_id."
            )
            return 3


        content_item_id = (
            first_item.content_item_id
        )


        # ====================================================
        # READBACK
        # ====================================================

        stored_rows = db.select(
            "content_items",

            params={
                "select": (
                    "id,subject_id,research_packet_id,"
                    "platform,format,content_family,status,"
                    "content_json,prompt_version,model,"
                    "capability_manifest_version,"
                    "brand_profile_version,"
                    "content_strategy_version"
                ),

                "id": (
                    "eq."
                    + content_item_id
                ),
            },
        )


        if len(stored_rows) != 1:
            print(
                "FAIL: expected one DB row."
            )
            return 4


        stored = stored_rows[0]


        envelope = (
            ContentItemEnvelope.model_validate(
                stored["content_json"]
            )
        )


        checks = {
            "subject": (
                stored["subject_id"]
                == subject_id
            ),

            "research": (
                stored["research_packet_id"]
                == RESEARCH_PACKET_ID
            ),

            "platform": (
                stored["platform"]
                == "instagram"
            ),

            "family": (
                stored["content_family"]
                == "C02"
            ),

            "status": (
                stored["status"]
                == "NEEDS_HUMAN_REVIEW"
            ),

            "generation_key": (
                envelope.generation_key
                == first_item.generation_key
            ),
        }


        for name, passed in checks.items():

            print(
                f"Readback {name}:",
                (
                    "PASS"
                    if passed
                    else "FAIL"
                ),
            )


        if not all(
            checks.values()
        ):
            return 5


        print()
        print(
            "DATABASE READBACK: PASS"
        )
        print()


        # ====================================================
        # SECOND BUILD
        #
        # Must reuse DB row.
        # NeverCallLLM makes accidental regeneration fatal.
        # ====================================================

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


        second = build_content_package(

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

            llm=NeverCallLLM(),

            store=store,

            variant_key=(
                VARIANT_KEY
            ),
        )


        second_item = second.items[0]


        print(
            "Build status:",
            second.build_status,
        )

        print(
            "Item status:",
            second_item.status,
        )

        print(
            "Content item ID:",
            second_item.content_item_id,
        )

        print()


        if second_item.status != "REUSED":
            print(
                "FAIL: second build was not reused."
            )
            return 6


        if (
            second_item.content_item_id
            != content_item_id
        ):
            print(
                "FAIL: reused a different row."
            )
            return 7


        if (
            second.package_id
            != first.package_id
        ):
            print(
                "FAIL: deterministic package ID changed."
            )
            return 8


        # ====================================================
        # DUPLICATE CHECK
        # ====================================================

        candidates = db.select(
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


        same_generation = []


        for candidate in candidates:

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
                == envelope.generation_key
            ):
                same_generation.append(
                    candidate
                )


        print(
            "Matching generation-key rows:",
            len(
                same_generation
            ),
        )


        if len(
            same_generation
        ) != 1:

            print(
                "FAIL: duplicate generation rows found."
            )
            return 9


        print()
        print(
            "IDEMPOTENCY: PASS"
        )

        print(
            "Additional model calls: 0"
        )

        print()


        # ====================================================
        # CONTENT PREVIEW
        # ====================================================

        content = envelope.content


        print(
            "=========================================="
        )
        print(
            " STORED DRAFT"
        )
        print(
            "=========================================="
        )
        print()


        print(
            "Hook:",
            content.hook,
        )

        print()


        for slide in content.slides:

            print(
                f"[{slide.slide_number}] "
                f"{slide.headline or ''}"
            )

            print(
                slide.body
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

        print(
            "Human review:",
            envelope.requires_human_review,
        )

        print()


        print(
            "=========================================="
        )
        print(
            " SECTION 3C DB VALIDATION: PASS"
        )
        print(
            "=========================================="
        )
        print()

        print(
            "Gemini network calls: 0"
        )

        print(
            "Publishing: DISABLED"
        )


    return 0


if __name__ == "__main__":

    raise SystemExit(
        main()
    )
