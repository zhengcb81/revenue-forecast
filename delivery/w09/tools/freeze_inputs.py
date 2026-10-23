"""Freeze the read-only W09 input inventory with real SHA-256 and byte sizes.

Reads only; never writes into the sealed audit run tree.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

RUN = Path(r"C:\Users\郑曾波\Projects\revenue-forecast-audit\runs\r1-20261021-cn-wuxi-apptec")
WORKDIR = Path(r"C:\Users\郑曾波\Projects\revenue-forecast-r1-research")
OUT = WORKDIR / "delivery" / "w09" / "inputs" / "readonly-inputs.json"

CARD = Path(
    r"C:\Users\郑曾波\Projects\company-wiki\docs\plans\du11-source-closure-2026-10-18"
    r"\harness_lanes\20261023\W09-RF-RESEARCH.md"
)
LANE = CARD.parent

# logical_name, path, purpose, card_expected_sha256
ITEMS = [
    ("w09_execution_card", CARD,
     "W09-RF-RESEARCH construction card (this package's authority)", None),
    ("lane_readme", LANE / "README.md", "shared lane entry and boundaries",
     "4d1a1162c8cccf908b407f248453052b0503e0956141641d892a76e1d80d765f"),
    ("lane_interfaces", LANE / "INTERFACES.md", "shared cross-package handoff contract",
     "87adff0f9e07d012110b06a66c3c1a327c82aee02d7c1ce8c2a01847ec0315f6"),
    ("lane_inputs", LANE / "INPUTS.json", "shared read-only input inventory",
     "725fd432ad81e13b5c1f95053fced7e0a2aeff6a591f93dde8867896d926760d"),
    ("lane_handoff_template", LANE / "handoff.template.json",
     "shared handoff schema template", "26ddbdd0039ffb127dafc7d0d9c1a03509e632beca77fd43c6ed37f5cd13d32b"),
    ("lane_dispatch", LANE / "dispatch.json", "actual start head and package binding", None),
    ("w09_original_card", RUN / "remediation/r1-final3-review-20261022/work_packages/W09.md",
     "original W09 work package card", None),
    ("preparation_handoff_json", RUN / "roles/executor/r1-remediation-02/w09-bridge/handoff.json",
     "free research preparation handoff (advice only)",
     "b1820987692ac6ceb3c715bf3f670938af593a1e568d9c8c29e5d00eec54082c"),
    ("preparation_handoff_md", RUN / "roles/executor/r1-remediation-02/w09-bridge/handoff.md",
     "free research preparation handoff narrative", None),
    ("root_causes", RUN / "diagnosis/r1-final3-review-20261022/root_causes.json",
     "three-review root cause set and 49-claim union",
     "45e088482d956ce18d6fd64548aed69711299c11fb35fc35df795a8efca72bab"),
    ("sealed_final3_input", RUN / "execution_replays/r1-remediation-01/phase_b/forecast/final3-input.json",
     "sealed formal old RF input (source of the new main input copy)",
     "e54ba7df7a5914772222e88e56661d0822e251e257814b9dc7c976c454660257"),
    ("sealed_final3_forecast", RUN / "execution_replays/r1-remediation-01/phase_b/forecast/final3-forecast.json",
     "sealed formal old RF output (old-path comparison only)",
     "41ea79efa319226ac93e65d5210bb304b4d458cfac95ef5998fdf06eaf12279d"),
    ("verified_source_pages", RUN / "execution_replays/r1-remediation-02/phase_b/research/verified-source-pages.json",
     "two-original ten-page verified text inventory",
     "66dced5bfbe7c5b6f206e62252a8f9dfca86d03b4e17293cb053b2a076537e7a"),
    ("source_page_addendum", RUN / "execution_replays/r1-remediation-02/phase_b/research/source-page-addendum-20261023.json",
     "annual p183 exact segment table addendum",
     "993cc92c0c914430e5f93edfca6b3bbc421624da146490435c4dda3f0e478a98"),
    ("claim_scope_bindings", RUN / "execution_replays/r1-remediation-02/phase_b/research/w09-preparation/claim-scope-bindings.json",
     "49-claim scope/role binding advice (proposal only)",
     "7e7dd04ecf6b9c20194790af268f87d4f9ac3644e5e60bbd8bf45408eb43cf88"),
    ("claim_scope_bindings_md", RUN / "execution_replays/r1-remediation-02/phase_b/research/w09-preparation/claim-scope-bindings.md",
     "human-readable claim scope advice",
     "72c1764a32e0e085ed4ec11479fd776e2579fbc4ae38a5e190e0dab28c8ab260"),
    ("component_bridge", RUN / "execution_replays/r1-remediation-02/phase_b/research/w09-preparation/component-bridge.json",
     "recomputable non-TIDES component bridge (advice only)",
     "95eccc0622b12ec5e292ae6817ab2154a7f98da44ab287255f2d9df09cb40bc7"),
    ("component_bridge_md", RUN / "execution_replays/r1-remediation-02/phase_b/research/w09-preparation/component-bridge.md",
     "component bridge narrative and falsifiers",
     "631730a903466d9179507fb97aa4f94dae77640f632d654fc66d41e41dcfe12d"),
    ("rpo_role_advice", RUN / "execution_replays/r1-remediation-02/phase_b/research/w09-preparation/rpo-role-advice.json",
     "RPO parameter kind/role advice", "70d04b6f58be2c0075ab90ddf596905392603897c3dc4653b1287c6c347e605d"),
    ("claim_binding_request", RUN / "execution_replays/r1-remediation-02/phase_b/research/w09-preparation/claim-binding-request.json",
     "declarative input of the preparation binding script",
     "5672fc76cd6a18b613cab971e079abc8c0a8c8a36829c6105451e9b340fbec7f"),
    ("calculation_request", RUN / "execution_replays/r1-remediation-02/phase_b/research/w09-preparation/calculation-request.json",
     "declarative input of the preparation calculation script",
     "1edb0a67691e95ea5277a37a4366170a71214a73fa51f0d319989131d5370f2a"),
    ("preparation_receipt", RUN / "execution_replays/r1-remediation-02/phase_b/research/w09-preparation/receipt.json",
     "preparation receipt with declared SHAs", "d52c091b122ea8ffc36738a0500a19a5308a46f56bf5340a8e7cbe7f1a240271"),
    ("prepare_w09_script", RUN / "roles/executor/r1-remediation-02/w09-bridge/prepare_w09.py",
     "preparation script (read only; not executed in place)",
     "9639f6fe2d1aa7da347cb89ca702c476b4c24c6e62117a016474ca2655cddfe0"),
    ("selfcheck_w09_script", RUN / "roles/executor/r1-remediation-02/w09-bridge/selfcheck_w09.py",
     "preparation self-check script (read only; not executed in place)",
     "4c3030c0def137b4ad8603fe3fc7c720922f06c20159d7f49f53ef28d69dc5df"),
    ("public_bundle", RUN / "reports/r1-remediation-01/storage-source-inventory/B/public-bundle.json",
     "old paid W07 public summary bundle (415965B expected)",
     "d4aaddb10fedc7204cb8e278bb998380c59eff44ce8c7a4dac0be85453bf62e4"),
    ("source_refs_index", RUN / "execution_replays/r1-remediation-01/phase_b/research/source_refs_index.json",
     "eleven existing SourceRef records", None),
    ("phase_b_manifest", RUN / "execution_replays/r1-remediation-01/phase_b/research/phase_b_manifest.json",
     "phase B research manifest (historical evidence inventory)", None),
    ("audit_scope", RUN / "scope.json", "central audit run scope (read-only reference)", None),
    ("final3_review_task_plan", RUN / "remediation/r1-final3-review-20261022/task_plan.md",
     "three-review remediation plan", None),
]


def sha256(path: Path) -> tuple[str, int]:
    digest, size = hashlib.sha256(), 0
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
            size += len(chunk)
    return digest.hexdigest(), size


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=WORKDIR, capture_output=True,
                          text=True, encoding="utf-8", check=False).stdout.strip()


def main() -> int:
    rows, mismatches = [], []
    for logical, path, purpose, expected in ITEMS:
        if not path.is_file():
            rows.append({"logical_name": logical, "path": str(path), "status": "MISSING",
                         "purpose": purpose})
            continue
        digest, size = sha256(path)
        row = {"logical_name": logical, "path": str(path), "sha256": digest,
               "byte_size": size, "purpose": purpose, "access": "read_only",
               "card_expected_sha256": expected}
        if expected is not None and expected != digest:
            row["sha_matches_card_expectation"] = False
            mismatches.append(logical)
        elif expected is not None:
            row["sha_matches_card_expectation"] = True
        rows.append(row)
    record = {
        "schema_version": "w09-readonly-inputs/1",
        "package_id": "W09-RF-RESEARCH",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "note": ("Reproducibility inventory only, not authorization or quality acceptance. "
                 "No file listed here is modified by this package."),
        "run_alias": "RUN",
        "run_root": str(RUN),
        "workdir": str(WORKDIR),
        "python": {"executable": sys.executable, "version": platform.python_version()},
        "git": {"start_head": git("rev-parse", "HEAD"),
                "branch": git("branch", "--show-current"),
                "status_short": git("status", "--short")},
        "card_path": str(CARD),
        "card_sha256": sha256(CARD)[0],
        "card_bytes": CARD.stat().st_size,
        "mismatch_logical_names": mismatches,
        "inputs": rows,
    }
    OUT.write_text(json.dumps(record, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(OUT), "count": len(rows), "mismatches": mismatches},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
