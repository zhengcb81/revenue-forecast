#!/usr/bin/env python3
"""check_domain_assertions.py — REM-79 mechanized (card REM79-MECHANIZATION).

Frozen contract: ../oracle.md (rule, lexicons, expectations) and
../oracle_table.json (machine expectation table).

RULE: a line that contains a universal-quantifier marker and contains NO
same-line domain qualifier is a violation.

Lexicon revision: oracle.md CORRECTION 1 (2026-09-22, append-only, prefix-proven)
added domain patterns D8/D9 and narrowed the EN marker boundaries at
alphanumeric/underscore adjacency (D10a). oracle.md CORRECTION 2 (same day, the
FINAL lexicon iteration — v2 freeze) added domain pattern D8b (count/noun
pairing incl. Chinese numerals), narrowed EN marker boundaries at hyphen
adjacency + code-call `all(`/`all[` (D10b), and added the quoted-line skip D11.
Sections 1-10 of the oracle and oracle_table.json expectations are unchanged.

CLI:
    python tools/check_domain_assertions.py [--json] FILE [FILE ...]

Exit codes: 0 = clean, 1 = violations found, 2 = usage/IO error.

Plan-scoped tooling, NOT product code. stdlib only, no network, never writes.
"""
import argparse
import json
import re
import sys

TOOL = "check_domain_assertions"
VERSION = "1.2.0-correction2"
RULE = "REM-79"

# --- universal-marker lexicon (oracle §3; D10a/D10b/D11 boundaries per CORRECTION 1+2)
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

# --- same-line domain patterns (§2 D1-D7 + CORRECTION 1 D8/D9 + CORRECTION 2 D8b)
D8 = (
    r"(?<!每)(?:[一二三四五六七八九十两几零]+(?:余|多)?|[≈约余近共]?\d+)\s*"
    r"(?:个|条|张|卡|项|次|行|类|族|组|种|点|位|批|份|轮|代|句|处|人|款|版|节|章|部分)"
)
D9 = (
    r"(?:剩余|新|旧|既定|原始|当前|本轮|本次|尚未|仍|待|均|上述|下列|该批|该项|此类)"
    r"[^。！？；\n]{0,14}(?:全部|没有|只有|无一|每一个|整个族|零代价)"
    r"|(?:全部|无一|只有)[^。！？；\n]{0,48}[A-Za-z]{1,4}[-_]?\d{1,4}"
    r"\s*[–\-—+、,，]\s*[A-Za-z]{0,4}[-_]?\d{1,4}"
)
D8B = (
    # b1: Chinese/Arabic numeral + CJK noun before the universal; gap excludes 的/过
    r"(?<![A-Za-z0-9_])(?:[一二三四五六七八九十廿卅]+(?:余|多)?|[≈约余近共]?\d+)\s*"
    r"[一-鿿]{1,4}[^。！？；\n的过]{0,6}(?:全部|没有|只有|无一|每一个|整个族|零代价)"
    # b1r: id-range (C1–C12) before the universal
    r"|[A-Za-z]{0,4}[-_]?\d{1,4}\s*[–\-—]\s*[A-Za-z]{0,4}[-_]?\d{1,4}"
    r"[^。！？；\n]{0,6}(?:全部|无一|只有)"
    # b2cjk: universal paired with a bounded NP (every/每一个 deliberately excluded)
    r"|(?:全部|没有|只有|无一)(?:\s*[一-鿿]{2,6}|\s+[`]?[A-Za-z][A-Za-z0-9_]{2,})"
    # b2en: `all` + capitalized proper-noun NP (ALL GREEN)
    r"|" + _B + r"all" + _E + r"\s+[A-Z][A-Za-z0-9_+.-]{2,}"
    # b3: conditional 只有…时
    r"|只有[^。！？；\n]{0,30}时(?:才|就|方|能|可)?"
)
DOMAIN_PATTERNS = [
    ("D1", r"域", 0),
    ("D2", r"domain\s*[:=]", re.IGNORECASE),
    ("D3", r"在[^。；;\n]{1,40}上", 0),
    ("D4", r"\d+\s*个", 0),
    (
        "D5",
        r"\d+\s*(?:cases?|rows?|probes?|characters|chars?|entries|lines?|files?"
        r"|cards|tests|runs?|trees|forms?|instances|samples|words?|tokens?"
        r"|bytes|sites|revisions?|rounds?)(?![A-Za-z])",
        re.IGNORECASE,
    ),
    ("D6", r"×\s*\d+|(?<![A-Za-z])N\s*=\s*\d+", 0),
    (
        "D7",
        r"（[^（）\n]{1,60}(?:、[^（）\n]{1,60}){2,}）"
        r"|(\([^()\n]{1,60}(?:,[^()\n]{1,60}){2,}\))",
        0,
    ),
    ("D8", D8, 0),
    ("D9", D9, 0),
    ("D8b", D8B, 0),
]

_MARKER_PATTERNS = (
    [(name, re.compile(name, re.IGNORECASE)) for name in CJK_MARKERS]
    + [(name, re.compile(pat, re.IGNORECASE)) for name, pat in EN_MARKERS]
)
_DOMAIN_COMPILED = [(pid, re.compile(pat, fl)) for pid, pat, fl in DOMAIN_PATTERNS]

MAX_EXCERPT = 160


def _quote_spans(line):
    """D11 quote spans: paired backticks, paired 「」, double quotes paired
    left-to-right with an unpaired opener extending to end-of-line."""
    spans = [ (m.start(), m.end()) for m in re.finditer(r"`[^`\n]*`", line) ]
    spans += [ (m.start(), m.end()) for m in re.finditer(r"「[^」\n]*」", line) ]
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


def find_markers(line):
    """D10b code-call + D11 quote/line-start suppressions applied to the lexicon."""
    if _line_is_quotation(line):
        return []
    spans = _quote_spans(line)
    hits = []
    for name, pat in _MARKER_PATTERNS:
        for m in pat.finditer(line):
            if any(s <= m.start() and m.end() <= e for s, e in spans):
                continue  # D11: marker inside a quoted span is not an occurrence
            if name == "all" and re.match(r"\s*[\[(]", line[m.end():]):
                continue  # D10b: code call all(...) / all[...]
            hits.append(name)
            break
    return hits


def find_domains(line):
    return [pid for pid, pat in _DOMAIN_COMPILED if pat.search(line)]


def excerpt(line):
    text = line.strip()
    if len(text) > MAX_EXCERPT:
        return text[: MAX_EXCERPT - 1] + "…"
    return text


def scan_file(path, domain_check=True):
    """Return (violations, error_message). violations: list of dicts."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            lines = fh.read().split("\n")
    except OSError as exc:
        return None, f"{path}: {exc}"
    if lines and lines[-1] == "":
        lines.pop()  # trailing newline artefact
    violations = []
    for idx, line in enumerate(lines, start=1):
        markers = find_markers(line)
        if not markers:
            continue
        if domain_check and find_domains(line):
            continue  # REM-79 satisfied: domain on the same line
        violations.append(
            {"line": idx, "markers": markers, "excerpt": excerpt(line)}
        )
    return violations, None


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="check_domain_assertions",
        description="REM-79: universal-quantifier claims must carry their domain "
        "on the same line.",
    )
    parser.add_argument("files", nargs="+", metavar="FILE")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of text")
    args = parser.parse_args(argv)

    report = {
        "tool": TOOL,
        "version": VERSION,
        "rule": RULE,
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
            print(f"{err}", file=sys.stderr)

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
                markers = ",".join(v["markers"])
                print(f"{entry['path']}:{v['line']}:[{markers}] {v['excerpt']}")
        if not io_error:
            print(
                f"{report['totals']['violations']} violation(s) across "
                f"{report['totals']['files']} file(s)"
            )

    if io_error:
        return 2
    return 1 if report["totals"]["violations"] else 0


if __name__ == "__main__":
    sys.exit(main())
