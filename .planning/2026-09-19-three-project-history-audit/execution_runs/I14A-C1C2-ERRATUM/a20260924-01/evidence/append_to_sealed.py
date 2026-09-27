"""Append the two correction sections to the SEALED I-14-A attempt (append-only).

Hard guards (the script refuses to write if any of these fails):
  * the sealed file still has its registered pre-image size and sha256;
  * the assembled bytes keep the pre-image as an exact prefix
    (sha256(first N bytes) == pre-image sha256)  => prefix_bytes_preserved=true;
  * the appended section itself declares its own pre-image and the
    "第 X 行已过时，以本节为准" wording required by T1-12 (1).

After the write it re-reads the file from disk and re-verifies the prefix, then
records pre/post sha256, sizes, appended size and the prefix proof in
evidence/prefix_proofs.json.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
EXEC_RUNS = ATTEMPT.parents[1]
SEALED = EXEC_RUNS / "I-14-A" / "a20260919-01"
EVID = ATTEMPT / "evidence"

TARGETS = [
    {
        "file": SEALED / "oracle.md",
        "append": EVID / "append_oracle_section.md",
        "pre_bytes": 20457,
        "pre_sha256": "87775f2f4ff025e4d104fd1dfe23d7f7bfc75a20520f8859732133e96ec84bb7",
        "corrects_lines": ["117-122", "119-120", "85", "219-220"],
    },
    {
        "file": SEALED / "decision.md",
        "append": EVID / "append_decision_section.md",
        "pre_bytes": 8467,
        "pre_sha256": "a1a9d37478ffb42f15877ac29b9ecb044b8f402f4d77f532d1a25f1646bfda24",
        "corrects_lines": ["91-92", "97"],
    },
]


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def main() -> int:
    results = []
    for t in TARGETS:
        path: Path = t["file"]
        app_path: Path = t["append"]

        pre = path.read_bytes()
        pre_sha = sha(pre)
        if len(pre) != t["pre_bytes"]:
            raise SystemExit(f"ABORT: {path.name} size {len(pre)} != registered {t['pre_bytes']}")
        if pre_sha != t["pre_sha256"]:
            raise SystemExit(f"ABORT: {path.name} sha256 {pre_sha} != registered {t['pre_sha256']}")

        app = app_path.read_bytes()
        if not app.endswith(b"\n"):
            raise SystemExit(f"ABORT: {app_path.name} must end with a newline")
        if b"\r\n" in app:
            raise SystemExit(f"ABORT: {app_path.name} must stay LF-only (sealed files are LF)")

        text = app.decode("utf-8")
        for needle in ("prefix_bytes_preserved=true", "以本节为准", t["pre_sha256"],
                       str(t["pre_bytes"])):
            if needle not in text:
                raise SystemExit(f"ABORT: {app_path.name} does not carry required marker: {needle}")

        assembled = pre + app
        prefix_ok_memory = sha(assembled[:len(pre)]) == t["pre_sha256"]
        if not prefix_ok_memory:
            raise SystemExit(f"ABORT: in-memory prefix proof failed for {path.name}")

        path.write_bytes(assembled)          # append-only: pre bytes untouched

        on_disk = path.read_bytes()
        prefix_ok_disk = sha(on_disk[:len(pre)]) == t["pre_sha256"]
        untouched_ok = on_disk[:len(pre)] == pre
        if not (prefix_ok_disk and untouched_ok):
            raise SystemExit(f"ABORT: on-disk prefix proof failed for {path.name}")

        results.append({
            "path": str(path.relative_to(SEALED.parents[2])),
            "append_source": str(app_path.relative_to(ATTEMPT.parents[2])),
            "pre_image": {"bytes": len(pre), "sha256": pre_sha},
            "appended_bytes": len(app),
            "post_image": {"bytes": len(on_disk), "sha256": sha(on_disk)},
            "prefix_bytes_preserved": bool(prefix_ok_disk and untouched_ok),
            "prefix_proof_method": f"sha256(first {len(pre)} bytes) == pre-image sha256, "
                                   "re-computed on disk after the write",
            "prefix_proof_in_memory_before_write": bool(prefix_ok_memory),
            "first_bytes_identical_to_pre_image": bool(untouched_ok),
            "corrects_lines_of_sealed_file": t["corrects_lines"],
            "append_text_sha256": sha(app),
            "append_text_file": app_path.name,
            "mode": "append-only (T1-12 (1)); no pre-existing byte modified",
        })
        print(f"{path.name}: pre {len(pre)}B/{pre_sha[:16]} -> post {len(on_disk)}B/"
              f"{sha(on_disk)[:16]}  prefix_bytes_preserved={prefix_ok_disk}")

    payload = {
        "purpose": "append-only correction proofs for the sealed I-14-A/a20260919-01 files",
        "sealer": "I14A-C1C2-ERRATUM/a20260924-01 (implementer of the append-only erratum)",
        "authority": ["OWNER_DECISIONS.md 十 L126", "OWNER_DECISIONS.md 十一 L143",
                      "T1-12 (1)", "T1-21",
                      "execution_runs/I14A-D1-OPS-REVIEW/a20260924-01/ruling.md "
                      "sha256 ede71bfa7b1a521b6f3252af539ef8aded9f645b92be82ac12460a93b11ab6c8"],
        "files": results,
        "all_prefixes_preserved": all(r["prefix_bytes_preserved"] for r in results),
    }
    out = EVID / "prefix_proofs.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    parsed = json.loads(out.read_text(encoding="utf-8"))
    print(json.dumps({"written": str(out), "all_prefixes_preserved":
                      parsed["all_prefixes_preserved"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
