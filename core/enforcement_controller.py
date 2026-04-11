"""
营收增长预测分析 - 强制执行控制器
版本: v1.0
创建日期: 2026-01-17

目的: 确保所有分析步骤必须完整执行，防止因省token或其他原因跳过流程
核心功能:
1. 步骤状态跟踪 (pending, in_progress, completed, failed)
2. 步骤依赖验证 (前一步未完成不能进入下一步)
3. 防跳过机制 (尝试跳过步骤时阻止并报错)
4. 与现有验证机制集成 (checklist.md, validate_report.py)
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Set, Any, Callable, Union
from enum import Enum

# 导入验证器模块
try:
    from .checklist_validator import ChecklistValidator, create_checklist_validator_for_step
except ImportError:
    ChecklistValidator = None
    create_checklist_validator_for_step = None

class StepStatus(Enum):
    """步骤状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class StepValidationResult:
    """步骤验证结果"""
    def __init__(self, is_valid: bool, errors: List[str] = None, warnings: List[str] = None):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []

    def __bool__(self):
        return self.is_valid

    def add_error(self, error: str):
        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, warning: str):
        self.warnings.append(warning)

    def to_dict(self) -> Dict:
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings
        }

class EnforcementStep:
    """强制执行步骤定义"""
    def __init__(self,
                 step_id: str,
                 name: str,
                 description: str = "",
                 dependencies: List[str] = None,
                 validation_func: Callable[[], StepValidationResult] = None,
                 required_outputs: List[str] = None):
        self.step_id = step_id
        self.name = name
        self.description = description
        self.dependencies = dependencies or []
        self.validation_func = validation_func
        self.required_outputs = required_outputs or []

        self.status = StepStatus.PENDING
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.validation_result: Optional[StepValidationResult] = None
        self.metadata: Dict[str, Any] = {}

    def start(self):
        """开始执行步骤"""
        if self.status != StepStatus.PENDING:
            raise ValueError(f"步骤 {self.step_id} 状态为 {self.status.value}，无法开始")
        self.status = StepStatus.IN_PROGRESS
        self.started_at = datetime.now()

    def complete(self, validation_result: StepValidationResult = None):
        """完成步骤"""
        if self.status != StepStatus.IN_PROGRESS:
            raise ValueError(f"步骤 {self.step_id} 状态为 {self.status.value}，无法完成")

        self.validation_result = validation_result or StepValidationResult(True)
        self.status = StepStatus.COMPLETED if self.validation_result.is_valid else StepStatus.FAILED
        self.completed_at = datetime.now()

    def fail(self, error: str):
        """标记步骤失败"""
        self.status = StepStatus.FAILED
        self.completed_at = datetime.now()
        self.validation_result = StepValidationResult(False, errors=[error])

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "step_id": self.step_id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "dependencies": self.dependencies,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "validation_result": self.validation_result.to_dict() if self.validation_result else None,
            "metadata": self.metadata
        }

class EnforcementController:
    """强制执行控制器"""

    def __init__(self, company_name: str, cache_dir: str = None):
        self.company_name = company_name
        self.cache_dir = cache_dir or self._get_default_cache_dir()
        self.steps: Dict[str, EnforcementStep] = {}
        self.execution_order: List[str] = []

        # 状态文件路径
        self.state_file = Path(self.cache_dir) / "enforcement_state.json"

        # 初始化标准步骤
        self._initialize_standard_steps()

    def _get_default_cache_dir(self) -> str:
        """获取默认缓存目录"""
        from .config import get_cache_base_dir, build_company_cache_dir
        cache_base = get_cache_base_dir()
        return build_company_cache_dir(self.company_name, cache_base)

    def _initialize_standard_steps(self):
        """初始化标准步骤（根据skill.md中的10个步骤）"""
        standard_steps = [
            ("step0", "加载配置", "加载系统配置，验证目录路径和维度文件配置"),
            ("step1", "初始化缓存系统", "创建公司专属缓存目录和metadata.json"),
            ("step2", "判断公司类型", "自动识别公司类型"),
            ("step3", "语言策略判断", "识别公司地域类型，确定搜索语言策略"),
            ("step4", "执行9维度研究", "完成9个维度的深度研究，生成缓存文件"),
            ("step4_5", "品牌矩阵分析", "产品驱动型公司品牌矩阵专项分析", ["step4"]),
            ("step5", "执行公司类型专项分析", "根据公司类型执行对应专项分析框架"),
            ("step6", "情景预测与加权计算", "完成乐观/基准/悲观三种情景预测"),
            ("step7", "综合CAGR计算", "计算最终的综合复合年增长率"),
            ("step8", "综合评分", "基于CAGR直接查表评分"),
            ("step9", "生成并保存报告", "生成JSON和Markdown两个报告文件"),
            ("step9_5", "报告验证", "自动化验证报告质量"),
            ("step10", "更新缓存", "更新缓存状态，保存分析结果")
        ]

        # 设置依赖关系
        dependencies_map = {
            "step0": [],
            "step1": ["step0"],
            "step2": ["step1"],
            "step3": ["step2"],
            "step4": ["step3"],
            "step4_5": ["step4"],  # 品牌矩阵分析依赖第4步
            "step5": ["step4"],    # 如果是产品驱动型，可能依赖step4_5，这里简化
            "step6": ["step5"],
            "step7": ["step6"],
            "step8": ["step7"],
            "step9": ["step8"],
            "step9_5": ["step9"],
            "step10": ["step9_5"]
        }

        for step_info in standard_steps:
            step_id = step_info[0]
            name = step_info[1]
            description = step_info[2] if len(step_info) > 2 else ""
            deps = dependencies_map.get(step_id, [])

            step = EnforcementStep(
                step_id=step_id,
                name=name,
                description=description,
                dependencies=deps
            )
            self.register_step(step)

    def register_step(self, step: EnforcementStep):
        """注册步骤"""
        if step.step_id in self.steps:
            raise ValueError(f"步骤 {step.step_id} 已注册")
        self.steps[step.step_id] = step
        self.execution_order.append(step.step_id)

    def validate_dependencies(self, step_id: str) -> StepValidationResult:
        """验证步骤依赖是否满足"""
        result = StepValidationResult(True)

        if step_id not in self.steps:
            result.add_error(f"步骤 {step_id} 未注册")
            return result

        step = self.steps[step_id]

        for dep_id in step.dependencies:
            if dep_id not in self.steps:
                result.add_error(f"依赖步骤 {dep_id} 未注册")
                continue

            dep_step = self.steps[dep_id]
            if dep_step.status != StepStatus.COMPLETED:
                result.add_error(f"依赖步骤 {dep_id} 未完成 (状态: {dep_step.status.value})")

        return result

    def can_start_step(self, step_id: str) -> bool:
        """检查是否可以开始步骤"""
        validation = self.validate_dependencies(step_id)
        return validation.is_valid

    def start_step(self, step_id: str) -> bool:
        """开始执行步骤"""
        if not self.can_start_step(step_id):
            validation = self.validate_dependencies(step_id)
            error_msg = f"无法开始步骤 {step_id}: " + "; ".join(validation.errors)
            raise ValueError(error_msg)

        step = self.steps[step_id]
        step.start()
        self._save_state()
        return True

    def complete_step(self, step_id: str, validation_result: StepValidationResult = None) -> bool:
        """完成步骤"""
        if step_id not in self.steps:
            raise ValueError(f"步骤 {step_id} 未注册")

        step = self.steps[step_id]

        if step.status != StepStatus.IN_PROGRESS:
            raise ValueError(f"步骤 {step_id} 状态为 {step.status.value}，无法完成")

        step.complete(validation_result)
        self._save_state()
        return True
    
    def complete_step_with_validation(
        self, 
        step_id: str, 
        token_usage: int = None,
        content: str = None,
        tool_calls: int = None,
        tool_types: List[str] = None,
        extra_validation: StepValidationResult = None
    ) -> bool:
        """
        完成步骤并进行多维度防跳过验证（v2.5.0增强版）
        
        不依赖单一时间指标，而是从Token消耗、内容深度、工具调用、
        文件生成等多个维度综合评估步骤完成质量。
        
        验证逻辑：
        - 内容深度和文件生成是硬性要求（必须满足）
        - Token消耗和工具调用是软性要求（可互补）
        - 至少满足两项才可通过
        
        Args:
            step_id: 步骤ID
            token_usage: 实际消耗的Token数
            content: 步骤输出的内容
            tool_calls: 工具调用总次数
            tool_types: 工具类型列表（如 ['web_search', 'read']）
            extra_validation: 额外的验证结果
            
        Returns:
            bool: 是否成功完成
        """
        # 标准完成流程检查
        if step_id not in self.steps:
            raise ValueError(f"步骤 {step_id} 未注册")
        
        step = self.steps[step_id]
        
        if step.status != StepStatus.IN_PROGRESS:
            raise ValueError(f"步骤 {step_id} 状态为 {step.status.value}，无法完成")
        
        # 获取缓存目录（用于文件验证）
        cache_dir = None
        try:
            from .config import get_cache_base_dir
            cache_dir = get_cache_base_dir()
        except:
            cache_dir = self.cache_dir
        
        # 多维度综合验证
        combined_result = AntiSkippingValidator.comprehensive_validation(
            step_id=step_id,
            token_usage=token_usage,
            content=content,
            tool_calls=tool_calls,
            tool_types=tool_types,
            cache_dir=cache_dir,
            company_name=self.company_name
        )
        
        # 合并额外验证结果
        if extra_validation is not None:
            if not extra_validation.is_valid:
                for error in extra_validation.errors:
                    combined_result.add_error(error)
            for warning in extra_validation.warnings:
                combined_result.add_warning(warning)
        
        # 如果有验证错误，阻止步骤完成
        if not combined_result.is_valid:
            print(f"\n{'='*70}")
            print(f"❌ 步骤 {step_id} 验证失败，无法完成！")
            print(f"{'='*70}")
            print("错误详情:")
            for error in combined_result.errors:
                print(f"  • {error}")
            if combined_result.warnings:
                print("\n警告:")
                for warning in combined_result.warnings:
                    print(f"  • {warning}")
            print(f"{'='*70}\n")
            raise ValueError(f"步骤 {step_id} 防跳过验证失败: {combined_result.errors}")
        
        # 验证通过，完成步骤
        step.complete(combined_result)
        self._save_state()
        
        # 打印验证通过信息
        print(f"✅ 步骤 {step_id} 完成并通过防跳过验证")
        if combined_result.warnings:
            print("警告:")
            for warning in combined_result.warnings:
                print(f"  • {warning}")
        
        return True

    def fail_step(self, step_id: str, error: str):
        """标记步骤失败"""
        if step_id not in self.steps:
            raise ValueError(f"步骤 {step_id} 未注册")

        step = self.steps[step_id]
        step.fail(error)
        self._save_state()

    def get_step_status(self, step_id: str) -> Optional[StepStatus]:
        """获取步骤状态"""
        step = self.steps.get(step_id)
        return step.status if step else None

    def get_execution_summary(self) -> Dict:
        """获取执行摘要"""
        total = len(self.steps)
        completed = sum(1 for step in self.steps.values() if step.status == StepStatus.COMPLETED)
        in_progress = sum(1 for step in self.steps.values() if step.status == StepStatus.IN_PROGRESS)
        pending = sum(1 for step in self.steps.values() if step.status == StepStatus.PENDING)
        failed = sum(1 for step in self.steps.values() if step.status == StepStatus.FAILED)

        # 检查是否有步骤被跳过
        skipped_steps = []
        for i, step_id in enumerate(self.execution_order):
            step = self.steps[step_id]
            if step.status == StepStatus.PENDING and i > 0:
                # 检查前一步是否完成
                prev_step_id = self.execution_order[i-1]
                prev_step = self.steps[prev_step_id]
                if prev_step.status == StepStatus.COMPLETED:
                    skipped_steps.append(step_id)

        return {
            "company_name": self.company_name,
            "total_steps": total,
            "completed": completed,
            "in_progress": in_progress,
            "pending": pending,
            "failed": failed,
            "completion_percentage": (completed / total * 100) if total > 0 else 0,
            "skipped_steps": skipped_steps,
            "has_skipped_steps": len(skipped_steps) > 0,
            "timestamp": datetime.now().isoformat()
        }

    def validate_no_skipped_steps(self) -> StepValidationResult:
        """验证没有步骤被跳过"""
        result = StepValidationResult(True)
        summary = self.get_execution_summary()

        if summary["has_skipped_steps"]:
            for step_id in summary["skipped_steps"]:
                step = self.steps[step_id]
                result.add_error(f"步骤被跳过: {step.name} ({step_id})")

        return result

    def enforce_complete_execution(self) -> StepValidationResult:
        """强制执行完整执行验证"""
        result = StepValidationResult(True)

        # 检查1: 所有步骤是否完成
        incomplete_steps = []
        for step_id, step in self.steps.items():
            if step.status not in [StepStatus.COMPLETED, StepStatus.FAILED]:
                incomplete_steps.append(f"{step.name} ({step_id}): {step.status.value}")

        if incomplete_steps:
            result.add_error(f"有未完成的步骤: {', '.join(incomplete_steps)}")

        # 检查2: 是否有步骤被跳过
        skip_validation = self.validate_no_skipped_steps()
        if not skip_validation:
            for error in skip_validation.errors:
                result.add_error(error)

        # 检查3: 是否有失败的步骤
        failed_steps = []
        for step_id, step in self.steps.items():
            if step.status == StepStatus.FAILED:
                failed_steps.append(f"{step.name} ({step_id})")

        if failed_steps:
            result.add_warning(f"有失败的步骤: {', '.join(failed_steps)}")
        
        # 检查4: 维度文件完整性（针对step4）
        if self.steps.get("step4") and self.steps["step4"].status == StepStatus.COMPLETED:
            try:
                from .config import get_cache_base_dir
                cache_base = get_cache_base_dir()
                dim_validation = ContentDepthValidator.validate_dimension_files(
                    cache_base, self.company_name, expected_dimensions=9
                )
                if not dim_validation.is_valid:
                    for error in dim_validation.errors:
                        result.add_error(f"维度文件验证: {error}")
                for warning in dim_validation.warnings:
                    result.add_warning(f"维度文件: {warning}")
            except Exception as e:
                result.add_warning(f"维度文件验证异常: {e}")

        return result
    
    def validate_step_output(self, step_id: str, **kwargs) -> StepValidationResult:
        """
        验证步骤输出质量（多维度）
        
        Args:
            step_id: 步骤ID
            **kwargs: 验证参数
                - token_usage: Token消耗数
                - content: 输出内容
                - tool_calls: 工具调用次数
                - tool_types: 工具类型列表
            
        Returns:
            StepValidationResult: 验证结果
        """
        result = StepValidationResult(True)
        
        # 使用新的综合验证方法
        combined = AntiSkippingValidator.comprehensive_validation(
            step_id=step_id,
            token_usage=kwargs.get("token_usage"),
            content=kwargs.get("content"),
            tool_calls=kwargs.get("tool_calls"),
            tool_types=kwargs.get("tool_types"),
            cache_dir=kwargs.get("cache_dir") or self.cache_dir,
            company_name=self.company_name
        )
        
        # 合并结果
        if not combined.is_valid:
            result.is_valid = False
        for error in combined.errors:
            result.add_error(error)
        for warning in combined.warnings:
            result.add_warning(warning)
        
        return result

    def _save_state(self):
        """保存状态到文件"""
        state = {
            "company_name": self.company_name,
            "cache_dir": self.cache_dir,
            "steps": {step_id: step.to_dict() for step_id, step in self.steps.items()},
            "execution_order": self.execution_order,
            "last_updated": datetime.now().isoformat()
        }

        # 确保目录存在
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)

        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def load_state(self) -> bool:
        """从文件加载状态"""
        if not os.path.exists(self.state_file):
            return False

        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)

            # 恢复步骤状态
            for step_id, step_data in state.get("steps", {}).items():
                if step_id in self.steps:
                    step = self.steps[step_id]
                    step.status = StepStatus(step_data["status"])
                    step.started_at = datetime.fromisoformat(step_data["started_at"]) if step_data["started_at"] else None
                    step.completed_at = datetime.fromisoformat(step_data["completed_at"]) if step_data["completed_at"] else None

                    # 恢复验证结果
                    if step_data.get("validation_result"):
                        vr_data = step_data["validation_result"]
                        step.validation_result = StepValidationResult(
                            vr_data["is_valid"],
                            vr_data.get("errors", []),
                            vr_data.get("warnings", [])
                        )

            return True
        except Exception as e:
            print(f"加载状态失败: {e}")
            return False

    def print_status_report(self):
        """打印状态报告"""
        summary = self.get_execution_summary()

        print("=" * 70)
        print("强制执行控制器状态报告")
        print("=" * 70)
        print(f"公司: {self.company_name}")
        print(f"总步骤数: {summary['total_steps']}")
        print(f"完成: {summary['completed']} | 进行中: {summary['in_progress']} | 待处理: {summary['pending']} | 失败: {summary['failed']}")
        print(f"完成度: {summary['completion_percentage']:.1f}%")
        print()

        # 打印步骤状态
        print("步骤状态详情:")
        print("-" * 70)
        for step_id in self.execution_order:
            step = self.steps[step_id]
            status_icon = {
                StepStatus.PENDING: "⏳",
                StepStatus.IN_PROGRESS: "🔄",
                StepStatus.COMPLETED: "✅",
                StepStatus.FAILED: "❌"
            }.get(step.status, "❓")

            deps_str = f" ← [{', '.join(step.dependencies)}]" if step.dependencies else ""
            print(f"{status_icon} {step.name} ({step_id}){deps_str}")
            if step.description:
                print(f"    {step.description}")

        # 检查跳过情况
        if summary["has_skipped_steps"]:
            print()
            print("⚠️ 警告: 检测到跳过步骤!")
            for step_id in summary["skipped_steps"]:
                step = self.steps[step_id]
                print(f"  ❌ {step.name} ({step_id}) 被跳过")

        print("=" * 70)


# ============ 防跳过验证器（v2.5.0 新增） ============

class AntiSkippingValidator:
    """
    防跳过验证器 - 多维度检测是否偷懒
    
    不依赖单一的时间指标，而是从多个维度综合评估：
    1. Token消耗 - 衡量思考深度
    2. 内容产出 - 衡量输出质量
    3. 工具调用 - 衡量行动次数
    4. 文件生成 - 衡量工作成果
    5. 相对时间 - 与历史平均对比（可选）
    
    优势:
    - 不受模型速度影响
    - 不受缓存影响
    - 更关注实际产出而非耗时
    """
    
    # ========== Token消耗要求 ==========
    STEP_MIN_TOKENS = {
        "step0": 500,
        "step1": 300,
        "step2": 1000,
        "step3": 800,
        "step4": 8000,      # 9维度研究核心
        "step4_5": 3000,
        "step5": 5000,
        "step6": 2000,
        "step7": 1000,
        "step8": 1500,
        "step9": 3000,
        "step9_5": 1000,
        "step10": 500
    }
    
    # ========== 内容产出要求 ==========
    STEP_MIN_CONTENT_LENGTH = {
        "step0": 100,
        "step1": 200,
        "step2": 500,
        "step3": 300,
        "step4": 5000,      # 9维度至少5000字符
        "step4_5": 2000,
        "step5": 3000,
        "step6": 1500,
        "step7": 500,
        "step8": 500,
        "step9": 3000,
        "step9_5": 200,
        "step10": 200
    }
    
    # ========== 工具调用要求（搜索、读取等） ==========
    STEP_MIN_TOOL_CALLS = {
        "step0": 2,         # 读取config.yaml和config.py
        "step1": 3,         # 创建目录、metadata.json、search-results
        "step2": 2,         # 读取type-detection.md + 搜索
        "step3": 2,         # 读取language-strategy.md + 搜索
        "step4": 18,        # 9维度 × 至少2次搜索
        "step4_5": 6,       # 品牌矩阵搜索
        "step5": 8,         # 公司类型专项分析
        "step6": 4,         # 情景分析
        "step7": 2,         # CAGR计算
        "step8": 2,         # 评分
        "step9": 4,         # 生成报告
        "step9_5": 1,       # 验证
        "step10": 2         # 更新缓存
    }
    
    # ========== 文件生成要求 ==========
    STEP_REQUIRED_FILES = {
        "step0": [],
        "step1": ["metadata.json"],
        "step2": [],
        "step3": [],
        "step4": ["dimension-*.md"],  # 至少9个维度文件
        "step4_5": ["dimension-10-brand-matrix.md"],
        "step5": ["*-analysis.md"],
        "step6": ["scenario-analysis.md"],
        "step7": [],
        "step8": ["scoring.md"],
        "step9": ["RevGrowth_*.json", "RevGrowth_FullReport_*.md"],
        "step9_5": [],
        "step10": ["metadata.json"]
    }
    
    # ========== 维度要求（针对step4） ==========
    STEP_DIMENSION_REQUIREMENTS = {
        "step4": {
            "min_dimensions": 9,
            "min_content_per_dimension": 500,  # 每个维度至少500字符
            "required_keywords": ["##", "###"]  # 必须有结构化标题
        }
    }
    
    @classmethod
    def validate_token_usage(cls, step_id: str, actual_tokens: int) -> StepValidationResult:
        """验证Token消耗"""
        result = StepValidationResult(True)
        min_tokens = cls.STEP_MIN_TOKENS.get(step_id, 1000)
        
        if actual_tokens < min_tokens:
            result.add_error(
                f"步骤 {step_id} Token消耗不足: {actual_tokens} < 要求 {min_tokens}\n"
                f"可能未充分展开分析，请补充内容！"
            )
            result.is_valid = False
        elif actual_tokens < min_tokens * 1.2:
            result.add_warning(f"步骤 {step_id} Token消耗偏低，建议检查内容深度")
        
        return result
    
    @classmethod
    def validate_content_depth(cls, step_id: str, content: str) -> StepValidationResult:
        """验证内容深度"""
        result = StepValidationResult(True)
        min_length = cls.STEP_MIN_CONTENT_LENGTH.get(step_id, 1000)
        
        if len(content) < min_length:
            result.add_error(
                f"步骤 {step_id} 内容过短: {len(content)} 字符 < 要求 {min_length} 字符"
            )
            result.is_valid = False
            return result
        
        # 关键步骤额外检查
        if step_id in ["step4", "step5", "step9"]:
            # 检查结构化
            if "##" not in content:
                result.add_error(f"步骤 {step_id} 缺少结构化标题(##)")
                result.is_valid = False
            
            # 检查数据
            data_patterns = ["%", "亿元", "万", "CAGR", "增长率"]
            if not any(p in content for p in data_patterns):
                result.add_warning(f"步骤 {step_id} 缺少数据支撑")
        
        return result
    
    @classmethod
    def validate_tool_calls(cls, step_id: str, tool_call_count: int, tool_types: List[str] = None) -> StepValidationResult:
        """
        验证工具调用次数
        
        Args:
            step_id: 步骤ID
            tool_call_count: 工具调用总次数
            tool_types: 调用的工具类型列表（如 ['web_search', 'read', 'write']）
        """
        result = StepValidationResult(True)
        min_calls = cls.STEP_MIN_TOOL_CALLS.get(step_id, 2)
        
        if tool_call_count < min_calls:
            result.add_error(
                f"步骤 {step_id} 工具调用次数不足: {tool_call_count} < 要求 {min_calls}\n"
                f"请确保执行了足够的搜索、读取等操作！"
            )
            result.is_valid = False
        
        # 检查工具类型多样性（关键步骤）
        if step_id in ["step4", "step5"] and tool_types:
            required_types = {"web_search", "read"}
            missing = required_types - set(tool_types)
            if missing:
                result.add_warning(f"步骤 {step_id} 建议包含操作: {', '.join(missing)}")
        
        return result
    
    @classmethod
    def validate_generated_files(cls, step_id: str, cache_dir: str, company_name: str) -> StepValidationResult:
        """
        验证生成的文件
        
        Args:
            step_id: 步骤ID
            cache_dir: 缓存根目录
            company_name: 公司名称
        """
        result = StepValidationResult(True)
        required_patterns = cls.STEP_REQUIRED_FILES.get(step_id, [])
        
        if not required_patterns:
            return result
        
        company_cache = os.path.join(cache_dir, company_name)
        if not os.path.exists(company_cache):
            result.add_error(f"缓存目录不存在: {company_cache}")
            result.is_valid = False
            return result
        
        # 检查文件是否存在
        for pattern in required_patterns:
            if "*" in pattern:
                # 通配符模式，检查匹配的文件数量
                import glob
                matched = glob.glob(os.path.join(company_cache, pattern))
                if not matched:
                    result.add_error(f"步骤 {step_id} 缺少文件: {pattern}")
                    result.is_valid = False
                elif step_id == "step4" and len(matched) < 9:
                    result.add_error(f"步骤 {step_id} 维度文件不足: {len(matched)} < 9")
                    result.is_valid = False
            else:
                # 具体文件名
                file_path = os.path.join(company_cache, pattern)
                if not os.path.exists(file_path):
                    result.add_error(f"步骤 {step_id} 缺少必需文件: {pattern}")
                    result.is_valid = False
        
        return result
    
    @classmethod
    def validate_dimension_files(cls, cache_dir: str, company_name: str) -> StepValidationResult:
        """专门验证step4的维度文件质量"""
        result = StepValidationResult(True)
        company_cache = os.path.join(cache_dir, company_name)
        
        # 查找维度文件
        import glob
        dim_files = glob.glob(os.path.join(company_cache, "dimension-*.md"))
        
        if len(dim_files) < 9:
            result.add_error(f"维度文件数量不足: {len(dim_files)} < 9")
            result.is_valid = False
            return result
        
        # 检查每个维度文件的内容
        for dim_file in dim_files:
            try:
                with open(dim_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查长度
                if len(content) < 500:
                    result.add_error(f"维度文件内容过短: {os.path.basename(dim_file)} ({len(content)}字符)")
                    result.is_valid = False
                
                # 检查结构
                if "##" not in content:
                    result.add_warning(f"维度文件缺少结构化标题: {os.path.basename(dim_file)}")
                    
            except Exception as e:
                result.add_error(f"无法读取维度文件 {dim_file}: {e}")
                result.is_valid = False
        
        return result
    
    @classmethod
    def comprehensive_validation(
        cls,
        step_id: str,
        token_usage: int = None,
        content: str = None,
        tool_calls: int = None,
        tool_types: List[str] = None,
        cache_dir: str = None,
        company_name: str = None
    ) -> StepValidationResult:
        """
        综合验证 - 从多个维度评估步骤完成质量
        
        只要满足以下任意两项即通过：
        1. Token消耗达标
        2. 内容深度达标
        3. 工具调用达标
        4. 文件生成达标
        
        这样可以避免单一指标的误判，同时确保实际工作量
        """
        result = StepValidationResult(True)
        passed_checks = 0
        total_checks = 0
        
        # 1. Token验证（如果提供）
        if token_usage is not None:
            total_checks += 1
            token_result = cls.validate_token_usage(step_id, token_usage)
            if token_result.is_valid:
                passed_checks += 1
            else:
                for error in token_result.errors:
                    result.add_warning(f"[Token] {error}")  # 降级为警告
        
        # 2. 内容深度验证（如果提供）
        if content is not None:
            total_checks += 1
            content_result = cls.validate_content_depth(step_id, content)
            if content_result.is_valid:
                passed_checks += 1
            else:
                for error in content_result.errors:
                    result.is_valid = False
                    result.add_error(f"[内容] {error}")  # 内容不足是硬错误
        
        # 3. 工具调用验证（如果提供）
        if tool_calls is not None:
            total_checks += 1
            tool_result = cls.validate_tool_calls(step_id, tool_calls, tool_types)
            if tool_result.is_valid:
                passed_checks += 1
            else:
                for error in tool_result.errors:
                    result.add_warning(f"[工具] {error}")  # 降级为警告
        
        # 4. 文件生成验证（如果提供）
        if cache_dir and company_name:
            total_checks += 1
            file_result = cls.validate_generated_files(step_id, cache_dir, company_name)
            if file_result.is_valid:
                passed_checks += 1
            else:
                for error in file_result.errors:
                    result.is_valid = False
                    result.add_error(f"[文件] {error}")  # 文件缺失是硬错误
        
        # 特殊：step4需要额外检查维度文件
        if step_id == "step4" and cache_dir and company_name:
            dim_result = cls.validate_dimension_files(cache_dir, company_name)
            if not dim_result.is_valid:
                result.is_valid = False
                for error in dim_result.errors:
                    result.add_error(f"[维度] {error}")
        
        # 综合判断：内容或文件必须有一项通过，其他可互补
        if total_checks >= 2:
            # 如果有两项以上检查，要求至少两项通过
            if passed_checks < 2:
                result.is_valid = False
                result.add_error(
                    f"步骤 {step_id} 综合验证未通过: 仅通过 {passed_checks}/{total_checks} 项检查\n"
                    f"请确保：内容深度达标、文件生成完整、工具调用充足（满足任意两项）"
                )
        
        return result


# 保留旧的类名以保持兼容性，但使用新的实现
class TokenUsageValidator(AntiSkippingValidator):
    """兼容性保留，功能已合并到 AntiSkippingValidator"""
    pass


class ContentDepthValidator:
    """内容深度验证器 - 验证分析内容的质量和深度"""
    
    @staticmethod
    def validate_dimension_files(cache_dir: str, company_name: str, expected_dimensions: int = 9) -> StepValidationResult:
        """
        验证维度分析文件是否完整且内容达标
        
        Args:
            cache_dir: 缓存目录
            company_name: 公司名称
            expected_dimensions: 期望的维度数量
            
        Returns:
            StepValidationResult: 验证结果
        """
        # 使用新类的实现
        return AntiSkippingValidator.validate_dimension_files(cache_dir, company_name)


# =============================================================================
# v2.5.1 新增：增强版验证器集成
# =============================================================================

class EnhancedValidatorV251:
    """
    增强版验证器 v2.5.1
    
    集成新的验证器：
    - ContentQualityValidator: 内容质量深度验证
    - ToolUsageValidator: 工具使用细分验证
    - CheckpointRegistry: 统一检查点注册
    
    用法:
        from enforcement_controller import EnhancedValidatorV251
        
        validator = EnhancedValidatorV251()
        result = validator.validate_step4_content_quality(content)
        result = validator.validate_step4_tool_usage(tool_calls)
    """
    
    def __init__(self):
        self._content_validator = None
        self._tool_validator = None
        self._registry = None
        self._initialized = False
    
    def _init_validators(self):
        """延迟初始化验证器"""
        if self._initialized:
            return
        
        try:
            from .validators.content_quality_validator import ContentQualityValidator
            from .validators.tool_usage_validator import ToolUsageValidator
            from .checkpoint_registry import CheckpointRegistry
            
            self._content_validator = ContentQualityValidator()
            self._tool_validator = ToolUsageValidator()
            self._registry = CheckpointRegistry()
            self._initialized = True
        except ImportError as e:
            print(f"[EnhancedValidatorV251] 警告: 无法导入v2.5.1验证器: {e}")
            self._initialized = False
    
    def validate_step4_content_quality(self, content: str) -> StepValidationResult:
        """
        验证Step4内容质量（v2.5.1增强版）
        
        除了字符数，还验证：
        - 数据点数量
        - 内容冗余度
        - 数据新鲜度
        - 结构层次
        """
        self._init_validators()
        
        if not self._initialized or self._content_validator is None:
            # 回退到基础验证
            return AntiSkippingValidator.validate_content_depth("step4", content)
        
        # 使用v2.5.1验证器
        checkpoint_result = self._content_validator.validate(content, "step4")
        
        # 转换为StepValidationResult
        result = StepValidationResult(checkpoint_result.passed)
        result.errors = checkpoint_result.errors
        result.warnings = checkpoint_result.warnings
        
        # 添加详细信息
        if checkpoint_result.details:
            detail_msg = f"内容质量评分: {checkpoint_result.score:.1f}/100 | "
            detail_msg += f"数据点: {checkpoint_result.details.get('data_points', 0)} | "
            detail_msg += f"冗余度: {checkpoint_result.details.get('redundancy_score', 0):.1%} | "
            detail_msg += f"新鲜度: {checkpoint_result.details.get('freshness_score', 0):.1%}"
            
            if not checkpoint_result.passed:
                result.add_error(detail_msg)
            else:
                result.add_warning(detail_msg)
        
        return result
    
    def validate_step4_tool_usage(self, tool_calls: List[Dict]) -> StepValidationResult:
        """
        验证Step4工具使用（v2.5.1增强版）
        
        除了调用次数，还验证：
        - 工具类型分布（搜索/读取/写入）
        - 数据源多样性
        - 搜索深度（翻页）
        - 重复搜索比例
        """
        self._init_validators()
        
        if not self._initialized or self._tool_validator is None:
            # 回退到基础验证
            return AntiSkippingValidator.validate_tool_calls("step4", len(tool_calls))
        
        # 使用v2.5.1验证器
        checkpoint_result = self._tool_validator.validate(tool_calls, "step4")
        
        # 转换为StepValidationResult
        result = StepValidationResult(checkpoint_result.passed)
        result.errors = checkpoint_result.errors
        result.warnings = checkpoint_result.warnings
        
        # 添加详细信息
        if checkpoint_result.details:
            detail_msg = f"工具使用评分: {checkpoint_result.score:.1f}/100 | "
            detail_msg += f"搜索: {checkpoint_result.details.get('web_search', 0)} | "
            detail_msg += f"读取: {checkpoint_result.details.get('file_read', 0)} | "
            detail_msg += f"写入: {checkpoint_result.details.get('file_write', 0)} | "
            detail_msg += f"数据源: {checkpoint_result.details.get('unique_sources', 0)}"
            
            if not checkpoint_result.passed:
                result.add_error(detail_msg)
            else:
                result.add_warning(detail_msg)
        
        return result
    
    def quick_content_check(self, content: str) -> Dict:
        """快速内容质量检查（用于实时监控）"""
        self._init_validators()
        
        if not self._initialized or self._content_validator is None:
            return {"passed": True, "message": "v2.5.1验证器未初始化"}
        
        return self._content_validator.quick_check(content, "step4")
    
    def quick_tool_check(self, tool_calls: List[Dict]) -> Dict:
        """快速工具使用检查（用于实时监控）"""
        self._init_validators()
        
        if not self._initialized or self._tool_validator is None:
            return {"passed": True, "message": "v2.5.1验证器未初始化"}
        
        return self._tool_validator.quick_check(tool_calls, "step4")
    
    def is_available(self) -> bool:
        """检查v2.5.1验证器是否可用"""
        self._init_validators()
        return self._initialized


# 全局实例（单例）
_enhanced_validator_v251 = None

def get_enhanced_validator_v251() -> EnhancedValidatorV251:
    """获取v2.5.1增强验证器实例"""
    global _enhanced_validator_v251
    if _enhanced_validator_v251 is None:
        _enhanced_validator_v251 = EnhancedValidatorV251()
    return _enhanced_validator_v251


class ContentDepthValidator:
    """
    内容深度验证器 - 验证分析内容的质量和深度
    """
    
    @staticmethod
    def validate_dimension_files(cache_dir: str, company_name: str, expected_dimensions: int = 9) -> StepValidationResult:
        """
        验证维度分析文件是否完整且内容达标
        
        Args:
            cache_dir: 缓存目录
            company_name: 公司名称
            expected_dimensions: 期望的维度数量
            
        Returns:
            StepValidationResult: 验证结果
        """
        result = StepValidationResult(True)
        
        company_cache_dir = os.path.join(cache_dir, company_name)
        
        # 检查缓存目录是否存在
        if not os.path.exists(company_cache_dir):
            result.add_error(f"❌ 公司缓存目录不存在: {company_cache_dir}")
            result.is_valid = False
            return result
        
        # 查找维度文件
        dimension_files = []
        for f in os.listdir(company_cache_dir):
            if f.startswith("dimension-") and f.endswith(".md"):
                dimension_files.append(f)
        
        # 检查维度文件数量
        if len(dimension_files) < expected_dimensions:
            result.add_error(
                f"❌ 维度文件不完整: 找到 {len(dimension_files)} 个，要求 {expected_dimensions} 个\n"
                f"缺失的维度文件必须补全！"
            )
            result.is_valid = False
        
        # 检查每个维度文件的内容深度
        for dim_file in dimension_files:
            file_path = os.path.join(company_cache_dir, dim_file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查文件大小
                file_size = len(content)
                if file_size < 1000:  # 至少1000字符
                    result.add_error(
                        f"❌ 维度文件内容过短: {dim_file} 仅 {file_size} 字符，要求至少1000字符"
                    )
                    result.is_valid = False
                elif file_size < 2000:
                    result.add_warning(
                        f"⚠️ 维度文件内容偏短: {dim_file} 仅 {file_size} 字符，建议补充"
                    )
                
                # 检查内容结构
                if "##" not in content:
                    result.add_warning(
                        f"⚠️ 维度文件缺少结构化标题: {dim_file}"
                    )
                    
            except Exception as e:
                result.add_error(f"❌ 无法读取维度文件 {dim_file}: {e}")
                result.is_valid = False
        
        return result
    
    @staticmethod
    def validate_report_content(report_path: str) -> StepValidationResult:
        """
        验证最终报告内容的完整性
        
        Args:
            report_path: 报告文件路径
            
        Returns:
            StepValidationResult: 验证结果
        """
        result = StepValidationResult(True)
        
        if not os.path.exists(report_path):
            result.add_error(f"❌ 报告文件不存在: {report_path}")
            result.is_valid = False
            return result
        
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            result.add_error(f"❌ 无法读取报告文件: {e}")
            result.is_valid = False
            return result
        
        # 检查必需章节
        required_sections = [
            "执行摘要",
            "关键财务指标", 
            "双曲线业务分析",
            "情景分析",
            "投资建议",
            "参数溯源"
        ]
        
        for section in required_sections:
            if section not in content:
                result.add_error(f"❌ 报告缺少必需章节: {section}")
                result.is_valid = False
        
        # 检查内容长度
        if len(content) < 10000:
            result.add_error(f"❌ 报告内容过短: {len(content)} 字符，要求至少10000字符")
            result.is_valid = False
        elif len(content) < 15000:
            result.add_warning(f"⚠️ 报告内容偏短: {len(content)} 字符，建议补充")
        
        # 检查数据丰富度
        data_indicators = content.count('%') + content.count('亿元') + content.count('万') + content.count('CAGR')
        if data_indicators < 20:
            result.add_warning(f"⚠️ 报告数据支撑可能不足（仅{data_indicators}个数据指标）")
        
        return result


# ============ 预定义验证函数 ============

def create_checklist_validator(checklist_path: str, step_id: str) -> Callable[[], StepValidationResult]:
    """创建基于checklist.md的验证函数"""
    def validator() -> StepValidationResult:
        result = StepValidationResult(True)

        if not os.path.exists(checklist_path):
            result.add_error(f"检查清单文件不存在: {checklist_path}")
            return result

        # 这里可以添加具体的checklist验证逻辑
        # 目前仅检查文件存在性
        result.add_warning(f"检查清单验证待实现: {checklist_path}")

        return result

    return validator

def create_report_validator(company_name: str, output_dir: str) -> Callable[[], StepValidationResult]:
    """创建基于validate_report.py的验证函数"""
    def validator() -> StepValidationResult:
        result = StepValidationResult(True)

        # 导入验证脚本
        try:
            # 这里需要根据实际路径导入
            validator_path = Path(__file__).parent.parent / "validate_report.py"
            if not validator_path.exists():
                result.add_error(f"验证脚本不存在: {validator_path}")
                return result

            # 运行验证脚本（简化版本）
            # 实际实现应该调用validate_report.py
            result.add_warning(f"报告验证待集成: {company_name}, {output_dir}")

        except Exception as e:
            result.add_error(f"验证脚本执行失败: {e}")

        return result

    return validator


# ============ 使用示例 ============

if __name__ == "__main__":
    """使用示例"""
    controller = EnforcementController("测试公司")

    # 打印初始状态
    controller.print_status_report()

    # 尝试执行步骤
    try:
        # 步骤0: 加载配置
        controller.start_step("step0")
        controller.complete_step("step0")

        # 步骤1: 初始化缓存
        controller.start_step("step1")
        controller.complete_step("step1")

        # 尝试跳过步骤2直接执行步骤3 (应该失败)
        try:
            controller.start_step("step3")
        except ValueError as e:
            print(f"预期错误: {e}")

        # 继续正常执行
        controller.start_step("step2")
        controller.complete_step("step2")

        controller.start_step("step3")
        controller.complete_step("step3")

        # 打印最终状态
        controller.print_status_report()

        # 验证完整执行
        validation = controller.enforce_complete_execution()
        print(f"完整执行验证: {'通过' if validation else '失败'}")
        if not validation:
            print(f"错误: {validation.errors}")

    except Exception as e:
        print(f"执行出错: {e}")


# =============================================================================
# Week 2 P1: 业务逻辑增强验证器集成
# =============================================================================

class BusinessLogicValidatorV251:
    """
    业务逻辑验证器 v2.5.1
    
    集成：
    - CAGRValidator: CAGR合理性验证
    - TracingValidator: 参数溯源验证
    - AutomatedChecklist: 检查清单自动化
    - DynamicThresholdManager: 动态阈值管理
    """
    
    def __init__(self):
        self._cagr_validator = None
        self._tracing_validator = None
        self._checklist = None
        self._threshold_manager = None
        self._initialized = False
    
    def _init_validators(self):
        """延迟初始化验证器"""
        if self._initialized:
            return
        
        try:
            from .validators.cagr_validator import CAGRValidator
            from .validators.tracing_validator import TracingValidator
            from .automated_checklist import AutomatedChecklist
            from .dynamic_threshold import DynamicThresholdManager
            
            self._cagr_validator = CAGRValidator()
            self._tracing_validator = TracingValidator()
            self._checklist = AutomatedChecklist()
            self._threshold_manager = DynamicThresholdManager()
            self._initialized = True
        except ImportError as e:
            print(f"[BusinessLogicValidatorV251] 警告: 无法导入验证器: {e}")
            self._initialized = False
    
    def validate_cagr_reasonableness(self, cagr: float, industry: str, 
                                     company: str, peers: List[str] = None) -> StepValidationResult:
        """验证CAGR合理性"""
        self._init_validators()
        
        if not self._initialized or self._cagr_validator is None:
            # 回退到基础验证
            result = StepValidationResult(True)
            result.add_warning("CAGR合理性验证器未初始化")
            return result
        
        checkpoint_result = self._cagr_validator.validate(cagr, industry, company, peers)
        
        result = StepValidationResult(checkpoint_result.passed)
        result.errors = checkpoint_result.errors
        result.warnings = checkpoint_result.warnings
        
        if checkpoint_result.details:
            detail_msg = f"CAGR合理性: {checkpoint_result.score:.1f}/100 | "
            benchmarks = checkpoint_result.details.get("benchmarks", {})
            if benchmarks.get("industry_avg"):
                detail_msg += f"行业平均: {benchmarks['industry_avg']:.1f}% | "
            if benchmarks.get("historical"):
                detail_msg += f"历史: {benchmarks['historical']:.1f}%"
            
            if not checkpoint_result.passed:
                result.add_error(detail_msg)
            else:
                result.add_warning(detail_msg)
        
        return result
    
    def validate_tracing_completeness(self, json_data: Dict) -> StepValidationResult:
        """验证参数溯源完整性"""
        self._init_validators()
        
        if not self._initialized or self._tracing_validator is None:
            result = StepValidationResult(True)
            result.add_warning("参数溯源验证器未初始化")
            return result
        
        checkpoint_result = self._tracing_validator.validate_report_tracing(json_data)
        
        result = StepValidationResult(checkpoint_result.passed)
        result.errors = checkpoint_result.errors
        result.warnings = checkpoint_result.warnings
        
        if checkpoint_result.details:
            metrics = checkpoint_result.details.get("metrics", {})
            detail_msg = f"溯源完整性: {metrics.get('trace_ratio', 0):.1%} | "
            detail_msg += f"关键参数: {metrics.get('critical_traced', 0)}/{len(self._tracing_validator.CRITICAL_PARAMS)}"
            
            if not checkpoint_result.passed:
                result.add_error(detail_msg)
            else:
                result.add_warning(detail_msg)
        
        return result
    
    def execute_checklist_for_step(self, step_id: str, context: "ValidationContext") -> StepValidationResult:
        """执行步骤检查清单"""
        self._init_validators()
        
        if not self._initialized or self._checklist is None:
            result = StepValidationResult(True)
            result.add_warning("检查清单自动化未初始化")
            return result
        
        return self._checklist.execute_checks_for_step(step_id, context)
    
    def get_dynamic_thresholds(self, step_id: str, company_profile: Dict[str, Any]) -> Dict:
        """获取动态阈值"""
        self._init_validators()
        
        if not self._initialized or self._threshold_manager is None:
            return {
                "tokens": 8000,
                "content_length": 5000,
                "tool_calls": 18,
                "note": "使用默认阈值（动态阈值系统未初始化）"
            }
        
        thresholds = self._threshold_manager.calculate_thresholds(step_id, company_profile)
        
        return {
            "tokens": thresholds.tokens,
            "content_length": thresholds.content_length,
            "tool_calls": thresholds.tool_calls,
            "data_points": thresholds.data_points,
            "applied_factor": thresholds.applied_factor,
            "factors": thresholds.factors_applied
        }
    
    def is_available(self) -> bool:
        """检查验证器是否可用"""
        self._init_validators()
        return self._initialized


# 全局实例（单例）
_business_logic_validator_v251 = None

def get_business_logic_validator_v251() -> BusinessLogicValidatorV251:
    """获取业务逻辑验证器实例"""
    global _business_logic_validator_v251
    if _business_logic_validator_v251 is None:
        _business_logic_validator_v251 = BusinessLogicValidatorV251()
    return _business_logic_validator_v251


# =============================================================================
# 统一的v2.5.1验证器接口
# =============================================================================

class UnifiedValidatorV251:
    """
    统一验证器 v2.5.1
    
    整合所有v2.5.1验证功能的统一接口
    """
    
    def __init__(self):
        self.enhanced = get_enhanced_validator_v251()
        self.business = get_business_logic_validator_v251()
    
    def validate_step4_comprehensive(self, content: str, tool_calls: List[Dict], 
                                     company_profile: Dict = None) -> Dict[str, StepValidationResult]:
        """综合验证Step4（内容质量+工具使用）"""
        results = {}
        
        # 内容质量验证
        results["content_quality"] = self.enhanced.validate_step4_content_quality(content)
        
        # 工具使用验证
        results["tool_usage"] = self.enhanced.validate_step4_tool_usage(tool_calls)
        
        return results
    
    def validate_step7_cagr(self, cagr: float, industry: str, 
                           company: str, peers: List[str] = None) -> StepValidationResult:
        """验证Step7 CAGR"""
        return self.business.validate_cagr_reasonableness(cagr, industry, company, peers)
    
    def validate_step9_report(self, json_data: Dict) -> Dict[str, StepValidationResult]:
        """验证Step9报告（溯源+检查清单）"""
        results = {}
        
        # 参数溯源验证
        results["tracing"] = self.business.validate_tracing_completeness(json_data)
        
        return results
    
    def get_step_thresholds(self, step_id: str, company_profile: Dict) -> Dict:
        """获取步骤阈值"""
        return self.business.get_dynamic_thresholds(step_id, company_profile)
    
    def is_v251_available(self) -> bool:
        """检查v2.5.1验证器是否可用"""
        return self.enhanced.is_available() and self.business.is_available()


# 全局统一验证器实例
_unified_validator_v251 = None

def get_unified_validator_v251() -> UnifiedValidatorV251:
    """获取统一验证器实例"""
    global _unified_validator_v251
    if _unified_validator_v251 is None:
        _unified_validator_v251 = UnifiedValidatorV251()
    return _unified_validator_v251


# =============================================================================
# Week 3-4: 智能功能与质量归因集成
# =============================================================================

class IntelligentValidatorV251:
    """
    智能验证器 v2.5.1
    
    集成：
    - IntelligentEarlyWarning: 智能预警系统
    - ConsistencyValidator: 数据一致性验证
    - QualityAttributionAnalyzer: 质量归因分析
    """
    
    def __init__(self):
        self._early_warning = None
        self._consistency_validator = None
        self._attribution_analyzer = None
        self._initialized = False
    
    def _init_validators(self):
        """延迟初始化"""
        if self._initialized:
            return
        
        try:
            from .intelligent_early_warning import IntelligentEarlyWarning
            from .validators.consistency_validator import ConsistencyValidator
            from .quality_attribution import QualityAttributionAnalyzer
            
            self._early_warning = IntelligentEarlyWarning()
            self._consistency_validator = ConsistencyValidator()
            self._attribution_analyzer = QualityAttributionAnalyzer()
            self._initialized = True
        except ImportError as e:
            print(f"[IntelligentValidatorV251] 警告: 无法导入验证器: {e}")
            self._initialized = False
    
    def monitor_execution(self, metrics: "StepMetrics") -> List:
        """监控执行并生成预警"""
        self._init_validators()
        
        if not self._initialized or self._early_warning is None:
            return []
        
        return self._early_warning.monitor_step_execution(metrics)
    
    def validate_consistency(self, json_path: str, md_path: str) -> StepValidationResult:
        """验证数据一致性"""
        self._init_validators()
        
        if not self._initialized or self._consistency_validator is None:
            result = StepValidationResult(True)
            result.add_warning("数据一致性验证器未初始化")
            return result
        
        checkpoint_result = self._consistency_validator.validate_json_md_consistency(json_path, md_path)
        
        result = StepValidationResult(checkpoint_result.passed)
        result.errors = checkpoint_result.errors
        result.warnings = checkpoint_result.warnings
        
        return result
    
    def analyze_quality(self, checkpoint_results: List, context: Dict) -> Dict:
        """分析质量问题归因"""
        self._init_validators()
        
        if not self._initialized or self._attribution_analyzer is None:
            return {"has_issues": False, "message": "质量归因分析器未初始化"}
        
        return self._attribution_analyzer.analyze(checkpoint_results, context)
    
    def is_available(self) -> bool:
        """检查验证器是否可用"""
        self._init_validators()
        return self._initialized


# 全局实例
_intelligent_validator_v251 = None

def get_intelligent_validator_v251() -> IntelligentValidatorV251:
    """获取智能验证器实例"""
    global _intelligent_validator_v251
    if _intelligent_validator_v251 is None:
        _intelligent_validator_v251 = IntelligentValidatorV251()
    return _intelligent_validator_v251


# =============================================================================
# v2.5.1 完整验证器统一接口
# =============================================================================

class CompleteValidatorV251:
    """
    v2.5.1 完整验证器
    
    整合所有验证功能的最终接口
    """
    
    def __init__(self):
        self.enhanced = get_enhanced_validator_v251()
        self.business = get_business_logic_validator_v251()
        self.intelligent = get_intelligent_validator_v251()
        self.unified = get_unified_validator_v251()
    
    # Week 1-2 功能
    def validate_step4(self, content: str, tool_calls: List[Dict]) -> Dict:
        """完整验证Step4"""
        return self.unified.validate_step4_comprehensive(content, tool_calls)
    
    def validate_step7(self, cagr: float, industry: str, company: str) -> StepValidationResult:
        """验证Step7 CAGR"""
        return self.unified.validate_step7_cagr(cagr, industry, company)
    
    def get_thresholds(self, step_id: str, profile: Dict) -> Dict:
        """获取动态阈值"""
        return self.unified.get_step_thresholds(step_id, profile)
    
    # Week 3-4 功能
    def validate_consistency(self, json_path: str, md_path: str) -> StepValidationResult:
        """验证数据一致性"""
        return self.intelligent.validate_consistency(json_path, md_path)
    
    def analyze_quality(self, results: List, context: Dict) -> Dict:
        """分析质量问题"""
        return self.intelligent.analyze_quality(results, context)
    
    def is_v251_available(self) -> bool:
        """检查v2.5.1是否完全可用"""
        return (
            self.enhanced.is_available() and
            self.business.is_available() and
            self.intelligent.is_available()
        )


# 全局完整验证器实例
_complete_validator_v251 = None

def get_complete_validator_v251() -> CompleteValidatorV251:
    """获取完整验证器实例"""
    global _complete_validator_v251
    if _complete_validator_v251 is None:
        _complete_validator_v251 = CompleteValidatorV251()
    return _complete_validator_v251


# =============================================================================
# v2.5.1 配置启用控制
# =============================================================================

V251_CONFIG = {
    "enabled": True,  # 是否启用v2.5.1验证器
    "fallback_to_legacy": True,  # 失败时回退到旧版
    "content_quality_enabled": True,
    "tool_usage_detailed_enabled": True,
    "cagr_validation_enabled": True,
    "tracing_validation_enabled": True,
    "dynamic_threshold_enabled": True,
    "early_warning_enabled": True,
    "consistency_validation_enabled": True,
    "quality_attribution_enabled": True
}

def is_v251_enabled() -> bool:
    """检查v2.5.1功能是否启用"""
    return V251_CONFIG.get("enabled", True)