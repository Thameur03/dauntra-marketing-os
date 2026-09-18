from contracts.research import (
    ResearchSource,
)

from app.retrieval.relevance import (
    filter_relevant_sources,
    primary_concepts,
)


SUBJECT = (
    "Does training to muscular failure "
    "produce more muscle hypertrophy than "
    "stopping a few reps before failure?"
)


def make_source(
    title: str,
    notes: str,
) -> ResearchSource:

    return ResearchSource(
        title=title,
        publisher="Fixture",
        source_type="study",
        notes=notes,
    )


def test_failure_is_primary():

    assert (
        primary_concepts(
            SUBJECT
        )
        == ["failure"]
    )


def test_title_first_filter_removes_adjacent_topics():

    failure_meta = make_source(
        (
            "Resistance training performed "
            "to repetition failure or non-failure"
        ),
        (
            "Muscle hypertrophy was evaluated."
        ),
    )


    proximity = make_source(
        (
            "Resistance training "
            "proximity-to-failure "
            "and skeletal muscle hypertrophy"
        ),
        (
            "Repetitions in reserve "
            "were evaluated."
        ),
    )


    rir_trial = make_source(
        (
            "Momentary muscular failure "
            "or repetitions-in-reserve"
        ),
        (
            "Resistance-trained adults "
            "were assessed for hypertrophy."
        ),
    )


    low_load = make_source(
        (
            "Low versus high load "
            "resistance training"
        ),
        (
            "Some included protocols trained "
            "to muscular failure. "
            "Muscle hypertrophy was measured."
        ),
    )


    tempo = make_source(
        (
            "Resistance training repetition "
            "tempo and muscle hypertrophy"
        ),
        (
            "Several studies instructed "
            "participants to train to failure."
        ),
    )


    autoregulation = make_source(
        (
            "Load and volume autoregulation "
            "for strength and hypertrophy"
        ),
        (
            "Velocity loss was used as "
            "a fatigue threshold."
        ),
    )


    result = filter_relevant_sources(
        SUBJECT,
        [
            failure_meta,
            proximity,
            rir_trial,
            low_load,
            tempo,
            autoregulation,
        ],
    )


    assert result == [
        failure_meta,
        proximity,
        rir_trial,
    ]


def test_hyphenated_rir_is_recognized():

    rir = make_source(
        (
            "Failure or "
            "repetitions-in-reserve "
            "during resistance training"
        ),
        (
            "Muscle hypertrophy "
            "was measured."
        ),
    )


    other = make_source(
        (
            "Resistance training tempo"
        ),
        (
            "Muscle hypertrophy "
            "was measured."
        ),
    )


    result = filter_relevant_sources(
        SUBJECT,
        [
            rir,
            other,
        ],
    )


    assert rir in result
