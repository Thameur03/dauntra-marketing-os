from __future__ import annotations

from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from contracts.common import (
    ContentFamily,
    Language,
    Market,
    Platform,
)

from contracts.content import (
    FacebookContent,
    InstagramCarouselContent,
    TikTokVideoContent,
    XContent,
)


AutomatedPlatformContent = (
    InstagramCarouselContent
    | TikTokVideoContent
    | XContent
    | FacebookContent
)


class ContentItemEnvelope(BaseModel):
    """
    Stable JSONB envelope stored in content_items.content_json.

    Keeping generation metadata inside content_json lets V1 use the
    existing database schema while still supporting traceability and
    application-level idempotency.
    """

    model_config = ConfigDict(
        extra="forbid"
    )

    schema_version: Literal[1] = 1

    generation_key: str = Field(
        min_length=64,
        max_length=64,
    )

    variant_key: str = Field(
        min_length=1,
        max_length=120,
    )

    research_prompt_version: str = Field(
        min_length=1,
        max_length=120,
    )

    content_brain_version: str = Field(
        min_length=1,
        max_length=120,
    )

    requires_human_review: bool

    content: AutomatedPlatformContent


class ContentPackageItem(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    platform: Platform

    status: Literal[
        "GENERATED",
        "NEEDS_HUMAN_REVIEW",
        "REUSED",
        "FAILED_VALIDATION",
        "FAILED_GENERATION",
        "FAILED_PERSISTENCE",
        "SKIPPED",
    ]

    database_status: str | None = None

    content_item_id: str | None = None

    generation_key: str = Field(
        min_length=64,
        max_length=64,
    )

    content: AutomatedPlatformContent | None = None

    error: str | None = Field(
        default=None,
        max_length=12000,
    )


class ContentPackage(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    package_id: str = Field(
        min_length=8,
        max_length=80,
    )

    subject_id: str = Field(
        min_length=1,
        max_length=120,
    )

    research_packet_id: str = Field(
        min_length=1,
        max_length=120,
    )

    content_family: ContentFamily

    market: Market = Market.GLOBAL

    language: Language = Language.EN

    model: str = Field(
        min_length=1,
        max_length=200,
    )

    evidence_status: Literal[
        "sufficient",
        "limited",
        "conflicting",
        "insufficient",
    ]

    requires_human_review: bool

    build_status: Literal[
        "COMPLETE",
        "PARTIAL",
        "FAILED",
    ]

    items: list[
        ContentPackageItem
    ] = Field(
        min_length=1,
        max_length=4,
    )
