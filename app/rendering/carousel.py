from __future__ import annotations

import hashlib
import html
import shutil
import subprocess

from dataclasses import dataclass
from pathlib import Path

from playwright.sync_api import (
    sync_playwright,
)

from app.rendering.profiles import (
    instagram_feed_profile,
)

from contracts.render import (
    CarouselRenderRequest,
    RenderCarouselSlide,
)


ROOT = Path(__file__).resolve().parents[2]


class RenderError(
    RuntimeError
):
    pass


class RenderOverflowError(
    RenderError
):
    pass


@dataclass(frozen=True)
class RenderedCarouselSlide:

    slide_number: int

    path: Path

    mime_type: str

    width: int

    height: int

    file_size_bytes: int

    sha256: str

    render_profile: str

    template_id: str

    template_version: str

    renderer_version: str


def _sha256(
    path: Path,
) -> str:

    digest = hashlib.sha256()


    with path.open(
        "rb"
    ) as handle:

        for chunk in iter(
            lambda: handle.read(
                1024 * 1024
            ),
            b"",
        ):

            digest.update(
                chunk
            )


    return digest.hexdigest()


def _headline_size(
    text: str,
) -> int:

    length = len(
        text.strip()
    )


    if length <= 26:
        return 92

    if length <= 42:
        return 84

    if length <= 62:
        return 74

    if length <= 84:
        return 64

    return 56


def _body_size(
    text: str,
) -> int:

    length = len(
        text.strip()
    )


    if length <= 170:
        return 35

    if length <= 280:
        return 32

    if length <= 420:
        return 29

    if length <= 650:
        return 27

    return 25


def _emphasis_size(
    text: str | None,
) -> int:

    if not text:
        return 30


    length = len(
        text.strip()
    )


    if length <= 90:
        return 31

    if length <= 150:
        return 28

    return 25


class InstagramCarouselRenderer:

    def __init__(
        self,
        *,
        chromium_path: str | None = None,
        ffmpeg_path: str | None = None,
        template_path: Path | None = None,
    ) -> None:

        self.profile = (
            instagram_feed_profile()
        )


        self.chromium_path = (
            chromium_path
            or shutil.which(
                "chromium"
            )
            or shutil.which(
                "chromium-browser"
            )
            or shutil.which(
                "google-chrome"
            )
        )


        self.ffmpeg_path = (
            ffmpeg_path
            or shutil.which(
                "ffmpeg"
            )
        )


        self.template_path = (
            template_path
            or ROOT
            / "templates"
            / "rendering"
            / "instagram_c02_lab_v1.html"
        )


        if not self.chromium_path:

            raise RenderError(
                "Chromium executable not found."
            )


        if not self.ffmpeg_path:

            raise RenderError(
                "ffmpeg executable not found."
            )


        if not self.template_path.exists():

            raise RenderError(
                "Carousel template not found: "
                + str(
                    self.template_path
                )
            )


        self.template = (
            self.template_path
            .read_text(
                encoding="utf-8"
            )
        )


    def _build_html(
        self,
        *,
        slide: RenderCarouselSlide,
        total: int,
    ) -> str:

        headline = (
            slide.headline
            or ""
        )


        emphasis = (
            slide.emphasis
            or ""
        )


        if slide.slide_number == 1:

            slide_class = (
                "slide-opening"
            )

            kicker = (
                "YOUR LATEST READ"
            )


        elif slide.slide_number == total:

            slide_class = (
                "slide-final"
            )

            kicker = (
                "ONE NEXT MOVE"
            )


        else:

            slide_class = (
                "slide-evidence"
            )

            kicker = (
                "WHAT IT MEANS"
            )


        progress_segments = (
            "\n".join(
                (
                    '<div class="progress-segment '
                    + (
                        "complete"
                        if index <= slide.slide_number
                        else "pending"
                    )
                    + '"></div>'
                )

                for index
                in range(
                    1,
                    total + 1,
                )
            )
        )


        values = {
            "SLIDE_CLASS": (
                slide_class
            ),

            "KICKER": html.escape(
                kicker
            ),

            "PROGRESS_SEGMENTS": (
                progress_segments
            ),

            "HEADLINE": html.escape(
                headline
            ),

            "BODY": html.escape(
                slide.body
            ),

            "EMPHASIS": html.escape(
                emphasis
            ),

            "EMPHASIS_CLASS": (
                ""
                if emphasis
                else "hidden"
            ),

            "SLIDE": str(
                slide.slide_number
            ),

            "TOTAL": str(
                total
            ),

            "HEADLINE_SIZE": str(
                _headline_size(
                    headline
                )
            ),

            "BODY_SIZE": str(
                _body_size(
                    slide.body
                )
            ),

            "EMPHASIS_SIZE": str(
                _emphasis_size(
                    slide.emphasis
                )
            ),
        }


        rendered = (
            self.template
        )


        for key, value in (
            values.items()
        ):

            rendered = rendered.replace(
                "{{"
                + key
                + "}}",
                value,
            )


        return rendered


    @staticmethod
    def _assert_no_overflow(
        page,
        *,
        slide_number: int,
    ) -> None:
        """
        Detect real clipping/geometry overflow.

        Do not compare scrollHeight/clientHeight on individual
        text nodes: Chromium font metrics can differ by a
        fractional pixel even when text is completely visible.

        Instead:
        1. verify the constrained #content container itself is
           not scrolling/clipping;
        2. verify visible text blocks remain inside the content
           rectangle with a small sub-pixel tolerance.
        """

        result = page.evaluate(
            """
            () => {
                const tolerance = 2;

                const canvas =
                    document.querySelector(
                        '#canvas'
                    );

                const content =
                    document.querySelector(
                        '#content'
                    );

                const headline =
                    document.querySelector(
                        '#headline'
                    );

                const body =
                    document.querySelector(
                        '#body'
                    );

                const emphasis =
                    document.querySelector(
                        '#emphasis-wrapper'
                    );


                if (!canvas || !content) {

                    return {
                        error:
                            'required render nodes missing'
                    };
                }


                const contentRect =
                    content.getBoundingClientRect();

                const canvasRect =
                    canvas.getBoundingClientRect();


                const containerOverflow = (
                    content.scrollHeight >
                    content.clientHeight + tolerance
                    ||
                    content.scrollWidth >
                    content.clientWidth + tolerance
                );


                const outside = (element) => {

                    if (!element) {
                        return false;
                    }


                    if (
                        element.classList
                        &&
                        element.classList
                            .contains('hidden')
                    ) {
                        return false;
                    }


                    const style =
                        window.getComputedStyle(
                            element
                        );


                    if (
                        style.display === 'none'
                        ||
                        style.visibility === 'hidden'
                    ) {
                        return false;
                    }


                    const rect =
                        element.getBoundingClientRect();


                    return (
                        rect.left <
                        contentRect.left - tolerance
                        ||
                        rect.right >
                        contentRect.right + tolerance
                        ||
                        rect.top <
                        contentRect.top - tolerance
                        ||
                        rect.bottom >
                        contentRect.bottom + tolerance
                    );
                };


                const canvasOverflow = (
                    contentRect.left <
                    canvasRect.left - tolerance
                    ||
                    contentRect.right >
                    canvasRect.right + tolerance
                    ||
                    contentRect.top <
                    canvasRect.top - tolerance
                    ||
                    contentRect.bottom >
                    canvasRect.bottom + tolerance
                );


                return {
                    container:
                        containerOverflow,

                    canvas:
                        canvasOverflow,

                    headline:
                        outside(headline),

                    body:
                        outside(body),

                    emphasis:
                        outside(emphasis),

                    metrics: {
                        contentClientHeight:
                            content.clientHeight,

                        contentScrollHeight:
                            content.scrollHeight,

                        contentClientWidth:
                            content.clientWidth,

                        contentScrollWidth:
                            content.scrollWidth,

                        contentTop:
                            contentRect.top,

                        contentBottom:
                            contentRect.bottom
                    }
                };
            }
            """
        )


        if "error" in result:

            raise RenderError(
                "Slide "
                + str(
                    slide_number
                )
                + ": "
                + result[
                    "error"
                ]
            )


        offenders = [
            name
            for name in (
                "container",
                "canvas",
                "headline",
                "body",
                "emphasis",
            )
            if result.get(
                name
            )
        ]


        if offenders:

            raise RenderOverflowError(
                "Slide "
                + str(
                    slide_number
                )
                + " overflowed: "
                + ", ".join(
                    offenders
                )
                + " | metrics="
                + str(
                    result.get(
                        "metrics",
                        {}
                    )
                )
            )


    def render(
        self,
        *,
        request: CarouselRenderRequest,
        output_dir: Path,
        template_version: str,
        renderer_version: str,
    ) -> list[
        RenderedCarouselSlide
    ]:

        if (
            request.render_profile
            != "INSTAGRAM_FEED"
        ):

            raise RenderError(
                "Unsupported render profile: "
                + request.render_profile
            )


        if (
            request.template_id
            != "C02"
        ):

            raise RenderError(
                "Section 4A currently supports "
                "C02 only."
            )


        expected_numbers = list(
            range(
                1,
                len(
                    request.slides
                )
                + 1,
            )
        )


        actual_numbers = [
            slide.slide_number
            for slide
            in request.slides
        ]


        if (
            actual_numbers
            != expected_numbers
        ):

            raise RenderError(
                "Carousel slide numbers "
                "must be sequential."
            )


        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )


        results: list[
            RenderedCarouselSlide
        ] = []


        with sync_playwright() as p:

            browser = (
                p.chromium.launch(

                    executable_path=(
                        self.chromium_path
                    ),

                    headless=True,

                    args=[
                        "--disable-gpu",
                        "--disable-dev-shm-usage",
                        "--font-render-hinting=none",
                    ],
                )
            )


            try:

                page = browser.new_page(

                    viewport={
                        "width": (
                            self.profile.width
                        ),

                        "height": (
                            self.profile.height
                        ),
                    },

                    device_scale_factor=1,
                )


                for slide in (
                    request.slides
                ):

                    slide_html = (
                        self._build_html(

                            slide=slide,

                            total=len(
                                request.slides
                            ),
                        )
                    )


                    page.set_content(
                        slide_html,
                        wait_until="load",
                    )


                    page.evaluate(
                        """
                        async () => {
                            await document.fonts.ready;
                        }
                        """
                    )


                    self._assert_no_overflow(
                        page,
                        slide_number=(
                            slide.slide_number
                        ),
                    )


                    png_path = (
                        output_dir
                        / (
                            "_slide_"
                            f"{slide.slide_number:02d}"
                            ".png"
                        )
                    )


                    jpg_path = (
                        output_dir
                        / (
                            "slide_"
                            f"{slide.slide_number:02d}"
                            ".jpg"
                        )
                    )


                    page.screenshot(

                        path=str(
                            png_path
                        ),

                        type="png",

                        full_page=False,
                    )


                    subprocess.run(
                        [
                            self.ffmpeg_path,

                            "-y",

                            "-hide_banner",

                            "-loglevel",
                            "error",

                            "-i",
                            str(
                                png_path
                            ),

                            "-frames:v",
                            "1",

                            "-q:v",
                            "2",

                            str(
                                jpg_path
                            ),
                        ],

                        check=True,
                    )


                    png_path.unlink(
                        missing_ok=True
                    )


                    if not jpg_path.exists():

                        raise RenderError(
                            "JPEG was not produced."
                        )


                    results.append(

                        RenderedCarouselSlide(

                            slide_number=(
                                slide.slide_number
                            ),

                            path=jpg_path,

                            mime_type=(
                                self.profile
                                .mime_type
                            ),

                            width=(
                                self.profile.width
                            ),

                            height=(
                                self.profile.height
                            ),

                            file_size_bytes=(
                                jpg_path
                                .stat()
                                .st_size
                            ),

                            sha256=_sha256(
                                jpg_path
                            ),

                            render_profile=(
                                self.profile
                                .profile_id
                            ),

                            template_id=(
                                request.template_id
                            ),

                            template_version=(
                                template_version
                            ),

                            renderer_version=(
                                renderer_version
                            ),
                        )
                    )


            finally:

                browser.close()


        return results
