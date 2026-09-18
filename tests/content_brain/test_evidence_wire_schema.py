from app.llm.evidence_schema import (
    EVIDENCE_SYNTHESIS_SCHEMA,
)


def test_wire_schema_has_no_refs():

    text = str(
        EVIDENCE_SYNTHESIS_SCHEMA
    )

    assert "$defs" not in text
    assert "$ref" not in text
    assert "anyOf" not in text


def test_wire_schema_contains_claim_structure():

    properties = (
        EVIDENCE_SYNTHESIS_SCHEMA[
            "properties"
        ]
    )

    assert "claims" in properties

    claim_properties = (
        properties["claims"]
        ["items"]
        ["properties"]
    )

    assert (
        "source_indexes"
        in claim_properties
    )

    assert (
        "confidence"
        in claim_properties
    )


def test_wire_schema_has_required_root_fields():

    required = set(
        EVIDENCE_SYNTHESIS_SCHEMA[
            "required"
        ]
    )

    assert (
        "evidence_status"
        in required
    )

    assert "claims" in required

    assert (
        "recommended_angles"
        in required
    )
