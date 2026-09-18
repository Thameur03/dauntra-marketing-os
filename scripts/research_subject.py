from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(ROOT),
    )


from app.db.research_store import (
    ResearchStore,
)

from app.research_engine import (
    research_subject,
)

from contracts.subject import (
    SubjectCreate,
)


def parse_args():

    parser = argparse.ArgumentParser(
        description=(
            "Research a DAUNTRA marketing subject "
            "and store the validated evidence packet."
        )
    )

    parser.add_argument(
        "--subject",
        required=True,
    )

    parser.add_argument(
        "--family",
        default="C02",
        choices=[
            "C01",
            "C02",
            "C03",
            "C04",
        ],
    )

    return parser.parse_args()


def main() -> int:

    args = parse_args()

    subject = SubjectCreate(
        subject=args.subject,
        content_family=args.family,
    )

    subject_id = None

    try:

        # ----------------------------------------------------
        # CREATE SUBJECT THROUGH SUPABASE HTTPS
        # ----------------------------------------------------

        with ResearchStore() as store:

            subject_id = (
                store.create_subject(
                    subject
                )
            )


        print()
        print(
            "=========================================="
        )
        print(
            " DAUNTRA RESEARCH ENGINE"
        )
        print(
            "=========================================="
        )
        print()

        print(
            f"Subject ID: {subject_id}"
        )

        print(
            f"Subject:    {subject.subject}"
        )

        print()

        print(
            "Pipeline:"
        )

        print(
            "  deterministic PubMed query builder"
        )

        print(
            "  -> PubMed scientific evidence"
        )

        print(
            "  -> ONE Gemini synthesis"
        )

        print(
            "  -> Pydantic validation"
        )

        print(
            "  -> Supabase HTTPS"
        )

        print()

        print(
            "Retrieving and analyzing "
            "scientific sources..."
        )

        print()


        # ----------------------------------------------------
        # RESEARCH
        #
        # Current engine makes ONE Gemini request.
        # ----------------------------------------------------

        packet, model = (
            research_subject(
                subject.subject
            )
        )


        # ----------------------------------------------------
        # STORE VALIDATED PACKET
        # ----------------------------------------------------

        with ResearchStore() as store:

            packet_id = (
                store.save_packet(
                    subject_id=subject_id,
                    packet=packet,
                    model=model,
                )
            )


        # ----------------------------------------------------
        # OUTPUT
        # ----------------------------------------------------

        print(
            "=========================================="
        )

        print(
            " RESEARCH: PASS"
        )

        print(
            "=========================================="
        )

        print()

        print(
            f"Research Packet ID: {packet_id}"
        )

        print(
            f"Model:              {model}"
        )

        print(
            f"Evidence status:    "
            f"{packet.evidence_status}"
        )

        print(
            f"Sources:            "
            f"{len(packet.sources)}"
        )

        print(
            f"Claims:             "
            f"{len(packet.claims)}"
        )

        print(
            "Human review:       "
            + (
                "YES"
                if packet.requires_human_review
                else "NO"
            )
        )

        print()

        print(
            "SUMMARY"
        )

        print(
            "-------"
        )

        print(
            packet.summary
        )

        print()

        print(
            "CORE FINDING"
        )

        print(
            "------------"
        )

        print(
            packet.core_finding
        )

        print()

        print(
            "IMPORTANT NUANCE"
        )

        print(
            "----------------"
        )

        print(
            packet.important_nuance
            or "None"
        )

        print()

        print(
            "CLAIMS"
        )

        print(
            "------"
        )


        for index, claim in enumerate(
            packet.claims
        ):

            print(
                f"[{index}] {claim.claim}"
            )

            print(
                "    sources: "
                + str(
                    claim.source_indexes
                )
            )

            print(
                "    confidence: "
                + str(
                    claim.confidence
                )
            )

            print(
                "    sensitivity: "
                + str(
                    claim.sensitivity
                )
            )

            print(
                "    human review: "
                + (
                    "YES"
                    if claim.human_review_required
                    else "NO"
                )
            )

            print()


        print(
            "SOURCES"
        )

        print(
            "-------"
        )


        for index, source in enumerate(
            packet.sources
        ):

            print(
                f"[{index}] "
                f"{source.title}"
            )

            if source.publisher:

                print(
                    "    publisher: "
                    f"{source.publisher}"
                )

            if source.publication_date:

                print(
                    "    date: "
                    f"{source.publication_date}"
                )

            if source.url:

                print(
                    "    "
                    f"{source.url}"
                )

            print()


        print(
            "RECOMMENDED ANGLES"
        )

        print(
            "------------------"
        )

        for angle in (
            packet.recommended_angles
        ):

            print(
                "- "
                + angle
            )


        print()
        print(
            "PROHIBITED ANGLES"
        )

        print(
            "-----------------"
        )

        for angle in (
            packet.prohibited_angles
        ):

            print(
                "- "
                + angle
            )


        print()
        print(
            "=========================================="
        )

        print(
            " SECTION 3A LIVE RESEARCH: PASS"
        )

        print(
            "=========================================="
        )

        print()

        print(
            "Validated research packet stored "
            "in Supabase via HTTPS."
        )

        return 0


    except Exception as exc:

        message = str(
            exc
        )


        # Best-effort attempt tracking.
        if subject_id:

            try:

                with ResearchStore() as store:

                    store.mark_error(
                        subject_id=subject_id,
                        error=message,
                    )

            except Exception:

                pass


        print()
        print(
            "=========================================="
        )

        print(
            " RESEARCH: FAIL"
        )

        print(
            "=========================================="
        )

        print()

        print(
            type(exc).__name__
            + ": "
            + message
        )

        return 1


if __name__ == "__main__":

    raise SystemExit(
        main()
    )
