# FAS-Bench Threat Model
**Role:** benchmark security and research threat model.
**Authority:** docs/specification.md.

## Phase 2 schema threats
Threats include oversized objects, pathological nesting, enormous arrays, graph-size denial of service, duplicate identifiers, reference explosion, malicious artifact metadata, parser differentials, unsupported versions, remote $ref dependencies, and evaluator denial of service.

## Controls
Validation is data-only; artifact content is never executed; arbitrary remote references are not retrieved; top-level contract objects are closed; IDs and references are semantically checked; deployment-specific size/depth/graph limits should be bounded.

## Ground-truth protection
Expected verdicts, hidden evidence, evaluator internals, and hidden tests remain outside the public submission contract.

## Limits
Phase 2 does not prove sandbox security, evaluator integrity, contamination resistance, or scientific validity. Those are later-phase empirical/security concerns.

## Phase 3 case threats
Case execution introduces risks from malicious benchmark artifacts, dependency confusion, network escape, host escape, secret leakage, oracle manipulation, and ground-truth leakage. The initial corpus therefore uses synthetic state, no uncontrolled network dependency, no real credentials or cloud accounts, and deterministic local oracles. Future dynamic cases must add stronger isolation before execution of arbitrary benchmark code.


## Phase 3 case execution controls

The initial dynamic gold cases execute only local synthetic HTTP targets bound to loopback. They do not require public Internet access, real credentials, cloud accounts, host mounts, Docker sockets, or privileged containers. Case validation treats oracle failures as infrastructure errors rather than security verdicts. The Phase 3 oracle harness executes case oracles in a pinned, network-disabled, read-only container with dropped capabilities, no-new-privileges, CPU/memory/PID limits, and no host Docker socket. These controls apply to the CI-validated initial public corpus.


## Phase 4 evidence-engine threats and controls

The evaluator treats submissions and case artifacts as untrusted data. Controls include case-root path confinement, traversal and absolute-path rejection, NUL rejection, schema validation, deterministic canonicalization, no execution of evidence fields, case-integrity verification before trust, cross-case identity binding, duplicate detection, and stable machine-readable reason codes. Symlink resolution is checked after canonical path resolution so an artifact cannot escape the case root.


## Phase 5 evaluator threats and controls

Threats include fabricated evidence, contradictory claims, malformed confidence (including NaN/Infinity), cross-case evidence substitution, duplicate-evidence flooding, title/severity manipulation, verdict-only submissions, case tampering, semantic ambiguity, false-positive overfitting, case-specific hard-coding, evaluator exceptions masquerading as UNKNOWN, and scoring leakage.

Controls include strict schema validation, finite confidence checks, Phase 4 evidence verification, case-integrity verification before trust, structured claim matching, declarative verdict derivation, deterministic fingerprints, duplicate-resistant evidence support, explicit contradiction states, and separate evaluator-error handling. The evaluator never imports or executes FAS and never uses evaluated-system output as ground truth.


## Phase 6 evaluator threats

The graph evaluator treats submissions as hostile data. Threats include oversized graphs, graph bombs, pathological cycles, path explosion, fabricated privileged identities, fabricated authorization/control edges, malicious identifiers, Unicode normalization ambiguity, cross-case references, schema confusion, evidence spoofing, and evaluator denial of service. The engine uses safe JSON parsing, no dynamic execution, deterministic normalization, finite node/edge/path/traversal limits, and structured diagnostics.


## Phase 7 threat model

The remediation evaluator treats candidate-produced state and evidence as hostile input. Relevant threats include cosmetic fixes, partial fixes, alternate-path bypasses, equivalent-sink replacement, evidence fabrication, test removal/weakening, baseline tampering, graph spoofing, control weakening, regression hiding, and resource-exhaustion through graph inputs. Phase 7 performs no dynamic candidate execution and therefore cannot itself provide the sandbox boundary required for arbitrary patch execution; that responsibility is explicitly reserved for Phase 9.


## Phase 8 scoring trust boundary

Phase 8 treats candidate submissions as untrusted structured data. Candidate-provided aggregate scores, weights, gold data, or result digests are never authoritative. The scorer performs deterministic calculations without executing candidate code or loading candidate modules. Resource, path, serialization, and hidden-gold controls remain part of the benchmark security boundary.


## Phase 10 benchmark-integrity threats

Phase 10 extends the threat model to direct and derivative memorization, identifier/template recognition, documentation and Git-history leakage, Docker/package/CI artifact leakage, cache poisoning, cross-run leakage, network acquisition, evaluator probing, malicious contributors, compromised dependencies, oracle compromise, and release tampering.

Controls include content-addressed manifests, deterministic leakage scans, public/hidden surface metadata, explicit eligibility states, pinned workflow actions, release verification, and preserved Phase 9 isolation. These controls reduce repository-level leakage; they do not prove absence of model-training contamination.

The benchmark must never report CONTAMINATION_STATUS=CLEAN unless the evidence supports that statement. Unknown external exposure remains UNKNOWN or NOT_ASSESSED.
