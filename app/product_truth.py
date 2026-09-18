from __future__ import annotations

from dataclasses import dataclass

from app.config_loader import load_capability_manifest


@dataclass(frozen=True)
class CapabilitySummary:
    allowed: tuple[str, ...]
    blocked: tuple[str, ...]


def capability_summary() -> CapabilitySummary:
    manifest = load_capability_manifest()

    features = manifest.get(
        "features",
        {},
    )

    allowed: list[str] = []
    blocked: list[str] = []

    for capability_id, config in features.items():

        if not isinstance(config, dict):
            continue

        if config.get(
            "marketing_allowed",
            False,
        ):
            allowed.append(capability_id)
        else:
            blocked.append(capability_id)

    return CapabilitySummary(
        allowed=tuple(sorted(allowed)),
        blocked=tuple(sorted(blocked)),
    )


def assert_capabilities_allowed(
    capabilities: list[str],
) -> None:

    manifest = load_capability_manifest()

    features = manifest.get(
        "features",
        {},
    )

    for capability in capabilities:

        config = features.get(capability)

        if config is None:
            raise ValueError(
                f"Unknown DAUNTRA capability: {capability}"
            )

        if not config.get(
            "marketing_allowed",
            False,
        ):
            raise ValueError(
                "DAUNTRA capability is not approved "
                f"for marketing: {capability}"
            )
