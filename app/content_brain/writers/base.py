from __future__ import annotations

from typing import Any

from app.content_brain.prompting import (
    build_writer_prompt,
    writer_system_instruction,
)

from app.content_brain.validators import (
    PlatformContent,
    validate_content_grounding,
)

from app.content_brain.wire_schemas import (
    FACEBOOK_SCHEMA,
    INSTAGRAM_SCHEMA,
    TIKTOK_SCHEMA,
    X_SCHEMA,
)

from app.llm.base import (
    StructuredLLM,
)

from app.product_truth import (
    capability_marketing_contexts,
)

from contracts.common import (
    ContentFamily,
    Platform,
)

from contracts.content import (
    FacebookContent,
    InstagramCarouselContent,
    TikTokVideoContent,
    XContent,
)

from contracts.research import (
    ResearchPacket,
)


MODELS = {
    Platform.INSTAGRAM: (
        InstagramCarouselContent
    ),

    Platform.TIKTOK: (
        TikTokVideoContent
    ),

    Platform.X: (
        XContent
    ),

    Platform.FACEBOOK: (
        FacebookContent
    ),
}


SCHEMAS = {
    Platform.INSTAGRAM: (
        INSTAGRAM_SCHEMA
    ),

    Platform.TIKTOK: (
        TIKTOK_SCHEMA
    ),

    Platform.X: (
        X_SCHEMA
    ),

    Platform.FACEBOOK: (
        FACEBOOK_SCHEMA
    ),
}



class GeneratedContentValidationError(ValueError):

    def __init__(
        self,
        *,
        content: PlatformContent,
        reason: str,
    ) -> None:

        self.content = content
        self.reason = reason

        super().__init__(
            reason
        )



class PlatformWriter:

    def __init__(
        self,
        *,
        llm: StructuredLLM,
        platform: Platform,
    ) -> None:

        if platform not in MODELS:

            raise ValueError(
                "Unsupported automated writer platform: "
                f"{platform}"
            )


        self.llm = llm
        self.platform = platform


    def _normalize_output(
        self,
        raw: dict[str, Any],
        *,
        content_family: ContentFamily,
    ) -> dict[str, Any]:

        payload = dict(
            raw
        )


        payload[
            "platform"
        ] = self.platform.value

        payload[
            "content_family"
        ] = content_family.value


        if (
            self.platform
            == Platform.INSTAGRAM
        ):

            payload[
                "format"
            ] = "carousel"


            for slide in payload.get(
                "slides",
                [],
            ):

                if (
                    slide.get(
                        "headline"
                    )
                    == ""
                ):

                    slide[
                        "headline"
                    ] = None


                if (
                    slide.get(
                        "emphasis"
                    )
                    == ""
                ):

                    slide[
                        "emphasis"
                    ] = None


        elif (
            self.platform
            == Platform.TIKTOK
        ):

            payload[
                "format"
            ] = "video"


        if payload.get(
            "cta"
        ) == "":

            payload[
                "cta"
            ] = None


        return payload


    def write(
        self,
        *,
        packet: ResearchPacket,
        content_family: ContentFamily,
        capability_ids: list[str] | None = None,
    ) -> PlatformContent:

        capability_ids = (
            capability_ids
            or []
        )


        if (
            content_family
            == ContentFamily.C04
            and not capability_ids
        ):

            raise ValueError(
                "C04 requires at least one explicitly "
                "selected approved capability."
            )


        capabilities = (
            capability_marketing_contexts(
                capability_ids
            )
        )


        prompt = build_writer_prompt(
            platform=self.platform,
            content_family=(
                content_family
            ),
            packet=packet,
            capabilities=capabilities,
        )


        raw = self.llm.generate_json(
            prompt=prompt,
            schema=SCHEMAS[
                self.platform
            ],
            system_instruction=(
                writer_system_instruction(
                    self.platform
                )
            ),
        )


        payload = (
            self._normalize_output(
                raw,
                content_family=(
                    content_family
                ),
            )
        )


        model = MODELS[
            self.platform
        ]


        content = (
            model.model_validate(
                payload
            )
        )


        try:

            validate_content_grounding(
                content=content,
                packet=packet,
                requested_capabilities=(
                    capability_ids
                ),
            )


        except ValueError as exc:

            raise GeneratedContentValidationError(
                content=content,
                reason=str(exc),
            ) from exc


        return content
