"""Apply the I-06-A candidate overlay to the isolated clone.

Usage:
  <py> -X utf8 -B scripts/w06a_apply_candidate.py

Creates iso/rf_fixed from iso/rf (pristine bytes) and applies the candidate
change to scripts/source_preparation.py inside the clone.  No product tree is
touched.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATTEMPT = HERE.parent
ISO = ATTEMPT / "iso"
SRC_TREE = ISO / "rf"
DST_TREE = ISO / "rf_fixed"
CANDIDATE = ISO / "candidate"

NEW_BLOCK = '''    # ---- I-06-A CANDIDATE (UNRATIFIED) ----------------------------------
    # Register the durable demand BEFORE the not_reviewed safety verdict is
    # applied: the block must be recoverable, and the verdict itself is
    # unchanged.  Any store failure raises, so `demand_queued` is never
    # reported for a demand that was not persisted.
    prompt_injection_status = envelope.get("prompt_injection_status")
    if prompt_injection_status is None:
        prompt_injection_status = "not_reviewed"  # defensive N-1 default
    from w06a_candidate_patch import _register_demand, block_message

    registration = _register_demand(request=request, handle=handle, envelope=envelope)
    if prompt_injection_status == "not_reviewed":
        raise RuntimeError(
            block_message(
                prompt_injection_status=prompt_injection_status,
                registration=registration,
            )
        )
    # ---- end I-06-A CANDIDATE -------------------------------------------
'''

REPLACED = '''    prompt_injection_status = envelope.get("prompt_injection_status")
    if prompt_injection_status is None:
        prompt_injection_status = "not_reviewed"  # defensive N-1 default
    if prompt_injection_status == "not_reviewed":
        raise RuntimeError(
            "prompt injection not reviewed — source preparation blocked "
            "per policy (prompt_injection_status=not_reviewed)")
'''


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    if DST_TREE.exists():
        shutil.rmtree(DST_TREE)
    shutil.copytree(SRC_TREE, DST_TREE)
    target = DST_TREE / "scripts" / "source_preparation.py"
    text = target.read_text(encoding="utf-8")
    if REPLACED not in text:
        raise SystemExit("candidate anchor not found — re-locate the block")
    patched = text.replace(REPLACED, NEW_BLOCK)
    target.write_text(patched, encoding="utf-8", newline="\n")
    for name in ("processing_demand_store.py", "w06a_candidate_patch.py"):
        shutil.copyfile(CANDIDATE / name, DST_TREE / "scripts" / name)
    manifest = {
        "clone": str(DST_TREE),
        "pristine_source_preparation_sha256": sha256_file(
            SRC_TREE / "scripts" / "source_preparation.py"
        ),
        "patched_source_preparation_sha256": sha256_file(target),
        "candidate_files": {
            name: sha256_file(DST_TREE / "scripts" / name)
            for name in ("processing_demand_store.py", "w06a_candidate_patch.py")
        },
        "note": "candidate overlay only; iso/rf stays pristine for the baseline run",
    }
    (ATTEMPT / "iso" / "candidate-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
