#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""I-12-D action 0: deterministic metric_numeric_oracle + negative cases.

Reads the FROZEN fixture verbatim from execution_v2/research_cards.json
(metric_numeric_oracle, sha 4a22e266…) and independently computes every metric with
exact rational arithmetic, then compares against the frozen expected values.

Writes:
  evidence/I-12-D/metric_oracle_result.json
  evidence/I-12-D/metric_negative_results.json

No network, no git, no actual values, no parameter release.
"""
import hashlib
import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
PLAN_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
EV = os.path.join(HERE, "evidence", "I-12-D")
CARDS = os.path.join(PLAN_ROOT, "execution_v2", "research_cards.json")
CARDS_SHA = "4a22e26608d421799e2b8adde0d0424fa48a634509a0559c51d279e06d918263"
TOL = Fraction(1, 10) ** 12


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def frac_out(fr):
    return {
        "defined": True,
        "numerator": fr.numerator,
        "denominator": fr.denominator,
        "string": "%d/%d" % (fr.numerator, fr.denominator),
        "decimal": float(fr),
    }


def undef(reason):
    return {"defined": False, "reason": reason, "value": None}


def score(sample_ids, actual, forecast, baseline, low, high, forecast_sample_ids=None,
          declared_nominal_coverage=None):
    """Frozen metric set. Zero denominators => undefined (never epsilon).
    sample_id misalignment => rejection (positional scoring forbidden)."""
    if forecast_sample_ids is not None and list(forecast_sample_ids) != list(sample_ids):
        return {
            "status": "rejected",
            "reason": "sample_id_misalignment",
            "detail": "forecast_sample_ids != sample_ids; positional scoring refused; "
                      "an explicit alignment table must be saved and checked "
                      "(origin/horizon/model) before any scoring",
            "expected_sample_ids": list(sample_ids),
            "received_sample_ids": list(forecast_sample_ids),
        }
    n = len(actual)
    signed = [forecast[i] - actual[i] for i in range(n)]
    aerr = [abs(x) for x in signed]
    aerr_sum = sum(aerr)
    denom_actual = sum(abs(x) for x in actual)
    berr = [abs(baseline[i] - actual[i]) for i in range(n)]
    berr_sum = sum(berr)

    out = {"status": "scored", "n": n, "sample_ids": list(sample_ids)}
    out["signed_errors"] = signed
    out["absolute_errors"] = aerr
    out["absolute_error_sum"] = aerr_sum
    out["MAE"] = frac_out(Fraction(aerr_sum, n))
    out["WAPE"] = frac_out(Fraction(aerr_sum, denom_actual)) if denom_actual != 0 else undef("zero_denominator")
    out["Bias_U"] = frac_out(Fraction(sum(signed), n))
    out["NormalizedBias"] = frac_out(Fraction(sum(signed), denom_actual)) if denom_actual != 0 else undef("zero_denominator")
    out["baseline_absolute_errors"] = berr
    out["baseline_absolute_error_sum"] = berr_sum
    if berr_sum == 0:
        out["skill_vs_baseline"] = undef("zero_denominator_baseline_loss")
    else:
        out["skill_vs_baseline"] = frac_out(Fraction(1, 1) - Fraction(aerr_sum, berr_sum))
    # scenario band checks
    data_errors = []
    contained, widths = [], []
    for i in range(n):
        if high[i] < low[i]:
            data_errors.append(sample_ids[i])
            contained.append(None)
            widths.append(None)
            continue
        contained.append(low[i] <= actual[i] <= high[i])
        widths.append(high[i] - low[i])
    out["contained"] = contained
    out["scenario_containment"] = frac_out(Fraction(sum(1 for c in contained if c is True), n))
    out["widths"] = widths
    if data_errors:
        out["interval_data_error"] = {"samples": data_errors, "rule": "high<low = 数据错误"}
        out["mean_width"] = undef("interval_data_error")
        out["normalized_width"] = undef("interval_data_error")
    else:
        out["interval_data_error"] = None
        wsum = sum(widths)
        out["mean_width"] = frac_out(Fraction(wsum, n))
        out["normalized_width"] = frac_out(Fraction(wsum, denom_actual)) if denom_actual != 0 else undef("zero_denominator")
    # probabilistic-only metrics are gated
    if declared_nominal_coverage is None:
        out["interval_score"] = {"status": "rejected", "reason": "probabilistic_interval_not_declared",
                                 "rule": "仅用于事前明确为 1-alpha 名义覆盖率的统计区间；情景带禁用（metric_definitions）"}
        out["pinball"] = {"status": "rejected", "reason": "quantile_not_declared"}
    return out


def parse_expected(v):
    if isinstance(v, list):
        return v
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return Fraction(str(v))
    s = str(v)
    if "=" in s:
        s = s.split("=")[-1].strip()
    if "/" in s:
        a, b = s.split("/")
        return Fraction(int(a.strip()), int(b.strip()))
    return Fraction(s)


def cmp_value(observed, expected_raw):
    exp = parse_expected(expected_raw)
    if isinstance(expected_raw, list):
        return {"expected": expected_raw, "observed": observed, "pass": observed == expected_raw}
    if isinstance(observed, (int, float)) and not isinstance(observed, bool):
        got = Fraction(str(observed))
        exact = (got == exp)
        approx = abs(float(got) - float(exp)) <= 1e-12
        return {"expected": str(expected_raw), "expected_fraction": "%d/%d" % (exp.numerator, exp.denominator),
                "observed": observed, "exact_equal": exact, "abs_diff_le_1e-12": approx,
                "pass": bool(exact and approx)}
    if not isinstance(observed, dict) or not observed.get("defined"):
        return {"expected": expected_raw, "observed": observed, "pass": False,
                "why": "expected a defined value but observed undefined"}
    got = Fraction(observed["numerator"], observed["denominator"])
    exact = (got == exp)
    approx = abs(float(got) - float(exp)) <= 1e-12
    return {"expected": str(expected_raw), "expected_fraction": "%d/%d" % (exp.numerator, exp.denominator),
            "observed_fraction": observed["string"], "exact_equal": exact,
            "abs_diff_le_1e-12": approx, "pass": bool(exact and approx)}


def main():
    os.makedirs(EV, exist_ok=True)
    got_sha = sha256(CARDS)
    if got_sha != CARDS_SHA:
        print("HARNESS: research_cards.json sha mismatch %s" % got_sha)
        return 1
    with open(CARDS, "r", encoding="utf-8") as f:
        cards = json.load(f)
    fx = cards["metric_numeric_oracle"]

    # ---------- positive oracle ----------
    res = score(fx["sample_ids"], fx["actual"], fx["forecast"], fx["baseline"], fx["low"], fx["high"])
    comparisons = {}
    all_pass = True
    for key, exp in fx["expected"].items():
        c = cmp_value(res.get(key), exp)
        comparisons[key] = c
        all_pass = all_pass and c["pass"]

    sub = fx["probabilistic_interval_subcase"]
    sub_res = {
        "precondition_verbatim": sub["precondition"],
        "precondition_met": False,
        "computed": False,
        "reason": "本评估设计字段 9 冻结 low/high = 情景带（scenario bands），无 1-alpha 名义覆盖率声明 ⇒ 前置不满足，不计算该子用例（只登记）",
        "gated_behavior_verified_in": "metric_negative_results.json case E2（请求即被拒）",
        "fixture_expected_recorded_not_computed": sub["expected_interval_scores"],
        "hand_work_recorded_not_computed": sub["hand_work"],
    }

    oracle_out = {
        "schema": "i12d_metric_oracle_result/1",
        "card": "I-12-D",
        "attempt": "execution_runs/I-12-D/a20260926-01",
        "role": "implementer_i12d",
        "synthetic": True,
        "qualification": fx["qualification"],
        "fixture_source": {"path": "execution_v2/research_cards.json",
                           "sha256": got_sha, "json_path": "metric_numeric_oracle"},
        "action_step": "卡文动作 0（先跑 oracle 与负例；合格才碰真实样本）",
        "fixture_input": {k: fx[k] for k in ("sample_ids", "actual", "forecast", "baseline", "low", "high")},
        "computed": res,
        "expected_comparisons": comparisons,
        "all_expected_pass": all_pass,
        "comparison_rule_verbatim": fx["comparison"],
        "hand_work_verbatim": fx["hand_work"],
        "probabilistic_interval_subcase": sub_res,
        "independent_hand_check": {
            "signed_sum": "10+10-20 = 0",
            "abs_sum": "10+10+20 = 40",
            "actual_denominator": "100+0+200 = 300",
            "baseline_abs_sum": "0+0+50 = 50",
            "width_sum": "30+20+20 = 70",
            "MAE": "40/3", "WAPE": "40/300", "Bias_U": "0/3 = 0", "NormalizedBias": "0/300 = 0",
            "skill": "1 - 40/50 = 1/5 = 0.2",
            "containment": "S1 90<=100<=120 True；S2 0<=0<=20 True；S3 170<=200<=190 False ⇒ 2/3",
            "mean_width": "70/3", "normalized_width": "70/300",
        },
        "zero_epsilon_policy": "零分母一律 undefined + reason，代码路径中不存在 epsilon 分支（负例 1 实测）",
        "metrics_used": ["MAE", "WAPE", "signed_bias(Bias_U/NormalizedBias)", "skill_vs_baseline",
                         "scenario_containment", "interval_width"],
        "metrics_not_enabled": ["sMAPE_optional", "MASE_optional", "interval_score_if_probabilistic",
                                "pinball_if_quantiles", "CAGR（本 oracle 无该输入）", "driver_reconciliation（本 oracle 无该输入）"],
        "metrics_not_enabled_reason": "未事前声明/前置不满足（metric_definitions 边界）⇒ 换指标即触发 D8 与卡文验收「未经批准不得换指标」",
        "limitation_verbatim": fx["limitation"],
        "verdict": "PASS_metric_implementation_qualified_only" if all_pass else "FAIL",
    }
    with open(os.path.join(EV, "metric_oracle_result.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(oracle_out, f, ensure_ascii=False, indent=2)
        f.write("\n")

    # ---------- negative cases ----------
    cases = []
    nc = fx["negative_cases"]

    # 1 zero denominator
    patch = nc[0]["input_patch"]
    r1 = score(fx["sample_ids"], patch["actual"], fx["forecast"], fx["baseline"], fx["low"], fx["high"])
    checks1 = {
        "WAPE_undefined": r1["WAPE"]["defined"] is False and r1["WAPE"]["reason"] == "zero_denominator",
        "NormalizedBias_undefined": r1["NormalizedBias"]["defined"] is False and r1["NormalizedBias"]["reason"] == "zero_denominator",
        "normalized_width_undefined": r1["normalized_width"]["defined"] is False and r1["normalized_width"]["reason"] == "zero_denominator",
        "MAE_defined": r1["MAE"]["defined"] is True,
        "no_epsilon_used": all(r1[k]["value"] is None for k in ("WAPE", "NormalizedBias", "normalized_width")),
        "negative_skill_preserved": r1["skill_vs_baseline"]["defined"] is True and float(r1["skill_vs_baseline"]["decimal"]) < 0,
    }
    cases.append({"case": "N1_zero_denominator", "frozen_index": 0, "input_patch": patch,
                  "expected_verbatim": nc[0]["expected"], "observed": {
                      "WAPE": r1["WAPE"], "NormalizedBias": r1["NormalizedBias"],
                      "normalized_width": r1["normalized_width"], "MAE": r1["MAE"],
                      "skill_vs_baseline": r1["skill_vs_baseline"],
                      "scenario_containment": r1["scenario_containment"]},
                  "checks": checks1, "pass": all(checks1.values())})

    # 2 sample_id misalignment
    patch2 = nc[1]["input_patch"]
    r2 = score(fx["sample_ids"], fx["actual"], fx["forecast"], fx["baseline"], fx["low"], fx["high"],
               forecast_sample_ids=patch2["forecast_sample_ids"])
    checks2 = {
        "rejected": r2.get("status") == "rejected",
        "reason_is_sample_id_misalignment": r2.get("reason") == "sample_id_misalignment",
        "no_metrics_emitted": not any(k in r2 for k in ("WAPE", "MAE", "skill_vs_baseline")),
        "position_scoring_refused": "positional scoring refused" in str(r2.get("detail", "")),
    }
    cases.append({"case": "N2_sample_id_misalignment", "frozen_index": 1, "input_patch": patch2,
                  "expected_verbatim": nc[1]["expected"], "observed": r2,
                  "checks": checks2, "pass": all(checks2.values())})

    # 3 baseline loss = 0
    patch3 = nc[2]["input_patch"]
    r3 = score(fx["sample_ids"], fx["actual"], fx["forecast"], patch3["baseline"], fx["low"], fx["high"])
    checks3 = {
        "skill_undefined": r3["skill_vs_baseline"]["defined"] is False,
        "reason_is_zero_denominator_baseline_loss": r3["skill_vs_baseline"]["reason"] == "zero_denominator_baseline_loss",
        "not_recorded_as_100pct_improvement": "100" not in json.dumps(r3["skill_vs_baseline"], ensure_ascii=False),
        "baseline_abs_sum_is_zero": r3["baseline_absolute_error_sum"] == 0,
    }
    cases.append({"case": "N3_baseline_loss_zero", "frozen_index": 2, "input_patch": patch3,
                  "expected_verbatim": nc[2]["expected"],
                  "observed": {"skill_vs_baseline": r3["skill_vs_baseline"],
                               "baseline_absolute_error_sum": r3["baseline_absolute_error_sum"]},
                  "checks": checks3, "pass": all(checks3.values())})

    # E1 extended: high < low
    rE1 = score(fx["sample_ids"], fx["actual"], fx["forecast"], fx["baseline"], fx["low"], [80, 20, 190])
    checksE1 = {
        "data_error_detected": (rE1.get("interval_data_error") or {}).get("samples") == ["S1"],
        "mean_width_undefined": rE1["mean_width"]["defined"] is False and rE1["mean_width"]["reason"] == "interval_data_error",
        "width_not_silently_averaged": rE1["widths"][0] is None,
    }
    cases.append({"case": "E1_high_below_low", "frozen_index": None, "control": "extended",
                  "input_patch": {"high": [80, 20, 190]},
                  "expected_verbatim": "high<low直接数据错误（metric_definitions interval_width boundary）⇒ 标记数据错误，不静默平均",
                  "observed": {"interval_data_error": rE1.get("interval_data_error"), "widths": rE1["widths"],
                               "mean_width": rE1["mean_width"]},
                  "checks": checksE1, "pass": all(checksE1.values())})

    # E2 extended: interval_score requested without declared nominal coverage
    rE2 = score(fx["sample_ids"], fx["actual"], fx["forecast"], fx["baseline"], fx["low"], fx["high"],
                declared_nominal_coverage=None)
    checksE2 = {
        "interval_score_rejected": rE2["interval_score"]["status"] == "rejected",
        "reason_probabilistic_not_declared": rE2["interval_score"]["reason"] == "probabilistic_interval_not_declared",
        "pinball_rejected": rE2["pinball"]["status"] == "rejected",
    }
    cases.append({"case": "E2_interval_score_gated", "frozen_index": None, "control": "extended",
                  "input_patch": {"request": "IS_alpha with no declared 1-alpha nominal coverage"},
                  "expected_verbatim": "仅用于事前明确为1-alpha名义覆盖率的统计区间；情景带禁用（metric_definitions）",
                  "observed": {"interval_score": rE2["interval_score"], "pinball": rE2["pinball"]},
                  "checks": checksE2, "pass": all(checksE2.values())})

    neg_out = {
        "schema": "i12d_metric_negative_results/1",
        "card": "I-12-D",
        "attempt": "execution_runs/I-12-D/a20260926-01",
        "role": "implementer_i12d",
        "synthetic": True,
        "qualification": fx["qualification"],
        "fixture_source": {"path": "execution_v2/research_cards.json", "sha256": got_sha,
                           "json_path": "metric_numeric_oracle.negative_cases"},
        "frozen_negative_cases_count": len(nc),
        "extended_controls_count": 2,
        "cases": cases,
        "all_pass": all(c["pass"] for c in cases),
        "stop_rule_verbatim": "发现零分母被任意epsilon替代、样本不对齐或结果挑选→STOP_METRICS。",
        "stop_triggered": not all(c["pass"] for c in cases),
        "limitation_verbatim": fx["limitation"],
    }
    with open(os.path.join(EV, "metric_negative_results.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(neg_out, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print("oracle all_expected_pass=%s verdict=%s" % (all_pass, oracle_out["verdict"]))
    print("negatives all_pass=%s stop_triggered=%s" % (neg_out["all_pass"], neg_out["stop_triggered"]))
    for c in cases:
        print("  %s pass=%s" % (c["case"], c["pass"]))
    return 0 if (all_pass and neg_out["all_pass"]) else 3


if __name__ == "__main__":
    sys.exit(main())
