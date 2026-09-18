from __future__ import annotations

import sys
from pathlib import Path

from pydantic import (
    BaseModel,
    ConfigDict,
)


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(ROOT),
    )


from app.llm.gemini import (
    GeminiProvider,
)


class CheckResult(
    BaseModel
):
    model_config = ConfigDict(
        extra="forbid"
    )

    status: str


print()
print("==========================================")
print(" GEMINI STRUCTURED OUTPUT CHECK")
print("==========================================")
print()


try:

    provider = GeminiProvider()

    result = provider.generate_structured(

        prompt=(
            "Return the word ok "
            "in the status field."
        ),

        response_model=CheckResult,
    )


    if result.status.lower() != "ok":
        raise RuntimeError(
            f"Unexpected result: "
            f"{result.status}"
        )


    print(
        "GEMINI CONNECTION: PASS"
    )

    print(
        "INTERACTIONS API: PASS"
    )

    print(
        "STRUCTURED OUTPUT: PASS"
    )

    print(
        "STORE=FALSE: CONFIGURED"
    )

    print(
        f"MODEL: {provider.model_name}"
    )


except Exception as exc:

    print(
        "GEMINI CHECK: FAIL"
    )

    print(
        type(exc).__name__
        + ": "
        + str(exc)
    )

    raise SystemExit(1)
