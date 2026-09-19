from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class MotionScene(BaseModel):
    id: str
    kicker: str = ""
    headline: str
    body: str = ""
    emphasis: str = ""
    top_right: str = "RESEARCH"
    duration_s: float = Field(default=4.5, gt=1.0)
    scene_type: Literal["intro", "evidence", "takeaway"] = "evidence"

    @field_validator("headline")
    @classmethod
    def validate_headline(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("headline cannot be empty")
        return value


class MotionProject(BaseModel):
    title: str
    brand: str = "DAUNTRA // EVIDENCE"
    footer: str = "THE WORK, UNDERSTOOD."
    width: int = 1080
    height: int = 1920
    fps: int = 30
    scenes: list[MotionScene]

    @property
    def total_duration_s(self) -> float:
        return round(sum(scene.duration_s for scene in self.scenes), 3)
