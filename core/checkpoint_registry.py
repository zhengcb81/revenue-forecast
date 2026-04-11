"""
Revenue Forecast - 统一检查点注册中心
版本: v2.5.1
创建日期: 2026-03-01

功能:
1. 统一注册所有检查点
2. 支持前置/后置钩子
3. 单例模式确保全局唯一
4. 支持检查点依赖管理
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import threading


class CheckpointType(Enum):
    """检查点类型"""
    BLOCKING = "blocking"       # 阻断型 - 失败阻止继续
    WARNING = "warning"         # 警告型 - 失败只警告
    LOGGING = "logging"         # 记录型 - 只记录不判断


class CheckpointPriority(Enum):
    """检查点优先级"""
    CRITICAL = 0     # 关键 - 必须通过
    HIGH = 1         # 高优先级
    NORMAL = 2       # 普通
    LOW = 3          # 低优先级


@dataclass
class CheckpointConfig:
    """检查点配置"""
    id: str
    name: str
    description: str = ""
    type: CheckpointType = CheckpointType.BLOCKING
    priority: CheckpointPriority = CheckpointPriority.NORMAL
    
    # 验证函数 - 可以是函数或函数路径
    validator: Optional[Union[Callable, str]] = None
    
    # 阈值配置
    thresholds: Dict[str, Any] = field(default_factory=dict)
    
    # 失败处理
    on_failure: str = "stop"  # stop / warn / continue
    
    # 是否启用
    enabled: bool = True
    
    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CheckpointResult:
    """检查点执行结果"""
    checkpoint_id: str
    passed: bool
    score: float = 0.0  # 0-100
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    execution_time_ms: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "checkpoint_id": self.checkpoint_id,
            "passed": self.passed,
            "score": self.score,
            "message": self.message,
            "details": self.details,
            "errors": self.errors,
            "warnings": self.warnings,
            "suggestions": self.suggestions,
            "execution_time_ms": self.execution_time_ms,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class ValidationContext:
    """验证上下文"""
    company_name: str
    step_id: str
    content: str = ""
    token_usage: int = 0
    tool_calls: List[Dict] = field(default_factory=list)
    files_generated: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "company_name": self.company_name,
            "step_id": self.step_id,
            "content_length": len(self.content),
            "token_usage": self.token_usage,
            "tool_calls_count": len(self.tool_calls),
            "files_generated": self.files_generated,
            "metrics": self.metrics,
            "metadata": self.metadata
        }


class Checkpoint:
    """检查点类"""
    
    def __init__(self, config: CheckpointConfig):
        self.config = config
        self.execution_count = 0
        self.failure_count = 0
        self.last_execution_time = None
        
    def execute(self, context: ValidationContext) -> CheckpointResult:
        """执行检查点"""
        import time
        start_time = time.time()
        
        self.execution_count += 1
        
        if not self.config.enabled:
            return CheckpointResult(
                checkpoint_id=self.config.id,
                passed=True,
                message="检查点已禁用"
            )
        
        # 获取验证函数
        validator = self._get_validator()
        if validator is None:
            return CheckpointResult(
                checkpoint_id=self.config.id,
                passed=True,
                message="无验证函数，跳过"
            )
        
        try:
            # 执行验证
            result = validator(context, self.config.thresholds)
            
            # 确保返回CheckpointResult
            if not isinstance(result, CheckpointResult):
                result = CheckpointResult(
                    checkpoint_id=self.config.id,
                    passed=bool(result),
                    message="验证完成"
                )
            
            result.checkpoint_id = self.config.id
            result.execution_time_ms = int((time.time() - start_time) * 1000)
            
            if not result.passed:
                self.failure_count += 1
            
            self.last_execution_time = datetime.now()
            return result
            
        except Exception as e:
            self.failure_count += 1
            return CheckpointResult(
                checkpoint_id=self.config.id,
                passed=False,
                message=f"验证执行异常: {str(e)}",
                errors=[str(e)]
            )
    
    def _get_validator(self) -> Optional[Callable]:
        """获取验证函数"""
        if self.config.validator is None:
            return None
        
        if callable(self.config.validator):
            return self.config.validator
        
        # 如果是字符串，尝试导入
        if isinstance(self.config.validator, str):
            try:
                module_path, func_name = self.config.validator.rsplit('.', 1)
                module = __import__(module_path, fromlist=[func_name])
                return getattr(module, func_name)
            except Exception as e:
                print(f"[Checkpoint] 无法加载验证函数 {self.config.validator}: {e}")
                return None
        
        return None
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            "checkpoint_id": self.config.id,
            "execution_count": self.execution_count,
            "failure_count": self.failure_count,
            "failure_rate": self.failure_count / max(self.execution_count, 1),
            "last_execution_time": self.last_execution_time.isoformat() if self.last_execution_time else None
        }


class CheckpointRegistry:
    """
    统一检查点注册中心 - 单例模式
    
    用法:
        registry = CheckpointRegistry()
        registry.register(CheckpointConfig(id="check1", ...))
        result = registry.execute("check1", context)
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.checkpoints: Dict[str, Checkpoint] = {}
        self.hooks: Dict[str, List[Callable]] = {
            "pre_execute": [],
            "post_execute": [],
            "on_failure": [],
            "on_success": []
        }
        self.execution_history: List[Dict] = []
        self._initialized = True
        
        print("[CheckpointRegistry] 初始化完成")
    
    def register(self, config: CheckpointConfig) -> 'CheckpointRegistry':
        """
        注册检查点
        
        Args:
            config: 检查点配置
            
        Returns:
            self (支持链式调用)
        """
        if config.id in self.checkpoints:
            print(f"[CheckpointRegistry] 警告: 检查点 {config.id} 已存在，将被覆盖")
        
        self.checkpoints[config.id] = Checkpoint(config)
        print(f"[CheckpointRegistry] 注册检查点: {config.id} ({config.name})")
        return self
    
    def register_batch(self, configs: List[CheckpointConfig]) -> 'CheckpointRegistry':
        """批量注册检查点"""
        for config in configs:
            self.register(config)
        return self
    
    def unregister(self, checkpoint_id: str) -> bool:
        """注销检查点"""
        if checkpoint_id in self.checkpoints:
            del self.checkpoints[checkpoint_id]
            print(f"[CheckpointRegistry] 注销检查点: {checkpoint_id}")
            return True
        return False
    
    def get(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """获取检查点"""
        return self.checkpoints.get(checkpoint_id)
    
    def execute(self, checkpoint_id: str, context: ValidationContext) -> CheckpointResult:
        """
        执行单个检查点
        
        Args:
            checkpoint_id: 检查点ID
            context: 验证上下文
            
        Returns:
            CheckpointResult: 执行结果
        """
        checkpoint = self.checkpoints.get(checkpoint_id)
        if checkpoint is None:
            return CheckpointResult(
                checkpoint_id=checkpoint_id,
                passed=False,
                message=f"检查点未找到: {checkpoint_id}",
                errors=[f"Unknown checkpoint: {checkpoint_id}"]
            )
        
        # 执行前置钩子
        for hook in self.hooks["pre_execute"]:
            try:
                hook(checkpoint_id, context)
            except Exception as e:
                print(f"[CheckpointRegistry] 前置钩子执行失败: {e}")
        
        # 执行检查点
        result = checkpoint.execute(context)
        
        # 记录历史
        self.execution_history.append({
            "checkpoint_id": checkpoint_id,
            "result": result.to_dict(),
            "context": context.to_dict()
        })
        
        # 执行后置钩子
        hook_type = "on_success" if result.passed else "on_failure"
        for hook in self.hooks[hook_type]:
            try:
                hook(checkpoint_id, context, result)
            except Exception as e:
                print(f"[CheckpointRegistry] 后置钩子执行失败: {e}")
        
        for hook in self.hooks["post_execute"]:
            try:
                hook(checkpoint_id, context, result)
            except Exception as e:
                print(f"[CheckpointRegistry] 后置钩子执行失败: {e}")
        
        return result
    
    def execute_batch(self, checkpoint_ids: List[str], context: ValidationContext) -> Dict[str, CheckpointResult]:
        """
        批量执行检查点
        
        按优先级排序：CRITICAL > HIGH > NORMAL > LOW
        同优先级按注册顺序执行
        """
        # 获取检查点并排序
        checkpoints_to_run = []
        for cid in checkpoint_ids:
            if cid in self.checkpoints:
                cp = self.checkpoints[cid]
                checkpoints_to_run.append((cp.config.priority.value, cid, cp))
        
        # 按优先级排序
        checkpoints_to_run.sort(key=lambda x: x[0])
        
        results = {}
        for _, cid, _ in checkpoints_to_run:
            result = self.execute(cid, context)
            results[cid] = result
            
            # 如果是阻断型且失败，立即停止
            if not result.passed:
                cp = self.checkpoints[cid]
                if cp.config.type == CheckpointType.BLOCKING:
                    print(f"[CheckpointRegistry] 阻断型检查点 {cid} 失败，停止后续检查")
                    break
        
        return results
    
    def execute_by_step(self, step_id: str, context: ValidationContext) -> Dict[str, CheckpointResult]:
        """
        执行与特定步骤关联的所有检查点
        
        检查点ID格式应为: "step_{step_id}_{check_name}"
        例如: "step4_content_quality"
        """
        prefix = f"step{step_id}_"
        checkpoint_ids = [cid for cid in self.checkpoints if cid.startswith(prefix) or cid.startswith(f"step_{step_id}_")]
        return self.execute_batch(checkpoint_ids, context)
    
    def add_hook(self, hook_point: str, callback: Callable) -> 'CheckpointRegistry':
        """
        添加钩子
        
        Args:
            hook_point: 钩子点 (pre_execute / post_execute / on_failure / on_success)
            callback: 回调函数
        """
        if hook_point not in self.hooks:
            raise ValueError(f"未知钩子点: {hook_point}")
        
        self.hooks[hook_point].append(callback)
        return self
    
    def remove_hook(self, hook_point: str, callback: Callable) -> bool:
        """移除钩子"""
        if hook_point in self.hooks and callback in self.hooks[hook_point]:
            self.hooks[hook_point].remove(callback)
            return True
        return False
    
    def list_checkpoints(self, enabled_only: bool = False) -> List[Dict]:
        """列出所有检查点"""
        result = []
        for cid, cp in self.checkpoints.items():
            if enabled_only and not cp.config.enabled:
                continue
            result.append({
                "id": cid,
                "name": cp.config.name,
                "type": cp.config.type.value,
                "priority": cp.config.priority.name,
                "enabled": cp.config.enabled,
                "stats": cp.get_stats()
            })
        return result
    
    def get_stats(self) -> Dict:
        """获取注册中心统计信息"""
        total_executions = len(self.execution_history)
        total_failures = sum(1 for h in self.execution_history if not h["result"]["passed"])
        
        return {
            "registered_checkpoints": len(self.checkpoints),
            "total_executions": total_executions,
            "total_failures": total_failures,
            "overall_failure_rate": total_failures / max(total_executions, 1),
            "checkpoint_stats": [cp.get_stats() for cp in self.checkpoints.values()]
        }
    
    def export_config(self, output_path: str):
        """导出检查点配置"""
        configs = []
        for cid, cp in self.checkpoints.items():
            configs.append({
                "id": cp.config.id,
                "name": cp.config.name,
                "description": cp.config.description,
                "type": cp.config.type.value,
                "priority": cp.config.priority.name,
                "thresholds": cp.config.thresholds,
                "on_failure": cp.config.on_failure,
                "enabled": cp.config.enabled
            })
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(configs, f, indent=2, ensure_ascii=False)
        
        print(f"[CheckpointRegistry] 配置已导出: {output_path}")
    
    def clear_history(self):
        """清空执行历史"""
        self.execution_history.clear()
        print("[CheckpointRegistry] 执行历史已清空")
    
    def reset(self):
        """重置注册中心"""
        self.checkpoints.clear()
        for hooks in self.hooks.values():
            hooks.clear()
        self.execution_history.clear()
        print("[CheckpointRegistry] 已重置")


# 便捷函数
def get_registry() -> CheckpointRegistry:
    """获取检查点注册中心实例"""
    return CheckpointRegistry()


# 预定义检查点ID常量
class CheckpointIDs:
    """标准检查点ID"""
    # Step 4 检查点
    STEP4_TOKEN_USAGE = "step4_token_usage"
    STEP4_CONTENT_QUALITY = "step4_content_quality"
    STEP4_TOOL_USAGE = "step4_tool_usage"
    STEP4_FILE_GENERATION = "step4_file_generation"
    STEP4_INFO_DENSITY = "step4_info_density"
    
    # Step 5 检查点
    STEP5_CONTENT_QUALITY = "step5_content_quality"
    STEP5_COMPANY_TYPE_SPECIFIC = "step5_company_type_specific"
    
    # Step 6 检查点
    STEP6_SCENARIO_CONSISTENCY = "step6_scenario_consistency"
    STEP6_PROBABILITY_SUM = "step6_probability_sum"
    
    # Step 7 检查点
    STEP7_CAGR_REASONABLENESS = "step7_cagr_reasonableness"
    STEP7_CAGR_CALCULATION = "step7_cagr_calculation"
    
    # Step 8 检查点
    STEP8_SCORING_CONSISTENCY = "step8_scoring_consistency"
    
    # Step 9 检查点
    STEP9_REPORT_COMPLETENESS = "step9_report_completeness"
    STEP9_LANGUAGE_CHECK = "step9_language_check"
    STEP9_JSON_MD_CONSISTENCY = "step9_json_md_consistency"
    STEP9_AI_VALIDATION = "step9_ai_validation"
    
    # 全局检查点
    GLOBAL_TRACING_COMPLETENESS = "global_tracing_completeness"
    GLOBAL_DATA_CONSISTENCY = "global_data_consistency"


if __name__ == "__main__":
    # 简单测试
    print("=" * 60)
    print("CheckpointRegistry 测试")
    print("=" * 60)
    
    registry = get_registry()
    
    # 注册测试检查点
    def sample_validator(context, thresholds):
        return CheckpointResult(
            checkpoint_id="test",
            passed=True,
            score=85.0,
            message="测试通过"
        )
    
    registry.register(CheckpointConfig(
        id="test_checkpoint",
        name="测试检查点",
        description="用于测试的检查点",
        validator=sample_validator,
        type=CheckpointType.BLOCKING,
        priority=CheckpointPriority.HIGH
    ))
    
    # 执行测试
    context = ValidationContext(
        company_name="测试公司",
        step_id="step4",
        content="测试内容",
        token_usage=10000
    )
    
    result = registry.execute("test_checkpoint", context)
    print(f"\n测试结果:")
    print(f"  通过: {result.passed}")
    print(f"  分数: {result.score}")
    print(f"  消息: {result.message}")
    
    # 统计信息
    print(f"\n统计信息:")
    stats = registry.get_stats()
    print(f"  注册检查点数: {stats['registered_checkpoints']}")
    print(f"  总执行次数: {stats['total_executions']}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
