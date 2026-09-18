from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from contracts.common import Platform


class PublicationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    content_item_id: str
    platform: Platform

    scheduled_at: datetime | None = None

    idempotency_key: str = Field(
        min_length=16,
        max_length=200,
    )


class PublicationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str

    provider_request_id: str | None = None
    provider_post_id: str | None = None
    platform_post_url: str | None = None

    error_message: str | None = None
