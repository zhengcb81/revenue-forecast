"""Parse a scheduler run log and print the failing checks (ASCII only).

Standalone helper: takes the log path and an output path, writes the failure
report to the output file and echoes a short summary.  Written as a file (not a
one-liner) because the console is GBK and the records are long.
"""

from __future__ import annotations

import json
import sys


def iter_records(text):
    marker = '{"case":'
    index = text.find(marker)
    while index != -1:
        depth = 0
        end = None
        for pos in range(index, len(text)):
            char = text[pos]
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    end = pos
                    break
        if end is None:
            return
        chunk = text[index:end + 1]
        try:
            yield json.loads(chunk)
        except ValueError:
            pass
        index = text.find(marker, end)


def read_log(path):
    """Read a scheduler log whatever encoding PowerShell's redirection used.

    ``Out-File`` writes UTF-16LE with a BOM, plain ``>`` writes UTF-16LE as well
    on Windows PowerShell, and cmd writes the ANSI/UTF-8 bytes straight through,
    so the encoding is detected instead of assumed.
    """
    with open(path, "rb") as handle:
        raw = handle.read()
    if raw.startswith(b"\xff\xfe"):
        return raw.decode("utf-16-le", errors="replace")
    if raw.startswith(b"\xfe\xff"):
        return raw.decode("utf-16-be", errors="replace")
    if raw.startswith(b"\xef\xbb\xbf"):
        return raw.decode("utf-8-sig", errors="replace")
    if raw.count(b"\x00") > len(raw) // 4:
        return raw.decode("utf-16-le", errors="replace")
    return raw.decode("utf-8", errors="replace")


def main(argv):
    log_path, out_path = argv[1], argv[2]
    text = read_log(log_path)
    lines = []
    seen = set()
    total_failures = 0
    for record in iter_records(text):
        case = record.get("case")
        if case in seen or "checks" not in record:
            continue
        seen.add(case)
        failures = [c for c in record.get("checks", []) if c.get("result") == "FAIL"]
        if not failures and not record.get("error"):
            lines.append(f"=== {case} PASS")
            continue
        total_failures += len(failures)
        lines.append(f"=== {case} {record.get('status')} ({len(failures)} failing checks)")
        for check in failures:
            lines.append(f"  FAIL: {check.get('check')}")
            lines.append(f"        {str(check.get('detail', ''))[:400]}")
        if record.get("error"):
            lines.append(f"  ERROR: {str(record['error'])[:400]}")
    with open(out_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")
    print(f"cases={len(seen)} failing_checks={total_failures} report={out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
