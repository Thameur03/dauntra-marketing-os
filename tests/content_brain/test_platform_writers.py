from __future__ import annotations

from copy import deepcopy
from typing import Any

import pytest

from app.content_brain.validators import (
    validate_content_grounding,
)

from app.content_brain.writers import (
    facebook_writer,
    instagram_writer,
    tiktok_writer,
    x_writer,
)

from app.product_truth import (
    capability_marketing_context,
)

from contracts.common import (
    ContentFamily,
)

from contracts.content import (
    XContent,
)

from contracts.research import (
    ResearchPacket,
)


CLAIM_1 = (
    "Training close to failure can produce "
    "substantial hypertrophy without requiring "
    "every set to reach momentary muscular failure."
)


CLAIM_2 = (
    "Training to failure can produce greater "
    "acute fatigue than stopping with repetitions "
    "in reserve."
)


def packet() -> ResearchPacket:

    return ResearchPacket(
        subject=(
            "Training to failure versus "
            "repetitions in reserve"
        ),

        evidence_status="conflicting",

        summary=(
            "Evidence suggests proximity to failure "
            "matters, while complete failure is not "
            "required in every set."
        ),

        core_finding=(
            "Training close to failure is generally "
            "a useful hypertrophy strategy."
        ),

        important_nuance=(
            "Exact effects vary by protocol, "
            "training status, and volume."
        ),

        limitations=[
            (
                "Failure definitions differ "
                "between studies."
            ),
        ],

        dauntra_relevance=(
            "Useful training education."
        ),

        sources=[
            {
                "title": (
                    "Failure versus non-failure "
                    "resistance training"
                ),

                "url": (
                    "https://pubmed.ncbi.nlm.nih.gov/"
                    "33497853/"
                ),

                "publisher": "Fixture",

                "source_type": (
                    "systematic_review"
                ),

                "notes": (
                    "Fixture source used for tests."
                ),
            },

            {
                "title": (
                    "Proximity to failure "
                    "and hypertrophy"
                ),

                "url": (
                    "https://pubmed.ncbi.nlm.nih.gov/"
                    "36334240/"
                ),

                "publisher": "Fixture",

                "source_type": (
                    "meta_analysis"
                ),

                "notes": (
                    "Fixture source used for tests."
                ),
            },
        ],

        claims=[
            {
                "claim": CLAIM_1,
                "sensitivity": "training",
                "source_indexes": [0, 1],
                "confidence": "high",
                "human_review_required": True,
            },

            {
                "claim": CLAIM_2,
                "sensitivity": "training",
                "source_indexes": [0],
                "confidence": "medium",
                "human_review_required": True,
            },
        ],

        recommended_angles=[
            (
                "Explain proximity to failure "
                "without absolutism."
            ),
        ],

        prohibited_angles=[
            (
                "Claim failure is mandatory "
                "for muscle growth."
            ),
        ],

        requires_human_review=True,
    )


class FakeLLM:

    def __init__(
        self,
        output: dict[str, Any],
    ) -> None:

        self.output = output

        self.calls: list[
            dict[str, Any]
        ] = []


    @property
    def model_name(self) -> str:

        return "fake-test-model"


    def generate_json(
        self,
        *,
        prompt: str,
        schema: dict[str, Any],
        system_instruction: str | None = None,
    ) -> dict[str, Any]:

        self.calls.append(
            {
                "prompt": prompt,
                "schema": schema,
                "system_instruction": (
                    system_instruction
                ),
            }
        )

        return deepcopy(
            self.output
        )


    def generate_structured(
        self,
        *,
        prompt,
        response_model,
        system_instruction=None,
    ):

        raise AssertionError(
            "Platform writers should use "
            "generate_json wire schemas."
        )


def test_instagram_writer():

    llm = FakeLLM(
        {
            "hook": (
                "You probably don't need "
                "every set to fail."
            ),

            "slides": [
                {
                    "slide_number": 1,
                    "headline": (
                        "Failure isn't the target"
                    ),
                    "body": (
                        "Proximity to failure matters "
                        "more than forcing every set "
                        "to absolute failure."
                    ),
                    "emphasis": (
                        "Close can be enough."
                    ),
                },

                {
                    "slide_number": 2,
                    "headline": (
                        "Fatigue still matters"
                    ),
                    "body": (
                        "Failure can add fatigue, "
                        "which affects later work."
                    ),
                    "emphasis": "",
                },
            ],

            "caption": (
                "The useful question is not simply "
                "failure vs no failure. It is how "
                "close your hard sets finish."
            ),

            "cta": (
                "Save this for later."
            ),

            "claims_used": [
                CLAIM_1,
                CLAIM_2,
            ],

            "capabilities_used": [],
        }
    )


    result = instagram_writer(
        llm
    ).write(
        packet=packet(),
        content_family=(
            ContentFamily.C02
        ),
    )


    assert (
        result.platform.value
        == "instagram"
    )

    assert len(
        result.slides
    ) == 2

    assert (
        result.slides[1].emphasis
        is None
    )

    assert len(
        llm.calls
    ) == 1

    assert (
        "Instagram"
        in llm.calls[0][
            "system_instruction"
        ]
        or "carousel"
        in llm.calls[0][
            "system_instruction"
        ].lower()
    )


def test_tiktok_writer():

    llm = FakeLLM(
        {
            "hook": (
                "Stop treating failure "
                "like a requirement."
            ),

            "chunks": [
                {
                    "text": (
                        "Training close to failure "
                        "can already be a strong "
                        "hypertrophy stimulus."
                    ),
                    "duration_ms": 3500,
                },

                {
                    "text": (
                        "Going all the way to failure "
                        "can also create more fatigue."
                    ),
                    "duration_ms": 3500,
                },
            ],

            "caption": (
                "Failure is a tool, "
                "not a universal rule."
            ),

            "cta": "",

            "claims_used": [
                CLAIM_1,
                CLAIM_2,
            ],

            "capabilities_used": [],
        }
    )


    result = tiktok_writer(
        llm
    ).write(
        packet=packet(),
        content_family=(
            ContentFamily.C02
        ),
    )


    assert (
        result.platform.value
        == "tiktok"
    )

    assert (
        result.cta
        is None
    )


def test_x_writer():

    llm = FakeLLM(
        {
            "format": "thread",

            "posts": [
                (
                    "Training to failure isn't "
                    "automatically better for growth."
                ),

                (
                    "Getting close to failure can be "
                    "effective while avoiding some "
                    "of the extra fatigue."
                ),
            ],

            "cta": "",

            "claims_used": [
                CLAIM_1,
                CLAIM_2,
            ],

            "capabilities_used": [],
        }
    )


    result = x_writer(
        llm
    ).write(
        packet=packet(),
        content_family=(
            ContentFamily.C02
        ),
    )


    assert (
        result.format
        == "thread"
    )

    assert len(
        result.posts
    ) == 2


def test_facebook_writer():

    llm = FakeLLM(
        {
            "format": "text",

            "body": (
                "Training to failure can be useful, "
                "but current evidence does not make "
                "it a requirement for every hard set. "
                "Stopping close to failure can still "
                "provide a strong hypertrophy stimulus."
            ),

            "cta": (
                "Follow DAUNTRA for more."
            ),

            "claims_used": [
                CLAIM_1,
            ],

            "capabilities_used": [],
        }
    )


    result = facebook_writer(
        llm
    ).write(
        packet=packet(),
        content_family=(
            ContentFamily.C02
        ),
    )


    assert (
        result.platform.value
        == "facebook"
    )


def test_unknown_claim_is_rejected():

    llm = FakeLLM(
        {
            "format": "text",

            "posts": [
                "A test post."
            ],

            "cta": "",

            "claims_used": [
                (
                    "Invented scientific claim "
                    "not present in packet."
                ),
            ],

            "capabilities_used": [],
        }
    )


    with pytest.raises(
        ValueError,
        match="not present verbatim",
    ):

        x_writer(
            llm
        ).write(
            packet=packet(),
            content_family=(
                ContentFamily.C02
            ),
        )


def test_c04_requires_selected_capability():

    llm = FakeLLM(
        {}
    )


    with pytest.raises(
        ValueError,
        match="C04 requires",
    ):

        instagram_writer(
            llm
        ).write(
            packet=packet(),
            content_family=(
                ContentFamily.C04
            ),
        )


def test_blocked_capability_rejected():

    llm = FakeLLM(
        {}
    )


    with pytest.raises(
        ValueError,
        match="not approved",
    ):

        instagram_writer(
            llm
        ).write(
            packet=packet(),
            content_family=(
                ContentFamily.C04
            ),
            capability_ids=[
                "ai_coach",
            ],
        )


def test_allowed_capability_context_is_safe():

    context = (
        capability_marketing_context(
            "workout_logging"
        )
    )


    assert (
        context.capability_id
        == "workout_logging"
    )

    assert (
        context.display_name
    )


def test_writer_cannot_use_unsupplied_capability():

    content = XContent(
        format="text",

        content_family=(
            ContentFamily.C04
        ),

        posts=[
            (
                "DAUNTRA can help structure "
                "workout logging."
            )
        ],

        claims_used=[],

        capabilities_used=[
            "workout_logging",
        ],
    )


    with pytest.raises(
        ValueError,
        match="not explicitly supplied",
    ):

        validate_content_grounding(
            content=content,
            packet=packet(),
            requested_capabilities=[],
        )


def test_x_text_requires_one_post():

    content = XContent(
        format="text",

        content_family=(
            ContentFamily.C02
        ),

        posts=[
            "Post one.",
            "Post two.",
        ],

        claims_used=[
            CLAIM_1,
        ],

        capabilities_used=[],
    )


    with pytest.raises(
        ValueError,
        match="exactly one",
    ):

        validate_content_grounding(
            content=content,
            packet=packet(),
            requested_capabilities=[],
        )


def test_rejected_writer_preserves_candidate():

    from app.content_brain.writers import (
        GeneratedContentValidationError,
    )


    llm = FakeLLM(
        {
            "format": "text",

            "posts": [
                (
                    "Science proves stopping "
                    "3 reps early guarantees gains."
                )
            ],

            "cta": "",

            "claims_used": [
                CLAIM_1,
            ],

            "capabilities_used": [],
        }
    )


    with pytest.raises(
        GeneratedContentValidationError
    ) as exc:

        x_writer(
            llm
        ).write(
            packet=packet(),
            content_family=(
                ContentFamily.C02
            ),
        )


    assert (
        exc.value.content.posts[0]
        == (
            "Science proves stopping "
            "3 reps early guarantees gains."
        )
    )

    assert (
        exc.value.reason
    )
