# Phase 13 — Enterprise Security and Operational Hardening

Phase 13 strengthens the release boundary with verifiable supply-chain controls.

## Required release controls

Every enterprise release must provide evidence for:

- content-addressed release identity;
- independent verification;
- reproducible package build;
- signed artifact provenance;
- signed SBOM attestation;
- repository secret-pattern scanning;
- dependency vulnerability auditing.

The implementation exposes these as explicit policy controls rather than
treating a successful build as proof of security.

## Provenance and SBOM

GitHub artifact attestations bind release artifacts to their workflow, source
commit, repository, and build context. SBOM attestations bind an artifact to
its machine-readable dependency inventory.

Consumers should verify attestations rather than merely checking that an
attestation exists. Provenance is evidence about how an artifact was produced;
it is not evidence that the artifact is intrinsically secure.

## Operational boundary

Phase 13 does not claim host/kernel security, universal supply-chain security,
or vulnerability-free dependencies. Those remain explicit trust and risk
boundaries.

The Phase 13 gate is an implementation policy gate. It cannot manufacture
external signatures, independent review, or incident-response evidence.
