from pydantic import BaseModel, ConfigDict, Field

from contracts.common import ContentFamily, Language, Market


class SubjectCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    subject: str = Field(min_length=3, max_length=500)
    note: str | None = Field(default=None, max_length=4000)

    content_family: ContentFamily | None = None

    market: Market = Market.GLOBAL
    language: Language = Language.EN
