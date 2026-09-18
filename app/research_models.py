from __future__ import annotations

from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from contracts.research import (
    ResearchClaim,
)


class PubMedSearchPlan(
    BaseModel
):
    model_config = ConfigDict(
        extra="forbid"
    )

    queries: list[str] = Field(
        min_length=1,
        max_length=3,
    )


class EvidenceSynthesis(
    BaseModel
):
    model_config = ConfigDict(
        extra="forbid"
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

    important_nuance: (
        str | None
    ) = None

    limitations: list[str] = Field(
        default_factory=list,
        max_length=20,
    )

    dauntra_relevance: (
        str | None
    ) = None

    claims: list[
        ResearchClaim
    ] = Field(
        min_length=1,
        max_length=30,
    )

    recommended_angles: list[str] = (
        Field(
            min_length=1,
            max_length=10,
        )
    )

    prohibited_angles: list[str] = (
        Field(
            default_factory=list,
            max_length=20,
        )
    )

    requires_human_review: bool = (
        False
    )
