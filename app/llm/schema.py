from __future__ import annotations

from typing import Any


# Gemini structured output supports a subset of JSON Schema.
#
# Pydantic may emit additional validation keywords such as:
#
#   minLength
#   maxLength
#   default
#
# Those validations remain enforced locally by Pydantic after
# Gemini returns its JSON. They do not need to be sent to Gemini.

SUPPORTED_KEYS = {
    "$id",
    "$defs",
    "$ref",
    "$anchor",
    "type",
    "format",
    "title",
    "description",
    "enum",
    "items",
    "prefixItems",
    "minItems",
    "maxItems",
    "minimum",
    "maximum",
    "anyOf",
    "oneOf",
    "properties",
    "additionalProperties",
    "required",
}


def sanitize_gemini_schema(
    schema: dict[str, Any],
) -> dict[str, Any]:

    def clean(
        value: Any,
        *,
        context: str | None = None,
    ) -> Any:

        if isinstance(value, list):

            return [
                clean(item)
                for item in value
            ]


        if not isinstance(value, dict):

            return value


        output: dict[str, Any] = {}


        for key, item in value.items():

            # Property names and $defs names are user/model
            # field names, not JSON-Schema keywords.
            if key in {
                "properties",
                "$defs",
            }:

                if isinstance(item, dict):

                    output[key] = {
                        name: clean(
                            child,
                            context=key,
                        )
                        for name, child
                        in item.items()
                    }

                continue


            if key not in SUPPORTED_KEYS:

                continue


            if key in {
                "items",
                "additionalProperties",
            }:

                output[key] = clean(
                    item,
                    context=key,
                )

                continue


            if key in {
                "anyOf",
                "oneOf",
                "prefixItems",
            }:

                output[key] = clean(
                    item,
                    context=key,
                )

                continue


            output[key] = item


        return output


    return clean(schema)
