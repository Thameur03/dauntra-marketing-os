from __future__ import annotations

import hashlib
import json

from app.content_brain.packet_view import (
    prepare_writer_packet,
)

from app.content_brain.versions import (
    generation_versions,
)

from app.content_brain.writers import (
    GeneratedContentValidationError,
    PlatformWriter,
)

from app.db.content_store import (
    ContentStore,
)

from app.llm.base import (
    StructuredLLM,
)

from app.product_truth import (
    assert_capabilities_allowed,
)

from contracts.common import (
    ContentFamily,
    Platform,
)

from contracts.content_package import (
    ContentItemEnvelope,
    ContentPackage,
    ContentPackageItem,
)

from contracts.research import (
    ResearchPacket,
)


AUTOMATED_PLATFORMS = (
    Platform.INSTAGRAM,
    Platform.TIKTOK,
    Platform.X,
    Platform.FACEBOOK,
)


def _canonical_json(
    value,
) -> str:

    return json.dumps(
        value,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
        ensure_ascii=False,
    )


def _generation_key(
    *,
    subject_id: str,
    research_packet_id: str,
    packet: ResearchPacket,
    platform: Platform,
    content_family: ContentFamily,
    capability_ids: list[str],
    model: str,
    variant_key: str,
) -> str:

    versions = generation_versions(
        platform
    )


    payload = {
        "subject_id": (
            subject_id
        ),

        "research_packet_id": (
            research_packet_id
        ),

        "writer_packet": (
            packet.model_dump(
                mode="json"
            )
        ),

        "platform": (
            platform.value
        ),

        "content_family": (
            content_family.value
        ),

        "capability_ids": sorted(
            set(
                capability_ids
            )
        ),

        "model": model,

        "variant_key": (
            variant_key
        ),

        "prompt_version": (
            versions.prompt_version
        ),

        "research_prompt_version": (
            versions.research_prompt_version
        ),

        "content_brain_version": (
            versions.content_brain_version
        ),

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


    return hashlib.sha256(
        _canonical_json(
            payload
        ).encode(
            "utf-8"
        )
    ).hexdigest()


def _package_id(
    *,
    subject_id: str,
    research_packet_id: str,
    content_family: ContentFamily,
    platforms: list[Platform],
    capability_ids: list[str],
    variant_key: str,
) -> str:

    payload = {
        "subject_id": subject_id,
        "research_packet_id": research_packet_id,
        "content_family": content_family.value,

        "platforms": [
            platform.value
            for platform
            in platforms
        ],

        "capability_ids": sorted(
            set(
                capability_ids
            )
        ),

        "variant_key": variant_key,
    }


    digest = hashlib.sha256(
        _canonical_json(
            payload
        ).encode(
            "utf-8"
        )
    ).hexdigest()


    return (
        "pkg_"
        + digest[:32]
    )


def _requires_human_review(
    *,
    packet: ResearchPacket,
    claims_used: list[str],
) -> bool:

    if packet.requires_human_review:

        return True


    claim_map = {
        claim.claim: claim
        for claim
        in packet.claims
    }


    for claim_text in claims_used:

        claim = claim_map.get(
            claim_text
        )


        if claim is None:

            continue


        if (
            claim.human_review_required
            or claim.sensitivity
            in {
                "training",
                "nutrition",
                "supplement",
                "health",
            }
        ):

            return True


    return False


def build_content_package(
    *,
    subject_id: str,
    research_packet_id: str,
    packet: ResearchPacket,
    content_family: ContentFamily,
    platforms: list[Platform],
    llm: StructuredLLM,
    capability_ids: list[str] | None = None,
    store: ContentStore | None = None,
    variant_key: str = "default",
    stop_on_generation_error: bool = True,
) -> ContentPackage:

    if not platforms:

        raise ValueError(
            "At least one platform is required."
        )


    platforms = list(
        dict.fromkeys(
            platforms
        )
    )


    unsupported = [
        platform
        for platform
        in platforms
        if platform
        not in AUTOMATED_PLATFORMS
    ]


    if unsupported:

        raise ValueError(
            "Automated Section 3C package does not "
            "support: "
            + ", ".join(
                platform.value
                for platform
                in unsupported
            )
        )


    capability_ids = list(
        dict.fromkeys(
            capability_ids
            or []
        )
    )


    assert_capabilities_allowed(
        capability_ids
    )


    if (
        content_family
        == ContentFamily.C04
        and not capability_ids
    ):

        raise ValueError(
            "C04 requires at least one explicitly "
            "selected approved DAUNTRA capability."
        )


    writer_packet = (
        prepare_writer_packet(
            packet
        )
    )


    package_review = (
        writer_packet
        .requires_human_review
    )


    items: list[
        ContentPackageItem
    ] = []


    generation_error_seen = False


    for index, platform in enumerate(
        platforms
    ):

        versions = (
            generation_versions(
                platform
            )
        )


        generation_key = (
            _generation_key(
                subject_id=subject_id,
                research_packet_id=(
                    research_packet_id
                ),
                packet=writer_packet,
                platform=platform,
                content_family=(
                    content_family
                ),
                capability_ids=(
                    capability_ids
                ),
                model=llm.model_name,
                variant_key=(
                    variant_key
                ),
            )
        )


        # ----------------------------------------------------
        # IDEMPOTENCY
        # ----------------------------------------------------

        if store is not None:

            existing = (
                store.find_existing(
                    subject_id=subject_id,

                    research_packet_id=(
                        research_packet_id
                    ),

                    platform=platform,

                    content_family=(
                        content_family
                    ),

                    generation_key=(
                        generation_key
                    ),
                )
            )


            if existing is not None:

                package_review = (
                    package_review
                    or existing
                    .envelope
                    .requires_human_review
                )


                items.append(
                    ContentPackageItem(
                        platform=platform,

                        status="REUSED",

                        database_status=(
                            existing
                            .database_status
                        ),

                        content_item_id=(
                            existing
                            .content_item_id
                        ),

                        generation_key=(
                            generation_key
                        ),

                        content=(
                            existing
                            .envelope
                            .content
                        ),
                    )
                )

                continue


        # ----------------------------------------------------
        # INDEPENDENT PLATFORM GENERATION
        # ----------------------------------------------------

        writer = PlatformWriter(
            llm=llm,
            platform=platform,
        )


        try:

            content = writer.write(
                packet=writer_packet,

                content_family=(
                    content_family
                ),

                capability_ids=(
                    capability_ids
                ),
            )


        except GeneratedContentValidationError as exc:

            items.append(
                ContentPackageItem(
                    platform=platform,

                    status=(
                        "FAILED_VALIDATION"
                    ),

                    generation_key=(
                        generation_key
                    ),

                    content=(
                        exc.content
                    ),

                    error=(
                        exc.reason
                    ),
                )
            )

            continue


        except Exception as exc:

            generation_error_seen = True


            items.append(
                ContentPackageItem(
                    platform=platform,

                    status=(
                        "FAILED_GENERATION"
                    ),

                    generation_key=(
                        generation_key
                    ),

                    error=(
                        type(
                            exc
                        ).__name__
                        + ": "
                        + str(
                            exc
                        )
                    ),
                )
            )


            if stop_on_generation_error:

                for skipped in (
                    platforms[
                        index + 1:
                    ]
                ):

                    skipped_key = (
                        _generation_key(
                            subject_id=(
                                subject_id
                            ),

                            research_packet_id=(
                                research_packet_id
                            ),

                            packet=(
                                writer_packet
                            ),

                            platform=skipped,

                            content_family=(
                                content_family
                            ),

                            capability_ids=(
                                capability_ids
                            ),

                            model=(
                                llm.model_name
                            ),

                            variant_key=(
                                variant_key
                            ),
                        )
                    )


                    items.append(
                        ContentPackageItem(
                            platform=(
                                skipped
                            ),

                            status=(
                                "SKIPPED"
                            ),

                            generation_key=(
                                skipped_key
                            ),

                            error=(
                                "Skipped after an earlier "
                                "platform generation error."
                            ),
                        )
                    )


                break


            continue


        # ----------------------------------------------------
        # REVIEW STATUS
        # ----------------------------------------------------

        requires_review = (
            _requires_human_review(
                packet=writer_packet,

                claims_used=(
                    content.claims_used
                ),
            )
        )


        package_review = (
            package_review
            or requires_review
        )


        envelope = (
            ContentItemEnvelope(
                generation_key=(
                    generation_key
                ),

                variant_key=(
                    variant_key
                ),

                research_prompt_version=(
                    versions
                    .research_prompt_version
                ),

                content_brain_version=(
                    versions
                    .content_brain_version
                ),

                requires_human_review=(
                    requires_review
                ),

                content=content,
            )
        )


        # ----------------------------------------------------
        # OPTIONAL PERSISTENCE
        # ----------------------------------------------------

        if store is not None:

            try:

                stored = store.save(
                    subject_id=subject_id,

                    research_packet_id=(
                        research_packet_id
                    ),

                    envelope=envelope,

                    model=(
                        llm.model_name
                    ),

                    versions=versions,
                )


            except Exception as exc:

                items.append(
                    ContentPackageItem(
                        platform=platform,

                        status=(
                            "FAILED_PERSISTENCE"
                        ),

                        generation_key=(
                            generation_key
                        ),

                        content=content,

                        error=(
                            type(
                                exc
                            ).__name__
                            + ": "
                            + str(
                                exc
                            )
                        ),
                    )
                )

                continue


            item_status = (
                "NEEDS_HUMAN_REVIEW"

                if requires_review

                else "GENERATED"
            )


            items.append(
                ContentPackageItem(
                    platform=platform,

                    status=(
                        item_status
                    ),

                    database_status=(
                        stored
                        .database_status
                    ),

                    content_item_id=(
                        stored
                        .content_item_id
                    ),

                    generation_key=(
                        generation_key
                    ),

                    content=content,
                )
            )


        else:

            item_status = (
                "NEEDS_HUMAN_REVIEW"

                if requires_review

                else "GENERATED"
            )


            items.append(
                ContentPackageItem(
                    platform=platform,

                    status=(
                        item_status
                    ),

                    generation_key=(
                        generation_key
                    ),

                    content=content,
                )
            )


    successful = [
        item
        for item
        in items
        if item.status
        in {
            "GENERATED",
            "NEEDS_HUMAN_REVIEW",
            "REUSED",
        }
    ]


    failed = [
        item
        for item
        in items
        if item.status
        in {
            "FAILED_VALIDATION",
            "FAILED_GENERATION",
            "FAILED_PERSISTENCE",
            "SKIPPED",
        }
    ]


    if (
        successful
        and not failed
    ):

        build_status = (
            "COMPLETE"
        )


    elif successful:

        build_status = (
            "PARTIAL"
        )


    else:

        build_status = (
            "FAILED"
        )


    return ContentPackage(

        package_id=(
            _package_id(
                subject_id=subject_id,

                research_packet_id=(
                    research_packet_id
                ),

                content_family=(
                    content_family
                ),

                platforms=platforms,

                capability_ids=(
                    capability_ids
                ),

                variant_key=(
                    variant_key
                ),
            )
        ),

        subject_id=subject_id,

        research_packet_id=(
            research_packet_id
        ),

        content_family=(
            content_family
        ),

        model=(
            llm.model_name
        ),

        evidence_status=(
            writer_packet
            .evidence_status
        ),

        requires_human_review=(
            package_review
        ),

        build_status=(
            build_status
        ),

        items=items,
    )
