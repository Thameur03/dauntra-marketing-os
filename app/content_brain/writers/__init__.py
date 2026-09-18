from app.content_brain.writers.base import (
    GeneratedContentValidationError,
    PlatformWriter,
)

from app.llm.base import (
    StructuredLLM,
)

from contracts.common import (
    Platform,
)


def instagram_writer(
    llm: StructuredLLM,
) -> PlatformWriter:

    return PlatformWriter(
        llm=llm,
        platform=Platform.INSTAGRAM,
    )


def tiktok_writer(
    llm: StructuredLLM,
) -> PlatformWriter:

    return PlatformWriter(
        llm=llm,
        platform=Platform.TIKTOK,
    )


def x_writer(
    llm: StructuredLLM,
) -> PlatformWriter:

    return PlatformWriter(
        llm=llm,
        platform=Platform.X,
    )


def facebook_writer(
    llm: StructuredLLM,
) -> PlatformWriter:

    return PlatformWriter(
        llm=llm,
        platform=Platform.FACEBOOK,
    )


__all__ = [
    "GeneratedContentValidationError",
    "PlatformWriter",
    "instagram_writer",
    "tiktok_writer",
    "x_writer",
    "facebook_writer",
]
