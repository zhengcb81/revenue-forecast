# -*- coding: utf-8 -*-
"""I-13-BC mutation runner: red arms on _mut/Mx copies; originals must stay byte-identical."""
import hashlib
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PLAN = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
FILES = ["oracle.md", "reviewer_answers.json", "final_scorecard.json", "verification.json", "handoff.json"]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(65536), b""):
            h.update(c)
    return h.hexdigest()


def snapshot():
    return {f: (os.path.getsize(os.path.join(HERE, f)), sha(os.path.join(HERE, f))) for f in FILES}


def load(root, name):
    with open(os.path.join(root, name), encoding="utf-8") as f:
        return json.load(f)


def save(root, name, obj):
    with open(os.path.join(root, name), "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def run_verify(root):
    r = subprocess.run([sys.executable, "-B", os.path.join(HERE, "_verify_i13bc.py"),
                        "--root", root, "--plan", PLAN], capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()


def main():
    before = snapshot()
    arms = {}

    def arm(mid, mutate):
        d = os.path.join(HERE, "_mut", mid)
        if os.path.isdir(d):
            shutil.rmtree(d)
        os.makedirs(d)
        for f in FILES:
            shutil.copy2(os.path.join(HERE, f), os.path.join(d, f))
        mutate(d)
        rc, out = run_verify(d)
        with open(os.path.join(d, "verifier_output.txt"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write("rc=%d\n%s\n" % (rc, out))
        arms[mid] = {"rc": rc, "violations": [ln for ln in out.splitlines() if ": " in ln][:8]}
        print("%s rc=%d" % (mid, rc))
        for ln in out.splitlines():
            print("   " + ln)

    # GREEN (originals)
    rc, out = run_verify(HERE)
    arms["GREEN"] = {"rc": rc, "violations": []}
    print("GREEN rc=%d" % rc)
    print("   " + out.replace("\n", "\n   "))

    def m1(d):  # one column PASS masks another: formula-side pass over disclosure not_granted
        fs = load(d, "final_scorecard.json")
        for r in fs["per_model_columns"]["rows"]:
            if r["model_id"] == "MS-PBP-M05":
                r["disclosure"]["status"] = "granted"
                r["row_status"] = "pass"
        save(d, "final_scorecard.json", fs)

    def m2(d):  # accuracy rewritten as verified
        fs = load(d, "final_scorecard.json")
        for r in fs["per_model_columns"]["rows"]:
            if r["model_id"] == "ZJ-SMT-M09":
                r["accuracy"]["status"] = "verified"
                r["accuracy"]["detail"] = "已验证预测"
        save(d, "final_scorecard.json", fs)

    def m3(d):  # classification escalation to ready
        fs = load(d, "final_scorecard.json")
        fs["classification"] = "buy_side_review_ready"
        fs["qualification_statuses"]["deployment_usable"]["status"] = True
        save(d, "final_scorecard.json", fs)

    def m4(d):  # red-line consumption / params released
        ho = load(d, "handoff.json")
        ho["params_released"] = True
        ho["redline_note"] = "consumed_for_forecast for path building"
        save(d, "handoff.json", ho)

    def m5(d):  # fabricated consensus numbers + contribution shares
        ra = load(d, "reviewer_answers.json")
        ra["action3_expectation_comparison"]["consensus_numbers"] = [1234.5]
        ra["five_questions"][2]["numeric_contribution_shares"] = [40, 35, 25]
        ra["action2_verification"]["driver_contributions"]["numeric_contribution_shares"] = [40, 35, 25]
        save(d, "reviewer_answers.json", ra)

    def m6(d):  # scenario band as probability + production/sales swap
        ra = load(d, "reviewer_answers.json")
        ra["accounting_distinctions"]["scenario_is_probability"] = True
        ra["accounting_distinctions"]["probability_claims_count"] = 1
        ra["accounting_distinctions"]["production_vs_sales"]["never_mixed"] = False
        save(d, "reviewer_answers.json", ra)

    arm("M1_one_column_masking", m1)
    arm("M2_accuracy_overclaim", m2)
    arm("M3_ready_escalation", m3)
    arm("M4_redline_consumption", m4)
    arm("M5_fabricated_numbers", m5)
    arm("M6_scenario_as_probability", m6)

    # GREEN after mutations (originals untouched?)
    after = snapshot()
    untouched = before == after
    rc2, out2 = run_verify(HERE)
    arms["GREEN_AFTER_MUTATIONS"] = {"rc": rc2, "violations": []}
    print("GREEN_AFTER_MUTATIONS rc=%d" % rc2)
    print("   " + out2.replace("\n", "\n   "))
    print("originals_untouched=%s" % untouched)

    with open(os.path.join(HERE, "_mut", "mutation_summary.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"arms": arms, "originals_untouched": untouched, "before": before, "after": after},
                  f, ensure_ascii=False, indent=2)
        f.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
