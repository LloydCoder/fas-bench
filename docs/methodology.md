# FAS-Bench Methodology

## Phase 8 measurement

Phase 8 calculates decomposable case metrics and aggregate statistics from deterministic Phase 4–7 outputs. Evidence, verdict, graph, remediation, calibration, and integrity remain separately inspectable. Brier and ECE are reported as lower-is-better diagnostics and explicitly transformed before contributing to the provisional composite. Bootstrap intervals record seed, resample count, confidence level, and method. The initial 20 public development cases are not statistically representative; small-sample results must retain n and uncertainty.
**Role:** research methodology.
**Authority:** docs/specification.md.

## Signal, finding, claim, evidence, verdict
A signal is an observation. A finding groups a reported condition. A claim is an assertion. Evidence supports or contradicts the claim. A verdict adjudicates security state. These are intentionally separate so persuasive prose or scanner output cannot become verified truth automatically.

## Attack paths and effective security
Paths are ordered references over stable graph IDs. Controls can invalidate apparent paths; graph cycles are allowed, while path traversal is explicitly ordered.

## Remediation and regression
Remediation records a security-property change and revalidation. Regression records loss of a previously secure property. Neither is reduced to a generic finding label.

## Structural versus semantic validation
JSON Schema handles local structure. Semantic validation handles relationships that require multiple objects.

## Scientific validity
Scoring weights, evidence-integrity thresholds, generalization, taxonomy completeness, and contamination resistance remain provisional research questions.

## Phase 3 corpus methodology
The validated initial cases prioritize causal clarity and reproducibility over codebase size. Synthetic cases make effective security boundaries observable and deterministic. Ground truth is triangulated from structured claims/evidence, attack-path representation, and an oracle-derived observed state. The public development corpus does not remove contamination risk; future evaluation requires held-out cases or undisclosed mutations.


## Phase 3 validation methodology

The corpus is a controlled experimental set, not a statistical sample of real-world vulnerabilities. Gold cases combine structured security-model evidence with executable security-property tests. Dynamic oracles exercise local synthetic targets; mutation tests verify oracle sensitivity to security-semantic changes. Public ground truth is deliberately acknowledged as a contamination risk, so later evaluation must use held-out or undisclosed variants.


## Phase 4 methodology

FAS-Bench separates observation, evidence, claim, security property, and verdict. Phase 4 verifies only the evidence layer. Canonicalization removes representation differences without erasing security-relevant distinctions. Evidence identity is content-derived, duplicate evidence is preserved for auditability but cannot inflate coverage, and missing evidence is not treated as invalid evidence. Later phases consume the structured result rather than reimplementing evidence resolution.


## Phase 5 adjudication methodology

FAS-Bench separates detection from adjudication. A scanner can correctly detect a suspicious source/sink, dependency, tool, or function while the security condition is blocked by an effective boundary. Phase 5 therefore matches findings by structured category and claims, verifies evidence through Phase 4, resolves reachability/control/precondition state from declarative case data, and only then evaluates the submitted verdict.

UNKNOWN means the authoritative condition cannot be concluded. CONDITIONAL requires explicit case-defined conditions. Remediation verdicts are based on security-property state, not the presence of a patch string. Correct verdict and evidence support remain separate dimensions for later scoring.


## Phase 6 graph methodology

Node matching alone is insufficient because a system can identify the right entities without proving how control or authority moves between them. Edge matching alone is insufficient because a graph can contain locally correct relationships while omitting the complete attack chain. Shortest-path matching is insufficient because a shorter route can erase an authorization or trust-boundary transition that determines exploitability. Text similarity is insufficient because equivalent security reasoning may be represented with different labels while materially different privilege or control semantics may share similar prose.

Phase 6 therefore evaluates semantic nodes, typed directed edges, ordered attack paths, trust-boundary crossings, evidence support, and contradictions separately. The graph score is deliberately explicit and versioned but remains provisional until later calibration work.


## Phase 7 methodology

Patch presence is not evidence of remediation. The evaluator compares security state, not source-text appearance. Path lifecycle is derived from semantic path status; alternate routes are classified by impact identity; security-critical control weakening is independently exposed; functional tests prevent trivial overblocking from receiving a complete remediation result. All raw dimensions remain available so Phase 8 can calibrate thresholds and weighting without rewriting the oracle.


## Phase 9 reproducibility and execution security
Dynamic execution is treated as an experimental measurement boundary. Run identity is content-derived from the case, submission, input digest, and execution policy. Candidate code is isolated from evaluator secrets and host state. Results preserve the exact policy, immutable image reference, execution status, timing, exit code, output limits, artifact hashes, and input digest. The harness fails closed rather than converting missing isolation into a benchmark result.


## Phase 10 methodology

Phase 10 measures benchmark integrity rather than adding another security-agent score. Corpus validity is checked recursively; case identity is content-derived; mutations declare semantic relationships; contamination scans are deterministic; release manifests bind the population and artifacts; and public reports explicitly expose limitations.

The initial twenty cases are a development corpus and are not asserted to be statistically representative. Mutation validity, contamination cleanliness, and benchmark saturation require empirical evidence. The repository therefore reports NOT_ASSESSED where the current artifacts cannot establish those properties.
