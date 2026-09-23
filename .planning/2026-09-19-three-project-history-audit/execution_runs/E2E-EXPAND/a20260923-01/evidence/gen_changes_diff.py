"""Generate <ATT>/changes.diff — ONLY this card's new/edited RF files.

No git (card rule): difflib over the current bytes vs the reconstructed
pre-card allowlist (the original3-entry file, read before editing).
"""
from __future__ import annotations

import difflib
import hashlib
from pathlib import Path

RF = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")
ATT = Path(__file__).resolve().parents[1]

ORIGINAL_ALLOWLIST = """{
  "note": "Digests that are deliberately frozen because they are HOST-INDEPENDENT: the declared content SHA-256 of a fixed sample filing.  A digest derived from a machine path (payload hash, cache key, export blob) must NOT be registered here.",
  "registered_hashes": {
    "01819e1c7daad939d1779a8aa729f50f02151192e609cb28c2c405634a8f343d": {
      "where": "tests/test_zr806_real_t2_samples.py:70 (SAMPLES entry companies-zijin-fy2025)",
      "rationale": "Declared content SHA-256 of the 紫金 FY2025 filing, recorded as sample metadata.  Hashing file BYTES is host-independent; the path next to it is what the ratchet baseline covers."
    },
    "004f733e709beea878229ae02b80a952c543129037fc940aaf01b77dfa977a89": {
      "where": "tests/test_zr806_real_t2_samples.py:71 (companies-zijin-fy2024)",
      "rationale": "Declared content SHA-256 of the 紫金 FY2024 filing - bytes, not a host-derived value."
    },
    "eb965857b1e95a9cd6ccdaa3c1e324d4d8558c924d61e9300a12b8e222676124": {
      "where": "tests/test_zr806_real_t2_samples.py:73 (dropbox-starlake-fy2024)",
      "rationale": "Declared content SHA-256 of the 星环科技 FY2024 annual report - bytes, not a host-derived value."
    }
  }
}
"""


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    parts: list[str] = []
    manifest: dict[str, dict] = {}

    for rel in ("e2e/run_cross_repo_chain_e2e.py",
                "tests/test_cross_repo_chain_e2e.py"):
        current = (RF / rel).read_text(encoding="utf-8")
        cur_lines = current.splitlines(keepends=True)
        diff = difflib.unified_diff([], cur_lines, fromfile="/dev/null",
                                    tofile=f"b/{rel}")
        parts.extend(diff)
        manifest[rel] = {
            "kind": "new",
            "after_sha256": sha(current.encode("utf-8")),
            "bytes": len(current.encode("utf-8")),
        }

    rel = "tests/contract/host_assumption_allowlist.json"
    before = ORIGINAL_ALLOWLIST
    after = (RF / rel).read_text(encoding="utf-8")
    diff = difflib.unified_diff(before.splitlines(keepends=True),
                                after.splitlines(keepends=True),
                                fromfile=f"a/{rel}", tofile=f"b/{rel}")
    parts.extend(diff)
    manifest[rel] = {
        "kind": "edited",
        "before_sha256": sha(before.encode("utf-8")),
        "after_sha256": sha(after.encode("utf-8")),
        "bytes_before": len(before.encode("utf-8")),
        "bytes_after": len(after.encode("utf-8")),
        "edit": "11 E2E-EXPAND content-hash pins registered (the "
                "host-assumption guard's own sanctioned mechanism, keeps "
                "step9/test_fc1307a green); 3 pre-existing entries untouched",
    }

    header = [
        "# E2E-EXPAND a20260923-01 — changes to revenue-forecast (only this "
        "card's new/edited files; no git — difflib reconstruction; CW/FF "
        "repos untouched, proven by before/after snapshots)",
        f"# manifest: {manifest}",
        "",
    ]
    out = ATT / "changes.diff"
    out.write_text("\n".join(header) + "".join(parts), encoding="utf-8")
    print(f"written {out} ({out.stat().st_size} bytes)")
    for k, v in manifest.items():
        print(f"  {k}: {v['kind']} after={v['after_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
