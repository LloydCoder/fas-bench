# Security Policy

FAS-Bench intentionally contains security-sensitive test cases, vulnerable fixtures, attacker-controlled inputs, and simulated credentials.

## Reporting a vulnerability

If you discover a vulnerability in the benchmark infrastructure, evaluator, CI configuration, dependency chain, or repository controls that could compromise the host or invalidate benchmark results, please report it privately to the repository maintainer rather than publishing exploit details in an issue.

## Benchmark integrity

Issues that only affect the security behavior of an intentionally vulnerable benchmark case are generally benchmark-content issues, not infrastructure vulnerabilities.

Do not include real credentials, personal data, or real external targets in benchmark cases.

## Safe execution

Benchmark cases must be treated as untrusted data and executed only in appropriately isolated environments.
