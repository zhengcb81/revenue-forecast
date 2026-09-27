#!/usr/bin/env python3
"""_run_mutations.py — I-11-C/a20260926-01 red/green mutation runner.

Mutates COPIES in _mut/ only; verifies original bytes unchanged after each run.
Runs verify_mapping.py as a subprocess and records rc + first violation line each.
"""
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EAS_DEFAULT = HERE.parents[1] / "I-11-B" / "a20260926-01" / "expert_assumptions.json"
MUT = HERE / "_mut"
MUT.mkdir(exist_ok=True)

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def run(args):
    r = subprocess.run([sys.executable, str(HERE / "verify_mapping.py"), *[str(a) for a in args]],
                       capture_output=True, text=True, encoding="utf-8")
    return r.returncode, (r.stdout or "").strip().splitlines(), (r.stderr or "").strip().splitlines()[:2]

mapping = HERE / "parameter_mapping.json"
handoff = HERE / "handoff.json"
results = []

# ---- green ----
m0, h0, e0 = sha(mapping), sha(handoff), sha(EAS_DEFAULT)
rc, out, _ = run([mapping, handoff, EAS_DEFAULT])
results.append({"id": "GREEN", "mutation": "原件（mapping+handoff+I-11-B EA+store）", "rc": rc,
                "expected_rc": 0, "expected": "ALL_INVARIANTS_OK", "observed": out[0] if out else "",
                "pass": rc == 0 and out and "ALL_INVARIANTS_OK" in out[0]})

def mutate(name, which, fn):
    src = {"mapping": mapping, "handoff": handoff, "eas": EAS_DEFAULT}[which]
    dst = MUT / f"{name}.json"
    shutil.copyfile(src, dst)
    data = json.loads(dst.read_text(encoding="utf-8-sig"))
    fn(data)
    dst.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    args = {"mapping": dst if which == "mapping" else mapping,
            "handoff": dst if which == "handoff" else handoff,
            "eas": dst if which == "eas" else EAS_DEFAULT}
    rc, out, _ = run([args["mapping"], args["handoff"], args["eas"]])
    viol = next((l for l in out if l.startswith("VIOLATION")), (out[0] if out else ""))
    return dst, rc, viol

def m1(d): d["mapping_rows"][0]["value_state"] = "released"
def m2(d): d["mapping_rows"][0]["new_value"]["base"] = 281520
def m3(d): d["params_released"] = True
def m4(d):
    for a in d["assumptions"]:
        if a["id"] == "EA-1":
            a.pop("sensitivity_interval", None)
def m5(d): d["c3_c5_residuals"][0]["registration"] = "resolved"

for name, which, fn, expect_key, red_id in [
    ("m1_released", "mapping", m1, "J1", "M1"),
    ("m2_synthetic", "mapping", m2, "J2", "M2"),
    ("m3_params_released", "handoff", m3, "J1", "M3"),
    ("m4_ea_missing_interval", "eas", m4, "J2", "M4"),
    ("m5_residual_resolved", "handoff", m5, "J4", "M5"),
]:
    dst, rc, viol = mutate(name, which, fn)
    ok = rc == 1 and expect_key in viol
    results.append({"id": red_id, "mutation": dst.name, "rc": rc, "expected_rc": 1,
                    "expected": f"rc=1 且违例含 {expect_key}", "observed": viol, "pass": ok})

# originals untouched?
untouched = {
    "parameter_mapping.json": sha(mapping) == m0,
    "handoff.json": sha(handoff) == h0,
    "expert_assumptions.json(I-11-B)": sha(EAS_DEFAULT) == e0,
}
print(json.dumps({"results": results, "originals_untouched": untouched}, ensure_ascii=False, indent=2))
sys.exit(0 if all(r["pass"] for r in results) and all(untouched.values()) else 1)
