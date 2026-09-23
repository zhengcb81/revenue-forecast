"""FIX-W06-GAPS mutation checks — one mutation per fix family (oracle APPEND C).

Each mutation copies the FIXED sources to a temp dir, applies ONE recorded
textual mutation, re-runs the family's green checks against the mutated copy
and records the observed verdict.  Expected: RED (the mutation must break the
family's green checks — proof the pins/scenarios are not vacuous).

Usage: python -X utf8 -B run_mutations.py [--only FAMILY]
Raw outputs -> evidence/MUTATION_<family>.txt
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATTEMPT = HERE.parent
ISO = ATTEMPT / "iso"
EVIDENCE = ATTEMPT / "evidence"
TMP = Path(os.environ["TEMP"]) / "fix-w06-gaps" / "mutations"
PY = sys.executable

LOG: list[str] = []
RESULTS: dict = {}


def log(line: str = "") -> None:
    LOG.append(line)
    print(line)


def run(cmd: list[str], env: dict | None = None) -> str:
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", env=dict(os.environ, **(env or {})))
    return (proc.stdout or "") + (proc.stderr or "")


def mutate_tree(src: Path, dst: Path, replacements: list[tuple[str, str]]) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    for rel, (old, new) in replacements:
        path = dst / rel
        text = path.read_text(encoding="utf-8")
        if old not in text:
            raise SystemExit(f"mutation anchor missing in {rel}: {old[:60]!r}")
        path.write_text(text.replace(old, new, 1), encoding="utf-8")


def verdict_store(family: str, module: Path, scripts: dict[str, str]) -> dict:
    out_dir = TMP / family
    out_dir.mkdir(parents=True, exist_ok=True)
    outputs = {}
    for name, script in scripts.items():
        out = out_dir / f"{name}.txt"
        text = run([PY, "-X", "utf8", "-B", str(HERE / script),
                    "--module", str(module), "--out", str(out)])
        outputs[name] = text.strip().splitlines()[-12:]
    overall = all(
        any("SCENARIOS: PASS" in line for line in lines)
        for lines in outputs.values()
    )
    return {"mutated": str(module), "observed": outputs,
            "verdict": "RED (mutation broke the green checks)" if not overall
            else "GREEN (!!! mutation did not break the checks)"}


def verdict_pkg(family: str, pkg: Path, script: str) -> dict:
    out_dir = TMP / family
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "run.txt"
    text = run([PY, "-X", "utf8", "-B", str(HERE / script),
                "--pkg-dir", str(pkg), "--out", str(out)])
    overall = "SCENARIOS: PASS" in text
    return {"mutated": str(pkg), "observed": text.strip().splitlines()[-12:],
            "verdict": "GREEN (!!! mutation did not break the checks)" if overall
            else "RED (mutation broke the green checks)"}


def verdict_pytest(family: str, test_file: Path, env: dict) -> dict:
    text = run([PY, "-X", "utf8", "-B", "-m", "pytest", str(test_file),
                "-q", "--no-header", "-p", "no:cacheprovider"], env=env)
    tail = text.strip().splitlines()[-8:]
    ok = any(" passed" in line and " failed" not in line for line in tail)
    return {"env": env, "observed": tail,
            "verdict": "GREEN (!!! mutation did not break the pins)" if ok
            else "RED (mutation broke the pins)"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None)
    args = ap.parse_args()
    if TMP.exists():
        shutil.rmtree(TMP)
    TMP.mkdir(parents=True)
    store_fixed = ISO / "candidate"
    pkg_fixed = ISO / "pi_pkg"

    families: list[tuple[str, callable]] = []

    def family(name: str, fn):
        if args.only is None or args.only == name:
            families.append((name, fn))

    # P1: drop one ADD COLUMN spec ------------------------------------------
    def m_p1():
        mutate_tree(store_fixed, TMP / "p1_cand", [
            ("processing_demand_store.py",
             ('    ("lease_owner", "TEXT"),\n', "    # mutation: lease_owner spec removed\n")),
        ])
        return verdict_store("P1", TMP / "p1_cand" / "processing_demand_store.py",
                             {"s_p1_migration.py": "s_p1_migration.py"})
    family("P1", m_p1)

    # P2-B: claim empty-pool refusal returns None ---------------------------
    def m_p2():
        mutate_tree(store_fixed, TMP / "p2_cand", [
            ("processing_demand_store.py",
             ('raise DemandStateError("no ready demand to claim")',
              'return None')),
        ])
        return verdict_store("P2B", TMP / "p2_cand" / "processing_demand_store.py",
                             {"s_p2_claim_refusal.py": "s_p2_claim_refusal.py"})
    family("P2B", m_p2)

    # P3: post-expiry refusal text changed ----------------------------------
    def m_p3():
        mutate_tree(store_fixed, TMP / "p3_cand", [
            ("processing_demand_store.py",
             ('                    if expired_running is not None:\n'
              '                        raise DemandStateError("lease expired")\n',
              '                    if expired_running is not None:\n'
              '                        raise DemandStateError("lease stale")\n')),
        ])
        return verdict_store("P3", TMP / "p3_cand" / "processing_demand_store.py",
                             {"s_p3_lease_expiry.py": "s_p3_lease_expiry.py"})
    family("P3", m_p3)

    # P4 face 1: one byte of a pinned candidate message ---------------------
    def m_p4a():
        mutate_tree(store_fixed, TMP / "p4a_cand", [
            ("processing_demand_store.py",
             ('raise DemandStateError("no ready demand to claim")',
              'raise DemandStateError("no ready demand to clam")')),
        ])
        return verdict_pytest(
            "P4a", ISO / "candidate" / "test_candidate_message_pins.py",
            {"GAPS_PIN_CANDIDATE": str(TMP / "p4a_cand")})
    family("P4a", m_p4a)

    # P4 face 2: one byte of the product block sentence (copy) --------------
    def m_p4b():
        d = TMP / "p4b_rf"
        d.mkdir(parents=True)
        for name in ("source_preparation.py", "processing_demand.py"):
            shutil.copy2(ISO.parent / "before" / "rf" / name, d / name)
        text = (d / "source_preparation.py").read_text(encoding="utf-8")
        anchor = "prompt injection not reviewed — source preparation blocked"
        assert anchor in text
        (d / "source_preparation.py").write_text(
            text.replace(anchor, "prompt injection not reviewed — source preparation blokced", 1),
            encoding="utf-8")
        return verdict_pytest(
            "P4b", ISO / "rf" / "test_message_contract_pins.py",
            {"GAPS_PIN_RF_SCRIPTS": str(d)})
    family("P4b", m_p4b)

    # P5-a: payload binding removed ------------------------------------------
    def m_p5a():
        mutate_tree(pkg_fixed, TMP / "p5a_pkg", [
            ("prompt_injection.py",
             ("if hashlib.sha256(payload_bytes).hexdigest() != evidence_sha256:",
              "if False:")),
        ])
        return verdict_pkg("P5a", TMP / "p5a_pkg", "s_p5_receipt.py")
    family("P5a", m_p5a)

    # P5-b: disposal gate removed -------------------------------------------
    def m_p5b():
        mutate_tree(pkg_fixed, TMP / "p5b_pkg", [
            ("prompt_injection.py",
             ('    if status == "detected_and_ignored":\n'
              '        disposal_fields = _disposal_gate(',
              '    if False:\n'
              '        disposal_fields = _disposal_gate(')),
        ])
        return verdict_pkg("P5b", TMP / "p5b_pkg", "s_p5_receipt.py")
    family("P5b", m_p5b)

    # P5-c: dual binding made optional --------------------------------------
    def m_p5c():
        mutate_tree(pkg_fixed, TMP / "p5c_pkg", [
            ("prompt_injection.py",
             ('_require_sha256(source_sha256, "source_sha256")',
              '_require_sha256(source_sha256, "source_sha256", optional=True)')),
        ])
        return verdict_pkg("P5c", TMP / "p5c_pkg", "s_p5_receipt.py")
    family("P5c", m_p5c)

    # P6-A: CAS predicate removed -------------------------------------------
    def m_p6a():
        mutate_tree(pkg_fixed, TMP / "p6a_pkg", [
            ("prompt_injection.py",
             ('"UPDATE documents SET metadata_json=? WHERE document_id=? "\n'
              '                    "AND metadata_json=?",',
              '"UPDATE documents SET metadata_json=? WHERE document_id=? "\n'
              '                    "AND metadata_json=? OR 1=1",')),
        ])
        return verdict_pkg("P6A", TMP / "p6a_pkg", "s_p6_concurrent.py")
    family("P6A", m_p6a)

    # P6-B: sqlite wrap removed ---------------------------------------------
    def m_p6b():
        mutate_tree(pkg_fixed, TMP / "p6b_pkg", [
            ("prompt_injection.py",
             ("except sqlite3.Error as exc:  # P6-B: never a bare sqlite3.* escape",
              "except ValueError as exc:  # mutation: wrap removed")),
        ])
        return verdict_pkg("P6B", TMP / "p6b_pkg", "s_p6_concurrent.py")
    family("P6B", m_p6b)

    # C7: state_domain check removed ----------------------------------------
    def m_c7():
        mutate_tree(pkg_fixed, TMP / "c7_pkg", [
            ("prompt_injection_guard.py",
             ('        # C7 fail-closed: no valid domain tag => ambiguous => never trusted.\n'
              '        if receipt.get("state_domain") != STATE_DOMAIN_REVIEW:\n'
              '            return None\n',
              '        # mutation: state_domain check removed\n')),
        ])
        return verdict_pkg("C7", TMP / "c7_pkg", "s_c7_state_domain.py")
    family("C7", m_c7)

    # P7: one identity field dropped ----------------------------------------
    def m_p7():
        mutate_tree(store_fixed, TMP / "p7_cand", [
            ("processing_demand_store.py",
             ('"as_of_date": request.get("as_of_date"),',
              '"as_of_date": None,')),
        ])
        return verdict_store("P7", TMP / "p7_cand" / "processing_demand_store.py",
                             {"s_p7_key.py": "s_p7_key.py"})
    family("P7", m_p7)

    for name, fn in families:
        log(f"=== mutation {name} ===")
        LOG.append("")
        result = fn()
        RESULTS[name] = result
        log(f"    {result['verdict']}")
        observed = result.get("observed", {})
        if isinstance(observed, dict):
            for key, lines in observed.items():
                log(f"    [{key}]")
                for line in lines:
                    log(f"    | {line}")
        else:
            for line in observed:
                log(f"    | {line}")
        EVIDENCE.mkdir(parents=True, exist_ok=True)
        (EVIDENCE / f"MUTATION_{name}.txt").write_text(
            "\n".join(LOG) + "\n", encoding="utf-8")
        LOG.clear()

    log("=== MUTATION SUMMARY ===")
    log(json.dumps({k: v["verdict"] for k, v in RESULTS.items()},
                   ensure_ascii=False, indent=2))
    (EVIDENCE / "MUTATION_summary.txt").write_text(
        json.dumps({k: v["verdict"] for k, v in RESULTS.items()},
                   ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
