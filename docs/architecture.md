# FAS-Bench Architecture

**Document role:** architecture and implementation model.  
**Authority:** docs/specification.md is normative; this document explains how implementation layers map to that contract.

## Purpose

FAS-Bench is an independent evaluation layer for security-analysis systems. Its architecture separates benchmark content, ground truth, system submissions, verification, scoring, and provenance so that no evaluated system becomes the benchmark reference implementation.

## Architectural layers

1. **Case layer** — repository/application fixture, scenario, environment assumptions, tests, and provenance.
2. **Ground-truth layer** — claims, evidence requirements, verdict, effective security graph, impact, remediation, and regression state.
3. **Submission layer** — normalized result emitted by an evaluated system.
4. **Verification layer** — deterministic checks against observable benchmark artifacts.
5. **Scoring layer** — multidimensional metrics, calibration, and efficiency.
6. **Provenance layer** — versions, hashes, environment, tools, and execution metadata.
7. **Security boundary layer** — isolated execution and hidden-ground-truth protection.

## Primary flow

case → analysis → structured submission → evidence verification → verdict evaluation → graph evaluation → remediation verification → regression evaluation → metrics/provenance

## Effective security model

The architecture must preserve the distinction between an apparent graph and an effective security graph. Source/configuration relationships are not sufficient to establish exploitability when authentication, authorization, IAM, resource policies, network policy, sandboxing, runtime restrictions, validation, or other controls block the path.

## Independence boundary

FAS-Bench MUST NOT import, require, execute, or derive ground truth from FAS. FAS is simply one candidate system that can submit results. The same benchmark contract must support other scanners, agents, and research systems.

## Data-flow boundaries

Public case material is an input to the evaluated system. Hidden ground truth and evaluator internals are inputs only to the evaluator. The evaluated system MUST NOT receive hidden ground truth.

The future schema layer is the interface between case data and evaluation. Phase 1 defines that interface conceptually; Phase 2 encodes it.

## Repository contract validation

Phase 1 includes a small contract vocabulary module and semantic tests. These validate canonical versions, verdicts, categories, difficulty levels, case IDs, gold-case membership, roadmap, required documentation, and independence assertions. This is repository validation, not the Phase 2 schema engine.

## Phase boundaries

Phase 1 defines semantics. Phase 2 encodes schemas. Phase 3 validates gold cases. Phases 4–7 implement deterministic evaluation subsystems. Phase 8 validates scoring empirically. Phase 9 hardens execution/reproducibility. Phase 10 expands the corpus and release/contamination controls.

## Security boundary

Case repositories, prompts, dependencies, fixtures, and dynamic artifacts are untrusted. Dynamic execution belongs in isolated environments with default-deny networking and synthetic credentials. No Phase 1 implementation should execute arbitrary benchmark case code.

## Implementation status

Phase 1 establishes the architecture and contract only. Complete evaluator, evidence engine, graph engine, scoring engine, and secure harness implementation remain later-phase work.
