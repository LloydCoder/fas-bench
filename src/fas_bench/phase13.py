"""Phase 13 enterprise release-security policy primitives."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

REQUIRED_RELEASE_CONTROLS = (
    "content_addressed_release",
    "independent_verification",
    "reproducible_build",
    "artifact_provenance_attestation",
    "sbom_attestation",
    "secret_scan",
    "dependency_audit",
)


def validate_release_security_policy(
    controls: Mapping[str, bool],
) -> list[str]:
    return [
        f"missing or failed enterprise release control: {name}"
        for name in REQUIRED_RELEASE_CONTROLS
        if controls.get(name) is not True
    ]


def phase13_gate(
    controls: Mapping[str, bool],
    *,
    artifacts: Sequence[str],
) -> dict:
    errors = validate_release_security_policy(controls)
    if not artifacts:
        errors.append("release must contain at least one attestable artifact")
    return {
        "phase": "13",
        "status": "PASS" if not errors else "FAIL",
        "errors": sorted(set(errors)),
        "enterprise_security_claim": False,
        "requires_signed_provenance": True,
        "requires_sbom": True,
    }
