import pytest

from app.content_brain.validators import (
    validate_content_grounding,
)

from contracts.common import (
    ContentFamily,
)

from contracts.content import (
    InstagramCarouselContent,
)

from contracts.research import (
    ResearchPacket,
)


CLAIM_A = (
    "Pooled meta-analytic evidence indicates no "
    "statistically significant difference in muscle "
    "hypertrophy between resistance training performed "
    "to momentary muscular failure and non-failure "
    "training in broad populations."
)


CLAIM_B = (
    "An exploratory multilevel meta-regression found "
    "that muscle hypertrophy increased as sets were "
    "terminated closer to failure (lower estimated "
    "repetitions in reserve)."
)


CLAIM_C = (
    "A randomized trial in trained individuals found "
    "similar quadriceps hypertrophy between sets taken "
    "to momentary failure and sets stopped at 1–2 "
    "repetitions in reserve, but failure caused greater "
    "repetition and velocity loss."
)


def packet() -> ResearchPacket:

    return ResearchPacket(
        subject=(
            "Failure versus repetitions "
            "in reserve"
        ),

        evidence_status="conflicting",

        summary=(
            "Evidence is mixed, with broad analyses "
            "showing no clear hypertrophic advantage "
            "to complete failure."
        ),

        core_finding=(
            "Complete muscular failure is not "
            "strictly required for hypertrophy."
        ),

        important_nuance=(
            "Some evidence suggests proximity "
            "to failure matters."
        ),

        limitations=[
            "Protocols and failure definitions vary."
        ],

        sources=[
            {
                "title": "Failure meta-analysis",
                "publisher": "Fixture",
                "source_type": "meta_analysis",
                "notes": "Fixture.",
            }
        ],

        claims=[
            {
                "claim": CLAIM_A,
                "sensitivity": "training",
                "source_indexes": [0],
                "confidence": "high",
            },

            {
                "claim": CLAIM_B,
                "sensitivity": "training",
                "source_indexes": [0],
                "confidence": "medium",
            },

            {
                "claim": CLAIM_C,
                "sensitivity": "training",
                "source_indexes": [0],
                "confidence": "high",
            },
        ],

        recommended_angles=[
            "Preserve nuance."
        ],

        prohibited_angles=[
            "Failure is mandatory."
        ],

        requires_human_review=True,
    )


def content(
    body: str,
    *,
    claims=None,
) -> InstagramCarouselContent:

    return InstagramCarouselContent(
        content_family=(
            ContentFamily.C02
        ),

        hook="Training near failure.",

        slides=[
            {
                "slide_number": 1,
                "headline": "Evidence",
                "body": body,
                "emphasis": None,
            },

            {
                "slide_number": 2,
                "headline": "Context",
                "body": (
                    "The evidence still depends "
                    "on protocol and population."
                ),
                "emphasis": None,
            },
        ],

        caption=(
            "Use the evidence with context."
        ),

        claims_used=(
            claims
            if claims is not None
            else [
                CLAIM_A,
                CLAIM_B,
                CLAIM_C,
            ]
        ),

        capabilities_used=[],
    )


def validate(
    item: InstagramCarouselContent,
):

    validate_content_grounding(
        content=item,
        packet=packet(),
        requested_capabilities=[],
    )


def test_rejects_unsupported_equivalence():

    with pytest.raises(
        ValueError,
        match="equivalence",
    ):

        validate(
            content(
                "Stopping short provides "
                "virtually the same gains."
            )
        )


def test_rejects_invented_rir_number():

    with pytest.raises(
        ValueError,
        match="numeric detail",
    ):

        validate(
            content(
                "Stopping 5 reps before failure "
                "is very different."
            )
        )


def test_allows_supported_one_to_two_rir():

    validate(
        content(
            "One trial found similar quadriceps "
            "hypertrophy when trained to failure "
            "or stopped at 1–2 repetitions "
            "in reserve."
        )
    )


def test_rejects_new_significantly_language():

    with pytest.raises(
        ValueError,
        match="significantly",
    ):

        validate(
            content(
                "Failure significantly increased "
                "repetition and velocity loss.",
                claims=[
                    CLAIM_C,
                ],
            )
        )


def test_rejects_certainty_from_conflicting_packet():

    with pytest.raises(
        ValueError,
        match="certainty",
    ):

        validate(
            content(
                "Science proves failure "
                "is unnecessary."
            )
        )


def test_first_live_instagram_candidate_is_rejected():

    item = InstagramCarouselContent(

        content_family=(
            ContentFamily.C02
        ),

        hook=(
            "Do you actually need to hit muscular "
            "failure to maximize hypertrophy?"
        ),

        slides=[
            {
                "slide_number": 1,
                "headline": (
                    "Do You Need to Train "
                    "to Complete Failure?"
                ),
                "body": (
                    "Evidence paints a more "
                    "balanced picture."
                ),
                "emphasis": (
                    "Proximity matters, but absolute "
                    "failure is not mandatory."
                ),
            },

            {
                "slide_number": 2,
                "headline": (
                    "What Broad Evidence Shows"
                ),
                "body": CLAIM_A,
                "emphasis": (
                    "Stopping before failure "
                    "does not blunt your gains."
                ),
            },

            {
                "slide_number": 3,
                "headline": (
                    "The Proximity Gradient"
                ),
                "body": CLAIM_B,
                "emphasis": (
                    "Ending a set 1–2 reps from failure "
                    "is very different from ending "
                    "it 5 reps early."
                ),
            },

            {
                "slide_number": 4,
                "headline": (
                    "The Cost of That Last Rep"
                ),
                "body": CLAIM_C,
                "emphasis": (
                    "Failure brings more fatigue."
                ),
            },
        ],

        caption=(
            "Failure significantly increases "
            "repetition and velocity loss."
        ),

        cta=(
            "Save this for later."
        ),

        claims_used=[
            CLAIM_A,
            CLAIM_B,
            CLAIM_C,
        ],

        capabilities_used=[],
    )


    with pytest.raises(
        ValueError
    ):

        validate(
            item
        )


def test_supported_range_allows_alternate_wording():

    item = content(
        (
            "A trial compared complete failure "
            "with stopping 1 to 2 repetitions "
            "in reserve."
        ),
        claims=[
            CLAIM_C,
        ],
    )


    validate(
        item
    )


def test_supported_range_does_not_allow_new_three():

    with pytest.raises(
        ValueError,
        match="3",
    ):

        validate(
            content(
                (
                    "A practical option is stopping "
                    "1 to 3 repetitions in reserve."
                ),
                claims=[
                    CLAIM_C,
                ],
            )
        )


def test_multiple_violations_are_reported_together():

    with pytest.raises(
        ValueError
    ) as exc:

        validate(
            content(
                (
                    "Science proves stopping 1 to 3 "
                    "repetitions in reserve produces "
                    "virtually the same gains and "
                    "significantly improves recovery."
                ),
                claims=[
                    CLAIM_C,
                ],
            )
        )


    message = str(
        exc.value
    )


    assert "3" in message

    assert (
        "virtually the same"
        in message
    )

    assert (
        "significantly"
        in message
    )

    assert (
        "certainty"
        in message
    )

    assert (
        "recovery"
        in message
    )
