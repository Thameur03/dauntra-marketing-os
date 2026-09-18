import pytest
from pydantic import ValidationError

from contracts.research import ResearchPacket


def base_packet():
    return {
        "subject": "Protein intake",
        "evidence_status": "sufficient",
        "summary": (
            "This is a sufficiently long synthetic "
            "summary used for contract testing."
        ),
        "core_finding": (
            "Total daily protein intake matters."
        ),
        "important_nuance": None,
        "limitations": [],
        "dauntra_relevance": None,
        "sources": [
            {
                "title": "Fixture Source",
                "url": "https://example.com/source",
                "publisher": "Fixture",
                "publication_date": None,
                "source_type": "study",
                "notes": "Synthetic test fixture.",
            }
        ],
        "claims": [
            {
                "claim": (
                    "Total daily protein intake matters."
                ),
                "sensitivity": "training",
                "source_indexes": [0],
                "confidence": "high",
                "human_review_required": False,
            }
        ],
        "recommended_angles": [
            "Explain total intake."
        ],
        "prohibited_angles": [],
        "requires_human_review": False,
    }


def test_valid_packet():
    packet = ResearchPacket(
        **base_packet()
    )

    assert (
        packet.evidence_status
        == "sufficient"
    )


def test_invalid_source_index_rejected():
    data = base_packet()

    data["claims"][0][
        "source_indexes"
    ] = [99]

    with pytest.raises(
        ValidationError
    ):
        ResearchPacket(
            **data
        )


def test_nutrition_requires_human_review():
    data = base_packet()

    data["claims"][0][
        "sensitivity"
    ] = "nutrition"

    packet = ResearchPacket(
        **data
    )

    assert (
        packet.requires_human_review
        is True
    )

    assert (
        packet.claims[0]
        .human_review_required
        is True
    )


def test_insufficient_evidence_requires_review():
    data = base_packet()

    data[
        "evidence_status"
    ] = "insufficient"

    packet = ResearchPacket(
        **data
    )

    assert (
        packet.requires_human_review
        is True
    )
