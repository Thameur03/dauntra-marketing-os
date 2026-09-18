from __future__ import annotations

from typing import Any, Protocol, TypeVar

from pydantic import BaseModel


T = TypeVar(
    "T",
    bound=BaseModel,
)


class StructuredLLM(
    Protocol
):

    @property
    def model_name(self) -> str:
        ...


    def generate_structured(
        self,
        *,
        prompt: str,
        response_model: type[T],
        system_instruction: str | None = None,
    ) -> T:
        ...


    def generate_json(
        self,
        *,
        prompt: str,
        schema: dict[str, Any],
        system_instruction: str | None = None,
    ) -> dict[str, Any]:
        ...
