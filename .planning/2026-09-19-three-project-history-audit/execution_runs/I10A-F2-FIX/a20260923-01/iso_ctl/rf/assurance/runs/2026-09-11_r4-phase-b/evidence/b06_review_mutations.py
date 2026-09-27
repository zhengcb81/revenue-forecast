"""B.VR (B06) mutation harness - runs on a TEMP copy of the HEAD tree.

Never touches the product checkout: the copy was produced with
``git archive`` and lives under %TEMP%.  Each mutation is a literal string
replacement in the copy's resolver.py; the file is restored from a pristine
backup between runs and the final hash is verified.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

TREE = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
    r"C:\Users\郑曾波\AppData\Local\Temp\b06_review"
)
RESOLVER = TREE / "src" / "company_wiki" / "source_catalog" / "resolver.py"
BACKUP = TREE / "resolver.py.b06review.bak"

B06_TESTS = "tests/contract/test_r4b06_qualification.py"
WIDER = (
    "tests/contract/test_r4b06_qualification.py "
    "tests/contract/test_resolution_envelope_fc704.py "
    "tests/contract/test_fc902_bundle_in_resolver.py "
    "tests/contract/test_fc905_receipt_envelope.py "
    "tests/contract/test_zr404_envelope_trace_rationale.py"
)

MUTATIONS: list[dict] = [
    {
        "id": "M1_preview_is_verified_input",
        "why": "drop the preview branch: any non-blocking gap still says verified_input",
        "old": '    if gaps:\n        return QUALIFICATION_PREVIEW, "locally readable; provenance gaps: " + ", ".join(gaps)\n',
        "new": "",
    },
    {
        "id": "M2_conflict_ignored",
        "why": "ignore the response-level conflict fact",
        "old": "    if conflict_reason:\n        return QUALIFICATION_BLOCKED, conflict_reason\n",
        "new": "",
    },
    {
        "id": "M3_identity_not_blocking",
        "why": "identity_missing no longer blocks",
        "old": '_QUALIFICATION_BLOCKING_GAPS = ("identity_missing", "period_missing", "source_missing")',
        "new": '_QUALIFICATION_BLOCKING_GAPS = ("period_missing", "source_missing")',
    },
    {
        "id": "M4_conflict_reader_blind",
        "why": "the conflict reader never reports anything",
        "old": "    if store is None or not document_id:\n        return \"\"",
        "new": "    if True:\n        return \"\"",
    },
    {
        "id": "M5_qualification_not_exported",
        "why": "to_dict drops the new key (breaks additivity)",
        "old": '            "qualification": self.qualification,\n',
        "new": "",
    },
    {
        "id": "M6_envelope_wiring_ignores_gaps",
        "why": "envelope keeps the conflict read but never applies the identity/period/source gaps",
        "old": "        gaps = _qualification_gaps(handle)\n",
        "new": "        gaps = [] if getattr(handle, \"capture_ready\", False) else _qualification_gaps(handle)\n",
    },
    {
        "id": "M7_qualification_for_every_response",
        "why": "fabricate a label even when nothing was served",
        "old": '    qualification: dict[str, Any] | None = None\n',
        "new": (
            '    qualification: dict[str, Any] | None = {\n'
            '        "label": QUALIFICATION_VERIFIED_INPUT, "gaps": [], "reason": ""\n'
            '    }\n'
        ),
    },
    {
        "id": "M8_schema_version_bumped",
        "why": "envelope_schema_version moves off 1.0",
        "old": 'RESOLUTION_ENVELOPE_SCHEMA_VERSION = "1.0"',
        "new": 'RESOLUTION_ENVELOPE_SCHEMA_VERSION = "1.1"',
    },
    {
        "id": "M9_envelope_skips_conflict_read",
        "why": "envelope wiring drops the S-13 conflict read",
        "old": "        conflict_reason = _metadata_conflict_reason(store, handle.document_id)\n",
        "new": '        conflict_reason = ""\n',
    },
    {
        "id": "M10_gap_map_ignored",
        "why": "missing_capture_fields no longer produce gap codes",
        "old": "    missing = [_GAP_BY_MISSING_FIELD.get(str(name), \"\") for name in\n               tuple(getattr(handle, \"missing_capture_fields\", ()) or ())]",
        "new": "    missing: list[str] = []",
    },
    {
        "id": "M11_period_rule_plan_conformant",
        "why": "the STRICTER rule the plan registered (no fiscal_year => period_missing)",
        "old": "        getattr(handle, \"fiscal_year\", None) is None\n        and not str(getattr(handle, \"published_date\", \"\") or \"\").strip()\n        and \"period_missing\" not in missing",
        "new": "        getattr(handle, \"fiscal_year\", None) is None\n        and \"period_missing\" not in missing",
    },
]


def run_tests(selection: str) -> dict:
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", *selection.split(), "-q", "-p", "no:cacheprovider"],
        cwd=str(TREE),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    tail = [line for line in (proc.stdout or "").splitlines() if line.strip()][-3:]
    return {
        "exit": proc.returncode,
        "tail": tail,
        "failed_tests": [
            line.split("::")[-1].split()[0]
            for line in (proc.stdout or "").splitlines()
            if line.startswith("FAILED")
        ],
    }


def main() -> None:
    pristine = RESOLVER.read_text(encoding="utf-8")
    pristine_sha = hashlib.sha256(pristine.encode("utf-8")).hexdigest()
    shutil.copy2(RESOLVER, BACKUP)
    results = []
    try:
        for mutation in MUTATIONS:
            if mutation["old"] not in pristine:
                results.append(
                    {
                        "id": mutation["id"],
                        "status": "not_applied",
                        "why": mutation["why"],
                        "detail": "anchor not found verbatim",
                    }
                )
                continue
            patched = pristine.replace(mutation["old"], mutation["new"], 1)
            RESOLVER.write_text(patched, encoding="utf-8")
            narrow = run_tests(B06_TESTS)
            wide = run_tests(WIDER) if narrow["exit"] == 0 else None
            RESOLVER.write_text(pristine, encoding="utf-8")
            results.append(
                {
                    "id": mutation["id"],
                    "why": mutation["why"],
                    "status": "killed" if narrow["exit"] != 0 else "survived",
                    "b06_file": narrow,
                    "wider_targeted": wide,
                }
            )
    finally:
        RESOLVER.write_text(pristine, encoding="utf-8")
    restored_sha = hashlib.sha256(RESOLVER.read_text(encoding="utf-8").encode("utf-8")).hexdigest()
    out = {
        "tree": str(TREE),
        "pristine_sha256": pristine_sha,
        "restored_sha256": restored_sha,
        "restored_identical": pristine_sha == restored_sha,
        "mutations": results,
    }
    target = Path(__file__).with_name("b06_review_mutations.json")
    target.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({m["id"]: m["status"] for m in results}, indent=1))
    print("restored_identical:", out["restored_identical"])


if __name__ == "__main__":
    main()
