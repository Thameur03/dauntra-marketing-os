from __future__ import annotations

from copy import deepcopy

import pytest

from app.content_brain.package import (
    build_content_package,
)

from app.db.content_store import (
    StoredContentItem,
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


CLAIM = (
    "Pooled evidence indicates no statistically "
    "significant hypertrophy difference between "
    "failure and non-failure resistance training."
)


def packet() -> ResearchPacket:

    return ResearchPacket(

        subject=(
            "Does resistance training to failure "
            "produce more hypertrophy?"
        ),

        evidence_status="conflicting",

        summary=(
            "Evidence does not show a clear universal "
            "hypertrophic advantage to failure."
        ),

        core_finding=(
            "Complete failure is not clearly superior."
        ),

        important_nuance=(
            "Training status and protocol matter."
        ),

        limitations=[
            (
                "Failure definitions vary "
                "between studies."
            )
        ],

        sources=[
            {
                "title": (
                    "Failure versus non-failure "
                    "resistance training"
                ),

                "publisher": "Fixture",

                "source_type": (
                    "meta_analysis"
                ),

                "notes": (
                    "Fixture evidence about "
                    "failure and hypertrophy."
                ),
            },

            {
                "title": (
                    "Proximity-to-failure "
                    "and hypertrophy"
                ),

                "publisher": "Fixture",

                "source_type": (
                    "systematic_review"
                ),

                "notes": (
                    "Fixture evidence about "
                    "proximity to failure."
                ),
            },
        ],

        claims=[
            {
                "claim": CLAIM,

                "sensitivity": (
                    "training"
                ),

                "source_indexes": [
                    0,
                    1,
                ],

                "confidence": "high",

                "human_review_required": (
                    True
                ),
            }
        ],

        recommended_angles=[
            (
                "Explain the evidence "
                "without absolutism."
            )
        ],

        prohibited_angles=[
            (
                "Failure is mandatory "
                "for hypertrophy."
            )
        ],

        requires_human_review=True,
    )


class QueueLLM:

    def __init__(
        self,
        outputs,
    ):

        self.outputs = list(
            outputs
        )

        self.calls = []


    @property
    def model_name(self):

        return (
            "fake-package-model"
        )


    def generate_json(
        self,
        *,
        prompt,
        schema,
        system_instruction=None,
    ):

        self.calls.append(
            {
                "prompt": prompt,
                "schema": schema,
                "system_instruction": (
                    system_instruction
                ),
            }
        )


        if not self.outputs:

            raise RuntimeError(
                "No fake output remaining."
            )


        value = self.outputs.pop(
            0
        )


        if isinstance(
            value,
            Exception,
        ):

            raise value


        return deepcopy(
            value
        )


    def generate_structured(
        self,
        **kwargs,
    ):

        raise AssertionError(
            "Package writers should use "
            "generate_json."
        )


def instagram_output():

    return {
        "hook": (
            "Is failure actually required?"
        ),

        "slides": [
            {
                "slide_number": 1,
                "headline": "The question",
                "body": (
                    "Complete failure is not "
                    "clearly superior."
                ),
                "emphasis": "",
            },

            {
                "slide_number": 2,
                "headline": "The evidence",
                "body": CLAIM,
                "emphasis": "",
            },
        ],

        "caption": (
            "The evidence is more nuanced "
            "than a simple failure rule."
        ),

        "cta": (
            "Save this for later."
        ),

        "claims_used": [
            CLAIM
        ],

        "capabilities_used": [],
    }


def x_output():

    return {
        "format": "text",

        "posts": [
            (
                "Training to failure is not "
                "clearly superior for hypertrophy."
            )
        ],

        "cta": "",

        "claims_used": [
            CLAIM
        ],

        "capabilities_used": [],
    }


def test_builds_independent_multiplatform_package():

    llm = QueueLLM(
        [
            instagram_output(),
            x_output(),
        ]
    )


    result = build_content_package(

        subject_id="subject-1",

        research_packet_id="packet-1",

        packet=packet(),

        content_family=(
            ContentFamily.C02
        ),

        platforms=[
            Platform.INSTAGRAM,
            Platform.X,
        ],

        llm=llm,
    )


    assert (
        result.build_status
        == "COMPLETE"
    )


    assert (
        result.requires_human_review
        is True
    )


    assert len(
        result.items
    ) == 2


    assert len(
        llm.calls
    ) == 2


    assert (
        "instagram"
        in llm.calls[0][
            "prompt"
        ]
    )


    assert (
        "\nx\n"
        in llm.calls[1][
            "prompt"
        ]
    )


    assert (
        result.items[0]
        .generation_key
        != result.items[1]
        .generation_key
    )


def test_validation_failure_does_not_destroy_success():

    bad_x = x_output()

    bad_x[
        "claims_used"
    ] = [
        "Invented claim."
    ]


    llm = QueueLLM(
        [
            instagram_output(),
            bad_x,
        ]
    )


    result = build_content_package(

        subject_id="subject-1",

        research_packet_id="packet-1",

        packet=packet(),

        content_family=(
            ContentFamily.C02
        ),

        platforms=[
            Platform.INSTAGRAM,
            Platform.X,
        ],

        llm=llm,
    )


    assert (
        result.build_status
        == "PARTIAL"
    )


    assert (
        result.items[0].status
        == "NEEDS_HUMAN_REVIEW"
    )


    assert (
        result.items[1].status
        == "FAILED_VALIDATION"
    )


    assert (
        result.items[0].content
        is not None
    )


def test_generation_error_preserves_previous_success_and_skips_rest():

    llm = QueueLLM(
        [
            instagram_output(),
            RuntimeError(
                "provider unavailable"
            ),
        ]
    )


    result = build_content_package(

        subject_id="subject-1",

        research_packet_id="packet-1",

        packet=packet(),

        content_family=(
            ContentFamily.C02
        ),

        platforms=[
            Platform.INSTAGRAM,
            Platform.X,
            Platform.FACEBOOK,
        ],

        llm=llm,
    )


    assert (
        result.build_status
        == "PARTIAL"
    )


    assert [
        item.status
        for item
        in result.items
    ] == [
        "NEEDS_HUMAN_REVIEW",
        "FAILED_GENERATION",
        "SKIPPED",
    ]


def test_package_id_is_deterministic():

    first = build_content_package(

        subject_id="subject-1",

        research_packet_id="packet-1",

        packet=packet(),

        content_family=(
            ContentFamily.C02
        ),

        platforms=[
            Platform.INSTAGRAM,
        ],

        llm=QueueLLM(
            [
                instagram_output()
            ]
        ),
    )


    second = build_content_package(

        subject_id="subject-1",

        research_packet_id="packet-1",

        packet=packet(),

        content_family=(
            ContentFamily.C02
        ),

        platforms=[
            Platform.INSTAGRAM,
        ],

        llm=QueueLLM(
            [
                instagram_output()
            ]
        ),
    )


    assert (
        first.package_id
        == second.package_id
    )


    assert (
        first.items[0]
        .generation_key
        == second.items[0]
        .generation_key
    )


def test_persistence_failure_preserves_generated_content():

    class BrokenStore:

        def find_existing(
            self,
            **kwargs,
        ):

            return None


        def save(
            self,
            **kwargs,
        ):

            raise RuntimeError(
                "database unavailable"
            )


    result = build_content_package(

        subject_id="subject-1",

        research_packet_id="packet-1",

        packet=packet(),

        content_family=(
            ContentFamily.C02
        ),

        platforms=[
            Platform.INSTAGRAM
        ],

        llm=QueueLLM(
            [
                instagram_output()
            ]
        ),

        store=BrokenStore(),
    )


    assert (
        result.build_status
        == "FAILED"
    )


    assert (
        result.items[0].status
        == "FAILED_PERSISTENCE"
    )


    assert (
        result.items[0].content
        is not None
    )


    assert (
        "database unavailable"
        in result.items[0].error
    )
