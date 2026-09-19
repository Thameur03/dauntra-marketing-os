from __future__ import annotations

import json
import math
import shutil
import subprocess
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from app.rendering.video_models import MotionProject, MotionScene


DARK_BG = (2, 8, 20, 255)
BLUE = (63, 148, 255, 255)
SOFT_BLUE = (90, 170, 255, 180)
DIM_BLUE = (72, 96, 120, 150)
WHITE = (245, 247, 250, 255)
SOFT_WHITE = (228, 234, 241, 235)
PANEL_BLUE = (72, 148, 240, 255)
PANEL_GLOW = (60, 130, 235, 180)
INACTIVE_BAR = (62, 74, 87, 255)


def _font_candidates() -> dict[str, list[str]]:
    return {
        "headline": [
            "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ],
        "body": [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ],
        "mono": [
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ],
    }


def _load_font(kind: str, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in _font_candidates()[kind]:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default()


def _draw_wrapped_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    *,
    xy: tuple[int, int],
    font: ImageFont.ImageFont,
    fill: tuple[int, int, int, int],
    max_width: int,
    line_gap: int = 10,
) -> tuple[int, int, int, int]:
    words = text.split()
    lines: list[str] = []
    current = ""

    for word in words:
        candidate = word if not current else f"{current} {word}"
        bbox = draw.textbbox((0, 0), candidate, font=font)
        width = bbox[2] - bbox[0]
        if width <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word

    if current:
        lines.append(current)

    y = xy[1]
    left = xy[0]
    right = xy[0]
    bottom = y

    for line in lines:
        draw.text((xy[0], y), line, font=font, fill=fill)
        bbox = draw.textbbox((xy[0], y), line, font=font)
        right = max(right, bbox[2])
        bottom = bbox[3]
        y = bbox[3] + line_gap

    return (left, xy[1], right, bottom)


def _draw_progress_bars(
    draw: ImageDraw.ImageDraw,
    *,
    total: int,
    current_index: int,
    width: int,
) -> None:
    left = 72
    top = 56
    gap = 18
    total_width = width - (2 * left)
    bar_width = int((total_width - gap * (total - 1)) / total)
    bar_height = 8

    for idx in range(total):
        x1 = left + idx * (bar_width + gap)
        x2 = x1 + bar_width
        color = BLUE if idx <= current_index else INACTIVE_BAR
        draw.rounded_rectangle((x1, top, x2, top + bar_height), radius=2, fill=color)


def build_lab_background(
    path: Path,
    *,
    width: int,
    height: int,
) -> None:
    """
    Clean DAUNTRA Lab background.

    Intentionally minimal:
    - no full-screen stripe texture
    - deep navy-black base
    - soft blue atmospheric glow
    - restrained trajectory graphics
    - subtle vignette
    """

    # --------------------------------------------------------
    # BASE
    # --------------------------------------------------------

    image = Image.new(
        "RGBA",
        (width, height),
        (1, 7, 17, 255),
    )


    # --------------------------------------------------------
    # SMOOTH BACKGROUND GRADIENT
    # --------------------------------------------------------

    gradient = Image.new(
        "RGBA",
        (width, height),
        (0, 0, 0, 0),
    )

    pixels = gradient.load()


    for y in range(height):

        vertical = (
            y / max(
                1,
                height - 1,
            )
        )


        for x in range(width):

            horizontal = (
                x / max(
                    1,
                    width - 1,
                )
            )


            # Very restrained navy variation.
            r = int(
                1
                + 2 * horizontal
            )

            g = int(
                7
                + 7 * vertical
                + 2 * horizontal
            )

            b = int(
                17
                + 14 * vertical
                + 6 * horizontal
            )


            pixels[
                x,
                y,
            ] = (
                r,
                g,
                b,
                255,
            )


    image = Image.alpha_composite(
        image,
        gradient,
    )


    # --------------------------------------------------------
    # ATMOSPHERIC BLUE GLOWS
    # --------------------------------------------------------

    glow_layer = Image.new(
        "RGBA",
        (width, height),
        (0, 0, 0, 0),
    )

    glow_draw = ImageDraw.Draw(
        glow_layer
    )


    def glow(
        cx: int,
        cy: int,
        radius: int,
        alpha: int,
    ) -> None:

        glow_draw.ellipse(
            (
                cx - radius,
                cy - radius,
                cx + radius,
                cy + radius,
            ),

            fill=(
                35,
                112,
                235,
                alpha,
            ),
        )


    # Main upper-mid atmospheric glow.
    glow(
        int(
            width * 0.68
        ),
        int(
            height * 0.34
        ),
        460,
        55,
    )


    # Secondary lower glow.
    glow(
        int(
            width * 0.28
        ),
        int(
            height * 0.72
        ),
        390,
        28,
    )


    # Small highlight around signal endpoint.
    glow(
        int(
            width * 0.88
        ),
        int(
            height * 0.18
        ),
        190,
        55,
    )


    glow_layer = (
        glow_layer.filter(
            ImageFilter.GaussianBlur(
                105
            )
        )
    )


    image = Image.alpha_composite(
        image,
        glow_layer,
    )


    # --------------------------------------------------------
    # SIGNAL / TRAJECTORY GRAPHICS
    # --------------------------------------------------------

    signal = Image.new(
        "RGBA",
        (width, height),
        (0, 0, 0, 0),
    )

    draw = ImageDraw.Draw(
        signal
    )


    main_points = [
        (
            -70,
            int(
                height * 0.70
            ),
        ),

        (
            int(
                width * 0.27
            ),
            int(
                height * 0.54
            ),
        ),

        (
            int(
                width * 0.54
            ),
            int(
                height * 0.38
            ),
        ),

        (
            int(
                width * 0.77
            ),
            int(
                height * 0.25
            ),
        ),

        (
            int(
                width * 0.96
            ),
            int(
                height * 0.14
            ),
        ),
    ]


    ghost_a = [
        (
            -90,
            int(
                height * 0.67
            ),
        ),

        (
            int(
                width * 0.30
            ),
            int(
                height * 0.50
            ),
        ),

        (
            int(
                width * 0.60
            ),
            int(
                height * 0.32
            ),
        ),

        (
            int(
                width * 0.91
            ),
            int(
                height * 0.15
            ),
        ),
    ]


    ghost_b = [
        (
            -40,
            int(
                height * 0.73
            ),
        ),

        (
            int(
                width * 0.35
            ),
            int(
                height * 0.58
            ),
        ),

        (
            int(
                width * 0.67
            ),
            int(
                height * 0.39
            ),
        ),

        (
            int(
                width * 0.94
            ),
            int(
                height * 0.20
            ),
        ),
    ]


    # Ghost paths — deliberately faint.
    draw.line(
        ghost_a,
        fill=(
            87,
            148,
            220,
            34,
        ),
        width=2,
    )


    draw.line(
        ghost_b,
        fill=(
            40,
            114,
            220,
            48,
        ),
        width=2,
    )


    # Main path.
    draw.line(
        main_points,
        fill=(
            48,
            145,
            255,
            205,
        ),
        width=4,
    )


    # --------------------------------------------------------
    # DASHED COMPARISON PATH
    # --------------------------------------------------------

    dashed_points = [
        (
            10,
            int(
                height * 0.75
            ),
        ),

        (
            int(
                width * 0.34
            ),
            int(
                height * 0.61
            ),
        ),

        (
            int(
                width * 0.62
            ),
            int(
                height * 0.45
            ),
        ),

        (
            int(
                width * 0.91
            ),
            int(
                height * 0.24
            ),
        ),
    ]


    for start_point, end_point in zip(
        dashed_points,
        dashed_points[1:],
    ):

        x1, y1 = start_point
        x2, y2 = end_point

        segments = 26


        for index in range(
            segments
        ):

            if index % 2:
                continue


            t1 = (
                index
                / segments
            )

            t2 = min(
                1.0,
                (
                    index + 0.70
                )
                / segments,
            )


            sx1 = (
                x1
                + (
                    x2 - x1
                )
                * t1
            )

            sy1 = (
                y1
                + (
                    y2 - y1
                )
                * t1
            )

            sx2 = (
                x1
                + (
                    x2 - x1
                )
                * t2
            )

            sy2 = (
                y1
                + (
                    y2 - y1
                )
                * t2
            )


            draw.line(
                (
                    sx1,
                    sy1,
                    sx2,
                    sy2,
                ),

                fill=(
                    45,
                    132,
                    247,
                    105,
                ),

                width=3,
            )


    # --------------------------------------------------------
    # DATA POINTS + SMALL GLOW
    # --------------------------------------------------------

    for point_index in (
        2,
        4,
    ):

        px, py = (
            main_points[
                point_index
            ]
        )


        # Outer halo.
        draw.ellipse(
            (
                px - 27,
                py - 27,
                px + 27,
                py + 27,
            ),

            fill=(
                48,
                145,
                255,
                18,
            ),
        )


        # Inner point.
        draw.ellipse(
            (
                px - 8,
                py - 8,
                px + 8,
                py + 8,
            ),

            fill=(
                83,
                174,
                255,
                235,
            ),
        )


    signal = signal.filter(
        ImageFilter.GaussianBlur(
            0.35
        )
    )


    image = Image.alpha_composite(
        image,
        signal,
    )


    # --------------------------------------------------------
    # VERY SUBTLE DIAGONAL LIGHT WASH
    # --------------------------------------------------------

    wash = Image.new(
        "RGBA",
        (width, height),
        (0, 0, 0, 0),
    )

    wash_draw = ImageDraw.Draw(
        wash
    )


    wash_draw.polygon(
        [
            (
                int(
                    width * 0.20
                ),
                0,
            ),

            (
                int(
                    width * 0.55
                ),
                0,
            ),

            (
                width,
                int(
                    height * 0.62
                ),
            ),

            (
                width,
                int(
                    height * 0.82
                ),
            ),
        ],

        fill=(
            55,
            124,
            230,
            11,
        ),
    )


    wash = wash.filter(
        ImageFilter.GaussianBlur(
            75
        )
    )


    image = Image.alpha_composite(
        image,
        wash,
    )


    # --------------------------------------------------------
    # VIGNETTE
    # --------------------------------------------------------

    vignette = Image.new(
        "RGBA",
        (width, height),
        (0, 0, 0, 0),
    )

    vignette_draw = ImageDraw.Draw(
        vignette
    )


    max_radius = int(
        max(
            width,
            height,
        )
        * 0.72
    )


    center_x = (
        width // 2
    )

    center_y = (
        height // 2
    )


    for radius in range(
        max_radius,
        100,
        -70,
    ):

        progress = (
            1
            - radius
            / max_radius
        )


        alpha = int(
            18
            * progress
        )


        vignette_draw.ellipse(
            (
                center_x - radius,
                center_y - radius,
                center_x + radius,
                center_y + radius,
            ),

            outline=(
                0,
                0,
                0,
                alpha,
            ),

            width=80,
        )


    vignette = vignette.filter(
        ImageFilter.GaussianBlur(
            55
        )
    )


    image = Image.alpha_composite(
        image,
        vignette,
    )


    # --------------------------------------------------------
    # OUTPUT
    # --------------------------------------------------------

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )


    image.convert(
        "RGB"
    ).save(
        path,
        quality=96,
    )


def render_scene_overlay(
    scene: MotionScene,
    *,
    index: int,
    total: int,
    project: MotionProject,
    out_path: Path,
) -> None:
    width = project.width
    height = project.height

    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    font_brand = _load_font("mono", 28)
    font_kicker = _load_font("mono", 26)
    font_headline = _load_font("headline", 88)
    font_body = _load_font("body", 36)
    font_emphasis = _load_font("body", 32)
    font_footer = _load_font("mono", 18)
    font_counter = _load_font("body", 24)

    _draw_progress_bars(draw, total=total, current_index=index, width=width)

    draw.text((72, 108), project.brand, font=font_brand, fill=BLUE)
    top_right_bbox = draw.textbbox((0, 0), scene.top_right, font=font_brand)
    draw.text((width - 72 - (top_right_bbox[2] - top_right_bbox[0]), 108), scene.top_right, font=font_brand, fill=BLUE)

    text_left = 72
    max_text_width = width - 144

    kicker_y = 760 if scene.scene_type == "takeaway" else 760 if scene.scene_type == "evidence" else 900
    headline_y = kicker_y + 55 if scene.kicker else kicker_y

    if scene.kicker:
        draw.text((text_left, kicker_y), scene.kicker, font=font_kicker, fill=BLUE)

    _draw_wrapped_text(
        draw,
        scene.headline,
        xy=(text_left, headline_y),
        font=font_headline,
        fill=WHITE,
        max_width=max_text_width,
        line_gap=8,
    )

    headline_bbox = draw.multiline_textbbox((text_left, headline_y), textwrap.fill(scene.headline, width=16), font=font_headline, spacing=8)
    body_start_y = headline_bbox[3] + 36

    body_box = None
    if scene.body.strip():
        body_box = _draw_wrapped_text(
            draw,
            scene.body,
            xy=(text_left, body_start_y),
            font=font_body,
            fill=SOFT_WHITE,
            max_width=max_text_width,
            line_gap=12,
        )

    if scene.emphasis.strip():
        panel_y = (body_box[3] + 46) if body_box else (body_start_y + 26)

        panel = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        pdraw = ImageDraw.Draw(panel)

        panel_x1 = 72
        panel_x2 = width - 72
        panel_y1 = panel_y
        panel_y2 = panel_y + 132

        pdraw.rounded_rectangle(
            (panel_x1, panel_y1, panel_x2, panel_y2),
            radius=24,
            fill=PANEL_GLOW,
        )
        panel = panel.filter(ImageFilter.GaussianBlur(14))
        image = Image.alpha_composite(image, panel)

        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle(
            (panel_x1, panel_y1, panel_x2, panel_y2),
            radius=24,
            fill=PANEL_BLUE,
        )

        _draw_wrapped_text(
            draw,
            scene.emphasis,
            xy=(panel_x1 + 32, panel_y1 + 28),
            font=font_emphasis,
            fill=WHITE,
            max_width=(panel_x2 - panel_x1 - 64),
            line_gap=6,
        )

    draw.text((72, height - 90), project.footer, font=font_footer, fill=(95, 125, 170, 255))

    counter = f"{index + 1} / {total}"
    counter_bbox = draw.textbbox((0, 0), counter, font=font_counter)
    draw.text((width - 72 - (counter_bbox[2] - counter_bbox[0]), height - 94), counter, font=font_counter, fill=BLUE)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(out_path)


def build_ffmpeg_command(
    *,
    background_path: Path,
    scene_paths: list[Path],
    project: MotionProject,
    output_path: Path,
) -> list[str]:
    total = project.total_duration_s
    fps = project.fps

    command = ["ffmpeg", "-y"]

    command += ["-loop", "1", "-t", str(total), "-i", str(background_path)]

    for scene_path in scene_paths:
        command += ["-loop", "1", "-t", str(total), "-i", str(scene_path)]

    filter_parts: list[str] = []

    filter_parts.append(
        "[0:v]"
        "scale=1120:1990,"
        "crop=1080:1920:"
        "(iw-1080)/2+10*sin(t/4):"
        "(ih-1920)/2+12*cos(t/5),"
        "format=rgba"
        "[bg0]"
    )

    start = 0.0
    for idx, scene in enumerate(project.scenes, start=1):
        end = start + scene.duration_s
        fade_in = start
        fade_out = max(start + 0.01, end - 0.35)

        filter_parts.append(
            f"[{idx}:v]"
            f"format=rgba,"
            f"fade=t=in:st={fade_in:.2f}:d=0.35:alpha=1,"
            f"fade=t=out:st={fade_out:.2f}:d=0.35:alpha=1"
            f"[ov{idx}]"
        )

        previous = f"bg{idx - 1}"
        current = f"bg{idx}"
        filter_parts.append(
            f"[{previous}][ov{idx}]"
            f"overlay=0:0:enable='between(t,{start:.2f},{end:.2f})'"
            f"[{current}]"
        )

        start = end

    final_label = f"bg{len(project.scenes)}"
    filter_parts.append(f"[{final_label}]format=yuv420p[vout]")

    command += [
        "-filter_complex",
        ";".join(filter_parts),
        "-map",
        "[vout]",
        "-r",
        str(fps),
        "-t",
        str(total),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(output_path),
    ]

    return command


def render_motion_project(project: MotionProject, out_dir: Path) -> dict:
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg is required but not installed or not on PATH")

    out_dir.mkdir(parents=True, exist_ok=True)

    background_path = out_dir / "background.png"
    build_lab_background(background_path, width=project.width, height=project.height)

    scene_paths: list[Path] = []
    for index, scene in enumerate(project.scenes):
        scene_path = out_dir / f"scene_{index + 1:02d}.png"
        render_scene_overlay(
            scene,
            index=index,
            total=len(project.scenes),
            project=project,
            out_path=scene_path,
        )
        scene_paths.append(scene_path)

    output_path = out_dir / "lab_motion.mp4"

    command = build_ffmpeg_command(
        background_path=background_path,
        scene_paths=scene_paths,
        project=project,
        output_path=output_path,
    )

    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )

    if completed.returncode != 0:
        raise RuntimeError(
            "ffmpeg render failed.\n\nSTDOUT:\n"
            + completed.stdout
            + "\n\nSTDERR:\n"
            + completed.stderr
        )

    timeline = []
    cursor = 0.0
    for i, scene in enumerate(project.scenes, start=1):
        timeline.append(
            {
                "scene_number": i,
                "id": scene.id,
                "start_s": round(cursor, 2),
                "end_s": round(cursor + scene.duration_s, 2),
                "duration_s": scene.duration_s,
                "headline": scene.headline,
            }
        )
        cursor += scene.duration_s

    manifest = {
        "title": project.title,
        "width": project.width,
        "height": project.height,
        "fps": project.fps,
        "total_duration_s": project.total_duration_s,
        "background": str(background_path),
        "scenes": [str(path) for path in scene_paths],
        "output": str(output_path),
        "timeline": timeline,
    }

    manifest_path = out_dir / "render_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    return manifest
