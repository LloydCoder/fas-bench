from fas_bench.scenarios import (
    EnvironmentSnapshot, EvaluationScenario, EventKind, InteractionEvent,
    scenario_gate,
)


def scenario(events=()):
    env = EnvironmentSnapshot("env-1", "linux", "sha256:image", "sha256:deps", "sha256:policy", "DENY")
    return EvaluationScenario("S-1", "1.0", "a" * 64, env, tuple(events), 4)


def test_scenario_identity_is_stable():
    assert scenario().identity() == scenario().identity()


def test_events_must_be_contiguous():
    e = InteractionEvent(1, EventKind.OBSERVATION, "agent", "b" * 64, "env-1")
    assert scenario_gate([scenario((e,))])["status"] == "FAIL"


def test_environment_identity_is_bound_to_events():
    e = InteractionEvent(0, EventKind.TOOL_CALL, "agent", "b" * 64, "other")
    assert scenario_gate([scenario((e,))])["status"] == "FAIL"


def test_valid_scenario_passes():
    e = InteractionEvent(0, EventKind.OBSERVATION, "agent", "b" * 64, "env-1")
    assert scenario_gate([scenario((e,))])["status"] == "PASS"
