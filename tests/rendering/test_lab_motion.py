from __future__ import annotations

from pathlib import Path

from app.rendering.lab_motion import (
    build_ffmpeg_command,
    build_lab_background,
    render_scene_overlay,
)
from app.rendering.video_models import MotionProject, MotionScene


def make_project() -> MotionProject:
    return MotionProject(
        title="Test project",
        scenes=[
            MotionScene(
                id="a",
                kicker="KICKER",
                headline="TEST HEADLINE",
                body="Body text goes here.",
                emphasis="Emphasis text.",
                duration_s=3.0,
            ),
            MotionScene(
                id="b",
                kicker="SECOND",
                headline="SECOND HEADLINE",
                body="More body text.",
                emphasis="Another emphasis.",
                duration_s=4.0,
            ),
        ],
    )


def test_total_duration() -> None:
    project = make_project()
    assert project.total_duration_s == 7.0


def test_background_is_created(tmp_path: Path) -> None:
    path = tmp_path / "background.png"
    build_lab_background(path, width=1080, height=1920)
    assert path.exists()
    assert path.stat().st_size > 0


def test_overlay_is_created(tmp_path: Path) -> None:
    project = make_project()
    path = tmp_path / "scene.png"
    render_scene_overlay(
        project.scenes[0],
        index=0,
        total=2,
        project=project,
        out_path=path,
    )
    assert path.exists()
    assert path.stat().st_size > 0


def test_ffmpeg_command_contains_output(tmp_path: Path) -> None:
    project = make_project()
    bg = tmp_path / "bg.png"
    scene_paths = [tmp_path / "s1.png", tmp_path / "s2.png"]
    out = tmp_path / "out.mp4"

    command = build_ffmpeg_command(
        background_path=bg,
        scene_paths=scene_paths,
        project=project,
        output_path=out,
    )

    assert command[0] == "ffmpeg"
    assert str(out) in command
