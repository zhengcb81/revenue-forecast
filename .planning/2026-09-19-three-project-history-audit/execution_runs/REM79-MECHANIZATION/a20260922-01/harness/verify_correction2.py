#!/usr/bin/env python3
"""verify_correction2.py — the parent-ordered quote-sample mini-GREEN (C2.3).

Declared in oracle.md CORRECTION 2 §C2.3 BEFORE this sample file existed:
file evidence/correction2/quote_samples.md, payloads at lines 4/6/8/10/12/14,
expected flags = [12, 14], expected NOT flagged = [4, 6, 8, 10], exit 1.

Runs the real checker as a subprocess, compares, writes raw outputs under
evidence/correction2/.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parent.parent
PY = sys.executable or "python"
SAMPLE = "evidence/correction2/quote_samples.md"
EXPECT_FLAGGED = [12, 14]
EXPECT_NOT = [4, 6, 8, 10]


def main() -> int:
    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    out_dir = ATTEMPT / "evidence/correction2"
    out_dir.mkdir(parents=True, exist_ok=True)

    txt = subprocess.run(
        [PY, "-B", "tools/check_domain_assertions.py", SAMPLE],
        capture_output=True, encoding="utf-8", errors="replace",
        cwd=str(ATTEMPT), env=env,
    )
    (out_dir / "quote_samples_text_stdout.txt").write_bytes(txt.stdout.encode("utf-8"))
    (out_dir / "quote_samples_text_stderr.txt").write_bytes(txt.stderr.encode("utf-8"))

    js = subprocess.run(
        [PY, "-B", "tools/check_domain_assertions.py", "--json", SAMPLE],
        capture_output=True, encoding="utf-8", errors="replace",
        cwd=str(ATTEMPT), env=env,
    )
    (out_dir / "quote_samples_json.json").write_bytes(js.stdout.encode("utf-8"))
    if js.returncode not in (0, 1):
        print(f"FATAL checker rc={js.returncode}: {js.stderr}", file=sys.stderr)
        return 2
    report = json.loads(js.stdout)
    flagged = sorted(v["line"] for v in report["files"][0].get("violations", []))
    verdict = {
        "declared_in": "oracle.md CORRECTION 2 §C2.3 (frozen before the sample existed)",
        "expect_flagged": EXPECT_FLAGGED,
        "expect_not_flagged": EXPECT_NOT,
        "reported_flagged": flagged,
        "rc": js.returncode,
        "expect_rc": 1,
        "pass": flagged == EXPECT_FLAGGED and js.returncode == 1
        and not (set(flagged) & set(EXPECT_NOT)),
        "verdict": None,
    }
    verdict["verdict"] = "C2_MINI_GREEN_PASS" if verdict["pass"] else "C2_MINI_GREEN_FAIL"
    (out_dir / "quote_samples_verdict.json").write_text(
        json.dumps(verdict, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(verdict, ensure_ascii=False, indent=2))
    return 0 if verdict["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
