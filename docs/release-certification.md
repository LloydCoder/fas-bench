# Release Certification

Certification is derived from observations and never copied from a manifest self-report.

States: NOT_CERTIFIED, VERIFIED, CERTIFIED, REVOKED.

A public repository cannot certify a hidden official corpus. Official held-out evaluation requires separately controlled infrastructure.

## External verification

Checkout the exact source commit, create a clean Python 3.12+ environment, install dependencies, run format/lint/tests/corpus validation/gold reproduction, build the manifest, run the independent verifier, reproduce the manifest, and record source commit, manifest digest, environment and limitations.

## Revocation

A release may be revoked after discovery of incorrect ground truth, artifact corruption, compromised provenance, a critical security defect or reproducibility failure. Revocation changes status without rewriting historical identity.
