from __future__ import annotations

import argparse
import json
import sys

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(ROOT),
    )


from app.db.supabase_rest import (
    SupabaseREST,
)

from app.rendering.carousel import (
    InstagramCarouselRenderer,
)

from contracts.content import (
    InstagramCarouselContent,
)

from contracts.content_package import (
    ContentItemEnvelope,
)

from contracts.render import (
    CarouselRenderRequest,
)


DEFAULT_CONTENT_ITEM_ID = (
    "df53ca56-5bef-44b6-88cd-d2b12b08f667"
)


def parse_args():

    parser = argparse.ArgumentParser(
        description=(
            "Render a persisted DAUNTRA "
            "Instagram carousel content item."
        )
    )


    parser.add_argument(
        "--content-item-id",
        default=(
            DEFAULT_CONTENT_ITEM_ID
        ),
    )


    parser.add_argument(
        "--output-dir",
        default=None,
    )


    return parser.parse_args()


def versions():

    path = (
        ROOT
        / "config"
        / "versions.yaml"
    )


    data = yaml.safe_load(
        path.read_text(
            encoding="utf-8"
        )
    )


    template_version = (
        data[
            "templates"
        ][
            "C02"
        ][
            "version"
        ]
    )


    renderer_version = (
        data[
            "renderer"
        ][
            "version"
        ]
    )


    return (
        str(
            template_version
        ),
        str(
            renderer_version
        ),
    )


def main() -> int:

    args = parse_args()


    output_dir = (

        Path(
            args.output_dir
        )

        if args.output_dir

        else (
            Path(
                "/tmp"
            )
            / "dauntra-render"
            / args.content_item_id
        )
    )


    with SupabaseREST() as db:

        rows = db.select(
            "content_items",

            params={
                "select": (
                    "id,status,platform,format,"
                    "content_family,content_json"
                ),

                "id": (
                    "eq."
                    + args.content_item_id
                ),
            },
        )


    if len(rows) != 1:

        print(
            "ERROR: expected exactly one "
            "content_item."
        )

        return 1


    row = rows[0]


    if (
        row[
            "platform"
        ]
        != "instagram"
    ):

        print(
            "ERROR: content item is not "
            "Instagram."
        )

        return 2


    if (
        row[
            "format"
        ]
        != "carousel"
    ):

        print(
            "ERROR: content item is not "
            "a carousel."
        )

        return 3


    envelope = (
        ContentItemEnvelope
        .model_validate(
            row[
                "content_json"
            ]
        )
    )


    content = envelope.content


    if not isinstance(
        content,
        InstagramCarouselContent,
    ):

        print(
            "ERROR: envelope content is not "
            "InstagramCarouselContent."
        )

        return 4


    request = (
        CarouselRenderRequest(

            template_id=(
                content
                .content_family
                .value
            ),

            render_profile=(
                "INSTAGRAM_FEED"
            ),

            slides=[
                {
                    "slide_number": (
                        slide.slide_number
                    ),

                    "headline": (
                        slide.headline
                    ),

                    "body": (
                        slide.body
                    ),

                    "emphasis": (
                        slide.emphasis
                    ),
                }

                for slide
                in content.slides
            ],
        )
    )


    (
        template_version,
        renderer_version,
    ) = versions()


    renderer = (
        InstagramCarouselRenderer()
    )


    print()
    print(
        "=========================================="
    )
    print(
        " INSTAGRAM CAROUSEL RENDER"
    )
    print(
        "=========================================="
    )
    print()

    print(
        "Content item:",
        row[
            "id"
        ],
    )

    print(
        "Content status:",
        row[
            "status"
        ],
    )

    print(
        "Slides:",
        len(
            request.slides
        ),
    )

    print(
        "Template:",
        request.template_id,
        template_version,
    )

    print(
        "Renderer:",
        renderer_version,
    )

    print(
        "Output:",
        output_dir,
    )

    print()


    rendered = renderer.render(

        request=request,

        output_dir=(
            output_dir
        ),

        template_version=(
            template_version
        ),

        renderer_version=(
            renderer_version
        ),
    )


    manifest = {
        "content_item_id": (
            row[
                "id"
            ]
        ),

        "render_profile": (
            "INSTAGRAM_FEED"
        ),

        "template_id": (
            request.template_id
        ),

        "template_version": (
            template_version
        ),

        "renderer_version": (
            renderer_version
        ),

        "assets": [
            {
                "slide_number": (
                    item.slide_number
                ),

                "filename": (
                    item.path.name
                ),

                "mime_type": (
                    item.mime_type
                ),

                "width": (
                    item.width
                ),

                "height": (
                    item.height
                ),

                "file_size_bytes": (
                    item.file_size_bytes
                ),

                "sha256": (
                    item.sha256
                ),
            }

            for item
            in rendered
        ],
    }


    manifest_path = (
        output_dir
        / "render_manifest.json"
    )


    manifest_path.write_text(
        json.dumps(
            manifest,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",

        encoding="utf-8",
    )


    for item in rendered:

        print(
            f"Slide {item.slide_number}:"
        )

        print(
            "  path:  ",
            item.path,
        )

        print(
            "  size:  ",
            f"{item.width}x{item.height}",
        )

        print(
            "  bytes: ",
            item.file_size_bytes,
        )

        print(
            "  sha256:",
            item.sha256,
        )


    print()
    print(
        "Manifest:",
        manifest_path,
    )

    print()

    print(
        "=========================================="
    )
    print(
        " RENDER: PASS"
    )
    print(
        "=========================================="
    )

    print()

    print(
        "Database writes: 0"
    )

    print(
        "Storage uploads: 0"
    )

    print(
        "Publishing: DISABLED"
    )


    return 0


if __name__ == "__main__":

    raise SystemExit(
        main()
    )
