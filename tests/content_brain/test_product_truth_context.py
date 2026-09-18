import pytest

from app.product_truth import (
    capability_marketing_context,
    capability_marketing_contexts,
    capability_summary,
)


def test_capability_summary_has_allowed_and_blocked():

    summary = (
        capability_summary()
    )

    assert (
        "workout_logging"
        in summary.allowed
    )

    assert (
        "ai_coach"
        in summary.blocked
    )


def test_safe_context_exposes_marketing_fields():

    context = (
        capability_marketing_context(
            "workout_logging"
        )
    )

    assert (
        context.capability_id
        == "workout_logging"
    )

    assert isinstance(
        context.allowed_claims,
        tuple,
    )

    assert isinstance(
        context.limitations,
        tuple,
    )

    assert isinstance(
        context.prohibited_claims,
        tuple,
    )


def test_blocked_capability_has_no_writer_context():

    with pytest.raises(
        ValueError,
        match="not approved",
    ):

        capability_marketing_context(
            "ai_coach"
        )


def test_context_order_is_preserved_and_deduplicated():

    contexts = (
        capability_marketing_contexts(
            [
                "workout_logging",
                "workout_logging",
                "rest_timer",
            ]
        )
    )

    assert [
        item.capability_id
        for item in contexts
    ] == [
        "workout_logging",
        "rest_timer",
    ]
