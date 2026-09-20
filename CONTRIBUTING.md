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


## Phase 3 validation states

A case remains IN_REVIEW until schema, semantic, reproducibility, oracle, integrity, and security gates pass. Do not mark a case VALIDATED manually. Gold cases require mutation sensitivity. Dynamic cases must use controlled local targets and deterministic cleanup.

## Phase 4 evidence contributions

Evidence changes must remain deterministic and benchmark-independent. New expected evidence must identify an authoritative case artifact and structured fact where the fact can be deterministically observed. Add positive, negative, boundary, duplicate, contradiction, missing, tampering, and ordering-invariance tests as appropriate. Never execute submission evidence fields. Run the complete case validation and evidence test suite before opening a pull request.


## Phase 5 evaluator contributions

Finding and verdict semantics must remain deterministic and case-independent. Core evaluator code MUST NOT branch on individual case IDs. Case-specific truth belongs in case artifacts, claims, evidence, attack paths, controls, conditions, and remediation metadata. Changes must include positive, negative, contradiction, missing-evidence, cross-case, metamorphic, and tamper tests where applicable. The evaluator must consume Phase 4 evidence results rather than reimplement evidence verification. Final benchmark scoring remains deferred to Phase 8.
