"""
Revenue Forecast - 内容质量验证器 v2.5.1
版本: v1.0
创建日期: 2026-03-01

功能:
1. 信息密度分析（数据点数量）
2. 内容冗余度检测
3. 数据新鲜度评估
4. 结构层次评估
5. 综合质量评分
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
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from checkpoint_registry import CheckpointResult, ValidationContext, CheckpointConfig


@dataclass
class ContentQualityMetrics:
    """内容质量指标"""
    # 基础指标
    char_count: int = 0
    line_count: int = 0
    
    # 数据指标
    data_points: int = 0
    numeric_values: int = 0
    percentage_values: int = 0
    currency_values: int = 0
    cagr_mentions: int = 0
    year_mentions: int = 0
    
    # 结构指标
    h1_count: int = 0
    h2_count: int = 0
    h3_count: int = 0
    list_items: int = 0
    table_rows: int = 0
    
    # 质量指标
    redundancy_score: float = 0.0  # 0-1, 越低越好
    freshness_score: float = 0.0   # 0-1, 越高越好
    citation_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "char_count": self.char_count,
            "line_count": self.line_count,
            "data_points": self.data_points,
            "numeric_values": self.numeric_values,
            "percentage_values": self.percentage_values,
            "currency_values": self.currency_values,
            "cagr_mentions": self.cagr_mentions,
            "year_mentions": self.year_mentions,
            "h1_count": self.h1_count,
            "h2_count": self.h2_count,
            "h3_count": self.h3_count,
            "list_items": self.list_items,
            "table_rows": self.table_rows,
            "redundancy_score": round(self.redundancy_score, 2),
            "freshness_score": round(self.freshness_score, 2),
            "citation_count": self.citation_count
        }


class ContentQualityValidator:
    """
    内容质量验证器
    
    不仅检查字符数，还检查信息密度、质量、结构等多维度指标
    """
    
    # 默认阈值配置
    DEFAULT_THRESHOLDS = {
        "step4": {
            "min_chars": 5000,
            "min_data_points": 20,
            "min_cagr_mentions": 2,
            "min_h2_sections": 5,
            "max_redundancy": 0.3,
            "min_freshness": 0.6,
            "min_citations": 3
        },
        "step5": {
            "min_chars": 3000,
            "min_data_points": 15,
            "min_cagr_mentions": 1,
            "min_h2_sections": 3,
            "max_redundancy": 0.35,
            "min_freshness": 0.5,
            "min_citations": 2
        },
        "step6": {
            "min_chars": 2000,
            "min_data_points": 10,
            "min_h2_sections": 2,
            "max_redundancy": 0.4,
            "min_freshness": 0.5
        }
    }
    
    def __init__(self, thresholds: Optional[Dict[str, Any]] = None):
        """
        初始化验证器
        
        Args:
            thresholds: 自定义阈值配置
        """
        self.thresholds = thresholds or self.DEFAULT_THRESHOLDS
        self.current_year = datetime.now().year
    
    def validate(self, content: str, step_id: str, context: Optional[ValidationContext] = None) -> CheckpointResult:
        """
        验证内容质量
        
        Args:
            content: 待验证内容
            step_id: 步骤ID
            context: 验证上下文（可选）
            
        Returns:
            CheckpointResult: 验证结果
        """
        # 获取阈值
        step_thresholds = self.thresholds.get(step_id, self.thresholds.get("step4", {}))
        
        # 计算指标
        metrics = self._calculate_metrics(content)
        
        # 执行各项验证
        checks = []
        
        # 1. 字符数检查
        if "min_chars" in step_thresholds:
            passed = metrics.char_count >= step_thresholds["min_chars"]
            checks.append(("字符数", passed, metrics.char_count, step_thresholds["min_chars"]))
        
        # 2. 数据点检查
        if "min_data_points" in step_thresholds:
            passed = metrics.data_points >= step_thresholds["min_data_points"]
            checks.append(("数据点", passed, metrics.data_points, step_thresholds["min_data_points"]))
        
        # 3. CAGR提及检查
        if "min_cagr_mentions" in step_thresholds:
            passed = metrics.cagr_mentions >= step_thresholds["min_cagr_mentions"]
            checks.append(("CAGR提及", passed, metrics.cagr_mentions, step_thresholds["min_cagr_mentions"]))
        
        # 4. 结构层次检查
        if "min_h2_sections" in step_thresholds:
            passed = metrics.h2_count >= step_thresholds["min_h2_sections"]
            checks.append(("H2章节", passed, metrics.h2_count, step_thresholds["min_h2_sections"]))
        
        # 5. 冗余度检查
        if "max_redundancy" in step_thresholds:
            passed = metrics.redundancy_score <= step_thresholds["max_redundancy"]
            checks.append(("冗余度", passed, metrics.redundancy_score, step_thresholds["max_redundancy"]))
        
        # 6. 新鲜度检查
        if "min_freshness" in step_thresholds:
            passed = metrics.freshness_score >= step_thresholds["min_freshness"]
            checks.append(("数据新鲜度", passed, metrics.freshness_score, step_thresholds["min_freshness"]))
        
        # 7. 引用检查
        if "min_citations" in step_thresholds:
            passed = metrics.citation_count >= step_thresholds["min_citations"]
            checks.append(("引用数", passed, metrics.citation_count, step_thresholds["min_citations"]))
        
        # 计算总分
        total_checks = len(checks)
        passed_checks = sum(1 for _, passed, _, _ in checks if passed)
        score = (passed_checks / total_checks * 100) if total_checks > 0 else 0
        
        # 判断是否通过（所有硬性检查必须通过）
        all_passed = all(passed for _, passed, _, _ in checks)
        
        # 生成结果
        errors = []
        warnings = []
        suggestions = []
        
        for check_name, passed, actual, threshold in checks:
            if not passed:
                if check_name in ["字符数", "数据点", "H2章节"]:
                    errors.append(f"{check_name}不足: {actual} < {threshold}")
                else:
                    warnings.append(f"{check_name}不达标: {actual} (要求: {threshold})")
                
                # 生成改进建议
                suggestion = self._generate_suggestion(check_name, actual, threshold)
                if suggestion:
                    suggestions.append(suggestion)
        
        # 额外建议
        if metrics.redundancy_score > 0.2:
            suggestions.append(f"内容冗余度为{metrics.redundancy_score:.1%}，建议精简重复表述")
        
        if metrics.freshness_score < 0.7:
            suggestions.append(f"数据新鲜度为{metrics.freshness_score:.1%}，建议补充最新数据")
        
        if metrics.citation_count < 3:
            suggestions.append("引用来源较少，建议增加数据溯源")
        
        return CheckpointResult(
            checkpoint_id=f"{step_id}_content_quality",
            passed=all_passed,
            score=score,
            message=f"内容质量评分: {score:.1f}/100 ({passed_checks}/{total_checks}项通过)",
            details=metrics.to_dict(),
            errors=errors,
            warnings=warnings,
            suggestions=suggestions
        )
    
    def _calculate_metrics(self, content: str) -> ContentQualityMetrics:
        """计算内容质量指标"""
        metrics = ContentQualityMetrics()
        
        # 基础指标
        metrics.char_count = len(content)
        metrics.line_count = len(content.split('\n'))
        
        # 数据点统计
        # 金额（亿元、万元、元）
        currency_pattern = r'\d+\.?\d*\s*[亿元万元]'
        metrics.currency_values = len(re.findall(currency_pattern, content))
        
        # 百分比
        percentage_pattern = r'\d+\.?\d*%'
        metrics.percentage_values = len(re.findall(percentage_pattern, content))
        
        # CAGR提及
        cagr_pattern = r'CAGR|cagr|复合.*增长'
        metrics.cagr_mentions = len(re.findall(cagr_pattern, content))
        
        # 年份提及
        year_pattern = r'20\d{2}'
        years = [int(y) for y in re.findall(year_pattern, content)]
        metrics.year_mentions = len(years)
        
        # 数字值（简单统计）
        numeric_pattern = r'\d+\.?\d*'
        metrics.numeric_values = len(re.findall(numeric_pattern, content))
        
        # 综合数据点 = 金额 + 百分比 + CAGR + 年份
        metrics.data_points = metrics.currency_values + metrics.percentage_values + metrics.cagr_mentions + metrics.year_mentions
        
        # 结构指标
        metrics.h1_count = len(re.findall(r'^#\s+', content, re.MULTILINE))
        metrics.h2_count = len(re.findall(r'^##\s+', content, re.MULTILINE))
        metrics.h3_count = len(re.findall(r'^###\s+', content, re.MULTILINE))
        
        # 列表项
        metrics.list_items = len(re.findall(r'^\s*[-*]\s+', content, re.MULTILINE))
        
        # 表格行（简化估计）
        metrics.table_rows = content.count('|')
        
        # 质量指标
        metrics.redundancy_score = self._calculate_redundancy(content)
        metrics.freshness_score = self._calculate_freshness(years)
        metrics.citation_count = self._count_citations(content)
        
        return metrics
    
    def _calculate_redundancy(self, content: str) -> float:
        """计算内容冗余度 (0-1, 越低越好)"""
        # 提取句子（按句号、问号、感叹号分割）
        sentences = [s.strip() for s in re.split(r'[。!?！？]', content) if len(s.strip()) > 15]
        
        if len(sentences) < 2:
            return 0.0
        
        # 计算句子间相似度（简化版：计算公共子串长度比例）
        redundant_count = 0
        similarity_threshold = 0.6
        
        for i, s1 in enumerate(sentences):
            for s2 in sentences[i+1:]:
                similarity = self._sentence_similarity(s1, s2)
                if similarity > similarity_threshold:
                    redundant_count += 1
                    break  # 每个句子只计算一次冗余
        
        return redundant_count / len(sentences)
    
    def _sentence_similarity(self, s1: str, s2: str) -> float:
        """计算两个句子的相似度（简化版）"""
        # 使用字符级别的最长公共子序列（LCS）
        if not s1 or not s2:
            return 0.0
        
        # 提取关键词（去除停用词）
        stop_words = set(['的', '了', '是', '在', '有', '和', '与', '或', '为', '对'])
        words1 = [w for w in s1 if w not in stop_words]
        words2 = [w for w in s2 if w not in stop_words]
        
        if not words1 or not words2:
            return 0.0
        
        # 计算Jaccard相似度
        set1 = set(words1)
        set2 = set(words2)
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_freshness(self, years: List[int]) -> float:
        """计算数据新鲜度 (0-1, 越高越好)"""
        if not years:
            return 0.5  # 没有年份数据，给中等评分
        
        # 计算平均数据年龄
        current_year = self.current_year
        ages = [current_year - y for y in years if y <= current_year and y > 2000]
        
        if not ages:
            return 0.5
        
        avg_age = sum(ages) / len(ages)
        
        # 新鲜度计算：3年内为1.0，每增加1年降低0.1，最低0.3
        freshness = max(0.3, 1.0 - (avg_age - 3) * 0.1)
        
        return min(1.0, freshness)
    
    def _count_citations(self, content: str) -> int:
        """统计引用/来源数量"""
        citation_patterns = [
            r'来源[：:]',
            r'据.*报道',
            r'根据.*数据',
            r'引用.*',
            r'参考.*',
            r'详见.*',
            r'[（(]\d{4}[）)]',  # 年份引用
        ]
        
        count = 0
        for pattern in citation_patterns:
            count += len(re.findall(pattern, content))
        
        return count
    
    def _generate_suggestion(self, check_name: str, actual: Any, threshold: Any) -> str:
        """生成改进建议"""
        suggestions = {
            "字符数": f"建议扩展分析内容，至少达到{threshold}字符",
            "数据点": f"建议增加更多数据支撑（金额、百分比、CAGR等）",
            "CAGR提及": f"建议明确分析CAGR增长预期",
            "H2章节": f"建议使用更多二级标题(##)组织内容",
            "冗余度": f"建议精简重复表述，提高信息密度",
            "数据新鲜度": f"建议补充{self.current_year-2}-{self.current_year}年的最新数据",
            "引用数": f"建议增加数据来源引用，提高可信度"
        }
        return suggestions.get(check_name, "")
    
    def quick_check(self, content: str, step_id: str = "step4") -> Dict[str, Any]:
        """
        快速检查 - 返回简化结果
        
        用于实时监控，性能优先
        """
        metrics = self._calculate_metrics(content)
        thresholds = self.thresholds.get(step_id, self.thresholds.get("step4", {}))
        
        # 只检查最关键的3项
        checks = {
            "chars": metrics.char_count >= thresholds.get("min_chars", 5000),
            "data_points": metrics.data_points >= thresholds.get("min_data_points", 20),
            "structure": metrics.h2_count >= thresholds.get("min_h2_sections", 5)
        }
        
        return {
            "passed": all(checks.values()),
            "checks": checks,
            "metrics": {
                "chars": metrics.char_count,
                "data_points": metrics.data_points,
                "h2_count": metrics.h2_count
            }
        }


# 便捷的验证函数
def validate_content_quality(content: str, step_id: str, thresholds: Optional[Dict[str, Any]] = None) -> CheckpointResult:
    """
    便捷函数：验证内容质量
    
    Args:
        content: 待验证内容
        step_id: 步骤ID
        thresholds: 自定义阈值
        
    Returns:
        CheckpointResult: 验证结果
    """
    validator = ContentQualityValidator(thresholds)
    return validator.validate(content, step_id)


def quick_quality_check(content: str, step_id: str = "step4") -> Dict[str, Any]:
    """
    便捷函数：快速质量检查
    
    Args:
        content: 待验证内容
        step_id: 步骤ID
        
    Returns:
        Dict: 简化检查结果
    """
    validator = ContentQualityValidator()
    return validator.quick_check(content, step_id)


if __name__ == "__main__":
    # 测试
    print("=" * 60)
    print("ContentQualityValidator 测试")
    print("=" * 60)
    
    # 测试高质量内容
    good_content = """
# 市场分析

## 市场规模
2026年中国智能手机市场规模达到3.5万亿元，同比增长8.5%（来源：IDC 2026Q1报告）。
预计2027-2031年CAGR为5-7%，主要受益于5G换机潮和高端化趋势。

## 竞争格局
小米集团2026年市场份额为16.8%，位居第二，仅次于苹果（23.5%）。
相比2025年的15.2%，增长了1.6个百分点。

## 增长驱动
1. 高端化：均价从1200元提升至1500元，涨幅25%
2. 海外扩张：欧洲市场增长35%，拉美增长28%
3. 生态协同：IoT设备连接数达7亿+

## 财务预测
预计2027年营收3,900亿元，同比增长22%；
2028年营收4,700亿元，同比增长21%；
2029年营收5,700亿元，同比增长21%。
CAGR 22.5%。

## 风险提示
1. 市场竞争加剧（来源：公司年报）
2. 地缘政治风险
3. 技术迭代风险
"""
    
    validator = ContentQualityValidator()
    
    print("\n高质量内容测试:")
    result = validator.validate(good_content, "step4")
    print(f"  通过: {result.passed}")
    print(f"  分数: {result.score:.1f}")
    print(f"  消息: {result.message}")
    print(f"  详细指标:")
    for k, v in result.details.items():
        print(f"    {k}: {v}")
    
    # 测试低质量内容
    bad_content = """
市场很大，公司很好。
未来会增长，前景很光明。
公司发展很快。
市场竞争很激烈。
"""
    
    print("\n低质量内容测试:")
    result = validator.validate(bad_content, "step4")
    print(f"  通过: {result.passed}")
    print(f"  分数: {result.score:.1f}")
    print(f"  错误: {result.errors}")
    print(f"  建议: {result.suggestions[:2]}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
