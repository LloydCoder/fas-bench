# Phase 6 — Attack-Path & Security-Graph Engine

Phase 6 adds a deterministic, evidence-aware graph substrate between claim/evidence adjudication and later scoring/remediation phases.

## Pipeline

Case → Evidence → Claims → Security Graph → Effective Security Graph → Attack Paths → Boundary/Control Analysis → Graph Comparison → Verdict/Scoring

The graph engine is independent of FAS and consumes JSON data only. It never executes submitted code, expressions, or serialized Python objects.

## Canonical model

Nodes use the Phase 2 NodeType taxonomy. Edges use the Phase 2 EdgeType taxonomy. Optional Phase 6 metadata records abstraction level, security relevance, aliases, evidence references, security semantics, confidence, trust-boundary references, and identity transitions.

The existing public FAS-001…FAS-020 graphs remain valid. Phase 6 extends their schema rather than replacing it.

## Deterministic identity

Graphs are canonicalized by recursively sorting object keys, deterministically normalizing text, sorting semantically unordered collections, and ordering graph objects by stable semantic keys. The SHA-256 digest is computed over this canonical UTF-8 representation.

Presentation-only ordering therefore does not affect graph identity.

## Validation

Validation checks duplicate IDs, unsupported node/edge types, dangling references, malformed path continuity, case mismatch, evidence references, and explicit resource limits. Diagnostics use structured codes instead of opaque exceptions.

Default limits are deliberately finite:

- 20,000 nodes
- 50,000 edges
- 1,000 paths
- 256 nodes per extracted path
- 5 MB serialized input
- 250,000 traversal states

## Matching and scoring

Node matching uses semantic type plus conservative normalized identity. Declared aliases can establish equivalent representation without requiring raw identifier equality.

Edges match by semantic edge type and matched endpoint identity. Path completeness requires the ordered node/edge chain to agree; a correct sink without the required transition is therefore incomplete.

The provisional Phase 6 graph score is:

0.30 NodeF1 + 0.35 EdgeF1 + 0.20 PathCompleteness + 0.15 BoundaryCrossingF1

These weights are methodology configuration, not a claim of scientific validation.

Unsupported and contradictory submitted edges are reported separately and cannot manufacture expected graph credit.

## Paths and cycles

Path extraction is deterministic breadth-first traversal with sorted adjacency, visited-node state, path-length bounds, and a global traversal-state limit. Cycles cannot recurse indefinitely.

The minimal security path favors preservation of security-critical node types rather than treating the numerically shortest route as authoritative.

## Remediation interface

diff_graphs(before, after) reports added/removed/changed nodes and edges using canonical identities. This is the Phase 6 substrate for later remediation/regression analysis; it does not itself declare a remediation verdict.

## CLI

- fas-bench graph validate <graph>
- fas-bench graph normalize <graph>
- fas-bench graph digest <graph>
- fas-bench graph paths <graph>
- fas-bench graph diff <before> <after>
- fas-bench graph compare --expected <graph> --submission <graph>

## Scientific boundary

Graph correctness and verdict correctness remain separate dimensions. A system can reconstruct a graph accurately while choosing the wrong verdict, or guess a correct verdict while providing incomplete or unsupported graph reasoning.

The public corpus is development data. It is not a hidden evaluation set; held-out or private cases are required for contamination-resistant benchmark evaluation.
