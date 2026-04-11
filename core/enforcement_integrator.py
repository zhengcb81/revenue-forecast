"""
强制执行集成器 - 将控制器与现有验证机制集成
版本: v1.0
创建日期: 2026-01-17

功能:
1. 集成EnforcementController与checklist验证
2. 集成EnforcementController与报告验证
3. 提供简化API
4. 生成综合验证报告
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from .enforcement_controller import EnforcementController, StepValidationResult
from .checklist_validator import ChecklistValidator

class EnforcementIntegrator:
    """强制执行集成器"""

    def __init__(self, company_name: str, project_root: str = None):
        self.company_name = company_name
        self.project_root = project_root or self._find_project_root()
        self.controller = EnforcementController(company_name)

        # 路径
        self.checklist_path = Path(__file__).parent.parent / "checklist.md"
        self.validate_report_path = Path(__file__).parent.parent / "validate_report.py"
        self.outputs_dir = Path(self.project_root) / "outputs"

        # 验证器
        self.checklist_validator = None
        if self.checklist_path.exists():
            try:
                self.checklist_validator = ChecklistValidator(str(self.checklist_path))
            except Exception as e:
                print(f"⚠️ 检查清单验证器初始化失败: {e}")

    def _find_project_root(self) -> str:
        """查找项目根目录"""
        # 假设技能目录在.claude/skills/revenue-forecast/
        # 项目根目录是技能目录的父级的父级的父级
        skill_dir = Path(__file__).parent.parent
        project_root = skill_dir.parent.parent.parent
        return str(project_root)

    def setup_checklist_validation(self):
        """设置检查清单验证"""
        if not self.checklist_validator:
            print("⚠️ 检查清单验证器不可用")
            return

        # 为每个步骤设置检查清单验证
        for step_id in self.controller.steps.keys():
            # 创建验证函数
            def create_validator(sid=step_id):
                def validator():
                    if not self.checklist_validator:
                        return StepValidationResult(True, warnings=["检查清单验证器不可用"])
                    return self.checklist_validator.validate_step(sid)
                return validator

            # 获取步骤并设置验证函数
            step = self.controller.steps[step_id]
            step.validation_func = create_validator(step_id)

    def validate_with_checklist(self, step_id: str) -> StepValidationResult:
        """使用检查清单验证步骤"""
        if not self.checklist_validator:
            return StepValidationResult(True, warnings=["检查清单验证器不可用"])

        return self.checklist_validator.validate_step(step_id)

    def run_report_validation(self) -> Tuple[bool, str]:
        """运行报告验证脚本"""
        if not self.validate_report_path.exists():
            return False, f"验证脚本不存在: {self.validate_report_path}"

        if not self.outputs_dir.exists():
            return False, f"输出目录不存在: {self.outputs_dir}"

        try:
            cmd = [
                sys.executable,
                str(self.validate_report_path),
                self.company_name,
                str(self.outputs_dir)
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=30
            )

            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, result.stderr or result.stdout

        except subprocess.TimeoutExpired:
            return False, "验证脚本执行超时"
        except Exception as e:
            return False, f"验证脚本执行失败: {e}"

    def validate_report_step(self) -> StepValidationResult:
        """验证报告步骤（对应step9_5）"""
        result = StepValidationResult(True)

        success, output = self.run_report_validation()
        if not success:
            result.add_error(f"报告验证失败: {output}")
        else:
            result.metadata = {"validation_output": output}

        return result

    def enforce_complete_analysis(self) -> Dict:
        """强制执行完整分析验证"""
        results = {
            "company_name": self.company_name,
            "controller_validation": None,
            "checklist_validation": None,
            "report_validation": None,
            "overall_passed": False
        }

        # 1. 控制器验证（步骤完整性和依赖）
        controller_result = self.controller.enforce_complete_execution()
        results["controller_validation"] = {
            "passed": bool(controller_result),
            "errors": controller_result.errors,
            "warnings": controller_result.warnings
        }

        # 2. 检查清单验证
        checklist_results = {}
        if self.checklist_validator:
            for step_id in self.controller.steps.keys():
                step_result = self.checklist_validator.validate_step(step_id)
                checklist_results[step_id] = {
                    "passed": bool(step_result),
                    "errors": step_result.errors,
                    "warnings": step_result.warnings
                }
        results["checklist_validation"] = checklist_results

        # 3. 报告验证
        report_result = self.validate_report_step()
        results["report_validation"] = {
            "passed": bool(report_result),
            "errors": report_result.errors,
            "warnings": report_result.warnings
        }

        # 总体通过条件
        controller_passed = bool(controller_result)
        checklist_passed = all(r["passed"] for r in checklist_results.values()) if checklist_results else True
        report_passed = bool(report_result)

        results["overall_passed"] = controller_passed and checklist_passed and report_passed

        return results

    def print_comprehensive_report(self):
        """打印综合验证报告"""
        print("=" * 80)
        print("营收增长预测分析 - 综合强制执行报告")
        print("=" * 80)
        print(f"公司: {self.company_name}")
        print(f"项目根目录: {self.project_root}")
        print()

        # 控制器状态
        print("1. 步骤执行状态:")
        print("-" * 40)
        self.controller.print_status_report()
        print()

        # 检查清单状态
        print("2. 检查清单验证:")
        print("-" * 40)
        if self.checklist_validator:
            self.checklist_validator.print_summary()
        else:
            print("⚠️ 检查清单验证器不可用")
        print()

        # 报告验证状态
        print("3. 报告验证:")
        print("-" * 40)
        success, output = self.run_report_validation()
        if success:
            print("✅ 报告验证通过")
        else:
            print("❌ 报告验证失败")
            print(f"   错误: {output}")
        print()

        # 总体结论
        print("4. 总体结论:")
        print("-" * 40)
        results = self.enforce_complete_analysis()
        if results["overall_passed"]:
            print("✅ 分析完整执行验证通过!")
            print("   所有步骤已完整执行，检查清单完成，报告验证通过。")
        else:
            print("❌ 分析完整执行验证失败!")
            if results["controller_validation"]["errors"]:
                print("   步骤执行问题:", ", ".join(results["controller_validation"]["errors"]))
            if results["report_validation"]["errors"]:
                print("   报告验证问题:", ", ".join(results["report_validation"]["errors"]))

        print("=" * 80)

    def get_recommendations(self) -> List[str]:
        """获取改进建议"""
        recommendations = []

        # 控制器建议
        controller_result = self.controller.enforce_complete_execution()
        if not controller_result:
            for error in controller_result.errors:
                recommendations.append(f"步骤执行: {error}")

        # 检查清单建议
        if self.checklist_validator:
            for step_id, step in self.checklist_validator.steps.items():
                completed, total = step.get_completion_rate()
                if completed < total:
                    recommendations.append(f"检查清单: 步骤 {step_id} 未完全完成 ({completed}/{total})")

        # 报告验证建议
        success, output = self.run_report_validation()
        if not success:
            recommendations.append(f"报告验证: {output}")

        return recommendations


# ============ 使用示例 ============

if __name__ == "__main__":
    """使用示例"""
    # 示例公司名称
    company = "测试公司"

    print("=" * 80)
    print("强制执行集成器测试")
    print("=" * 80)

    try:
        integrator = EnforcementIntegrator(company)

        # 设置检查清单验证
        integrator.setup_checklist_validation()

        # 模拟执行一些步骤
        print(f"\n模拟执行步骤:")
        print("-" * 40)

        # 步骤0
        if integrator.controller.can_start_step("step0"):
            integrator.controller.start_step("step0")
            integrator.controller.complete_step("step0")
            print("✅ 步骤0: 加载配置 - 完成")

        # 步骤1
        if integrator.controller.can_start_step("step1"):
            integrator.controller.start_step("step1")
            integrator.controller.complete_step("step1")
            print("✅ 步骤1: 初始化缓存系统 - 完成")

        # 尝试跳过步骤2（应该被阻止）
        print("\n测试防跳过机制:")
        print("-" * 40)
        try:
            integrator.controller.start_step("step3")
            print("❌ 错误: 成功跳过了步骤2")
        except ValueError as e:
            print(f"✅ 正确阻止跳过: {e}")

        # 打印综合报告
        print("\n综合验证报告:")
        integrator.print_comprehensive_report()

        # 获取建议
        print("\n改进建议:")
        recommendations = integrator.get_recommendations()
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. {rec}")
        else:
            print("✅ 无改进建议")

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

    print("=" * 80)