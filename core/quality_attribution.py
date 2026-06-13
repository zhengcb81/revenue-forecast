"""
Revenue Forecast - 质量归因分析器 v2.5.1
版本: v1.0
创建日期: 2026-03-01

功能:
1. 质量问题根因分析
2. 归因聚类
3. 改进建议生成
4. 修复时间预估
"""

# v2.6.0 统一 UTF-8 编码引导（避免 Windows cp936/gbk 中文乱码）
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
try:
    from core.encoding import setup_utf8_console as _setup_utf8_console
    _setup_utf8_console()
except Exception:
    pass

import os
import sys
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from checkpoint_registry import CheckpointResult


@dataclass
class RootCause:
    """根因分析结果"""
    issue: str                    # 问题描述
    root_cause: str              # 根本原因
    evidence: str                # 证据
    solution: str                # 解决方案
    prevention: str              # 预防措施
    estimated_fix_time: int = 10  # 预估修复时间（分钟）
    priority: str = "medium"      # 优先级


@dataclass
class ImprovementRoadmap:
    """改进行动路线图"""
    immediate_actions: List[Dict]    # 立即执行
    short_term_actions: List[Dict]   # 短期（本周）
    long_term_actions: List[Dict]    # 长期（本月）
    estimated_total_time: int = 0    # 总预估时间


class QualityAttributionAnalyzer:
    """
    质量归因分析器
    
    分析质量问题的根本原因，生成改进方案
    """
    
    # 归因规则库
    ATTRIBUTION_RULES = {
        # 内容相关问题
        "content_insufficient": {
            "causes": [
                {
                    "condition": lambda ctx: ctx.get("tool_calls", 0) < 10,
                    "cause": "信息收集不充分",
                    "solution": "增加深度搜索，获取更多行业数据和市场信息",
                    "prevention": "设定最低搜索次数要求",
                    "fix_time": 15
                },
                {
                    "condition": lambda ctx: ctx.get("token_usage", 0) < 5000,
                    "cause": "分析深度不够",
                    "solution": "扩展分析维度，深入每个要点，增加细节",
                    "prevention": "使用结构化分析模板",
                    "fix_time": 20
                },
                {
                    "condition": lambda ctx: ctx.get("content_redundancy", 0) > 0.3,
                    "cause": "内容冗余或跑题",
                    "solution": "精简内容，聚焦关键信息，删除重复表述",
                    "prevention": "实时信息密度检测",
                    "fix_time": 10
                }
            ],
            "default": {
                "cause": "内容产出不足",
                "solution": "重新审视分析框架，确保覆盖所有关键维度",
                "prevention": "使用检查清单确保完整性",
                "fix_time": 15
            }
        },
        
        # CAGR相关问题
        "cagr_unreasonable": {
            "causes": [
                {
                    "condition": lambda ctx: ctx.get("vs_industry_multiple", 1) > 3,
                    "cause": "增长假设过于乐观",
                    "solution": "参考行业平均增速，重新评估市场空间和竞争格局",
                    "prevention": "使用CAGR合理性检查工具",
                    "fix_time": 20
                },
                {
                    "condition": lambda ctx: abs(ctx.get("vs_historical_diff", 0)) > 15,
                    "cause": "未充分考虑历史趋势",
                    "solution": "分析增长加速/减速的驱动因素，提供合理解释",
                    "prevention": "对比历史CAGR",
                    "fix_time": 15
                },
                {
                    "condition": lambda ctx: ctx.get("cagr", 0) > 50,
                    "cause": "爆发式增长缺乏支撑",
                    "solution": "详细论证市场份额获取计划和竞争优势",
                    "prevention": "高CAGR强制论证要求",
                    "fix_time": 30
                }
            ],
            "default": {
                "cause": "CAGR预测不合理",
                "solution": "重新审视关键假设，参考同业数据",
                "prevention": "CAGR合理性实时验证",
                "fix_time": 20
            }
        },
        
        # 溯源相关问题
        "tracing_incomplete": {
            "causes": [
                {
                    "condition": lambda ctx: ctx.get("critical_missing", []),
                    "cause": "关键参数缺少溯源",
                    "solution": "为revenue_base, cagr等关键参数添加来源",
                    "prevention": "强制关键参数溯源",
                    "fix_time": 10
                },
                {
                    "condition": lambda ctx: ctx.get("trace_ratio", 0) < 0.5,
                    "cause": "整体溯源意识不足",
                    "solution": "系统性添加数据来源，优先高置信度来源",
                    "prevention": "溯源实时提醒",
                    "fix_time": 25
                }
            ],
            "default": {
                "cause": "参数溯源不完整",
                "solution": "补充数据来源，提高可信度",
                "prevention": "80%溯源覆盖率检查",
                "fix_time": 15
            }
        },
        
        # 工具使用问题
        "tool_usage_suboptimal": {
            "causes": [
                {
                    "condition": lambda ctx: ctx.get("search_ratio", 0) > 0.9,
                    "cause": "过度依赖搜索，缺乏整理",
                    "solution": "减少搜索，增加文件写入，整理已有信息",
                    "prevention": "搜索/写入比例监控",
                    "fix_time": 10
                },
                {
                    "condition": lambda ctx: ctx.get("unique_sources", 0) < 3,
                    "cause": "数据来源单一",
                    "solution": "拓展信息来源，使用多元化数据源",
                    "prevention": "数据源多样性检查",
                    "fix_time": 15
                }
            ],
            "default": {
                "cause": "工具使用效率低",
                "solution": "优化工具使用策略",
                "prevention": "工具使用模式分析",
                "fix_time": 10
            }
        },
        
        # 一致性问题
        "consistency_error": {
            "causes": [
                {
                    "condition": lambda ctx: ctx.get("scenario_logic_error", False),
                    "cause": "情景分析逻辑错误",
                    "solution": "修正情景顺序，确保乐观>=基准>=悲观",
                    "prevention": "情景逻辑自动检查",
                    "fix_time": 5
                },
                {
                    "condition": lambda ctx: ctx.get("json_md_mismatch", False),
                    "cause": "JSON和Markdown不同步",
                    "solution": "统一数据源，重新生成报告",
                    "prevention": "数据一致性验证",
                    "fix_time": 10
                }
            ],
            "default": {
                "cause": "数据不一致",
                "solution": "检查并修正数据差异",
                "prevention": "一致性自动验证",
                "fix_time": 10
            }
        }
    }
    
    def __init__(self):
        """初始化质量归因分析器"""
        pass
    
    def analyze(self, checkpoint_results: List[CheckpointResult], 
                context: Dict[str, Any]) -> Dict:
        """
        分析质量问题
        
        Args:
            checkpoint_results: 检查点结果列表
            context: 分析上下文数据
            
        Returns:
            Dict: 分析结果
        """
        # 收集失败的检查点
        failures = [r for r in checkpoint_results if not r.passed]
        
        if not failures:
            return {
                "has_issues": False,
                "message": "未发现质量问题",
                "root_causes": [],
                "roadmap": None
            }
        
        # 分析每个失败
        root_causes = []
        for failure in failures:
            causes = self._analyze_failure(failure, context)
            root_causes.extend(causes)
        
        # 聚类相似问题
        clustered = self._cluster_issues(root_causes)
        
        # 生成改进路线图
        roadmap = self._generate_roadmap(root_causes)
        
        return {
            "has_issues": True,
            "total_issues": len(failures),
            "unique_causes": len(clustered),
            "root_causes": [self._root_cause_to_dict(rc) for rc in root_causes],
            "clustered_issues": clustered,
            "roadmap": self._roadmap_to_dict(roadmap),
            "estimated_total_time": roadmap.estimated_total_time
        }
    
    def _analyze_failure(self, failure: CheckpointResult, 
                        context: Dict) -> List[RootCause]:
        """分析单个失败"""
        causes = []
        
        # 根据检查点ID匹配规则
        checkpoint_id = failure.checkpoint_id
        
        # 匹配规则
        matched_rules = []
        if "content_quality" in checkpoint_id or "content_depth" in checkpoint_id:
            matched_rules.append("content_insufficient")
        if "cagr" in checkpoint_id:
            matched_rules.append("cagr_unreasonable")
        if "tracing" in checkpoint_id:
            matched_rules.append("tracing_incomplete")
        if "tool_usage" in checkpoint_id:
            matched_rules.append("tool_usage_suboptimal")
        if "consistency" in checkpoint_id:
            matched_rules.append("consistency_error")
        
        # 应用规则
        for rule_key in matched_rules:
            if rule_key in self.ATTRIBUTION_RULES:
                rule = self.ATTRIBUTION_RULES[rule_key]
                
                # 检查条件
                matched = False
                for cause_config in rule.get("causes", []):
                    try:
                        if cause_config["condition"](context):
                            causes.append(RootCause(
                                issue=failure.message,
                                root_cause=cause_config["cause"],
                                evidence=self._extract_evidence(failure, context),
                                solution=cause_config["solution"],
                                prevention=cause_config["prevention"],
                                estimated_fix_time=cause_config.get("fix_time", 15)
                            ))
                            matched = True
                            break
                    except:
                        pass
                
                # 如果没有匹配到，使用默认值
                if not matched:
                    default = rule.get("default", {})
                    causes.append(RootCause(
                        issue=failure.message,
                        root_cause=default.get("cause", "未知原因"),
                        evidence="未找到具体证据",
                        solution=default.get("solution", "需要进一步分析"),
                        prevention=default.get("prevention", "加强检查"),
                        estimated_fix_time=default.get("fix_time", 15)
                    ))
        
        if not causes:
            # 未匹配到任何规则
            causes.append(RootCause(
                issue=failure.message,
                root_cause="需要进一步分析",
                evidence=f"检查点: {checkpoint_id}",
                solution="查看详细错误信息，针对性修复",
                prevention="完善检查规则",
                estimated_fix_time=15
            ))
        
        return causes
    
    def _extract_evidence(self, failure: CheckpointResult, 
                         context: Dict) -> str:
        """提取证据"""
        evidence_parts = []
        
        if failure.details:
            # 提取关键指标
            for key in ["score", "trace_ratio", "token_efficiency", "redundancy"]:
                if key in failure.details:
                    evidence_parts.append(f"{key}={failure.details[key]}")
        
        # 添加上下文证据
        if "token_usage" in context:
            evidence_parts.append(f"tokens={context['token_usage']}")
        if "tool_calls" in context:
            evidence_parts.append(f"tools={len(context['tool_calls'])}")
        
        return ", ".join(evidence_parts) if evidence_parts else "见详细信息"
    
    def _cluster_issues(self, root_causes: List[RootCause]) -> Dict[str, List[str]]:
        """聚类相似问题"""
        clusters = defaultdict(list)
        
        for cause in root_causes:
            # 按根本原因聚类
            clusters[cause.root_cause].append(cause.issue)
        
        return dict(clusters)
    
    def _generate_roadmap(self, root_causes: List[RootCause]) -> ImprovementRoadmap:
        """生成改进行动路线图"""
        roadmap = ImprovementRoadmap(
            immediate_actions=[],
            short_term_actions=[],
            long_term_actions=[]
        )
        
        # 按修复时间排序
        sorted_causes = sorted(root_causes, key=lambda c: c.estimated_fix_time)
        
        total_time = 0
        
        for cause in sorted_causes:
            action = {
                "issue": cause.issue,
                "root_cause": cause.root_cause,
                "solution": cause.solution,
                "estimated_time": cause.estimated_fix_time
            }
            
            # 分类：<=10分钟立即，<=30分钟短期，>30分钟长期
            if cause.estimated_fix_time <= 10:
                roadmap.immediate_actions.append(action)
            elif cause.estimated_fix_time <= 30:
                roadmap.short_term_actions.append(action)
            else:
                roadmap.long_term_actions.append(action)
            
            total_time += cause.estimated_fix_time
        
        roadmap.estimated_total_time = total_time
        
        return roadmap
    
    def _root_cause_to_dict(self, rc: RootCause) -> Dict:
        """转换为字典"""
        return {
            "issue": rc.issue,
            "root_cause": rc.root_cause,
            "evidence": rc.evidence,
            "solution": rc.solution,
            "prevention": rc.prevention,
            "estimated_fix_time": rc.estimated_fix_time,
            "priority": rc.priority
        }
    
    def _roadmap_to_dict(self, roadmap: ImprovementRoadmap) -> Dict:
        """转换为字典"""
        return {
            "immediate_actions": roadmap.immediate_actions,
            "short_term_actions": roadmap.short_term_actions,
            "long_term_actions": roadmap.long_term_actions,
            "estimated_total_time": roadmap.estimated_total_time,
            "total_actions": (
                len(roadmap.immediate_actions) +
                len(roadmap.short_term_actions) +
                len(roadmap.long_term_actions)
            )
        }


# 便捷函数
def analyze_quality_issues(checkpoint_results: List[CheckpointResult], 
                          context: Dict) -> Dict:
    """便捷函数：分析质量问题"""
    analyzer = QualityAttributionAnalyzer()
    return analyzer.analyze(checkpoint_results, context)


if __name__ == "__main__":
    # 测试
    print("=" * 60)
    print("QualityAttributionAnalyzer 测试")
    print("=" * 60)
    
    analyzer = QualityAttributionAnalyzer()
    
    # 创建测试失败的检查点结果
    from checkpoint_registry import CheckpointResult
    
    test_failures = [
        CheckpointResult(
            checkpoint_id="step4_content_quality",
            passed=False,
            message="内容质量不足",
            details={"data_points": 5, "redundancy": 0.4}
        ),
        CheckpointResult(
            checkpoint_id="step7_cagr",
            passed=False,
            message="CAGR不合理"
        )
    ]
    
    test_context = {
        "tool_calls": ["search"] * 5,
        "token_usage": 3000,
        "content_redundancy": 0.4,
        "cagr": 80,
        "vs_industry_multiple": 6
    }
    
    print("\n测试质量归因分析:")
    result = analyzer.analyze(test_failures, test_context)
    
    print(f"  发现问题: {result['has_issues']}")
    print(f"  问题数量: {result['total_issues']}")
    print(f"  根因数量: {len(result['root_causes'])}")
    print(f"  预估总修复时间: {result['estimated_total_time']}分钟")
    
    print("\n根因分析:")
    for cause in result['root_causes'][:3]:
        print(f"  - {cause['root_cause']}: {cause['solution']}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
