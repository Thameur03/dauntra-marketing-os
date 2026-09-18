from __future__ import annotations

from pathlib import Path

import yaml

from app.product_truth import (
    CapabilityMarketingContext,
)

from contracts.common import (
    ContentFamily,
    Platform,
)

from contracts.research import (
    ResearchPacket,
)


ROOT = Path(__file__).resolve().parents[2]


PLATFORM_PROMPTS = {
    Platform.INSTAGRAM: (
        ROOT
        / "prompts"
        / "writers"
        / "instagram.txt"
    ),

    Platform.TIKTOK: (
        ROOT
        / "prompts"
        / "writers"
        / "tiktok.txt"
    ),

    Platform.X: (
        ROOT
        / "prompts"
        / "writers"
        / "x.txt"
    ),

    Platform.FACEBOOK: (
        ROOT
        / "prompts"
        / "writers"
        / "facebook.txt"
    ),
}


def _load_yaml(
    path: Path,
) -> dict:

    value = yaml.safe_load(
        path.read_text(
            encoding="utf-8"
        )
    )

    if not isinstance(
        value,
        dict,
    ):
        raise ValueError(
            f"Expected mapping in {path}"
        )

    return value


def writer_system_instruction(
    platform: Platform,
) -> str:

    common_path = (
        ROOT
        / "prompts"
        / "writers"
        / "common_system.txt"
    )

    platform_path = (
        PLATFORM_PROMPTS[
            platform
        ]
    )

    return (
        common_path.read_text(
            encoding="utf-8"
        ).strip()
        + "\n\nPLATFORM-SPECIFIC RULES\n\n"
        + platform_path.read_text(
            encoding="utf-8"
        ).strip()
    )


def _brand_context() -> str:

    profile = _load_yaml(
        ROOT
        / "brand"
        / "brand_profile.yaml"
    )

    brand = profile.get(
        "brand",
        {},
    )

    voice = profile.get(
        "voice",
        {},
    )

    writing = profile.get(
        "writing_rules",
        {},
    )

    global_rules = profile.get(
        "global_rules",
        [],
    )

    should_be = voice.get(
        "should_be",
        [],
    )

    should_not_be = voice.get(
        "should_not_be",
        [],
    )

    prefer = writing.get(
        "prefer",
        [],
    )

    avoid = writing.get(
        "avoid",
        [],
    )

    return "\n".join(
        [
            (
                "Brand: "
                + str(
                    brand.get(
                        "name",
                        "DAUNTRA",
                    )
                )
            ),

            (
                "Tagline: "
                + str(
                    brand.get(
                        "tagline",
                        "",
                    )
                )
            ),

            (
                "Voice should be: "
                + ", ".join(
                    map(
                        str,
                        should_be,
                    )
                )
            ),

            (
                "Voice should not be: "
                + ", ".join(
                    map(
                        str,
                        should_not_be,
                    )
                )
            ),

            (
                "Prefer: "
                + "; ".join(
                    map(
                        str,
                        prefer,
                    )
                )
            ),

            (
                "Avoid: "
                + "; ".join(
                    map(
                        str,
                        avoid,
                    )
                )
            ),

            (
                "Global rules: "
                + "; ".join(
                    map(
                        str,
                        global_rules,
                    )
                )
            ),
        ]
    )


def _cta_context() -> str:

    strategy = _load_yaml(
        ROOT
        / "brand"
        / "content_strategy.yaml"
    )

    policy = strategy.get(
        "cta_policy",
        {},
    )

    primary = policy.get(
        "primary",
        [],
    )

    secondary = policy.get(
        "secondary",
        [],
    )

    rules = policy.get(
        "rules",
        [],
    )

    return "\n".join(
        [
            (
                "Approved primary CTA options: "
                + "; ".join(
                    map(
                        str,
                        primary,
                    )
                )
            ),

            (
                "Approved secondary CTA options: "
                + "; ".join(
                    map(
                        str,
                        secondary,
                    )
                )
            ),

            (
                "CTA rules: "
                + "; ".join(
                    map(
                        str,
                        rules,
                    )
                )
            ),
        ]
    )


def _research_context(
    packet: ResearchPacket,
) -> str:

    lines: list[str] = [
        f"Subject: {packet.subject}",
        (
            "Evidence status: "
            f"{packet.evidence_status}"
        ),
        f"Summary: {packet.summary}",
        (
            "Core finding: "
            f"{packet.core_finding}"
        ),
    ]


    if packet.important_nuance:

        lines.append(
            "Important nuance: "
            + packet.important_nuance
        )


    if packet.limitations:

        lines.append(
            "Limitations:"
        )

        for limitation in (
            packet.limitations
        ):

            lines.append(
                "- "
                + limitation
            )


    lines.append(
        ""
    )

    lines.append(
        "EVIDENCE CLAIMS"
    )


    for index, claim in enumerate(
        packet.claims
    ):

        lines.append(
            f"[{index}] {claim.claim}"
        )

        lines.append(
            "    confidence="
            f"{claim.confidence}; "
            "sensitivity="
            f"{claim.sensitivity}; "
            "sources="
            f"{claim.source_indexes}"
        )


    lines.append(
        ""
    )

    lines.append(
        "SOURCE TITLES"
    )


    for index, source in enumerate(
        packet.sources
    ):

        lines.append(
            f"[{index}] "
            f"{source.title}"
        )


    lines.append(
        ""
    )

    lines.append(
        "RECOMMENDED ANGLES"
    )


    for angle in (
        packet.recommended_angles
    ):

        lines.append(
            "- "
            + angle
        )


    if packet.prohibited_angles:

        lines.append(
            ""
        )

        lines.append(
            "PROHIBITED ANGLES"
        )


        for angle in (
            packet.prohibited_angles
        ):

            lines.append(
                "- "
                + angle
            )


    return "\n".join(
        lines
    )


def _capability_context(
    capabilities: tuple[
        CapabilityMarketingContext,
        ...,
    ],
) -> str:

    if not capabilities:

        return (
            "APPROVED DAUNTRA CAPABILITIES\n"
            "None supplied.\n"
            "Do not make DAUNTRA feature claims."
        )


    lines = [
        "APPROVED DAUNTRA CAPABILITIES"
    ]


    for capability in capabilities:

        lines.extend(
            [
                "",
                (
                    "Capability ID: "
                    + capability.capability_id
                ),

                (
                    "Display name: "
                    + capability.display_name
                ),

                (
                    "Status: "
                    + capability.status
                ),

                (
                    "Description: "
                    + capability.description
                ),

                "Allowed claims:",
            ]
        )


        for claim in (
            capability.allowed_claims
        ):

            lines.append(
                "- "
                + claim
            )


        lines.append(
            "Limitations:"
        )


        for limitation in (
            capability.limitations
        ):

            lines.append(
                "- "
                + limitation
            )


        lines.append(
            "Prohibited claims:"
        )


        for claim in (
            capability.prohibited_claims
        ):

            lines.append(
                "- "
                + claim
            )


    return "\n".join(
        lines
    )


def build_writer_prompt(
    *,
    platform: Platform,
    content_family: ContentFamily,
    packet: ResearchPacket,
    capabilities: tuple[
        CapabilityMarketingContext,
        ...,
    ],
) -> str:

    return "\n\n".join(
        [
            (
                "TARGET PLATFORM\n"
                f"{platform.value}"
            ),

            (
                "CONTENT FAMILY\n"
                f"{content_family.value}"
            ),

            (
                "BRAND CONTEXT\n"
                + _brand_context()
            ),

            (
                "CTA CONTEXT\n"
                + _cta_context()
            ),

            (
                "RESEARCH PACKET\n"
                + _research_context(
                    packet
                )
            ),

            _capability_context(
                capabilities
            ),

            (
                "OUTPUT REQUIREMENT\n"
                "Return only the requested structured JSON. "
                "Do not include markdown or commentary."
            ),
        ]
    )
