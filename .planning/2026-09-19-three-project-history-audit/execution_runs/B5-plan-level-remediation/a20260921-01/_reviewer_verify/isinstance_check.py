"""Reviewer check: is any isinstance() used to compare `expected`?  And rc-map check."""
import json
import os
import re

ATTEMPT = (r"C:\Users\郑曾波\Projects\revenue-forecast\.planning"
           r"\2026-09-19-three-project-history-audit\execution_runs"
           r"\B5-plan-level-remediation\a20260921-01")
BATCHES = ["M05-M08", "M09-M12", "M13-M16", "M21-M24", "M25-M28", "M29-M31"]

for batch in BATCHES:
    new = os.path.join(ATTEMPT, batch, "run_card.py")
    txt = open(new, encoding="utf-8").read()
    lines = txt.splitlines()
    print("=" * 78)
    print(batch)
    print("-- lines containing both isinstance and 'expected'/'declared' --")
    hits = [(i, ln.strip()) for i, ln in enumerate(lines, 1)
            if "isinstance" in ln and re.search(r"expected|declared", ln)]
    for i, ln in hits:
        print("  %-5d %s" % (i, ln[:150]))
    if not hits:
        print("  (none)")
    print("-- enforcement sites --")
    for i, ln in enumerate(lines, 1):
        if re.search(r"raised_name|declared_ok|declared_usable|NOT_JUDGED_declaration_unusable|"
                     r"FAIL_declared_expectation_mismatch", ln):
            print("  %-5d %s" % (i, ln.strip()[:150]))
