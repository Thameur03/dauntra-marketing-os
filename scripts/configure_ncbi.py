from __future__ import annotations

from getpass import getpass
from pathlib import Path

from dotenv import set_key


ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"


print()
print("==========================================")
print(" NCBI / PUBMED CONFIGURATION")
print("==========================================")
print()
print(
    "NCBI recommends that automated E-utilities "
    "requests include a contact email."
)
print()
print(
    "This does NOT require a credit card."
)
print()


email = input(
    "Contact email for NCBI requests: "
).strip()

if not email or "@" not in email:
    raise SystemExit(
        "ERROR: Enter a valid contact email."
    )


api_key = getpass(
    "NCBI_API_KEY [optional - press Enter to skip]: "
).strip()


ENV_PATH.touch(
    exist_ok=True
)

set_key(
    str(ENV_PATH),
    "NCBI_EMAIL",
    email,
)

if api_key:
    set_key(
        str(ENV_PATH),
        "NCBI_API_KEY",
        api_key,
    )


ENV_PATH.chmod(0o600)


print()
print("NCBI configuration saved.")
print()
print(
    "NCBI API key: "
    + (
        "CONFIGURED"
        if api_key
        else "NOT REQUIRED / SKIPPED"
    )
)
