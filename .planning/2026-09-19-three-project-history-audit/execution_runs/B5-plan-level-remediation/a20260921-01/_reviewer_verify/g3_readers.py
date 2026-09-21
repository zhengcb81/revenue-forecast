"""Reviewer check for G3: who, on disk, READS expectation_consistency.facts.declared_expectations?

Read-only scan of the M13-M16 historical trees (all four cards) for reader code: any
.json path / dict-key reference to the renamed key.
"""
import json
import os
import re

PLAN = (r"C:\Users\郑曾波\Projects\revenue-forecast\.planning"
        r"\2026-09-19-three-project-history-audit")
CARDS = ["M13", "M14", "M15", "M16"]
PAT = re.compile(r"declared_expectations")
hits = []
for card in CARDS:
    base = os.path.join(PLAN, "execution_runs", card)
    for root, dirs, files in os.walk(base):
        for fn in files:
            p = os.path.join(root, fn)
            if not fn.endswith((".py", ".ps1", ".json", ".md", ".txt")):
                continue
            try:
                t = open(p, encoding="utf-8", errors="replace").read()
            except Exception:
                continue
            for m in PAT.finditer(t):
                seg = t[max(0, m.start() - 90):m.end() + 60].replace("\n", " ")
                hits.append({"file": os.path.relpath(p, PLAN), "snippet": seg})

# classify: is it a READ of the old key in facts, or just a printed/derived label?
readers = [h for h in hits if re.search(r'facts\[|facts\.get|\["declared_expectations"\]|'
                                        r"\['declared_expectations'\]|\"declared_expectations\"\]",
                                        h["snippet"])]
print("total occurrences: %d" % len(hits))
print("occurrences that look like a READ of the key: %d" % len(readers))
for h in readers[:20]:
    print("  %s\n     ...%s..." % (h["file"], h["snippet"][:160]))
print("\n--- non-reader occurrences (first 12) ---")
for h in [x for x in hits if x not in readers][:12]:
    print("  %s\n     ...%s..." % (h["file"], h["snippet"][:160]))
