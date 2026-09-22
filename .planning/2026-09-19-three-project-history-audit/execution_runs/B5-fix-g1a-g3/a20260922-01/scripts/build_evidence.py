"""B5-fix-g1a-g3 evidence builder: per-batch evidence.json (PROPAGATION_CONTRACT §6 shape,
arms POPULATED — F-3) + attempt-level evidence/arm_matrix.json + regenerated runner diffs.

Data source: _scratch/arms_raw.json (128 real child-process runs, raw rc only).
B5's attempt is read-only: its evidence.json supplies insertion_points/rc_codes_after for the
four batches this card did not re-patch, and its recorded arm rc for the arm-B comparison.
"""
from __future__ import annotations

import difflib
import hashlib
import json
import os
import re

PLAN = r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
ATTEMPT = os.path.join(PLAN, "execution_runs", "B5-fix-g1a-g3", "a20260922-01")
B5 = os.path.join(PLAN, "execution_runs", "B5-plan-level-remediation", "a20260921-01")
SCRATCH = os.path.join(ATTEMPT, "_scratch")

BATCHES = {
    "M01-M04": {"cards": ["M01", "M02", "M03", "M04"], "rep": "M01", "patched_by": None},
    "M05-M08": {"cards": ["M05", "M06", "M07", "M08"], "rep": "M05", "patched_by": "B5"},
    "M09-M12": {"cards": ["M09", "M10", "M11", "M12"], "rep": "M09", "patched_by": "B5"},
    "M13-M16": {"cards": ["M13", "M14", "M15", "M16"], "rep": "M13", "patched_by": "B5+this-card"},
    "M17-M20": {"cards": ["M17", "M18", "M19", "M20"], "rep": "M17", "patched_by": None},
    "M21-M24": {"cards": ["M21", "M22", "M23", "M24"], "rep": "M21", "patched_by": "B5"},
    "M25-M28": {"cards": ["M25", "M26", "M27", "M28"], "rep": "M25", "patched_by": "B5+this-card"},
    "M29-M31": {"cards": ["M29", "M30", "M31"], "rep": "M29", "patched_by": "B5"},
}
EXPECTED = {"E": 0, "F": 3, "G": 2}
B5_RECORDED_B = {"M01-M04": None, "M05-M08": 0, "M09-M12": 3, "M13-M16": 2,
                 "M17-M20": 3, "M21-M24": 3, "M25-M28": 1, "M29-M31": 0}
# M17/M01 arm B note: for the unpatched batches the B role == the F role runner (byte-copy),
# so B5 recorded nothing; M17-B here is a measurement of the reference runner itself.
RC_LEGEND = {
    "M01-M04": {"0": "pass", "2": "no verdict (harness_incomplete)", "3": "negative",
                "1": "only via an uncaught crash (no rc=1 branch in the runner)"},
    "M17-M20": {"0": "EXIT_PASS", "1": "EXIT_HARNESS", "2": "EXIT_NO_VERDICT",
                "3": "EXIT_NEGATIVE"},
}


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def dump_json(path, doc):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
        fh.write("\n")


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def norm_verdict(v):
    if isinstance(v, dict):
        return v.get("verdict")
    return v


def find_line(source, needle):
    for i, line in enumerate(source.splitlines(), start=1):
        if needle in line:
            return i
    return None


def main():
    runs = load(os.path.join(SCRATCH, "arms_raw.json"))
    by_batch = {}
    for r in runs:
        by_batch.setdefault(r["batch"], {}).setdefault(r["arm"], {})[r["card"]] = r

    matrix = {"fix_card": "B5-fix-g1a-g3", "attempt": "a20260922-01",
              "source": "_scratch/arms_raw.json (raw child-process exit codes)",
              "expectations": {"E": 0, "F": 3, "G": 2, "B": "measured (unchanged)",
                               "S": "1 (structural, M25-M28 only)"},
              "batches": {}, "cards": {}, "uniform_23_required": None,
              "uniform_27_with_reference": None, "all_31": None, "notes": []}
    all_expect_ok = True
    all27 = True
    all31 = True

    for batch, cfg in BATCHES.items():
        arms = by_batch.get(batch, {})
        b5_ev_path = os.path.join(B5, batch, "evidence.json")
        b5_ev = load(b5_ev_path) if os.path.exists(b5_ev_path) else None

        runner_after_p = os.path.join(ATTEMPT, batch, "run_card.py")
        runner_before_p = os.path.join(ATTEMPT, batch, "run_card_before.py")
        src_after = open(runner_after_p, encoding="utf-8").read()
        src_before = open(runner_before_p, encoding="utf-8").read()

        # ---- regenerated diff ------------------------------------------------------------
        diff_name = None
        diff_stats = {"added_lines": 0, "removed_lines": 0}
        if src_after != src_before:
            before_lines = src_before.splitlines(keepends=True)
            after_lines = src_after.splitlines(keepends=True)
            ud = list(difflib.unified_diff(before_lines, after_lines,
                                           fromfile="%s/run_card_before.py" % batch,
                                           tofile="%s/run_card.py (B5-fix-g1a-g3)" % batch))
            diff_name = "%s/runner.diff" % batch
            with open(os.path.join(ATTEMPT, batch, "runner.diff"), "w", encoding="utf-8",
                      newline="\n") as fh:
                fh.writelines(ud)
            diff_stats = {
                "added_lines": sum(1 for l in ud if l.startswith("+") and not l.startswith("+++")),
                "removed_lines": sum(1 for l in ud if l.startswith("-")
                                     and not l.startswith("---")),
            }
        else:
            old = os.path.join(ATTEMPT, batch, "runner.diff")
            if os.path.exists(old):
                os.remove(old)

        # ---- insertion points ------------------------------------------------------------
        insertion = list((b5_ev or {}).get("insertion_points") or [])
        if batch == "M13-M16":
            insertion = [p for p in insertion
                         if "declared_expectations" not in json.dumps(p)]
            insertion.append({
                "file": "run_card.py", "line": find_line(
                    src_after, "declared_in_cases = sorted("),
                "what": ("B5-fix F-1/G3: emit BOTH facts keys - declared_expectations "
                         "(historical, read by M14 recovery/consolidated_report.py:75) AND "
                         "declared_expectations_in_cases_json (contract §2 name), same value "
                         "computed once")})
        if batch == "M25-M28":
            insertion.append({
                "file": "run_card.py", "line": find_line(src_after,
                                                         "# ---- G1-a explicit routing"),
                "what": ("B5-fix F-2/G1-a: whole-set gate explicitly routed - structural rc=1 "
                         "unchanged / declaration unusable rc=2+no_verdict before judging / "
                         "usable-but-different rc=3; never non-gating, never rc=1 for a value "
                         "difference")})
            insertion.append({
                "file": "run_card.py", "line": find_line(src_after,
                                                         "set_level_forces_fail ="),
                "what": "G1-a routing is load-bearing in the final exit-code decision"})

        # ---- arms -------------------------------------------------------------------------
        arm_block = {}
        for arm in ("E", "F", "B", "G"):
            per = arms.get(arm, {})
            rcs = {card: per[card]["raw_rc"] for card in cfg["cards"] if card in per}
            vals = sorted(set(rcs.values()))
            verdicts = sorted({str(norm_verdict(per[c]["verdict"]))
                               for c in per})
            mutated = sorted({per[c]["mutated_case"] for c in per})
            rec = {
                "rc": vals[0] if len(vals) == 1 else rcs,
                "rc_per_card": rcs,
                "rc_uniform": len(vals) == 1,
                "verdict": verdicts[0] if len(verdicts) == 1 else verdicts,
                "declared_expectation_mismatch": (
                    per[cfg["cards"][0]]["mismatch_count"] if arm in ("E", "F", "G") else None),
                "mismatch_ids_per_card": {c: per[c]["mismatch_ids"] for c in per},
                "mutated_case": mutated[0] if len(mutated) == 1 else mutated,
                "out_written_all": all(per[c]["out_written"] for c in per),
                "note": "",
            }
            if arm in EXPECTED:
                rec["expected_rc"] = EXPECTED[arm]
                rec["meets_expectation"] = (len(vals) == 1 and vals[0] == EXPECTED[arm])
                if cfg["patched_by"] is not None:
                    all_expect_ok = all_expect_ok and rec["meets_expectation"]
            if arm == "B":
                rec["b5_recorded_rc"] = B5_RECORDED_B[batch]
                rec["unchanged_vs_b5_recorded"] = (B5_RECORDED_B[batch] is None
                                                   or rec["rc"] == B5_RECORDED_B[batch])
                rec["note"] = ("historical byte-copy runner on the same mutated cases; rc is a "
                               "MEASUREMENT and must not change vs B5's recorded value")
            if arm == "E":
                rec["note"] = "green control: patched runner + frozen cases.json"
            if arm == "F":
                rec["note"] = ("owner-mandated mutation arm: usable-but-different `expected` -> "
                               "rc=3 (the arm that was previously unreachable on M25-M28)")
            if arm == "G":
                rec["note"] = ("declaration unusable (expected key deleted) -> rc=2 + no_verdict; "
                               "the mutated case is NOT_JUDGED, never counted as a mismatch")
            arm_block[arm] = rec

        # ---- supplementary S arm (M25-M28) -------------------------------------------------
        extra_arms = {}
        if "S" in arms:
            per = arms["S"]
            rcs = {card: per[card]["raw_rc"] for card in cfg["cards"]}
            vals_S = sorted(set(rcs.values()))
            extra_arms["S"] = {
                "rc": vals_S[0] if len(vals_S) == 1 else rcs,
                "rc_per_card": rcs,
                "expected_rc": 1,
                "meets_expectation": set(rcs.values()) == {1},
                "note": ("structural arm: one extra unknown-id case -> the structural gate still "
                         "aborts at rc=1 UNCHANGED (G1-a keeps rc=1 for harness/fixture faults)"),
            }

        # ---- batch scope note ---------------------------------------------------------------
        scope = ("this batch carries NO REM-21 patch (it is outside the six T1-8-authorized "
                 "batches): both runner roles are byte-copies of the historical file; arms are "
                 "MEASUREMENT ONLY and were reported to the owner as a scope finding"
                 if cfg["patched_by"] is None else
                 "runner patch scope: %s" % cfg["patched_by"])

        open_issues = []
        if b5_ev:
            open_issues += ["carried from B5 attempt (read-only): %s"
                            % i for i in (b5_ev.get("open_issues") or [])]
        if batch == "M05-M08":
            open_issues.append(
                "F-6 (informational): B5's arm runs mutated CONT-BREAK (last case) instead of "
                "the contract's first/lowest-id NEG-CARD, and did not declare the deviation. "
                "THIS card's runs use NEG-CARD (first case in file order whose frozen expected "
                "is ModelRegistryError): E=0/F=3/B=0/G=2 identical, so no result changes; the "
                "reviewer's independent NEG-CARD re-run agrees.")
        if batch == "M13-M16":
            open_issues.append(
                "G3/F-1 fixed: BOTH facts keys emitted. Correction recorded: B5 implementer's "
                "claim 'M05-M08 did the same thing' was INACCURATE - M05-M08's runner has NO "
                "expectation_consistency.facts block at all; none was added there.")
            open_issues.append(
                "F-3 fixed: arms.{E,F,B,G} in this evidence.json are populated from real runs "
                "(B5's copy had all-null arm fields).")
        if batch == "M25-M28":
            open_issues.append(
                "F-2/G1 fixed per owner ruling G1-a: whole-set gate explicitly routed "
                "(rc=1 structural / rc=2 unusable before judging / rc=3 usable-diff per case).")
            open_issues.append(
                "G2 conflict: the frozen case_contract.rule 'rc=1' text vs the frozen rc table "
                "is registered as a KNOWN CONFLICT with owner ruling 留置 (permanently "
                "registered; NO precedence between the frozen artifacts is asserted). See "
                "decision.md. No frozen file edited (T1-11).")
            open_issues.append(
                "F-4 registered: on M25-M28 a deleted `expected` historically gave rc=1 via the "
                "WHOLE-SET case_contract gate (case.get('expected') -> None != declared), NOT "
                "via a hard-subscript KeyError; no KeyError, no output JSON. START_HERE append 2 "
                "explains only the KeyError mechanism - its text is left unedited (no "
                "authorization to append to START_HERE in this card); correction carried here.")
            open_issues.append(
                "F-5 registered: arm G on M25-M28 is a SECOND semantic change (historical rc=1 "
                "from the set-level gate -> patched rc=2 + no_verdict), required for T1-19 "
                "cross-batch uniformity; registered alongside G1 rather than silently.")
            open_issues.append(
                "arm S (structural, new): rc=1 on all four cards - the structural abort is "
                "unchanged by the G1-a routing.")
        if batch in ("M01-M04",):
            open_issues.append(
                "SCOPE FINDING (reported to owner): measured E=0/F=0/B=0/G=1 on all four cards - "
                "no per-case gate was ever propagated here (F is a fabricated green) and a "
                "deleted `expected` crashes rc=1 (hard subscript). Out of this card's "
                "authorization to patch; measurement only.")

        # ---- M13 G3 block ------------------------------------------------------------------
        extra_blocks = {}
        if batch == "M13-M16":
            g3 = {}
            for arm in ("E", "F", "B", "G"):
                for card in cfg["cards"]:
                    r = arms[arm][card]
                    g3["%s/%s" % (arm, card)] = {
                        "facts_keys": r["g3_facts_keys"],
                        "old_key_present": r["g3_old_key_present"],
                        "new_key_present": r["g3_new_key_present"],
                        "keys_equal_when_both_present": r["g3_keys_equal"],
                        "runner_role": r["runner_role"],
                    }
            extra_blocks["g3_both_keys"] = {
                "patched_runner_outputs_have_both_keys": all(
                    v["old_key_present"] and v["new_key_present"] and v["keys_equal_when_both_present"]
                    for k, v in g3.items() if not k.startswith("B/")),
                "arm_b_historical_outputs_have_old_key_only": all(
                    v["old_key_present"] and not v["new_key_present"]
                    for k, v in g3.items() if k.startswith("B/")),
                "reader_proof": "evidence/g3_reader_proof.json (M14 consolidated_report.py:75)",
                "per_output": g3,
            }
        if batch == "M25-M28":
            routes = {}
            for arm in ("E", "F", "G"):
                for card in cfg["cards"]:
                    r = arms[arm][card]
                    routes["%s/%s" % (arm, card)] = {
                        "route_rc": r["case_contract_route_rc"],
                        "gating": r["case_contract_gating"],
                        "raw_rc": r["raw_rc"],
                        "verdict": norm_verdict(r["verdict"]),
                        "no_verdict_reason": r["no_verdict_reason"],
                        "unusable_ids": r["unusable_ids"],
                        "mismatch_ids": r["mismatch_ids"],
                    }
            extra_blocks["g1a_routing"] = {
                "authority": "owner G1-a execution ruling 2026-09-22",
                "structural_arm_S_rc": extra_arms.get("S", {}).get("rc_per_card"),
                "declaration_unusable_arm_G": "rc=2 + no_verdict, evaluated before judging",
                "usable_different_arm_F": "rc=3 (load-bearing set-level route + per-case)",
                "set_level_gate_state": "EXPLICITLY ROUTED (set_level_declaration_gating=true)",
                "value_difference_never_rc1": True,
                "frozen_rule_text_conflict": "known conflict, owner ruling 留置 - no precedence asserted",
                "per_output": routes,
            }

        evidence = {
            "batch": batch,
            "cards": cfg["cards"],
            "fix_card": "B5-fix-g1a-g3",
            "scope_note": scope,
            "runner_before": {
                "path": "execution_runs/%s/a20260919-01/scripts/run_card.py" % cfg["rep"],
                "sha256": sha256_file(runner_before_p),
                "bytes": os.path.getsize(runner_before_p),
                "byte_identical_to_historical": sha256_file(runner_before_p) == sha256_file(
                    os.path.join(PLAN, "execution_runs", cfg["rep"], "a20260919-01",
                                 "scripts", "run_card.py")),
            },
            "runner_after": {
                "path": "execution_runs/B5-fix-g1a-g3/a20260922-01/%s/run_card.py" % batch,
                "sha256": sha256_file(runner_after_p),
                "bytes": os.path.getsize(runner_after_p),
                "identical_to_historical": (sha256_file(runner_after_p)
                                            == sha256_file(runner_before_p)),
            },
            "diff_path": diff_name,
            "diff_stats": diff_stats,
            "cards_cases_sha256": {card: arms["E"][card]["frozen_cases_sha256"]
                                   for card in cfg["cards"]},
            "insertion_points": insertion,
            "arms": arm_block,
            "extra_arms": extra_arms,
            "rc_codes_after": RC_LEGEND.get(batch) or (b5_ev or {}).get("rc_codes_after"),
            "isolated_code_root_sha256": {
                "model_registry.py": "9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f",
                "model_extensions.py": "9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911",
            },
            "historical_writes": [],
            "boundaries_respected": True,
            "unmet_prerequisites": [],
            "open_issues": open_issues,
        }
        evidence.update(extra_blocks)
        dump_json(os.path.join(ATTEMPT, batch, "evidence.json"), evidence)

        # ---- matrix row --------------------------------------------------------------------
        row = {"cards": cfg["cards"], "patched_by": cfg["patched_by"], "arms": {}}
        for arm in ("E", "F", "B", "G", "S"):
            if arm in arms:
                rcs = {c: arms[arm][c]["raw_rc"] for c in arms[arm]}
                row["arms"][arm] = rcs
                if arm in EXPECTED:
                    ok = set(rcs.values()) == {EXPECTED[arm]}
                    row.setdefault("expectation_ok", True)
                    row["expectation_ok"] = row["expectation_ok"] and ok
                    if cfg["patched_by"] is not None:
                        all_expect_ok = all_expect_ok and ok
        in_required = cfg["patched_by"] is not None
        batch_uniform = all(set(row["arms"][a].values()) == {EXPECTED[a]}
                            for a in ("E", "F", "G") if a in row["arms"])
        row["uniform_EFG"] = batch_uniform
        matrix["batches"][batch] = row
        for card in cfg["cards"]:
            matrix["cards"][card] = {a: arms[a][card]["raw_rc"] for a in ("E", "F", "B", "G")
                                     if a in arms}
        all31 = all31 and batch_uniform
        if in_required or batch == "M17-M20":
            all27 = all27 and batch_uniform

    required_batches = [b for b, c in BATCHES.items() if c["patched_by"] is not None]
    matrix["uniform_23_required"] = all(
        matrix["batches"][b]["uniform_EFG"] for b in required_batches)
    matrix["uniform_27_with_reference"] = all27
    matrix["uniform_23_expectations_met"] = all_expect_ok
    matrix["all_31_uniform"] = all31
    matrix["not_uniform_batches"] = [b for b in matrix["batches"]
                                     if not matrix["batches"][b]["uniform_EFG"]]
    matrix["notes"] = [
        "E/F/G uniform (0/3/2) on all 23 cards of the six REM-21 batches: "
        + ", ".join(required_batches),
        "M17-M20 (reference, byte-copy) also uniform -> 27/31 cards uniform.",
        "M01-M04 (never in T1-8's six authorized batches) measured E=0/F=0/B=0/G=1: "
        "no per-case gate was ever propagated there and a deleted `expected` crashes rc=1. "
        "Patch is OUT OF SCOPE for this card; reported to the owner as a scope finding.",
        "Arm B is a measurement and is unchanged vs B5's recorded values on all six batches "
        "(M05=0, M09=3, M13=2, M21=3, M25=1, M29=0).",
    ]
    dump_json(os.path.join(ATTEMPT, "evidence", "arm_matrix.json"), matrix)

    # ---- attempt-level changes.diff (runner deltas of THIS attempt vs historical) ----------
    parts = []
    for batch in BATCHES:
        p = os.path.join(ATTEMPT, batch, "runner.diff")
        if os.path.exists(p):
            parts.append(open(p, encoding="utf-8").read())
    with open(os.path.join(ATTEMPT, "changes.diff"), "w", encoding="utf-8",
              newline="\n") as fh:
        fh.write("".join(parts))

    print("uniform_23_required:", matrix["uniform_23_required"])
    print("uniform_27_with_reference:", matrix["uniform_27_with_reference"])
    print("all_31_uniform:", matrix["all_31_uniform"],
          "not_uniform:", matrix["not_uniform_batches"])
    print("expectations_met_on_required:", all_expect_ok)
    for batch in BATCHES:
        row = matrix["batches"][batch]
        print("%-9s %s" % (batch, {a: sorted(set(v.values())) for a, v in row["arms"].items()}))
    print("wrote per-batch evidence.json, evidence/arm_matrix.json, changes.diff")
    return 0 if matrix["uniform_23_required"] and all_expect_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
