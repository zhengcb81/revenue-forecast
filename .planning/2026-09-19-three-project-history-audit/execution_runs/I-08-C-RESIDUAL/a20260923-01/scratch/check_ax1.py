"""I08CR-c8 — AX-1 (F4/F5): decode the surviving r1 RED stdout (register 22/补1 erratum
re-verification) + B1-PREREQ evidence-protocol / freeze-chain presence. Read-only."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ATT = Path(__file__).resolve().parents[1]
EVID = ATT / "evidence"
PLAN = ATT.parents[2]
B1 = PLAN / "execution_runs" / "B1-I08C-product-fixes" / "a20260921-01"
B1P = PLAN / "execution_runs" / "B1-PREREQ" / "a20260922-01"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    out = {}
    r1 = B1 / "before" / "b1_unfixed.stdout.txt"
    raw = r1.read_bytes()
    out["r1_red_stdout"] = {"path": str(r1), "sha256": sha(r1), "bytes": len(raw)}
    decoded = None
    for enc in ("utf-16", "utf-8-sig", "utf-8"):
        try:
            decoded = raw.decode(enc)
            out["r1_red_stdout"]["decoded_with"] = enc
            break
        except UnicodeDecodeError:
            continue
    out["r1_red_stdout"]["contains_10_failed_2_passed"] = (
        decoded is not None and "10 failed, 2 passed" in decoded
    )
    out["r1_red_stdout"]["contains_summary_line"] = (
        decoded is not None and "10 failed, 2 passed in" in decoded
    )
    # which nodes passed in r1 (the register erratum says R8 passed trivially)
    out["r1_red_stdout"]["has_passed_nodes"] = (
        decoded.count("PASSED") if decoded else None
    )
    out["r1_red_stdout"]["has_failed_nodes"] = decoded.count("FAILED") if decoded else None

    freeze = B1P / "freeze.json"
    out["b1prereq_freeze_chain"] = {
        "freeze_json_present": freeze.exists(),
        "freeze_json_sha256": sha(freeze) if freeze.exists() else None,
    }
    if freeze.exists():
        data = json.loads(freeze.read_text(encoding="utf-8"))
        out["b1prereq_freeze_chain"]["keys"] = sorted(data.keys())[:20]
        for k in ("entries", "chain", "files", "items"):
            if isinstance(data.get(k), list):
                out["b1prereq_freeze_chain"][f"{k}_count"] = len(data[k])
    sums = [p for p in (B1P / "evidence").rglob("*") if p.is_file() and "SUMS" in p.name.upper()]
    out["sha256sums_files"] = [{"path": str(p), "sha256": sha(p), "lines": len(p.read_text(encoding="utf-8", errors="replace").splitlines())} for p in sums]
    out["b1prereq_oracle_hash_pin_policy_present"] = "hash-pin" in (
        (B1 / "oracle.md").read_text(encoding="utf-8", errors="replace")
    )

    ok = (
        out["r1_red_stdout"]["contains_10_failed_2_passed"]
        and out["b1prereq_freeze_chain"]["freeze_json_present"]
    )
    out["all_ok"] = ok
    (EVID / "AX1_f4f5_checks.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))
    print("AX1_ALL_OK:", ok)
    return 0 if ok else 3


if __name__ == "__main__":
    raise SystemExit(main())
