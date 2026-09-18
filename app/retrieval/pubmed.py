from __future__ import annotations

import os
import time
import xml.etree.ElementTree as ET

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import httpx

from dotenv import load_dotenv

from contracts.research import (
    ResearchSource,
)


ROOT = Path(__file__).resolve().parents[2]

load_dotenv(
    ROOT / ".env"
)


EUTILS = (
    "https://eutils.ncbi.nlm.nih.gov/"
    "entrez/eutils"
)


NCBI_TOOL = "DAUNTRA_Marketing_OS"


class PubMedError(
    RuntimeError
):
    pass


def _text(
    element: ET.Element | None,
) -> str:

    if element is None:
        return ""

    return "".join(
        element.itertext()
    ).strip()


def _publication_date(
    article: ET.Element,
) -> str | None:

    pub_date = article.find(
        ".//JournalIssue/PubDate"
    )

    if pub_date is None:
        return None


    year = _text(
        pub_date.find("Year")
    )

    month = _text(
        pub_date.find("Month")
    )

    day = _text(
        pub_date.find("Day")
    )


    if year:

        return " ".join(
            value
            for value in (
                year,
                month,
                day,
            )
            if value
        )


    medline = _text(
        pub_date.find(
            "MedlineDate"
        )
    )

    return medline or None


def _source_type(
    publication_types: list[str],
) -> str:

    normalized = {
        value.lower()
        for value
        in publication_types
    }


    if any(
        "meta-analysis" in value
        for value in normalized
    ):
        return "meta_analysis"


    if any(
        "systematic review" in value
        for value in normalized
    ):
        return "systematic_review"


    if any(
        "guideline" in value
        for value in normalized
    ):
        return "guideline"


    return "study"


@dataclass(frozen=True)
class PubMedResult:

    pmid: str

    source: ResearchSource


class PubMedRetriever:

    def __init__(
        self,
        *,
        timeout_seconds: float = 30.0,
        max_retries: int = 5,
    ) -> None:

        self.email = os.getenv(
            "NCBI_EMAIL",
            "",
        ).strip()

        self.api_key = os.getenv(
            "NCBI_API_KEY",
            "",
        ).strip()

        self.max_retries = max_retries


        # NCBI supports:
        #
        #   no API key -> max 3 requests/sec
        #   API key    -> max 10 requests/sec
        #
        # Stay deliberately below both limits.

        self.minimum_interval = (
            0.12
            if self.api_key
            else 0.40
        )


        self._last_request_at = 0.0


        self.client = httpx.Client(

            timeout=timeout_seconds,

            headers={
                "User-Agent": (
                    "DAUNTRA-Marketing-OS/1.0 "
                    "(scientific research pipeline)"
                )
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


    def _wait_for_rate_limit(
        self,
    ) -> None:

        if not self._last_request_at:
            return


        elapsed = (
            time.monotonic()
            - self._last_request_at
        )


        remaining = (
            self.minimum_interval
            - elapsed
        )


        if remaining > 0:

            time.sleep(
                remaining
            )


    def _request_params(
        self,
        params: dict,
    ) -> dict:

        output = dict(
            params
        )


        output["tool"] = (
            NCBI_TOOL
        )


        if self.email:

            output["email"] = (
                self.email
            )


        if self.api_key:

            output["api_key"] = (
                self.api_key
            )


        return output


    @staticmethod
    def _retry_after_seconds(
        response: httpx.Response,
    ) -> float | None:

        value = response.headers.get(
            "Retry-After"
        )


        if not value:
            return None


        try:

            return float(
                value
            )

        except ValueError:

            return None


    def _get(
        self,
        endpoint: str,
        *,
        params: dict,
    ) -> httpx.Response:

        url = (
            f"{EUTILS}/{endpoint}"
        )


        last_error: Exception | None = (
            None
        )


        for attempt in range(
            self.max_retries
        ):

            self._wait_for_rate_limit()


            try:

                response = (
                    self.client.get(
                        url,
                        params=(
                            self
                            ._request_params(
                                params
                            )
                        ),
                    )
                )


                self._last_request_at = (
                    time.monotonic()
                )


            except httpx.HTTPError as exc:

                last_error = exc


                if (
                    attempt
                    >= self.max_retries - 1
                ):

                    break


                time.sleep(
                    min(
                        8.0,
                        1.0
                        * (
                            2 ** attempt
                        ),
                    )
                )

                continue


            if response.status_code == 200:

                return response


            retryable = (
                response.status_code
                == 429
                or
                500
                <= response.status_code
                <= 599
            )


            if not retryable:

                raise PubMedError(
                    "PubMed request failed: "
                    f"HTTP "
                    f"{response.status_code}"
                )


            if (
                attempt
                >= self.max_retries - 1
            ):

                raise PubMedError(
                    "PubMed request failed "
                    "after retries: "
                    f"HTTP "
                    f"{response.status_code}"
                )


            retry_after = (
                self
                ._retry_after_seconds(
                    response
                )
            )


            delay = max(

                retry_after or 0,

                min(
                    8.0,
                    1.0
                    * (
                        2 ** attempt
                    ),
                ),
            )


            print(
                "PubMed temporary "
                f"HTTP "
                f"{response.status_code}; "
                f"retrying in "
                f"{delay:.1f}s..."
            )


            time.sleep(
                delay
            )


        raise PubMedError(
            "PubMed network request "
            f"failed: {last_error}"
        )


    def search_ids(
        self,
        query: str,
        *,
        limit: int = 8,
    ) -> list[str]:

        response = self._get(

            "esearch.fcgi",

            params={
                "db": "pubmed",
                "term": query,
                "retmode": "json",
                "retmax": limit,
                "sort": "relevance",
            },
        )


        try:

            payload = (
                response.json()
            )

        except Exception as exc:

            raise PubMedError(
                "PubMed search returned "
                "invalid JSON."
            ) from exc


        return (

            payload
            .get(
                "esearchresult",
                {},
            )
            .get(
                "idlist",
                [],
            )
        )


    def fetch(
        self,
        pmids: Iterable[str],
    ) -> list[PubMedResult]:

        ids = list(
            dict.fromkeys(
                pmids
            )
        )


        if not ids:

            return []


        response = self._get(

            "efetch.fcgi",

            params={
                "db": "pubmed",
                "id": ",".join(
                    ids
                ),
                "retmode": "xml",
            },
        )


        try:

            root = ET.fromstring(
                response.text
            )


        except ET.ParseError as exc:

            raise PubMedError(
                "PubMed returned "
                "invalid XML."
            ) from exc


        output: list[
            PubMedResult
        ] = []


        for article in root.findall(
            ".//PubmedArticle"
        ):

            citation = article.find(
                "MedlineCitation"
            )


            if citation is None:

                continue


            pmid = _text(
                citation.find(
                    "PMID"
                )
            )


            if not pmid:

                continue


            article_node = (
                citation.find(
                    "Article"
                )
            )


            if article_node is None:

                continue


            title = _text(
                article_node.find(
                    "ArticleTitle"
                )
            )


            if not title:

                continue


            abstract_parts: list[str] = []


            for node in (
                article_node.findall(
                    ".//Abstract/"
                    "AbstractText"
                )
            ):

                content = _text(
                    node
                )


                if not content:

                    continue


                label = (
                    node.attrib.get(
                        "Label"
                    )
                )


                if label:

                    content = (
                        f"{label}: "
                        f"{content}"
                    )


                abstract_parts.append(
                    content
                )


            abstract = "\n".join(
                abstract_parts
            )


            # The automated synthesis must have
            # actual abstract evidence.
            if not abstract:

                continue


            journal = _text(
                article_node.find(
                    ".//Journal/Title"
                )
            )


            publication_types = [

                _text(
                    node
                )

                for node
                in article_node.findall(
                    ".//PublicationTypeList/"
                    "PublicationType"
                )

                if _text(
                    node
                )
            ]


            source = ResearchSource(

                title=title,

                url=(
                    "https://pubmed.ncbi.nlm.nih.gov/"
                    f"{pmid}/"
                ),

                publisher=(
                    journal
                    if journal
                    else "PubMed"
                ),

                publication_date=(
                    _publication_date(
                        article_node
                    )
                ),

                source_type=(
                    _source_type(
                        publication_types
                    )
                ),

                notes=(
                    abstract[:12000]
                ),
            )


            output.append(

                PubMedResult(
                    pmid=pmid,
                    source=source,
                )
            )


        return output


    def search(
        self,
        queries: list[str],
        *,
        per_query: int = 6,
        maximum_sources: int = 12,
    ) -> list[ResearchSource]:

        ids: list[str] = []


        # Maximum of three generated strategies.
        # Calls are serialized and rate-limited.

        for query in queries[:3]:

            clean_query = (
                query.strip()
            )


            if not clean_query:

                continue


            ids.extend(

                self.search_ids(
                    clean_query,
                    limit=per_query,
                )
            )


        ids = list(
            dict.fromkeys(
                ids
            )
        )


        results = self.fetch(
            ids
        )


        return [

            result.source

            for result
            in results[
                :maximum_sources
            ]
        ]
