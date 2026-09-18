from app.retrieval.query_builder import (
    build_pubmed_queries,
)


def test_failure_hypertrophy_query_uses_scientific_terms():

    queries = build_pubmed_queries(
        "Does training to muscular failure "
        "produce more muscle hypertrophy than "
        "stopping a few reps before failure?"
    )

    text = " ".join(
        queries
    ).lower()

    assert (
        "proximity to failure"
        in text
    )

    assert (
        "repetitions in reserve"
        in text
    )

    assert (
        "muscular failure"
        in text
    )

    assert (
        "hypertrophy"
        in text
    )

    assert (
        "resistance training"
        in text
    )


def test_query_builder_prioritizes_reviews():

    queries = build_pubmed_queries(
        "training to failure for hypertrophy"
    )

    first = queries[0].lower()

    assert (
        "systematic review"
        in first
    )

    assert (
        "meta-analysis"
        in first
    )


def test_query_builder_max_three_queries():

    queries = build_pubmed_queries(
        "resistance training volume "
        "frequency strength hypertrophy"
    )

    assert len(queries) <= 3


def test_unknown_topic_has_deterministic_fallback():

    queries = build_pubmed_queries(
        "sleep duration athletic recovery"
    )

    assert queries

    assert any(
        "sleep" in query
        for query in queries
    )
