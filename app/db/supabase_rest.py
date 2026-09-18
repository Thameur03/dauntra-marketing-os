from __future__ import annotations

import base64
import json
import os

from pathlib import Path
from typing import Any

import httpx

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[2]

load_dotenv(
    ROOT / ".env"
)


class SupabaseRESTError(
    RuntimeError
):
    pass


def _jwt_role(
    key: str,
) -> str | None:

    try:

        parts = key.split(".")

        if len(parts) != 3:
            return None


        payload = parts[1]

        payload += (
            "="
            * (-len(payload) % 4)
        )


        data = json.loads(
            base64.urlsafe_b64decode(
                payload
            )
        )


        role = data.get(
            "role"
        )


        return (
            str(role)
            if role
            else None
        )


    except Exception:

        return None


def _backend_key() -> str:

    key = (

        os.getenv(
            "SUPABASE_BACKEND_KEY",
            "",
        ).strip()

        or

        os.getenv(
            "SUPABASE_SECRET_KEY",
            "",
        ).strip()

        or

        os.getenv(
            "SUPABASE_SERVICE_ROLE_KEY",
            "",
        ).strip()
    )


    if not key:

        raise SupabaseRESTError(
            "Supabase backend key is missing."
        )


    if key.startswith(
        "sb_secret_"
    ):

        return key


    if (
        _jwt_role(key)
        == "service_role"
    ):

        return key


    raise SupabaseRESTError(
        "Supabase key is not an approved "
        "backend secret/service_role key."
    )


class SupabaseREST:

    def __init__(
        self,
        *,
        timeout: float = 25.0,
    ) -> None:

        self.url = os.getenv(
            "SUPABASE_URL",
            "",
        ).rstrip("/")


        self.backend_key = (
            _backend_key()
        )


        if not self.url:

            raise SupabaseRESTError(
                "SUPABASE_URL is missing."
            )


        self.client = httpx.Client(

            base_url=(
                self.url
                + "/rest/v1"
            ),

            timeout=timeout,

            headers={
                "apikey": (
                    self.backend_key
                ),

                "Content-Type": (
                    "application/json"
                ),

                "Accept": (
                    "application/json"
                ),
            },
        )


    def close(self) -> None:

        self.client.close()


    def __enter__(self):

        return self


    def __exit__(
        self,
        exc_type,
        exc,
        tb,
    ):

        self.close()


    @staticmethod
    def _filters(
        filters: dict[str, Any],
    ) -> dict[str, str]:

        return {
            key: f"eq.{value}"
            for key, value
            in filters.items()
        }


    @staticmethod
    def _check(
        response: httpx.Response,
    ) -> None:

        if (
            200
            <= response.status_code
            < 300
        ):

            return


        raise SupabaseRESTError(

            "Supabase Data API returned "
            f"HTTP {response.status_code}: "
            f"{response.text[:2000]}"
        )


    def select(
        self,
        table: str,
        *,
        params: dict[str, Any],
    ) -> list[dict[str, Any]]:

        response = self.client.get(
            f"/{table}",
            params=params,
        )


        self._check(
            response
        )


        payload = (
            response.json()
        )


        if not isinstance(
            payload,
            list,
        ):

            raise SupabaseRESTError(
                "Invalid SELECT response."
            )


        return payload


    def insert(
        self,
        table: str,
        row: dict[str, Any],
    ) -> dict[str, Any]:

        response = self.client.post(

            f"/{table}",

            json=row,

            headers={
                "Prefer": (
                    "return=representation"
                ),
            },
        )


        self._check(
            response
        )


        payload = (
            response.json()
        )


        if (
            not isinstance(
                payload,
                list,
            )
            or not payload
        ):

            raise SupabaseRESTError(
                "Insert returned no row."
            )


        return payload[0]


    def update(
        self,
        table: str,
        *,
        filters: dict[str, Any],
        values: dict[str, Any],
    ) -> list[dict[str, Any]]:

        response = self.client.patch(

            f"/{table}",

            params=self._filters(
                filters
            ),

            json=values,

            headers={
                "Prefer": (
                    "return=representation"
                ),
            },
        )


        self._check(
            response
        )


        payload = (
            response.json()
        )


        if not isinstance(
            payload,
            list,
        ):

            raise SupabaseRESTError(
                "Invalid UPDATE response."
            )


        return payload


    def delete(
        self,
        table: str,
        *,
        filters: dict[str, Any],
    ) -> list[dict[str, Any]]:

        response = self.client.delete(

            f"/{table}",

            params=self._filters(
                filters
            ),

            headers={
                "Prefer": (
                    "return=representation"
                ),
            },
        )


        self._check(
            response
        )


        payload = (
            response.json()
        )


        if not isinstance(
            payload,
            list,
        ):

            raise SupabaseRESTError(
                "Invalid DELETE response."
            )


        return payload
