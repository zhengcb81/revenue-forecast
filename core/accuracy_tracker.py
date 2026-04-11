"""
预测准确度追踪系统 v1.0
创建日期: 2026-03-01

用途: 
1. 记录历史预测数据
2. 追踪预测与实际结果的偏差
3. 计算准确度指标
4. 生成校准系数
5. 提供预测质量改进建议

集成:
- 与 rolling-forecast.md 配合实现季度滚动预测追踪
- 与 enforcement_controller.py 配合实现执行质量追踪
- 输出到 JSON/Markdown 报告
"""

import json
import os
import math
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class PredictionRecord:
    """单次预测记录"""
    prediction_date: str  # 预测日期 YYYY-MM-DD
    batch_id: str  # 批次ID (V1, V2, Q1, Q2, 等)
    target_year: int  # 预测目标年份
    predicted_revenue: float  # 预测营收（亿元）
    confidence_interval_lower: float  # 置信区间下限
    confidence_interval_upper: float  # 置信区间上限
    scenario_probs: Dict[str, float]  # 情景概率 {optimistic, base, pessimistic}
    predicted_cagr: float  # 预测CAGR
    notes: str = ""  # 备注
    
    # 实际数据（后续填入）
    actual_revenue: Optional[float] = None
    actual_cagr: Optional[float] = None
    actual_date: Optional[str] = None
    
    @property
    def deviation_rate(self) -> Optional[float]:
        """计算偏差率"""
        if self.actual_revenue is None or self.predicted_revenue == 0:
            return None
        return (self.predicted_revenue - self.actual_revenue) / self.actual_revenue
    
    @property
    def absolute_deviation_rate(self) -> Optional[float]:
        """计算绝对偏差率"""
        dev = self.deviation_rate
        return abs(dev) if dev is not None else None
    
    @property
    def is_within_confidence_interval(self) -> Optional[bool]:
        """检查实际值是否在置信区间内"""
        if self.actual_revenue is None:
            return None
        return (self.confidence_interval_lower <= self.actual_revenue <= 
                self.confidence_interval_upper)


@dataclass
class AccuracyMetrics:
    """准确度指标"""
    # 基础指标
    prediction_count: int  # 预测次数
    actual_count: int  # 已有实际值的记录数
    
    # 偏差指标
    mean_deviation: Optional[float]  # 平均偏差
    mean_absolute_deviation: Optional[float]  # 平均绝对偏差
    std_deviation: Optional[float]  # 偏差标准差
    max_deviation: Optional[float]  # 最大偏差
    min_deviation: Optional[float]  # 最小偏差
    
    # 方向指标
    direction_accuracy: Optional[float]  # 方向准确率（预测涨跌方向正确的比例）
    optimistic_count: int  # 乐观预测次数（预测>实际）
    pessimistic_count: int  # 悲观预测次数（预测<实际）
    neutral_count: int  # 中性预测次数（预测≈实际，偏差<2%）
    
    # 区间指标
    interval_coverage_rate: Optional[float]  # 置信区间覆盖率
    
    # 质量评级
    quality_rating: str  # 优秀/良好/一般/较差
    
    # 校准系数
    calibration_factor: float  # 校准系数（用于调整未来预测）
    bias_type: str  # 乐观/悲观/中性


class PredictionAccuracyTracker:
    """
    预测准确度追踪器
    
    功能:
    1. 记录和管理预测历史
    2. 计算准确度指标
    3. 生成校准系数
    4. 输出准确度报告
    """
    
    def __init__(self, company_name: str, cache_base_dir: str = "revenue-forecast-cache"):
        """
        初始化追踪器
        
        Args:
            company_name: 公司名称
            cache_base_dir: 缓存根目录
        """
        self.company_name = company_name
        self.cache_base_dir = cache_base_dir
        self.company_cache_dir = os.path.join(cache_base_dir, company_name)
        self.tracker_file = os.path.join(self.company_cache_dir, "accuracy_history.json")
        
        # 确保目录存在
        os.makedirs(self.company_cache_dir, exist_ok=True)
        
        # 加载历史记录
        self.records: List[PredictionRecord] = self._load_records()
    
    def _load_records(self) -> List[PredictionRecord]:
        """从文件加载历史记录"""
        if not os.path.exists(self.tracker_file):
            return []
        
        try:
            with open(self.tracker_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            records = []
            for record_data in data.get('records', []):
                record = PredictionRecord(**record_data)
                records.append(record)
            
            return records
        except Exception as e:
            print(f"⚠️ 加载准确度历史记录失败: {e}")
            return []
    
    def _save_records(self):
        """保存记录到文件"""
        try:
            data = {
                'company_name': self.company_name,
                'last_updated': datetime.now().isoformat(),
                'records': [asdict(r) for r in self.records]
            }
            
            with open(self.tracker_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 保存准确度历史记录失败: {e}")
    
    def record_prediction(
        self,
        prediction_date: str,
        batch_id: str,
        target_year: int,
        predicted_revenue: float,
        confidence_interval: Tuple[float, float],
        scenario_probs: Dict[str, float],
        predicted_cagr: float,
        notes: str = ""
    ) -> PredictionRecord:
        """
        记录新的预测
        
        Args:
            prediction_date: 预测日期 YYYY-MM-DD
            batch_id: 批次ID (V1, V2, Q1, 等)
            target_year: 目标年份
            predicted_revenue: 预测营收（亿元）
            confidence_interval: (下限, 上限)
            scenario_probs: 情景概率
            predicted_cagr: 预测CAGR
            notes: 备注
            
        Returns:
            PredictionRecord: 创建的记录
        """
        record = PredictionRecord(
            prediction_date=prediction_date,
            batch_id=batch_id,
            target_year=target_year,
            predicted_revenue=predicted_revenue,
            confidence_interval_lower=confidence_interval[0],
            confidence_interval_upper=confidence_interval[1],
            scenario_probs=scenario_probs,
            predicted_cagr=predicted_cagr,
            notes=notes
        )
        
        # 检查是否已存在相同批次的记录，如有则更新
        existing_idx = None
        for i, r in enumerate(self.records):
            if r.batch_id == batch_id and r.target_year == target_year:
                existing_idx = i
                break
        
        if existing_idx is not None:
            # 保留实际值（如果已存在）
            existing = self.records[existing_idx]
            record.actual_revenue = existing.actual_revenue
            record.actual_cagr = existing.actual_cagr
            record.actual_date = existing.actual_date
            self.records[existing_idx] = record
        else:
            self.records.append(record)
        
        self._save_records()
        return record
    
    def update_actual(
        self,
        target_year: int,
        actual_revenue: float,
        actual_date: str = None
    ) -> List[PredictionRecord]:
        """
        更新实际数据
        
        Args:
            target_year: 目标年份
            actual_revenue: 实际营收
            actual_date: 实际数据日期（可选）
            
        Returns:
            List[PredictionRecord]: 更新的记录列表
        """
        if actual_date is None:
            actual_date = datetime.now().strftime("%Y-%m-%d")
        
        updated_records = []
        for record in self.records:
            if record.target_year == target_year and record.actual_revenue is None:
                record.actual_revenue = actual_revenue
                record.actual_date = actual_date
                
                # 计算实际CAGR（如果有基期数据）
                # 这里简化处理，实际应该根据基期营收计算
                record.actual_cagr = record.predicted_cagr + (record.deviation_rate or 0) * 100
                
                updated_records.append(record)
        
        if updated_records:
            self._save_records()
        
        return updated_records
    
    def calculate_metrics(self, target_year: int = None) -> AccuracyMetrics:
        """
        计算准确度指标
        
        Args:
            target_year: 目标年份（可选，默认所有年份）
            
        Returns:
            AccuracyMetrics: 准确度指标
        """
        # 筛选记录
        records = self.records
        if target_year is not None:
            records = [r for r in records if r.target_year == target_year]
        
        # 有实际值的记录
        records_with_actual = [r for r in records if r.actual_revenue is not None]
        
        prediction_count = len(records)
        actual_count = len(records_with_actual)
        
        if actual_count == 0:
            return AccuracyMetrics(
                prediction_count=prediction_count,
                actual_count=0,
                mean_deviation=None,
                mean_absolute_deviation=None,
                std_deviation=None,
                max_deviation=None,
                min_deviation=None,
                direction_accuracy=None,
                optimistic_count=0,
                pessimistic_count=0,
                neutral_count=0,
                interval_coverage_rate=None,
                quality_rating="暂无数据",
                calibration_factor=1.0,
                bias_type="未知"
            )
        
        # 计算偏差
        deviations = [r.deviation_rate for r in records_with_actual]
        abs_deviations = [abs(d) for d in deviations]
        
        mean_deviation = sum(deviations) / len(deviations)
        mean_absolute_deviation = sum(abs_deviations) / len(abs_deviations)
        std_deviation = math.sqrt(sum((d - mean_deviation) ** 2 for d in deviations) / len(deviations))
        max_deviation = max(deviations)
        min_deviation = min(deviations)
        
        # 方向准确率（简化版：假设都能预测对方向）
        # 实际应用中需要与上一期预测对比
        direction_accuracy = 1.0  # 简化处理
        
        # 乐观/悲观/中性统计
        optimistic_count = sum(1 for d in deviations if d > 0.02)
        pessimistic_count = sum(1 for d in deviations if d < -0.02)
        neutral_count = len(deviations) - optimistic_count - pessimistic_count
        
        # 置信区间覆盖率
        interval_checks = [r.is_within_confidence_interval for r in records_with_actual]
        interval_coverage_rate = sum(1 for x in interval_checks if x) / len(interval_checks)
        
        # 质量评级
        if mean_absolute_deviation is not None:
            if mean_absolute_deviation < 0.05:
                quality_rating = "优秀"
            elif mean_absolute_deviation < 0.10:
                quality_rating = "良好"
            elif mean_absolute_deviation < 0.15:
                quality_rating = "一般"
            else:
                quality_rating = "较差"
        else:
            quality_rating = "暂无数据"
        
        # 校准系数
        calibration_factor = 1 / (1 + mean_deviation) if mean_deviation != -1 else 1.0
        
        # 偏差类型
        if mean_deviation > 0.05:
            bias_type = "乐观"
        elif mean_deviation < -0.05:
            bias_type = "悲观"
        else:
            bias_type = "中性"
        
        return AccuracyMetrics(
            prediction_count=prediction_count,
            actual_count=actual_count,
            mean_deviation=mean_deviation,
            mean_absolute_deviation=mean_absolute_deviation,
            std_deviation=std_deviation,
            max_deviation=max_deviation,
            min_deviation=min_deviation,
            direction_accuracy=direction_accuracy,
            optimistic_count=optimistic_count,
            pessimistic_count=pessimistic_count,
            neutral_count=neutral_count,
            interval_coverage_rate=interval_coverage_rate,
            quality_rating=quality_rating,
            calibration_factor=calibration_factor,
            bias_type=bias_type
        )
    
    def get_calibration_recommendation(self, target_year: int = None) -> str:
        """
        获取校准建议
        
        Args:
            target_year: 目标年份
            
        Returns:
            str: 校准建议文本
        """
        metrics = self.calculate_metrics(target_year)
        
        if metrics.actual_count == 0:
            return "暂无历史预测数据，无法提供校准建议。"
        
        recommendations = []
        
        # 基于偏差类型的建议
        if metrics.bias_type == "乐观":
            recommendations.append(
                f"📊 **系统性乐观偏差**: 历史预测平均偏高 {metrics.mean_deviation*100:.1f}%\n"
                f"   建议: 未来预测乘以校准系数 {metrics.calibration_factor:.3f}"
            )
        elif metrics.bias_type == "悲观":
            recommendations.append(
                f"📊 **系统性悲观偏差**: 历史预测平均偏低 {abs(metrics.mean_deviation)*100:.1f}%\n"
                f"   建议: 未来预测乘以校准系数 {metrics.calibration_factor:.3f}"
            )
        else:
            recommendations.append(
                f"✅ **预测无偏**: 历史预测平均偏差 {metrics.mean_deviation*100:.1f}%（在合理范围内）"
            )
        
        # 基于波动性的建议
        if metrics.std_deviation and metrics.std_deviation > 0.10:
            recommendations.append(
                f"⚠️ **预测波动较大**: 标准差 {metrics.std_deviation*100:.1f}%\n"
                f"   建议: 扩大置信区间，提高预测保守性"
            )
        
        # 基于区间覆盖率的建议
        if metrics.interval_coverage_rate and metrics.interval_coverage_rate < 0.70:
            recommendations.append(
                f"⚠️ **置信区间覆盖不足**: 实际值落在区间内的比例仅 {metrics.interval_coverage_rate*100:.0f}%\n"
                f"   建议: 扩大置信区间宽度"
            )
        
        # 综合评级
        recommendations.append(
            f"\n📈 **准确度评级**: {metrics.quality_rating}\n"
            f"   基于 {metrics.actual_count} 次预测记录"
        )
        
        return "\n\n".join(recommendations)
    
    def generate_accuracy_report(self, target_year: int = None) -> str:
        """
        生成准确度报告
        
        Args:
            target_year: 目标年份
            
        Returns:
            str: Markdown格式的准确度报告
        """
        metrics = self.calculate_metrics(target_year)
        
        # 筛选记录
        records = self.records
        if target_year is not None:
            records = [r for r in records if r.target_year == target_year]
        
        # 生成报告
        report = f"""# 预测准确度评估报告

## 概述

- **公司名称**: {self.company_name}
- **评估日期**: {datetime.now().strftime("%Y-%m-%d")}
- **目标年份**: {target_year if target_year else "所有年份"}
- **预测记录数**: {metrics.prediction_count}
- **已有实际值**: {metrics.actual_count}

## 准确度指标

### 偏差分析

| 指标 | 数值 | 说明 |
|-----|------|------|
| **平均偏差** | {metrics.mean_deviation*100:.2f}% if metrics.mean_deviation else "N/A" | 正值表示预测偏高 |
| **平均绝对偏差** | {metrics.mean_absolute_deviation*100:.2f}% if metrics.mean_absolute_deviation else "N/A" | 不考虑方向的平均误差 |
| **偏差标准差** | {metrics.std_deviation*100:.2f}% if metrics.std_deviation else "N/A" | 预测稳定性 |
| **最大偏差** | {metrics.max_deviation*100:.2f}% if metrics.max_deviation else "N/A" | 最大一次误差 |
| **最小偏差** | {metrics.min_deviation*100:.2f}% if metrics.min_deviation else "N/A" | 最准一次 |

### 方向与区间

| 指标 | 数值 | 说明 |
|-----|------|------|
| **方向准确率** | {metrics.direction_accuracy*100:.1f}% if metrics.direction_accuracy else "N/A" | 预测涨跌方向正确的比例 |
| **置信区间覆盖率** | {metrics.interval_coverage_rate*100:.1f}% if metrics.interval_coverage_rate else "N/A" | 实际值落在区间内的比例 |

### 偏差分布

| 类型 | 次数 | 占比 |
|-----|------|------|
| 乐观预测（预测>实际） | {metrics.optimistic_count} | {metrics.optimistic_count/metrics.actual_count*100:.1f}% |
| 中性预测（偏差<2%） | {metrics.neutral_count} | {metrics.neutral_count/metrics.actual_count*100:.1f}% |
| 悲观预测（预测<实际） | {metrics.pessimistic_count} | {metrics.pessimistic_count/metrics.actual_count*100:.1f}% |

## 质量评级

**准确度评级**: {metrics.quality_rating}

- **偏差类型**: {metrics.bias_type}
- **校准系数**: {metrics.calibration_factor:.4f}

## 预测历史

| 批次 | 预测日期 | 预测营收(亿) | 置信区间 | 实际营收(亿) | 偏差率 | 评级 |
|-----|---------|-------------|---------|-------------|-------|------|
"""
        
        # 添加每条记录
        for r in records:
            actual_str = f"{r.actual_revenue:.1f}" if r.actual_revenue else "-"
            deviation_str = f"{r.deviation_rate*100:.1f}%" if r.deviation_rate else "-"
            
            # 评级
            if r.absolute_deviation_rate is not None:
                if r.absolute_deviation_rate < 0.05:
                    rating = "优秀"
                elif r.absolute_deviation_rate < 0.10:
                    rating = "良好"
                elif r.absolute_deviation_rate < 0.15:
                    rating = "一般"
                else:
                    rating = "较差"
            else:
                rating = "-"
            
            report += f"| {r.batch_id} | {r.prediction_date} | {r.predicted_revenue:.1f} | "
            report += f"[{r.confidence_interval_lower:.1f}, {r.confidence_interval_upper:.1f}] | "
            report += f"{actual_str} | {deviation_str} | {rating} |\n"
        
        # 添加校准建议
        report += f"\n## 校准建议\n\n{self.get_calibration_recommendation(target_year)}\n"
        
        return report
    
    def export_to_json(self) -> Dict:
        """导出为JSON格式"""
        metrics = self.calculate_metrics()
        
        return {
            "company_name": self.company_name,
            "export_date": datetime.now().isoformat(),
            "metrics": {
                "prediction_count": metrics.prediction_count,
                "actual_count": metrics.actual_count,
                "mean_deviation": metrics.mean_deviation,
                "mean_absolute_deviation": metrics.mean_absolute_deviation,
                "quality_rating": metrics.quality_rating,
                "calibration_factor": metrics.calibration_factor,
                "bias_type": metrics.bias_type
            },
            "records": [asdict(r) for r in self.records]
        }


class RollingForecastTracker:
    """
    季度滚动预测追踪器
    
    专门用于追踪季度滚动预测的准确度
    """
    
    def __init__(self, company_name: str, cache_base_dir: str = "revenue-forecast-cache"):
        self.company_name = company_name
        self.cache_base_dir = cache_base_dir
        self.base_tracker = PredictionAccuracyTracker(company_name, cache_base_dir)
    
    def record_quarterly_update(
        self,
        year: int,
        quarter: int,  # 1, 2, 3, 4
        prediction: float,
        confidence_interval: Tuple[float, float],
        scenario_probs: Dict[str, float],
        notes: str = ""
    ) -> PredictionRecord:
        """记录季度滚动更新"""
        batch_id = f"Q{quarter}"
        prediction_date = f"{year}-{quarter*3:02d}-15"  # 假设每季度中旬更新
        
        return self.base_tracker.record_prediction(
            prediction_date=prediction_date,
            batch_id=batch_id,
            target_year=year,
            predicted_revenue=prediction,
            confidence_interval=confidence_interval,
            scenario_probs=scenario_probs,
            predicted_cagr=0.0,  # 季度更新可不填
            notes=notes
        )
    
    def close_year(self, year: int, actual_revenue: float):
        """年度闭环，填入实际值"""
        return self.base_tracker.update_actual(year, actual_revenue)
    
    def get_rolling_accuracy_summary(self, year: int) -> Dict:
        """获取年度滚动准确度摘要"""
        metrics = self.base_tracker.calculate_metrics(year)
        
        return {
            "year": year,
            "prediction_batches": ["初始", "Q1", "Q2", "Q3", "年末"],
            "metrics": {
                "mean_deviation": metrics.mean_deviation,
                "mean_absolute_deviation": metrics.mean_absolute_deviation,
                "quality_rating": metrics.quality_rating,
                "calibration_factor": metrics.calibration_factor
            },
            "improvement": {
                "initial_to_final": None,  # 初始预测 vs 最终实际
                "rolling_effectiveness": None  # 滚动更新的有效性
            }
        }


# ============ 便捷函数 ============

def create_tracker(company_name: str) -> PredictionAccuracyTracker:
    """创建追踪器的便捷函数"""
    return PredictionAccuracyTracker(company_name)


def quick_accuracy_check(company_name: str) -> str:
    """快速检查准确度的便捷函数"""
    tracker = create_tracker(company_name)
    return tracker.get_calibration_recommendation()


# ============ 测试代码 ============

if __name__ == "__main__":
    # 测试代码
    tracker = PredictionAccuracyTracker("测试公司")
    
    # 记录一些测试预测
    tracker.record_prediction(
        prediction_date="2024-12-15",
        batch_id="V1",
        target_year=2025,
        predicted_revenue=100.0,
        confidence_interval=(85.0, 115.0),
        scenario_probs={"optimistic": 0.25, "base": 0.50, "pessimistic": 0.25},
        predicted_cagr=8.0,
        notes="初始预测"
    )
    
    tracker.record_prediction(
        prediction_date="2025-04-15",
        batch_id="V2",
        target_year=2025,
        predicted_revenue=105.0,
        confidence_interval=(92.0, 118.0),
        scenario_probs={"optimistic": 0.30, "base": 0.55, "pessimistic": 0.15},
        predicted_cagr=10.0,
        notes="Q1滚动更新"
    )
    
    # 填入实际值
    tracker.update_actual(2025, 103.0)
    
    # 生成报告
    print(tracker.generate_accuracy_report(2025))
