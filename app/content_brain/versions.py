from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from contracts.common import (
    Platform,
)


ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class GenerationVersions:
    prompt_version: str
    research_prompt_version: str
    content_brain_version: str
    capability_manifest_version: str
    brand_profile_version: str
    content_strategy_version: str


def _yaml(
    path: Path,
) -> dict:

    value = yaml.safe_load(
        path.read_text(
            encoding="utf-8"
        )
    )

    if not isinstance(
        value,
        dict,
    ):
        raise ValueError(
            f"Expected mapping in {path}"
        )

    return value


def _schema_version(
    relative_path: str,
) -> str:

    data = _yaml(
        ROOT
        / relative_path
    )

    value = data.get(
        "schema_version"
    )

    if value is None:

        raise ValueError(
            f"{relative_path} has no schema_version."
        )


    return (
        "schema_v"
        + str(value)
    )


def generation_versions(
    platform: Platform,
) -> GenerationVersions:

    versions = _yaml(
        ROOT
        / "config"
        / "versions.yaml"
    )


    prompts = versions.get(
        "prompts",
        {},
    )


    platform_config = prompts.get(
        platform.value,
        {},
    )


    prompt_version = (
        platform_config.get(
            "version"
        )
    )


    if (
        not prompt_version
        or prompt_version
        == "not_created"
    ):

        raise ValueError(
            "Missing writer prompt version for "
            f"{platform.value}."
        )


    research_prompt_version = (
        prompts
        .get(
            "research",
            {},
        )
        .get(
            "version",
            "unknown",
        )
    )


    content_brain_version = (
        versions
        .get(
            "content_brain",
            {},
        )
        .get(
            "version",
            "unknown",
        )
    )


    return GenerationVersions(

        prompt_version=str(
            prompt_version
        ),

        research_prompt_version=str(
            research_prompt_version
        ),

        content_brain_version=str(
            content_brain_version
        ),

        capability_manifest_version=(
            _schema_version(
                "brand/capability_manifest.yaml"
            )
        ),

        brand_profile_version=(
            _schema_version(
                "brand/brand_profile.yaml"
            )
        ),

        content_strategy_version=(
            _schema_version(
                "brand/content_strategy.yaml"
            )
        ),
    )
