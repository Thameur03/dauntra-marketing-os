#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "$0")/.."

echo
echo "=========================================="
echo " SUPABASE LOCAL CONFIGURATION"
echo "=========================================="
echo
echo "Paste your complete Supabase PostgreSQL connection URL."
echo
echo "Recommended:"
echo "  Supabase Dashboard -> Connect -> Session pooler"
echo
echo "The value will NOT be displayed."
echo "It will be stored only in:"
echo
echo "  .env"
echo
echo ".env is ignored by Git."
echo

read -r -s -p "DATABASE_URL: " DATABASE_URL
echo

if [[ -z "$DATABASE_URL" ]]; then
    echo "ERROR: DATABASE_URL cannot be empty."
    exit 1
fi

case "$DATABASE_URL" in
    postgres://*|postgresql://*)
        ;;
    *)
        echo "ERROR: This does not look like a PostgreSQL URL."
        exit 1
        ;;
esac

# Preserve other future env variables if .env already exists,
# but replace DATABASE_URL safely.

touch .env

grep -v '^DATABASE_URL=' .env > .env.tmp || true

{
    cat .env.tmp
    printf 'DATABASE_URL="%s"\n' "$DATABASE_URL"
} > .env

rm -f .env.tmp

chmod 600 .env

unset DATABASE_URL

echo
echo "Saved securely to .env"
echo
echo "Permissions:"
ls -l .env
echo

if git check-ignore -q .env; then
    echo "OK      .env is ignored by Git"
else
    echo "ERROR   .env is NOT ignored by Git"
    exit 1
fi
