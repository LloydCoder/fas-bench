"""Canonical Phase 2 benchmark vocabulary."""

BENCHMARK_VERSION = "0.1.0"
SCHEMA_VERSION = "0.1"
EVALUATOR_VERSION = "0.1.0"
CASE_SET_VERSION = "0.1.0"
SUBMISSION_FORMAT_VERSION = "0.1"

VERDICTS = (
    "EXPLOITABLE",
    "NOT_EXPLOITABLE",
    "CONDITIONALLY_EXPLOITABLE",
    "REMEDIATED",
    "REMEDIATION_FAILED",
    "REGRESSED",
    "UNKNOWN",
)

CATEGORIES = (
    "C1_REACHABILITY",
    "C2_DATA_FLOW_TAINT",
    "C3_AUTHENTICATION_AUTHORIZATION",
    "C4_AI_AGENT_SECURITY",
    "C5_MCP_SECURITY",
    "C6_SUPPLY_CHAIN",
    "C7_SECRETS_SENSITIVE_DATA",
    "C8_INFRASTRUCTURE_CLOUD",
    "C9_CROSS_COMPONENT_ATTACK_PATHS",
    "C10_REMEDIATION_REGRESSION",
)

DIFFICULTY_LEVELS = (
    "L1_LOCAL",
    "L2_MULTI_FUNCTION",
    "L3_MULTI_COMPONENT",
    "L4_AGENTIC",
    "L5_CROSS_SYSTEM",
)

CASE_IDS = tuple(f"FAS-{i:03d}" for i in range(1, 21))
GOLD_CASE_IDS = ("FAS-001", "FAS-002", "FAS-006", "FAS-016", "FAS-020")

ROADMAP = (
    "PHASE 1 — Specification & Benchmark Contract",
    "PHASE 2 — Schema & Data Model",
    "PHASE 3 — Gold Cases & Ground Truth",
    "PHASE 4 — Deterministic Evidence Engine",
    "PHASE 5 — Verdict & Finding Evaluator",
    "PHASE 6 — Attack-Path & Security-Graph Engine",
    "PHASE 7 — Remediation & Regression Engine",
    "PHASE 8 — Scoring, Calibration & Benchmark Analytics",
    "PHASE 9 — Secure Evaluation Harness & Reproducibility",
    "PHASE 10 — Benchmark Corpus, Contamination Defense & Release",
)

_CASE_TITLES = (
    "Dead SSRF",
    "Reachable SSRF",
    "Sanitized Command Injection",
    "Indirect Command Injection",
    "IDOR",
    "Authorization False Positive",
    "Excessive Agent Capability",
    "Agent Sandbox Boundary",
    "MCP Tool Poisoning",
    "Safe MCP Server",
    "Malicious Dependency",
    "Vulnerable but Unreachable Dependency",
    "Revoked Secret",
    "Live Credential Attack Path",
    "Public Storage Exposure",
    "Privilege Boundary",
    "Multi-Service Compromise",
    "Agent → CI/CD → Production",
    "Verified Fix",
    "Fake Fix / Alternate Path",
)
CASE_REGISTRY = tuple(
    (f"FAS-{i:03d}", title) for i, title in enumerate(_CASE_TITLES, 1)
)

EVIDENCE_TYPES = (
    "SOURCE_LOCATION",
    "SINK_LOCATION",
    "TRANSFORMATION",
    "DATA_FLOW",
    "CONFIGURATION",
    "DEPENDENCY",
    "IDENTITY",
    "PERMISSION",
    "POLICY",
    "TRUST_BOUNDARY",
    "RUNTIME_EVENT",
    "NETWORK_EVENT",
    "TOOL_INVOCATION",
    "TEST_RESULT",
    "REMEDIATION",
    "ENVIRONMENT_STATE",
    "DOCUMENTATION",
)
EVIDENCE_ROLES = ("DIRECT", "SUPPORTING", "MISSING", "CONTRADICTORY")
EVIDENCE_STATES = ("VERIFIED", "INVALID", "UNRESOLVED", "CONTRADICTED")
