from __future__ import annotations

import os
from getpass import getpass
from pathlib import Path
from urllib.parse import unquote, urlsplit

from dotenv import load_dotenv, set_key


ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"

load_dotenv(ENV_PATH)


database_url = os.getenv(
    "DATABASE_URL",
    "",
).strip()


if not database_url:
    raise SystemExit(
        "DATABASE_URL is missing."
    )


parsed = urlsplit(
    database_url
)

username = unquote(
    parsed.username or ""
)


project_ref = None


if username.startswith(
    "postgres."
):

    project_ref = username.split(
        ".",
        1,
    )[1]


if not project_ref:

    raise SystemExit(
        "Could not derive Supabase project reference "
        "from DATABASE_URL."
    )


supabase_url = (
    f"https://{project_ref}.supabase.co"
)


print()
print("==========================================")
print(" SUPABASE HTTPS CONFIGURATION")
print("==========================================")
print()

print(
    "Project URL derived successfully:"
)

print(
    f"  {supabase_url}"
)

print()

print(
    "Paste the server-side Supabase SECRET key."
)

print(
    "Recommended format: sb_secret_..."
)

print()

print(
    "Do NOT use the publishable key."
)

print(
    "The key will not be displayed."
)

print()


secret_key = getpass(
    "SUPABASE_SECRET_KEY: "
).strip()


if not secret_key:

    raise SystemExit(
        "Secret key cannot be empty."
    )


ENV_PATH.touch(
    exist_ok=True
)


set_key(
    str(ENV_PATH),
    "SUPABASE_URL",
    supabase_url,
)


set_key(
    str(ENV_PATH),
    "SUPABASE_SECRET_KEY",
    secret_key,
)


set_key(
    str(ENV_PATH),
    "DB_RUNTIME_TRANSPORT",
    "rest",
)


ENV_PATH.chmod(
    0o600
)


print()
print(
    "Saved securely to .env"
)

print(
    "Runtime database transport: REST/HTTPS"
)
