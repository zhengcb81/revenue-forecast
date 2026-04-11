"""
Revenue Forecast - 参数溯源验证器 v2.5.1
版本: v1.0
创建日期: 2026-03-01

功能:
1. 参数溯源完整性验证
2. 数据源质量评估
3. 关键参数强制溯源
4. 溯源覆盖率统计
"""

import re
import os
import sys
from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from checkpoint_registry import CheckpointResult, ValidationContext


@dataclass
class ParameterSource:
    """参数来源信息"""
    param_name: str
    value: Any
    source: str = ""
    source_type: str = "unknown"  # official, third_party, estimate, assumption
    confidence: str = "medium"    # high, medium, low
    url: str = ""
    timestamp: str = ""
    notes: str = ""
    
    def is_valid(self) -> bool:
        """检查溯源是否有效"""
        return bool(self.source) and self.source_type != "unknown"


@dataclass
class TracingMetrics:
    """溯源指标"""
    total_params: int = 0
    traced_params: int = 0
    critical_traced: int = 0
    high_confidence: int = 0
    medium_confidence: int = 0
    low_confidence: int = 0
    by_source_type: Dict[str, int] = field(default_factory=dict)
    
    @property
    def trace_ratio(self) -> float:
        return self.traced_params / max(self.total_params, 1)
    
    @property
    def critical_coverage(self) -> float:
        return self.critical_traced / max(len(TracingValidator.CRITICAL_PARAMS), 1)


class TracingValidator:
    """
    参数溯源验证器
    
    确保分析中使用的关键参数都有明确的来源
    """
    
    # 关键参数列表（必须溯源）
    CRITICAL_PARAMS = [
        "revenue_base",
        "revenue_2026",
        "cagr",
        "cagr_optimistic",
        "cagr_base",
        "cagr_pessimistic",
        "market_share",
        "market_growth_rate",
        "price_change",
        "penetration_rate",
        "capacity_utilization"
    ]
    
    # 溯源要求配置
    REQUIREMENTS = {
        "min_trace_ratio": 0.8,        # 至少80%参数需要溯源
        "critical_trace_ratio": 1.0,   # 关键参数必须100%溯源
        "min_high_confidence_ratio": 0.3,  # 至少30%高置信度
        "min_source_diversity": 2      # 至少2种不同类型的来源
    }
    
    # 来源类型可信度评分
    SOURCE_TYPE_SCORES = {
        "official": 1.0,       # 官方财报
        "regulatory": 0.95,    # 监管披露
        "third_party": 0.8,    # 第三方数据
        "industry_report": 0.75,  # 行业报告
        "expert": 0.7,         # 专家访谈
        "estimate": 0.5,       # 估算
        "assumption": 0.3      # 假设
    }
    
    def __init__(self, requirements: Optional[Dict] = None):
        """初始化验证器"""
        self.requirements = requirements or self.REQUIREMENTS
    
    def validate(self, parameters: List[ParameterSource], 
                 context: Optional[ValidationContext] = None) -> CheckpointResult:
        """
        验证参数溯源完整性
        
        Args:
            parameters: 参数列表
            context: 验证上下文
            
        Returns:
            CheckpointResult: 验证结果
        """
        # 计算指标
        metrics = self._calculate_metrics(parameters)
        
        # 执行验证
        checks = []
        errors = []
        warnings = []
        suggestions = []
        
        # 1. 总体溯源率检查
        min_ratio = self.requirements["min_trace_ratio"]
        passed = metrics.trace_ratio >= min_ratio
        checks.append(("总体溯源率", passed, f"{metrics.trace_ratio:.1%}", f">= {min_ratio:.0%}"))
        if not passed:
            errors.append(f"总体溯源率不足: {metrics.trace_ratio:.1%} < {min_ratio:.0%}")
            suggestions.append(f"建议为更多参数添加来源，至少达到{min_ratio:.0%}")
        
        # 2. 关键参数溯源检查
        critical_missing = self._get_critical_missing(parameters)
        passed = len(critical_missing) == 0
        checks.append(("关键参数溯源", passed, f"{metrics.critical_traced}/{len(self.CRITICAL_PARAMS)}", "100%"))
        if not passed:
            errors.append(f"关键参数缺少溯源: {', '.join(critical_missing)}")
            suggestions.append("以下关键参数必须提供来源: revenue_base, cagr, market_share等")
        
        # 3. 高置信度比例检查
        min_high_ratio = self.requirements["min_high_confidence_ratio"]
        high_ratio = metrics.high_confidence / max(metrics.total_params, 1)
        passed = high_ratio >= min_high_ratio
        checks.append(("高置信度比例", passed, f"{high_ratio:.1%}", f">= {min_high_ratio:.0%}"))
        if not passed:
            warnings.append(f"高置信度数据比例较低: {high_ratio:.1%}")
            suggestions.append("建议优先使用官方财报、监管披露等高可信度来源")
        
        # 4. 来源多样性检查
        min_diversity = self.requirements["min_source_diversity"]
        source_types = len(metrics.by_source_type)
        passed = source_types >= min_diversity
        checks.append(("来源多样性", passed, f"{source_types}种", f">= {min_diversity}种"))
        if not passed:
            warnings.append(f"数据来源类型较单一: 仅{source_types}种")
            suggestions.append("建议多元化数据来源，包括财报、行业报告、第三方数据等")
        
        # 计算分数
        passed_checks = sum(1 for _, passed, _, _ in checks if passed)
        score = (passed_checks / len(checks) * 100) if checks else 100
        
        all_passed = len(errors) == 0
        
        return CheckpointResult(
            checkpoint_id="global_tracing_completeness",
            passed=all_passed,
            score=score,
            message=f"参数溯源验证: {metrics.trace_ratio:.1%} ({metrics.traced_params}/{metrics.total_params})",
            details={
                "metrics": {
                    "total": metrics.total_params,
                    "traced": metrics.traced_params,
                    "trace_ratio": round(metrics.trace_ratio, 2),
                    "critical_traced": metrics.critical_traced,
                    "by_source_type": metrics.by_source_type
                },
                "critical_missing": critical_missing
            },
            errors=errors,
            warnings=warnings,
            suggestions=suggestions
        )
    
    def validate_report_tracing(self, json_data: Dict) -> CheckpointResult:
        """
        验证报告中的参数溯源
        
        从JSON报告中提取参数并验证溯源
        """
        parameters = self._extract_parameters_from_json(json_data)
        return self.validate(parameters)
    
    def _calculate_metrics(self, parameters: List[ParameterSource]) -> TracingMetrics:
        """计算溯源指标"""
        metrics = TracingMetrics()
        metrics.total_params = len(parameters)
        
        for param in parameters:
            if param.is_valid():
                metrics.traced_params += 1
                
                # 检查是否为关键参数
                if param.param_name in self.CRITICAL_PARAMS:
                    metrics.critical_traced += 1
                
                # 置信度统计
                if param.confidence == "high":
                    metrics.high_confidence += 1
                elif param.confidence == "medium":
                    metrics.medium_confidence += 1
                else:
                    metrics.low_confidence += 1
                
                # 来源类型统计
                source_type = param.source_type or "unknown"
                metrics.by_source_type[source_type] = metrics.by_source_type.get(source_type, 0) + 1
        
        return metrics
    
    def _get_critical_missing(self, parameters: List[ParameterSource]) -> List[str]:
        """获取缺少溯源的关键参数"""
        param_dict = {p.param_name: p for p in parameters}
        missing = []
        
        for critical in self.CRITICAL_PARAMS:
            if critical not in param_dict or not param_dict[critical].is_valid():
                missing.append(critical)
        
        return missing
    
    def _extract_parameters_from_json(self, json_data: Dict) -> List[ParameterSource]:
        """从JSON数据中提取参数"""
        parameters = []
        
        # 尝试从不同位置提取参数
        # 1. 顶层参数
        for key in ["revenue_base", "cagr", "market_share", "score"]:
            if key in json_data:
                param = ParameterSource(
                    param_name=key,
                    value=json_data[key],
                    source=json_data.get(f"{key}_source", ""),
                    source_type=json_data.get(f"{key}_source_type", "unknown")
                )
                parameters.append(param)
        
        # 2. key_metrics中的参数
        if "key_metrics" in json_data and isinstance(json_data["key_metrics"], dict):
            for key, value in json_data["key_metrics"].items():
                if isinstance(value, (int, float)):
                    param = ParameterSource(
                        param_name=key,
                        value=value,
                        source=json_data["key_metrics"].get(f"{key}_source", "")
                    )
                    parameters.append(param)
        
        # 3. scenario_analysis中的参数
        if "scenario_analysis" in json_data:
            for scenario in ["optimistic", "base", "pessimistic"]:
                if scenario in json_data["scenario_analysis"]:
                    scen_data = json_data["scenario_analysis"][scenario]
                    if "cagr" in scen_data:
                        param = ParameterSource(
                            param_name=f"cagr_{scenario}",
                            value=scen_data["cagr"],
                            source=scen_data.get("cagr_source", "")
                        )
                        parameters.append(param)
        
        # 4. parameter_tracing字段
        if "parameter_tracing" in json_data:
            for param_data in json_data["parameter_tracing"]:
                param = ParameterSource(
                    param_name=param_data.get("name", "unknown"),
                    value=param_data.get("value"),
                    source=param_data.get("source", ""),
                    source_type=param_data.get("source_type", "unknown"),
                    confidence=param_data.get("confidence", "medium"),
                    url=param_data.get("url", "")
                )
                parameters.append(param)
        
        return parameters
    
    def evaluate_source_quality(self, source_type: str, has_url: bool = False) -> float:
        """
        评估来源质量
        
        Returns:
            float: 质量评分 0-1
        """
        base_score = self.SOURCE_TYPE_SCORES.get(source_type, 0.5)
        
        # 有可验证URL加分
        if has_url and source_type in ["official", "regulatory", "third_party"]:
            base_score = min(1.0, base_score + 0.1)
        
        return base_score


# 便捷函数
def validate_tracing(parameters: List[ParameterSource]) -> CheckpointResult:
    """便捷函数：验证参数溯源"""
    validator = TracingValidator()
    return validator.validate(parameters)


def validate_report_tracing(json_data: Dict) -> CheckpointResult:
    """便捷函数：验证报告参数溯源"""
    validator = TracingValidator()
    return validator.validate_report_tracing(json_data)


if __name__ == "__main__":
    # 测试
    print("=" * 60)
    print("TracingValidator 测试")
    print("=" * 60)
    
    validator = TracingValidator()
    
    # 创建测试参数
    test_params = [
        ParameterSource("revenue_base", 2700, "2025年报", "official", "high"),
        ParameterSource("cagr", 22.5, "分析师预测", "estimate", "medium"),
        ParameterSource("market_share", 16.8, "IDC报告", "third_party", "high"),
        ParameterSource("growth_driver", "高端化", "", "unknown", "low"),  # 缺少来源
    ]
    
    print("\n测试参数溯源验证:")
    result = validator.validate(test_params)
    print(f"  通过: {result.passed}")
    print(f"  分数: {result.score:.1f}")
    print(f"  消息: {result.message}")
    print(f"  错误: {result.errors}")
    print(f"  建议: {result.suggestions}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
