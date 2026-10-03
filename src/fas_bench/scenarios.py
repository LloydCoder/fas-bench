"""Phase 18 scenario, environment, and agentic interaction contracts."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import StrEnum


class EventKind(StrEnum):
    OBSERVATION = "OBSERVATION"
    TOOL_CALL = "TOOL_CALL"
    TOOL_RESULT = "TOOL_RESULT"
    DECISION = "DECISION"
    ARTIFACT = "ARTIFACT"
    STATE_CHANGE = "STATE_CHANGE"
    FAILURE = "FAILURE"


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
                {"sequence": e.sequence, "kind": e.kind.value, "actor": e.actor,
                 "payload_digest": e.payload_digest, "environment_id": e.environment_id}
                for e in self.events
            ],
            "max_turns": self.max_turns,
        }
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()


def validate_scenario(scenario: EvaluationScenario) -> list[str]:
    errors: list[str] = []
    if scenario.max_turns < 1:
        errors.append("max_turns must be positive")
    if not scenario.initial_state_digest:
        errors.append("initial_state_digest is required")
    if scenario.environment.environment_id == "":
        errors.append("environment_id is required")
    sequences = [event.sequence for event in scenario.events]
    if sequences != list(range(len(sequences))):
        errors.append("event sequence must be contiguous from zero")
    if any(event.environment_id != scenario.environment.environment_id for event in scenario.events):
        errors.append("event environment identity mismatch")
    return sorted(set(errors))


def scenario_gate(scenarios: list[EvaluationScenario]) -> dict:
    errors = [f"{s.scenario_id}: {e}" for s in scenarios for e in validate_scenario(s)]
    ids = [s.scenario_id for s in scenarios]
    if len(ids) != len(set(ids)):
        errors.append("duplicate scenario_id")
    return {
        "phase": "18",
        "status": "PASS" if scenarios and not errors else "FAIL",
        "scenario_count": len(scenarios),
        "errors": sorted(set(errors)),
        "execution_authority": "PHASE9_SECURE_EVAL",
        "host_execution": False,
    }
