"""B.VR (B07) mutation battery against the payload comparison (question d/e).

For each mutation: copy the CURRENT checkout's ``src`` + ``config`` into a temp
directory, apply ONE literal mutation inside the copy (the product repo is never
touched), run the author's measurement method (same shipped config path +
explicit fixed project_root) and report whether the comparison still says
"identical".

A mutation that SURVIVES is one the payload comparison cannot see; a KILLED
mutation is one where the comparison reports a payload change.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RUN = Path(__file__).resolve().parents[1]
REVENUE = Path(__file__).resolve().parents[4]
CURRENT = REVENUE.parent / "company-wiki"
FIXED_PROJECT_ROOT = Path(r"C:\r4-b07-payload-baseline")

PAYLOAD_PROBE = r'''
import hashlib, json, sys
from pathlib import Path
sys.path.insert(0, r"{src}")
from company_wiki.source_catalog.cli import _policy_export_payload
from company_wiki.source_catalog.config import load_catalog_config

checkout = Path(r"{checkout}")
config = load_catalog_config(checkout / "config" / "source_catalog.yaml",
                             project_root=Path(r"{project_root}"))
payload = _policy_export_payload(config)
canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
print(json.dumps({{
    "policy_hash": payload.get("policy_hash"),
    "canonical_sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
    "canonical_bytes": len(canonical.encode("utf-8")),
    "payload": payload,
}}, ensure_ascii=False))
'''

MUTATIONS = [
    {
        "id": "M1-config-priority",
        "file": "config/source_catalog.yaml",
        "old": "    priority: 10",
        "new": "    priority: 11",
        "expect": "killed (payload input: shipped config changed)",
    },
    {
        "id": "M2-config-root-path",
        "file": "config/source_catalog.yaml",
        "old": '"${PROJECT_ROOT}/future_lake"',
        "new": '"${PROJECT_ROOT}/future_lake_renamed"',
        "expect": "killed (payload input: root path changed)",
    },
    {
        "id": "M3-export-document-field",
        "file": "src/company_wiki/source_catalog/policy_2x.py",
        "old": '                "priority": spec.priority,',
        "new": '                "priority": spec.priority + 1000,',
        "expect": "killed (payload input: exported document field changed)",
    },
    {
        "id": "M4-consumer-payload-key",
        "file": "src/company_wiki/source_catalog/cli.py",
        "old": '        "roots": policy["roots"],',
        "new": '        "roots_v2": policy["roots"],',
        "expect": "killed (the compared function's own output changed)",
    },
    {
        "id": "M5-reusable-kind-only",
        "file": "src/company_wiki/source_catalog/policy_2x.py",
        "old": (
            '    if spec.reusable_for_filing is not None:\n'
            '        return bool(spec.reusable_for_filing)\n'
            '    return spec.kind in config.reusable_root_kinds'
        ),
        "new": '    return spec.kind in config.reusable_root_kinds',
        "expect": (
            "SURVIVES on the shipped config (every root is reusable either way) - "
            "the gate is byte equality on ONE config, not an export-semantics gate"
        ),
    },
    {
        "id": "M6-resolver-version-bump",
        "file": "src/company_wiki/source_catalog/resolver.py",
        "old": 'SOURCE_RESOLVER_SCHEMA_VERSION = "1.0"',
        "new": 'SOURCE_RESOLVER_SCHEMA_VERSION = "1.1"',
        "expect": (
            "SURVIVES: the compared artifact does not depend on resolver.py, which "
            "is why the B07 commit cannot move the payload"
        ),
    },
]


def measure(checkout: Path) -> dict:
    script = PAYLOAD_PROBE.format(
        src=str(checkout / "src"),
        checkout=str(checkout),
        project_root=str(FIXED_PROJECT_ROOT),
    )
    result = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, cwd=str(checkout)
    )
    if result.returncode != 0:
        return {"error": result.stderr[-1500:]}
    return json.loads(result.stdout.strip().splitlines()[-1])


def copy_checkout(dest: Path) -> None:
    shutil.copytree(
        CURRENT / "src", dest / "src", ignore=shutil.ignore_patterns("__pycache__")
    )
    shutil.copytree(CURRENT / "config", dest / "config")


def main() -> int:
    base_root = Path(tempfile.mkdtemp(prefix="b07_review_mut_"))
    reference = measure(CURRENT)
    report: dict = {
        "reference": {
            "canonical_sha256": reference.get("canonical_sha256"),
            "canonical_bytes": reference.get("canonical_bytes"),
            "policy_hash": reference.get("policy_hash"),
        },
        "mutations": [],
    }
    for spec in MUTATIONS:
        dest = base_root / spec["id"]
        copy_checkout(dest)
        target = dest / spec["file"]
        text = target.read_text(encoding="utf-8")
        occurrences = text.count(spec["old"])
        if occurrences != 1:
            report["mutations"].append(
                {**spec, "applied": False, "occurrences": occurrences}
            )
            continue
        target.write_text(text.replace(spec["old"], spec["new"]), encoding="utf-8")
        measured = measure(dest)
        if "error" in measured:
            report["mutations"].append({**spec, "applied": True, "probe_error": measured["error"]})
            continue
        identical = measured["canonical_sha256"] == reference.get("canonical_sha256")
        report["mutations"].append(
            {
                "id": spec["id"],
                "file": spec["file"],
                "applied": True,
                "compared_identical": identical,
                "status": "survived" if identical else "killed",
                "expect": spec["expect"],
                "canonical_sha256": measured["canonical_sha256"],
                "policy_hash": measured["policy_hash"],
            }
        )
    out = RUN / "evidence" / "b07_review_mutations.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print("wrote", out.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
