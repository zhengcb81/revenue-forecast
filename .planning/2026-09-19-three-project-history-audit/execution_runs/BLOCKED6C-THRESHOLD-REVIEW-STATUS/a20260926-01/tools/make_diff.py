"""BLOCKED6C changes.diff generator (oracle.md section 8 / exit criterion 6).

Produces one per-file disclosed unified diff between the SEALED pre-image
(iso/ copy of execution_runs/I-11-A/a20260919-01/tools/validate_hypotheses.py,
byte-identical to the sealed original) and this attempt's patched copy
(iso_patched/...). Read-only with respect to every source: it only reads the two
copies and writes <run>/changes.diff.

Usage:
  python -X utf8 -B tools/make_diff.py --out <changes.diff>
"""
from __future__ import annotations

import argparse
import datetime
import difflib
import hashlib
import os
import sys

RUN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# RUN = <planning>/execution_runs/BLOCKED6C-.../a20260926-01  => three levels up
PLANNING = os.path.abspath(os.path.join(RUN, os.pardir, os.pardir, os.pardir))
SEALED = os.path.join(PLANNING, "execution_runs", "I-11-A", "a20260919-01",
                      "tools", "validate_hypotheses.py")
ISO = os.path.join(RUN, "iso", "tools", "validate_hypotheses.py")
PATCHED = os.path.join(RUN, "iso_patched", "tools", "validate_hypotheses.py")


def sha_bytes(path):
    raw = open(path, "rb").read()
    return hashlib.sha256(raw).hexdigest(), len(raw)


def rel(path):
    return os.path.relpath(path, PLANNING).replace("\\", "/")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    s_sha, s_len = sha_bytes(SEALED)
    i_sha, i_len = sha_bytes(ISO)
    p_sha, p_len = sha_bytes(PATCHED)
    if s_sha != i_sha or s_len != i_len:
        raise SystemExit("iso/ pre-image is NOT byte-identical to the sealed original")

    pre = open(ISO, "r", encoding="utf-8", newline="").read().splitlines(keepends=True)
    post = open(PATCHED, "r", encoding="utf-8", newline="").read().splitlines(keepends=True)
    body = list(difflib.unified_diff(
        pre, post,
        fromfile="a/" + rel(SEALED),
        tofile="b/" + rel(PATCHED),
        n=3,
    ))
    if not body:
        raise SystemExit("empty diff")

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    head = "\n".join([
        "changes.diff — BLOCKED6C-THRESHOLD-REVIEW-STATUS (a20260926-01)",
        "generated_at_local: %s" % now,
        "role: I-11-A implementer-side / orchestration schema-side executor "
        "(handoff.implementer_signed=false); diff only, never applied to the repository",
        "sealed (unchanged): %s" % rel(SEALED),
        "  sha256=%s bytes=%d" % (s_sha, s_len),
        "pre-image (this attempt iso/ copy, byte-identical to the sealed original): %s"
        % rel(ISO),
        "  sha256=%s bytes=%d" % (i_sha, i_len),
        "post-image (this attempt iso_patched/ copy ONLY): %s" % rel(PATCHED),
        "  sha256=%s bytes=%d" % (p_sha, p_len),
        "touched paths: 1 file — tools/validate_hypotheses.py (inside this attempt's "
        "iso_patched/ only); hypotheses.json is NOT in this diff (append-only schema, "
        "oracle.md 3.1: the default exists precisely so history need not be rewritten)",
        "product repos (dayu-agent / company-wiki / revenue-forecast outside .planning): "
        "NOT touched (0 files); src/ : 0 files; scripts/ : 0 files",
        "guards added: B6C-SCHEMA / B6C-HELPERS / B6C-G1 / B6C-G2 / B6C-G3 / B6C-G4, "
        "each inside marker-delimited blocks so a mutation can delete exactly one",
        "pre-existing predicates are untouched: FALSIFIER_KEYS, THRESHOLD_BASES, the "
        "E_THRESHOLD_BASIS_UNKNOWN closed set and R2's five checks keep their original "
        "bytes (verified by mutant M3, which deletes that closed set on purpose)",
        "error codes added (oracle.md 3.2): E_THRESHOLD_REVIEW_STATUS_UNKNOWN, "
        "E_THRESHOLD_REVIEW_STATUS_UNSEALED, E_THRESHOLD_REVIEW_STATUS_NOT_REVIEWED "
        "(DEC-14 item 5: registered in this card's oracle 3.2, the sealed I-11-A oracle "
        "is NOT rewritten)",
        "evidence: red/baseline_run.log + red/baseline_validation_report.json "
        "(positive pass, 21/21 rejected, rc=0), red/ce_run.log + red/ce22_ce25_report.json "
        "(CE-22..CE-25 4/4 ACCEPTED by the pre-patch validator, rc=1), "
        "green/cases_run.log + green/cases_report.json + green/validation_report.json "
        "(positive 0 errors, 4/4 new CE rejected, 25/25 suite, rc=0), "
        "mut/M1..M5/cases_report.json (5/5 mutants red), l271/l271_report.json "
        "(L271_trigger_fired=false, literal A-6.1 reading=true)",
        "---",
    ]) + "\n"
    out = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(head)
        fh.write("".join(body).replace("\r\n", "\n"))
    raw = open(out, "rb").read()
    print("changes.diff bytes=%d sha256=%s" % (len(raw), hashlib.sha256(raw).hexdigest()))
    print("lines=%d" % raw.decode("utf-8").count("\n"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
