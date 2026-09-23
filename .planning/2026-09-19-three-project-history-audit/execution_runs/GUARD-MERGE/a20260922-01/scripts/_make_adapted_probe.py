"""Build the fixture-adapted copy of TTL's probe (GUARD-MERGE).

Rule 1-3 makes prompt_injection.py the FIX face (P5-a payload binding
mandatory), so TTL's fixture data producer (make_store) must carry an
evidence_payload.  Every frozen expectation (check(...) / observe(...)
call sites and literals) stays byte-identical to TTL's probe; this script
proves it by emitting a unified diff of the ONLY changed block.
"""
import difflib
import pathlib
import sys

src = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
old = '''        record_prompt_injection_review(
            con, doc, status="not_detected", reviewer="ttl30d-probe",
            evidence_sha256="e" * 64, now=reviewed_at,
            source_sha256=source, policy_hash=policy,
        )'''
new = '''        # GUARD-MERGE fixture adaptation ONLY (rule 1-3: prompt_injection.py =
        # FIX face, P5-a payload binding mandatory).  Every frozen expectation
        # (check(...) calls) is byte-identical to TTL's probe; only this data
        # producer is brought up to the merged receipt contract.
        _payload = ""  # clean text => scan_text => not_detected (matches status)
        record_prompt_injection_review(
            con, doc, status="not_detected", reviewer="ttl30d-probe",
            evidence_sha256=hashlib.sha256(_payload.encode("utf-8")).hexdigest(),
            now=reviewed_at,
            source_sha256=source, policy_hash=policy,
            evidence_payload=_payload,
        )'''
assert src.count(old) == 1, src.count(old)
out = src.replace(old, new)
pathlib.Path(sys.argv[2]).write_text(out, encoding="utf-8", newline="\n")
d = list(difflib.unified_diff(
    src.splitlines(True), out.splitlines(True),
    fromfile="TTL-30D-POLICY/a20260922-01/scripts/ttl30d_probe.py",
    tofile="GUARD-MERGE/a20260922-01/scripts/ttl30d_probe.py (fixture adaptation)",
    n=3))
pathlib.Path(sys.argv[3]).write_text("".join(d), encoding="utf-8", newline="\n")
# prove no frozen expectation line changed
old_checks = [l for l in src.splitlines() if l.startswith("check(")]
new_checks = [l for l in out.splitlines() if l.startswith("check(")]
assert old_checks == new_checks, "frozen check() expectations changed!"
print("adapted probe written; diff hunks:",
      sum(1 for l in d if l.startswith("@@")),
      "| check() lines identical:", len(old_checks))
