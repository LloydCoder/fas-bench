# Schemas
**Role:** Phase 2 executable data-contract guidance.
**Authority:** docs/specification.md.

## Draft and versioning
All normative schemas use JSON Schema Draft 2020-12, stable $id values, and the https://fas-bench.dev/schemas namespace. Schema family version is 0.1 under v0.1 directories; benchmark specification remains 0.1.0.

## Families
case, claim, evidence, attack-graph, verdict, remediation, submission, evaluation-result, plus shared common definitions.

## Structural versus semantic validation
JSON Schema validates type, required fields, enums, patterns, ranges, local structure, and closed-object fields. Python semantic validation validates references, graph/path integrity, version compatibility, conditional verdicts, remediation state, and evaluation arithmetic.

schema-valid != semantically-valid != benchmark-correct.

## Strictness
Contract objects reject unknown properties. Extensibility is explicit through metadata/attributes objects.

## Offline operation
All ordinary $ref resolution is local. The validator registers repository schema resources in memory and never fetches arbitrary remote URLs.

## Compatibility
Patch-compatible changes preserve existing valid instances and semantics. Additive compatible changes require explicit review. Breaking changes require a new schema directory.

## Evaluator-only ground truth
`schemas/ground-truth/v0.1/ground-truth.schema.json` defines the evaluator-only shape for expected verdicts and hidden evidence. It is never accepted as the public submission contract and does not contain the Phase 3 corpus.
