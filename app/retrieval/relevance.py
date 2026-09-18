from __future__ import annotations

import re

from contracts.research import (
    ResearchSource,
)

from app.retrieval.query_builder import (
    CONCEPTS,
)


# Generic concepts are useful as context/outcomes, but should
# not normally decide whether a source directly answers the
# founder's question when a more specific concept exists.
GENERIC_CONCEPTS = {
    "resistance_training",
    "hypertrophy",
    "strength",
}


def _normalize(
    text: str,
) -> str:

    return re.sub(
        r"[^a-z0-9]+",
        " ",
        text.lower(),
    ).strip()


def _concept_patterns(
    concept: str,
) -> set[str]:

    config = CONCEPTS[
        concept
    ]

    patterns: set[str] = set()


    for trigger in config[
        "triggers"
    ]:

        clean = _normalize(
            trigger
        )

        if clean:

            patterns.add(
                clean
            )


    for term in config[
        "terms"
    ]:

        clean = (
            term
            .replace(
                "[Title/Abstract]",
                "",
            )
            .replace(
                '"',
                "",
            )
        )

        clean = _normalize(
            clean
        )

        if clean:

            patterns.add(
                clean
            )


    return patterns


def _hits(
    text: str,
    concept: str,
) -> set[str]:

    normalized = _normalize(
        text
    )


    return {
        pattern
        for pattern
        in _concept_patterns(
            concept
        )
        if pattern in normalized
    }


def subject_concepts(
    subject: str,
) -> list[str]:

    normalized = _normalize(
        subject
    )

    matched: list[str] = []


    for name, config in CONCEPTS.items():

        triggers = {
            _normalize(trigger)
            for trigger
            in config[
                "triggers"
            ]
        }


        if any(
            trigger
            and trigger in normalized
            for trigger in triggers
        ):

            matched.append(
                name
            )


    # A training + hypertrophy question implicitly belongs to
    # resistance-training evidence even when the founder uses
    # ordinary wording rather than the scientific phrase.
    if (
        "hypertrophy" in matched
        and "training" in normalized
        and "resistance_training"
        not in matched
    ):

        matched.insert(
            0,
            "resistance_training",
        )


    return matched


def primary_concepts(
    subject: str,
) -> list[str]:

    concepts = (
        subject_concepts(
            subject
        )
    )


    specific = [
        concept
        for concept in concepts
        if concept
        not in GENERIC_CONCEPTS
    ]


    if specific:

        return specific


    return concepts


def supporting_concepts(
    subject: str,
) -> list[str]:

    concepts = (
        subject_concepts(
            subject
        )
    )

    primary = set(
        primary_concepts(
            subject
        )
    )


    return [
        concept
        for concept in concepts
        if concept not in primary
    ]


def _has_supporting_context(
    source: ResearchSource,
    supporting: list[str],
) -> bool:

    if not supporting:

        return True


    combined = (
        (source.title or "")
        + "\n"
        + (source.notes or "")
    )


    return any(

        _hits(
            combined,
            concept,
        )

        for concept
        in supporting
    )


def _title_is_direct(
    source: ResearchSource,
    primary: list[str],
    supporting: list[str],
) -> bool:

    title = (
        source.title
        or ""
    )


    primary_hit = any(

        _hits(
            title,
            concept,
        )

        for concept
        in primary
    )


    return (
        primary_hit
        and
        _has_supporting_context(
            source,
            supporting,
        )
    )


def _abstract_is_strongly_direct(
    source: ResearchSource,
    primary: list[str],
    supporting: list[str],
) -> bool:

    abstract = (
        source.notes
        or ""
    )


    distinct_hits: set[
        tuple[str, str]
    ] = set()


    for concept in primary:

        for pattern in _hits(
            abstract,
            concept,
        ):

            distinct_hits.add(
                (
                    concept,
                    pattern,
                )
            )


    # One incidental mention is not sufficient.
    return (
        len(distinct_hits) >= 2
        and
        _has_supporting_context(
            source,
            supporting,
        )
    )


def filter_relevant_sources(
    subject: str,
    sources: list[ResearchSource],
) -> list[ResearchSource]:

    primary = (
        primary_concepts(
            subject
        )
    )

    supporting = (
        supporting_concepts(
            subject
        )
    )


    # If we cannot identify a specific research concept,
    # preserve the retriever's evidence rather than pretending
    # we can rank it reliably.
    if not primary:

        return sources


    title_direct = [

        source

        for source
        in sources

        if _title_is_direct(
            source,
            primary,
            supporting,
        )
    ]


    # When PubMed already gives us multiple papers whose titles
    # directly address the primary question, prefer them over
    # papers that only mention the topic somewhere in an
    # abstract.
    if len(title_direct) >= 2:

        return title_direct


    abstract_direct = [

        source

        for source
        in sources

        if (
            source
            not in title_direct
            and
            _abstract_is_strongly_direct(
                source,
                primary,
                supporting,
            )
        )
    ]


    return (
        title_direct
        + abstract_direct
    )
