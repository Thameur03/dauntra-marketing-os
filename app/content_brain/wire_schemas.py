from __future__ import annotations


STRING_LIST = {
    "type": "array",
    "items": {
        "type": "string",
    },
}


INSTAGRAM_SCHEMA = {
    "type": "object",
    "properties": {
        "hook": {
            "type": "string",
            "minLength": 1,
            "maxLength": 300,
        },

        "slides": {
            "type": "array",
            "minItems": 2,
            "maxItems": 10,
            "items": {
                "type": "object",
                "properties": {
                    "slide_number": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 10,
                    },

                    "headline": {
                        "type": "string",
                        "maxLength": 180,
                    },

                    "body": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 1200,
                    },

                    "emphasis": {
                        "type": "string",
                        "maxLength": 240,
                    },
                },

                "required": [
                    "slide_number",
                    "headline",
                    "body",
                    "emphasis",
                ],

                "additionalProperties": False,
            },
        },

        "caption": {
            "type": "string",
            "minLength": 1,
            "maxLength": 4000,
        },

        "cta": {
            "type": "string",
            "maxLength": 300,
        },

        "claims_used": STRING_LIST,

        "capabilities_used": STRING_LIST,
    },

    "required": [
        "hook",
        "slides",
        "caption",
        "cta",
        "claims_used",
        "capabilities_used",
    ],

    "additionalProperties": False,
}


TIKTOK_SCHEMA = {
    "type": "object",

    "properties": {
        "hook": {
            "type": "string",
            "minLength": 1,
            "maxLength": 300,
        },

        "chunks": {
            "type": "array",
            "minItems": 1,
            "maxItems": 30,

            "items": {
                "type": "object",

                "properties": {
                    "text": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 500,
                    },

                    "duration_ms": {
                        "type": "integer",
                        "minimum": 250,
                        "maximum": 30000,
                    },
                },

                "required": [
                    "text",
                    "duration_ms",
                ],

                "additionalProperties": False,
            },
        },

        "caption": {
            "type": "string",
            "minLength": 1,
            "maxLength": 3000,
        },

        "cta": {
            "type": "string",
            "maxLength": 300,
        },

        "claims_used": STRING_LIST,

        "capabilities_used": STRING_LIST,
    },

    "required": [
        "hook",
        "chunks",
        "caption",
        "cta",
        "claims_used",
        "capabilities_used",
    ],

    "additionalProperties": False,
}


X_SCHEMA = {
    "type": "object",

    "properties": {
        "format": {
            "type": "string",
            "enum": [
                "text",
                "thread",
            ],
        },

        "posts": {
            "type": "array",
            "minItems": 1,
            "maxItems": 20,

            "items": {
                "type": "string",
                "minLength": 1,
                "maxLength": 280,
            },
        },

        "cta": {
            "type": "string",
            "maxLength": 300,
        },

        "claims_used": STRING_LIST,

        "capabilities_used": STRING_LIST,
    },

    "required": [
        "format",
        "posts",
        "cta",
        "claims_used",
        "capabilities_used",
    ],

    "additionalProperties": False,
}


FACEBOOK_SCHEMA = {
    "type": "object",

    "properties": {
        "format": {
            "type": "string",

            "enum": [
                "text",
                "image",
                "video",
            ],
        },

        "body": {
            "type": "string",
            "minLength": 1,
            "maxLength": 12000,
        },

        "cta": {
            "type": "string",
            "maxLength": 300,
        },

        "claims_used": STRING_LIST,

        "capabilities_used": STRING_LIST,
    },

    "required": [
        "format",
        "body",
        "cta",
        "claims_used",
        "capabilities_used",
    ],

    "additionalProperties": False,
}
