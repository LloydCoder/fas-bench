# FAS-Bench Threat Model

**Document role:** benchmark security and research threat model.  
**Authority:** docs/specification.md defines benchmark security requirements.

## Assets

- evaluator host and execution environment;
- hidden ground truth;
- benchmark cases and fixtures;
- scoring and normalization logic;
- evaluation artifacts and provenance;
- synthetic credentials/secrets;
- result integrity;
- benchmark versioning and reproducibility metadata.

## Evaluated-system threats

The evaluated system may:

- hallucinate evidence;
- fabricate tool output;
- invent source locations or functions;
- misjudge reachability;
- claim exploitability without a complete path;
- overclaim or underclaim;
- be influenced by prompt injection;
- be influenced by malicious tool/MCP descriptions;
- omit path segments;
- assert an ineffective remediation;
- miss alternate paths.

The benchmark addresses these through structured submissions, evidence verification, hidden ground truth, explicit verdict semantics, and graph/path comparison.

## Benchmark threats

Benchmark infrastructure may face:

- case leakage;
- hidden-ground-truth leakage;
- evaluator compromise;
- malicious case code;
- malicious dependencies;
- network escape;
- credential leakage;
- evaluator nondeterminism;
- benchmark gaming;
- metric gaming;
- result tampering;
- denial of service.

Required baseline controls include isolation, synthetic credentials, default-deny networking, dependency pinning where practical, strict public/hidden separation, deterministic evaluation, provenance recording, and content integrity checks.

## Research threats

Threats to scientific validity include:

- selection bias;
- case-construction bias;
- contamination;
- taxonomy bias;
- scoring-weight bias;
- environment bias;
- evaluator implementation bias;
- overfitting to synthetic cases;
- insufficient expert review;
- leakage from public cases into model training or prompts.

Phase 1 explicitly treats these as unresolved research risks rather than claiming they are solved.

## Security execution rules

Benchmark cases are untrusted inputs. Arbitrary case code MUST NOT execute directly on the evaluator host. Dynamic execution MUST be isolated. Outbound network access MUST default to denied unless a case explicitly requires a controlled network. Real credentials, production data, and real external targets MUST NOT be used.

## Ground-truth protection

Hidden ground truth must not be available to the evaluated system. Public case material and private evaluation material must have separate trust boundaries. Evaluator internals must not be exposed through the normal submission interface.

## Integrity and provenance

Case and evaluation artifacts should be content-addressed where practical. Evaluations should record benchmark, case, evaluator, submission, environment, tool, and content versions.

## Threat-model limits

No Phase 1 control proves sandbox security, contamination resistance, or evaluator integrity. Those controls are implemented and tested in later phases, especially Phase 9 and Phase 10.
