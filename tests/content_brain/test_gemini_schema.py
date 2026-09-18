import json

from app.llm.schema import (
    sanitize_gemini_schema,
)

from app.research_models import (
    EvidenceSynthesis,
)


def test_gemini_schema_removes_unsupported_constraints():

    raw = (
        EvidenceSynthesis
        .model_json_schema()
    )

    cleaned = (
        sanitize_gemini_schema(
            raw
        )
    )

    encoded = json.dumps(
        cleaned
    )


    assert '"minLength"' not in encoded
    assert '"maxLength"' not in encoded
    assert '"default"' not in encoded


def test_gemini_schema_keeps_required_structure():

    cleaned = (
        sanitize_gemini_schema(
            EvidenceSynthesis
            .model_json_schema()
        )
    )

    assert (
        cleaned["type"]
        == "object"
    )

    assert (
        "properties"
        in cleaned
    )

    assert (
        "$defs"
        in cleaned
    )

    assert (
        "claims"
        in cleaned["properties"]
    )
