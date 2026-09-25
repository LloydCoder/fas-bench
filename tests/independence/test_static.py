import ast
from pathlib import Path


def test_independence_surface_has_no_forbidden_imports():
    root = Path(__file__).resolve().parents[2] / "src" / "fas_bench"
    forbidden = {"fas", "threatfade", "tinlance"}
    for path in root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert all(
                    alias.name.split(".", 1)[0].lower() not in forbidden for alias in node.names
                )
            elif isinstance(node, ast.ImportFrom) and node.module:
                assert node.module.split(".", 1)[0].lower() not in forbidden
