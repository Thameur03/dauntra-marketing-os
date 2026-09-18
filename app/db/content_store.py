from __future__ import annotations

from dataclasses import dataclass

from app.db.supabase_rest import (
    SupabaseREST,
)

from app.content_brain.versions import (
    GenerationVersions,
)

from contracts.common import (
    ContentFamily,
    Platform,
)

from contracts.content_package import (
    ContentItemEnvelope,
)


REUSABLE_STATUSES = {
    "GENERATED",
    "NEEDS_HUMAN_REVIEW",
    "QA_PENDING",
    "APPROVED",
    "READY_TO_PUBLISH",
    "SCHEDULED",
    "PUBLISHED",
}


@dataclass(frozen=True)
class StoredContentItem:
    content_item_id: str
    database_status: str
    envelope: ContentItemEnvelope


class ContentStore:

    def __init__(
        self,
        db: SupabaseREST,
    ) -> None:

        self.db = db


    def find_existing(
        self,
        *,
        subject_id: str,
        research_packet_id: str,
        platform: Platform,
        content_family: ContentFamily,
        generation_key: str,
    ) -> StoredContentItem | None:

        rows = self.db.select(
            "content_items",

            params={
                "select": (
                    "id,status,content_json"
                ),

                "subject_id": (
                    f"eq.{subject_id}"
                ),

                "research_packet_id": (
                    f"eq.{research_packet_id}"
                ),

                "platform": (
                    f"eq.{platform.value}"
                ),

                "content_family": (
                    f"eq.{content_family.value}"
                ),

                "limit": "100",
            },
        )


        for row in rows:

            if (
                row.get(
                    "status"
                )
                not in REUSABLE_STATUSES
            ):

                continue


            raw = row.get(
                "content_json"
            )


            if not isinstance(
                raw,
                dict,
            ):

                continue


            try:

                envelope = (
                    ContentItemEnvelope
                    .model_validate(
                        raw
                    )
                )

            except Exception:

                # Old smoke-test or pre-envelope content item.
                continue


            if (
                envelope.generation_key
                != generation_key
            ):

                continue


            return StoredContentItem(
                content_item_id=str(
                    row["id"]
                ),

                database_status=str(
                    row["status"]
                ),

                envelope=envelope,
            )


        return None


    def save(
        self,
        *,
        subject_id: str,
        research_packet_id: str,
        envelope: ContentItemEnvelope,
        model: str,
        versions: GenerationVersions,
    ) -> StoredContentItem:

        content = envelope.content


        status = (
            "NEEDS_HUMAN_REVIEW"

            if envelope.requires_human_review

            else "GENERATED"
        )


        payload = {
            "subject_id": (
                subject_id
            ),

            "research_packet_id": (
                research_packet_id
            ),

            "content_test_id": None,

            "variant_parent_id": None,

            "platform": (
                content.platform.value
            ),

            "format": (
                content.format
            ),

            "content_family": (
                content.content_family.value
            ),

            "market": (
                content.market.value
            ),

            "language": (
                content.language.value
            ),

            "timezone_window": None,

            "status": status,

            "content_json": (
                envelope.model_dump(
                    mode="json"
                )
            ),

            "prompt_version": (
                versions.prompt_version
            ),

            "model": model,

            "capability_manifest_version": (
                versions.capability_manifest_version
            ),

            "brand_profile_version": (
                versions.brand_profile_version
            ),

            "content_strategy_version": (
                versions.content_strategy_version
            ),
        }


        rows = self.db.insert(
            "content_items",
            payload,
        )


        if isinstance(
            rows,
            dict,
        ):

            rows = [
                rows
            ]


        if (
            not isinstance(
                rows,
                list,
            )
            or len(
                rows
            )
            != 1
        ):

            raise RuntimeError(
                "Expected one inserted content_item."
            )


        row = rows[0]


        return StoredContentItem(
            content_item_id=str(
                row[
                    "id"
                ]
            ),

            database_status=str(
                row[
                    "status"
                ]
            ),

            envelope=envelope,
        )
