#!/usr/bin/env python
"""Family (b) — rerun of I-10-B `frozen_regression_rerun.py` WITHOUT writing into I-10-B.

I-10-B's script derives its input/output paths from its own location
(`RUN = HERE.parent`, `SCRATCH = RUN/_scratch_import`, `EV = RUN.parent.parent`),
so executing it in place would overwrite I-10-B's frozen evidence. This wrapper
imports the ORIGINAL script byte-for-byte (sha recorded in run_log) and redirects
only the module globals RUN/SCRATCH to this attempt; `EV` keeps its imported
value (= .../execution_runs), which is the correct card-input root for both.

Inputs are local copies of I-10-B's frozen registry variants; their sha256 are
checked against the source before running.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import sys
from pathlib import Path

ATT = Path(__file__).resolve().parents[1]
EXEC_RUNS = ATT.parent.parent
SRC = EXEC_RUNS / "I-10-B" / "a20260919-01" / "scripts" / "frozen_regression_rerun.py"
SRC_SCRATCH = EXEC_RUNS / "I-10-B" / "a20260919-01" / "_scratch_import"
LOCAL_SCRATCH = ATT / "_scratch_i10b"
OUT = ATT / "frozen_regression_rerun.json"
REFERENCE = EXEC_RUNS / "I-10-B" / "a20260919-01" / "frozen_regression_rerun.json"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    copy_rows = []
    for rel in ("before/model_registry.py", "before/model_extensions.py",
                "after/model_registry.py", "after/model_extensions.py"):
        src = SRC_SCRATCH / rel
        dst = LOCAL_SCRATCH / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists() or sha(dst) != sha(src):
            shutil.copyfile(src, dst)
        copy_rows.append({"file": rel, "source_sha256": sha(src),
                          "local_sha256": sha(dst), "identical": sha(src) == sha(dst)})

    spec = importlib.util.spec_from_file_location("i10b_frozen_regression_rerun", SRC)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["i10b_frozen_regression_rerun"] = mod
    spec.loader.exec_module(mod)  # noqa: S603 — local frozen card script, no network

    ev_imported = str(mod.EV)
    mod.RUN = ATT
    mod.SCRATCH = LOCAL_SCRATCH
    rc = mod.main()

    payload = {
        "artifact": "i10b_frozen_regression_rerun_rerun",
        "source_script": str(SRC),
        "source_script_sha256": sha(SRC),
        "ev_path_used": ev_imported,
        "input_copies": copy_rows,
        "harness_rc": rc,
        "any_phase_flipped": json.loads(OUT.read_text(encoding="utf-8"))["any_phase_flipped"],
        "reference_json": str(REFERENCE),
        "reference_sha256": sha(REFERENCE),
        "output_sha256": sha(OUT),
        "byte_identical_to_i10b_frozen_output": sha(OUT) == sha(REFERENCE),
    }
    (ATT / "evidence" / "i10b_frr_rerun.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    print(json.dumps(payload, ensure_ascii=False, indent=1))
    return 0 if rc == 0 else rc


if __name__ == "__main__":
    raise SystemExit(main())
