from __future__ import annotations


# Deliberately simple Gemini-facing schema.
#
# Important:
#
# This is NOT our final validation layer.
#
# Gemini only sees this compact schema.
# The returned JSON is then validated again by the full
# Pydantic EvidenceSynthesis model.
#
# Keeping the API schema small avoids Gemini rejecting
# a large Pydantic-generated schema.

EVIDENCE_SYNTHESIS_SCHEMA = {
    "type": "object",

    "properties": {

        "evidence_status": {
            "type": "string",
            "enum": [
                "sufficient",
                "limited",
                "conflicting",
                "insufficient",
            ],
        },

        "summary": {
            "type": "string",
        },

        "core_finding": {
            "type": "string",
        },

        "important_nuance": {
            "type": "string",
        },

        "limitations": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },

        "dauntra_relevance": {
            "type": "string",
        },

        "claims": {
            "type": "array",

            "items": {
                "type": "object",

                "properties": {

                    "claim": {
                        "type": "string",
                    },

                    "sensitivity": {
                        "type": "string",
                        "enum": [
                            "general",
                            "training",
                            "nutrition",
                            "supplement",
                            "health",
                            "product",
                        ],
                    },

                    "source_indexes": {
                        "type": "array",
                        "items": {
                            "type": "integer",
                        },
                    },

                    "confidence": {
                        "type": "string",
                        "enum": [
                            "high",
                            "medium",
                            "low",
                        ],
                    },

                    "human_review_required": {
                        "type": "boolean",
                    },
                },

                "required": [
                    "claim",
                    "sensitivity",
                    "source_indexes",
                    "confidence",
                    "human_review_required",
                ],
            },
        },

        "recommended_angles": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },

        "prohibited_angles": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },

        "requires_human_review": {
            "type": "boolean",
        },
    },

    "required": [
        "evidence_status",
        "summary",
        "core_finding",
        "important_nuance",
        "limitations",
        "dauntra_relevance",
        "claims",
        "recommended_angles",
        "prohibited_angles",
        "requires_human_review",
    ],
}
