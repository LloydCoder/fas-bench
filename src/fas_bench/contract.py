"""Canonical benchmark vocabulary loaded from the normative common schema."""

from __future__ import annotations

import json
from pathlib import Path

BENCHMARK_VERSION = "0.1.0"
SCHEMA_VERSION = "0.1"
EVALUATOR_VERSION = "0.1.0"
CASE_SET_VERSION = "0.1.0"
SUBMISSION_FORMAT_VERSION = "0.1"


def _common_definitions() -> dict:
    package_schema = Path(__file__).resolve().parent / "schemas/common/v0.1/common.schema.json"
    repository_schema = (
        Path(__file__).resolve().parents[2] / "schemas/common/v0.1/common.schema.json"
    )
    schema_path = package_schema if package_schema.exists() else repository_schema
    return json.loads(schema_path.read_text(encoding="utf-8"))["$defs"]


_DEFS = _common_definitions()
VERDICTS = tuple(_DEFS["Verdict"]["enum"])
CATEGORIES = tuple(_DEFS["Category"]["enum"])
DIFFICULTY_LEVELS = tuple(_DEFS["Difficulty"]["enum"])
EVIDENCE_TYPES = tuple(_DEFS["EvidenceType"]["enum"])
EVIDENCE_ROLES = tuple(_DEFS["EvidenceRole"]["enum"])
EVIDENCE_STATES = tuple(_DEFS["EvidenceVerification"]["enum"])
CLAIM_TYPES = tuple(_DEFS["ClaimType"]["enum"])
REASON_CODES = tuple(_DEFS["ReasonCode"]["enum"])
NODE_TYPES = tuple(_DEFS["NodeType"]["enum"])
EDGE_TYPES = tuple(_DEFS["EdgeType"]["enum"])

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
CASE_REGISTRY = tuple((f"FAS-{i:03d}", title) for i, title in enumerate(_CASE_TITLES, 1))
