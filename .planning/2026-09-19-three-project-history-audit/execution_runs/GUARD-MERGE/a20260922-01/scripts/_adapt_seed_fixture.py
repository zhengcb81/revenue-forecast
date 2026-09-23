"""Bring the MIRROR's test_readiness_graph seed fixture up to the merged C7
contract (rule 1-2: missing state_domain => reject), byte-identical otherwise.

Conflict recorded by GUARD-MERGE battery (i) round 1: the seeded receipt in
tests/unit/test_readiness_graph.py carries no ``state_domain`` tag, so the
merged guard (FIX C7 face, oracle battery iii case N3 = missing => rejected)
evaluates it as ``absent`` and TTL's frozen expectation G2 (seeded receipt
with ttl==cap => safety_cache_state "hit") fails.

Resolution per oracle.md §5: the frozen expectation is NOT touched; the data
producer is brought up to the merged contract (one added receipt field).
"""
import difflib
import pathlib
import sys

src = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
old = '''                        "evidence_sha256": "e" * 64,
                        "source_sha256": S1,
                        "policy_hash": RULESET_HASH,'''
new = '''                        "evidence_sha256": "e" * 64,
                        "source_sha256": S1,
                        "policy_hash": RULESET_HASH,
                        # GUARD-MERGE fixture adaptation (C7, rule 1-2):
                        # receipts carry an explicit review-domain tag.
                        "state_domain": "review",'''
assert src.count(old) == 1, src.count(old)
out = src.replace(old, new)
pathlib.Path(sys.argv[2]).write_text(out, encoding="utf-8", newline="\n")
d = list(difflib.unified_diff(
    src.splitlines(True), out.splitlines(True),
    fromfile="company-wiki/tests/unit/test_readiness_graph.py (prod)",
    tofile="GUARD-MERGE mirror fixture (added state_domain receipt tag)",
    n=3))
pathlib.Path(sys.argv[3]).write_text("".join(d), encoding="utf-8", newline="\n")
print("seed fixture adapted; diff hunks:", sum(1 for l in d if l.startswith("@@")))
