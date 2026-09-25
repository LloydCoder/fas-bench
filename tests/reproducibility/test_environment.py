from pathlib import Path

from fas_bench.verification import environment_report


def test_environment_report_has_no_obvious_secret_fields():
    report = environment_report(Path.cwd())
    assert "password" not in str(report).lower()
    assert "token" not in str(report).lower()
    assert report["python"]
