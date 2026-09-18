from __future__ import annotations

from getpass import getpass
from pathlib import Path

from dotenv import set_key


ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"


print()
print("==========================================")
print(" GEMINI LOCAL CONFIGURATION")
print("==========================================")
print()
print("The API key will be stored only in .env.")
print("It will not be displayed.")
print()


api_key = getpass("GEMINI_API_KEY: ").strip()

if not api_key:
    raise SystemExit(
        "ERROR: Gemini API key cannot be empty."
    )


model = input(
    "GEMINI_MODEL [gemini-3.8-flash]: "
).strip()

if not model:
    model = "gemini-3.8-flash"


ENV_PATH.touch(
    exist_ok=True
)

set_key(
    str(ENV_PATH),
    "LLM_PROVIDER",
    "gemini",
)

set_key(
    str(ENV_PATH),
    "GEMINI_API_KEY",
    api_key,
)

set_key(
    str(ENV_PATH),
    "GEMINI_MODEL",
    model,
)

ENV_PATH.chmod(0o600)


print()
print("Saved securely.")
print(f"Model: {model}")
print()
