# Phase 10 — Mutation Contract

Mutation is an integrity mechanism, not a filename-renaming exercise.

Each mutation declares an operator, parent case, output variant, semantic class, expected security delta, expected verdict delta, validation status, and artifact digest.

## Implemented operators

### Identifier mutation

Python `NAME` tokens are renamed while strings and comments are left untouched. The implementation uses Python's tokenizer rather than string replacement.

### Formatting mutation

The source is parsed and re-emitted with Python's AST unparser. The before/after AST is compared without location attributes. If the AST changes, the mutation is rejected.

### JSON key-order mutation

Objects are recursively sorted for deterministic serialization. This is an explicitly non-semantic representation mutation.

## Validation rule

A mutation operator is not ground truth. The trusted validator/oracle must establish the resulting security relation. The mutation schema therefore distinguishes `SEMANTICALLY_EQUIVALENT`, security-changing relations, and `INVALID`.

The current Phase 10 public corpus does not claim that all conceptual mutation classes are implemented. Future operators must provide a real transformation plus an oracle-backed semantic validation path before they enter an official release.

## Metrics

The schema supports mutation validity and semantic classes. Mutation kill/survival statistics should be computed from actual evaluated systems; no fabricated rates are shipped in this release.
