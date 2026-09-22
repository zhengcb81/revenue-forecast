"""I-14-E-APPLY: freeze instant + binding hashes, recorded BEFORE any run.

Writes:
  before/freeze_instant.json  - the freeze timestamp and the oracle's own hash
  before/binding_hashes.json  - every anchor this attempt binds, with equality proofs

Nothing here writes to the production repos.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

ATT = Path(__file__).resolve().parents[1]
ATTEMPT = "execution_runs/I-14-E-APPLY/a20260921-01"
PROD_CW = Path(os.environ["USERPROFILE"]) / "Projects" / "company-wiki"
SUITE_REL = "tests/contract/test_source_catalog_worker_bootstrap.py"
LAUNCHER_REL = "scripts/source_catalog_worker.ps1"
LOGON_REL = "scripts/source_catalog_worker_at_logon.ps1"
I14E = (Path(os.environ["USERPROFILE"]) / "Projects" / "revenue-forecast" / ".planning"
        / "2026-09-19-three-project-history-audit" / "execution_runs" / "I-14-E"
        / "a20260919-01")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    before = ATT / "before"
    before.mkdir(parents=True, exist_ok=True)
    py = ATT / "iso" / "venv" / "Scripts" / "python.exe"

    anchors = {
        "prod_test_file": PROD_CW / SUITE_REL,
        "prod_launcher": PROD_CW / LAUNCHER_REL,
        "prod_logon_wrapper": PROD_CW / LOGON_REL,
        "iso_src_test_file": ATT / "iso" / SUITE_REL,
        "iso_src_launcher": ATT / "iso" / LAUNCHER_REL,
        "iso_T0_test_file": ATT / "iso" / "T0" / SUITE_REL,
        "iso_T0b_test_file": ATT / "iso" / "T0b" / SUITE_REL,
        "iso_T0_launcher": ATT / "iso" / "T0" / LAUNCHER_REL,
        "iso_T0b_launcher": ATT / "iso" / "T0b" / LAUNCHER_REL,
        "i14e_oracle": I14E / "oracle.md",
        "i14e_proposal": I14E / "after" / "proposed-test-side-change.md",
        "i14e_analysis": I14E / "after" / "analysis.json",
        "i14e_fail_able": I14E / "after" / "fail-able-cases.json",
        "oracle_md": ATT / "oracle.md",
    }
    hashes = {name: sha256(path) for name, path in anchors.items()}
    missing = [name for name, path in anchors.items() if not path.exists()]
    if missing:
        raise SystemExit(f"missing anchors: {missing}")

    equalities = {
        "prod_test_file == iso_src_test_file": (
            hashes["prod_test_file"] == hashes["iso_src_test_file"]),
        "iso_src_test_file == iso_T0_test_file": (
            hashes["iso_src_test_file"] == hashes["iso_T0_test_file"]),
        "iso_T0_test_file == iso_T0b_test_file": (
            hashes["iso_T0_test_file"] == hashes["iso_T0b_test_file"]),
        "prod_launcher == iso_src_launcher": (
            hashes["prod_launcher"] == hashes["iso_src_launcher"]),
        "iso_T0_launcher == iso_T0b_launcher": (
            hashes["iso_T0_launcher"] == hashes["iso_T0b_launcher"]),
    }

    venv_info = subprocess.run(
        [str(py), "-c", "import sys,pytest;print(sys.version.split()[0], pytest.__version__)"],
        capture_output=True, text=True)
    cw_head = subprocess.run(["git", "-C", str(PROD_CW), "rev-parse", "HEAD"],
                             capture_output=True, text=True)
    cw_branch = subprocess.run(["git", "-C", str(PROD_CW), "rev-parse", "--abbrev-ref", "HEAD"],
                               capture_output=True, text=True)

    payload = {
        "card": "I-14-E-APPLY",
        "attempt": ATTEMPT,
        "frozen_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "frozen_local": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "machine": {
            "platform": platform.platform(),
            "logical_cores": os.cpu_count(),
            "python": sys.version.split()[0],
            "runner_python": str(py),
            "runner_python_version": venv_info.stdout.strip() or venv_info.stderr.strip(),
        },
        "production_checkout": {
            "path": str(PROD_CW),
            "git_head": cw_head.stdout.strip(),
            "git_branch": cw_branch.stdout.strip(),
        },
        "authorization": {
            "ruling": ("OWNER_DECISIONS.md SS13 T1-7 authorizes a card to fix the product "
                       "test's timing assumption; this apply-card is that authorization."),
            "boundary": ("production repos read-only in place; the change lives only under "
                         "iso/ and promotion is a separate owner decision"),
        },
        "anchors": {name: {"path": str(path), "sha256": hashes[name]}
                    for name, path in anchors.items()},
        "equalities": equalities,
        "equalities_all_hold": all(equalities.values()),
    }

    (before / "binding_hashes.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    # the freeze record proper: the oracle text is hashed at freeze time
    freeze = {
        "card": "I-14-E-APPLY",
        "attempt": ATTEMPT,
        "frozen_utc": payload["frozen_utc"],
        "oracle_sha256": hashes["oracle_md"],
        "basis": {
            "i14e_oracle_sha256": hashes["i14e_oracle"],
            "i14e_proposed_change_sha256": hashes["i14e_proposal"],
            "i14e_analysis_sha256": hashes["i14e_analysis"],
            "i14e_fail_able_cases_sha256": hashes["i14e_fail_able"],
        },
        "pre_change_sut_sha256": hashes["iso_src_test_file"],
        "statement": ("frozen before any run of this attempt; the change form, the four "
                      "robustness criteria R1-R4, the arm counts and the non-vacuity node "
                      "were all fixed in oracle.md before the first execution"),
    }
    (before / "freeze_instant.json").write_text(
        json.dumps(freeze, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps({"frozen_utc": payload["frozen_utc"],
                      "equalities_all_hold": payload["equalities_all_hold"],
                      "prod_test_sha256": hashes["prod_test_file"],
                      "oracle_sha256": hashes["oracle_md"]}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
