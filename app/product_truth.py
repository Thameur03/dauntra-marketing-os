from __future__ import annotations

from dataclasses import dataclass

from app.config_loader import (
    load_capability_manifest,
)


@dataclass(frozen=True)
class CapabilitySummary:
    allowed: tuple[str, ...]
    blocked: tuple[str, ...]


@dataclass(frozen=True)
class CapabilityMarketingContext:
    capability_id: str
    display_name: str
    status: str
    description: str
    allowed_claims: tuple[str, ...]
    limitations: tuple[str, ...]
    prohibited_claims: tuple[str, ...]


def _features() -> dict:
    manifest = load_capability_manifest()

    features = manifest.get(
        "features",
        {},
    )

    if not isinstance(
        features,
        dict,
    ):
        raise ValueError(
            "Capability manifest features "
            "must be a mapping."
        )

    return features


def capability_summary() -> CapabilitySummary:
    features = _features()

    allowed: list[str] = []
    blocked: list[str] = []

    for capability_id, config in features.items():

        if not isinstance(
            config,
            dict,
        ):
            continue

        if config.get(
            "marketing_allowed",
            False,
        ):
            allowed.append(
                capability_id
            )

        else:
            blocked.append(
                capability_id
            )

    return CapabilitySummary(
        allowed=tuple(
            sorted(
                allowed
            )
        ),
        blocked=tuple(
            sorted(
                blocked
            )
        ),
    )


def assert_capabilities_allowed(
    capabilities: list[str],
) -> None:
    features = _features()

    for capability in capabilities:

        config = features.get(
            capability
        )

        if config is None:
            raise ValueError(
                "Unknown DAUNTRA capability: "
                f"{capability}"
            )

        if not isinstance(
            config,
            dict,
        ):
            raise ValueError(
                "Invalid capability configuration: "
                f"{capability}"
            )

        if not config.get(
            "marketing_allowed",
            False,
        ):
            raise ValueError(
                "DAUNTRA capability is not approved "
                f"for marketing: {capability}"
            )


def capability_marketing_context(
    capability_id: str,
) -> CapabilityMarketingContext:
    assert_capabilities_allowed(
        [
            capability_id,
        ]
    )

    config = _features()[
        capability_id
    ]

    def string_list(
        key: str,
    ) -> tuple[str, ...]:

        value = config.get(
            key,
            [],
        )

        if not isinstance(
            value,
            list,
        ):
            return ()

        return tuple(
            str(item).strip()
            for item in value
            if str(item).strip()
        )


    return CapabilityMarketingContext(
        capability_id=capability_id,

        display_name=str(
            config.get(
                "display_name",
                capability_id,
            )
        ).strip(),

        status=str(
            config.get(
                "status",
                "unknown",
            )
        ).strip(),

        description=str(
            config.get(
                "description",
                "",
            )
        ).strip(),

        allowed_claims=string_list(
            "allowed_claims"
        ),

        limitations=string_list(
            "limitations"
        ),

        prohibited_claims=string_list(
            "prohibited_claims"
        ),
    )


def capability_marketing_contexts(
    capability_ids: list[str],
) -> tuple[
    CapabilityMarketingContext,
    ...,
]:
    # Preserve caller order while removing duplicates.
    unique = list(
        dict.fromkeys(
            capability_ids
        )
    )

    return tuple(
        capability_marketing_context(
            capability_id
        )
        for capability_id
        in unique
    )
