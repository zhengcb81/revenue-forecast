"""GUARD-MERGE close check: oracle unchanged, production untouched, deliverable hashes."""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys
from datetime import datetime, timezone

A = pathlib.Path(sys.argv[1])
CW = pathlib.Path(r"C:\Users\郑曾波\Projects\company-wiki\src\company_wiki\source_catalog")
RF = pathlib.Path(r"C:\Users\郑曾波\Projects\revenue-forecast")


def sha(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


PROD = {
    "prompt_injection_guard.py": "f900a13d7c22fe3bd742485c6b603de11b92a56d2414a2a046216ccd3b0b9c08",
    "prompt_injection.py": "7b22f23918d5e6b083a3c5272de2ed26c8a0c420b007f1268c664c0c86139618",
    "readiness_graph.py": "3f4c43b0049eca71fde4f7d9152b02674a26679b4470f6607383eb1820685acc",
}

freeze = json.loads((A / "oracle_freeze.json").read_text(encoding="utf-8-sig"))
oracle_now = sha(A / "oracle.md")

checks = {
    "oracle_unchanged_since_freeze": oracle_now == freeze["sha256"],
    "oracle_sha256": oracle_now,
    "production_untouched": all(sha(CW / k) == v for k, v in PROD.items()),
    "production_live": {k: sha(CW / k) for k in PROD},
    "production_matches_before_copies": all(
        sha(CW / k) == sha(A / "before" / k) for k in PROD),
    "rf_tests_written": False,
    "merged_faces": {k: sha(A / "iso" / k) for k in PROD},
}

deliverables = {}
for rel in ("oracle.md", "oracle_freeze.json", "binding.json", "commands.json",
            "decision.md", "changes.diff", "handoff.json", "recovery.md",
            "evidence/SUMMARY.md",
            "iso/prompt_injection_guard.py", "iso/prompt_injection.py",
            "iso/readiness_graph.py"):
    p = A / rel
    deliverables[rel] = {"sha256": sha(p), "bytes": p.stat().st_size}

payload = {
    "card": "GUARD-MERGE",
    "attempt": "a20260922-01",
    "closed_utc": datetime.now(timezone.utc).isoformat(),
    "checks": checks,
    "deliverables": deliverables,
    "git": "zero git commands executed (changes.diff is python difflib)",
    "production_writes": 0,
}
(A / "evidence" / "final_deliverable_hashes.json").write_text(
    json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({k: checks[k] for k in
                  ("oracle_unchanged_since_freeze", "oracle_sha256",
                   "production_untouched", "production_matches_before_copies")},
                 ensure_ascii=False, indent=2))
print(json.dumps({k: v["sha256"][:16] for k, v in deliverables.items()},
                 ensure_ascii=False, indent=2))
ok = (checks["oracle_unchanged_since_freeze"]
      and checks["production_untouched"]
      and checks["production_matches_before_copies"]
      and checks["merged_faces"]["prompt_injection_guard.py"]
      == "d71254782c10cd6d58c768eeb50e220de5e3d8047709e26f0604b5c59e67df0d")
sys.exit(0 if ok else 1)
