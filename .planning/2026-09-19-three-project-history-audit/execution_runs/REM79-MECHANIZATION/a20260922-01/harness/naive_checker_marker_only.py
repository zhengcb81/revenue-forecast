#!/usr/bin/env python3
"""naive_checker_marker_only.py — the DELIBERATELY-NAIVE RED arm.

Same CLI and output shape as tools/check_domain_assertions.py, but it only
detects universal markers and applies NO domain requirement. Per the frozen
oracle (oracle.md §7 / oracle_table.json red_arm_contract), this variant MUST
FAIL the frozen expectation table: it flags the 14 same-line-domain negative
payloads whose expected flag set is empty.

Run RED only; do not use for real scans.

Lexicon note: marker boundaries and quote/code suppressions follow oracle.md
CORRECTION 1 D10a + CORRECTION 2 D10b/D11 so both arms share one marker-occurrence
lexicon; this arm still applies NO domain logic, so the corrections' domain-side
changes (D8/D9/D8b) cannot affect what it reports.
"""
import argparse
import json
import re
import sys

TOOL = "naive_checker_marker_only"
VERSION = "1.0.2-red-correction2"
RULE = "REM-79"
VARIANT = "naive_marker_only"

CJK_MARKERS = ["只有", "全部", "没有", "整个族", "零代价", "无一", "每一个"]
_B = r"(?<![A-Za-z0-9_\-–—])"
_E = r"(?![A-Za-z0-9_\-–—])"
EN_MARKERS = [
    ("only", _B + r"only" + _E),
    ("all", _B + r"all" + _E),
    ("none", _B + r"none" + _E),
    ("every", _B + r"every" + _E),
    ("whole family", _B + r"whole family" + _E),
    ("zero cost", _B + r"zero cost" + _E),
]
_MARKER_PATTERNS = (
    [(name, re.compile(name, re.IGNORECASE)) for name in CJK_MARKERS]
    + [(name, re.compile(pat, re.IGNORECASE)) for name, pat in EN_MARKERS]
)
MAX_EXCERPT = 160


def excerpt(line):
    text = line.strip()
    return text[: MAX_EXCERPT - 1] + "…" if len(text) > MAX_EXCERPT else text


def _quote_spans(line):
    spans = [(m.start(), m.end()) for m in re.finditer(r"`[^`\n]*`", line)]
    spans += [(m.start(), m.end()) for m in re.finditer(r"「[^」\n]*」", line)]
    i = 0
    while True:
        start = line.find('"', i)
        if start < 0:
            break
        end = line.find('"', start + 1)
        if end < 0:
            spans.append((start, len(line)))
            break
        spans.append((start, end + 1))
        i = end + 1
    return spans


def _line_is_quotation(line):
    s = line.lstrip()
    return s.startswith('"') or s.startswith("「") or s.startswith(">") or s.startswith('*"')


def scan_file(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            lines = fh.read().split("\n")
    except OSError as exc:
        return None, f"{path}: {exc}"
    if lines and lines[-1] == "":
        lines.pop()
    violations = []
    for idx, line in enumerate(lines, start=1):
        if _line_is_quotation(line):
            continue
        spans = _quote_spans(line)
        markers = []
        for name, pat in _MARKER_PATTERNS:
            for m in pat.finditer(line):
                if any(s <= m.start() and m.end() <= e for s, e in spans):
                    continue
                if name == "all" and re.match(r"\s*[\[(]", line[m.end():]):
                    continue
                markers.append(name)
                break
        if markers:
            violations.append(
                {"line": idx, "markers": markers, "excerpt": excerpt(line)}
            )
    return violations, None


def main(argv=None):
    parser = argparse.ArgumentParser(prog=TOOL)
    parser.add_argument("files", nargs="+", metavar="FILE")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    report = {
        "tool": TOOL,
        "version": VERSION,
        "rule": RULE,
        "variant": VARIANT,
        "domain_check": False,
        "files": [],
        "totals": {"files": 0, "violations": 0},
    }
    io_error = False
    for path in args.files:
        violations, err = scan_file(path)
        if err is None:
            report["files"].append({"path": path, "violations": violations})
        else:
            io_error = True
            report["files"].append({"path": path, "error": err})
            print(err, file=sys.stderr)

    if not io_error:
        for entry in report["files"]:
            report["totals"]["violations"] += len(entry["violations"])
        report["totals"]["files"] = len(report["files"])

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for entry in report["files"]:
            if "error" in entry:
                continue
            for v in entry["violations"]:
                print(
                    f"{entry['path']}:{v['line']}:[{','.join(v['markers'])}] "
                    f"{v['excerpt']}"
                )
        if not io_error:
            print(
                f"{report['totals']['violations']} violation(s) across "
                f"{report['totals']['files']} file(s)  (variant: {VARIANT}, "
                f"domain_check=false)"
            )
    if io_error:
        return 2
    return 1 if report["totals"]["violations"] else 0


if __name__ == "__main__":
    sys.exit(main())
