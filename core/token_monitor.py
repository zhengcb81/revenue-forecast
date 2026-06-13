"""
Token使用监控模块
版本: v1.0
创建日期: 2026-01-17

功能:
1. 估算步骤所需token
2. 监控实际token使用
3. token不足时提前报告错误
4. 防止因token限制而生成简化报告
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
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

class TokenEstimator:
    """Token估算器"""

    # 平均token消耗（基于经验数据）
    TOKEN_PER_CHAR = 0.3  # 中文约0.3 token/字符
    TOKEN_PER_WORD = 1.3  # 英文约1.3 token/单词

    # 步骤基础token消耗（估算值）
    STEP_TOKEN_COSTS = {
        "step0": 500,      # 加载配置
        "step1": 800,      # 初始化缓存
        "step2": 1200,     # 判断公司类型
        "step3": 1000,     # 语言策略判断
        "step4": 50000,    # 9维度研究（最大消耗）
        "step4_5": 8000,   # 品牌矩阵分析
        "step5": 3000,     # 公司类型专项分析
        "step6": 2000,     # 情景预测
        "step7": 1500,     # 综合CAGR计算
        "step8": 1000,     # 综合评分
        "step9": 8000,     # 生成报告
        "step9_5": 500,    # 报告验证
        "step10": 1000     # 更新缓存
    }

    # 搜索操作额外消耗
    SEARCH_TOKEN_COST = 2000  # 每次搜索约2000 tokens

    @classmethod
    def estimate_text_tokens(cls, text: str) -> int:
        """估算文本的token数量"""
        if not text:
            return 0

        # 检测中英文比例
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        total_chars = len(text)

        if chinese_chars > total_chars * 0.5:
            # 以中文为主
            return int(total_chars * cls.TOKEN_PER_CHAR)
        else:
            # 以英文为主
            words = text.split()
            return int(len(words) * cls.TOKEN_PER_WORD)

    @classmethod
    def estimate_step_tokens(cls, step_id: str, search_count: int = 0) -> int:
        """估算步骤所需token"""
        base_cost = cls.STEP_TOKEN_COSTS.get(step_id, 1000)
        search_cost = search_count * cls.SEARCH_TOKEN_COST
        return base_cost + search_cost

    @classmethod
    def estimate_total_tokens(cls, steps: List[str], search_counts: Dict[str, int] = None) -> int:
        """估算总token消耗"""
        total = 0
        search_counts = search_counts or {}

        for step_id in steps:
            search_count = search_counts.get(step_id, 0)
            total += cls.estimate_step_tokens(step_id, search_count)

        return total

    @classmethod
    def get_token_budget(cls) -> int:
        """获取可用token预算"""
        # Claude Sonnet 4.5默认约200K tokens
        # 保守估计使用180K
        return 180000

    @classmethod
    def get_buffer_tokens(cls) -> int:
        """获取缓冲token（用于错误处理和报告）"""
        return 20000


class TokenMonitor:
    """Token监控器"""

    def __init__(self, company_name: str, token_budget: int = None):
        self.company_name = company_name
        self.token_budget = token_budget or TokenEstimator.get_token_budget()
        self.buffer_tokens = TokenEstimator.get_buffer_tokens()
        self.effective_budget = self.token_budget - self.buffer_tokens

        self.step_estimates: Dict[str, int] = {}
        self.step_actual_usage: Dict[str, int] = {}
        self.total_estimated = 0
        self.total_used = 0
        self.warnings: List[str] = []

    def estimate_analysis(self, steps: List[str], search_counts: Dict[str, int] = None) -> bool:
        """估算分析是否可行"""
        self.total_estimated = TokenEstimator.estimate_total_tokens(steps, search_counts)

        # 记录每步估算
        for step_id in steps:
            search_count = search_counts.get(step_id, 0) if search_counts else 0
            estimate = TokenEstimator.estimate_step_tokens(step_id, search_count)
            self.step_estimates[step_id] = estimate

        # 检查是否超出预算
        if self.total_estimated > self.effective_budget:
            self.warnings.append(
                f"⚠️ Token估算超限: 预计使用 {self.total_estimated:,} tokens，"
                f"预算 {self.effective_budget:,} tokens"
            )
            return False

        return True

    def check_step_feasibility(self, step_id: str, search_count: int = 0) -> Tuple[bool, str]:
        """检查单个步骤是否可行"""
        # 估算当前步骤
        step_estimate = TokenEstimator.estimate_step_tokens(step_id, search_count)

        # 估算剩余步骤（基于标准流程）
        remaining_steps = self._get_remaining_steps(step_id)
        remaining_estimate = TokenEstimator.estimate_total_tokens(remaining_steps)

        # 总计（已用 + 当前 + 剩余）
        total_needed = self.total_used + step_estimate + remaining_estimate

        if total_needed > self.effective_budget:
            return False, (
                f"步骤 {step_id} 无法执行: 预计需要 {total_needed:,} tokens，"
                f"剩余预算 {self.effective_budget - self.total_used:,} tokens。"
                f"建议: 减少搜索次数或分批执行。"
            )

        return True, f"Token预算充足，预计使用 {step_estimate:,} tokens"

    def _get_remaining_steps(self, current_step: str) -> List[str]:
        """获取剩余步骤列表"""
        all_steps = [
            "step0", "step1", "step2", "step3", "step4", "step4_5", "step5",
            "step6", "step7", "step8", "step9", "step9_5", "step10"
        ]

        try:
            idx = all_steps.index(current_step)
            return all_steps[idx + 1:]
        except ValueError:
            return []

    def record_step_usage(self, step_id: str, estimated: int):
        """记录步骤token使用（估算值）"""
        self.step_actual_usage[step_id] = estimated
        self.total_used += estimated

    def get_remaining_budget(self) -> int:
        """获取剩余token预算"""
        return self.effective_budget - self.total_used

    def get_usage_summary(self) -> Dict:
        """获取使用摘要"""
        return {
            "company_name": self.company_name,
            "token_budget": self.token_budget,
            "effective_budget": self.effective_budget,
            "total_estimated": self.total_estimated,
            "total_used": self.total_used,
            "remaining": self.get_remaining_budget(),
            "usage_percentage": (self.total_used / self.effective_budget * 100) if self.effective_budget > 0 else 0,
            "step_estimates": self.step_estimates,
            "step_actual_usage": self.step_actual_usage,
            "warnings": self.warnings
        }

    def print_report(self):
        """打印token使用报告"""
        summary = self.get_usage_summary()

        print("=" * 70)
        print("Token使用监控报告")
        print("=" * 70)
        print(f"公司: {self.company_name}")
        print(f"总预算: {summary['token_budget']:,} tokens")
        print(f"有效预算: {summary['effective_budget']:,} tokens (扣除缓冲)")
        print()
        print(f"已使用: {summary['total_used']:,} tokens ({summary['usage_percentage']:.1f}%)")
        print(f"剩余: {summary['remaining']:,} tokens")
        print()

        print("步骤Token估算:")
        print("-" * 70)
        for step_id, estimate in summary['step_estimates'].items():
            used = summary['step_actual_usage'].get(step_id, 0)
            status = "✅" if used > 0 else "⏳"
            print(f"{status} {step_id}: {estimate:,} tokens (已用: {used:,})")

        if summary['warnings']:
            print()
            print("警告:")
            for warning in summary['warnings']:
                print(f"  {warning}")

        print("=" * 70)


class TokenEnforcement:
    """Token强制执行器"""

    def __init__(self, company_name: str):
        self.monitor = TokenMonitor(company_name)

    def validate_before_analysis(self, steps: List[str], search_counts: Dict[str, int] = None) -> StepValidationResult:
        """分析前验证token预算"""
        from .enforcement_controller import StepValidationResult

        result = StepValidationResult(True)

        # 执行估算
        feasible = self.monitor.estimate_analysis(steps, search_counts)

        if not feasible:
            for warning in self.monitor.warnings:
                result.add_error(warning)

            # 添加建议
            result.add_warning("建议: 减少搜索次数或分批执行分析")
            result.add_warning("禁止: 不得因token限制而生成简化版报告")

        return result

    def validate_before_step(self, step_id: str, search_count: int = 0) -> StepValidationResult:
        """步骤前验证token预算"""
        from .enforcement_controller import StepValidationResult

        result = StepValidationResult(True)
        feasible, message = self.monitor.check_step_feasibility(step_id, search_count)

        if not feasible:
            result.add_error(message)
            result.add_error("禁止跳过此步骤或生成简化报告")
            result.add_warning("建议: 减少搜索次数或分批执行")

        return result

    def record_step(self, step_id: str, search_count: int = 0):
        """记录步骤完成"""
        estimate = TokenEstimator.estimate_step_tokens(step_id, search_count)
        self.monitor.record_step_usage(step_id, estimate)

    def enforce_no_simplification(self) -> StepValidationResult:
        """强制执行：不得生成简化报告"""
        from .enforcement_controller import StepValidationResult

        result = StepValidationResult(True)

        # 检查是否有步骤被跳过
        if self.monitor.total_used < self.monitor.total_estimated * 0.5:
            result.add_error(
                f"⚠️ 疑似生成简化报告: 实际使用 {self.monitor.total_used:,} tokens，"
                f"估算 {self.monitor.total_estimated:,} tokens"
            )
            result.add_error("禁止: 不得因token限制而跳过步骤或简化报告")

        return result


# ============ 使用示例 ============

if __name__ == "__main__":
    """使用示例"""
    print("=" * 70)
    print("Token监控器测试")
    print("=" * 70)

    # 创建监控器
    company = "测试公司"
    enforcer = TokenEnforcement(company)

    # 模拟搜索次数
    search_counts = {
        "step4": 25,  # 9维度研究，25次搜索
        "step4_5": 6  # 品牌矩阵，6次搜索
    }

    # 分析前验证
    print("\n1. 分析前Token验证:")
    print("-" * 70)
    steps = ["step0", "step1", "step2", "step3", "step4", "step4_5", "step5", "step6", "step7", "step8", "step9", "step9_5", "step10"]
    validation = enforcer.validate_before_analysis(steps, search_counts)

    if validation:
        print("✅ Token预算充足")
        print(f"   预计使用: {enforcer.monitor.total_estimated:,} tokens")
        print(f"   有效预算: {enforcer.monitor.effective_budget:,} tokens")
    else:
        print("❌ Token预算不足")
        for error in validation.errors:
            print(f"   {error}")
        for warning in validation.warnings:
            print(f"   {warning}")

    # 模拟执行步骤
    print("\n2. 模拟执行步骤:")
    print("-" * 70)

    for step_id in ["step0", "step1", "step2", "step3"]:
        # 步骤前验证
        step_validation = enforcer.validate_before_step(step_id)
        if step_validation:
            print(f"✅ {step_id}: Token充足")
            enforcer.record_step(step_id)
        else:
            print(f"❌ {step_id}: Token不足 - {step_validation.errors[0]}")
            break

    # 打印使用报告
    enforcer.monitor.print_report()

    # 简化报告检查
    print("\n3. 简化报告检查:")
    print("-" * 70)
    simplification_check = enforcer.enforce_no_simplification()
    if simplification_check:
        print("✅ 未检测到简化报告")
    else:
        print("❌ 疑似生成简化报告:")
        for error in simplification_check.errors:
            print(f"   {error}")

    print("=" * 70)
