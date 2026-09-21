"""I-14-E: pre-run binding hashes (run BEFORE any measurement; writes evidence only).

Produces `evidence/binding_hashes.json`:
  * per-tree file manifest digests for iso/T0/src, iso/T4/src, iso/T0b/src, CW/src
  * byte-equality proofs: T0b == T0, iso/T0 == I-14-C product/src,
    iso/T4 == I-14-C product_fixed/src
  * the T0-vs-T4 file-level difference list (what "two trees" means here)
  * product-side anchors (CW HEAD test file, both ps1 launchers, pytest.ini)
  * the frozen band's artefact hashes (frequency json, its captures, the surviving
    scratch events index)
Read-only w.r.t. every production repo.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
RUNS = ATTEMPT.parent.parent
CW = Path(r"C:\Users\郑曾波\Projects\company-wiki")
I14C = RUNS / "I-14-C" / "a20260919-01"
OUT = ATTEMPT / "evidence" / "binding_hashes.json"

TREES = {
    "T0": ATTEMPT / "iso" / "T0" / "src",
    "T4": ATTEMPT / "iso" / "T4" / "src",
    "T0b": ATTEMPT / "iso" / "T0b" / "src",
    "CW_HEAD": CW / "src",
    "I14C_product": I14C / "iso" / "product" / "src",
    "I14C_product_fixed": I14C / "iso" / "product_fixed" / "src",
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(root: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for name in filenames:
            if name.endswith(".pyc"):
                continue
            fp = Path(dirpath) / name
            out[fp.relative_to(root).as_posix()] = sha256_file(fp)
    return out


def manifest_digest(files: dict[str, str]) -> str:
    blob = "\n".join(f"{k} {v}" for k, v in sorted(files.items())).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def main() -> int:
    inv = {label: inventory(root) for label, root in TREES.items()}
    payload: dict = {
        "card": "I-14-E",
        "attempt": "a20260919-01",
        "interpreter": {
            "path": str(ATTEMPT / "iso" / "venv" / "Scripts" / "python.exe"),
            "provenance": ("byte copy of I-14-F/a20260919-01/iso/venv, itself copied from the "
                           "I-00-A template; package set verified equal to I-14-C's runner venv "
                           "(the interpreter that produced the frozen band)"),
            "pip_freeze_sha256": sha256_file(ATTEMPT / "iso" / "venv-pip-list.txt"),
            "pip_freeze": (ATTEMPT / "iso" / "venv-pip-list.txt").read_text(
                encoding="utf-8").split(),
            "global_miniconda_python": ("used only for glue/protocol scripts that never import "
                                        "the product package (extraction, hashing, reporting); "
                                        "never as the pytest runner or the child interpreter"),
        },
        "trees": {label: {"root": str(root), "files": len(inv[label]),
                          "manifest_sha256": manifest_digest(inv[label])}
                  for label, root in TREES.items()},
        "equalities": {},
        "differences": {},
    }
    for a, b in (("T0b", "T0"), ("T0", "I14C_product"), ("T4", "I14C_product_fixed"),
                 ("T0", "T4"), ("T0", "CW_HEAD"), ("T4", "CW_HEAD")):
        only_a = sorted(set(inv[a]) - set(inv[b]))
        only_b = sorted(set(inv[b]) - set(inv[a]))
        diff = sorted(k for k in set(inv[a]) & set(inv[b]) if inv[a][k] != inv[b][k])
        payload["equalities"][f"{a}=={b}"] = not (only_a or only_b or diff)
        if only_a or only_b or diff:
            payload["differences"][f"{a} vs {b}"] = {
                "only_in_" + a: only_a, "only_in_" + b: only_b,
                "content_diff": {k: {a: inv[a][k], b: inv[b][k]} for k in diff},
            }
    payload["anchors"] = {}
    for path, label in [
        (CW / "tests" / "contract" / "test_source_catalog_worker_bootstrap.py", "CW_test_file"),
        (CW / "scripts" / "source_catalog_worker.ps1", "CW_supervisor_ps1"),
        (CW / "scripts" / "source_catalog_worker_at_logon.ps1", "CW_logon_ps1"),
        (CW / "pytest.ini", "CW_pytest_ini"),
        (CW / "tests" / "contract" / "conftest.py", "CW_tests_contract_conftest"),
    ]:
        payload["anchors"][label] = {
            "path": str(path), "sha256": sha256_file(path), "bytes": path.stat().st_size,
        }
    freq = I14C / "r5" / "flake-evidence" / "frequency-child_without_runtime.json"
    payload["frozen_band_artefacts"] = {
        "frequency_json": {"path": str(freq), "sha256": sha256_file(freq)},
        "captures_dir": str(freq.parent / "frequency-captures"),
        "scratch_root": str(Path(os.environ.get("TEMP", "")) / "i14c-flake-freq"),
        "raw_record_extract": {
            "path": str(ATTEMPT / "evidence" / "frozen_band_raw_record.json"),
        },
    }
    payload["scope_declaration"] = {
        "disclosure_adaptation": "unmapped",
        "accuracy": "unproven",
        "qualification": ("test-timing measurement only; no product code, no product test change, "
                          "production repos read-only"),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"equalities": payload["equalities"],
                      "manifests": {k: v["manifest_sha256"][:16] + "..."
                                    for k, v in payload["trees"].items()},
                      "diff_keys": {k: list(v["content_diff"]) for k, v in
                                    payload["differences"].items()}},
                     indent=2))
    print("out:", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
