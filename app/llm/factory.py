from __future__ import annotations

import os

from app.llm.gemini import (
    GeminiProvider,
)


def get_llm_provider():

    provider = os.getenv(
        "LLM_PROVIDER",
        "gemini",
    ).lower()


    if provider == "gemini":
        return GeminiProvider()


    raise ValueError(
        "Unsupported LLM provider: "
        f"{provider}"
    )
