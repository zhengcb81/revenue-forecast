"""
Revenue Forecast - 工具使用验证器 v2.5.1
版本: v1.0
创建日期: 2026-03-01

功能:
1. 工具类型细分验证（搜索/读取/写入）
2. 数据源多样性检查
3. 工具使用模式分析
4. 异常使用检测
"""

# v2.6.0 统一 UTF-8 编码引导（避免 Windows cp936/gbk 中文乱码）
import os as _os, sys as _sys
for _p in (_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))),
           _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))):
    if _p not in _sys.path:
        _sys.path.insert(0, _p)
try:
    from core.encoding import setup_utf8_console as _setup_utf8_console
    _setup_utf8_console()
except Exception:
    pass

import re
import os
import sys
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from checkpoint_registry import CheckpointResult, ValidationContext, CheckpointConfig


@dataclass
class ToolUsageMetrics:
    """工具使用指标"""
    total_calls: int = 0
    
    # 按类型统计
    web_search: int = 0
    file_read: int = 0
    file_write: int = 0
    file_edit: int = 0
    bash: int = 0
    other: int = 0
    
    # 数据源统计
    unique_sources: int = 0
    sources: Set[str] = field(default_factory=set)
    
    # 搜索深度
    search_pages: int = 0
    searches_with_pagination: int = 0
    
    # 时间分布
    first_call_time: Optional[float] = None
    last_call_time: Optional[float] = None
    
    # 异常指标
    repeated_searches: int = 0
    failed_calls: int = 0
    
    def to_dict(self) -> Dict:
        return {
            "total_calls": self.total_calls,
            "web_search": self.web_search,
            "file_read": self.file_read,
            "file_write": self.file_write,
            "file_edit": self.file_edit,
            "bash": self.bash,
            "other": self.other,
            "unique_sources": self.unique_sources,
            "sources": list(self.sources)[:10],  # 只保留前10个
            "search_pages": self.search_pages,
            "searches_with_pagination": self.searches_with_pagination,
            "repeated_searches": self.repeated_searches
        }


class ToolUsageValidator:
    """
    工具使用验证器
    
    不仅检查调用次数，还检查类型分布、数据源多样性等
    """
    
    # 步骤详细的工具要求配置
    STEP_TOOL_REQUIREMENTS = {
        "step4": {
            "total": 18,
            "min_by_type": {
                "web_search": 10,   # 至少10次搜索（获取最新信息）
                "file_read": 5,     # 至少5次读取（模块文档）
                "file_write": 3     # 至少3次写入（维度文件）
            },
            "quality_indicators": {
                "unique_sources": 5,        # 至少5个不同数据源
                "searches_with_pagination": 2,  # 至少2次深度搜索（翻页）
                "max_repeated_ratio": 0.3   # 重复搜索不超过30%
            }
        },
        "step5": {
            "total": 12,
            "min_by_type": {
                "web_search": 6,
                "file_read": 3,
                "file_write": 2
            },
            "quality_indicators": {
                "unique_sources": 3,
                "searches_with_pagination": 1,
                "max_repeated_ratio": 0.4
            }
        },
        "step6": {
            "total": 8,
            "min_by_type": {
                "web_search": 4,
                "file_read": 2,
                "file_write": 1
            },
            "quality_indicators": {
                "unique_sources": 2,
                "max_repeated_ratio": 0.5
            }
        }
    }
    
    def __init__(self, requirements: Optional[Dict] = None):
        """
        初始化验证器
        
        Args:
            requirements: 自定义工具要求配置
        """
        self.requirements = requirements or self.STEP_TOOL_REQUIREMENTS
    
    def validate(self, tool_calls: List[Dict], step_id: str, context: Optional[ValidationContext] = None) -> CheckpointResult:
        """
        验证工具使用情况
        
        Args:
            tool_calls: 工具调用列表
            step_id: 步骤ID
            context: 验证上下文（可选）
            
        Returns:
            CheckpointResult: 验证结果
        """
        # 获取要求
        requirements = self.requirements.get(step_id, self.requirements.get("step4", {}))
        
        # 计算指标
        metrics = self._calculate_metrics(tool_calls)
        
        # 执行各项验证
        checks = []
        errors = []
        warnings = []
        suggestions = []
        
        # 1. 总调用次数检查
        if "total" in requirements:
            passed = metrics.total_calls >= requirements["total"]
            checks.append(("总调用次数", passed, metrics.total_calls, requirements["total"]))
            if not passed:
                errors.append(f"工具调用次数不足: {metrics.total_calls} < {requirements['total']}")
                suggestions.append(f"建议增加工具调用，至少使用{requirements['total']}次")
        
        # 2. 各类型最小数量检查
        min_by_type = requirements.get("min_by_type", {})
        type_mapping = {
            "web_search": metrics.web_search,
            "file_read": metrics.file_read,
            "file_write": metrics.file_write
        }
        
        for tool_type, min_count in min_by_type.items():
            actual = type_mapping.get(tool_type, 0)
            passed = actual >= min_count
            checks.append((f"{tool_type}调用", passed, actual, min_count))
            if not passed:
                errors.append(f"{tool_type}调用不足: {actual} < {min_count}")
                suggestions.append(self._get_tool_suggestion(tool_type, min_count))
        
        # 3. 数据源多样性检查
        quality = requirements.get("quality_indicators", {})
        if "unique_sources" in quality:
            passed = metrics.unique_sources >= quality["unique_sources"]
            checks.append(("数据源多样性", passed, metrics.unique_sources, quality["unique_sources"]))
            if not passed:
                warnings.append(f"数据源不够多样: {metrics.unique_sources} < {quality['unique_sources']}")
                suggestions.append("建议从更多不同来源获取信息")
        
        # 4. 搜索深度检查
        if "searches_with_pagination" in quality:
            passed = metrics.searches_with_pagination >= quality["searches_with_pagination"]
            checks.append(("搜索深度", passed, metrics.searches_with_pagination, quality["searches_with_pagination"]))
            if not passed:
                warnings.append("搜索深度不足，建议查看更多搜索结果页面")
        
        # 5. 重复搜索检查
        if "max_repeated_ratio" in quality and metrics.total_calls > 0:
            repeated_ratio = metrics.repeated_searches / metrics.total_calls
            passed = repeated_ratio <= quality["max_repeated_ratio"]
            checks.append(("重复搜索比例", passed, f"{repeated_ratio:.1%}", f"<= {quality['max_repeated_ratio']:.0%}"))
            if not passed:
                warnings.append(f"重复搜索比例过高: {repeated_ratio:.1%}")
                suggestions.append("建议减少重复搜索，提高信息利用效率")
        
        # 计算分数
        total_checks = len(checks)
        passed_checks = sum(1 for _, passed, _, _ in checks if passed)
        score = (passed_checks / total_checks * 100) if total_checks > 0 else 0
        
        # 判断是否通过（所有硬性检查必须通过）
        all_passed = all(passed for _, passed, _, _ in checks)
        
        return CheckpointResult(
            checkpoint_id=f"{step_id}_tool_usage",
            passed=all_passed,
            score=score,
            message=f"工具使用评分: {score:.1f}/100 ({passed_checks}/{total_checks}项通过)",
            details=metrics.to_dict(),
            errors=errors,
            warnings=warnings,
            suggestions=suggestions
        )
    
    def _calculate_metrics(self, tool_calls: List[Dict]) -> ToolUsageMetrics:
        """计算工具使用指标"""
        metrics = ToolUsageMetrics()
        metrics.total_calls = len(tool_calls)
        
        if not tool_calls:
            return metrics
        
        # 记录搜索查询以检测重复
        search_queries = []
        
        for call in tool_calls:
            tool_type = call.get("type", "unknown")
            tool_name = call.get("name", "")
            params = call.get("params", {})
            
            # 分类统计
            if "search" in tool_name.lower() or tool_type == "web_search":
                metrics.web_search += 1
                
                # 记录搜索查询
                query = params.get("query", "")
                if query:
                    search_queries.append(query.lower())
                
                # 检测翻页
                if "page" in params or "offset" in params:
                    metrics.searches_with_pagination += 1
                    metrics.search_pages += 1
                    
            elif "read" in tool_name.lower() or tool_type == "file_read":
                metrics.file_read += 1
                
                # 记录数据源
                path = params.get("path", "")
                if path:
                    metrics.sources.add(path)
                    
            elif "write" in tool_name.lower() or tool_type == "file_write":
                metrics.file_write += 1
                
            elif "edit" in tool_name.lower() or tool_type == "file_edit":
                metrics.file_edit += 1
                
            elif "bash" in tool_name.lower() or tool_type == "bash":
                metrics.bash += 1
                
            else:
                metrics.other += 1
            
            # 检测失败调用
            if call.get("status") == "error" or call.get("error"):
                metrics.failed_calls += 1
        
        # 统计独特数据源
        metrics.unique_sources = len(metrics.sources)
        
        # 检测重复搜索
        query_counts = defaultdict(int)
        for query in search_queries:
            # 简化查询（去除标点、空格）
            simplified = re.sub(r'[^\w]', '', query)
            query_counts[simplified] += 1
        
        metrics.repeated_searches = sum(1 for count in query_counts.values() if count > 1)
        
        return metrics
    
    def _get_tool_suggestion(self, tool_type: str, min_count: int) -> str:
        """获取工具使用建议"""
        suggestions = {
            "web_search": f"建议增加深度搜索，获取更多行业和市场信息（至少{min_count}次）",
            "file_read": f"建议更多读取模块文档和参考资料（至少{min_count}次）",
            "file_write": f"建议及时保存分析结果到维度文件（至少{min_count}次）"
        }
        return suggestions.get(tool_type, f"建议增加{tool_type}的使用")
    
    def analyze_usage_pattern(self, tool_calls: List[Dict]) -> Dict:
        """
        分析工具使用模式
        
        用于提供优化建议
        """
        if not tool_calls:
            return {"pattern": "unknown", "suggestions": []}
        
        metrics = self._calculate_metrics(tool_calls)
        
        patterns = []
        suggestions = []
        
        # 模式1: 搜索过多型
        if metrics.web_search > metrics.total_calls * 0.8:
            patterns.append("search_heavy")
            suggestions.append("搜索比例过高，建议更多文件操作整理信息")
        
        # 模式2: 写入不足型
        if metrics.file_write < 3 and metrics.web_search > 10:
            patterns.append("low_output")
            suggestions.append("搜索多但产出少，建议及时保存分析结果")
        
        # 模式3: 深度不足型
        if metrics.searches_with_pagination == 0 and metrics.web_search > 5:
            patterns.append("shallow_search")
            suggestions.append("搜索未翻页，建议查看更多搜索结果")
        
        # 模式4: 单一来源型
        if metrics.unique_sources < 3 and metrics.web_search > 5:
            patterns.append("single_source")
            suggestions.append("数据来源较单一，建议多元化信息来源")
        
        # 模式5: 重复搜索型
        if metrics.repeated_searches > metrics.total_calls * 0.3:
            patterns.append("repetitive")
            suggestions.append("重复搜索较多，建议提高信息利用效率")
        
        # 理想模式
        if not patterns:
            patterns.append("balanced")
            suggestions.append("工具使用平衡，继续保持")
        
        return {
            "pattern": patterns[0] if patterns else "unknown",
            "all_patterns": patterns,
            "suggestions": suggestions,
            "metrics": metrics.to_dict()
        }
    
    def quick_check(self, tool_calls: List[Dict], step_id: str = "step4") -> Dict:
        """
        快速检查 - 返回简化结果
        
        用于实时监控
        """
        metrics = self._calculate_metrics(tool_calls)
        requirements = self.requirements.get(step_id, self.requirements.get("step4", {}))
        
        min_by_type = requirements.get("min_by_type", {})
        
        checks = {
            "total": metrics.total_calls >= requirements.get("total", 18),
            "web_search": metrics.web_search >= min_by_type.get("web_search", 10),
            "file_read": metrics.file_read >= min_by_type.get("file_read", 5),
            "file_write": metrics.file_write >= min_by_type.get("file_write", 3)
        }
        
        return {
            "passed": all(checks.values()),
            "checks": checks,
            "metrics": {
                "total": metrics.total_calls,
                "web_search": metrics.web_search,
                "file_read": metrics.file_read,
                "file_write": metrics.file_write
            }
        }


# 便捷的验证函数
def validate_tool_usage(tool_calls: List[Dict], step_id: str, requirements: Optional[Dict] = None) -> CheckpointResult:
    """
    便捷函数：验证工具使用
    
    Args:
        tool_calls: 工具调用列表
        step_id: 步骤ID
        requirements: 自定义要求
        
    Returns:
        CheckpointResult: 验证结果
    """
    validator = ToolUsageValidator(requirements)
    return validator.validate(tool_calls, step_id)


def analyze_tool_pattern(tool_calls: List[Dict]) -> Dict:
    """
    便捷函数：分析工具使用模式
    
    Args:
        tool_calls: 工具调用列表
        
    Returns:
        Dict: 分析结果
    """
    validator = ToolUsageValidator()
    return validator.analyze_usage_pattern(tool_calls)


if __name__ == "__main__":
    # 测试
    print("=" * 60)
    print("ToolUsageValidator 测试")
    print("=" * 60)
    
    # 模拟工具调用
    good_tool_calls = [
        {"type": "web_search", "name": "web_search", "params": {"query": "小米集团 2026年营收"}},
        {"type": "web_search", "name": "web_search", "params": {"query": "智能手机市场 2026 规模", "page": 2}},
        {"type": "web_search", "name": "web_search", "params": {"query": "小米 IoT业务增长"}},
        {"type": "web_search", "name": "web_search", "params": {"query": "小米汽车 SU7 销量"}},
        {"type": "web_search", "name": "web_search", "params": {"query": "小米高端手机市场份额"}},
        {"type": "file_read", "name": "read_file", "params": {"path": "modules/company-types/product-driven.md"}},
        {"type": "file_read", "name": "read_file", "params": {"path": "modules/scoring/scoring-framework.md"}},
        {"type": "file_write", "name": "write_file", "params": {"path": "dimension-1-market.md"}},
        {"type": "web_search", "name": "web_search", "params": {"query": "小米竞争对手 华为 苹果 OPPO"}},
        {"type": "web_search", "name": "web_search", "params": {"query": "中国智能手机 2027-2031 预测"}},
        {"type": "file_read", "name": "read_file", "params": {"path": "modules/analysis/research-dimensions.md"}},
        {"type": "file_write", "name": "write_file", "params": {"path": "dimension-2-competition.md"}},
        {"type": "web_search", "name": "web_search", "params": {"query": "小米生态链 投资版图"}},
        {"type": "file_write", "name": "write_file", "params": {"path": "dimension-3-product.md"}},
        {"type": "web_search", "name": "web_search", "params": {"query": "小米海外市场 欧洲 印度"}},
        {"type": "web_search", "name": "web_search", "params": {"query": "小米集团 财报 2026Q1", "page": 2}},
        {"type": "file_read", "name": "read_file", "params": {"path": "config.yaml"}},
        {"type": "file_write", "name": "write_file", "params": {"path": "dimension-4-revenue.md"}},
    ]
    
    validator = ToolUsageValidator()
    
    print("\n高质量工具使用测试:")
    result = validator.validate(good_tool_calls, "step4")
    print(f"  通过: {result.passed}")
    print(f"  分数: {result.score:.1f}")
    print(f"  消息: {result.message}")
    print(f"  详细指标:")
    for k, v in result.details.items():
        if isinstance(v, (int, str)):
            print(f"    {k}: {v}")
    
    # 分析使用模式
    print("\n使用模式分析:")
    pattern = validator.analyze_usage_pattern(good_tool_calls)
    print(f"  模式: {pattern['pattern']}")
    print(f"  建议: {pattern['suggestions']}")
    
    # 测试低质量工具使用
    bad_tool_calls = [
        {"type": "web_search", "name": "web_search", "params": {"query": "小米集团"}},
        {"type": "web_search", "name": "web_search", "params": {"query": "小米集团"}},  # 重复
        {"type": "web_search", "name": "web_search", "params": {"query": "小米集团"}},  # 重复
        {"type": "web_search", "name": "web_search", "params": {"query": "小米"}},
        {"type": "web_search", "name": "web_search", "params": {"query": "小米"}},  # 重复
    ]
    
    print("\n低质量工具使用测试:")
    result = validator.validate(bad_tool_calls, "step4")
    print(f"  通过: {result.passed}")
    print(f"  分数: {result.score:.1f}")
    print(f"  错误: {result.errors}")
    print(f"  警告: {result.warnings}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
