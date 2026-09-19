# Contributing to FAS-Bench
**Authority:** docs/specification.md.

Contributions must preserve evidence-first evaluation, exploitability semantics, effective security boundaries, alternate-path analysis, reproducibility, and independence from evaluated systems.

## Phase 2 contract
Schema changes require tests, fixtures, documentation, and compatibility review. New semantics must be proposed as specification changes. JSON Schema remains the serialized contract; semantic invariants belong in the validator.

## Independence
FAS-Bench MUST NOT import, require, execute, or derive ground truth from FAS.

## Security
Treat benchmark inputs as untrusted. Do not execute case code on the host, use real credentials, or allow uncontrolled external networking.

## CI
Formatting, linting, tests, schema validation, build, package import, and repository consistency checks must remain green.

## Phase 3 case contributions
New or changed cases must include a falsifiable security hypothesis, explicit attacker model, synthetic credentials only, controlled environment, structured ground truth, deterministic oracle, limitations, and case version. Public cases are development data; do not commit hidden evaluation answers. Run `fas-bench cases validate-all` and the gold reproduction checks before opening a pull request.
