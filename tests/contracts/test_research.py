from contracts.research import ResearchPacket


def test_valid_research_packet():

    packet = ResearchPacket(

        subject=(
            "Does protein timing matter?"
        ),

        evidence_status="sufficient",

        summary=(
            "Protein distribution and total daily intake "
            "should be considered together when discussing timing."
        ),

        core_finding=(
            "Total intake remains a major factor."
        ),

        important_nuance=(
            "Timing can still matter in specific contexts."
        ),

        limitations=[],

        dauntra_relevance=(
            "Relevant to nutrition education."
        ),

        sources=[
            {
                "title": (
                    "Example research source"
                ),
                "url": (
                    "https://example.com/study"
                ),
                "publisher": "Example",
                "source_type": "study",
                "notes": (
                    "Used only as a contract "
                    "validation fixture."
                ),
            }
        ],

        claims=[
            {
                "claim": (
                    "Total intake is important."
                ),
                "sensitivity": "nutrition",
                "source_indexes": [0],
                "confidence": "high",
                "human_review_required": True,
            }
        ],

        recommended_angles=[
            "What matters more than perfect timing?"
        ],

        prohibited_angles=[
            "Protein timing never matters."
        ],

        requires_human_review=True,
    )

    assert (
        packet.requires_human_review
        is True
    )

    assert len(
        packet.sources
    ) == 1
