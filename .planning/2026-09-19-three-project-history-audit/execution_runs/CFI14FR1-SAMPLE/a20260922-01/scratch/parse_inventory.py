"""Per-file pass/fail/skip inventory from a raw pytest byte stream (oracle A3).

Usage:
  parse_inventory.py <raw.txt> <out_summary.json> [<pre_lastfailed.json> <post_lastfailed.json>]

Reads the raw stdout+stderr BYTES captured by cmd /c redirection, derives a per-file
inventory under tests/contract and tests/unit, and reconciles the totals against the
raw final summary line. Nothing is smoothed over: any mismatch is recorded in the
output as `reconciliation`.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import OrderedDict
from pathlib import Path

STATUS_ORDER = ["passed", "failed", "skipped", "error", "xfailed", "xpassed"]

RE_VERBOSE = re.compile(
    r"^(tests/[^\s:]+\.py)::(.*?)\s+"
    r"(PASSED|FAILED|SKIPPED|ERROR|XFAIL|XPASSED)"
    r"(?:\s+\[\s*\d+%])?\s*$"
)
# note: both RE_PROGRESS and the summary nodeids may carry either separator before
# normalization; the loop normalizes `tests\` -> `tests/` before matching.
RE_PROGRESS = re.compile(r"^(tests/[^\s]+\.py)\s+([.sSEXFPxpi]+)\s*\[\s*\d+%]\s*$")
# pytest wraps long progress output: continuation lines carry ONLY chars + percentage
# (observed in this card's raw outputs) and belong to the last path seen.
RE_CONTINUATION = re.compile(r"^([.sSEXFPxpi]+)\s*\[\s*\d+%]\s*$")
RE_COLLECTED = re.compile(r"^collected (\d+) item")
RE_SHORT = re.compile(r"^(FAILED|ERROR)\s+(.+)$")

CHARMAP = {
    ".": "passed",
    "F": "failed",
    "s": "skipped",
    "S": "skipped",
    "E": "error",
    "x": "xfailed",
    "X": "xpassed",
    "p": "xpassed",
    "i": "error",
}

FINAL_NUM = re.compile(
    r"(\d+) (passed|failed|skipped|error|errors|xfail|xpass|xfailed|xpassed|deselected|warning|warnings)"
)


def new_counts() -> "OrderedDict[str, int]":
    return OrderedDict((k, 0) for k in STATUS_ORDER)


def add(counts, status_key, n=1):
    counts[status_key] = counts.get(status_key, 0) + n


def main() -> int:
    raw_path, out_path = Path(sys.argv[1]), Path(sys.argv[2])
    pre_lf = Path(sys.argv[3]) if len(sys.argv) > 3 else None
    post_lf = Path(sys.argv[4]) if len(sys.argv) > 4 else None

    raw = raw_path.read_bytes()
    text = raw.decode("utf-8", errors="replace")
    lines = text.splitlines()

    per_file: "OrderedDict[str, OrderedDict[str, int]]" = OrderedDict()
    failed_nodeids: list[str] = []
    error_nodeids: list[str] = []
    skipped_nodeids: list[str] = []
    node_status: dict[str, str] = {}
    collected_declared = None
    method_votes = {"verbose": 0, "progress_chars": 0, "short_summary": 0}
    decision_lines = [ln for ln in lines if ln.startswith("CW-BASETEMP-DECISION")
                      or ln.startswith("CW-BASETEMP-CLEANUP")]

    def file_slot(path: str) -> "OrderedDict[str, int]":
        if path not in per_file:
            per_file[path] = new_counts()
        return per_file[path]

    summary_section = False
    last_progress_file = None
    for ln in lines:
        # Windows pytest prints BACKSLASH paths (tests\contract\file.py) in progress and
        # verbose lines while the short summary uses forward slashes. Normalize the FIRST
        # whitespace-delimited token (the nodeid/file token) so every regex below sees one
        # canonical form; the remainder of the line (chars + [N%]) is untouched, and
        # byte-level reads elsewhere are unaffected.
        if ln.startswith("tests"):
            tok = ln.split(None, 1)[0]
            if "\\" in tok:
                rest = ln[len(tok):]
                ln = tok.replace("\\", "/") + rest
        m = RE_COLLECTED.match(ln)
        if m:
            collected_declared = int(m.group(1))
        if "short test summary info" in ln:
            summary_section = True
            continue
        if summary_section and ln.startswith("=") and "summary" not in ln:
            summary_section = False

        m = RE_VERBOSE.match(ln)
        if m:
            path, node, status = m.group(1), m.group(2), m.group(3)
            key = {
                "PASSED": "passed", "FAILED": "failed", "SKIPPED": "skipped",
                "ERROR": "error", "XFAIL": "xfailed", "XPASSED": "xpassed",
            }[status]
            slot = file_slot(path)
            # a node is counted once per terminal report line
            node_id = f"{path}::{node}"
            if node_status.get(node_id) is None:
                add(slot, key)
                node_status[node_id] = key
                method_votes["verbose"] += 1
                if key == "failed":
                    failed_nodeids.append(node_id)
                elif key == "error":
                    error_nodeids.append(node_id)
                elif key == "skipped":
                    skipped_nodeids.append(node_id)
            continue

        m = RE_PROGRESS.match(ln)
        if m and method_votes["verbose"] == 0:
            path, chars = m.group(1), m.group(2)
            last_progress_file = path
            slot = file_slot(path)
            for ch in chars:
                if ch in " %":
                    continue
                add(slot, CHARMAP.get(ch, "error"))
                method_votes["progress_chars"] += 1
            continue

        m = RE_CONTINUATION.match(ln)
        if m and method_votes["verbose"] == 0 and last_progress_file is not None:
            chars = m.group(1)
            slot = file_slot(last_progress_file)
            for ch in chars:
                add(slot, CHARMAP.get(ch, "error"))
                method_votes["progress_chars"] += 1
            continue

        if summary_section:
            m = RE_SHORT.match(ln)
            if m:
                kind, rest = m.group(1), m.group(2).strip()
                node_id = rest.split(" - ", 1)[0].strip()
                method_votes["short_summary"] += 1
                if kind == "FAILED":
                    if node_id not in failed_nodeids:
                        failed_nodeids.append(node_id)
                else:
                    if node_id not in error_nodeids:
                        error_nodeids.append(node_id)
                # attach to a file slot if the nodeid has a file part
                if node_id.startswith("tests/"):
                    path = node_id.split("::", 1)[0]
                    if path not in per_file:
                        file_slot(path)

    # If progress-char method was used, failing node ids come only from the short
    # summary / FAILURES headers; ensure every failed node has a file slot.
    for node_id in failed_nodeids + error_nodeids:
        if node_id.startswith("tests/"):
            file_slot(node_id.split("::", 1)[0])

    # ---- totals ----
    totals = new_counts()
    for counts in per_file.values():
        for k in STATUS_ORDER:
            add(totals, k, counts.get(k, 0))

    # ---- final summary line of the raw output (last line mentioning results) ----
    final_line = None
    for ln in reversed(lines):
        if ("passed" in ln or "failed" in ln or "error" in ln or "no tests ran" in ln) and re.search(r"=+\s*$", ln):
            final_line = ln
            break
        if final_line is None and ("passed in" in ln or "failed in" in ln or "error in" in ln):
            final_line = ln
    final_numbers: dict[str, int] = {}
    if final_line:
        for n, word in FINAL_NUM.findall(final_line):
            w = {"errors": "error", "warning": "warnings", "warnings": "warnings",
                 "xfail": "xfailed", "xpass": "xpassed"}.get(word, word)
            final_numbers[w] = final_numbers.get(w, 0) + int(n)

    # ---- lastfailed delta (cross-check) ----
    lastfailed_delta = None
    if pre_lf and post_lf and pre_lf.exists() and post_lf.exists():
        pre = set(json.loads(pre_lf.read_text("utf-8")))
        post = set(json.loads(post_lf.read_text("utf-8")))
        lastfailed_delta = {
            "new_failures_post_minus_pre": sorted(post - pre),
            "cleared_pre_minus_post": sorted(pre - post),
            "post_count": len(post),
            "pre_count": len(pre),
        }

    # ---- reconciliation vs raw summary line ----
    rec: dict[str, object] = {"ok": True, "problems": [], "informational": []}
    problems: list[str] = []
    informational: list[str] = []
    if collected_declared is not None:
        counted = sum(totals.values())
        if counted != collected_declared:
            problems.append(
                f"collected_declared={collected_declared} != sum(per-file counts)={counted}"
            )
    for key in ("passed", "failed", "skipped", "error"):
        if key in final_numbers and final_numbers[key] != totals.get(key, 0):
            # failed/error may be double-reported (progress chars + short summary)
            problems.append(
                f"final_summary[{key}]={final_numbers[key]} != per_file[{key}]={totals.get(key, 0)}"
            )
    if lastfailed_delta is not None:
        lf_set = set(failed_nodeids) | set(error_nodeids)
        new = set(lastfailed_delta["new_failures_post_minus_pre"])
        missing = sorted(new - lf_set)
        extra = sorted(lf_set - new)
        if missing:
            problems.append(f"lastfailed delta has failures not seen in raw parse: {missing[:20]}")
        if extra:
            informational.append(
                f"raw failures already present in the PRE-RUN baseline lastfailed (failed in "
                f"an older run too, i.e. pre-existing well before this card): {extra}"
            )
    rec = {"ok": not problems, "problems": problems, "informational": informational}

    per_root: dict[str, dict[str, int]] = {}
    for path, counts in per_file.items():
        parts = path.split("/")
        root = "/".join(parts[:2]) if len(parts) >= 3 else "other"
        slot = per_root.setdefault(root, {"files": 0, **{k: 0 for k in STATUS_ORDER}})
        slot["files"] += 1
        for k in STATUS_ORDER:
            slot[k] += counts.get(k, 0)

    out = {
        "raw": {
            "path": str(raw_path),
            "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "line_count": len(lines),
            "decisions_seen_in_stdout": decision_lines,
        },
        "collected_declared": collected_declared,
        "parse_method_votes": method_votes,
        "final_summary_line": final_line,
        "final_summary_numbers": final_numbers,
        "totals": totals,
        "totals_sum": sum(totals.values()),
        "per_root": per_root,
        "per_file": {p: dict(c) for p, c in per_file.items()},
        "files_seen": len(per_file),
        "failed_nodeids": failed_nodeids,
        "error_nodeids": error_nodeids,
        "skipped_nodeids": skipped_nodeids,
        "lastfailed_delta": lastfailed_delta,
        "reconciliation": rec,
    }
    Path(out_path).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({
        "files": out["files_seen"],
        "totals": totals,
        "per_root": per_root,
        "reconciliation": rec,
        "method_votes": method_votes,
    }, ensure_ascii=False, indent=1))
    return 0 if rec["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
