from __future__ import annotations

import json
import os

from pathlib import Path
from typing import Any, TypeVar

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel

from app.llm.schema import (
    sanitize_gemini_schema,
)


T = TypeVar(
    "T",
    bound=BaseModel,
)


ROOT = Path(__file__).resolve().parents[2]

load_dotenv(
    ROOT / ".env"
)


class GeminiProviderError(
    RuntimeError
):
    pass


class GeminiProvider:

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:

        self.api_key = (
            api_key
            or os.getenv(
                "GEMINI_API_KEY"
            )
        )

        self._model = (
            model
            or os.getenv(
                "GEMINI_MODEL",
                "gemini-3.8-flash",
            )
        )


        if not self.api_key:

            raise GeminiProviderError(
                "GEMINI_API_KEY is missing."
            )


    @property
    def model_name(
        self,
    ) -> str:

        return self._model


    def _interaction(
        self,
        *,
        prompt: str,
        schema: dict[str, Any],
        system_instruction: str | None = None,
    ) -> str:

        try:

            with genai.Client(
                api_key=self.api_key
            ) as client:

                interaction = (
                    client
                    .interactions
                    .create(

                        model=self._model,

                        input=prompt,

                        system_instruction=(
                            system_instruction
                            if system_instruction
                            else None
                        ),

                        response_format={
                            "type": "text",
                            "mime_type": (
                                "application/json"
                            ),
                            "schema": schema,
                        },

                        store=False,
                    )
                )


        except Exception as exc:

            raise GeminiProviderError(
                "Gemini interaction failed: "
                f"{exc}"
            ) from exc


        output_text = (
            interaction.output_text
        )


        if not output_text:

            raise GeminiProviderError(
                "Gemini returned no "
                "text output."
            )


        return output_text


    def generate_json(
        self,
        *,
        prompt: str,
        schema: dict[str, Any],
        system_instruction: str | None = None,
    ) -> dict[str, Any]:

        output_text = self._interaction(

            prompt=prompt,

            schema=schema,

            system_instruction=(
                system_instruction
            ),
        )


        try:

            value = json.loads(
                output_text
            )

        except json.JSONDecodeError as exc:

            raise GeminiProviderError(
                "Gemini returned invalid JSON."
            ) from exc


        if not isinstance(
            value,
            dict,
        ):

            raise GeminiProviderError(
                "Expected Gemini to return "
                "a JSON object."
            )


        return value


    def generate_structured(
        self,
        *,
        prompt: str,
        response_model: type[T],
        system_instruction: str | None = None,
    ) -> T:

        raw_schema = (
            response_model
            .model_json_schema()
        )


        schema = (
            sanitize_gemini_schema(
                raw_schema
            )
        )


        output_text = self._interaction(

            prompt=prompt,

            schema=schema,

            system_instruction=(
                system_instruction
            ),
        )


        try:

            # Full application validation happens here.

            return (
                response_model
                .model_validate_json(
                    output_text
                )
            )


        except Exception as exc:

            raise GeminiProviderError(

                "Gemini returned JSON but "
                f"failed local "
                f"{response_model.__name__} "
                f"validation: {exc}"

            ) from exc
