from __future__ import annotations

from app.retrieval.relevance import (
    filter_relevant_sources,
)

from contracts.research import (
    ResearchPacket,
)


def _source_key(
    source,
) -> tuple[str, str]:

    return (
        source.title,
        str(
            source.url
            or ""
        ),
    )


def prepare_writer_packet(
    packet: ResearchPacket,
) -> ResearchPacket:
    """
    Produce the evidence view supplied to content writers.

    The stored ResearchPacket remains untouched.

    Sources that are only tangential to the founder's subject
    are removed deterministically. Claims depending entirely
    on removed sources are also removed, and surviving source
    indexes are re-numbered.
    """

    filtered_sources = (
        filter_relevant_sources(
            packet.subject,
            packet.sources,
        )
    )


    allowed_keys = {
        _source_key(
            source
        )
        for source
        in filtered_sources
    }


    selected_old_indexes = [
        index

        for index, source
        in enumerate(
            packet.sources
        )

        if _source_key(
            source
        )
        in allowed_keys
    ]


    if not selected_old_indexes:

        raise ValueError(
            "No relevant sources remain "
            "for the writer."
        )


    old_to_new = {
        old_index: new_index

        for new_index, old_index
        in enumerate(
            selected_old_indexes
        )
    }


    new_sources = [
        packet.sources[
            old_index
        ].model_dump(
            mode="json"
        )

        for old_index
        in selected_old_indexes
    ]


    new_claims = []


    for claim in packet.claims:

        # A claim survives only when every source it cites
        # survived the relevance filter.
        #
        # This prevents a claim from appearing better-supported
        # than it really is after filtering.

        if not all(
            source_index
            in old_to_new

            for source_index
            in claim.source_indexes
        ):

            continue


        claim_data = (
            claim.model_dump(
                mode="json"
            )
        )


        claim_data[
            "source_indexes"
        ] = [
            old_to_new[
                source_index
            ]

            for source_index
            in claim.source_indexes
        ]


        new_claims.append(
            claim_data
        )


    if not new_claims:

        raise ValueError(
            "No grounded research claims remain "
            "for the writer."
        )


    data = packet.model_dump(
        mode="json"
    )


    data[
        "sources"
    ] = new_sources


    data[
        "claims"
    ] = new_claims


    return ResearchPacket.model_validate(
        data
    )
