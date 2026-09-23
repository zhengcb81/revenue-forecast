"""Build the two frozen mutants (oracle.md §2 mutation plan).

Usage: python make_mutants.py <iso_guard.py> <mutants_out_dir>

MUT-1 (m1): remove the CAP guard block this card adds (cap comparison +
            finite check); keep the pre-existing ``ttl_seconds < 0`` check
            and the past-now check.  Frozen: must redden N1/N2/N3/N9/N8/G1.
MUT-2 (m2): remove the ``now < reviewed_at`` clock-anomaly check; keep the
            cap guard.  Frozen: must redden N5/N6.

One guard flipped per mutant; each replacement must match exactly once.
"""
import hashlib
import sys
from pathlib import Path

iso_path = Path(sys.argv[1])
out_root = Path(sys.argv[2])
iso = iso_path.read_text(encoding="utf-8")

CAP_BLOCK = '''    if ttl_seconds > POLICY_RECEIPT_TTL_CAP_SECONDS:
        raise PromptInjectionGuardError(
            "ttl_seconds exceeds policy cap of 2592000s")
    if not math.isfinite(ttl_seconds):
        raise PromptInjectionGuardError("ttl_seconds must be a finite number")
'''

PAST_BLOCK = '''    if now_seconds < reviewed_at:
        # OPEN-6 C6: the caller's `now` may only TIGHTEN freshness.  A `now`
        # before reviewed_at makes the age negative (never > ttl_seconds),
        # which would let a rewound clock resurrect an expired receipt —
        # fail closed as a clock anomaly instead of reporting fresh.
        return ReviewEvaluation(
            status="not_reviewed", cache_state="tampered",
            reason="receipt reviewed_at is after now "
                   "(clock anomaly; now may only tighten freshness)",
        )
'''

assert iso.count(CAP_BLOCK) == 1, "CAP_BLOCK must match exactly once"
assert iso.count(PAST_BLOCK) == 1, "PAST_BLOCK must match exactly once"

mutants = {
    "m1": iso.replace(CAP_BLOCK, ""),
    "m2": iso.replace(PAST_BLOCK, ""),
}
report = {}
for name, content in mutants.items():
    d = out_root / name
    d.mkdir(parents=True, exist_ok=True)
    target = d / "prompt_injection_guard.py"
    target.write_text(content, encoding="utf-8")
    compile(content, str(target), "exec")  # syntactic sanity
    report[name] = hashlib.sha256(target.read_bytes()).hexdigest()
print(report)
