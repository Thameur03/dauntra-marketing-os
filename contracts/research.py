from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class ResearchSource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=500)
    url: HttpUrl | None = None

    publisher: str | None = Field(default=None, max_length=300)
    publication_date: str | None = None

    source_type: Literal[
        "study",
        "systematic_review",
        "guideline",
        "official",
        "product_truth",
        "other",
    ]

    notes: str = Field(min_length=1, max_length=3000)


class ResearchClaim(BaseModel):
    model_config = ConfigDict(extra="forbid")

    claim: str = Field(min_length=1, max_length=1500)

    sensitivity: Literal[
        "general",
        "training",
        "nutrition",
        "supplement",
        "health",
        "product",
    ]

    source_indexes: list[int] = Field(default_factory=list)

    confidence: Literal[
        "high",
        "medium",
        "low",
    ]

    human_review_required: bool = False


class ResearchPacket(BaseModel):
    model_config = ConfigDict(extra="forbid")

    subject: str = Field(min_length=3, max_length=500)

    summary: str = Field(min_length=20, max_length=6000)

    core_finding: str = Field(min_length=5, max_length=3000)

    important_nuance: str | None = Field(default=None, max_length=3000)

    dauntra_relevance: str | None = Field(default=None, max_length=3000)

    sources: list[ResearchSource] = Field(min_length=1)

    claims: list[ResearchClaim] = Field(min_length=1)

    recommended_angles: list[str] = Field(
        min_length=1,
        max_length=10,
    )

    prohibited_angles: list[str] = Field(default_factory=list)

    requires_human_review: bool = False
