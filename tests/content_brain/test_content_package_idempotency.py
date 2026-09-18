from __future__ import annotations

from app.content_brain.package import (
    _generation_key,
    build_content_package,
)

from app.content_brain.packet_view import (
    prepare_writer_packet,
)

from app.content_brain.versions import (
    generation_versions,
)

from app.db.content_store import (
    StoredContentItem,
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

from tests.content_brain.test_content_package import (
    packet,
)


class NeverCallLLM:

    @property
    def model_name(self):

        return "fake-package-model"


    def generate_json(
        self,
        **kwargs,
    ):

        raise AssertionError(
            "LLM should not be called "
            "when idempotent content exists."
        )


    def generate_structured(
        self,
        **kwargs,
    ):

        raise AssertionError(
            "LLM should not be called."
        )


class ReuseStore:

    def __init__(
        self,
        stored,
    ):

        self.stored = stored


    def find_existing(
        self,
        **kwargs,
    ):

        assert (
            kwargs[
                "generation_key"
            ]
            == self.stored
            .envelope
            .generation_key
        )

        return self.stored


    def save(
        self,
        **kwargs,
    ):

        raise AssertionError(
            "save should not run "
            "for reused content."
        )


def test_existing_generation_skips_model_call():

    research = packet()

    writer_packet = (
        prepare_writer_packet(
            research
        )
    )


    key = _generation_key(

        subject_id="subject-1",

        research_packet_id=(
            "packet-1"
        ),

        packet=writer_packet,

        platform=Platform.X,

        content_family=(
            ContentFamily.C02
        ),

        capability_ids=[],

        model="fake-package-model",

        variant_key="default",
    )


    versions = (
        generation_versions(
            Platform.X
        )
    )


    envelope = (
        ContentItemEnvelope(

            generation_key=key,

            variant_key="default",

            research_prompt_version=(
                versions
                .research_prompt_version
            ),

            content_brain_version=(
                versions
                .content_brain_version
            ),

            requires_human_review=True,

            content=XContent(

                format="text",

                content_family=(
                    ContentFamily.C02
                ),

                posts=[
                    (
                        "Previously generated "
                        "content."
                    )
                ],

                claims_used=[],

                capabilities_used=[],
            ),
        )
    )


    store = ReuseStore(

        StoredContentItem(

            content_item_id=(
                "existing-1"
            ),

            database_status=(
                "NEEDS_HUMAN_REVIEW"
            ),

            envelope=envelope,
        )
    )


    result = build_content_package(

        subject_id="subject-1",

        research_packet_id="packet-1",

        packet=research,

        content_family=(
            ContentFamily.C02
        ),

        platforms=[
            Platform.X
        ],

        llm=NeverCallLLM(),

        store=store,
    )


    assert (
        result.build_status
        == "COMPLETE"
    )


    assert (
        result.items[0]
        .status
        == "REUSED"
    )


    assert (
        result.items[0]
        .content_item_id
        == "existing-1"
    )
