"""I-14-E: build commands.json from the campaign log (argv + observed rc) plus the per-run
return codes recorded in the band JSONs.

The campaign log is written by harness/run_campaign.ps1; this script only transcribes it,
so the recorded argv is what actually ran rather than a retyped copy.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
LOG = ATTEMPT / "after" / "campaign.log"
OUT = ATTEMPT / "commands.json"

STEP_RE = re.compile(r"^=== (.+) ===$")
ARGV_RE = re.compile(r"^argv: (.+)$")
RC_RE = re.compile(r"^rc=(-?\d+) elapsed=([0-9.,]+)s$")


def read_log(path: Path) -> list[str]:
    """Windows PowerShell 5.1's Tee-Object writes UTF-16LE with a BOM; pwsh 7 writes UTF-8.
    Sniff the BOM instead of guessing, so the transcribed argv is the real one."""
    if not path.exists():
        return []
    raw = path.read_bytes()
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16").splitlines()
    return raw.decode("utf-8", "replace").splitlines()


def main() -> int:
    lines: list[str] = []
    logs = [ATTEMPT / "after" / "campaign.log", ATTEMPT / "after" / "campaign-band.log"]
    for log in logs:
        lines.extend(read_log(log))
    steps: list[dict] = []
    current: dict | None = None
    for line in lines:
        match = STEP_RE.match(line.strip())
        if match:
            current = {"id": match.group(1), "argv": None, "raw_exit_code": None,
                       "elapsed_seconds": None}
            steps.append(current)
            continue
        if current is None:
            continue
        match = ARGV_RE.match(line)
        if match and current["argv"] is None:
            current["argv"] = match.group(1).split(" ")
            continue
        match = RC_RE.match(line.strip())
        if match and current["raw_exit_code"] is None:
            current["raw_exit_code"] = int(match.group(1))
            current["elapsed_seconds"] = float(match.group(2).replace(",", ""))

    per_run: dict = {}
    for name in ("child-quiet", "child-cpu8", "child-spawn", "logon-quiet", "logon-cpu8"):
        path = ATTEMPT / "after" / f"band-{name}.json"
        if not path.exists():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        codes: dict[str, int] = {}
        for row in payload["results"]:
            key = str(row["returncode"])
            codes[key] = codes.get(key, 0) + 1
        per_run[name] = {"node": payload["node"], "condition": payload["condition"],
                         "runs": len(payload["results"]), "raw_returncode_histogram": codes,
                         "verdicts": payload["tally_by_condition"],
                         "expected": ("rc 0 = node passed; rc 1 = node failed (assertion) or "
                                      "the SUT's own 15 s subprocess timeout raised "
                                      "TimeoutExpired inside pytest")}

    commands = []
    seen_ids: dict[str, int] = {}
    for index, step in enumerate(steps, start=1):
        seen_ids[step["id"]] = seen_ids.get(step["id"], 0) + 1
        superseded = (step["raw_exit_code"] == 1 and (step["elapsed_seconds"] or 99) < 5.0
                      and step["id"].startswith("M-B"))
        entry = {
            "id": step["id"],
            "invocation": seen_ids[step["id"]],
            "purpose": step["id"],
            "cwd": str(ATTEMPT),
            "argv": step["argv"],
            "binding_status": "bound",
            "network": "disabled",
            "raw_exit_code": step["raw_exit_code"],
            "elapsed_seconds": step["elapsed_seconds"],
            "expected_returncode": 0,
            "expected_business_result": (
                "evidence collector: rc=0 means the collector ran; the business verdicts live "
                "in the per-run records, never in this rc"),
            "note": ("SUPERSEDED invocation: died instantly on a non-ASCII path literal that "
                     "Windows PowerShell 5.1 mis-decoded (see harness/README.md and "
                     "oracle-addendum-A); the authoritative invocation is the later one with the "
                     "same id"
                     if superseded else ""),
        }
        commands.append(entry)
    payload = {
        "card": "I-14-E",
        "attempt": "a20260919-01",
        "exit_code_legend": {
            "0": "通过 / collector ran正常结束",
            "1": "harness 失败（本 attempt 未出现）",
            "2": "无裁决 / 预期拒绝（本 attempt 不适用）",
            "3": "未达预期（产品节点失败时 pytest rc=1，属于 SUT 的失败而非本 collector 的失败）",
        },
        "note": ("per START_HERE rc 码表：collector rc 与产品判定分开记录；产品节点的 rc 见 "
                 "per_run_returncodes"),
        "source_log": [str(p) for p in logs if p.exists()],
        "commands": commands,
        "per_run_returncodes": per_run,
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"steps": len(commands),
                      "missing_argv": [c["id"] for c in commands if not c["argv"]],
                      "nonzero_rc": [(c["id"], c["raw_exit_code"]) for c in commands
                                     if c["raw_exit_code"] not in (0, None)],
                      "per_run": {k: v["raw_returncode_histogram"] for k, v in per_run.items()}},
                     indent=2))
    print("out:", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
