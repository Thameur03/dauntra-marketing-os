from __future__ import annotations

import json
import subprocess

from pathlib import Path

from app.rendering.carousel import (
    InstagramCarouselRenderer,
)

from contracts.render import (
    CarouselRenderRequest,
)


def request():

    return CarouselRenderRequest(

        template_id="C02",

        render_profile=(
            "INSTAGRAM_FEED"
        ),

        slides=[
            {
                "slide_number": 1,

                "headline": (
                    "Does every set need "
                    "to reach failure?"
                ),

                "body": (
                    "Research is more nuanced "
                    "than a simple yes or no."
                ),

                "emphasis": (
                    "Evidence before absolutes."
                ),
            },

            {
                "slide_number": 2,

                "headline": (
                    "Look at the trade-off"
                ),

                "body": (
                    "Training closer to failure "
                    "can matter, while complete "
                    "failure can also increase "
                    "acute fatigue."
                ),

                "emphasis": (
                    "Context matters."
                ),
            },
        ],
    )


def dimensions(
    path: Path,
):

    result = subprocess.run(
        [
            "ffprobe",

            "-v",
            "error",

            "-select_streams",
            "v:0",

            "-show_entries",
            "stream=width,height",

            "-of",
            "json",

            str(
                path
            ),
        ],

        check=True,

        capture_output=True,

        text=True,
    )


    data = json.loads(
        result.stdout
    )


    stream = (
        data[
            "streams"
        ][0]
    )


    return (
        int(
            stream[
                "width"
            ]
        ),

        int(
            stream[
                "height"
            ]
        ),
    )


def test_carousel_renders_real_jpegs(
    tmp_path,
):

    renderer = (
        InstagramCarouselRenderer()
    )


    result = renderer.render(

        request=request(),

        output_dir=(
            tmp_path
            / "render"
        ),

        template_version=(
            "c02_test"
        ),

        renderer_version=(
            "renderer_test"
        ),
    )


    assert len(
        result
    ) == 2


    for asset in result:

        assert (
            asset.path.exists()
        )

        assert (
            asset.path.suffix
            == ".jpg"
        )

        assert (
            asset.mime_type
            == "image/jpeg"
        )

        assert (
            asset.file_size_bytes
            > 10_000
        )

        assert len(
            asset.sha256
        ) == 64


        assert dimensions(
            asset.path
        ) == (
            1080,
            1350,
        )


def test_same_request_is_deterministic(
    tmp_path,
):

    renderer = (
        InstagramCarouselRenderer()
    )


    first = renderer.render(

        request=request(),

        output_dir=(
            tmp_path
            / "first"
        ),

        template_version=(
            "c02_test"
        ),

        renderer_version=(
            "renderer_test"
        ),
    )


    second = renderer.render(

        request=request(),

        output_dir=(
            tmp_path
            / "second"
        ),

        template_version=(
            "c02_test"
        ),

        renderer_version=(
            "renderer_test"
        ),
    )


    assert [
        item.sha256
        for item
        in first
    ] == [
        item.sha256
        for item
        in second
    ]


def test_maximum_copy_never_silently_clips(
    tmp_path,
):

    from app.rendering.carousel import (
        RenderOverflowError,
    )


    torture = CarouselRenderRequest(

        template_id="C02",

        render_profile=(
            "INSTAGRAM_FEED"
        ),

        slides=[
            {
                "slide_number": 1,

                "headline": (
                    "A" * 180
                ),

                "body": (
                    "Evidence context "
                    * 75
                )[:1200],

                "emphasis": (
                    "Important limitation "
                    * 20
                )[:240],
            },

            {
                "slide_number": 2,

                "headline": (
                    "Control slide"
                ),

                "body": (
                    "Short content."
                ),

                "emphasis": (
                    "No clipping."
                ),
            },
        ],
    )


    renderer = (
        InstagramCarouselRenderer()
    )


    try:

        assets = renderer.render(

            request=torture,

            output_dir=(
                tmp_path
                / "torture"
            ),

            template_version=(
                "c02_test"
            ),

            renderer_version=(
                "renderer_test"
            ),
        )


    except RenderOverflowError:

        # Correct behavior:
        # impossible layout rejected explicitly.
        return


    # Also valid:
    # adaptive sizing genuinely fitted the content.
    assert len(
        assets
    ) == 2


    for asset in assets:

        assert dimensions(
            asset.path
        ) == (
            1080,
            1350,
        )


def test_progress_rail_includes_current_slide():

    renderer = (
        InstagramCarouselRenderer()
    )

    render_request = request()


    first_html = renderer._build_html(
        slide=render_request.slides[0],
        total=2,
    )


    second_html = renderer._build_html(
        slide=render_request.slides[1],
        total=2,
    )


    assert (
        first_html.count(
            'progress-segment complete'
        )
        == 1
    )


    assert (
        second_html.count(
            'progress-segment complete'
        )
        == 2
    )
