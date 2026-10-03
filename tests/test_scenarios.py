from fas_bench.scenarios import (
    EnvironmentSnapshot,
    EvaluationScenario,
    EventKind,
    InteractionEvent,
    scenario_gate,
)


def scenario(events=()):
    env = EnvironmentSnapshot("env-1", "linux", "a" * 64, "b" * 64, "c" * 64, "DENY")
    return EvaluationScenario("S-1", "1.0", "d" * 64, env, tuple(events), 4)


def event(sequence=0, environment_id="env-1"):
    return InteractionEvent(sequence, EventKind.OBSERVATION, "agent", "e" * 64, environment_id)


def test_scenario_identity_is_stable():
    assert scenario().identity() == scenario().identity()


def test_events_must_be_contiguous():
    assert scenario_gate([scenario((event(sequence=1),))])["status"] == "FAIL"


def test_environment_identity_is_bound_to_events():
    assert scenario_gate([scenario((event(environment_id="other"),))])["status"] == "FAIL"


def test_invalid_environment_digest_fails_closed():
    env = EnvironmentSnapshot("env-1", "linux", "sha256:image", "b" * 64, "c" * 64, "DENY")
    invalid = EvaluationScenario("S-1", "1.0", "d" * 64, env, (), 4)
    assert scenario_gate([invalid])["status"] == "FAIL"


def test_multiple_events_can_share_a_turn():
    valid = scenario(tuple(event(sequence=i) for i in range(5)))
    assert scenario_gate([valid])["status"] == "PASS"


def test_valid_scenario_passes():
    assert scenario_gate([scenario((event(),))])["status"] == "PASS"


def test_event_turn_is_bounded():
    invalid = scenario((event(),))
    invalid = EvaluationScenario(
        invalid.scenario_id,
        invalid.version,
        invalid.initial_state_digest,
        invalid.environment,
        (InteractionEvent(0, EventKind.OBSERVATION, "agent", "e" * 64, "env-1", 4),),
        invalid.max_turns,
    )
    assert scenario_gate([invalid])["status"] == "FAIL"
