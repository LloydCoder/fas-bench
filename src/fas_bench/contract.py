"""Phase 1 benchmark contract constants.

This module contains the small, implementation-neutral vocabulary used by the
repository-contract checks. It is not the Phase 2 schema engine.
"""

BENCHMARK_VERSION = "0.1.0"
SCHEMA_VERSION = "0.1.0"
EVALUATOR_VERSION = "0.1.0"
CASE_SET_VERSION = "0.1.0"
SUBMISSION_FORMAT_VERSION = "0.1.0"

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
    "C1 Reachability",
    "C2 Data Flow / Taint",
    "C3 Authentication / Authorization",
    "C4 AI Agent Security",
    "C5 MCP Security",
    "C6 Supply Chain",
    "C7 Secrets / Sensitive Data",
    "C8 Infrastructure / Cloud",
    "C9 Cross-Component Attack Paths",
    "C10 Remediation / Regression",
)

DIFFICULTY_LEVELS = ("L1 Local", "L2 Multi-function", "L3 Multi-component", "L4 Agentic", "L5 Cross-system")

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

CASE_REGISTRY = (
    ("FAS-001", "Dead SSRF"),
    ("FAS-002", "Reachable SSRF"),
    ("FAS-003", "Sanitized Command Injection"),
    ("FAS-004", "Indirect Command Injection"),
    ("FAS-005", "IDOR"),
    ("FAS-006", "Authorization False Positive"),
    ("FAS-007", "Excessive Agent Capability"),
    ("FAS-008", "Agent Sandbox Boundary"),
    ("FAS-009", "MCP Tool Poisoning"),
    ("FAS-010", "Safe MCP Server"),
    ("FAS-011", "Malicious Dependency"),
    ("FAS-012", "Vulnerable but Unreachable Dependency"),
    ("FAS-013", "Revoked Secret"),
    ("FAS-014", "Live Credential Attack Path"),
    ("FAS-015", "Public Storage Exposure"),
    ("FAS-016", "Privilege Boundary"),
    ("FAS-017", "Multi-Service Compromise"),
    ("FAS-018", "Agent → CI/CD → Production"),
    ("FAS-019", "Verified Fix"),
    ("FAS-020", "Fake Fix / Alternate Path"),
)

EVIDENCE_TYPES = (
    "SOURCE_LOCATION", "SINK_LOCATION", "TRANSFORMATION", "DATA_FLOW",
    "CONFIGURATION", "DEPENDENCY", "IDENTITY", "PERMISSION", "POLICY",
    "TRUST_BOUNDARY", "RUNTIME_EVENT", "NETWORK_EVENT", "TOOL_INVOCATION",
    "TEST_RESULT", "REMEDIATION", "ENVIRONMENT_STATE", "DOCUMENTATION",
)
EVIDENCE_ROLES = ("DIRECT", "SUPPORTING", "MISSING", "CONTRADICTORY")
EVIDENCE_STATES = ("VERIFIED", "INVALID", "UNRESOLVED", "CONTRADICTED")
