"""
AI辅助验证工具 v1.0
创建日期: 2026-03-01

功能：
1. 自动检测报告完整性
2. 验证逻辑一致性
3. 检查数据质量
4. 评估内容可读性
5. 生成综合验证报告

用途：
- 在报告生成后自动验证质量
- 在分析过程中实时检查问题
- 为分析师提供改进建议
"""

# v2.6.0 统一 UTF-8 编码引导（避免 Windows cp936/gbk 中文乱码）
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
try:
    from core.encoding import setup_utf8_console as _setup_utf8_console
    _setup_utf8_console()
except Exception:
    pass

import json
import os
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ValidationScore:
    """验证得分"""
    category: str           # 类别
    score: float           # 得分（0-100）
    max_score: float       # 满分
    passed: bool           # 是否通过
    issues: List[str]      # 问题列表
    suggestions: List[str] # 改进建议


class AIReportValidator:
    """
    AI报告验证器
    
    自动检测报告质量问题，提供量化评分和改进建议
    """
    
    def __init__(self):
        self.validation_results: List[ValidationScore] = []
        
    def validate_report(self, json_path: str, markdown_path: str) -> Dict:
        """
        综合验证报告
        
        Args:
            json_path: JSON报告路径
            markdown_path: Markdown报告路径
            
        Returns:
            Dict: 验证结果
        """
        self.validation_results = []
        
        # 执行各项验证
        completeness = self._validate_completeness(json_path, markdown_path)
        consistency = self._validate_consistency(json_path)
        data_quality = self._validate_data_quality(markdown_path)
        readability = self._validate_readability(markdown_path)
        
        self.validation_results = [
            completeness,
            consistency,
            data_quality,
            readability
        ]
        
        # 计算综合得分
        total_score = sum(r.score for r in self.validation_results)
        max_score = sum(r.max_score for r in self.validation_results)
        overall_score = (total_score / max_score * 100) if max_score > 0 else 0
        
        # 确定评级
        if overall_score >= 90:
            grade = "优秀"
        elif overall_score >= 75:
            grade = "良好"
        elif overall_score >= 60:
            grade = "合格"
        else:
            grade = "需改进"
        
        return {
            "overall_score": round(overall_score, 1),
            "grade": grade,
            "passed": all(r.passed for r in self.validation_results),
            "categories": [
                {
                    "name": r.category,
                    "score": r.score,
                    "max_score": r.max_score,
                    "passed": r.passed,
                    "issues": r.issues,
                    "suggestions": r.suggestions
                }
                for r in self.validation_results
            ],
            "summary": self._generate_summary()
        }
    
    def _validate_completeness(self, json_path: str, markdown_path: str) -> ValidationScore:
        """验证报告完整性"""
        score = 0
        max_score = 100
        issues = []
        suggestions = []
        
        # 检查文件存在
        if not os.path.exists(json_path):
            issues.append("JSON报告文件不存在")
            suggestions.append("请生成JSON格式报告")
        else:
            score += 20
        
        if not os.path.exists(markdown_path):
            issues.append("Markdown报告文件不存在")
            suggestions.append("请生成Markdown完整报告")
        else:
            score += 20
        
        # 检查JSON必需字段
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                required_json_fields = [
                    "company_name",
                    "score",
                    "overall_score",
                    "scenario_analysis",
                    "key_metrics"
                ]
                
                missing_fields = [f for f in required_json_fields if f not in data]
                if missing_fields:
                    issues.append(f"JSON缺少必需字段: {', '.join(missing_fields)}")
                    suggestions.append(f"请补充以下字段: {', '.join(missing_fields)}")
                else:
                    score += 30
                    
            except Exception as e:
                issues.append(f"JSON解析错误: {e}")
                suggestions.append("请检查JSON格式是否正确")
        
        # 检查Markdown必需章节
        if os.path.exists(markdown_path):
            try:
                with open(markdown_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                required_sections = [
                    "执行摘要",
                    "关键财务指标",
                    "双曲线业务分析",
                    "情景分析",
                    "投资建议",
                    "参数溯源"
                ]
                
                missing_sections = [s for s in required_sections if s not in content]
                if missing_sections:
                    issues.append(f"Markdown缺少必需章节: {', '.join(missing_sections)}")
                    suggestions.append(f"请添加以下章节: {', '.join(missing_sections)}")
                else:
                    score += 30
                    
            except Exception as e:
                issues.append(f"Markdown读取错误: {e}")
        
        passed = score >= 70
        
        return ValidationScore(
            category="完整性",
            score=score,
            max_score=max_score,
            passed=passed,
            issues=issues,
            suggestions=suggestions
        )
    
    def _validate_consistency(self, json_path: str) -> ValidationScore:
        """验证逻辑一致性"""
        score = 100
        max_score = 100
        issues = []
        suggestions = []
        
        if not os.path.exists(json_path):
            return ValidationScore(
                category="一致性",
                score=0,
                max_score=max_score,
                passed=False,
                issues=["JSON文件不存在，无法验证一致性"],
                suggestions=["请先生成JSON报告"]
            )
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 检查1: CAGR与评分匹配
            if "overall_score" in data and "cagr" in data.get("overall_score", {}):
                cagr = data["overall_score"]["cagr"]
                score_value = data["overall_score"].get("score", 0)
                
                # 根据CAGR检查评分是否合理
                expected_score_range = self._get_expected_score_range(cagr)
                if not (expected_score_range[0] <= score_value <= expected_score_range[1]):
                    issues.append(
                        f"评分与CAGR不匹配: CAGR={cagr}%, 评分={score_value}, "
                        f"期望范围={expected_score_range}"
                    )
                    suggestions.append("请根据CAGR查表确定正确评分")
                    score -= 25
            
            # 检查2: 情景概率总和
            if "scenario_analysis" in data:
                scenarios = data["scenario_analysis"]
                probs = [s.get("probability", 0) for s in scenarios.values() if isinstance(s, dict)]
                if probs and abs(sum(probs) - 1.0) > 0.01:
                    issues.append(f"情景概率总和不等于100%: {sum(probs)*100:.1f}%")
                    suggestions.append("请调整情景概率使其总和为100%")
                    score -= 20
            
            # 检查3: 乐观>基准>悲观
            if "scenario_analysis" in data:
                sa = data["scenario_analysis"]
                if all(k in sa for k in ["optimistic", "base", "pessimistic"]):
                    opt_cagr = sa["optimistic"].get("cagr", 0)
                    base_cagr = sa["base"].get("cagr", 0)
                    pess_cagr = sa["pessimistic"].get("cagr", 0)
                    
                    if not (opt_cagr >= base_cagr >= pess_cagr):
                        issues.append("情景CAGR排序错误: 应满足 乐观≥基准≥悲观")
                        suggestions.append("请检查各情景的CAGR设定")
                        score -= 25
            
            # 检查4: 财务指标合理性
            if "key_metrics" in data:
                km = data["key_metrics"]
                
                # 毛利率应在合理范围
                if "gross_margin" in km:
                    gm = km["gross_margin"]
                    if gm < 0 or gm > 95:
                        issues.append(f"毛利率异常: {gm}%")
                        suggestions.append("请核实毛利率数据")
                        score -= 15
            
        except Exception as e:
            issues.append(f"一致性验证出错: {e}")
            score = 0
        
        passed = score >= 70
        
        return ValidationScore(
            category="一致性",
            score=max(0, score),
            max_score=max_score,
            passed=passed,
            issues=issues,
            suggestions=suggestions
        )
    
    def _validate_data_quality(self, markdown_path: str) -> ValidationScore:
        """验证数据质量"""
        score = 100
        max_score = 100
        issues = []
        suggestions = []
        
        if not os.path.exists(markdown_path):
            return ValidationScore(
                category="数据质量",
                score=0,
                max_score=max_score,
                passed=False,
                issues=["Markdown文件不存在"],
                suggestions=["请先生成Markdown报告"]
            )
        
        try:
            with open(markdown_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查1: 数据密度（数字、单位出现频率）
            data_patterns = {
                "百分比": len(re.findall(r'\d+\.?\d*%', content)),
                "亿元": len(re.findall(r'\d+\.?\d*亿', content)),
                "万元": len(re.findall(r'\d+\.?\d*万', content)),
                "CAGR": len(re.findall(r'CAGR|复合增长率', content)),
                "年份": len(re.findall(r'20\d{2}', content))
            }
            
            total_data_points = sum(data_patterns.values())
            content_length = len(content)
            data_density = total_data_points / (content_length / 1000)  # 每千字数据点
            
            if data_density < 5:
                issues.append(f"数据密度偏低: {data_density:.1f}个数据点/千字")
                suggestions.append("建议增加更多量化数据和指标")
                score -= 20
            elif data_density < 10:
                suggestions.append("数据密度尚可，可适当增加更多量化分析")
            
            # 检查2: 数据一致性（单位统一）
            has_yi = '亿元' in content or '亿' in content
            has_wan = '万元' in content or '万' in content
            
            if has_yi and has_wan:
                # 检查是否混用（除非有明确换算）
                if content.count('亿元') > 0 and content.count('万元') > 10:
                    suggestions.append("注意单位统一：建议主要使用亿元或万元，避免频繁切换")
            
            # 检查3: 时间一致性
            years = re.findall(r'20\d{2}', content)
            if years:
                unique_years = set(years)
                if len(unique_years) < 3:
                    issues.append("时间跨度不足，建议包含更多年份的数据")
                    score -= 10
            
            # 检查4: 参数溯源
            if "参数溯源" in content or "数据来源" in content:
                score += 0  # 已存在
            else:
                issues.append("缺少参数溯源章节")
                suggestions.append("请添加数据来源和参数设定依据")
                score -= 15
            
        except Exception as e:
            issues.append(f"数据质量验证出错: {e}")
            score = 0
        
        passed = score >= 70
        
        return ValidationScore(
            category="数据质量",
            score=max(0, score),
            max_score=max_score,
            passed=passed,
            issues=issues,
            suggestions=suggestions
        )
    
    def _validate_readability(self, markdown_path: str) -> ValidationScore:
        """验证可读性"""
        score = 100
        max_score = 100
        issues = []
        suggestions = []
        
        if not os.path.exists(markdown_path):
            return ValidationScore(
                category="可读性",
                score=0,
                max_score=max_score,
                passed=False,
                issues=["Markdown文件不存在"],
                suggestions=["请先生成Markdown报告"]
            )
        
        try:
            with open(markdown_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查1: 内容长度
            if len(content) < 5000:
                issues.append(f"报告内容过短: {len(content)}字符")
                suggestions.append("建议扩充分析内容，至少5000字符")
                score -= 30
            elif len(content) < 10000:
                suggestions.append("内容长度尚可，建议进一步丰富分析")
            
            # 检查2: 结构层次
            h1_count = content.count('\n# ')
            h2_count = content.count('\n## ')
            h3_count = content.count('\n### ')
            
            if h2_count < 5:
                issues.append("章节结构过于简单，缺少二级标题")
                suggestions.append("建议使用##划分更多章节")
                score -= 20
            
            if h3_count < 10:
                suggestions.append("可适当增加三级标题(###)细化内容结构")
            
            # 检查3: 段落分布
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            if len(paragraphs) < 20:
                issues.append("段落数量偏少，内容可能过于集中")
                score -= 15
            
            # 检查4: 表格使用
            table_count = content.count('|')
            if table_count < 20:
                suggestions.append("建议增加更多表格呈现数据，提高可读性")
            
            # 检查5: 语言质量（简单检查）
            # 检查过长的句子
            sentences = re.split(r'[。！？]', content)
            long_sentences = [s for s in sentences if len(s) > 200]
            if len(long_sentences) > 10:
                suggestions.append("部分句子过长，建议适当断句提高可读性")
            
        except Exception as e:
            issues.append(f"可读性验证出错: {e}")
            score = 0
        
        passed = score >= 70
        
        return ValidationScore(
            category="可读性",
            score=max(0, score),
            max_score=max_score,
            passed=passed,
            issues=issues,
            suggestions=suggestions
        )
    
    def _get_expected_score_range(self, cagr: float) -> Tuple[float, float]:
        """根据CAGR获取期望评分范围"""
        if cagr >= 30:
            return (9.5, 10.0)
        elif cagr >= 25:
            return (8.5, 9.4)
        elif cagr >= 20:
            return (7.5, 8.4)
        elif cagr >= 18:
            return (7.0, 7.4)
        elif cagr >= 15:
            return (6.5, 6.9)
        elif cagr >= 12:
            return (5.5, 6.4)
        elif cagr >= 10:
            return (4.5, 5.4)
        elif cagr >= 8:
            return (3.5, 4.4)
        elif cagr >= 5:
            return (2.5, 3.4)
        else:
            return (0.5, 2.4)
    
    def _generate_summary(self) -> str:
        """生成验证摘要"""
        total_issues = sum(len(r.issues) for r in self.validation_results)
        total_suggestions = sum(len(r.suggestions) for r in self.validation_results)
        
        if total_issues == 0:
            return "报告质量优秀，无明显问题。"
        elif total_issues <= 3:
            return f"报告质量良好，发现{total_issues}个小问题，建议参考改进建议优化。"
        else:
            return f"报告存在{total_issues}个问题需要修正，请优先处理标记为'错误'的项。"
    
    def generate_report(self, json_path: str, markdown_path: str) -> str:
        """生成验证报告（Markdown格式）"""
        result = self.validate_report(json_path, markdown_path)
        
        report = f"""# AI验证报告

## 综合评分

**总体得分**: {result['overall_score']}/100  
**质量评级**: {result['grade']}  
**验证结果**: {'通过' if result['passed'] else '需改进'}

{result['summary']}

## 分项评分

"""
        
        for cat in result['categories']:
            status = "通过" if cat['passed'] else "需改进"
            report += f"""### {cat['name']} - {cat['score']}/{cat['max_score']} ({status})

"""
            if cat['issues']:
                report += "**问题**:\n"
                for issue in cat['issues']:
                    report += f"- ⚠️ {issue}\n"
                report += "\n"
            
            if cat['suggestions']:
                report += "**建议**:\n"
                for sug in cat['suggestions']:
                    report += f"- 💡 {sug}\n"
                report += "\n"
        
        report += """## 改进优先级

1. **高优先级**（影响报告可用性）:
   - 修复所有"错误"级别的问题
   - 确保JSON和Markdown文件完整

2. **中优先级**（提升报告质量）:
   - 补充缺失的章节
   - 增加数据密度

3. **低优先级**（锦上添花）:
   - 优化排版和可读性
   - 增加图表和表格

---

*本报告由AI验证工具自动生成*
"""
        
        return report


class RealtimeValidator:
    """
    实时验证器
    
    在分析过程中实时检查问题
    """
    
    @staticmethod
    def check_dimension_quality(file_path: str) -> Dict:
        """
        检查维度分析文件质量
        
        Args:
            file_path: 维度文件路径
            
        Returns:
            Dict: 质量检查结果
        """
        if not os.path.exists(file_path):
            return {
                "valid": False,
                "score": 0,
                "issues": ["文件不存在"]
            }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            issues = []
            score = 100
            
            # 检查长度
            if len(content) < 500:
                issues.append("内容过短，建议至少500字符")
                score -= 30
            
            # 检查结构
            if '##' not in content:
                issues.append("缺少二级标题，建议添加##结构")
                score -= 20
            
            # 检查数据
            if not any(c in content for c in ['%', '亿元', '万', 'CAGR']):
                issues.append("缺少数据支撑，建议添加量化指标")
                score -= 20
            
            return {
                "valid": score >= 60,
                "score": max(0, score),
                "issues": issues,
                "content_length": len(content)
            }
            
        except Exception as e:
            return {
                "valid": False,
                "score": 0,
                "issues": [f"读取文件出错: {e}"]
            }
    
    @staticmethod
    def check_cagr_consistency(cagr: float, score: float) -> Dict:
        """
        检查CAGR与评分一致性
        
        Args:
            cagr: 综合CAGR
            score: 综合评分
            
        Returns:
            Dict: 一致性检查结果
        """
        validator = AIReportValidator()
        expected_range = validator._get_expected_score_range(cagr)
        
        if expected_range[0] <= score <= expected_range[1]:
            return {
                "consistent": True,
                "message": f"评分与CAGR匹配: {score}分对应CAGR {cagr}%"
            }
        else:
            return {
                "consistent": False,
                "message": f"评分与CAGR不匹配: 评分{score}分，但CAGR {cagr}% 对应评分应在{expected_range}之间",
                "expected_range": expected_range
            }


# ========== 便捷函数 ==========

def quick_validate(json_path: str, markdown_path: str) -> bool:
    """快速验证报告是否合格"""
    validator = AIReportValidator()
    result = validator.validate_report(json_path, markdown_path)
    return result['passed']


def validate_and_report(json_path: str, markdown_path: str, output_path: str = None):
    """验证并输出报告"""
    validator = AIReportValidator()
    
    # 执行验证
    result = validator.validate_report(json_path, markdown_path)
    
    # 生成报告
    report = validator.generate_report(json_path, markdown_path)
    
    # 输出
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"验证报告已保存: {output_path}")
    else:
        print(report)
    
    return result['passed']


# ========== 测试代码 ==========

if __name__ == "__main__":
    # 测试
    print("AI验证工具测试")
    print("=" * 50)
    
    # 测试CAGR一致性检查
    result = RealtimeValidator.check_cagr_consistency(15, 6.8)
    print(f"CAGR=15%, Score=6.8: {result}")
    
    result = RealtimeValidator.check_cagr_consistency(15, 8.5)
    print(f"CAGR=15%, Score=8.5: {result}")
