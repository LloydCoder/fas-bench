from pathlib import Path


def test_independence_surface_has_no_forbidden_imports():
    root = Path(__file__).resolve().parents[2] / "src" / "fas_bench"
    forbidden = {"fas", "threatfade", "tinlance"}
    for path in root.rglob("*.py"):
        text = path.read_text(encoding="utf-8").lower()
        for name in forbidden:
            assert f"import {name}" not in text
            assert f"from {name}" not in text
