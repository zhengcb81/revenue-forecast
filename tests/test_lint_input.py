from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from test_recognition_bridge import forecast_document  # noqa: E402
import lint_input  # noqa: E402


class LintTests(unittest.TestCase):
    def setUp(self) -> None:
        self.base = forecast_document()

    def test_clean_doc_has_zero_findings(self) -> None:
        self.assertEqual(lint_input.lint(self.base), [])

    def test_detects_capture_field_shape(self) -> None:
        data = copy.deepcopy(self.base)
        data["sources"][0]["capture"]["bogus_key"] = "x"
        findings = lint_input.lint(data)
        self.assertTrue(any(f["category"] == "capture_shape" for f in findings), findings)

    def test_detects_missing_capture_key(self) -> None:
        data = copy.deepcopy(self.base)
        del data["sources"][0]["capture"]["captured_date"]
        findings = lint_input.lint(data)
        self.assertTrue(any(f["category"] == "capture_shape" for f in findings), findings)

    def test_detects_ghost_source_id(self) -> None:
        data = copy.deepcopy(self.base)
        data["parameters"][0]["source_ids"] = ["ghost_source"]
        findings = lint_input.lint(data)
        self.assertTrue(any("ghost_source" in f["message"] for f in findings), findings)

    def test_detects_claim_target_mismatch(self) -> None:
        data = copy.deepcopy(self.base)
        claim = next(c for c in data["evidence_claims"] if c["target_type"] == "parameter")
        claim["target_id"] = "segment_b_base"
        findings = lint_input.lint(data)
        self.assertTrue(
            any(f["category"] == "reference" and "does not support" in f["message"] for f in findings),
            findings,
        )

    def test_detects_stale_receipt_and_excerpt_hashes(self) -> None:
        data = copy.deepcopy(self.base)
        data["sources"][0]["capture"]["receipt_sha256"] = "0" * 64
        data["evidence_claims"][0]["excerpt_sha256"] = "0" * 64
        findings = lint_input.lint(data)
        self.assertGreaterEqual([f["category"] for f in findings].count("hash"), 2, findings)

    def test_detects_attribution_weight_not_one(self) -> None:
        data = copy.deepcopy(self.base)
        data["growth_driver_tree"]["drivers"][0]["segment_attribution"][0]["weight"] = 0.8
        findings = lint_input.lint(data)
        self.assertTrue(
            any(f["category"] == "aggregate" and "weight" in f["message"] for f in findings),
            findings,
        )

    def test_collect_all_reports_independent_violations(self) -> None:
        data = copy.deepcopy(self.base)
        data["parameters"][0]["source_ids"] = ["ghost_source"]
        data["evidence_claims"][0]["excerpt_sha256"] = "0" * 64
        data["growth_driver_tree"]["drivers"][0]["segment_attribution"][0]["weight"] = 0.8
        findings = lint_input.lint(data)
        categories = {f["category"] for f in findings}
        self.assertIn("reference", categories)
        self.assertIn("hash", categories)
        self.assertIn("aggregate", categories)
        self.assertGreaterEqual(len(findings), 3)


class LintCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.base = forecast_document()
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = self._tmp.name

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _write(self, data: dict) -> str:
        path = os.path.join(self.dir, "input.json")
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False)
        return path

    def _run(self, *args: str) -> subprocess.CompletedProcess:
        root = Path(__file__).resolve().parents[1]
        cmd = [sys.executable, str(root / "scripts" / "lint_input.py"), *args]
        env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
        return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", env=env)

    def test_clean_doc_exit_0(self) -> None:
        result = self._run(self._write(copy.deepcopy(self.base)))
        self.assertEqual(result.returncode, 0)

    def test_findings_exit_2(self) -> None:
        data = copy.deepcopy(self.base)
        data["parameters"][0]["source_ids"] = ["ghost_source"]
        result = self._run(self._write(data))
        self.assertEqual(result.returncode, 2)
        self.assertIn("ghost_source", result.stdout + result.stderr)

    def test_conclusion_digit_without_claim_warns(self) -> None:
        # Phase 17.3: conclusion 含数字但记录无任何 claim 背书 → --check-conclusion-facts 报告
        data = copy.deepcopy(self.base)
        record = next(r for r in data["research_coverage"] if r["dimension"] == "policy")
        record["conclusion"] = "市場規模預計年增長7%但無任何 claim 背書"
        record["parameter_ids"] = []
        result = self._run("--check-conclusion-facts", self._write(data))
        self.assertEqual(result.returncode, 2)
        output = result.stdout + result.stderr
        self.assertIn("[conclusion-facts]", output)
        self.assertIn("policy", output)

    def test_conclusion_digit_with_claim_passes(self) -> None:
        # Phase 17.3 正向护栏: 同记录引用的 claim excerpt 含该数字 → 0 findings
        data = copy.deepcopy(self.base)
        import hashlib
        claim = next(c for c in data["evidence_claims"] if c["target_type"] == "parameter")
        claim["excerpt"] = "來源摘錄：雲收入同比增長7%"
        claim["excerpt_sha256"] = hashlib.sha256(claim["excerpt"].encode("utf-8")).hexdigest()
        record = next(r for r in data["research_coverage"] if r["dimension"] == "growth_curve")
        record["conclusion"] = "模型驅動收入路徑年增長7%（有 claim 背書）"
        record["parameter_ids"] = [claim["target_id"]]
        result = self._run("--check-conclusion-facts", self._write(data))
        self.assertEqual(result.returncode, 0)

    def test_sensitivity_absolute_level_param_pre_terminal_warns(self) -> None:
        # Phase 17.4: 绝对水平型参数（usage_platform eligible_activity）年份 < 终期 → 告警
        data = copy.deepcopy(self.base)
        seg = data["segments"][0]
        first_year = str(data["forecast_years"][0])
        pid = f"0_base_{first_year}"
        seg["scenarios"]["base"] = {
            "model": "usage_platform",
            "driver_parameter_ids": {"eligible_activity": [pid], "monetization_rate": []},
            "rationale": "sensitivity propagation test",
        }
        data["sensitivity_tests"] = [
            {"name": "pre-terminal", "parameter_id": pid, "shock_type": "percent", "shock_value": 0.1},
        ]
        result = self._run("--check-sensitivity-propagation", self._write(data))
        self.assertEqual(result.returncode, 2)
        output = result.stdout + result.stderr
        self.assertIn("[sensitivity-propagation]", output)
        self.assertIn(pid, output)

    def test_sensitivity_terminal_param_passes(self) -> None:
        # Phase 17.4 正向护栏: 终期年参数（usage_platform 绝对水平型但年份==终期）→ 0 findings
        # （真正触发 year >= terminal_year 短路分支，而非依赖模型传播型）
        data = copy.deepcopy(self.base)
        segment = data["segments"][0]
        max_year = str(max(data["forecast_years"]))
        pid = f"0_base_{max_year}"
        segment["scenarios"]["base"] = {
            "model": "usage_platform",
            "driver_parameter_ids": {"eligible_activity": [pid], "monetization_rate": []},
            "rationale": "sensitivity propagation test",
        }
        data["sensitivity_tests"] = [
            {"name": "terminal", "parameter_id": pid, "shock_type": "percent", "shock_value": 0.1},
        ]
        result = self._run("--check-sensitivity-propagation", self._write(data))
        self.assertEqual(result.returncode, 0)

    def test_sensitivity_growth_rate_param_passes(self) -> None:
        # Phase 17.4 正向护栏: direct_growth growth_rate 为传播型 → 0 findings
        data = copy.deepcopy(self.base)
        seg = data["segments"][0]
        first_year = str(data["forecast_years"][0])
        pid = f"0_base_{first_year}"
        seg["scenarios"]["base"] = {
            "model": "direct_growth",
            "driver_parameter_ids": {"growth_rate": [pid]},
            "rationale": "sensitivity propagation test",
        }
        data["sensitivity_tests"] = [
            {"name": "growth-rate", "parameter_id": pid, "shock_type": "percent", "shock_value": 0.1},
        ]
        result = self._run("--check-sensitivity-propagation", self._write(data))
        self.assertEqual(result.returncode, 0)


class LintHeuristicInProcessTests(unittest.TestCase):
    """In-process coverage for the opt-in heuristics (subprocess CLI tests are
    invisible to the coverage run, so the flag branches need direct calls)."""

    def setUp(self) -> None:
        self.base = forecast_document()

    def test_conclusion_facts_flag_reports_in_process(self) -> None:
        data = copy.deepcopy(self.base)
        record = next(r for r in data["research_coverage"] if r["dimension"] == "policy")
        record["conclusion"] = "市場規模預計年增長7%但無任何 claim 背書"
        record["parameter_ids"] = []
        findings = lint_input.lint(data, check_conclusion_facts=True)
        self.assertTrue(any(f["category"] == "conclusion-facts" for f in findings), findings)
        # 默认关闭（向后兼容护栏）
        self.assertFalse(any(f["category"] == "conclusion-facts" for f in lint_input.lint(data)))

    def test_sensitivity_propagation_flag_reports_in_process(self) -> None:
        data = copy.deepcopy(self.base)
        segment = data["segments"][0]
        pid = f"0_base_{data['forecast_years'][0]}"
        segment["scenarios"]["base"] = {
            "model": "usage_platform",
            "driver_parameter_ids": {"eligible_activity": [pid], "monetization_rate": []},
            "rationale": "in-process coverage",
        }
        data["sensitivity_tests"] = [
            {"name": "t", "parameter_id": pid, "shock_type": "percent", "shock_value": 0.1},
        ]
        findings = lint_input.lint(data, check_sensitivity_propagation=True)
        self.assertTrue(any(f["category"] == "sensitivity-propagation" for f in findings), findings)
        # 默认关闭（向后兼容护栏）
        self.assertFalse(any(f["category"] == "sensitivity-propagation" for f in lint_input.lint(data)))

    def test_odd_number_token_does_not_crash(self) -> None:
        # 审查回归（B1 Important）: "1.2.3" 类 token 通过数字正则但不是 float，
        # 启发式必须不崩溃（lint "never raises" 契约）
        data = copy.deepcopy(self.base)
        record = next(r for r in data["research_coverage"] if r["dimension"] == "policy")
        record["conclusion"] = "版本1.2.3已部署，增長7%，2026.06.18公告"
        record["parameter_ids"] = []
        findings = lint_input.lint(data, check_conclusion_facts=True)
        self.assertTrue(any(f["category"] == "conclusion-facts" for f in findings), findings)

    def test_management_communication_conclusion_facts_in_process(self) -> None:
        data = copy.deepcopy(self.base)
        record = next(r for r in data["management_communication_coverage"] if r["category"] == "latest_annual_filing")
        record["conclusion"] = "董事會公告披露回購金額7億元"
        record["material_revenue_target_ids"] = []
        findings = lint_input.lint(data, check_conclusion_facts=True)
        self.assertTrue(any(f["category"] == "conclusion-facts" for f in findings), findings)


class MainInProcessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.base = forecast_document()
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = self._tmp.name

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _path(self, data: dict) -> str:
        path = os.path.join(self.dir, "i.json")
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False)
        return path

    def test_main_clean_returns_0(self) -> None:
        self.assertEqual(lint_input.main([self._path(copy.deepcopy(self.base))]), 0)

    def test_main_findings_return_2(self) -> None:
        data = copy.deepcopy(self.base)
        data["parameters"][0]["source_ids"] = ["ghost_source"]
        self.assertEqual(lint_input.main([self._path(data)]), 2)

    def test_main_bad_json_returns_2(self) -> None:
        path = os.path.join(self.dir, "bad.json")
        Path(path).write_text("{x", encoding="utf-8")
        self.assertEqual(lint_input.main([path]), 2)

    def test_main_non_object_input_returns_2(self) -> None:
        path = os.path.join(self.dir, "arr.json")
        Path(path).write_text("[1, 2, 3]", encoding="utf-8")
        self.assertEqual(lint_input.main([path]), 2)


if __name__ == "__main__":
    unittest.main()
