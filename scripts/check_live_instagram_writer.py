from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:

    sys.path.insert(
        0,
        str(ROOT),
    )


from app.content_brain.packet_view import (
    prepare_writer_packet,
)

from app.content_brain.writers import (
    GeneratedContentValidationError,
    instagram_writer,
)

from app.db.supabase_rest import (
    SupabaseREST,
)

from app.llm.gemini import (
    GeminiProvider,
)

from contracts.common import (
    ContentFamily,
)

from contracts.research import (
    ResearchPacket,
)


PACKET_ID = (
    "4d0fecb7-f733-4ddb-94ce-8d25a1acaee5"
)


print()
print("==========================================")
print(" LIVE INSTAGRAM WRITER")
print("==========================================")
print()


# ------------------------------------------------------------
# Load previously validated research packet.
# ------------------------------------------------------------

with SupabaseREST() as db:

    rows = db.select(
        "research_packets",

        params={
            "select": (
                "id,status,model,packet_json"
            ),

            "id": (
                f"eq.{PACKET_ID}"
            ),
        },
    )


if len(rows) != 1:

    print(
        "FAIL: expected exactly one "
        "ResearchPacket."
    )

    raise SystemExit(1)


stored = rows[0]


packet = ResearchPacket.model_validate(
    stored[
        "packet_json"
    ]
)


writer_packet = (
    prepare_writer_packet(
        packet
    )
)


print(
    "Stored packet:"
)

print(
    "  sources:",
    len(
        packet.sources
    ),
)

print(
    "  claims: ",
    len(
        packet.claims
    ),
)


print()

print(
    "Writer packet:"
)

print(
    "  sources:",
    len(
        writer_packet.sources
    ),
)

print(
    "  claims: ",
    len(
        writer_packet.claims
    ),
)

print()


print(
    "Writer-visible sources:"
)


for index, source in enumerate(
    writer_packet.sources
):

    print(
        f"  [{index}] "
        f"{source.title}"
    )


print()

print(
    "Writer-visible claims:"
)


for index, claim in enumerate(
    writer_packet.claims
):

    print(
        f"  [{index}] "
        f"{claim.claim}"
    )

    print(
        "      sources:",
        claim.source_indexes,
    )


print()
print(
    "=========================================="
)

print(
    " STARTING ONE GEMINI REQUEST"
)

print(
    "=========================================="
)

print()


llm = GeminiProvider()


try:

    content = instagram_writer(
        llm
    ).write(

        packet=writer_packet,

        content_family=(
            ContentFamily.C02
        ),

        capability_ids=[],
    )


except GeneratedContentValidationError as exc:

    print(
        "INSTAGRAM WRITER: REJECTED"
    )

    print()

    print(
        "VALIDATION REASONS"
    )

    print(
        "------------------"
    )

    print(
        exc.reason
    )

    print()

    print(
        "REJECTED CANDIDATE"
    )

    print(
        "------------------"
    )

    print(
        json.dumps(
            exc.content.model_dump(
                mode="json"
            ),
            indent=2,
            ensure_ascii=False,
        )
    )

    print()

    print(
        "No content_item was written "
        "to the database."
    )

    raise SystemExit(2)


print(
    "INSTAGRAM WRITER: PASS"
)

print()

print(
    "Model:",
    llm.model_name,
)

print(
    "Platform:",
    content.platform.value,
)

print(
    "Family:",
    content.content_family.value,
)

print(
    "Format:",
    content.format,
)

print()

print(
    "HOOK"
)

print(
    "----"
)

print(
    content.hook
)

print()


print(
    "SLIDES"
)

print(
    "------"
)


for slide in content.slides:

    print(
        f"[{slide.slide_number}]"
    )

    if slide.headline:

        print(
            "Headline:",
            slide.headline,
        )

    print(
        "Body:",
        slide.body,
    )

    if slide.emphasis:

        print(
            "Emphasis:",
            slide.emphasis,
        )

    print()


print(
    "CAPTION"
)

print(
    "-------"
)

print(
    content.caption
)

print()


print(
    "CTA"
)

print(
    "---"
)

print(
    content.cta
    or "(none)"
)

print()


print(
    "CLAIMS USED"
)

print(
    "-----------"
)


for claim in (
    content.claims_used
):

    print(
        "-",
        claim,
    )


print()

print(
    "CAPABILITIES USED"
)

print(
    "-----------------"
)

print(
    content.capabilities_used
)

print()


print(
    "HUMAN REVIEW REQUIRED:"
)

print(
    "YES"
    if writer_packet.requires_human_review
    else "NO"
)

print()


print(
    "=========================================="
)

print(
    " LIVE INSTAGRAM WRITER: PASS"
)

print(
    "=========================================="
)

print()

print(
    "No content_item was written "
    "to the database."
)
