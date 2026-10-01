# Phase 11 — Corpus Expansion and Security-Semantic Mutation

Phase 11 establishes the engineering contract for expanding FAS-Bench without weakening its evidence-first semantics.

## Exit contract

A Phase 11 corpus implementation MUST carry explicit category, difficulty, provenance, validation type, and lifecycle metadata; preserve canonical FAS case identity; distinguish public development data from held-out official evaluation data; reject invalid mutations; require an authoritative oracle for every security-changing mutation; retain deterministic artifact digests; and avoid claiming statistical representativeness from the public corpus.

The implementation gate is exposed by fas_bench.phase11.phase11_gate.

## Mutation rule

Security-changing relations cannot self-certify. An authoritative oracle must establish the intended security relation. This prevents a mutation generator from silently becoming a ground-truth authority.

## Scientific boundary

The Phase 11 engineering gate does not establish statistical representativeness. Public cases remain development data until independent oracle review and empirical measurement establish their validity.
