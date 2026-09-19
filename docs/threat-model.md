# FAS-Bench Threat Model

The benchmark itself is an attack surface.

## Assets

- host evaluator
- hidden ground truth
- benchmark cases
- scoring logic
- evaluation artifacts
- credentials and synthetic secrets
- result integrity
- reproducibility metadata

## Threats

- prompt injection through benchmark artifacts
- malicious dependencies
- data exfiltration
- sandbox escape
- evaluator compromise
- result tampering
- hidden-ground-truth disclosure
- benchmark contamination
- supply-chain compromise
- denial of service

## Baseline controls

- isolated execution
- synthetic credentials
- restricted outbound networking
- pinned dependencies
- immutable or content-addressed evaluation artifacts
- strict separation of public cases and hidden ground truth
- deterministic evaluator behavior
