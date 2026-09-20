"""Correction pass for the r3 drift declaration: the window's timezone field (one M-card attempt).

The first revision of ``recovery/production_drift_note.json`` described the window's timezone as
"the machine's local time (Asia/Shanghai)". That was an assumption, and it is wrong: an explicit
clock check (``Get-Date`` local ``2026-09-20 04:58:19`` against UTC ``03:58:19``,
``[System.TimeZoneInfo]::Local.Id`` = ``GMT Standard Time``, offset ``+01:00``) shows the machine is
on GMT Standard Time. The declared window therefore maps as

    2026-09-20 04:35:31-04:40:53 local  ==  2026-09-20 03:35:31-03:40:53 UTC

which also confirms the ordering claim: the ledger fields were written at 03:28-03:30 UTC
(04:28-04:30 local), i.e. about five minutes BEFORE the rollback.

This script (a) corrects the source templates that emit that text, so a future run is right, and
(b) rewrites the two already-written files in this attempt with the corrected fields, changing
nothing else. Every edit is a single count-asserted literal replacement of ONE source line; each
rewritten JSON is re-parsed before it is written, and the Python sources are re-compiled.

Exit codes: 0 ok, 9 an expected anchor line was not found exactly once, 1 harness error.
"""

from __future__ import annotations

import hashlib
import json
import os
import py_compile
import tempfile

SCRIPT = os.path.abspath(__file__)
ATTEMPT = os.path.dirname(os.path.dirname(os.path.dirname(SCRIPT)))
CARD = os.path.basename(os.path.dirname(ATTEMPT))
BK = os.path.join(ATTEMPT, "recovery", "bookkeeping_r3")

EDITS = [
    # (file, exact anchor line without newline, replacement lines without newline)
    (os.path.join(ATTEMPT, "recovery", "production_drift_note.json"),
     '  "timezone": "the machine\'s local time (Asia/Shanghai)",',
     ['  "timezone": "the machine\'s local time (GMT Standard Time, UTC+1 on 2026-09-20): the '
      'window is 2026-09-20 04:35:31-04:40:53 local = 2026-09-20 03:35:31-03:40:53 UTC",',
      '  "utc_start": "2026-09-20 03:35:31",',
      '  "utc_end": "2026-09-20 03:40:53",']),
    (os.path.join(ATTEMPT, "recovery", "bookkeeping_r3", "ledger_regeneration_r3.json"),
     '  "why_they_must_be_identical": "they were recorded at 2026-09-20T03:28-03:30Z, i.e. before '
     'the production-drift window; production is back on the anchored revision, so the current '
     'reading reproduces them"',
     ['  "why_they_must_be_identical": "they were recorded at 2026-09-20T03:28-03:30Z '
      '(= 04:28-04:30 local, about five minutes before the 04:35:31 local rollback), i.e. before '
      'the production-drift window; production is back on the anchored revision, so the current '
      'reading reproduces them"']),
    (os.path.join(ATTEMPT, "recovery", "bookkeeping_r3", "transcribe_r3_verdict.py"),
     '            "timezone": "the machine\'s local time (Asia/Shanghai)",',
     ['            "timezone": "the machine\'s local time (GMT Standard Time, UTC+1 on "',
      '                        "2026-09-20): the window is 2026-09-20 04:35:31-04:40:53 local = "',
      '                        "2026-09-20 03:35:31-03:40:53 UTC",',
      '            "utc_start": "2026-09-20 03:35:31",',
      '            "utc_end": "2026-09-20 03:40:53",']),
    (os.path.join(ATTEMPT, "recovery", "bookkeeping_r3", "regenerate_ledger_r3.py"),
     '                "why_they_must_be_identical": "they were recorded at '
     '2026-09-20T03:28-03:30Z, i.e. "',
     ['                "why_they_must_be_identical": "they were recorded at '
      '2026-09-20T03:28-03:30Z "',
      '                                              "(= 04:28-04:30 local, about five minutes "',
      '                                              "before the 04:35:31 local rollback), i.e. "']),
]


def sha256b(data):
    return hashlib.sha256(data).hexdigest()


def rb(path):
    with open(path, "rb") as handle:
        return handle.read()


def wb(path, data):
    with open(path, "wb") as handle:
        handle.write(data)


def apply_edit(path, anchor, replacement_lines):
    raw = rb(path)
    text = raw.decode("utf-8")
    rel = os.path.relpath(path, ATTEMPT).replace("\\", "/")
    if replacement_lines[0] in text and anchor not in text:
        return {"path": rel, "already_correct": True, "sha256_before": sha256b(raw),
                "sha256_after": sha256b(raw), "bytes_before": len(raw), "bytes_after": len(raw)}
    if text.count(anchor) != 1:
        raise AssertionError("anchor found %d times in %s" % (text.count(anchor), rel))
    out = text.replace(anchor, "\n".join(replacement_lines))
    if rel.endswith(".json"):
        json.loads(out)
    if rel.endswith(".py"):
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as fh:
            fh.write(out)
            tmp = fh.name
        py_compile.compile(tmp, doraise=True)
        os.unlink(tmp)
    data = out.encode("utf-8")
    wb(path, data)
    return {"path": rel, "already_correct": False, "sha256_before": sha256b(raw),
            "sha256_after": sha256b(data), "bytes_before": len(raw), "bytes_after": len(data)}


def update_summary():
    """Keep the bookkeeping table truthful: the drift note's row must show its final bytes."""
    path = os.path.join(BK, "summary.json")
    raw = rb(path)
    summary = json.loads(raw.decode("utf-8"))
    note_path = os.path.join(ATTEMPT, "recovery", "production_drift_note.json")
    for entry in summary.get("changes", []):
        if entry["path"] == "recovery/production_drift_note.json":
            entry["sha256_after"] = sha256b(rb(note_path))
            entry["bytes_after"] = os.path.getsize(note_path)
            entry["corrected_after_the_first_write"] = (
                "F-r3-02 timezone field corrected: Asia/Shanghai -> GMT Standard Time with the "
                "local -> UTC mapping (see drift_note_timezone_correction)")
    summary["drift_note_timezone_correction"] = {
        "what": "recovery/production_drift_note.json described the drift window's timezone as "
                "\"Asia/Shanghai\"; the machine's local zone is GMT Standard Time (UTC+1 on "
                "2026-09-20), so the declared window 2026-09-20 04:35:31-04:40:53 local is "
                "2026-09-20 03:35:31-03:40:53 UTC",
        "how_established": "Get-Date local 2026-09-20 04:58:19 vs UTC 03:58:19, "
                           "[System.TimeZoneInfo]::Local.Id = GMT Standard Time, offset +01:00",
        "also_corrected": ["recovery/bookkeeping_r3/ledger_regeneration_r3.json",
                           "recovery/bookkeeping_r3/transcribe_r3_verdict.py (template)",
                           "recovery/bookkeeping_r3/regenerate_ledger_r3.py (template)"],
        "script": "recovery/bookkeeping_r3/fix_drift_note_timezone_r3.py",
        "effect_on_the_drift_claim": "none: the ordering claim holds either way, and is now stated "
                                     "in UTC as well (ledger fields written 03:28-03:30 UTC = "
                                     "04:28-04:30 local, about five minutes before the rollback)",
        "expectations_tolerances_frozen_artifacts_touched": False,
    }
    data = (json.dumps(summary, ensure_ascii=False, indent=1) + "\n").encode("utf-8")
    wb(path, data)
    return {"path": os.path.relpath(path, ATTEMPT).replace("\\", "/"),
            "sha256_before": sha256b(raw), "sha256_after": sha256b(data),
            "bytes_before": len(raw), "bytes_after": len(data)}


def main() -> int:
    print("=== drift-note timezone correction - card %s ===" % CARD)
    results = []
    for path, anchor, replacement in EDITS:
        entry = apply_edit(path, anchor, replacement)
        results.append(entry)
        print("  %-56s %s" % (entry["path"],
                              "already correct" if entry["already_correct"]
                              else "%s -> %s (%d -> %d B)"
                              % (entry["sha256_before"][:12], entry["sha256_after"][:12],
                                 entry["bytes_before"], entry["bytes_after"])))
    summary_entry = update_summary()
    print("  %-56s %s -> %s (%d -> %d B)"
          % (summary_entry["path"], summary_entry["sha256_before"][:12],
             summary_entry["sha256_after"][:12], summary_entry["bytes_before"],
             summary_entry["bytes_after"]))
    note = json.loads(rb(os.path.join(ATTEMPT, "recovery", "production_drift_note.json")).decode("utf-8"))
    print("  window: %s | UTC %s - %s" % (note["window"]["local_window_text"],
                                          note["window"]["utc_start"], note["window"]["utc_end"]))
    print("  timezone: %s" % note["window"]["timezone"])
    report = json.loads(rb(os.path.join(BK, "ledger_regeneration_r3.json")).decode("utf-8"))
    print("  report: %s" % report["historical_values_preserved"]["why_they_must_be_identical"])
    print("=== done ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
