from __future__ import annotations

from pathlib import Path

from app.rendering.lab_motion_b import (
    build_background_layers,
    build_ffmpeg_command_b,
)

from app.rendering.video_models import (
    MotionProject,
    MotionScene,
)


def project() -> MotionProject:

    return MotionProject(

        title="B test",

        scenes=[
            MotionScene(
                id="a",
                headline="FIRST SCENE",
                body="Test body.",
                duration_s=3.0,
            ),

            MotionScene(
                id="b",
                headline="SECOND SCENE",
                body="Second body.",
                duration_s=3.0,
            ),
        ],
    )


def test_builds_independent_background_layers(
    tmp_path: Path,
):

    layers = build_background_layers(

        tmp_path
        / "layers",

        width=1080,
        height=1920,
    )


    assert set(
        layers
    ) == {
        "base",
        "glow_primary",
        "glow_secondary",
        "ribbon",
        "signal",
    }


    for path in layers.values():

        assert path.exists()

        assert (
            path.stat().st_size
            > 0
        )


def test_option_b_command_animates_layers(
    tmp_path: Path,
):

    p = project()


    layers = build_background_layers(

        tmp_path
        / "layers",

        width=p.width,
        height=p.height,
    )


    scenes = [
        tmp_path
        / "scene_01.png",

        tmp_path
        / "scene_02.png",
    ]


    output = (
        tmp_path
        / "out.mp4"
    )


    command = build_ffmpeg_command_b(

        layers=layers,

        scene_paths=scenes,

        project=p,

        output_path=output,
    )


    joined = " ".join(
        command
    )


    assert (
        "sin(t"
        in joined
    )

    assert (
        "cos(t"
        in joined
    )

    assert (
        "libx264"
        in joined
    )

    assert str(
        output
    ) in command
