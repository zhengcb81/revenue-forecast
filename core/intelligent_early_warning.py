"""
Revenue Forecast - 智能预警系统 v2.5.1
版本: v1.0
创建日期: 2026-03-01

功能:
1. 实时监控分析过程
2. 异常模式检测
3. 质量风险预测
4. 智能建议生成
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
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from checkpoint_registry import ValidationContext


class AlertLevel(Enum):
    """预警级别"""
    INFO = "info"         # 信息提示
    WARNING = "warning"   # 警告
    CRITICAL = "critical" # 严重


@dataclass
class Alert:
    """预警信息"""
    level: AlertLevel
    type: str
    message: str
    suggestion: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "level": self.level.value,
            "type": self.type,
            "message": self.message,
            "suggestion": self.suggestion,
            "timestamp": datetime.fromtimestamp(self.timestamp).isoformat(),
            "metadata": self.metadata
        }


@dataclass
class StepMetrics:
    """步骤执行指标"""
    step_id: str
    token_usage: int = 0
    content_length: int = 0
    tool_calls: List[Dict] = field(default_factory=list)
    content_redundancy: float = 0.0
    data_freshness: float = 0.0
    execution_time: float = 0.0
    
    @property
    def token_efficiency(self) -> float:
        """Token效率：每Token产出的字符数"""
        if self.token_usage == 0:
            return 0.0
        return self.content_length / self.token_usage
    
    @property
    def tool_call_count(self) -> int:
        return len(self.tool_calls)


class IntelligentEarlyWarning:
    """
    智能预警系统
    
    实时监控分析过程，提前发现问题
    """
    
    # 预警规则配置
    WARNING_RULES = {
        # Token效率相关
        "token_efficiency_low": {
            "condition": lambda m: m.token_efficiency < 0.3 and m.token_usage > 5000,
            "level": AlertLevel.WARNING,
            "message": "Token效率过低 ({efficiency:.2f} 字符/Token)",
            "suggestion": "可能存在过度思考，建议聚焦核心维度，避免发散"
        },
        "token_efficiency_very_low": {
            "condition": lambda m: m.token_efficiency < 0.15 and m.token_usage > 3000,
            "level": AlertLevel.CRITICAL,
            "message": "Token效率极低，分析可能陷入困境",
            "suggestion": "立即检查分析方向，考虑重新开始当前步骤"
        },
        
        # 工具使用相关
        "high_tools_low_output": {
            "condition": lambda m: m.tool_call_count > 20 and m.content_length < 2000,
            "level": AlertLevel.WARNING,
            "message": f"工具调用({0})多但产出({1})少，可能陷入信息陷阱",
            "suggestion": "建议暂停搜索，整理已有信息，开始写作"
        },
        "excessive_tools": {
            "condition": lambda m: m.tool_call_count > 30,
            "level": AlertLevel.INFO,
            "message": "工具调用次数较多，注意控制分析范围",
            "suggestion": "建议优先使用已有信息，避免过度搜索"
        },
        
        # 内容质量相关
        "high_redundancy": {
            "condition": lambda m: m.content_redundancy > 0.3,
            "level": AlertLevel.WARNING,
            "message": "内容冗余度较高 ({redundancy:.1%})",
            "suggestion": "建议精简重复表述，提高信息密度"
        },
        "low_data_freshness": {
            "condition": lambda m: m.data_freshness < 0.5 and m.content_length > 1000,
            "level": AlertLevel.WARNING,
            "message": "数据新鲜度较低，可能使用过时的信息",
            "suggestion": "建议补充最新的行业数据和市场信息"
        },
        
        # 执行时间相关
        "long_execution": {
            "condition": lambda m: m.execution_time > 300,  # 5分钟
            "level": AlertLevel.INFO,
            "message": "当前步骤执行时间较长",
            "suggestion": "考虑是否需要深入当前步骤，或可以进入下一步"
        },
        "very_long_execution": {
            "condition": lambda m: m.execution_time > 600,  # 10分钟
            "level": AlertLevel.WARNING,
            "message": "当前步骤执行时间过长",
            "suggestion": "建议检查分析进度，避免在单个步骤消耗过多时间"
        },
        
        # Step4 特殊规则
        "step4_insufficient_search": {
            "condition": lambda m: m.step_id == "step4" and m.tool_call_count < 5,
            "level": AlertLevel.WARNING,
            "message": "Step4搜索次数不足，可能影响分析深度",
            "suggestion": "建议增加深度搜索，获取更全面的市场信息"
        },
        "step4_short_content": {
            "condition": lambda m: m.step_id == "step4" and m.content_length < 3000 and m.tool_call_count > 10,
            "level": AlertLevel.WARNING,
            "message": "Step4内容产出不足，信息利用效率低",
            "suggestion": "建议充分利用搜索结果，扩展分析内容"
        }
    }
    
    def __init__(self):
        """初始化智能预警系统"""
        self.alert_history: List[Alert] = []
        self.metrics_history: List[StepMetrics] = []
        self.pattern_db = self._load_pattern_database()
        self.alert_handlers: List[Callable] = []
    
    def monitor_step_execution(self, metrics: StepMetrics) -> List[Alert]:
        """
        监控步骤执行，生成预警
        
        Args:
            metrics: 步骤执行指标
            
        Returns:
            List[Alert]: 预警列表
        """
        alerts = []
        
        # 执行规则检查
        for rule_id, rule in self.WARNING_RULES.items():
            try:
                if rule["condition"](metrics):
                    alert = Alert(
                        level=rule["level"],
                        type=rule_id,
                        message=rule["message"].format(
                            efficiency=metrics.token_efficiency,
                            redundancy=metrics.content_redundancy,
                            freshness=metrics.data_freshness
                        ),
                        suggestion=rule["suggestion"],
                        metadata={
                            "step_id": metrics.step_id,
                            "metrics": {
                                "token_usage": metrics.token_usage,
                                "content_length": metrics.content_length,
                                "tool_calls": metrics.tool_call_count,
                                "token_efficiency": metrics.token_efficiency,
                                "redundancy": metrics.content_redundancy
                            }
                        }
                    )
                    alerts.append(alert)
                    self.alert_history.append(alert)
            except Exception as e:
                # 规则执行失败不中断
                pass
        
        # 记录指标历史
        self.metrics_history.append(metrics)
        
        # 执行模式匹配
        pattern_alerts = self._detect_patterns(metrics)
        alerts.extend(pattern_alerts)
        
        # 调用预警处理器
        for handler in self.alert_handlers:
            try:
                for alert in alerts:
                    handler(alert)
            except Exception:
                pass
        
        return alerts
    
    def predict_final_quality(self, current_metrics: StepMetrics, 
                             completed_steps: List[str]) -> Dict:
        """
        预测最终报告质量
        
        基于当前进度和已完成步骤预测
        
        Args:
            current_metrics: 当前步骤指标
            completed_steps: 已完成步骤列表
            
        Returns:
            Dict: 质量预测结果
        """
        risk_factors = []
        confidence_boosters = []
        
        # 基于当前步骤评估
        if current_metrics.token_efficiency < 0.3:
            risk_factors.append("Token效率低")
        else:
            confidence_boosters.append("Token效率正常")
        
        if current_metrics.content_redundancy > 0.3:
            risk_factors.append("内容冗余度高")
        
        if current_metrics.data_freshness < 0.5:
            risk_factors.append("数据新鲜度低")
        else:
            confidence_boosters.append("数据新鲜度高")
        
        # 基于历史模式预测
        similar_patterns = self._find_similar_patterns(current_metrics)
        if similar_patterns:
            avg_quality = sum(p.get("final_quality", 0) for p in similar_patterns) / len(similar_patterns)
            quality_prediction = avg_quality
        else:
            # 基于简单规则预测
            base_score = 70
            if current_metrics.token_efficiency > 0.5:
                base_score += 10
            if current_metrics.data_freshness > 0.7:
                base_score += 10
            if current_metrics.content_redundancy < 0.2:
                base_score += 10
            quality_prediction = min(95, base_score)
        
        # 计算置信度
        confidence = 0.6
        if len(self.metrics_history) > 5:
            confidence = 0.8
        
        # 生成改进建议
        suggestions = []
        if "Token效率低" in risk_factors:
            suggestions.append("精简分析内容，聚焦核心要点")
        if "内容冗余度高" in risk_factors:
            suggestions.append("删除重复表述，提高信息密度")
        if "数据新鲜度低" in risk_factors:
            suggestions.append("补充最新的行业数据")
        
        return {
            "predicted_quality": round(quality_prediction, 1),
            "confidence": round(confidence, 2),
            "risk_factors": risk_factors,
            "confidence_boosters": confidence_boosters,
            "suggestions": suggestions,
            "risk_level": "high" if len(risk_factors) >= 2 else "medium" if risk_factors else "low"
        }
    
    def quick_health_check(self, context: ValidationContext) -> Dict:
        """
        快速健康检查
        
        用于实时监控，返回简化结果
        
        Args:
            context: 验证上下文
            
        Returns:
            Dict: 健康状态
        """
        metrics = StepMetrics(
            step_id=context.step_id,
            token_usage=context.token_usage,
            content_length=len(context.content),
            tool_calls=context.tool_calls
        )
        
        alerts = self.monitor_step_execution(metrics)
        
        critical_count = sum(1 for a in alerts if a.level == AlertLevel.CRITICAL)
        warning_count = sum(1 for a in alerts if a.level == AlertLevel.WARNING)
        
        status = "healthy"
        if critical_count > 0:
            status = "critical"
        elif warning_count > 1:
            status = "warning"
        elif warning_count > 0:
            status = "attention"
        
        return {
            "status": status,
            "alerts_count": len(alerts),
            "critical": critical_count,
            "warning": warning_count,
            "latest_alert": alerts[-1].message if alerts else None,
            "token_efficiency": round(metrics.token_efficiency, 2)
        }
    
    def register_alert_handler(self, handler: Callable):
        """注册预警处理器"""
        self.alert_handlers.append(handler)
    
    def _load_pattern_database(self) -> List[Dict]:
        """加载历史模式数据库"""
        # 简化实现，返回空列表
        return []
    
    def _detect_patterns(self, metrics: StepMetrics) -> List[Alert]:
        """检测异常模式"""
        alerts = []
        
        # 检测工具使用激增
        if len(self.metrics_history) >= 3:
            recent_calls = [m.tool_call_count for m in self.metrics_history[-3:]]
            if recent_calls[-1] > recent_calls[0] * 2:
                alerts.append(Alert(
                    level=AlertLevel.INFO,
                    type="tool_usage_spike",
                    message="工具调用次数激增",
                    suggestion="注意控制搜索范围，避免信息过载"
                ))
        
        # 检测内容产出停滞
        if len(self.metrics_history) >= 3:
            recent_lengths = [m.content_length for m in self.metrics_history[-3:]]
            if max(recent_lengths) - min(recent_lengths) < 100:
                alerts.append(Alert(
                    level=AlertLevel.WARNING,
                    type="content_stagnation",
                    message="内容产出增长停滞",
                    suggestion="可能陷入思考循环，建议整理已有内容"
                ))
        
        return alerts
    
    def _find_similar_patterns(self, metrics: StepMetrics) -> List[Dict]:
        """查找相似的历史模式"""
        similar = []
        
        for pattern in self.pattern_db:
            # 简单匹配：步骤ID相同且Token效率相近
            if pattern.get("step_id") == metrics.step_id:
                pattern_efficiency = pattern.get("token_efficiency", 0)
                if abs(pattern_efficiency - metrics.token_efficiency) < 0.1:
                    similar.append(pattern)
        
        return similar
    
    def get_alert_summary(self) -> Dict:
        """获取预警摘要"""
        if not self.alert_history:
            return {"total": 0, "by_level": {}, "by_type": {}}
        
        by_level = {}
        by_type = {}
        
        for alert in self.alert_history:
            level = alert.level.value
            by_level[level] = by_level.get(level, 0) + 1
            
            by_type[alert.type] = by_type.get(alert.type, 0) + 1
        
        return {
            "total": len(self.alert_history),
            "by_level": by_level,
            "by_type": by_type,
            "recent_alerts": [a.to_dict() for a in self.alert_history[-5:]]
        }
    
    def reset(self):
        """重置预警系统"""
        self.alert_history.clear()
        self.metrics_history.clear()


# 便捷函数
def create_early_warning_system() -> IntelligentEarlyWarning:
    """创建智能预警系统实例"""
    return IntelligentEarlyWarning()


if __name__ == "__main__":
    # 测试
    print("=" * 60)
    print("IntelligentEarlyWarning 测试")
    print("=" * 60)
    
    warning_system = IntelligentEarlyWarning()
    
    # 测试场景1：Token效率低
    print("\n测试场景1: Token效率低")
    metrics1 = StepMetrics(
        step_id="step4",
        token_usage=10000,
        content_length=2000,  # 效率 0.2
        tool_calls=[{"type": "search"}] * 15,
        content_redundancy=0.2,
        data_freshness=0.6
    )
    alerts1 = warning_system.monitor_step_execution(metrics1)
    for alert in alerts1:
        print(f"  [{alert.level.value}] {alert.message}")
    
    # 测试场景2：工具调用多但产出少
    print("\n测试场景2: 工具调用多但产出少")
    metrics2 = StepMetrics(
        step_id="step4",
        token_usage=8000,
        content_length=1500,
        tool_calls=[{"type": "search"}] * 25,
        content_redundancy=0.15,
        data_freshness=0.7
    )
    alerts2 = warning_system.monitor_step_execution(metrics2)
    for alert in alerts2:
        print(f"  [{alert.level.value}] {alert.message}")
    
    # 测试质量预测
    print("\n测试质量预测:")
    prediction = warning_system.predict_final_quality(metrics1, ["step1", "step2", "step3"])
    print(f"  预测质量: {prediction['predicted_quality']}")
    print(f"  置信度: {prediction['confidence']}")
    print(f"  风险因素: {prediction['risk_factors']}")
    print(f"  建议: {prediction['suggestions']}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
