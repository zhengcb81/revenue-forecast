"""
Revenue Forecast - 数据一致性验证器 v2.5.1
版本: v1.0
创建日期: 2026-03-01

功能:
1. JSON与Markdown数据对比
2. 关键字段一致性检查
3. 情景数据一致性
4. 数值逻辑验证
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
import re
import os
import sys
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from checkpoint_registry import CheckpointResult


@dataclass
class DataMismatch:
    """数据不匹配信息"""
    field: str
    json_value: Any
    md_value: Any
    tolerance: float = 0.01
    
    def to_dict(self) -> Dict:
        return {
            "field": self.field,
            "json_value": self.json_value,
            "md_value": self.md_value,
            "difference": self._calculate_difference(),
            "tolerance": self.tolerance
        }
    
    def _calculate_difference(self) -> Optional[float]:
        """计算差异"""
        try:
            if isinstance(self.json_value, (int, float)) and isinstance(self.md_value, (int, float)):
                return abs(self.json_value - self.md_value)
        except:
            pass
        return None
    
    @property
    def is_significant(self) -> bool:
        """差异是否显著"""
        diff = self._calculate_difference()
        if diff is None:
            return self.json_value != self.md_value
        
        # 相对容差
        if isinstance(self.json_value, (int, float)) and self.json_value != 0:
            relative_diff = diff / abs(self.json_value)
            return relative_diff > self.tolerance
        
        return diff > 0.01


class ConsistencyValidator:
    """
    数据一致性验证器
    
    验证JSON和Markdown报告中的数据一致
    """
    
    # 关键字段列表
    KEY_FIELDS = [
        "company_name",
        "analysis_date",
        "score",
        "overall_score",
        "cagr",
        "revenue_2026",
        "revenue_2031"
    ]
    
    # 情景字段
    SCENARIO_FIELDS = [
        "cagr_optimistic",
        "cagr_base",
        "cagr_pessimistic",
        "revenue_2031_optimistic",
        "revenue_2031_base",
        "revenue_2031_pessimistic"
    ]
    
    # 容差配置
    TOLERANCE = {
        "cagr": 0.5,        # CAGR 容差 0.5%
        "revenue": 0.05,    # 营收容差 5%
        "score": 0.1,       # 评分容差 0.1
        "percentage": 0.01  # 百分比容差 1%
    }
    
    def __init__(self):
        """初始化验证器"""
        pass
    
    def validate_json_md_consistency(self, json_path: str, md_path: str) -> CheckpointResult:
        """
        验证JSON和Markdown数据一致性
        
        Args:
            json_path: JSON文件路径
            md_path: Markdown文件路径
            
        Returns:
            CheckpointResult: 验证结果
        """
        # 加载数据
        json_data = self._load_json(json_path)
        if json_data is None:
            return CheckpointResult(
                checkpoint_id="consistency_json_md",
                passed=False,
                message="无法加载JSON文件",
                errors=[f"JSON文件不存在或格式错误: {json_path}"]
            )
        
        md_data = self._extract_data_from_markdown(md_path)
        if md_data is None:
            return CheckpointResult(
                checkpoint_id="consistency_json_md",
                passed=False,
                message="无法加载Markdown文件",
                errors=[f"Markdown文件不存在: {md_path}"]
            )
        
        # 执行对比
        mismatches = []
        
        # 1. 对比关键字段
        for field in self.KEY_FIELDS:
            json_value = self._get_nested_value(json_data, field)
            md_value = self._get_nested_value(md_data, field)
            
            if json_value is not None or md_value is not None:
                mismatch = self._compare_values(field, json_value, md_value)
                if mismatch and mismatch.is_significant:
                    mismatches.append(mismatch)
        
        # 2. 对比情景数据
        for field in self.SCENARIO_FIELDS:
            json_value = self._get_nested_value(json_data, field)
            md_value = self._get_nested_value(md_data, field)
            
            if json_value is not None or md_value is not None:
                tolerance = self.TOLERANCE.get("cagr", 0.01) if "cagr" in field else self.TOLERANCE.get("revenue", 0.05)
                mismatch = self._compare_values(field, json_value, md_value, tolerance)
                if mismatch and mismatch.is_significant:
                    mismatches.append(mismatch)
        
        # 3. 验证情景逻辑（乐观>基准>悲观）
        logic_errors = self._validate_scenario_logic(json_data)
        
        # 生成结果
        passed = len(mismatches) == 0 and len(logic_errors) == 0
        
        errors = [f"{m.field}: JSON={m.json_value}, MD={m.md_value}" for m in mismatches]
        errors.extend(logic_errors)
        
        return CheckpointResult(
            checkpoint_id="consistency_json_md",
            passed=passed,
            score=100 - len(mismatches) * 10 - len(logic_errors) * 20,
            message=f"数据一致性: {len(mismatches)}项不一致, {len(logic_errors)}项逻辑错误",
            details={
                "json_fields": len(json_data),
                "md_fields": len(md_data),
                "mismatches": [m.to_dict() for m in mismatches],
                "logic_errors": logic_errors
            },
            errors=errors if errors else [],
            suggestions=self._generate_suggestions(mismatches, logic_errors)
        )
    
    def validate_internal_consistency(self, json_data: Dict) -> CheckpointResult:
        """
        验证JSON数据内部一致性
        
        检查：
        - 情景概率之和是否为100%
        - 乐观>基准>悲观
        - CAGR与营收增长是否匹配
        """
        errors = []
        
        # 1. 检查情景概率
        scenarios = json_data.get("scenario_analysis", {})
        total_prob = 0
        for scen in ["optimistic", "base", "pessimistic"]:
            prob = self._get_nested_value(scenarios, f"{scen}.probability")
            if prob:
                total_prob += prob
        
        if total_prob > 0 and abs(total_prob - 1.0) > 0.01:
            errors.append(f"情景概率之和不等于100%: {total_prob:.0%}")
        
        # 2. 检查CAGR顺序
        cagr_opt = self._get_nested_value(scenarios, "optimistic.cagr")
        cagr_base = self._get_nested_value(scenarios, "base.cagr")
        cagr_pes = self._get_nested_value(scenarios, "pessimistic.cagr")
        
        if all([cagr_opt, cagr_base, cagr_pes]):
            if not (cagr_opt >= cagr_base >= cagr_pes):
                errors.append("CAGR顺序错误：应为乐观>=基准>=悲观")
        
        # 3. 检查营收一致性
        revenue_base = json_data.get("revenue_base")
        revenue_2031 = self._get_nested_value(scenarios, "base.revenue_2031")
        cagr = cagr_base
        
        if all([revenue_base, revenue_2031, cagr]):
            # 根据CAGR计算期望的2031年营收
            years = 5  # 假设5年预测期
            expected_revenue = revenue_base * ((1 + cagr/100) ** years)
            
            if abs(expected_revenue - revenue_2031) / revenue_2031 > 0.1:
                errors.append(f"营收与CAGR不匹配：基于CAGR计算的2031营收为{expected_revenue:.0f}，但实际为{revenue_2031:.0f}")
        
        passed = len(errors) == 0
        
        return CheckpointResult(
            checkpoint_id="consistency_internal",
            passed=passed,
            score=100 - len(errors) * 20,
            message=f"内部一致性: {len(errors)}项错误",
            errors=errors,
            suggestions=["请检查情景分析和CAGR计算逻辑"] if errors else []
        )
    
    def _load_json(self, path: str) -> Optional[Dict]:
        """加载JSON文件"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None
    
    def _extract_data_from_markdown(self, path: str) -> Optional[Dict]:
        """从Markdown提取数据"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            data = {}
            
            # 提取表格数据
            tables = re.findall(r'\|(.+?)\|\n\|[-:| ]+\|\n((?:\|.+\|\n)+)', content)
            for headers, rows in tables:
                headers = [h.strip() for h in headers.split('|') if h.strip()]
                for row in rows.strip().split('\n'):
                    cells = [c.strip() for c in row.split('|') if c.strip()]
                    if len(cells) >= 2:
                        # 尝试解析数值
                        key = cells[0]
                        value = self._parse_value(cells[1])
                        data[key] = value
            
            # 提取关键指标
            patterns = {
                "score": r'综合评分[:：]\s*([\d.]+)',
                "cagr": r'CAGR[:：]\s*([\d.]+)',
                "revenue_2026": r'2026年营收[:：]\s*([\d,]+)',
                "revenue_2031": r'2031年营收[:：]\s*([\d,]+)'
            }
            
            for key, pattern in patterns.items():
                match = re.search(pattern, content)
                if match:
                    data[key] = self._parse_value(match.group(1))
            
            return data
            
        except Exception:
            return None
    
    def _parse_value(self, value_str: str) -> Any:
        """解析数值"""
        value_str = value_str.strip().replace(',', '').replace('%', '')
        
        # 尝试整数
        try:
            return int(value_str)
        except:
            pass
        
        # 尝试浮点数
        try:
            return float(value_str)
        except:
            pass
        
        return value_str
    
    def _get_nested_value(self, data: Dict, path: str) -> Any:
        """获取嵌套值"""
        keys = path.split('.')
        value = data
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        
        return value
    
    def _compare_values(self, field: str, json_value: Any, md_value: Any, 
                       tolerance: float = 0.01) -> Optional[DataMismatch]:
        """对比两个值"""
        if json_value is None and md_value is None:
            return None
        
        if json_value is None or md_value is None:
            return DataMismatch(field, json_value, md_value, tolerance)
        
        # 数值对比
        if isinstance(json_value, (int, float)) and isinstance(md_value, (int, float)):
            return DataMismatch(field, json_value, md_value, tolerance)
        
        # 字符串对比
        if str(json_value) != str(md_value):
            return DataMismatch(field, json_value, md_value, tolerance)
        
        return None
    
    def _validate_scenario_logic(self, json_data: Dict) -> List[str]:
        """验证情景逻辑"""
        errors = []
        scenarios = json_data.get("scenario_analysis", {})
        
        cagr_opt = self._get_nested_value(scenarios, "optimistic.cagr")
        cagr_base = self._get_nested_value(scenarios, "base.cagr")
        cagr_pes = self._get_nested_value(scenarios, "pessimistic.cagr")
        
        if all([cagr_opt, cagr_base, cagr_pes]):
            if cagr_opt < cagr_base:
                errors.append("乐观CAGR应>=基准CAGR")
            if cagr_base < cagr_pes:
                errors.append("基准CAGR应>=悲观CAGR")
        
        return errors
    
    def _generate_suggestions(self, mismatches: List[DataMismatch], 
                             logic_errors: List[str]) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        if mismatches:
            suggestions.append(f"请核对以下字段的一致性: {', '.join(m.field for m in mismatches[:3])}")
            suggestions.append("确保JSON和Markdown报告使用相同的数据源")
        
        if logic_errors:
            suggestions.append("请检查情景分析的逻辑关系")
        
        return suggestions


# 便捷函数
def validate_report_consistency(json_path: str, md_path: str) -> CheckpointResult:
    """便捷函数：验证报告一致性"""
    validator = ConsistencyValidator()
    return validator.validate_json_md_consistency(json_path, md_path)


if __name__ == "__main__":
    # 测试
    print("=" * 60)
    print("ConsistencyValidator 测试")
    print("=" * 60)
    
    validator = ConsistencyValidator()
    
    # 创建测试数据
    test_json = {
        "company_name": "测试公司",
        "score": 8.5,
        "cagr": 22.5,
        "scenario_analysis": {
            "optimistic": {"cagr": 28, "probability": 0.25},
            "base": {"cagr": 22.5, "probability": 0.5},
            "pessimistic": {"cagr": 15, "probability": 0.25}
        }
    }
    
    # 测试内部一致性
    print("\n测试内部一致性:")
    result1 = validator.validate_internal_consistency(test_json)
    print(f"  通过: {result1.passed}")
    print(f"  消息: {result1.message}")
    
    # 测试不一致的数据
    bad_json = {
        "company_name": "测试公司",
        "score": 8.5,
        "scenario_analysis": {
            "optimistic": {"cagr": 20},  # 小于基准
            "base": {"cagr": 22.5},
            "pessimistic": {"cagr": 15}
        }
    }
    
    print("\n测试CAGR顺序错误:")
    result2 = validator.validate_internal_consistency(bad_json)
    print(f"  通过: {result2.passed}")
    print(f"  错误: {result2.errors}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
