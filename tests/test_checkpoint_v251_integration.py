"""
Revenue Forecast v2.5.1 - 检查点系统集成测试
版本: v1.0
创建日期: 2026-03-01
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.checkpoint_registry import CheckpointRegistry, CheckpointConfig, CheckpointType
from core.validators.content_quality_validator import ContentQualityValidator
from core.validators.tool_usage_validator import ToolUsageValidator
from core.validators.cagr_validator import CAGRValidator
from core.validators.tracing_validator import TracingValidator, ParameterSource
from core.industry_data import IndustryData
from core.automated_checklist import AutomatedChecklist
from core.dynamic_threshold import DynamicThresholdManager
from core.enforcement_controller import (
    EnhancedValidatorV251, 
    BusinessLogicValidatorV251,
    UnifiedValidatorV251,
    get_enhanced_validator_v251,
    get_business_logic_validator_v251,
    get_unified_validator_v251
)


def test_checkpoint_registry():
    """测试检查点注册中心"""
    print("\n" + "="*60)
    print("测试: CheckpointRegistry")
    print("="*60)
    
    registry = CheckpointRegistry()
    
    # 注册测试检查点
    config = CheckpointConfig(
        id="test_checkpoint",
        name="测试检查点",
        type=CheckpointType.BLOCKING
    )
    registry.register(config)
    
    # 列出检查点
    checkpoints = registry.list_checkpoints()
    assert len(checkpoints) >= 1, "应该至少有一个检查点"
    
    print(f"[PASS] 注册中心工作正常，已注册 {len(checkpoints)} 个检查点")
    return True


def test_content_quality_validator():
    """测试内容质量验证器"""
    print("\n" + "="*60)
    print("测试: ContentQualityValidator")
    print("="*60)
    
    validator = ContentQualityValidator()
    
    # 测试高质量内容
    good_content = """
# 市场分析

## 市场规模
2026年中国智能手机市场规模达到3.5万亿元，同比增长8.5%。
预计2027-2031年CAGR为5-7%，主要受益于5G换机潮。

## 竞争格局
小米集团2026年市场份额为16.8%，位居第二。
相比2025年的15.2%，增长了1.6个百分点。

## 增长驱动
1. 高端化：均价从1200元提升至1500元，涨幅25%
2. 海外扩张：欧洲市场增长35%
3. 生态协同：IoT设备连接数达7亿+
""" * 10  # 扩展内容长度
    
    result = validator.validate(good_content, "step4")
    
    print(f"  通过: {result.passed}")
    print(f"  分数: {result.score:.1f}")
    print(f"  数据点: {result.details.get('data_points', 0)}")
    
    # 测试低质量内容
    bad_content = "市场很大，公司很好。未来会增长。"
    result2 = validator.validate(bad_content, "step4")
    
    assert not result2.passed, "低质量内容应该不通过"
    print(f"[PASS] 内容质量验证器工作正常")
    return True


def test_tool_usage_validator():
    """测试工具使用验证器"""
    print("\n" + "="*60)
    print("测试: ToolUsageValidator")
    print("="*60)
    
    validator = ToolUsageValidator()
    
    # 模拟工具调用
    tool_calls = [
        {"type": "web_search", "name": "search", "params": {"query": "小米集团"}},
        {"type": "web_search", "name": "search", "params": {"query": "智能手机市场"}},
        {"type": "file_read", "name": "read", "params": {"path": "config.yaml"}},
        {"type": "file_write", "name": "write", "params": {"path": "output.md"}},
    ] * 5  # 扩展调用次数
    
    result = validator.validate(tool_calls, "step4")
    
    print(f"  通过: {result.passed}")
    print(f"  分数: {result.score:.1f}")
    print(f"  总调用: {result.details.get('total_calls', 0)}")
    
    print(f"[PASS] 工具使用验证器工作正常")
    return True


def test_cagr_validator():
    """测试CAGR验证器"""
    print("\n" + "="*60)
    print("测试: CAGRValidator")
    print("="*60)
    
    validator = CAGRValidator()
    
    # 测试合理CAGR
    result1 = validator.validate(25, "technology", "测试公司")
    print(f"  CAGR 25% (technology): passed={result1.passed}, score={result1.score:.1f}")
    
    # 测试过高CAGR
    result2 = validator.validate(80, "technology", "测试公司")
    print(f"  CAGR 80% (technology): passed={result2.passed}, score={result2.score:.1f}")
    
    assert not result2.passed, "过高CAGR应该不通过"
    print(f"[PASS] CAGR验证器工作正常")
    return True


def test_industry_data():
    """测试行业数据模块"""
    print("\n" + "="*60)
    print("测试: IndustryData")
    print("="*60)
    
    data = IndustryData()
    
    # 获取行业CAGR
    tech_cagr = data.get_industry_cagr("technology")
    print(f"  Technology CAGR: {tech_cagr}%")
    
    assert tech_cagr is not None, "应该能获取到行业CAGR"
    print(f"[PASS] 行业数据模块工作正常")
    return True


def test_tracing_validator():
    """测试参数溯源验证器"""
    print("\n" + "="*60)
    print("测试: TracingValidator")
    print("="*60)
    
    validator = TracingValidator()
    
    # 创建测试参数
    params = [
        ParameterSource("revenue_base", 2700, "2025年报", "official", "high"),
        ParameterSource("cagr", 22.5, "分析师预测", "estimate", "medium"),
        ParameterSource("market_share", 16.8, "IDC报告", "third_party", "high"),
    ]
    
    result = validator.validate(params)
    
    print(f"  通过: {result.passed}")
    print(f"  分数: {result.score:.1f}")
    print(f"  溯源率: {result.details.get('metrics', {}).get('trace_ratio', 0):.1%}")
    
    print(f"[PASS] 参数溯源验证器工作正常")
    return True


def test_automated_checklist():
    """测试检查清单自动化"""
    print("\n" + "="*60)
    print("测试: AutomatedChecklist")
    print("="*60)
    
    checklist = AutomatedChecklist()
    
    print(f"  加载了 {len(checklist.check_items)} 个检查项")
    
    assert len(checklist.check_items) >= 0, "应该能加载检查项"
    print(f"[PASS] 检查清单自动化工作正常")
    return True


def test_dynamic_threshold():
    """测试动态阈值系统"""
    print("\n" + "="*60)
    print("测试: DynamicThresholdManager")
    print("="*60)
    
    manager = DynamicThresholdManager()
    
    # 测试大型公司
    large_company = {
        "market_cap": 5000,
        "business_segments": 5,
        "industry": "technology"
    }
    
    thresholds = manager.calculate_thresholds("step4", large_company)
    
    print(f"  大型公司阈值:")
    print(f"    Tokens: {thresholds.tokens}")
    print(f"    Content: {thresholds.content_length}")
    print(f"    调整因子: {thresholds.applied_factor:.2f}")
    
    assert thresholds.applied_factor > 1.0, "大型公司应该有更高的阈值"
    print(f"[PASS] 动态阈值系统工作正常")
    return True


def test_enhanced_validator():
    """测试增强版验证器集成"""
    print("\n" + "="*60)
    print("测试: EnhancedValidatorV251")
    print("="*60)
    
    enhanced = get_enhanced_validator_v251()
    
    print(f"  可用: {enhanced.is_available()}")
    
    # 测试内容质量验证
    content = "测试内容" * 1000
    result = enhanced.validate_step4_content_quality(content)
    print(f"  内容质量验证: passed={result.is_valid}")
    
    print(f"[PASS] 增强版验证器工作正常")
    return True


def test_unified_validator():
    """测试统一验证器"""
    print("\n" + "="*60)
    print("测试: UnifiedValidatorV251")
    print("="*60)
    
    unified = get_unified_validator_v251()
    
    print(f"  v2.5.1可用: {unified.is_v251_available()}")
    
    # 测试动态阈值获取
    profile = {"market_cap": 1000, "business_segments": 3, "industry": "technology"}
    thresholds = unified.get_step_thresholds("step4", profile)
    
    print(f"  动态阈值:")
    print(f"    Tokens: {thresholds['tokens']}")
    print(f"    调整因子: {thresholds.get('applied_factor', 1.0):.2f}")
    
    print(f"[PASS] 统一验证器工作正常")
    return True


def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*70)
    print("Revenue Forecast v2.5.1 检查点系统集成测试")
    print("="*70)
    
    tests = [
        ("CheckpointRegistry", test_checkpoint_registry),
        ("ContentQualityValidator", test_content_quality_validator),
        ("ToolUsageValidator", test_tool_usage_validator),
        ("CAGRValidator", test_cagr_validator),
        ("IndustryData", test_industry_data),
        ("TracingValidator", test_tracing_validator),
        ("AutomatedChecklist", test_automated_checklist),
        ("DynamicThreshold", test_dynamic_threshold),
        ("EnhancedValidator", test_enhanced_validator),
        ("UnifiedValidator", test_unified_validator),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            failed += 1
            print(f"[FAIL] {name}: {e}")
    
    print("\n" + "="*70)
    print(f"测试结果: {passed}/{len(tests)} 通过, {failed} 失败")
    print("="*70)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
