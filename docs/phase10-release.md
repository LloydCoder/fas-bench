# Phase 10 — Release Procedure

1. Freeze the intended case population.
2. Run `fas-bench corpus validate`.
3. Run legacy corpus and gold validation.
4. Run contamination and independence audits.
5. Run mutation tests.
6. Build the release manifest.
7. Verify the manifest against the source tree.
8. Build wheel and source distribution in clean CI.
9. Install the built wheel and execute CLI smoke tests.
10. Review documentation, schema versions, changelog, and known limitations.
11. Publish only artifacts whose digests match the manifest.

Release channels are development, release-candidate, public, and official. The public repository currently supports development/public practice artifacts; it does not pretend that a hidden official corpus is present.

## Historical compatibility

A result must retain the benchmark, scoring, evaluator, harness, schema, and case-population versions with which it was produced. New semantics require a new version rather than silently reinterpreting historical results.


## Phase 10.1 release-integrity rules

Release verification independently recomputes component, case, fixture, oracle, and manifest digests. The manifest's `validation_status` field is metadata and is never proof of validation. A SHA-256 release digest establishes content integrity, not authenticity or a cryptographic signature. The public repository cannot qualify itself as an official held-out release; official evaluation requires separately controlled evaluation infrastructure.

<!-- Phase 10.1 release-integrity contract -->
