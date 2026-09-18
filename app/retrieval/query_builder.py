from __future__ import annotations

import re


# ============================================================
# SCIENTIFIC CONCEPT DICTIONARY
#
# Founder subjects are written in normal English.
# PubMed should receive scientific search terminology.
#
# No LLM is required.
# ============================================================

CONCEPTS = {

    "resistance_training": {
        "triggers": (
            "resistance training",
            "strength training",
            "weight training",
            "weightlifting",
            "lifting weights",
        ),

        "terms": (
            '"resistance training"[Title/Abstract]',
            '"strength training"[Title/Abstract]',
            '"weight training"[Title/Abstract]',
        ),
    },


    "failure": {
        "triggers": (
            "failure",
            "reps before failure",
            "repetitions before failure",
            "reps in reserve",
            "repetitions in reserve",
            "rir",
            "proximity to failure",
        ),

        "terms": (
            '"training to failure"[Title/Abstract]',
            '"muscular failure"[Title/Abstract]',
            '"momentary muscular failure"[Title/Abstract]',
            '"proximity to failure"[Title/Abstract]',
            '"repetitions in reserve"[Title/Abstract]',
        ),
    },


    "hypertrophy": {
        "triggers": (
            "hypertrophy",
            "muscle growth",
            "muscle size",
            "build muscle",
            "gain muscle",
        ),

        "terms": (
            'hypertrophy[Title/Abstract]',
            '"muscle hypertrophy"[Title/Abstract]',
            '"muscle growth"[Title/Abstract]',
            '"muscle size"[Title/Abstract]',
        ),
    },


    "strength": {
        "triggers": (
            "strength",
            "one rep max",
            "1rm",
            "maximum strength",
        ),

        "terms": (
            '"muscle strength"[Title/Abstract]',
            '"strength gain"[Title/Abstract]',
            '"maximal strength"[Title/Abstract]',
            '1RM[Title/Abstract]',
        ),
    },


    "volume": {
        "triggers": (
            "training volume",
            "number of sets",
            "weekly sets",
            "sets per muscle",
        ),

        "terms": (
            '"training volume"[Title/Abstract]',
            '"resistance training volume"[Title/Abstract]',
            '"weekly sets"[Title/Abstract]',
        ),
    },


    "frequency": {
        "triggers": (
            "training frequency",
            "times per week",
            "frequency",
        ),

        "terms": (
            '"training frequency"[Title/Abstract]',
            '"resistance training frequency"[Title/Abstract]',
        ),
    },


    "protein": {
        "triggers": (
            "protein",
            "protein intake",
            "protein supplementation",
        ),

        "terms": (
            '"protein intake"[Title/Abstract]',
            '"protein supplementation"[Title/Abstract]',
            '"dietary protein"[Title/Abstract]',
        ),
    },


    "creatine": {
        "triggers": (
            "creatine",
        ),

        "terms": (
            'creatine[Title/Abstract]',
            '"creatine supplementation"[Title/Abstract]',
        ),
    },
}


STOPWORDS = {
    "about",
    "after",
    "before",
    "better",
    "does",
    "from",
    "greater",
    "have",
    "more",
    "much",
    "produce",
    "should",
    "stopping",
    "than",
    "that",
    "their",
    "them",
    "this",
    "training",
    "what",
    "when",
    "where",
    "which",
    "with",
    "would",
}


def _clean(
    text: str,
) -> str:

    return re.sub(
        r"\s+",
        " ",
        text,
    ).strip()


def _group(
    terms: tuple[str, ...],
) -> str:

    return (
        "("
        + " OR ".join(terms)
        + ")"
    )


def _matched_concepts(
    subject: str,
) -> list[str]:

    lowered = subject.lower()

    matches: list[str] = []


    for name, config in CONCEPTS.items():

        if any(
            trigger in lowered
            for trigger
            in config["triggers"]
        ):

            matches.append(
                name
            )


    # Hypertrophy questions involving training almost always
    # concern resistance exercise, even if the founder did not
    # explicitly write "resistance training".

    if (
        "hypertrophy" in matches
        and "training" in lowered
        and "resistance_training"
        not in matches
    ):

        matches.insert(
            0,
            "resistance_training",
        )


    return matches


def _fallback_keywords(
    subject: str,
) -> list[str]:

    words = re.findall(
        r"[a-zA-Z][a-zA-Z\-]{2,}",
        subject.lower(),
    )


    output: list[str] = []


    for word in words:

        word = word.strip("-")


        if (
            len(word) < 4
            or word in STOPWORDS
        ):

            continue


        if word not in output:

            output.append(
                word
            )


    return output[:6]


def build_pubmed_queries(
    subject: str,
) -> list[str]:

    subject = _clean(
        subject
    )


    if not subject:

        raise ValueError(
            "Research subject cannot be empty."
        )


    concepts = _matched_concepts(
        subject
    )


    queries: list[str] = []


    # ========================================================
    # CONCEPT-AWARE SEARCH
    # ========================================================

    if concepts:

        groups = [

            _group(
                CONCEPTS[name][
                    "terms"
                ]
            )

            for name
            in concepts[:4]
        ]


        balanced = (
            " AND ".join(
                groups
            )
        )


        # First preference:
        # high-level evidence.

        review_query = (

            balanced

            + " AND "

            + "("
            + '"systematic review"[Publication Type]'
            + " OR "
            + '"meta-analysis"[Publication Type]'
            + ")"
        )


        queries.append(
            review_query
        )


        # Second preference:
        # all relevant study designs.

        queries.append(
            balanced
        )


        # Third query:
        # remove generic resistance-training concept if we
        # already have at least two more specific concepts.

        specific = [
            name
            for name in concepts
            if name != "resistance_training"
        ]


        if len(specific) >= 2:

            broad = " AND ".join(

                _group(
                    CONCEPTS[name][
                        "terms"
                    ]
                )

                for name
                in specific[:3]
            )


            queries.append(
                broad
            )


    # ========================================================
    # GENERIC FALLBACK
    # ========================================================

    else:

        keywords = (
            _fallback_keywords(
                subject
            )
        )


        if not keywords:

            raise ValueError(
                "Could not derive PubMed "
                "search terms."
            )


        precise = " AND ".join(

            f"{word}[Title/Abstract]"

            for word
            in keywords[:4]
        )


        broad = " OR ".join(

            f"{word}[Title/Abstract]"

            for word
            in keywords
        )


        queries.extend(
            [
                precise,
                f"({broad})",
            ]
        )


    # Preserve order, remove duplicates,
    # and never generate more than 3 PubMed requests.

    return list(
        dict.fromkeys(
            query.strip()
            for query in queries
            if query.strip()
        )
    )[:3]
