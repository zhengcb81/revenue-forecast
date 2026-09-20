"""Parse a scheduler run log into an honest per-case report.

Fixes the r2 F-I04C-04 defect: the v1 reader skipped any record without a
``checks`` key, which silently DROPPED harness-error records (a case that never
produced a result) and could report a failing case as PASS.  This version counts:

  * every case record, including ``{"case": ..., "error": ...}`` (harness error);
  * failing checks per case AND in total;
  * the SUMMARY line of the scheduler, for cross-checking.

Standalone: reads the log path, writes the report, prints a one-line summary with
the true counts.  Written as a file because the console is GBK and records are long.
"""

from __future__ import annotations

import json
import sys


def read_log(path):
    """Read a scheduler log whatever encoding PowerShell's redirection used."""
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


def iter_objects(text):
    """Yield every JSON object printed on its own line.

    The v1 reader searched for the literal ``{"case":`` and therefore MISSED every
    record whose first key sorted differently (``check()`` records start with
    ``{"A_lease_id"`` for F-L1) -- the second half of the F-I04C-04 defect.  The
    scheduler now writes one object per line without wrapping, so line-based
    parsing is exact; a balanced-brace fallback still handles a wrapped line.
    """
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("{"):
            continue
        try:
            obj = json.loads(stripped)
        except ValueError:
            obj = None
        if isinstance(obj, dict):
            yield obj
            continue
        # fallback: a record that got wrapped over several lines
        index = text.find(stripped)
        depth = 0
        for pos in range(index, len(text)):
            char = text[pos]
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    try:
                        yield json.loads(text[index:pos + 1])
                    except ValueError:
                        pass
                    break


def summary_line(text):
    marker = "=== SUMMARY ==="
    position = text.find(marker)
    if position == -1:
        return None
    for obj in iter_objects(text[position:]):
        if "cases" in obj:
            return obj
    return None


def main(argv):
    log_path, out_path = argv[1], argv[2]
    text = read_log(log_path)
    lines = []
    seen = set()
    cases_pass = 0
    cases_fail = 0
    cases_harness_error = 0
    failing_checks = 0
    for record in iter_objects(text):
        case = record.get("case")
        # The scheduler's SUMMARY rows are {"case","exit","seconds"} and carry no
        # result; only real case records have checks or an error.
        if case is None or ("checks" not in record and "error" not in record):
            continue
        if case in seen:
            continue
        seen.add(case)
        checks = record.get("checks") or []
        failures = [c for c in checks if c.get("result") == "FAIL"]
        error = record.get("error")
        if error and not checks:
            cases_harness_error += 1
            lines.append(f"=== {case} HARNESS-ERROR (no result produced)")
            lines.append(f"  ERROR: {str(error)[:400]}")
            continue
        if failures:
            cases_fail += 1
            failing_checks += len(failures)
            lines.append(f"=== {case} FAIL ({len(failures)} failing checks "
                         f"of {len(checks)})")
            for check in failures:
                lines.append(f"  FAIL: {check.get('check')}")
                lines.append(f"        {str(check.get('detail', ''))[:400]}")
        else:
            cases_pass += 1
            lines.append(f"=== {case} PASS ({len(checks)} checks)")
        if error:
            lines.append(f"  NOTE(error field): {str(error)[:200]}")
    scheduler_summary = summary_line(text)
    header = [
        f"# cases_in_log={len(seen)} pass={cases_pass} fail={cases_fail} "
        f"harness_error={cases_harness_error} failing_checks={failing_checks}",
    ]
    if scheduler_summary:
        header.append("# scheduler SUMMARY: " + json.dumps(
            {k: v for k, v in scheduler_summary.items() if k != "cases"},
            sort_keys=True))
        header.append("# scheduler per-case exits: " + json.dumps(
            {row["case"]: row["exit"] for row in scheduler_summary.get("cases", [])},
            sort_keys=True))
    with open(out_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(header + lines) + "\n")
    print(f"cases={len(seen)} pass={cases_pass} fail={cases_fail} "
          f"harness_error={cases_harness_error} failing_checks={failing_checks} "
          f"report={out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
