"""
Revenue Forecast v2.5.1 - 完整功能测试
版本: v1.0
创建日期: 2026-03-01

测试所有v2.5.1功能模块
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入所有模块
from core.checkpoint_registry import CheckpointRegistry, CheckpointConfig
from core.validators.content_quality_validator import ContentQualityValidator
from core.validators.tool_usage_validator import ToolUsageValidator
from core.validators.cagr_validator import CAGRValidator
from core.validators.tracing_validator import TracingValidator, ParameterSource
from core.validators.consistency_validator import ConsistencyValidator
from core.industry_data import IndustryData
from core.automated_checklist import AutomatedChecklist
from core.dynamic_threshold import DynamicThresholdManager
from core.intelligent_early_warning import IntelligentEarlyWarning, StepMetrics
from core.quality_attribution import QualityAttributionAnalyzer
from core.enforcement_controller import (
    EnhancedValidatorV251,
    BusinessLogicValidatorV251,
    IntelligentValidatorV251,
    UnifiedValidatorV251,
    CompleteValidatorV251,
    get_complete_validator_v251
)


class Colors:
    """终端颜色"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'


def print_header(text):
    """打印标题"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")


def print_result(name, passed, message=""):
    """打印结果"""
    status = f"{Colors.GREEN}[PASS]{Colors.END}" if passed else f"{Colors.RED}[FAIL]{Colors.END}"
    print(f"  {status} {name}")
    if message:
        print(f"       {message}")


def test_all_modules():
    """测试所有模块"""
    results = []
    
    # 1. CheckpointRegistry
    print_header("测试 CheckpointRegistry")
    try:
        registry = CheckpointRegistry()
        registry.register(CheckpointConfig(id="test", name="Test"))
        checkpoints = registry.list_checkpoints()
        print_result("CheckpointRegistry", True, f"已注册 {len(checkpoints)} 个检查点")
        results.append(("CheckpointRegistry", True))
    except Exception as e:
        print_result("CheckpointRegistry", False, str(e))
        results.append(("CheckpointRegistry", False))
    
    # 2. ContentQualityValidator
    print_header("测试 ContentQualityValidator")
    try:
        validator = ContentQualityValidator()
        content = "测试内容" * 1000
        result = validator.validate(content, "step4")
        print_result("ContentQualityValidator", True, f"评分: {result.score:.1f}")
        results.append(("ContentQualityValidator", True))
    except Exception as e:
        print_result("ContentQualityValidator", False, str(e))
        results.append(("ContentQualityValidator", False))
    
    # 3. ToolUsageValidator
    print_header("测试 ToolUsageValidator")
    try:
        validator = ToolUsageValidator()
        tool_calls = [{"type": "search"}] * 10 + [{"type": "read"}] * 5 + [{"type": "write"}] * 5
        result = validator.validate(tool_calls, "step4")
        print_result("ToolUsageValidator", True, f"评分: {result.score:.1f}")
        results.append(("ToolUsageValidator", True))
    except Exception as e:
        print_result("ToolUsageValidator", False, str(e))
        results.append(("ToolUsageValidator", False))
    
    # 4. CAGRValidator
    print_header("测试 CAGRValidator")
    try:
        validator = CAGRValidator()
        result = validator.validate(25, "technology", "测试公司")
        print_result("CAGRValidator", True, f"25% CAGR 通过: {result.passed}")
        results.append(("CAGRValidator", True))
    except Exception as e:
        print_result("CAGRValidator", False, str(e))
        results.append(("CAGRValidator", False))
    
    # 5. IndustryData
    print_header("测试 IndustryData")
    try:
        data = IndustryData()
        cagr = data.get_industry_cagr("technology")
        print_result("IndustryData", True, f"Technology CAGR: {cagr}%")
        results.append(("IndustryData", True))
    except Exception as e:
        print_result("IndustryData", False, str(e))
        results.append(("IndustryData", False))
    
    # 6. TracingValidator
    print_header("测试 TracingValidator")
    try:
        validator = TracingValidator()
        params = [
            ParameterSource("revenue_base", 1000, "年报", "official", "high"),
            ParameterSource("cagr", 20, "预测", "estimate", "medium")
        ]
        result = validator.validate(params)
        print_result("TracingValidator", True, f"溯源率: {result.details.get('metrics', {}).get('trace_ratio', 0):.0%}")
        results.append(("TracingValidator", True))
    except Exception as e:
        print_result("TracingValidator", False, str(e))
        results.append(("TracingValidator", False))
    
    # 7. ConsistencyValidator
    print_header("测试 ConsistencyValidator")
    try:
        validator = ConsistencyValidator()
        test_json = {
            "company_name": "测试",
            "score": 8.5,
            "scenario_analysis": {
                "optimistic": {"cagr": 28},
                "base": {"cagr": 22.5},
                "pessimistic": {"cagr": 15}
            }
        }
        result = validator.validate_internal_consistency(test_json)
        print_result("ConsistencyValidator", True, f"内部一致性: {result.passed}")
        results.append(("ConsistencyValidator", True))
    except Exception as e:
        print_result("ConsistencyValidator", False, str(e))
        results.append(("ConsistencyValidator", False))
    
    # 8. AutomatedChecklist
    print_header("测试 AutomatedChecklist")
    try:
        checklist = AutomatedChecklist()
        print_result("AutomatedChecklist", True, f"加载了 {len(checklist.check_items)} 个检查项")
        results.append(("AutomatedChecklist", True))
    except Exception as e:
        print_result("AutomatedChecklist", False, str(e))
        results.append(("AutomatedChecklist", False))
    
    # 9. DynamicThresholdManager
    print_header("测试 DynamicThresholdManager")
    try:
        manager = DynamicThresholdManager()
        profile = {"market_cap": 1000, "business_segments": 3, "industry": "technology"}
        thresholds = manager.calculate_thresholds("step4", profile)
        print_result("DynamicThresholdManager", True, f"Tokens: {thresholds.tokens}")
        results.append(("DynamicThresholdManager", True))
    except Exception as e:
        print_result("DynamicThresholdManager", False, str(e))
        results.append(("DynamicThresholdManager", False))
    
    # 10. IntelligentEarlyWarning
    print_header("测试 IntelligentEarlyWarning")
    try:
        warning_system = IntelligentEarlyWarning()
        metrics = StepMetrics(
            step_id="step4",
            token_usage=10000,
            content_length=2000,
            tool_calls=[{}] * 15
        )
        alerts = warning_system.monitor_step_execution(metrics)
        print_result("IntelligentEarlyWarning", True, f"生成 {len(alerts)} 个预警")
        results.append(("IntelligentEarlyWarning", True))
    except Exception as e:
        print_result("IntelligentEarlyWarning", False, str(e))
        results.append(("IntelligentEarlyWarning", False))
    
    # 11. QualityAttributionAnalyzer
    print_header("测试 QualityAttributionAnalyzer")
    try:
        from core.checkpoint_registry import CheckpointResult
        analyzer = QualityAttributionAnalyzer()
        test_failures = [
            CheckpointResult("test1", False, "测试失败")
        ]
        context = {"tool_calls": [], "token_usage": 1000}
        result = analyzer.analyze(test_failures, context)
        print_result("QualityAttributionAnalyzer", True, f"发现问题: {result['has_issues']}")
        results.append(("QualityAttributionAnalyzer", True))
    except Exception as e:
        print_result("QualityAttributionAnalyzer", False, str(e))
        results.append(("QualityAttributionAnalyzer", False))
    
    # 12. CompleteValidatorV251
    print_header("测试 CompleteValidatorV251")
    try:
        validator = get_complete_validator_v251()
        available = validator.is_v251_available()
        print_result("CompleteValidatorV251", True, f"v2.5.1可用: {available}")
        results.append(("CompleteValidatorV251", True))
    except Exception as e:
        print_result("CompleteValidatorV251", False, str(e))
        results.append(("CompleteValidatorV251", False))
    
    return results


def print_summary(results):
    """打印测试摘要"""
    print_header("测试摘要")
    
    passed = sum(1 for _, r in results if r)
    failed = sum(1 for _, r in results if not r)
    total = len(results)
    
    for name, result in results:
        status = f"{Colors.GREEN}✓{Colors.END}" if result else f"{Colors.RED}✗{Colors.END}"
        print(f"  {status} {name}")
    
    print(f"\n{Colors.BLUE}总计: {passed}/{total} 通过, {failed} 失败{Colors.END}")
    
    if failed == 0:
        print(f"\n{Colors.GREEN}🎉 所有测试通过！v2.5.1 功能完整可用！{Colors.END}")
    else:
        print(f"\n{Colors.YELLOW}⚠️ 有 {failed} 个模块需要检查{Colors.END}")
    
    return failed == 0


def main():
    """主函数"""
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}Revenue Forecast v2.5.1 完整功能测试{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    
    results = test_all_modules()
    success = print_summary(results)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
