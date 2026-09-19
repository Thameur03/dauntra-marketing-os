from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class RenderProfileSpec:
    profile_id: str
    width: int
    height: int
    file_type: str
    mime_type: str
    extension: str


def instagram_feed_profile() -> RenderProfileSpec:

    path = (
        ROOT
        / "config"
        / "platforms.yaml"
    )


    data = yaml.safe_load(
        path.read_text(
            encoding="utf-8"
        )
    )


    carousel = (
        data[
            "platforms"
        ][
            "instagram"
        ][
            "planned_formats"
        ][
            "carousel"
        ]
    )


    if not carousel.get(
        "enabled"
    ):

        raise ValueError(
            "Instagram carousel rendering "
            "is disabled."
        )


    width = int(
        carousel[
            "width"
        ]
    )

    height = int(
        carousel[
            "height"
        ]
    )

    file_type = str(
        carousel[
            "file_type"
        ]
    ).lower()


    if (
        width != 1080
        or height != 1350
    ):

        raise ValueError(
            "INSTAGRAM_FEED must be "
            "1080x1350."
        )


    if file_type not in {
        "jpeg",
        "jpg",
    }:

        raise ValueError(
            "Instagram carousel V1 "
            "must render JPEG."
        )


    return RenderProfileSpec(
        profile_id=(
            "INSTAGRAM_FEED"
        ),

        width=width,

        height=height,

        file_type="jpeg",

        mime_type="image/jpeg",

        extension="jpg",
    )
