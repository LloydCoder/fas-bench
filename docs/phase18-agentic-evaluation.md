# Phase 18 — Scenario, Environment & Agentic Evaluation

Phase 18 defines deterministic scenario and interaction contracts for dynamic,
multi-turn, tool-using, and multi-agent evaluation.

## Contract

Every scenario binds an initial state to an environment identity. Every
interaction event is ordered, typed, digest-bound, and tied to that environment.
Scenario identity is content-derived.

The benchmark records observations and state transitions; it does not infer
security truth from an agent's narrative. Dynamic execution remains delegated to
the Phase 9 secure evaluator.

## Environment boundary

An environment snapshot identifies the OS family, immutable execution image,
dependency state, policy state, and network policy. Environment identity is part
of scenario identity so results from materially different environments cannot
be silently compared.

## Agentic scope

The event model supports tool calls, tool results, decisions, artifacts, state
changes, observations, and failures. This provides a stable seam for long-running
and multi-agent evaluators without turning FAS-Bench into a generic agent
runtime.
