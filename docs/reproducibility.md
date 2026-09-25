# Reproducibility Contract

Case identity, corpus identity and release-manifest identity are deterministic content identities. Runtime duration is not part of deterministic identity.

Equivalent source trees must produce the same release manifest. Environment reports may record Python, operating system, architecture, dependency versions and container identity, but environment reports are not themselves content identity.

Package byte reproducibility depends on the controlled build environment and build backend. Phase 10.2 verifies project-controlled inputs and clean-install behavior without claiming universal byte-for-byte reproducibility across arbitrary toolchains.

Supported semantic environments are Python 3.12 and 3.13. Secure-container semantics are Linux/Docker-specific and are not claimed equivalent on every operating system.
