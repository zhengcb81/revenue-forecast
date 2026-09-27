"""`B-payload-hash`, made executable: compare the policy-export payload the
resolve output carries, byte for byte, between a pre-B baseline checkout and
the current tree.

The acceptance map registers this gate as the operation contract's requirement
that "resolve is read-only but produces an outward contract artifact, so B02/B04
must keep that payload's bytes/hash contract" - the payload is filing-fetch's
FC-501 containment source.  It was carried as BLOCKED for two stated reasons:
no frozen baseline, and "reading the value needs an unapproved CLI".  The second
reason is false: `cli._policy_export_payload(config)` is a pure function.

Method (both sides identical):
  * load the SHIPPED config (`config/source_catalog.yaml`) from the checkout
    under test, with an EXPLICIT `project_root` - the payload embeds each root's
    absolute `path_ref`, so `${PROJECT_ROOT}` must not drift between checkouts;
  * serialise the payload canonically (sorted keys, UTF-8) and hash it;
  * compare the two byte strings.

The absolute hash is MACHINE-DEPENDENT (findings F-B01-9: this host computes
c773099b..., CI on Linux ca3b7f5d... for the same config), so the pinned
artifact is the COMPARISON, not the value.

Usage:
    python evidence/b07_payload_baseline.py <baseline-checkout> [current-checkout]
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

RUN = Path(__file__).resolve().parents[1]
REVENUE = Path(__file__).resolve().parents[4]
CURRENT = REVENUE.parent / "company-wiki"
FIXED_PROJECT_ROOT = Path(r"C:\r4-b07-payload-baseline")  # any fixed, existing-or-not path

PROBE = r'''
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
    "checkout": str(checkout),
    "policy_hash": payload.get("policy_hash"),
    "canonical_sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
    "canonical_bytes": len(canonical.encode("utf-8")),
    "schema_version": payload.get("schema_version"),
    "reusable_root_kinds": payload.get("reusable_root_kinds"),
    "reusable_roots": sorted(r.get("root_id") for r in payload.get("roots") or []
                             if r.get("reusable_for_filing")),
}}, ensure_ascii=False))
'''


def measure(checkout: Path) -> dict:
    script = PROBE.format(
        src=str(checkout / "src"),
        checkout=str(checkout),
        project_root=str(FIXED_PROJECT_ROOT),
    )
    result = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, cwd=str(checkout)
    )
    if result.returncode != 0:
        raise SystemExit(f"probe failed in {checkout}:\n{result.stderr[-2000:]}")
    return json.loads(result.stdout.strip().splitlines()[-1])


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        raise SystemExit(__doc__)
    baseline = Path(argv[1])
    current = Path(argv[2]) if len(argv) > 2 else CURRENT
    left = measure(baseline)
    right = measure(current)
    same = left["canonical_sha256"] == right["canonical_sha256"]
    report = {
        "gate": "B-payload-hash",
        "method": ("same shipped config + explicit fixed project_root on both sides; canonical "
                   "JSON (sorted keys, UTF-8) byte comparison of cli._policy_export_payload"),
        "baseline": left,
        "current": right,
        "identical": same,
        "conclusion": (
            "payload bytes unchanged across the compared revision window"
            if same
            else "PAYLOAD CHANGED - block the merge unless a synchronized cross-repo migration "
                 "is submitted with it"
        ),
        "machine_dependence": ("the absolute policy_hash embeds each root's absolute path_ref, so "
                               "it is machine-scoped (F-B01-9); only this comparison is portable"),
    }
    out = RUN / "evidence" / "b07-payload-baseline.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print("wrote", out.relative_to(REVENUE).as_posix())
    return 0 if same else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
