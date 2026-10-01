# Phase 11.1 — Dynamic and Agentic Oracle Contract

Phase 11.1 extends FAS-Bench from corpus/mutation integrity into runtime-observable
security behavior without making the runtime oracle a self-certifying source of
ground truth.

## Design boundary

The dynamic oracle produces **observations**, not benchmark verdicts.

An observation records:

- the oracle identity;
- the case identity;
- observation type;
- execution status;
- execution/run identity;
- input, artifact, policy, and environment digests;
- timestamp;
- independently inspectable evidence.

The benchmark evaluator may use a validated observation as an input to the
case's authoritative ground-truth relation, but an oracle's claimed PASS/FAIL
must never silently become the final benchmark verdict.

## Security contract

Untrusted oracle code is not executed by this module. Runtime execution must
be delegated to the existing fail-closed secure-evaluation provider.

The provider must retain its existing isolation, resource, network, artifact,
identity, and policy controls. Infrastructure failure and policy violation
remain distinct from security observations.

## Exit gate

The Python gate is fas_bench.phase11_1.dynamic_oracle_gate.

The gate deliberately does not claim:

- universal runtime isolation;
- correctness of an oracle implementation;
- statistical representativeness;
- hidden-corpus integrity;
- final benchmark ground-truth validity.

Those claims require the later validation and independent-review phases.
