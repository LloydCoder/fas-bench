# Phase 10.2 — Independent Verification

Phase 10.2 establishes an executable verification foundation around Phase 10.1 release controls.

## Layers

Implementation → independent observations → independent verifier → release certification.

The independent verifier does not invoke the production release verifier. It independently recomputes component and manifest digests and applies explicit policy checks.

## Reference semantics

Small reference functions cover canonical JSON, tree identity, path confinement, line-range extraction, graph identity and score boundaries. They are intentionally simpler than production code.

## Boundary

Phase 10.2 does not claim the complete evaluator is independently proven correct. Scientific validity, hidden-corpus integrity, host security and statistical representativeness remain external-review concerns.
