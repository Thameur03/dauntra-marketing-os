from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]


def load_yaml(relative_path: str) -> dict[str, Any]:
    path = ROOT / relative_path

    if not path.exists():
        raise FileNotFoundError(
            f"Required configuration file not found: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8",
    ) as handle:
        data = yaml.safe_load(handle)

    if not isinstance(data, dict):
        raise ValueError(
            f"Expected YAML object in {path}"
        )

    return data


def load_product_truth() -> dict[str, Any]:
    return load_yaml(
        "brand/product_truth.yaml"
    )


def load_capability_manifest() -> dict[str, Any]:
    return load_yaml(
        "brand/capability_manifest.yaml"
    )


def load_brand_profile() -> dict[str, Any]:
    return load_yaml(
        "brand/brand_profile.yaml"
    )


def load_audience_profile() -> dict[str, Any]:
    return load_yaml(
        "brand/audience_profile.yaml"
    )


def load_content_strategy() -> dict[str, Any]:
    return load_yaml(
        "brand/content_strategy.yaml"
    )
