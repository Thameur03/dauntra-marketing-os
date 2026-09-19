from __future__ import annotations

import json
import math
import shutil
import subprocess
from pathlib import Path

from PIL import (
    Image,
    ImageDraw,
    ImageFilter,
)

from app.rendering.lab_motion import (
    render_scene_overlay,
)

from app.rendering.video_models import (
    MotionProject,
)


# ============================================================
# COLORS
# ============================================================

BG_TOP = (
    1,
    6,
    14,
    255,
)

BG_BOTTOM = (
    2,
    14,
    29,
    255,
)

BLUE = (
    47,
    145,
    255,
    255,
)

BLUE_BRIGHT = (
    88,
    177,
    255,
    255,
)


# ============================================================
# HELPERS
# ============================================================

def _vertical_gradient(
    width: int,
    height: int,
) -> Image.Image:

    image = Image.new(
        "RGBA",
        (
            width,
            height,
        ),
        BG_TOP,
    )

    pixels = image.load()


    for y in range(
        height
    ):

        ratio = (
            y
            / max(
                1,
                height - 1,
            )
        )


        r = int(
            BG_TOP[0]
            + (
                BG_BOTTOM[0]
                - BG_TOP[0]
            )
            * ratio
        )

        g = int(
            BG_TOP[1]
            + (
                BG_BOTTOM[1]
                - BG_TOP[1]
            )
            * ratio
        )

        b = int(
            BG_TOP[2]
            + (
                BG_BOTTOM[2]
                - BG_TOP[2]
            )
            * ratio
        )


        for x in range(
            width
        ):

            horizontal = (
                x
                / max(
                    1,
                    width - 1,
                )
            )


            pixels[
                x,
                y,
            ] = (
                r,
                min(
                    255,
                    g
                    + int(
                        horizontal
                        * 2
                    ),
                ),
                min(
                    255,
                    b
                    + int(
                        horizontal
                        * 5
                    ),
                ),
                255,
            )


    return image


def _build_base(
    path: Path,
    *,
    width: int,
    height: int,
) -> None:

    image = _vertical_gradient(
        width,
        height,
    )


    # --------------------------------------------------------
    # VIGNETTE
    # --------------------------------------------------------

    vignette = Image.new(
        "RGBA",
        (
            width,
            height,
        ),
        (
            0,
            0,
            0,
            0,
        ),
    )

    draw = ImageDraw.Draw(
        vignette
    )


    steps = 18

    for index in range(
        steps
    ):

        ratio = (
            index
            / steps
        )


        margin_x = int(
            width
            * ratio
            * 0.24
        )

        margin_y = int(
            height
            * ratio
            * 0.20
        )


        alpha = int(
            11
            * (
                1
                - ratio
            )
        )


        draw.rounded_rectangle(
            (
                margin_x,
                margin_y,
                width
                - margin_x,
                height
                - margin_y,
            ),

            radius=180,

            outline=(
                0,
                0,
                0,
                alpha,
            ),

            width=90,
        )


    vignette = (
        vignette.filter(
            ImageFilter.GaussianBlur(
                65
            )
        )
    )


    image = (
        Image.alpha_composite(
            image,
            vignette,
        )
    )


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


def _build_glow(
    path: Path,
    *,
    size: int,
    color: tuple[
        int,
        int,
        int,
    ],
    strength: int,
) -> None:

    layer = Image.new(
        "RGBA",
        (
            size,
            size,
        ),
        (
            0,
            0,
            0,
            0,
        ),
    )

    draw = ImageDraw.Draw(
        layer
    )


    center = (
        size // 2
    )


    rings = [
        (
            0.43,
            int(
                strength
                * 0.18
            ),
        ),
        (
            0.34,
            int(
                strength
                * 0.28
            ),
        ),
        (
            0.25,
            int(
                strength
                * 0.42
            ),
        ),
        (
            0.16,
            int(
                strength
                * 0.60
            ),
        ),
    ]


    for radius_ratio, alpha in rings:

        radius = int(
            size
            * radius_ratio
        )


        draw.ellipse(
            (
                center
                - radius,
                center
                - radius,
                center
                + radius,
                center
                + radius,
            ),

            fill=(
                color[0],
                color[1],
                color[2],
                alpha,
            ),
        )


    layer = layer.filter(
        ImageFilter.GaussianBlur(
            int(
                size
                * 0.09
            )
        )
    )


    layer.save(
        path
    )


def _build_ribbon(
    path: Path,
    *,
    width: int,
    height: int,
) -> None:

    layer = Image.new(
        "RGBA",
        (
            width,
            height,
        ),
        (
            0,
            0,
            0,
            0,
        ),
    )

    draw = ImageDraw.Draw(
        layer
    )


    draw.polygon(
        [
            (
                -200,
                int(
                    height
                    * 0.68
                ),
            ),

            (
                180,
                int(
                    height
                    * 0.72
                ),
            ),

            (
                width
                + 170,
                int(
                    height
                    * 0.18
                ),
            ),

            (
                width
                - 180,
                int(
                    height
                    * 0.14
                ),
            ),
        ],

        fill=(
            55,
            126,
            235,
            14,
        ),
    )


    layer = layer.filter(
        ImageFilter.GaussianBlur(
            95
        )
    )


    layer.save(
        path
    )


def _build_signal(
    path: Path,
    *,
    width: int,
    height: int,
) -> None:

    layer = Image.new(
        "RGBA",
        (
            width,
            height,
        ),
        (
            0,
            0,
            0,
            0,
        ),
    )

    glow = Image.new(
        "RGBA",
        (
            width,
            height,
        ),
        (
            0,
            0,
            0,
            0,
        ),
    )


    draw = ImageDraw.Draw(
        layer
    )

    glow_draw = ImageDraw.Draw(
        glow
    )


    main = [
        (
            -100,
            int(
                height
                * 0.81
            ),
        ),

        (
            int(
                width
                * 0.28
            ),
            int(
                height
                * 0.62
            ),
        ),

        (
            int(
                width
                * 0.56
            ),
            int(
                height
                * 0.45
            ),
        ),

        (
            int(
                width
                * 0.78
            ),
            int(
                height
                * 0.30
            ),
        ),

        (
            int(
                width
                * 0.98
            ),
            int(
                height
                * 0.16
            ),
        ),
    ]


    ghost_1 = [
        (
            -100,
            int(
                height
                * 0.76
            ),
        ),

        (
            int(
                width
                * 0.31
            ),
            int(
                height
                * 0.58
            ),
        ),

        (
            int(
                width
                * 0.60
            ),
            int(
                height
                * 0.40
            ),
        ),

        (
            int(
                width
                * 0.95
            ),
            int(
                height
                * 0.14
            ),
        ),
    ]


    ghost_2 = [
        (
            -90,
            int(
                height
                * 0.85
            ),
        ),

        (
            int(
                width
                * 0.34
            ),
            int(
                height
                * 0.69
            ),
        ),

        (
            int(
                width
                * 0.69
            ),
            int(
                height
                * 0.47
            ),
        ),

        (
            int(
                width
                * 0.97
            ),
            int(
                height
                * 0.27
            ),
        ),
    ]


    draw.line(
        ghost_1,
        fill=(
            104,
            159,
            221,
            32,
        ),
        width=3,
    )


    draw.line(
        ghost_2,
        fill=(
            47,
            135,
            255,
            42,
        ),
        width=3,
    )


    # --------------------------------------------------------
    # DASHED REFERENCE LINE
    # --------------------------------------------------------

    dashed = [
        (
            -20,
            int(
                height
                * 0.88
            ),
        ),

        (
            int(
                width
                * 0.37
            ),
            int(
                height
                * 0.71
            ),
        ),

        (
            int(
                width
                * 0.68
            ),
            int(
                height
                * 0.51
            ),
        ),

        (
            int(
                width
                * 0.94
            ),
            int(
                height
                * 0.30
            ),
        ),
    ]


    for point_a, point_b in zip(
        dashed,
        dashed[1:],
    ):

        x1, y1 = point_a
        x2, y2 = point_b


        segments = 28


        for index in range(
            segments
        ):

            if index % 2 != 0:
                continue


            t1 = (
                index
                / segments
            )

            t2 = min(
                1.0,
                (
                    index
                    + 0.62
                )
                / segments,
            )


            draw.line(
                (
                    x1
                    + (
                        x2
                        - x1
                    )
                    * t1,

                    y1
                    + (
                        y2
                        - y1
                    )
                    * t1,

                    x1
                    + (
                        x2
                        - x1
                    )
                    * t2,

                    y1
                    + (
                        y2
                        - y1
                    )
                    * t2,
                ),

                fill=(
                    48,
                    141,
                    255,
                    94,
                ),

                width=3,
            )


    # --------------------------------------------------------
    # MAIN SIGNAL
    # --------------------------------------------------------

    glow_draw.line(
        main,
        fill=(
            47,
            145,
            255,
            115,
        ),
        width=15,
    )


    glow = glow.filter(
        ImageFilter.GaussianBlur(
            15
        )
    )


    layer = Image.alpha_composite(
        layer,
        glow,
    )

    draw = ImageDraw.Draw(
        layer
    )


    draw.line(
        main,
        fill=(
            48,
            149,
            255,
            210,
        ),
        width=4,
    )


    # --------------------------------------------------------
    # DATA POINTS
    # --------------------------------------------------------

    for point_index in (
        2,
        4,
    ):

        x, y = (
            main[
                point_index
            ]
        )


        halo = Image.new(
            "RGBA",
            (
                width,
                height,
            ),
            (
                0,
                0,
                0,
                0,
            ),
        )


        halo_draw = (
            ImageDraw.Draw(
                halo
            )
        )


        halo_draw.ellipse(
            (
                x - 32,
                y - 32,
                x + 32,
                y + 32,
            ),

            fill=(
                55,
                150,
                255,
                80,
            ),
        )


        halo = halo.filter(
            ImageFilter.GaussianBlur(
                19
            )
        )


        layer = (
            Image.alpha_composite(
                layer,
                halo,
            )
        )


        draw = ImageDraw.Draw(
            layer
        )


        draw.ellipse(
            (
                x - 8,
                y - 8,
                x + 8,
                y + 8,
            ),

            fill=(
                BLUE_BRIGHT
            ),
        )


    layer.save(
        path
    )


# ============================================================
# BUILD ALL BACKGROUND LAYERS
# ============================================================

def build_background_layers(
    directory: Path,
    *,
    width: int,
    height: int,
) -> dict[
    str,
    Path,
]:

    directory.mkdir(
        parents=True,
        exist_ok=True,
    )


    base = (
        directory
        / "bg_base.jpg"
    )

    glow_primary = (
        directory
        / "bg_glow_primary.png"
    )

    glow_secondary = (
        directory
        / "bg_glow_secondary.png"
    )

    ribbon = (
        directory
        / "bg_ribbon.png"
    )

    signal = (
        directory
        / "bg_signal.png"
    )


    _build_base(
        base,
        width=width,
        height=height,
    )


    _build_glow(
        glow_primary,
        size=1250,
        color=(
            40,
            118,
            235,
        ),
        strength=105,
    )


    _build_glow(
        glow_secondary,
        size=900,
        color=(
            20,
            80,
            185,
        ),
        strength=65,
    )


    _build_ribbon(
        ribbon,
        width=width,
        height=height,
    )


    _build_signal(
        signal,
        width=width,
        height=height,
    )


    return {
        "base": base,
        "glow_primary": (
            glow_primary
        ),
        "glow_secondary": (
            glow_secondary
        ),
        "ribbon": ribbon,
        "signal": signal,
    }


# ============================================================
# FFMPEG
# ============================================================

def build_ffmpeg_command_b(
    *,
    layers: dict[
        str,
        Path,
    ],
    scene_paths: list[
        Path
    ],
    project: MotionProject,
    output_path: Path,
) -> list[
    str
]:

    total = (
        project
        .total_duration_s
    )


    command = [
        "ffmpeg",
        "-y",
    ]


    # --------------------------------------------------------
    # FIVE BACKGROUND INPUTS
    # --------------------------------------------------------

    for key in (
        "base",
        "glow_primary",
        "glow_secondary",
        "ribbon",
        "signal",
    ):

        command += [
            "-loop",
            "1",

            "-t",
            str(
                total
            ),

            "-i",
            str(
                layers[
                    key
                ]
            ),
        ]


    # --------------------------------------------------------
    # TEXT SCENE INPUTS
    # --------------------------------------------------------

    for scene_path in (
        scene_paths
    ):

        command += [
            "-loop",
            "1",

            "-t",
            str(
                total
            ),

            "-i",
            str(
                scene_path
            ),
        ]


    filters: list[
        str
    ] = []


    # --------------------------------------------------------
    # BASE CAMERA DRIFT
    # --------------------------------------------------------

    filters.append(
        "[0:v]"
        "scale=1120:1995,"
        "crop=1080:1920:"
        "20+8*sin(t/7):"
        "37+9*cos(t/8),"
        "format=rgba"
        "[base]"
    )


    # --------------------------------------------------------
    # PRIMARY GLOW
    #
    # Actual independently moving atmosphere.
    # --------------------------------------------------------

    filters.append(
        "[1:v]"
        "format=rgba"
        "[glow1]"
    )


    filters.append(
        "[base][glow1]"
        "overlay="
        "x='-260+55*sin(t*0.19)':"
        "y='180+65*cos(t*0.15)':"
        "format=auto"
        "[bg1]"
    )


    # --------------------------------------------------------
    # SECONDARY GLOW
    # --------------------------------------------------------

    filters.append(
        "[2:v]"
        "format=rgba"
        "[glow2]"
    )


    filters.append(
        "[bg1][glow2]"
        "overlay="
        "x='420+45*cos(t*0.13)':"
        "y='940+75*sin(t*0.11)':"
        "format=auto"
        "[bg2]"
    )


    # --------------------------------------------------------
    # DIAGONAL LIGHT FIELD
    # --------------------------------------------------------

    filters.append(
        "[3:v]"
        "format=rgba"
        "[ribbon]"
    )


    filters.append(
        "[bg2][ribbon]"
        "overlay="
        "x='10+18*sin(t*0.08)':"
        "y='-8+14*cos(t*0.10)':"
        "format=auto"
        "[bg3]"
    )


    # --------------------------------------------------------
    # SIGNAL LAYER
    #
    # Moves independently from the atmosphere.
    # --------------------------------------------------------

    filters.append(
        "[4:v]"
        "format=rgba"
        "[signal]"
    )


    filters.append(
        "[bg3][signal]"
        "overlay="
        "x='-15+14*sin(t*0.17)':"
        "y='35+12*cos(t*0.14)':"
        "format=auto"
        "[bg4]"
    )


    # --------------------------------------------------------
    # TEXT SCENES
    # --------------------------------------------------------

    cursor = 0.0


    for scene_index, scene in enumerate(
        project.scenes
    ):

        input_index = (
            5
            + scene_index
        )


        start = cursor

        end = (
            start
            + scene.duration_s
        )


        fade_in_duration = (
            0.40
        )

        fade_out_duration = (
            0.32
        )


        fade_out_start = max(
            start
            + 0.01,

            end
            - fade_out_duration,
        )


        scene_label = (
            f"scene{scene_index}"
        )


        filters.append(
            f"[{input_index}:v]"
            "format=rgba,"
            f"fade=t=in:"
            f"st={start:.3f}:"
            f"d={fade_in_duration:.3f}:"
            "alpha=1,"
            f"fade=t=out:"
            f"st={fade_out_start:.3f}:"
            f"d={fade_out_duration:.3f}:"
            "alpha=1"
            f"[{scene_label}]"
        )


        previous = (
            "bg4"
            if scene_index == 0
            else (
                f"text{scene_index - 1}"
            )
        )


        output = (
            f"text{scene_index}"
        )


        filters.append(
            f"[{previous}]"
            f"[{scene_label}]"
            "overlay=0:0:"
            f"enable='between("
            f"t,"
            f"{start:.3f},"
            f"{end:.3f}"
            f")'"
            f"[{output}]"
        )


        cursor = end


    final = (
        f"text{len(project.scenes) - 1}"
    )


    filters.append(
        f"[{final}]"
        "format=yuv420p"
        "[vout]"
    )


    command += [
        "-filter_complex",
        ";".join(
            filters
        ),

        "-map",
        "[vout]",

        "-r",
        str(
            project.fps
        ),

        "-t",
        str(
            total
        ),

        "-c:v",
        "libx264",

        "-preset",
        "medium",

        "-crf",
        "18",

        "-pix_fmt",
        "yuv420p",

        "-movflags",
        "+faststart",

        str(
            output_path
        ),
    ]


    return command


# ============================================================
# RENDER
# ============================================================

def render_motion_project_b(
    project: MotionProject,
    out_dir: Path,
) -> dict:

    if (
        shutil.which(
            "ffmpeg"
        )
        is None
    ):

        raise RuntimeError(
            "ffmpeg not found"
        )


    out_dir.mkdir(
        parents=True,
        exist_ok=True,
    )


    layers_dir = (
        out_dir
        / "background_layers"
    )


    layers = (
        build_background_layers(
            layers_dir,
            width=project.width,
            height=project.height,
        )
    )


    scene_paths: list[
        Path
    ] = []


    for index, scene in enumerate(
        project.scenes
    ):

        scene_path = (
            out_dir
            / (
                f"scene_"
                f"{index + 1:02d}"
                ".png"
            )
        )


        render_scene_overlay(
            scene,
            index=index,
            total=len(
                project.scenes
            ),
            project=project,
            out_path=scene_path,
        )


        scene_paths.append(
            scene_path
        )


    output_path = (
        out_dir
        / "lab_motion_b.mp4"
    )


    command = (
        build_ffmpeg_command_b(
            layers=layers,
            scene_paths=scene_paths,
            project=project,
            output_path=output_path,
        )
    )


    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )


    if completed.returncode != 0:

        raise RuntimeError(
            "Option B ffmpeg render failed.\n"
            "\nSTDOUT:\n"
            + completed.stdout
            + "\nSTDERR:\n"
            + completed.stderr
        )


    timeline = []

    cursor = 0.0


    for index, scene in enumerate(
        project.scenes,
        start=1,
    ):

        timeline.append(
            {
                "scene_number": (
                    index
                ),

                "id": (
                    scene.id
                ),

                "start_s": round(
                    cursor,
                    3,
                ),

                "end_s": round(
                    cursor
                    + scene.duration_s,
                    3,
                ),

                "duration_s": (
                    scene.duration_s
                ),

                "headline": (
                    scene.headline
                ),
            }
        )


        cursor += (
            scene.duration_s
        )


    manifest = {
        "variant": (
            "lab_motion_b"
        ),

        "background_system": (
            "layered_cinematic_v1"
        ),

        "title": (
            project.title
        ),

        "width": (
            project.width
        ),

        "height": (
            project.height
        ),

        "fps": (
            project.fps
        ),

        "total_duration_s": (
            project
            .total_duration_s
        ),

        "background_layers": {
            key: str(
                value
            )
            for key, value
            in layers.items()
        },

        "scene_overlays": [
            str(
                path
            )
            for path
            in scene_paths
        ],

        "output": str(
            output_path
        ),

        "timeline": (
            timeline
        ),
    }


    manifest_path = (
        out_dir
        / "render_manifest_b.json"
    )


    manifest_path.write_text(
        json.dumps(
            manifest,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


    return manifest
