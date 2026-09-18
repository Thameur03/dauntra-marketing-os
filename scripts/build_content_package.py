from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:

    sys.path.insert(
        0,
        str(ROOT),
    )


from app.content_brain.package import (
    build_content_package,
)

from app.db.content_store import (
    ContentStore,
)

from app.db.supabase_rest import (
    SupabaseREST,
)

from app.llm.gemini import (
    GeminiProvider,
)

from contracts.common import (
    ContentFamily,
    Platform,
)

from contracts.research import (
    ResearchPacket,
)


AUTOMATED_PLATFORM_VALUES = [
    Platform.INSTAGRAM.value,
    Platform.TIKTOK.value,
    Platform.X.value,
    Platform.FACEBOOK.value,
]


def parse_args():

    parser = argparse.ArgumentParser(
        description=(
            "Build a DAUNTRA multi-platform "
            "content package from an existing "
            "ResearchPacket."
        )
    )


    parser.add_argument(
        "--research-packet-id",
        required=True,
    )


    parser.add_argument(
        "--family",
        required=True,
        choices=[
            family.value
            for family
            in ContentFamily
        ],
    )


    parser.add_argument(
        "--platform",
        action="append",
        required=True,
        choices=(
            AUTOMATED_PLATFORM_VALUES
        ),
        help=(
            "Repeat for each platform."
        ),
    )


    parser.add_argument(
        "--capability",
        action="append",
        default=[],
    )


    parser.add_argument(
        "--variant-key",
        default="default",
    )


    parser.add_argument(
        "--persist",
        action="store_true",
        help=(
            "Write successful drafts to "
            "content_items. Without this flag "
            "the package is generated but not stored."
        ),
    )


    return parser.parse_args()


def main() -> int:

    args = parse_args()


    print()
    print(
        "=========================================="
    )

    print(
        " DAUNTRA CONTENT PACKAGE"
    )

    print(
        "=========================================="
    )

    print()


    with SupabaseREST() as db:

        rows = db.select(
            "research_packets",

            params={
                "select": (
                    "id,subject_id,status,"
                    "packet_json,prompt_version,model"
                ),

                "id": (
                    "eq."
                    + args.research_packet_id
                ),
            },
        )


        if len(rows) != 1:

            print(
                "ERROR: ResearchPacket not found."
            )

            return 1


        row = rows[0]


        if row[
            "status"
        ] not in {
            "READY",
            "NEEDS_REVIEW",
        }:

            print(
                "ERROR: ResearchPacket status "
                "cannot be used for generation: "
                + str(
                    row[
                        "status"
                    ]
                )
            )

            return 1


        packet = (
            ResearchPacket
            .model_validate(
                row[
                    "packet_json"
                ]
            )
        )


        llm = GeminiProvider()


        store = (
            ContentStore(
                db
            )

            if args.persist

            else None
        )


        package = (
            build_content_package(

                subject_id=str(
                    row[
                        "subject_id"
                    ]
                ),

                research_packet_id=str(
                    row[
                        "id"
                    ]
                ),

                packet=packet,

                content_family=(
                    ContentFamily(
                        args.family
                    )
                ),

                platforms=[
                    Platform(
                        platform
                    )
                    for platform
                    in args.platform
                ],

                capability_ids=(
                    args.capability
                ),

                llm=llm,

                store=store,

                variant_key=(
                    args.variant_key
                ),
            )
        )


    print(
        "Package ID:",
        package.package_id,
    )

    print(
        "Build status:",
        package.build_status,
    )

    print(
        "Human review:",
        (
            "YES"
            if package.requires_human_review
            else "NO"
        ),
    )

    print(
        "Model:",
        package.model,
    )

    print()


    for item in package.items:

        print(
            "------------------------------------------"
        )

        print(
            "Platform:",
            item.platform.value,
        )

        print(
            "Status:",
            item.status,
        )

        print(
            "Generation key:",
            item.generation_key,
        )


        if item.content_item_id:

            print(
                "Content item ID:",
                item.content_item_id,
            )


        if item.database_status:

            print(
                "Database status:",
                item.database_status,
            )


        if item.error:

            print()
            print(
                "ERROR:"
            )

            print(
                item.error
            )


        if item.content is not None:

            print()
            print(
                "CONTENT:"
            )

            print(
                json.dumps(
                    item.content.model_dump(
                        mode="json"
                    ),
                    indent=2,
                    ensure_ascii=False,
                )
            )


        print()


    print(
        "=========================================="
    )

    print(
        " CONTENT PACKAGE COMPLETE"
    )

    print(
        "=========================================="
    )

    print()

    print(
        "Persistence:",
        (
            "ENABLED"
            if args.persist
            else "DISABLED"
        ),
    )

    print(
        "Publishing: DISABLED"
    )


    return (
        0
        if package.build_status
        != "FAILED"
        else 2
    )


if __name__ == "__main__":

    raise SystemExit(
        main()
    )
