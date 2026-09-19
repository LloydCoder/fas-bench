# Security Policy

**Document role:** security reporting and benchmark-integrity policy.  
**Authority:** docs/specification.md defines benchmark security requirements.

FAS-Bench intentionally contains security-sensitive test cases, vulnerable fixtures, attacker-controlled inputs, and simulated credentials.

## Reporting vulnerabilities

Report vulnerabilities in benchmark infrastructure, evaluator code, CI configuration, dependency chains, or repository controls that could compromise a host or invalidate benchmark results privately to the repository maintainer.

Do not publish exploit details that could compromise hidden evaluation infrastructure before coordinated remediation.

## Benchmark cases are intentional

A vulnerability that exists solely because a case is intentionally designed to model a security condition is generally benchmark content, not an accidental infrastructure vulnerability. Case behavior must remain isolated from benchmark infrastructure.

## Do not include real secrets

Contributors MUST NOT include real credentials, personal data, production configuration, or real external targets. Use synthetic secrets and isolated fixtures.

## Safe execution

Benchmark cases are untrusted inputs. Arbitrary case code MUST NOT execute directly on a development or evaluation host. Dynamic execution MUST be isolated and outbound networking MUST default to denied unless a case explicitly requires controlled networking.

## Ground-truth protection

Do not disclose hidden ground truth, hidden tests, evaluator internals, or private evaluation artifacts. Accidental disclosure that could affect benchmark validity should be reported privately.

## Scope

This policy covers the FAS-Bench software, repository controls, CI/evaluation infrastructure, and benchmark-integrity mechanisms. It does not classify intentionally vulnerable case behavior as a product defect.
