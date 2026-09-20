# Phase 10 — Corpus and Release Contract

FAS-Bench Phase 10 adds a first-class integrity layer around the public development corpus. The initial twenty cases remain public development data and are never represented as a hidden official set.

## Corpus identity

A corpus is identified by canonical case content, not a directory name or version string. Case and repository artifacts are SHA-256 content-addressed. The Phase 10 validator composes the existing Phase 1–9 case validator with provenance, lifecycle, and contamination metadata checks.

Use:

`fas-bench corpus validate`

`fas-bench corpus stats`

## Lifecycle

The release lifecycle is:

DRAFT → AUTHOR_VALIDATION → PEER_REVIEW → ORACLE_VALIDATED → SECURITY_VALIDATED → REPRODUCIBILITY_VALIDATED → RELEASE_CANDIDATE → RELEASED → MAINTAINED → DEPRECATED → RETIRED.

The legacy Phase 1–9 `VALIDATED` value is preserved as a compatibility value and is mapped to Phase 10's `ORACLE_VALIDATED` for the initial public corpus. It does not mean RELEASED.

## Release manifest

`fas-bench benchmark release --version <version> --channel <development|release-candidate|public|official>`

produces a canonical manifest containing case, fixture, oracle, component, schema, mutation, provenance, validation, and release digests. Release identity is the digest of canonical metadata; timestamps are not identity inputs.

Verify with:

`fas-bench release verify release-manifest.json`

A manifest is invalid if any referenced case or component changes.

## Public versus official

The current repository contains only public development cases. An official release may reference a separately protected held-out corpus, but hidden material must not be committed to the public package. The release architecture records the channel and hidden-ground-truth flag without pretending that a hidden set exists today.

## Contamination

The contamination scanner checks forbidden paths, credential-shaped material, private-key material, and package/release boundaries. The independence audit also ensures the core package does not import FAS, ThreatFade, or Tinlance.

Contamination status is deliberately conservative: absence of a detected leak is not reported as proof that model-training contamination does not exist.

## Mutation

The mutation engine currently provides verified Python identifier and formatting-preserving operators. Python token rewriting preserves token semantics while allowing layout changes; the AST guard rejects formatting mutations that alter parsed structure. Security-changing operators are represented by the schema and must be validated against an authoritative oracle before release.

See `docs/phase10-mutation.md`.

## Limitations

The initial corpus has twenty public cases. It is not statistically representative. Hidden evaluation, temporal contamination measurement, empirical saturation studies, human-agreement studies, and signed release attestations require external governance and/or a separately protected evaluation service.
