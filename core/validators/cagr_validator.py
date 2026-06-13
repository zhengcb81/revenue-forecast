"""
Revenue Forecast - CAGR合理性验证器 v2.5.1
版本: v1.0
创建日期: 2026-03-01

功能:
1. 与行业平均对比
2. 与公司历史对比
3. 与同业对比
4. 绝对值合理性检查
5. 生成合理性论证要求
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

import json
import os
import sys
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from checkpoint_registry import CheckpointResult, ValidationContext


@dataclass
class CAGRBenchmark:
    """CAGR基准数据"""
    industry_avg: Optional[float] = None
    industry_high: Optional[float] = None
    industry_low: Optional[float] = None
    historical: Optional[float] = None
    peer_avg: Optional[float] = None
    peer_max: Optional[float] = None
    peer_min: Optional[float] = None
    
    def to_dict(self) -> Dict:
        return {
            "industry_avg": self.industry_avg,
            "industry_high": self.industry_high,
            "industry_low": self.industry_low,
            "historical": self.historical,
            "peer_avg": self.peer_avg,
            "peer_max": self.peer_max,
            "peer_min": self.peer_min
        }


class CAGRValidator:
    """
    CAGR合理性验证器
    
    验证预测的CAGR是否合理，避免过于乐观或悲观
    """
    
    # 验证规则配置
    VALIDATION_RULES = {
        "vs_industry": {
            "max_multiple": 3.0,      # 不能超过行业平均3倍
            "warning_multiple": 2.0,  # 超过2倍警告
            "min_deviation": -50      # 不能低于行业平均50pp
        },
        "vs_historical": {
            "max_deviation": 15,      # 与历史差异不超过15pp
            "warning_deviation": 10   # 超过10pp警告
        },
        "vs_peers": {
            "max_vs_max": 1.5,        # 不能超过同业最高1.5倍
            "max_vs_avg": 2.5,        # 不能超过同业平均2.5倍
            "warning_vs_avg": 2.0     # 超过2倍警告
        },
        "absolute": {
            "extreme_high": 50,       # >50%需要额外论证
            "warning_high": 30,       # >30%警告
            "extreme_low": -20,       # <-20%需要额外论证
            "min_reasonable": -10     # 最低合理值
        }
    }
    
    def __init__(self, rules: Optional[Dict] = None):
        """
        初始化验证器
        
        Args:
            rules: 自定义验证规则
        """
        self.rules = rules or self.VALIDATION_RULES
        self._benchmarks_cache = {}
    
    def validate(self, cagr: float, industry: str, company: str, 
                 peers: Optional[List[str]] = None,
                 context: Optional[ValidationContext] = None) -> CheckpointResult:
        """
        验证CAGR合理性
        
        Args:
            cagr: 预测的CAGR (%)
            industry: 行业名称
            company: 公司名称
            peers: 同业公司列表
            context: 验证上下文
            
        Returns:
            CheckpointResult: 验证结果
        """
        # 获取基准数据
        benchmarks = self._get_benchmarks(industry, company, peers)
        
        # 执行各项验证
        checks = []
        errors = []
        warnings = []
        suggestions = []
        
        # 1. 与行业平均对比
        if benchmarks.industry_avg is not None:
            passed, msg = self._check_vs_industry(cagr, benchmarks.industry_avg)
            checks.append(("vs_industry", passed, cagr, benchmarks.industry_avg))
            if not passed:
                errors.append(msg)
                suggestions.append(f"行业平均CAGR为{benchmarks.industry_avg:.1f}%，建议重新评估增长假设")
            elif cagr > benchmarks.industry_avg * self.rules["vs_industry"]["warning_multiple"]:
                warnings.append(f"CAGR({cagr}%)显著高于行业平均({benchmarks.industry_avg:.1f}%)")
        
        # 2. 与公司历史对比
        if benchmarks.historical is not None:
            passed, msg = self._check_vs_historical(cagr, benchmarks.historical)
            checks.append(("vs_historical", passed, cagr, benchmarks.historical))
            if not passed:
                errors.append(msg)
                suggestions.append("预测与历史表现差异过大，需要提供增长加速/减速的合理解释")
            elif abs(cagr - benchmarks.historical) > self.rules["vs_historical"]["warning_deviation"]:
                warnings.append(f"预测CAGR({cagr}%)与历史({benchmarks.historical:.1f}%)差异较大")
        
        # 3. 与同业对比
        if benchmarks.peer_max is not None and benchmarks.peer_avg is not None:
            passed, msg = self._check_vs_peers(cagr, benchmarks.peer_max, benchmarks.peer_avg)
            checks.append(("vs_peers", passed, cagr, benchmarks.peer_max))
            if not passed:
                errors.append(msg)
                suggestions.append(f"同业最高CAGR为{benchmarks.peer_max:.1f}%，需要提供超越同业的竞争优势论证")
            elif cagr > benchmarks.peer_avg * self.rules["vs_peers"]["warning_vs_avg"]:
                warnings.append(f"CAGR({cagr}%)显著高于同业平均({benchmarks.peer_avg:.1f}%)")
        
        # 4. 绝对值合理性
        passed, msg = self._check_absolute(cagr)
        checks.append(("absolute", passed, cagr, None))
        if not passed:
            errors.append(msg)
            if cagr > self.rules["absolute"]["extreme_high"]:
                suggestions.append("CAGR超过50%属于爆发式增长，需要提供详细的增长驱动因素和市场份额获取计划")
            elif cagr < self.rules["absolute"]["extreme_low"]:
                suggestions.append("CAGR低于-20%显示严重衰退，需要论证是否为暂时性下滑")
        elif cagr > self.rules["absolute"]["warning_high"]:
            warnings.append(f"CAGR({cagr}%)超过30%，属于高增长，需要验证可持续性")
        
        # 计算分数
        total_checks = len(checks)
        passed_checks = sum(1 for _, passed, _, _ in checks if passed)
        score = (passed_checks / total_checks * 100) if total_checks > 0 else 100
        
        # 判断是否通过
        all_passed = len(errors) == 0
        
        # 生成详细消息
        if all_passed:
            message = f"CAGR合理性验证通过 (评分: {score:.1f}/100)"
            if warnings:
                message += f"，有{len(warnings)}项警告"
        else:
            message = f"CAGR合理性验证未通过 (评分: {score:.1f}/100)，{len(errors)}项错误"
        
        return CheckpointResult(
            checkpoint_id="step7_cagr_reasonableness",
            passed=all_passed,
            score=score,
            message=message,
            details={
                "cagr": cagr,
                "benchmarks": benchmarks.to_dict(),
                "checks": {name: passed for name, passed, _, _ in checks}
            },
            errors=errors,
            warnings=warnings,
            suggestions=suggestions
        )
    
    def _check_vs_industry(self, cagr: float, industry_avg: float) -> Tuple[bool, str]:
        """检查与行业平均的对比"""
        max_multiple = self.rules["vs_industry"]["max_multiple"]
        
        if cagr > industry_avg * max_multiple:
            return False, f"CAGR({cagr}%)远高于行业平均({industry_avg:.1f}%)的{max_multiple}倍"
        
        if cagr < industry_avg + self.rules["vs_industry"]["min_deviation"]:
            return False, f"CAGR({cagr}%)远低于行业平均({industry_avg:.1f}%)"
        
        return True, ""
    
    def _check_vs_historical(self, cagr: float, historical: float) -> Tuple[bool, str]:
        """检查与历史表现的对比"""
        max_deviation = self.rules["vs_historical"]["max_deviation"]
        deviation = abs(cagr - historical)
        
        if deviation > max_deviation:
            direction = "增长" if cagr > historical else "下降"
            return False, f"预测CAGR({cagr}%)与历史({historical:.1f}%)差异{deviation:.1f}pp，{direction}过快"
        
        return True, ""
    
    def _check_vs_peers(self, cagr: float, peer_max: float, peer_avg: float) -> Tuple[bool, str]:
        """检查与同业的对比"""
        max_vs_max = self.rules["vs_peers"]["max_vs_max"]
        max_vs_avg = self.rules["vs_peers"]["max_vs_avg"]
        
        if cagr > peer_max * max_vs_max:
            return False, f"CAGR({cagr}%)显著高于同业最高({peer_max:.1f}%)的{max_vs_max}倍"
        
        if cagr > peer_avg * max_vs_avg:
            return False, f"CAGR({cagr}%)远高于同业平均({peer_avg:.1f}%)的{max_vs_avg}倍"
        
        return True, ""
    
    def _check_absolute(self, cagr: float) -> Tuple[bool, str]:
        """检查绝对值合理性"""
        extreme_high = self.rules["absolute"]["extreme_high"]
        extreme_low = self.rules["absolute"]["extreme_low"]
        min_reasonable = self.rules["absolute"]["min_reasonable"]
        
        if cagr > extreme_high:
            return False, f"CAGR({cagr}%)超过{extreme_high}%，属于极端高增长"
        
        if cagr < extreme_low:
            return False, f"CAGR({cagr}%)低于{extreme_low}%，显示严重衰退"
        
        if cagr < min_reasonable:
            return False, f"CAGR({cagr}%)过低，投资回报可能不理想"
        
        return True, ""
    
    def _get_benchmarks(self, industry: str, company: str, 
                        peers: Optional[List[str]] = None) -> CAGRBenchmark:
        """获取基准数据"""
        cache_key = f"{industry}_{company}"
        if cache_key in self._benchmarks_cache:
            return self._benchmarks_cache[cache_key]
        
        benchmarks = CAGRBenchmark()
        
        # 从行业数据模块获取
        try:
            from ..industry_data import IndustryData
            data = IndustryData()
            benchmarks.industry_avg = data.get_industry_cagr(industry, "avg")
            benchmarks.industry_high = data.get_industry_cagr(industry, "high")
            benchmarks.industry_low = data.get_industry_cagr(industry, "low")
        except ImportError:
            # 使用内置数据
            benchmarks.industry_avg = self._get_builtin_industry_cagr(industry)
        
        # 获取公司历史CAGR
        benchmarks.historical = self._get_company_historical_cagr(company)
        
        # 获取同业数据
        if peers:
            peer_cagrs = [self._get_company_historical_cagr(p) for p in peers]
            peer_cagrs = [c for c in peer_cagrs if c is not None]
            if peer_cagrs:
                benchmarks.peer_avg = sum(peer_cagrs) / len(peer_cagrs)
                benchmarks.peer_max = max(peer_cagrs)
                benchmarks.peer_min = min(peer_cagrs)
        
        self._benchmarks_cache[cache_key] = benchmarks
        return benchmarks
    
    def _get_builtin_industry_cagr(self, industry: str) -> Optional[float]:
        """获取内置行业CAGR数据"""
        # 简化版内置数据
        builtin_data = {
            "technology": 12.0,
            "software": 15.0,
            "hardware": 8.0,
            "semiconductor": 10.0,
            "consumer_electronics": 6.0,
            "automotive": 5.0,
            "new_energy": 20.0,
            "pharmaceutical": 8.0,
            "healthcare": 10.0,
            "financial": 6.0,
            "banking": 5.0,
            "insurance": 7.0,
            "retail": 5.0,
            "e_commerce": 15.0,
            "manufacturing": 4.0,
            "energy": 3.0,
            "utilities": 2.0,
            "real_estate": 2.0,
            "construction": 3.0,
            "materials": 4.0
        }
        
        # 标准化行业名称
        industry_normalized = industry.lower().replace(" ", "_").replace("-", "_")
        return builtin_data.get(industry_normalized)
    
    def _get_company_historical_cagr(self, company: str) -> Optional[float]:
        """获取公司历史CAGR"""
        # 从缓存或数据库获取
        # 这里简化实现，返回None表示无数据
        return None
    
    def generate_reasoning_requirements(self, cagr: float, benchmarks: CAGRBenchmark) -> List[str]:
        """生成需要论证的问题列表"""
        requirements = []
        
        if benchmarks.industry_avg and cagr > benchmarks.industry_avg * 2:
            requirements.append(f"为什么公司能实现{benchmarks.industry_avg:.1f}%行业平均的{cagr/benchmarks.industry_avg:.1f}倍增长？")
        
        if benchmarks.historical and abs(cagr - benchmarks.historical) > 10:
            direction = "加速" if cagr > benchmarks.historical else "减速"
            requirements.append(f"相比历史CAGR({benchmarks.historical:.1f}%)，增长的{direction}驱动因素是什么？")
        
        if benchmarks.peer_max and cagr > benchmarks.peer_max:
            requirements.append(f"如何超越同业最高({benchmarks.peer_max:.1f}%)的？")
        
        if cagr > 30:
            requirements.append("高增长(>30%)的可持续性如何？市场容量是否足够？")
        
        if cagr > 50:
            requirements.append("爆发式增长(>50%)的退出风险如何？")
        
        return requirements


# 便捷函数
def validate_cagr(cagr: float, industry: str, company: str, 
                  peers: Optional[List[str]] = None) -> CheckpointResult:
    """
    便捷函数：验证CAGR合理性
    
    Args:
        cagr: 预测的CAGR (%)
        industry: 行业名称
        company: 公司名称
        peers: 同业公司列表
        
    Returns:
        CheckpointResult: 验证结果
    """
    validator = CAGRValidator()
    return validator.validate(cagr, industry, company, peers)


if __name__ == "__main__":
    # 测试
    print("=" * 60)
    print("CAGRValidator 测试")
    print("=" * 60)
    
    validator = CAGRValidator()
    
    # 测试合理CAGR
    print("\n合理CAGR测试 (25%, technology行业):")
    result = validator.validate(25, "technology", "测试公司", ["竞品A", "竞品B"])
    print(f"  通过: {result.passed}")
    print(f"  分数: {result.score:.1f}")
    print(f"  消息: {result.message}")
    print(f"  警告: {result.warnings}")
    
    # 测试过高CAGR
    print("\n过高CAGR测试 (80%, technology行业):")
    result = validator.validate(80, "technology", "测试公司")
    print(f"  通过: {result.passed}")
    print(f"  分数: {result.score:.1f}")
    print(f"  错误: {result.errors}")
    print(f"  建议: {result.suggestions}")
    
    # 测试过低CAGR
    print("\n过低CAGR测试 (-30%, retail行业):")
    result = validator.validate(-30, "retail", "测试公司")
    print(f"  通过: {result.passed}")
    print(f"  分数: {result.score:.1f}")
    print(f"  错误: {result.errors}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
