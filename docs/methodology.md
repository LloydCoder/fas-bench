# FAS-Bench Methodology

**Document role:** research methodology and benchmark-design rationale.  
**Authority:** docs/specification.md is the normative contract.

## Research objective

FAS-Bench is designed to study evidence-grounded security adjudication rather than vulnerability prose generation. The central research question is whether a system can establish what a security signal means under explicit environment and attacker assumptions.

## Design principles

Methodological priorities are:

- expert-reviewed ground truth;
- deterministic validation wherever possible;
- explicit false-positive traps;
- controlled environment assumptions;
- machine-readable claims and evidence;
- effective security-boundary reasoning;
- attack-path comparison;
- remediation verification;
- regression analysis;
- confidence calibration;
- contamination resistance;
- reproducibility.

## Case construction

A case should isolate a security property and provide sufficient observable material to adjudicate it. Cases should include negative controls where useful, explicit assumptions, deterministic validation, and evidence requirements.

The initial 20 cases are a design registry. Phase 3 is responsible for constructing and validating the actual gold corpus. No Phase 1 statement should imply statistical representativeness.

## Evidence methodology

Claims are independently mapped to benchmark-observable evidence. Evidence should be precise enough to verify source locations, transformations, configuration, permissions, policies, runtime events, or other relevant facts. Fabricated evidence is a first-class failure mode.

## Attack-path methodology

Security paths are represented as normalized graphs so that multi-step reasoning and boundary crossings can be evaluated independently of prose. The effective graph incorporates controls that may invalidate an apparent path.

## Remediation methodology

A fix is successful only if it changes the relevant security property. A disappearing code pattern is not sufficient if the original impact remains reachable through an alternate path.

## Contamination methodology

Public development material is compatible with hidden evaluation. Planned defenses include semantic-preserving mutations, identifier renaming, architecture-preserving transformations, temporal splits, hidden cases, and leakage detection. Their effectiveness must be measured rather than assumed.

## Scientific validity

Scoring weights, evidence-integrity thresholds, composite metrics, taxonomy completeness, and generalization are provisional research questions until validated. Aggregate scores must not hide component failures.

## External benchmark engineering precedents

SEC-bench demonstrates reproducible, containerized security-task instances and automated verification. SWE-bench demonstrates structured predictions, repeatable test execution, containerized evaluation, and saved evaluation artifacts. FAS-Bench adopts those engineering disciplines while defining a different task semantics centered on evidence-grounded security adjudication.