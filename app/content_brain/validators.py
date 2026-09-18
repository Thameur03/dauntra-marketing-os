from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from app.product_truth import (
    assert_capabilities_allowed,
    capability_marketing_contexts,
)

from contracts.common import (
    ContentFamily,
    Platform,
)

from contracts.content import (
    FacebookContent,
    InstagramCarouselContent,
    TikTokVideoContent,
    XContent,
)

from contracts.research import (
    ResearchPacket,
)


PlatformContent = (
    InstagramCarouselContent
    | TikTokVideoContent
    | XContent
    | FacebookContent
)


def _all_strings(
    value: Any,
) -> list[str]:

    output: list[str] = []


    if isinstance(
        value,
        str,
    ):

        output.append(
            value
        )


    elif isinstance(
        value,
        dict,
    ):

        for child in value.values():

            output.extend(
                _all_strings(
                    child
                )
            )


    elif isinstance(
        value,
        list,
    ):

        for child in value:

            output.extend(
                _all_strings(
                    child
                )
            )


    return output


def _normalized(
    text: str,
) -> str:

    return " ".join(
        text.lower().split()
    )


def validate_content_grounding(
    *,
    content: PlatformContent,
    packet: ResearchPacket,
    requested_capabilities: list[str],
) -> None:

    # --------------------------------------------------------
    # FAMILY
    # --------------------------------------------------------

    family = content.content_family


    # --------------------------------------------------------
    # EVIDENCE CLAIM REFERENCES
    # --------------------------------------------------------

    valid_claims = {
        claim.claim
        for claim
        in packet.claims
    }


    if len(
        content.claims_used
    ) != len(
        set(
            content.claims_used
        )
    ):

        raise ValueError(
            "claims_used contains duplicates."
        )


    for claim in (
        content.claims_used
    ):

        if claim not in valid_claims:

            raise ValueError(
                "Content references an evidence claim "
                "that is not present verbatim in the "
                "ResearchPacket."
            )


    # Educational/evidence families need at least one grounded
    # research claim.

    if (
        family
        in {
            ContentFamily.C01,
            ContentFamily.C02,
            ContentFamily.C03,
        }
        and not content.claims_used
    ):

        raise ValueError(
            f"{family.value} content must reference "
            "at least one validated research claim."
        )


    # --------------------------------------------------------
    # CAPABILITY REFERENCES
    # --------------------------------------------------------

    requested_capabilities = list(
        dict.fromkeys(
            requested_capabilities
        )
    )


    assert_capabilities_allowed(
        requested_capabilities
    )


    if len(
        content.capabilities_used
    ) != len(
        set(
            content.capabilities_used
        )
    ):

        raise ValueError(
            "capabilities_used contains duplicates."
        )


    requested_set = set(
        requested_capabilities
    )


    for capability in (
        content.capabilities_used
    ):

        if capability not in requested_set:

            raise ValueError(
                "Writer used a DAUNTRA capability "
                "that was not explicitly supplied "
                f"to this generation: {capability}"
            )


    assert_capabilities_allowed(
        content.capabilities_used
    )


    # C04 is the dedicated product family.
    if (
        family
        == ContentFamily.C04
        and not content.capabilities_used
    ):

        raise ValueError(
            "C04 product content must reference at "
            "least one approved DAUNTRA capability."
        )


    # --------------------------------------------------------
    # PROHIBITED PRODUCT CLAIM EXACT-MATCH GUARD
    #
    # This is deterministic defense-in-depth.
    # Semantic factual QA comes later in the QA section.
    # --------------------------------------------------------

    if content.capabilities_used:

        contexts = (
            capability_marketing_contexts(
                content.capabilities_used
            )
        )


        text = "\n".join(
            _all_strings(
                content.model_dump(
                    mode="json"
                )
            )
        )


        normalized_text = (
            _normalized(
                text
            )
        )


        for context in contexts:

            for prohibited in (
                context.prohibited_claims
            ):

                normalized_prohibited = (
                    _normalized(
                        prohibited
                    )
                )


                if (
                    normalized_prohibited
                    and normalized_prohibited
                    in normalized_text
                ):

                    raise ValueError(
                        "Generated content contains a "
                        "prohibited product claim: "
                        f"{prohibited}"
                    )


    # --------------------------------------------------------
    # PLATFORM-SPECIFIC DETERMINISTIC RULES
    # --------------------------------------------------------

    if isinstance(
        content,
        InstagramCarouselContent,
    ):

        expected = list(
            range(
                1,
                len(
                    content.slides
                )
                + 1,
            )
        )

        actual = [
            slide.slide_number
            for slide
            in content.slides
        ]


        if actual != expected:

            raise ValueError(
                "Instagram slide numbers must be "
                "sequential starting at 1."
            )


    if isinstance(
        content,
        XContent,
    ):

        for post in content.posts:

            if len(post) > 280:

                raise ValueError(
                    "X post exceeds 280 characters."
                )


        if (
            content.format
            == "text"
            and len(
                content.posts
            )
            != 1
        ):

            raise ValueError(
                "X text format must contain "
                "exactly one post."
            )


        if (
            content.format
            == "thread"
            and len(
                content.posts
            )
            < 2
        ):

            raise ValueError(
                "X thread format must contain "
                "at least two posts."
            )


    # --------------------------------------------------------
    # EVIDENCE LANGUAGE
    # --------------------------------------------------------

    validate_evidence_language(
        content=content,
        packet=packet,
    )

# ============================================================
# EVIDENCE-LANGUAGE DEFENSE IN DEPTH
# ============================================================

import re


UNSUPPORTED_EQUIVALENCE_PHRASES = (
    "virtually the same",
    "essentially the same",
    "exactly the same",
    "identical results",
    "identical gains",
    "equivalent results",
    "equivalent gains",
    "does not blunt your gains",
    "doesn't blunt your gains",
    "does not blunt gains",
    "doesn't blunt gains",
)


ABSOLUTE_PHRASES = (
    "guarantees",
    "guaranteed",
    "always produces",
    "always leads to",
    "never produces",
    "completely eliminates",
)


def _public_copy_strings(
    content: PlatformContent,
) -> list[str]:

    if isinstance(
        content,
        InstagramCarouselContent,
    ):

        values: list[str] = [
            content.hook,
            content.caption,
        ]

        if content.cta:
            values.append(
                content.cta
            )

        for slide in content.slides:

            if slide.headline:
                values.append(
                    slide.headline
                )

            values.append(
                slide.body
            )

            if slide.emphasis:
                values.append(
                    slide.emphasis
                )

        return values


    if isinstance(
        content,
        TikTokVideoContent,
    ):

        values = [
            content.hook,
            content.caption,
        ]

        values.extend(
            chunk.text
            for chunk
            in content.chunks
        )

        if content.cta:
            values.append(
                content.cta
            )

        return values


    if isinstance(
        content,
        XContent,
    ):

        values = list(
            content.posts
        )

        if content.cta:
            values.append(
                content.cta
            )

        return values


    if isinstance(
        content,
        FacebookContent,
    ):

        values = [
            content.body,
        ]

        if content.cta:
            values.append(
                content.cta
            )

        return values


    return []


def _evidence_text(
    packet: ResearchPacket,
) -> str:

    parts = [
        packet.summary,
        packet.core_finding,
        packet.important_nuance or "",
    ]


    parts.extend(
        claim.claim
        for claim
        in packet.claims
    )


    parts.extend(
        packet.limitations
    )


    return "\n".join(
        parts
    )


def _extract_numeric_atoms(
    text: str,
) -> set[str]:
    """
    Compare atomic numeric values rather than surface ranges.

    Example:
      evidence "1–2 repetitions"
      -> {"1", "2"}

      generated "1 to 2 repetitions"
      -> {"1", "2"}

    This prevents punctuation/style differences from becoming
    false positives while still rejecting a new value like 3.
    """

    return set(
        re.findall(
            r"(?<![A-Za-z])"
            r"\d+(?:\.\d+)?"
            r"(?![A-Za-z])",
            text,
        )
    )


def _numeric_contexts(
    text: str,
    numbers: set[str],
) -> list[str]:

    contexts: list[str] = []


    for number in sorted(
        numbers
    ):

        pattern = re.compile(
            rf".{{0,45}}"
            rf"(?<![A-Za-z])"
            rf"{re.escape(number)}"
            rf"(?![A-Za-z])"
            rf".{{0,45}}",
            flags=re.IGNORECASE,
        )


        for match in pattern.finditer(
            text
        ):

            snippet = " ".join(
                match.group(0).split()
            )

            if snippet not in contexts:
                contexts.append(
                    snippet
                )


    return contexts


def validate_evidence_language(
    *,
    content: PlatformContent,
    packet: ResearchPacket,
) -> None:

    violations: list[str] = []


    public_strings = (
        _public_copy_strings(
            content
        )
    )

    public_text = "\n".join(
        public_strings
    )

    normalized = " ".join(
        public_text
        .lower()
        .split()
    )


    # --------------------------------------------------------
    # 1. EQUIVALENCE / OVERSTATEMENT
    # --------------------------------------------------------

    for phrase in (
        UNSUPPORTED_EQUIVALENCE_PHRASES
    ):

        if phrase in normalized:

            violations.append(
                "Unsupported equivalence/overstatement "
                f"language: '{phrase}'."
            )


    for phrase in (
        ABSOLUTE_PHRASES
    ):

        if phrase in normalized:

            violations.append(
                "Unsupported absolute language: "
                f"'{phrase}'."
            )


    # --------------------------------------------------------
    # 2. NUMERIC DETAIL
    # --------------------------------------------------------

    evidence_numbers = (
        _extract_numeric_atoms(
            _evidence_text(
                packet
            )
        )
    )


    public_numbers = (
        _extract_numeric_atoms(
            public_text
        )
    )


    unsupported_numbers = (
        public_numbers
        - evidence_numbers
    )


    if unsupported_numbers:

        violations.append(
            "Generated copy introduces numeric detail "
            "not present in supplied evidence: "
            + ", ".join(
                sorted(
                    unsupported_numbers,
                    key=lambda value: float(value),
                )
            )
            + "."
        )


        contexts = _numeric_contexts(
            public_text,
            unsupported_numbers,
        )


        for context in contexts[:8]:

            violations.append(
                "Unsupported-number context: "
                f'"{context}"'
            )


    # --------------------------------------------------------
    # 3. STATISTICAL LANGUAGE
    # --------------------------------------------------------

    public_lower = (
        public_text.lower()
    )


    used_claim_text = "\n".join(
        content.claims_used
    ).lower()


    if (
        re.search(
            r"\bsignificantly\b",
            public_lower,
        )
        and "significantly"
        not in used_claim_text
    ):

        violations.append(
            "Generated copy uses 'significantly' "
            "without that wording appearing in a "
            "cited evidence claim."
        )


    # --------------------------------------------------------
    # 4. CERTAINTY FROM UNCERTAIN EVIDENCE
    # --------------------------------------------------------

    if (
        packet.evidence_status
        in {
            "conflicting",
            "limited",
            "insufficient",
        }
    ):

        certainty_phrases = (
            "research proves",
            "science proves",
            "the evidence proves",
            "we know for certain",
            "definitively proves",
        )


        for phrase in (
            certainty_phrases
        ):

            if phrase in normalized:

                violations.append(
                    "Uncertain evidence was converted "
                    "into certainty language: "
                    f"'{phrase}'."
                )


    # --------------------------------------------------------
    # 5. DOWNSTREAM-INFERENCE GUARDS
    # --------------------------------------------------------

    cited_text = used_claim_text


    guarded_inferences = {
        "subsequent sets": (
            "subsequent"
        ),

        "session quality": (
            "session quality"
        ),

        "recovery": (
            "recovery"
        ),

        "across the week": (
            "week"
        ),
    }


    for public_phrase, evidence_marker in (
        guarded_inferences.items()
    ):

        if (
            public_phrase
            in normalized
            and evidence_marker
            not in cited_text
        ):

            violations.append(
                "Generated copy introduces a downstream "
                "inference not stated in cited claims: "
                f"'{public_phrase}'."
            )


    if violations:

        raise ValueError(
            "Evidence-language validation failed:\n- "
            + "\n- ".join(
                violations
            )
        )
