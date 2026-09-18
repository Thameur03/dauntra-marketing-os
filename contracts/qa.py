from pydantic import BaseModel, ConfigDict, Field

from contracts.common import QAGate, QAResult


class QACheckResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    gate: QAGate
    result: QAResult

    reason_code: str | None = Field(default=None, max_length=150)

    message: str | None = Field(default=None, max_length=3000)

    evidence: dict = Field(default_factory=dict)

    human_review_required: bool = False
