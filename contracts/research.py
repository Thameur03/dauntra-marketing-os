from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    model_validator,
)


class ResearchSource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(
        min_length=1,
        max_length=500,
    )

    url: HttpUrl | None = None

    publisher: str | None = Field(
        default=None,
        max_length=300,
    )

    publication_date: str | None = None

    source_type: Literal[
        "study",
        "systematic_review",
        "meta_analysis",
        "guideline",
        "position_stand",
        "official",
        "product_truth",
        "other",
    ]

    notes: str = Field(
        min_length=1,
        max_length=3000,
    )


class ResearchClaim(BaseModel):
    model_config = ConfigDict(extra="forbid")

    claim: str = Field(
        min_length=1,
        max_length=1500,
    )

    sensitivity: Literal[
        "general",
        "training",
        "nutrition",
        "supplement",
        "health",
        "product",
    ]

    source_indexes: list[int] = Field(
        default_factory=list,
    )

    confidence: Literal[
        "high",
        "medium",
        "low",
    ]

    human_review_required: bool = False


class ResearchPacket(BaseModel):
    model_config = ConfigDict(extra="forbid")

    subject: str = Field(
        min_length=3,
        max_length=500,
    )

    evidence_status: Literal[
        "sufficient",
        "limited",
        "conflicting",
        "insufficient",
    ]

    summary: str = Field(
        min_length=20,
        max_length=6000,
    )

    core_finding: str = Field(
        min_length=5,
        max_length=3000,
    )

    important_nuance: str | None = Field(
        default=None,
        max_length=3000,
    )

    limitations: list[str] = Field(
        default_factory=list,
        max_length=20,
    )

    dauntra_relevance: str | None = Field(
        default=None,
        max_length=3000,
    )

    sources: list[ResearchSource] = Field(
        min_length=1,
        max_length=30,
    )

    claims: list[ResearchClaim] = Field(
        min_length=1,
        max_length=30,
    )

    recommended_angles: list[str] = Field(
        min_length=1,
        max_length=10,
    )

    prohibited_angles: list[str] = Field(
        default_factory=list,
        max_length=20,
    )

    requires_human_review: bool = False

    @model_validator(mode="after")
    def validate_claim_sources(self):
        source_count = len(self.sources)

        for claim in self.claims:

            if not claim.source_indexes:
                raise ValueError(
                    "Every research claim must cite at least one source."
                )

            for index in claim.source_indexes:
                if index < 0 or index >= source_count:
                    raise ValueError(
                        f"Claim references invalid source index {index}."
                    )

            if claim.sensitivity in {
                "nutrition",
                "supplement",
                "health",
            }:
                claim.human_review_required = True
                self.requires_human_review = True

        if self.evidence_status in {
            "limited",
            "conflicting",
            "insufficient",
        }:
            self.requires_human_review = True

        return self
