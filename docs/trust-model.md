# Trust Model

FAS-Bench separates benchmark implementation, candidate-controlled data, secure execution and release infrastructure.

Candidate submissions, evidence, graphs, remediation claims, scores, artifacts and metadata are untrusted. Candidate-declared scores or digests do not become authoritative merely because they are present.

Commit and digest verification provide integrity evidence, not authenticity or scientific correctness. Secure execution depends on the host kernel and container runtime. Container isolation is not an escape-proof guarantee.

GitHub Actions is an infrastructure trust boundary: a successful workflow is evidence of that execution, not proof of every scientific assumption. SHA-256 provides content integrity, not authenticity or a signature. The public twenty-case corpus is not statistically representative.
