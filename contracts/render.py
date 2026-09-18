from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class RenderCarouselSlide(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slide_number: int = Field(ge=1, le=20)
    headline: str | None = Field(default=None, max_length=180)
    body: str = Field(min_length=1, max_length=1200)
    emphasis: str | None = Field(default=None, max_length=240)


class CarouselRenderRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    template_id: Literal["C01", "C02", "C03", "C04"]

    render_profile: Literal[
        "INSTAGRAM_FEED",
    ]

    slides: list[RenderCarouselSlide] = Field(
        min_length=2,
        max_length=10,
    )


class VideoRenderChunk(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1, max_length=500)
    duration_ms: int | None = Field(default=None, ge=250, le=30000)


class VideoRenderRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    template_id: Literal["V01"]

    render_profile: Literal[
        "VERTICAL_VIDEO",
    ] = "VERTICAL_VIDEO"

    chunks: list[VideoRenderChunk] = Field(
        min_length=1,
        max_length=30,
    )

    audio_mode: Literal[
        "silent",
        "licensed_bed",
        "tts",
    ] = "silent"
