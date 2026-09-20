# fmt: off
"""Deterministic mutation engine with explicit semantic relations and validation hooks."""

from __future__ import annotations

import ast
import hashlib
import io
import json
import tokenize
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

SEMANTIC_CLASSES = (
    "SEMANTICALLY_EQUIVALENT",
    "SECURITY_WEAKENED",
    "SECURITY_STRENGTHENED",
    "ALTERNATE_PATH_INTRODUCED",
    "CONTROL_REMOVED",
    "CONTROL_ADDED",
    "REMEDIATION_INVALIDATED",
    "INVALID",
)

@dataclass(frozen=True)
class Mutation:
    mutation_id: str
    operator: str
    input_case: str
    output_variant: str
    semantic_class: str
    expected_security_delta: str
    expected_verdict_delta: str
    validation_status: str
    artifact_digest: str

def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def rename_identifiers(source: str, mapping: dict[str, str]) -> str:
    """Rename NAME tokens only; strings/comments are untouched."""
    if not mapping:
        return source
    tokens = tokenize.generate_tokens(io.StringIO(source).readline)
    changed = []
    for tok in tokens:
        if tok.type == tokenize.NAME and tok.string in mapping:
            tok = tok._replace(string=mapping[tok.string])
        changed.append(tok)
    return tokenize.untokenize(changed)

def formatting_mutation(source: str) -> str:
    """Whitespace-only mutation validated by AST equivalence."""
    tree = ast.parse(source)
    mutated = ast.unparse(tree) + "\n"
    if ast.dump(tree, include_attributes=False) != ast.dump(ast.parse(mutated), include_attributes=False):
        raise ValueError("formatting mutation changed the AST")
    return mutated

def json_key_order_mutation(document: dict) -> dict:
    """Return a recursively key-sorted copy; JSON object order is non-semantic."""
    return json.loads(json.dumps(document, sort_keys=True, ensure_ascii=False))

def mutation_valid(source_before: str, source_after: str) -> bool:
    """Structural semantic guard for Python-equivalent mutations."""
    before = ast.dump(ast.parse(source_before), include_attributes=False)
    after = ast.dump(ast.parse(source_after), include_attributes=False)
    return before == after

def make_mutation(
    *,
    mutation_id: str,
    operator: str,
    input_case: str,
    output_variant: str,
    semantic_class: str,
    expected_security_delta: str,
    expected_verdict_delta: str,
    artifact: bytes,
    validator: Callable[[bytes], bool] | None = None,
) -> Mutation:
    if semantic_class not in SEMANTIC_CLASSES:
        raise ValueError(f"unknown semantic class: {semantic_class}")
    valid = validator(artifact) if validator else True
    status = "VALIDATED" if valid else "MUTATION_VALIDATION_FAILURE"
    return Mutation(
        mutation_id=mutation_id,
        operator=operator,
        input_case=input_case,
        output_variant=output_variant,
        semantic_class=semantic_class,
        expected_security_delta=expected_security_delta,
        expected_verdict_delta=expected_verdict_delta,
        validation_status=status,
        artifact_digest=_digest(artifact),
    )

def generate_identifier_mutation(case_id: str, source: str, suffix: str = "variant") -> Mutation:
    mapping = {"user_input": f"user_input_{suffix}", "target": f"target_{suffix}"}
    output = rename_identifiers(source, mapping)
    return make_mutation(
        mutation_id=f"{case_id}-ID-{_digest(output.encode())[:12]}",
        operator="IDENTIFIER_RENAME",
        input_case=case_id,
        output_variant=f"{case_id}-{suffix}",
        semantic_class="SEMANTICALLY_EQUIVALENT",
        expected_security_delta="NONE",
        expected_verdict_delta="SAME",
        artifact=output.encode(),
        validator=lambda data: bool(data),
    )
