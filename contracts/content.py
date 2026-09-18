from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from contracts.common import ContentFamily, Language, Market, Platform


class CarouselSlide(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slide_number: int = Field(ge=1, le=20)
    headline: str | None = Field(default=None, max_length=180)
    body: str = Field(min_length=1, max_length=1200)
    emphasis: str | None = Field(default=None, max_length=240)


class InstagramCarouselContent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    platform: Literal[Platform.INSTAGRAM] = Platform.INSTAGRAM
    format: Literal["carousel"] = "carousel"

    content_family: ContentFamily
    market: Market = Market.GLOBAL
    language: Language = Language.EN

    hook: str = Field(min_length=1, max_length=300)

    slides: list[CarouselSlide] = Field(
        min_length=2,
        max_length=10,
    )

    caption: str = Field(min_length=1, max_length=4000)

    cta: str | None = Field(default=None, max_length=300)

    claims_used: list[str] = Field(default_factory=list)
    capabilities_used: list[str] = Field(default_factory=list)


class VideoChunk(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1, max_length=500)
    duration_ms: int | None = Field(default=None, ge=250, le=30000)


class TikTokVideoContent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    platform: Literal[Platform.TIKTOK] = Platform.TIKTOK
    format: Literal["video"] = "video"

    content_family: ContentFamily
    market: Market = Market.GLOBAL
    language: Language = Language.EN

    hook: str = Field(min_length=1, max_length=300)

    chunks: list[VideoChunk] = Field(
        min_length=1,
        max_length=30,
    )

    caption: str = Field(min_length=1, max_length=3000)

    cta: str | None = Field(default=None, max_length=300)

    claims_used: list[str] = Field(default_factory=list)
    capabilities_used: list[str] = Field(default_factory=list)


class XContent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    platform: Literal[Platform.X] = Platform.X
    format: Literal["text", "thread"]

    content_family: ContentFamily
    market: Market = Market.GLOBAL
    language: Language = Language.EN

    posts: list[str] = Field(min_length=1, max_length=20)

    cta: str | None = Field(default=None, max_length=300)

    claims_used: list[str] = Field(default_factory=list)
    capabilities_used: list[str] = Field(default_factory=list)


class FacebookContent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    platform: Literal[Platform.FACEBOOK] = Platform.FACEBOOK
    format: Literal["text", "image", "video"]

    content_family: ContentFamily
    market: Market = Market.GLOBAL
    language: Language = Language.EN

    body: str = Field(min_length=1, max_length=12000)

    cta: str | None = Field(default=None, max_length=300)

    claims_used: list[str] = Field(default_factory=list)
    capabilities_used: list[str] = Field(default_factory=list)


class RedditContent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    platform: Literal[Platform.REDDIT] = Platform.REDDIT
    format: Literal["discussion"] = "discussion"

    content_family: ContentFamily
    market: Market = Market.GLOBAL
    language: Language = Language.EN

    title: str = Field(min_length=1, max_length=300)
    body: str = Field(min_length=1, max_length=20000)

    subreddit_notes: str | None = Field(default=None, max_length=2000)

    claims_used: list[str] = Field(default_factory=list)
    capabilities_used: list[str] = Field(default_factory=list)
