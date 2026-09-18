from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class MetricSnapshotInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    impressions: int | None = Field(default=None, ge=0)
    reach: int | None = Field(default=None, ge=0)
    views: int | None = Field(default=None, ge=0)

    likes: int | None = Field(default=None, ge=0)
    comments: int | None = Field(default=None, ge=0)
    shares: int | None = Field(default=None, ge=0)
    saves: int | None = Field(default=None, ge=0)

    watch_time_ms: int | None = Field(default=None, ge=0)
    average_watch_time_ms: int | None = Field(default=None, ge=0)

    completion_rate: float | None = Field(
        default=None,
        ge=0,
        le=1,
    )

    profile_visits: int | None = Field(default=None, ge=0)
    followers_gained: int | None = Field(default=None, ge=0)

    raw_metrics: dict = Field(default_factory=dict)

    captured_at: datetime


class ConversionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    conversion_id: str = Field(min_length=1, max_length=300)

    conversion_type: Literal[
        "WAITLIST_SIGNUP",
        "INSTALL",
        "TRIAL",
        "SUBSCRIPTION",
    ]

    qualified: bool = False

    visitor_id: str | None = Field(default=None, max_length=500)

    first_touch_click_id: str | None = None
    last_touch_click_id: str | None = None

    metadata: dict = Field(default_factory=dict)

    converted_at: datetime
