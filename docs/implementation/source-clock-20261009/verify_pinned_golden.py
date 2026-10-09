"""Recheck untouched 4.1.0 goldens in their pinned runtime; compare economics."""
from __future__ import annotations

import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
from tempfile import TemporaryDirectory

RF = Path(__file__).resolve().parents[3]
BASE = "e688b0a2dceeb7de453e43dad3534061bf346bc9"
OUTPUT = Path(__file__).with_name("pinned_golden_validation.json")
EXPORT = r'''import json,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()/"scripts"))
sys.path.insert(0,str(Path.cwd()/"tests"))
from revenue_core import ENGINE_VERSION,canonical_sha256
from test_golden_behavior_lock import MODEL_SPECS,run_family
print(json.dumps({"engine_version":ENGINE_VERSION,"families":{family:{"hash":canonical_sha256(result),"result":result} for family in MODEL_SPECS for result in [run_family(family)]}},separators=(",",":")))
'''


def export(root, registry):
    env = dict(os.environ)
    env["REVENUE_PUBLICATION_REGISTRY"] = str(registry)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONUTF8"] = "1"
    result = subprocess.run([sys.executable, "-B", "-c", EXPORT], cwd=root, env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=40, check=True)
    return json.loads(result.stdout)


def main():
    golden = RF / "tests/golden_behavior_hashes.json"
    before = hashlib.sha256(golden.read_bytes()).hexdigest()
    expected = json.loads(golden.read_bytes())
    report = {"schema_version": "pinned-golden-validation/1", "base": BASE,
              "status": "NOT_RUN", "golden_sha_before": before, "families": {}}
    scratch_path = None
    try:
        with TemporaryDirectory(prefix="rfpin-") as scratch:
            scratch_path = Path(scratch)
            pinned = scratch_path / "pinned"
            pinned.mkdir()
            archive = subprocess.run(["git", "archive", BASE, "scripts", "tests", "config"], cwd=RF,
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30, check=True)
            with tarfile.open(fileobj=io.BytesIO(archive.stdout)) as packed:
                packed.extractall(pinned, filter="data")
            old = export(pinned, scratch_path / "old-registry")
            new = export(RF, scratch_path / "new-registry")
            assert old["engine_version"] == "4.1.0" and new["engine_version"] == "4.1.1"
            metadata = {"engine_version", "workflow_receipt", "publication_receipt", "result_sha256"}
            for family in expected:
                original = old["families"][family]
                current = new["families"][family]
                assert original["hash"] == expected[family], family + " original golden changed"
                first, second = original["result"], current["result"]
                differing = sorted(key for key in set(first) | set(second) if first.get(key) != second.get(key))
                assert not (set(differing) - metadata), family + " nonmetadata change: " + repr(differing)
                report["families"][family] = {"pinned_hash": original["hash"],
                    "old_full_output_matches_locked_golden": True,
                    "current_result_sha": current["hash"], "changed_top_fields": differing,
                    "nonmetadata_fields_exactly_equal": True}
            report["status"] = "PASS"
    finally:
        report["golden_sha_after"] = hashlib.sha256(golden.read_bytes()).hexdigest()
        report["golden_bytes_unchanged"] = report["golden_sha_after"] == before
        report["temporary_runtime_cleaned"] = scratch_path is not None and not scratch_path.exists()
        OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "families": len(report["families"]),
                      "old_golden_bytes_unchanged": report["golden_bytes_unchanged"]}))


if __name__ == "__main__":
    main()
