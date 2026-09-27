"""I08CR-c11 — production state re-check: promoted anchors, trust file absent,
git porcelain empty (=> zero production writes by this card). Read-only."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

RF = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")
ATT = Path(__file__).resolve().parents[1]
EVID = ATT / "evidence"

EXPECT = {
    "scripts/revenue_publication.py": "bc2bb4a33e36ed9ad82bc4ffe33e57de8999002c2c7910b9c8b9d1565678fcd0",
    "scripts/revenue_core.py": "8a761498f5eb729e4f4227f2a315d709253f8b96acf7baa7253ab425e73ac883",
    "scripts/revenue_report.py": "212f00598feca408dc429d4c7a5332131ce25f1165b079347e4b295345df7d3b",
    "scripts/publication_registry.py": "29aaae4f9864d9c4dbb92720744daa49315a2980dfa158b0e3666cb86d886344",
    "scripts/contracts/evidence.py": "054e364a7a5c428f43c6378f795429751b26f24af8de07e22da4b3d0ac8a4561",
}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    out = {"anchors": {}}
    for rel, want in EXPECT.items():
        got = sha(RF / rel)
        out["anchors"][rel] = {"expected": want, "measured": got, "match": got == want}
    trust = RF / "config" / "trusted_signer_public_keys.json"
    out["trust_file_absent"] = not trust.exists()
    r = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all", "--", "scripts", "tests", "config", "artifacts"],
        cwd=RF, capture_output=True, text=True,
    )
    out["git_porcelain_rc"] = r.returncode
    out["git_porcelain_lines"] = [l for l in r.stdout.splitlines() if l.strip()]
    out["git_porcelain_empty"] = not out["git_porcelain_lines"]
    ok = all(v["match"] for v in out["anchors"].values()) and out["trust_file_absent"] and out["git_porcelain_empty"]
    out["all_ok"] = ok
    (EVID / "c11_production_state.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))
    print("C11_ALL_OK:", ok)
    return 0 if ok else 3


if __name__ == "__main__":
    raise SystemExit(main())
