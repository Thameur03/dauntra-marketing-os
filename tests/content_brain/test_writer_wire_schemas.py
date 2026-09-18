from app.content_brain.wire_schemas import (
    FACEBOOK_SCHEMA,
    INSTAGRAM_SCHEMA,
    TIKTOK_SCHEMA,
    X_SCHEMA,
)


def test_writer_schemas_are_compact_objects():

    for schema in (
        INSTAGRAM_SCHEMA,
        TIKTOK_SCHEMA,
        X_SCHEMA,
        FACEBOOK_SCHEMA,
    ):

        assert (
            schema["type"]
            == "object"
        )

        assert (
            schema[
                "additionalProperties"
            ]
            is False
        )

        text = str(
            schema
        )

        assert "$ref" not in text
        assert "$defs" not in text
        assert "anyOf" not in text


def test_x_wire_schema_enforces_280():

    assert (
        X_SCHEMA[
            "properties"
        ][
            "posts"
        ][
            "items"
        ][
            "maxLength"
        ]
        == 280
    )
