from __future__ import annotations

import sys

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:

    sys.path.insert(
        0,
        str(ROOT),
    )


from app.llm.evidence_schema import (
    EVIDENCE_SYNTHESIS_SCHEMA,
)

from app.llm.gemini import (
    GeminiProvider,
)

from app.research_models import (
    EvidenceSynthesis,
)


print()
print("==========================================")
print(" GEMINI RESEARCH WIRE-SCHEMA CHECK")
print("==========================================")
print()


provider = GeminiProvider()


prompt = """
This is only a structured-output integration test.

Return:

evidence_status:
sufficient

summary:
A synthetic schema-validation response for the DAUNTRA research engine.

core_finding:
The compact Gemini wire schema is functioning.

important_nuance:
This is synthetic test data only.

limitations:
One item saying this is not scientific evidence.

dauntra_relevance:
This validates infrastructure only.

claims:
Exactly one claim.

Its claim text:
This is a synthetic validation claim.

Its sensitivity:
general

Its source_indexes:
[0]

Its confidence:
high

Its human_review_required:
false

recommended_angles:
One item: Synthetic validation only.

prohibited_angles:
One item: Do not publish this fixture.

requires_human_review:
false

Do not introduce any real scientific claims.
""".strip()


try:

    raw = provider.generate_json(

        prompt=prompt,

        schema=(
            EVIDENCE_SYNTHESIS_SCHEMA
        ),

        system_instruction=(
            "Return the requested synthetic "
            "structured test data."
        ),
    )


    result = (
        EvidenceSynthesis
        .model_validate(
            raw
        )
    )


    if not result.claims:

        raise RuntimeError(
            "No claims returned."
        )


    print(
        "WIRE SCHEMA API: PASS"
    )

    print(
        "JSON DECODING: PASS"
    )

    print(
        "PYDANTIC VALIDATION: PASS"
    )

    print(
        f"MODEL: {provider.model_name}"
    )


except Exception as exc:

    print(
        "WIRE SCHEMA API: FAIL"
    )

    print()

    print(
        type(exc).__name__
        + ": "
        + str(exc)
    )

    raise SystemExit(1)
