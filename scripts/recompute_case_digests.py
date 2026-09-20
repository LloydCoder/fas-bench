from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, "src")
from fas_bench.cases import _digest_case

root = Path(__file__).resolve().parents[1]
cases = root / "cases"
manifest = json.loads((cases / "manifest.json").read_text(encoding="utf-8"))
changed = False
for case_dir in sorted(cases.glob("FAS-*")):
    if not case_dir.is_dir():
        continue
    digest = _digest_case(case_dir)
    metadata_path = case_dir / "metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if metadata.get("artifact_digest") != digest:
        metadata["artifact_digest"] = digest
        metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
        changed = True
    for item in manifest.get("cases", []):
        if item.get("case_id") == case_dir.name and item.get("artifact_digest") != digest:
            item["artifact_digest"] = digest
            changed = True
if changed:
    (cases / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print("updated")
else:
    print("current")
