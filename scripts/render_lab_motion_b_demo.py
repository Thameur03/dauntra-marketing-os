from __future__ import annotations

import sys
from pathlib import Path


ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

if str(ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(ROOT),
    )


from app.rendering.lab_motion_b import (
    render_motion_project_b,
)

from app.rendering.video_models import (
    MotionProject,
    MotionScene,
)


def project() -> MotionProject:

    return MotionProject(

        title=(
            "Do you need to hit failure?"
        ),

        scenes=[

            MotionScene(
                id="s1",
                scene_type="intro",
                top_right="RESEARCH",
                kicker="YOUR LATEST READ",
                headline=(
                    "DO YOU NEED TO HIT FAILURE?"
                ),
                body=(
                    "It is widely assumed that maximizing "
                    "hypertrophy requires pushing every set "
                    "until the weight cannot move. The evidence "
                    "shows a more balanced trade-off between "
                    "proximity to failure and acute fatigue."
                ),
                emphasis=(
                    "Proximity matters, but absolute failure "
                    "comes with trade-offs."
                ),
                duration_s=4.2,
            ),

            MotionScene(
                id="s2",
                scene_type="evidence",
                top_right="RESEARCH",
                kicker="WHAT BROAD DATA SHOWS",
                headline=(
                    "NO CLEAR ADVANTAGE TO FULL FAILURE"
                ),
                body=(
                    "Broad meta-analytic evidence indicates "
                    "no statistically significant difference "
                    "in hypertrophy between failure and "
                    "non-failure training across general "
                    "populations."
                ),
                emphasis=(
                    "Stopping short of failure does not "
                    "automatically blunt growth."
                ),
                duration_s=4.8,
            ),

            MotionScene(
                id="s3",
                scene_type="evidence",
                top_right="RESEARCH",
                kicker="WHAT IT MEANS",
                headline=(
                    "PROXIMITY TO FAILURE MATTERS"
                ),
                body=(
                    "An exploratory multilevel meta-regression "
                    "found that muscle hypertrophy increased "
                    "as sets were terminated closer to failure."
                ),
                emphasis=(
                    "Closer proximity to failure generally "
                    "increases the growth stimulus."
                ),
                duration_s=4.4,
            ),

            MotionScene(
                id="s4",
                scene_type="evidence",
                top_right="RESEARCH",
                kicker="THE COST OF FAILURE",
                headline=(
                    "FATIGUE GOES UP FAST"
                ),
                body=(
                    "In trained individuals, similar quadriceps "
                    "hypertrophy was seen when sets stopped "
                    "short of failure, while full failure "
                    "created greater repetition and velocity "
                    "loss."
                ),
                emphasis=(
                    "The last reps may add fatigue faster "
                    "than they add benefit."
                ),
                duration_s=4.6,
            ),

            MotionScene(
                id="s5",
                scene_type="evidence",
                top_right="RESEARCH",
                kicker="WHEN IT MAY HELP",
                headline=(
                    "FAILURE CAN BE USED SELECTIVELY"
                ),
                body=(
                    "Some subgroup analyses and low-volume "
                    "contexts suggest a small benefit for "
                    "training to failure, especially when "
                    "overall volume is limited."
                ),
                emphasis=(
                    "Useful as a tool, not as a universal "
                    "baseline rule."
                ),
                duration_s=4.2,
            ),

            MotionScene(
                id="s6",
                scene_type="takeaway",
                top_right="RESEARCH",
                kicker="ONE NEXT MOVE",
                headline=(
                    "A PRACTICAL TAKEAWAY"
                ),
                body=(
                    "Terminating most sets at 1–2 repetitions "
                    "in reserve provides a strong hypertrophic "
                    "stimulus while reducing acute velocity "
                    "and repetition loss. Full failure can be "
                    "applied selectively rather than as a "
                    "baseline rule."
                ),
                emphasis=(
                    "Train hard enough to stimulate growth "
                    "without unnecessary fatigue."
                ),
                duration_s=5.0,
            ),
        ],
    )


def main() -> None:

    output = Path(
        "/tmp/dauntra-lab-motion-b"
    )


    manifest = (
        render_motion_project_b(
            project(),
            output,
        )
    )


    print()
    print(
        "=========================================="
    )

    print(
        " DAUNTRA LAB MOTION — OPTION B"
    )

    print(
        "=========================================="
    )

    print()

    print(
        "Background system:"
    )

    print(
        "  layered_cinematic_v1"
    )

    print()

    print(
        "Video:"
    )

    print(
        " ",
        manifest[
            "output"
        ],
    )

    print()

    print(
        "Duration:"
    )

    print(
        " ",
        manifest[
            "total_duration_s"
        ],
        "seconds",
    )

    print()

    print(
        "Option A was not modified."
    )


if __name__ == "__main__":
    main()
