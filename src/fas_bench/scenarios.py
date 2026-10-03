"""Phase 18 scenario, environment, and agentic interaction contracts."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import StrEnum


_SHA256 = 64


class EventKind(StrEnum):
    OBSERVATION = "OBSERVATION"
    TOOL_CALL = "TOOL_CALL"
    TOOL_RESULT = "TOOL_RESULT"
    DECISION = "DECISION"
    ARTIFACT = "ARTIFACT"
    STATE_CHANGE = "STATE_CHANGE"
    FAILURE = "FAILURE"


def _valid_digest(value: str) -> bool:
    return (
        isinstance(value, str)
        and len(value) == _SHA256
        and value == value.lower()\n        and all(character in "0123456789abcdef" for character in value)
    )


@dataclass(frozen=True)
class EnvironmentSnapshot:
    environment_id: str
    os_family: str
    image_digest: str
    dependency_digest: str
    policy_digest: str
    network_policy: str


@dataclass(frozen=True)
class InteractionEvent:
    sequence: int
    kind: EventKind
    actor: str
    payload_digest: str
    environment_id: str
    turn: int = 0


@dataclass(frozen=True)
class EvaluationScenario:
    scenario_id: str
    version: str
    initial_state_digest: str
    environment: EnvironmentSnapshot
    events: tuple[InteractionEvent, ...]
    max_turns: int = 1

    def identity(self) -> str:
        payload = {
            "scenario_id": self.scenario_id,
            "version": self.version,
            "initial_state_digest": self.initial_state_digest,
            "environment": self.environment.__dict__,
            "events": [
                {
                    "sequence": e.sequence,
                    "kind": e.kind.value,
                    "actor": e.actor,
                    "payload_digest": e.payload_digest,
                    "environment_id": e.environment_id,
                    "turn": e.turn,
                }
                for e in self.events
            ],
            "max_turns": self.max_turns,
        }
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()


def validate_scenario(scenario: EvaluationScenario) -> list[str]:
    errors: list[str] = []
    if not isinstance(scenario.scenario_id, str) or not scenario.scenario_id.strip():
        errors.append("scenario_id is required")
    if not isinstance(scenario.version, str) or not scenario.version.strip():
        errors.append("version is required")
    if scenario.max_turns < 1:
        errors.append("max_turns must be positive")
    if not _valid_digest(scenario.initial_state_digest):
        errors.append("initial_state_digest must be a lowercase SHA-256 digest")

    environment = scenario.environment
    for name in ("environment_id", "os_family", "network_policy"):
        value = getattr(environment, name)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"environment {name} is required")
    for name in ("image_digest", "dependency_digest", "policy_digest"):
        if not _valid_digest(getattr(environment, name)):
            errors.append(f"environment {name} must be a lowercase SHA-256 digest")

    sequences = [event.sequence for event in scenario.events]
    if sequences != list(range(len(sequences))):
        errors.append("event sequence must be contiguous from zero")
    for event in scenario.events:
        if not isinstance(event.actor, str) or not event.actor.strip():
            errors.append(f"event {event.sequence} actor is required")
        if not _valid_digest(event.payload_digest):
            errors.append(
                f"event {event.sequence} payload_digest must be a lowercase SHA-256 digest"
            )
        if event.environment_id != environment.environment_id:
            errors.append("event environment identity mismatch")
        if event.turn < 0 or event.turn >= scenario.max_turns:
            errors.append(f"event {event.sequence} turn is outside max_turns")
    if len({event.sequence for event in scenario.events}) != len(scenario.events):
        errors.append("event sequence values must be unique")
    return sorted(set(errors))


def scenario_gate(scenarios: list[EvaluationScenario]) -> dict:
    errors = [
        f"{s.scenario_id}@{s.version}: {e}"
        for s in scenarios
        for e in validate_scenario(s)
    ]
    versions = [(s.scenario_id, s.version) for s in scenarios]
    if len(versions) != len(set(versions)):
        errors.append("duplicate scenario_id/version")
    return {
        "phase": "18",
        "status": "PASS" if scenarios and not errors else "FAIL",
        "scenario_count": len(scenarios),
        "errors": sorted(set(errors)),
        "execution_authority": "PHASE9_SECURE_EVAL",
        "host_execution": False,
    }
