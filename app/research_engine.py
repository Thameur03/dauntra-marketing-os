from __future__ import annotations

from pathlib import Path

from app.llm.factory import (
    get_llm_provider,
)

from app.llm.evidence_schema import (
    EVIDENCE_SYNTHESIS_SCHEMA,
)

from app.research_models import (
    EvidenceSynthesis,
)

from app.retrieval.pubmed import (
    PubMedRetriever,
)

from app.retrieval.query_builder import (
    build_pubmed_queries,
)

from app.retrieval.relevance import (
    filter_relevant_sources,
)

from contracts.research import (
    ResearchPacket,
)


ROOT = Path(__file__).resolve().parents[1]


class ResearchEngineError(
    RuntimeError
):
    pass


def _system_prompt() -> str:

    return (
        ROOT
        .joinpath(
            "prompts/research_system.txt"
        )
        .read_text(
            encoding="utf-8"
        )
    )


def _evidence_prompt(
    *,
    subject: str,
    sources,
) -> str:

    blocks = []


    for index, source in enumerate(
        sources
    ):

        blocks.append(
            f"""
SOURCE INDEX: {index}

TITLE:
{source.title}

PUBLICATION:
{source.publisher or "Unknown"}

DATE:
{source.publication_date or "Unknown"}

TYPE:
{source.source_type}

URL:
{source.url}

ABSTRACT:
{source.notes}
""".strip()
        )


    evidence = "\n\n".join(
        blocks
    )


    return f"""
RESEARCH SUBJECT:

{subject}


SUPPLIED SCIENTIFIC EVIDENCE:

{evidence}


Create a conservative evidence synthesis.

Rules:

1. Use ONLY the supplied sources.

2. Every factual claim must contain one or more valid
   source_indexes referring to the numbered sources above.

3. Never invent:
   - studies
   - statistics
   - authors
   - effect sizes
   - findings
   - URLs

4. If the evidence does not adequately answer the subject,
   choose limited, conflicting, or insufficient.

5. Do not reproduce complete abstracts.

6. Recommended content angles must stay within what these
   sources can support.
""".strip()


def research_subject(
    subject: str,
) -> tuple[
    ResearchPacket,
    str,
]:

    # --------------------------------------------------------
    # PUBMED QUERY GENERATION
    #
    # IMPORTANT:
    # This is deliberately deterministic.
    #
    # We do NOT spend a Gemini request generating search terms.
    # --------------------------------------------------------

    queries = build_pubmed_queries(
        subject
    )


    try:

        with PubMedRetriever() as retriever:

            sources = retriever.search(
                queries,
                per_query=6,
                maximum_sources=12,
            )


    except Exception as exc:

        raise ResearchEngineError(
            "Scientific retrieval failed: "
            f"{exc}"
        ) from exc


    # Broader fallback, still with NO Gemini call.

    if len(sources) < 2:

        try:

            with PubMedRetriever() as retriever:

                sources = retriever.search(
                    [subject],
                    per_query=10,
                    maximum_sources=12,
                )


        except Exception as exc:

            raise ResearchEngineError(
                "Fallback scientific retrieval "
                f"failed: {exc}"
            ) from exc


    if not sources:

        raise ResearchEngineError(
            "No usable PubMed abstracts "
            "were retrieved."
        )


    # Remove sources that mention the topic only
    # incidentally. This happens before Gemini and
    # therefore costs no model request.

    sources = filter_relevant_sources(
        subject,
        sources,
    )


    if not sources:

        raise ResearchEngineError(
            "No sufficiently relevant scientific "
            "sources remained after filtering."
        )


    # --------------------------------------------------------
    # ONE GEMINI REQUEST PER SUBJECT
    # --------------------------------------------------------

    provider = get_llm_provider()


    raw_synthesis = (
        provider.generate_json(

            prompt=_evidence_prompt(
                subject=subject,
                sources=sources,
            ),

            schema=(
                EVIDENCE_SYNTHESIS_SCHEMA
            ),

            system_instruction=(
                _system_prompt()
            ),
        )
    )


    # --------------------------------------------------------
    # STRICT LOCAL VALIDATION
    # --------------------------------------------------------

    try:

        synthesis = (
            EvidenceSynthesis
            .model_validate(
                raw_synthesis
            )
        )


    except Exception as exc:

        raise ResearchEngineError(
            "Gemini evidence synthesis "
            "failed local validation: "
            f"{exc}"
        ) from exc


    try:

        packet = ResearchPacket(

            subject=subject,

            evidence_status=(
                synthesis
                .evidence_status
            ),

            summary=(
                synthesis.summary
            ),

            core_finding=(
                synthesis.core_finding
            ),

            important_nuance=(
                synthesis
                .important_nuance
            ),

            limitations=(
                synthesis.limitations
            ),

            dauntra_relevance=(
                synthesis
                .dauntra_relevance
            ),

            sources=sources,

            claims=(
                synthesis.claims
            ),

            recommended_angles=(
                synthesis
                .recommended_angles
            ),

            prohibited_angles=(
                synthesis
                .prohibited_angles
            ),

            requires_human_review=(
                synthesis
                .requires_human_review
            ),
        )


    except Exception as exc:

        raise ResearchEngineError(
            "Research packet failed final "
            f"validation: {exc}"
        ) from exc


    return (
        packet,
        provider.model_name,
    )
