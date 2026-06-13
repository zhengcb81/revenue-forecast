"""
Revenue Forecast - 动态阈值系统 v2.5.1
版本: v1.0
创建日期: 2026-03-01

功能:
1. 根据公司特征动态调整阈值
2. 支持多种复杂度因子
3. 阈值调整和记录
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
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


@dataclass
class Thresholds:
    """阈值配置"""
    tokens: int
    content_length: int
    tool_calls: int
    data_points: int
    applied_factor: float = 1.0
    factors_applied: Dict[str, float] = None


class DynamicThresholdManager:
    """
    动态阈值管理器
    
    根据公司复杂度动态调整验证阈值
    """
    
    # 基础阈值
    BASE_THRESHOLDS = {
        "step4": Thresholds(
            tokens=8000,
            content_length=5000,
            tool_calls=18,
            data_points=20
        ),
        "step5": Thresholds(
            tokens=6000,
            content_length=4000,
            tool_calls=12,
            data_points=15
        ),
        "step6": Thresholds(
            tokens=4000,
            content_length=3000,
            tool_calls=8,
            data_points=10
        )
    }
    
    # 复杂度因子配置
    COMPLEXITY_FACTORS = {
        # 公司规模
        "market_cap": {
            "large": 1.3,      # 千亿以上
            "medium": 1.0,     # 百亿-千亿
            "small": 0.8       # 百亿以下
        },
        
        # 业务复杂度
        "business_segments": {
            "conglomerate": 1.5,      # 集团型（5+业务）
            "diversified": 1.2,       # 多元化（3-5业务）
            "multi_product": 1.1,     # 多产品（2-3业务）
            "single_product": 0.9     # 单一产品
        },
        
        # 行业特性
        "industry": {
            "financial": 1.3,         # 金融（数据密集）
            "technology": 1.2,        # 科技（快速变化）
            "healthcare": 1.15,       # 医疗（专业性强）
            "energy": 1.1,            # 能源（政策敏感）
            "manufacturing": 1.0,     # 制造（标准）
            "retail": 0.95,           # 零售（相对简单）
            "utilities": 0.9          # 公用事业（稳定）
        },
        
        # 上市状态
        "listing_status": {
            "listed": 1.1,            # 上市公司（信息披露完善）
            "unlisted": 1.0           # 非上市（数据获取难）
        },
        
        # 国际化程度
        "global_exposure": {
            "global": 1.2,            # 全球化（多市场分析）
            "regional": 1.0,          # 区域性
            "domestic": 0.95          # 纯国内
        },
        
        # 数据可得性
        "data_availability": {
            "high": 0.9,              # 数据丰富（可适当降低要求）
            "medium": 1.0,            # 数据适中
            "low": 1.2                # 数据稀缺（需要更多搜索）
        }
    }
    
    def __init__(self):
        """初始化动态阈值管理器"""
        self._threshold_history = []
    
    def calculate_thresholds(self, step_id: str, company_profile: Dict[str, Any]) -> Thresholds:
        """
        计算动态阈值
        
        Args:
            step_id: 步骤ID
            company_profile: 公司特征配置
                {
                    "market_cap": float,  # 市值（亿元）
                    "business_segments": int,  # 业务板块数量
                    "industry": str,  # 行业
                    "is_listed": bool,  # 是否上市
                    "global_exposure": str,  # 国际化程度
                    "data_availability": str  # 数据可得性
                }
                
        Returns:
            Thresholds: 调整后的阈值
        """
        # 获取基础阈值
        base = self.BASE_THRESHOLDS.get(step_id, self.BASE_THRESHOLDS["step4"])
        
        # 计算各维度因子
        factors = {}
        
        # 1. 公司规模因子
        market_cap = company_profile.get("market_cap", 500)
        if market_cap > 1000:
            factors["market_cap"] = self.COMPLEXITY_FACTORS["market_cap"]["large"]
        elif market_cap > 100:
            factors["market_cap"] = self.COMPLEXITY_FACTORS["market_cap"]["medium"]
        else:
            factors["market_cap"] = self.COMPLEXITY_FACTORS["market_cap"]["small"]
        
        # 2. 业务复杂度因子
        segments = company_profile.get("business_segments", 1)
        if segments >= 5:
            factors["business_segments"] = self.COMPLEXITY_FACTORS["business_segments"]["conglomerate"]
        elif segments >= 3:
            factors["business_segments"] = self.COMPLEXITY_FACTORS["business_segments"]["diversified"]
        elif segments >= 2:
            factors["business_segments"] = self.COMPLEXITY_FACTORS["business_segments"]["multi_product"]
        else:
            factors["business_segments"] = self.COMPLEXITY_FACTORS["business_segments"]["single_product"]
        
        # 3. 行业因子
        industry = company_profile.get("industry", "manufacturing").lower()
        factors["industry"] = self.COMPLEXITY_FACTORS["industry"].get(industry, 1.0)
        
        # 4. 上市状态因子
        is_listed = company_profile.get("is_listed", True)
        factors["listing_status"] = self.COMPLEXITY_FACTORS["listing_status"]["listed" if is_listed else "unlisted"]
        
        # 5. 国际化因子
        global_exp = company_profile.get("global_exposure", "domestic")
        factors["global_exposure"] = self.COMPLEXITY_FACTORS["global_exposure"].get(global_exp, 1.0)
        
        # 6. 数据可得性因子
        data_avail = company_profile.get("data_availability", "medium")
        factors["data_availability"] = self.COMPLEXITY_FACTORS["data_availability"].get(data_avail, 1.0)
        
        # 计算综合因子
        composite_factor = sum(factors.values()) / len(factors)
        
        # 应用因子（限制范围 0.7 - 1.5）
        composite_factor = max(0.7, min(1.5, composite_factor))
        
        # 调整阈值
        adjusted = Thresholds(
            tokens=int(base.tokens * composite_factor),
            content_length=int(base.content_length * composite_factor),
            tool_calls=int(base.tool_calls * composite_factor),
            data_points=int(base.data_points * composite_factor),
            applied_factor=composite_factor,
            factors_applied=factors
        )
        
        # 记录历史
        self._threshold_history.append({
            "step_id": step_id,
            "company": company_profile.get("name", "unknown"),
            "base": {
                "tokens": base.tokens,
                "content_length": base.content_length,
                "tool_calls": base.tool_calls,
                "data_points": base.data_points
            },
            "adjusted": {
                "tokens": adjusted.tokens,
                "content_length": adjusted.content_length,
                "tool_calls": adjusted.tool_calls,
                "data_points": adjusted.data_points
            },
            "factor": composite_factor,
            "factors": factors
        })
        
        return adjusted
    
    def get_thresholds_for_company(self, step_id: str, company_name: str, 
                                   company_profile: Dict[str, Any]) -> Dict:
        """
        获取公司特定的阈值（包含说明）
        
        Returns:
            Dict: 包含阈值和说明
        """
        thresholds = self.calculate_thresholds(step_id, company_profile)
        
        return {
            "step_id": step_id,
            "company": company_name,
            "thresholds": {
                "tokens": thresholds.tokens,
                "content_length": thresholds.content_length,
                "tool_calls": thresholds.tool_calls,
                "data_points": thresholds.data_points
            },
            "base_thresholds": {
                "tokens": self.BASE_THRESHOLDS[step_id].tokens,
                "content_length": self.BASE_THRESHOLDS[step_id].content_length,
                "tool_calls": self.BASE_THRESHOLDS[step_id].tool_calls,
                "data_points": self.BASE_THRESHOLDS[step_id].data_points
            },
            "applied_factor": round(thresholds.applied_factor, 2),
            "factors": thresholds.factors_applied,
            "explanation": self._generate_explanation(thresholds, company_profile)
        }
    
    def _generate_explanation(self, thresholds: Thresholds, profile: Dict) -> str:
        """生成阈值调整说明"""
        factor = thresholds.applied_factor
        
        if factor > 1.2:
            level = "较高"
            reason = "公司复杂度高"
        elif factor > 1.05:
            level = "偏高"
            reason = "公司有一定复杂度"
        elif factor < 0.85:
            level = "较低"
            reason = "公司相对简单"
        elif factor < 0.95:
            level = "偏低"
            reason = "公司较为简单"
        else:
            level = "标准"
            reason = "公司复杂度适中"
        
        factors_desc = []
        if profile.get("market_cap", 0) > 1000:
            factors_desc.append("大公司")
        if profile.get("business_segments", 1) > 3:
            factors_desc.append("多元化业务")
        if profile.get("global_exposure") == "global":
            factors_desc.append("全球化")
        if profile.get("data_availability") == "low":
            factors_desc.append("数据稀缺")
        
        explanation = f"阈值设置为{level}水平（调整系数: {factor:.2f}）"
        if factors_desc:
            explanation += f"，因为该公司具有: {', '.join(factors_desc)}等特征"
        
        return explanation
    
    def suggest_threshold_adjustment(self, step_id: str, metrics: Dict[str, Any]) -> Optional[str]:
        """
        基于历史表现建议阈值调整
        
        Args:
            step_id: 步骤ID
            metrics: 实际指标数据
            
        Returns:
            str: 调整建议，或None
        """
        # 这里可以实现基于历史数据的智能建议
        # 简化实现：返回None
        return None
    
    def get_threshold_history(self) -> List[Dict]:
        """获取阈值调整历史"""
        return self._threshold_history


# 便捷函数
def get_dynamic_thresholds(step_id: str, company_profile: Dict[str, Any]) -> Thresholds:
    """便捷函数：获取动态阈值"""
    manager = DynamicThresholdManager()
    return manager.calculate_thresholds(step_id, company_profile)


if __name__ == "__main__":
    # 测试
    print("=" * 60)
    print("DynamicThresholdManager 测试")
    print("=" * 60)
    
    manager = DynamicThresholdManager()
    
    # 测试大型集团企业
    large_conglomerate = {
        "name": "测试集团",
        "market_cap": 5000,  # 5000亿
        "business_segments": 6,  # 6个业务板块
        "industry": "technology",
        "is_listed": True,
        "global_exposure": "global",
        "data_availability": "high"
    }
    
    print("\n大型集团企业阈值:")
    result = manager.get_thresholds_for_company("step4", "测试集团", large_conglomerate)
    print(f"  调整系数: {result['applied_factor']}")
    print(f"  Token阈值: {result['thresholds']['tokens']} (基础: {result['base_thresholds']['tokens']})")
    print(f"  说明: {result['explanation']}")
    
    # 测试小型单一业务公司
    small_company = {
        "name": "测试小公司",
        "market_cap": 50,  # 50亿
        "business_segments": 1,
        "industry": "retail",
        "is_listed": False,
        "global_exposure": "domestic",
        "data_availability": "medium"
    }
    
    print("\n小型公司阈值:")
    result = manager.get_thresholds_for_company("step4", "测试小公司", small_company)
    print(f"  调整系数: {result['applied_factor']}")
    print(f"  Token阈值: {result['thresholds']['tokens']} (基础: {result['base_thresholds']['tokens']})")
    print(f"  说明: {result['explanation']}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
