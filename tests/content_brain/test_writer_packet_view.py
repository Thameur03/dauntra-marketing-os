from app.content_brain.packet_view import (
    prepare_writer_packet,
)

from contracts.research import (
    ResearchPacket,
)


def test_writer_packet_removes_tangential_claims_and_reindexes():

    packet = ResearchPacket(

        subject=(
            "Does training to muscular failure "
            "produce more muscle hypertrophy "
            "than stopping a few reps before failure?"
        ),

        evidence_status="conflicting",

        summary=(
            "Research compares failure and "
            "non-failure resistance training."
        ),

        core_finding=(
            "Complete failure is not always required."
        ),

        important_nuance=(
            "Proximity to failure may matter."
        ),

        limitations=[
            "Protocols differ."
        ],

        sources=[
            {
                "title": (
                    "Training to failure versus "
                    "non-failure for hypertrophy"
                ),
                "publisher": "Fixture",
                "source_type": "meta_analysis",
                "notes": (
                    "Muscular failure and "
                    "hypertrophy."
                ),
            },

            {
                "title": (
                    "Resistance training repetition "
                    "tempo and hypertrophy"
                ),
                "publisher": "Fixture",
                "source_type": "meta_analysis",
                "notes": (
                    "Tempo study with incidental "
                    "failure mention."
                ),
            },

            {
                "title": (
                    "Proximity-to-failure and "
                    "muscle hypertrophy"
                ),
                "publisher": "Fixture",
                "source_type": "systematic_review",
                "notes": (
                    "Repetitions in reserve "
                    "and hypertrophy."
                ),
            },
        ],

        claims=[
            {
                "claim": (
                    "Failure was not clearly superior "
                    "to non-failure training."
                ),
                "sensitivity": "training",
                "source_indexes": [0],
                "confidence": "high",
            },

            {
                "claim": (
                    "Repetition tempo affected "
                    "hypertrophy."
                ),
                "sensitivity": "training",
                "source_indexes": [1],
                "confidence": "medium",
            },

            {
                "claim": (
                    "Proximity to failure may influence "
                    "hypertrophy."
                ),
                "sensitivity": "training",
                "source_indexes": [2],
                "confidence": "medium",
            },
        ],

        recommended_angles=[
            "Explain proximity to failure."
        ],

        prohibited_angles=[
            "Failure is mandatory."
        ],

        requires_human_review=True,
    )


    result = prepare_writer_packet(
        packet
    )


    assert len(
        result.sources
    ) == 2


    assert len(
        result.claims
    ) == 2


    assert [
        claim.source_indexes
        for claim
        in result.claims
    ] == [
        [0],
        [1],
    ]


    titles = [
        source.title.lower()
        for source
        in result.sources
    ]


    assert not any(
        "tempo"
        in title
        for title
        in titles
    )
