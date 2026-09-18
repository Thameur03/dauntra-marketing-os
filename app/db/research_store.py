from __future__ import annotations

from app.db.supabase_rest import (
    SupabaseREST,
)

from contracts.research import (
    ResearchPacket,
)

from contracts.subject import (
    SubjectCreate,
)


class ResearchStore:

    def __init__(self) -> None:

        self.db = SupabaseREST()


    def close(self) -> None:

        self.db.close()


    def __enter__(self):

        return self


    def __exit__(
        self,
        exc_type,
        exc,
        tb,
    ):

        self.close()


    def create_subject(
        self,
        subject: SubjectCreate,
    ) -> str:

        row = self.db.insert(

            "subjects",

            {
                "subject_text": (
                    subject.subject
                ),

                "note": (
                    subject.note
                ),

                "source": "founder",

                "content_family": (
                    subject
                    .content_family
                    .value
                ),

                "market": (
                    subject.market.value
                ),

                "language": (
                    subject.language.value
                ),

                "status": (
                    "RESEARCHING"
                ),
            },
        )


        return str(
            row["id"]
        )


    def save_packet(
        self,
        *,
        subject_id: str,
        packet: ResearchPacket,
        model: str,
    ) -> str:

        status = (

            "NEEDS_REVIEW"

            if packet.requires_human_review

            else "READY"
        )


        row = self.db.insert(

            "research_packets",

            {
                "subject_id": (
                    subject_id
                ),

                "status": status,

                "packet_json": (
                    packet.model_dump(
                        mode="json"
                    )
                ),

                "prompt_version": (
                    "research_v1"
                ),

                "model": model,
            },
        )


        self.db.update(

            "subjects",

            filters={
                "id": subject_id,
            },

            values={
                "status": "READY",
            },
        )


        return str(
            row["id"]
        )


    def mark_error(
        self,
        *,
        subject_id: str,
        error: str,
    ) -> None:

        self.db.update(

            "subjects",

            filters={
                "id": subject_id,
            },

            values={
                "status": "ERROR",
            },
        )


        self.db.insert(

            "system_errors",

            {
                "source": (
                    "research_engine"
                ),

                "entity_type": (
                    "subject"
                ),

                "entity_id": (
                    subject_id
                ),

                "error_code": (
                    "RESEARCH_FAILED"
                ),

                "error_message": (
                    error[:5000]
                ),
            },
        )


    def delete_subject(
        self,
        subject_id: str,
    ) -> None:

        self.db.delete(

            "subjects",

            filters={
                "id": subject_id,
            },
        )
