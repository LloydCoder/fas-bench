# Security Policy

FAS-Bench contains intentionally vulnerable benchmark cases and security-sensitive evaluation infrastructure. A security issue can affect benchmark integrity even when no production system is directly exposed.

## Private reporting

**Do not disclose security vulnerabilities, hidden-evaluation material, sandbox escapes, credential exposure, or oracle-compromise details in a public issue.**

Preferred path:

1. Use GitHub's private vulnerability reporting for this repository when it is enabled: https://github.com/LloydCoder/fas-bench/security/advisories/new
2. If private reporting is unavailable, contact the maintainer **@LloydCoder** privately through GitHub and state that the message is a security report.
3. Do not attach real credentials, private keys, hidden cases, or sensitive production data. Use synthetic/minimized reproduction material.

GitHub private vulnerability reporting is separate from SECURITY.md and must be enabled for the private-report form to accept submissions.

## What should be reported privately

Report issues such as:

- sandbox or host-execution escapes;
- Docker-socket, host-mount, credential, or network-isolation bypasses;
- evaluator or oracle compromise;
- hidden-corpus or official-answer leakage;
- contamination-control bypasses;
- release-manifest or provenance tampering;
- dependency or CI vulnerabilities that can affect released artifacts;
- unsafe parsing or denial-of-service conditions with meaningful security impact.

Intentional vulnerabilities inside synthetic benchmark cases are not, by themselves, repository vulnerabilities. Report a case-integrity defect when the case violates its documented isolation or ground-truth contract.

## Response targets

These are maintainer response targets, not guarantees:

| Stage | Target |
|---|---|
| Initial acknowledgement | within 3 business days |
| Initial triage | within 7 business days |
| Mitigation / coordinated disclosure plan | normally within 14 business days after triage |
| Public disclosure | coordinated with the reporter after a fix or mitigation is available, where appropriate |

Complex issues may require more time. The reporter will be informed when practical if the target cannot be met.

## Disclosure

Please allow reasonable time for investigation and remediation. Do not publish proof-of-concept details that would expose hidden benchmark material or materially weaken evaluation integrity before coordinated disclosure.

When a vulnerability is confirmed, maintainers may publish a GitHub Security Advisory, release notes, or a security notice containing the affected versions, impact, mitigation, and credit where the reporter agrees.

## Security invariants

Benchmark inputs and candidate submissions are untrusted.

The project must preserve:

- no direct host execution of candidate code;
- fail-closed secure execution;
- immutable container image references for dynamic execution;
- no privileged containers or Docker-socket exposure;
- bounded CPU, memory, PIDs, time, and output;
- isolated input/workspace/output handling;
- content-derived identities and artifact digests;
- deterministic validation;
- separation of observations, evidence, findings, verdicts, and ground truth;
- public/hidden corpus separation;
- FAS-Bench independence from evaluated products.

Container isolation is not claimed to be escape-proof. The host kernel, runtime, hardware, and Docker daemon remain part of the trusted computing base.

## Safe reporting checklist

Include:

- affected version or commit;
- affected component/path;
- security impact;
- minimal reproduction;
- required preconditions;
- whether the issue affects public or private benchmark material;
- any proposed mitigation.

Never include live secrets.
