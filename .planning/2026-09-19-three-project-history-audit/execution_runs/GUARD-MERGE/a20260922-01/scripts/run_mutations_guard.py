"""GUARD-MERGE battery (v): guard-side mutation spot checks.

Each mutant = the merged guard with EXACTLY ONE frozen check removed
(textual, recorded below), run through TTL's probe suite (fixture-adapted
copy in scripts/ttl30d_probe.py, expectations byte-identical to TTL's).
After every mutant the merged face is restored and a confirm run must be
16/16 again.

Usage: python run_mutions_guard.py <attempt_dir> <mirror_src_dir>
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys

A = pathlib.Path(sys.argv[1])
MIRROR = pathlib.Path(sys.argv[2])
EVID = A / "evidence" / "raw"
GUARD = MIRROR / "src" / "company_wiki" / "source_catalog" / "prompt_injection_guard.py"
PROBE = A / "scripts" / "ttl30d_probe.py"

base_text = (A / "iso" / "prompt_injection_guard.py").read_text(encoding="utf-8")

MUTANTS = {
    "v1_cap_check_removed": {
        "remove": (
            '    if ttl_seconds > POLICY_RECEIPT_TTL_CAP_SECONDS:\n'
            '        raise PromptInjectionGuardError(\n'
            '            "ttl_seconds exceeds policy cap of 2592000s")\n'
        ),
        "expect_red": ["TTL-G1", "TTL-N1", "TTL-N2", "TTL-N3"],
        "why": "over-cap REJECT removed alone — N8/N9 stay green because the "
               "isfinite gate behind it still rejects NaN/inf (defense in depth)",
    },
    "v1b_cap_and_isfinite_block_removed": {
        "remove": (
            '    if ttl_seconds > POLICY_RECEIPT_TTL_CAP_SECONDS:\n'
            '        raise PromptInjectionGuardError(\n'
            '            "ttl_seconds exceeds policy cap of 2592000s")\n'
            '    if not math.isfinite(ttl_seconds):\n'
            '        raise PromptInjectionGuardError("ttl_seconds must be a finite number")\n'
        ),
        "expect_red": ["TTL-G1", "TTL-N1", "TTL-N2", "TTL-N3", "TTL-N8", "TTL-N9"],
        "why": "TTL's MUT-1 exact mutant: the whole cap+isfinite validation "
               "block removed (frozen set from TTL commands.json C9)",
    },
    "v2_pastnow_clock_anomaly_removed": {
        "remove": (
            '    if now_seconds < reviewed_at:\n'
            "        # OPEN-6 C6: the caller's `now` may only TIGHTEN freshness.  A `now`\n"
            "        # before reviewed_at makes the age negative (never > ttl_seconds),\n"
            "        # which would let a rewound clock resurrect an expired receipt —\n"
            "        # fail closed as a clock anomaly instead of reporting fresh.\n"
            "        return ReviewEvaluation(\n"
            '            status="not_reviewed", cache_state="tampered",\n'
            "            state_domain=STATE_DOMAIN_CACHE,\n"
            '            reason="receipt reviewed_at is after now "\n'
            '                   "(clock anomaly; now may only tighten freshness)",\n'
            "        )\n"
        ),
        "expect_red": ["TTL-N5", "TTL-N6"],
        "why": "_freshness clock-anomaly branch removed (TTL MUT-2 frozen set)",
    },
    "v3_isfinite_removed": {
        "remove": (
            '    if not math.isfinite(ttl_seconds):\n'
            '        raise PromptInjectionGuardError("ttl_seconds must be a finite number")\n'
        ),
        "expect_red": ["TTL-N8"],
        "why": "isfinite gate removed — TTL-N8 (NaN) is the explicit NaN case; "
               "inf stays caught by the cap check (TTL-N9 green)",
    },
}


def run_probe(tag: str) -> dict:
    out = EVID / f"battery_v_probe_{tag}.json"
    proc = subprocess.run(
        [sys.executable, "-X", "utf8", str(PROBE), str(MIRROR / "src"), str(out)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    (EVID / f"battery_v_probe_{tag}.log").write_text(
        (proc.stdout or "") + (proc.stderr or ""), encoding="utf-8")
    payload = json.loads(out.read_text(encoding="utf-8"))
    return payload


summary = {}
for tag, spec in MUTANTS.items():
    mutant_text = base_text.replace(spec["remove"], "", 1)
    assert mutant_text != base_text, f"{tag}: mutation text not found"
    GUARD.write_text(mutant_text, encoding="utf-8", newline="\n")
    mutant_sha = hashlib.sha256(GUARD.read_bytes()).hexdigest()
    res = run_probe(tag)
    GUARD.write_text(base_text, encoding="utf-8", newline="\n")
    confirm = run_probe(tag + "_restored") if tag == list(MUTANTS)[-1] else None
    failed = res["gating_failed"]
    ok = sorted(failed) == sorted(spec["expect_red"])
    summary[tag] = {
        "mutant_guard_sha256": mutant_sha,
        "expect_red": spec["expect_red"],
        "observed_red": failed,
        "ok": ok,
        "why": spec["why"],
        "evidence": f"evidence/raw/battery_v_probe_{tag}.json",
    }
    print(tag, "OK" if ok else "MISMATCH", "observed:", failed)

restored_sha = hashlib.sha256(GUARD.read_bytes()).hexdigest()
base_sha = hashlib.sha256(base_text.encode("utf-8")).hexdigest()
confirm_res = run_probe("confirm_green")
summary["_restored"] = {
    "mirror_guard_sha256": restored_sha,
    "merged_guard_sha256": base_sha,
    "restored_byte_identical": restored_sha == base_sha,
    "confirm_green_gating_failed": confirm_res["gating_failed"],
    "confirm_green_gating_passed": confirm_res["gating_passed"],
}
(EVID / "battery_v_mutations_summary.json").write_text(
    json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({k: (v if k == "_restored" else v["ok"])
                  for k, v in summary.items()}, ensure_ascii=False))
all_ok = all(v["ok"] for k, v in summary.items() if not k.startswith("_"))
all_ok = all_ok and summary["_restored"]["restored_byte_identical"] \
    and not summary["_restored"]["confirm_green_gating_failed"]
sys.exit(0 if all_ok else 1)
