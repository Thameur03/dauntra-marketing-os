from app.content_brain.versions import (
    generation_versions,
)

from app.db.content_store import (
    ContentStore,
)

from contracts.common import (
    ContentFamily,
    Platform,
)

from contracts.content import (
    XContent,
)

from contracts.content_package import (
    ContentItemEnvelope,
)


class FakeREST:

    def __init__(self):

        self.rows = []

        self.insert_calls = []


    def select(
        self,
        table,
        params=None,
    ):

        assert (
            table
            == "content_items"
        )

        return list(
            self.rows
        )


    def insert(
        self,
        table,
        payload,
    ):

        assert (
            table
            == "content_items"
        )


        self.insert_calls.append(
            payload
        )


        return [
            {
                **payload,
                "id": "content-1",
            }
        ]


def envelope():

    return ContentItemEnvelope(

        generation_key=(
            "a" * 64
        ),

        variant_key="default",

        research_prompt_version=(
            "research_v1"
        ),

        content_brain_version="3C-dev",

        requires_human_review=True,

        content=XContent(

            format="text",

            content_family=(
                ContentFamily.C02
            ),

            posts=[
                (
                    "A grounded training post."
                )
            ],

            claims_used=[],

            capabilities_used=[],
        ),
    )


def test_content_store_inserts_current_schema():

    db = FakeREST()

    store = ContentStore(
        db
    )


    versions = (
        generation_versions(
            Platform.X
        )
    )


    result = store.save(

        subject_id="subject-1",

        research_packet_id="packet-1",

        envelope=envelope(),

        model="fake-model",

        versions=versions,
    )


    assert (
        result.content_item_id
        == "content-1"
    )


    payload = (
        db.insert_calls[0]
    )


    assert (
        payload[
            "platform"
        ]
        == "x"
    )


    assert (
        payload[
            "status"
        ]
        == "NEEDS_HUMAN_REVIEW"
    )


    assert (
        payload[
            "content_json"
        ][
            "generation_key"
        ]
        == "a" * 64
    )


    assert (
        payload[
            "content_json"
        ][
            "content"
        ][
            "platform"
        ]
        == "x"
    )


def test_content_store_reuses_matching_generation_key():

    db = FakeREST()

    item = envelope()


    db.rows = [
        {
            "id": "existing-1",

            "status": (
                "NEEDS_HUMAN_REVIEW"
            ),

            "content_json": (
                item.model_dump(
                    mode="json"
                )
            ),
        }
    ]


    store = ContentStore(
        db
    )


    result = (
        store.find_existing(

            subject_id="subject-1",

            research_packet_id=(
                "packet-1"
            ),

            platform=(
                Platform.X
            ),

            content_family=(
                ContentFamily.C02
            ),

            generation_key=(
                "a" * 64
            ),
        )
    )


    assert result is not None

    assert (
        result.content_item_id
        == "existing-1"
    )
