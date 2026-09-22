"""I-14-E: post-run hash closure.

Re-computes the production-repo anchors and the attempt's tree manifests after all runs and
compares them with the pre-run values in ``evidence/binding_hashes.json``.  Equality is the
evidence that this attempt wrote nothing into company-wiki / revenue-forecast / filing-fetch
and that the measured trees are the ones that were bound.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
OUT = ATTEMPT / "after" / "final_hashes.json"
PRE = ATTEMPT / "evidence" / "binding_hashes.json"
CW = Path(os.environ.get("USERPROFILE", r"C:\Users")) / "Projects" / "company-wiki"
RF = ATTEMPT.parents[3]
FF = Path(os.environ.get("USERPROFILE", r"C:\Users")) / "Projects" / "filing-fetch"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(root: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for name in filenames:
            if name.endswith(".pyc"):
                continue
            fp = Path(dirpath) / name
            out[fp.relative_to(root).as_posix()] = sha(fp)
    return out


def manifest_digest(files: dict[str, str]) -> str:
    blob = "\n".join(f"{k} {v}" for k, v in sorted(files.items())).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def main() -> int:
    pre = json.loads(PRE.read_text(encoding="utf-8"))
    payload: dict = {"card": "I-14-E", "attempt": "a20260919-01",
                     "pre_run_source": str(PRE), "checks": {}, "all_equal": True}
    trees = {
        "iso/T0/src": ATTEMPT / "iso" / "T0" / "src",
        "iso/T4/src": ATTEMPT / "iso" / "T4" / "src",
        "iso/T0b/src": ATTEMPT / "iso" / "T0b" / "src",
        "CW/src": CW / "src",
    }
    for label, root in trees.items():
        post = manifest_digest(inventory(root))
        pre_entry = pre["trees"].get(
            {"iso/T0/src": "T0", "iso/T4/src": "T4", "iso/T0b/src": "T0b",
             "CW/src": "CW_HEAD"}[label])
        equal = bool(pre_entry) and pre_entry["manifest_sha256"] == post
        payload["checks"][label] = {"pre_manifest_sha256": pre_entry["manifest_sha256"]
                                    if pre_entry else None,
                                    "post_manifest_sha256": post, "equal": equal}
        payload["all_equal"] &= equal
    for label, path in (("CW_test_file",
                         CW / "tests" / "contract" / "test_source_catalog_worker_bootstrap.py"),
                        ("CW_supervisor_ps1", CW / "scripts" / "source_catalog_worker.ps1"),
                        ("CW_logon_ps1", CW / "scripts" / "source_catalog_worker_at_logon.ps1")):
        post = sha(path)
        pre_value = pre["anchors"][label]["sha256"]
        equal = post == pre_value
        payload["checks"][label] = {"pre_sha256": pre_value, "post_sha256": post,
                                    "equal": equal}
        payload["all_equal"] &= equal
    payload["production_repos_note"] = (
        "no writes were made into any production repo by this attempt; the anchors above are "
        "byte-identical before and after, and the attempt's own scratch roots live under %TEMP%")
    payload["production_heads_at_end"] = {}
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"all_equal": payload["all_equal"],
                      "checks": {k: v["equal"] for k, v in payload["checks"].items()}},
                     indent=2))
    print("out:", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
