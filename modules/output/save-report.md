## 五、保存报告 ⭐️ 新增章节

在完成完整的营收增长预测分析报告后，必须将结果保存到两个文件中。

### 5.1 输出目录结构

```
{当前工作目录}/
└── outputs/                              # 报告输出目录（如果不存在则自动创建）
    ├── RevGrowth_{公司中文名}.json       # 简要JSON摘要
    └── RevGrowth_FullReport_{公司中文名}.md  # 完整Markdown报告
```

**说明**：
- `{当前工作目录}` 为执行分析时的工作目录（通常为项目根目录）
- `{公司中文名}` 为输入参数 `company_name`，直接使用中文名称（如"阿里巴巴"）
- 如果 outputs 目录不存在，自动创建

**示例**：
```
C:\Users\郑曾波\Projects\Research/
└── outputs/
    ├── RevGrowth_阿里巴巴.json
    └── RevGrowth_FullReport_阿里巴巴.md
```

### 5.2 JSON摘要文件 ⭐️⭐️ v2.0.0更新

**文件路径**：`outputs/RevGrowth_{公司中文名}.json`

**文件内容(v2.0.0新格式)**：
```json
{
  "company_name": "迈瑞医疗",
  "analysis_date": "2026-01-11",
  "score": {
    "total_score": 7.2,
    "rating": "☑️ 适度配置",
    "rating_text": "稳健成长型,低波动"
  },
  "summary": "## 核心结论\n\n**1. 双曲线共振开启,海外再造迈瑞**:\n   - 从2015-2020年的\"高速成长期\"(CAGR 20%+)进入2025-2029年的\"稳健成长期\"(综合CAGR 19.2%)\n   - 第一曲线(国内业务)从\"主引擎\"变为\"压舱石\"(占比从78.75%降至40.8%)\n   - 第二曲线(海外业务)成为\"新引擎\"(占比从21.25%提升至59.2%,CAGR 25-30%)\n\n**2. 投资建议**:\n   - 评级: ☑️ 适度配置(7.2/10分)\n   - 预期收益:基准情景5年CAGR 19.2%,营收从367亿增长至898亿\n   - 推荐仓位:20-30%(核心底仓)\n   - 适合投资者:追求稳健增长,收益预期20-25%/年,持有周期3-5年",
  "key_metrics": {
    "current_revenue": 367.26,
    "revenue_cagr_5y": 19.2,
    "domestic_business_cagr": "12-15",
    "overseas_cagr": "25-30",
    "ivd_revenue": 137.65,
    "life_support_revenue": 135.57,
    "medical_imaging_revenue": 74.98,
    "overseas_revenue": 78.02,
    "overseas_ratio": 21.25,
    "emerging_business_revenue": "40+",
    "net_margin": 31.8,
    "moat_score": "8.5/10分"
  },
  "scenario_analysis": {
    "optimistic": {
      "probability": 0.25,
      "cagr_5y": 24.4,
      "revenue_2029": 1094,
      "description": "海外业务超预期(CAGR 30%+),新兴业务爆发(CAGR 35%+),医疗新基建超预期,集采降价压力缓解"
    },
    "base": {
      "probability": 0.50,
      "cagr_5y": 19.6,
      "revenue_2029": 898,
      "description": "国内市场稳健增长,海外业务按计划推进,新兴业务逐步放量,适度集采降价"
    },
    "pessimistic": {
      "probability": 0.25,
      "cagr_5y": 11.6,
      "revenue_2029": 637,
      "description": "地产基建下行影响医院采购,集采大幅降价,地缘政治风险,国内竞争加剧"
    },
    "weighted": {
      "probability": 1.00,
      "cagr_5y": 19.2,
      "revenue_2029": 882,
      "annual_revenue_forecast": {
        "2025": 460,
        "2026": 553,
        "2027": 663,
        "2028": 765,
        "2029": 882
      }
    }
  },
  "key_drivers": [
    {
      "factor": "海外市场扩张(第二曲线)",
      "impact": "极高",
      "contribution": "25-30%营收增长",
      "certainty": "高",
      "time_window": "2025-2030"
    },
    {
      "factor": "体外诊断业务稳健增长",
      "impact": "高",
      "contribution": "15-18%营收增长",
      "certainty": "高",
      "time_window": "持续"
    },
    {
      "factor": "新兴业务爆发(微创外科、动物医疗)",
      "impact": "高",
      "contribution": "25-30%+营收增长",
      "certainty": "中高",
      "time_window": "2025-2029"
    }
  ],
  "major_risks": [
    {
      "risk": "国内市场竞争加剧",
      "level": "中",
      "impact": "-5%至-10%营收增长",
      "mitigation": "提升高端产品占比,差异化竞争,加强品牌建设"
    },
    {
      "risk": "集采降价压力",
      "level": "中",
      "impact": "-10%至-20%毛利率",
      "mitigation": "加速海外业务拓展,提升高毛利产品占比"
    },
    {
      "risk": "地缘政治风险",
      "level": "低",
      "impact": "-10%至-20%海外业务",
      "mitigation": "非高端影像设备,风险相对可控"
    }
  ],
  "competitive_position": {
    "domestic_market_share": "中国最大医疗器械龙头",
    "global_market_share": "全球医疗器械企业排名约30-40位",
    "moat_score": "8.5/10分",
    "advantages": [
      "全产品线布局(监护仪、IVD、超声)",
      "成本优势(比GPS便宜20-40%)",
      "供应链优势(HyTest等并购补强)",
      "品牌认知度高(中国第一品牌)",
      "盈利能力强(净利率31.8%)"
    ],
    "disadvantages": [
      "相比GPS:全球品牌认知度仍有差距",
      "相比联影医疗:在高端影像设备技术仍有差距"
    ]
  },
  "dual_curve_analysis": {
    "first_curve": {
      "name": "国内业务(三大主业)",
      "current_ratio": 78.75,
      "target_ratio": "40-55",
      "cagr": "12-15",
      "description": "稳健增长,市占率提升空间大"
    },
    "second_curve": {
      "name": "海外业务",
      "current_ratio": 21.25,
      "target_ratio": "45-50",
      "cagr": "25-30",
      "description": "爆发式增长,性价比+全产品线驱动"
    },
    "third_curve": {
      "name": "新兴业务(微创外科、动物医疗、心血管、骨科)",
      "current_revenue": "40+",
      "cagr": "25-30+",
      "description": "高速增长,未来潜力大"
    },
    "transition_probability": 0.75,
    "transition_status": "衔接良好"
  }
}
```

**字段说明(v2.0.0更新)**:

**基本信息**:
- **company_name**：公司中文名称
- **analysis_date**：分析日期(YYYY-MM-DD)

**评分信息(v2.0.0简化)**:
- **score.total_score**：最终总分(0-10分,保留1位小数)
- **score.rating**：投资评级(emoji + 文字描述)
  - ✅ 强烈推荐(≥9.5分)
  - ✅ 推荐(7.5-9.4分)
  - ☑️ 接近推荐(7.0-7.4分)
  - ☑️ 适度配置(5.5-6.9分)
  - ⚠️ 观望(4.5-5.4分)
  - ❌ 不推荐(<4.5分)
- **score.rating_text**：评级说明(1-2句话概括特征)

**总结信息**:
- **summary**：完整总结文字(来自报告第九章,包含核心结论、投资建议、关键观察节点)

**关键指标**:
- **key_metrics.current_revenue**：当前营收(亿元)
- **key_metrics.revenue_cagr_5y**：综合5年CAGR(%)
- **key_metrics.domestic_business_cagr**：国内业务CAGR(范围)
- **key_metrics.overseas_cagr**：海外业务CAGR(范围)
- 其他业务指标...

**情景分析(v2.0.0新增weighted)**:
- **scenario_analysis.optimistic**：乐观情景
  - probability: 概率(如0.25)
  - cagr_5y: 5年CAGR(%)
  - revenue_2029: 2029年营收(亿元)
  - description: 情景描述(有利因素列表)
- **scenario_analysis.base**：基准情景
  - 同上
- **scenario_analysis.pessimistic**：悲观情景
  - 同上
- **scenario_analysis.weighted**：⭐️v2.0.0新增综合结果
  - probability: 1.00(加权平均)
  - cagr_5y: 综合5年CAGR(%)
  - revenue_2029: 综合2029年营收(亿元)
  - annual_revenue_forecast: ⭐️v2.0.0新增年度预测(2025-2029每年加权平均营收)

**关键驱动因素、风险、竞争地位、双曲线分析**:
- 保持v1.8.0格式不变

### 5.3 完整Markdown报告

**文件路径**：`outputs/RevGrowth_FullReport_{公司中文名}.md`

**文件内容**：完整的营收增长预测分析报告（从第一章到第九章的所有内容）

**报告结构**：
```markdown
# {公司名称} 营收增长预测分析报告

## 一、公司概况
...

## 二、双曲线业务深度分析⭐️
...

## 三、分维度深度分析
...

## 四、未来5年营收预测
...

## 五、关键驱动因素
...

## 六、主要风险因素
...

## 七、敏感性分析
...

## 八、营收增长综合评分⭐️
...

## 九、总结与建议
...

---
**报告生成时间**：YYYY-MM-DD HH:MM:SS
**分析框架版本**：v1.6.0
**分析师**：Claude AI
**数据来源**：公开财报、行业报告、新闻资讯等
```

### 5.4 JSON验证 ⭐️ 新增

在保存JSON之前，必须验证CAGR字段的完整性和一致性：

```python
def validate_cagr_fields(json_data):
    """
    验证JSON中的CAGR字段符合v2.2.0标准

    检查项：
    1. composite_cagr字段存在且非零
    2. 其他CAGR字段与composite_cagr保持一致
    3. 字段命名符合标准（不使用废弃字段名）
    """
    errors = []
    warnings = []

    # 1. 检查顶层composite_cagr字段
    composite_cagr = json_data.get('composite_cagr')
    if composite_cagr is None:
        errors.append("❌ 缺少顶层字段: composite_cagr")
    elif composite_cagr == 0:
        errors.append("❌ composite_cagr字段值为0，请检查数据")
    else:
        print(f"✅ composite_cagr: {composite_cagr}%")

    # 2. 检查score.cagr字段
    if 'score' in json_data and isinstance(json_data['score'], dict):
        score_cagr = json_data['score'].get('cagr')
        if score_cagr is not None:
            if composite_cagr and abs(score_cagr - composite_cagr) > 0.1:
                warnings.append(f"⚠️  score.cagr ({score_cagr}%) 与 composite_cagr ({composite_cagr}%) 不一致")
            else:
                print(f"✅ score.cagr: {score_cagr}%")

    # 3. 检查key_metrics.revenue_cagr_5y字段
    if 'key_metrics' in json_data:
        metrics_cagr = json_data['key_metrics'].get('revenue_cagr_5y')
        if metrics_cagr is not None:
            if composite_cagr and abs(metrics_cagr - composite_cagr) > 0.1:
                warnings.append(f"⚠️  key_metrics.revenue_cagr_5y ({metrics_cagr}%) 与 composite_cagr ({composite_cagr}%) 不一致")
            else:
                print(f"✅ key_metrics.revenue_cagr_5y: {metrics_cagr}%")

    # 4. 检查scenario_analysis字段命名
    if 'scenario_analysis' in json_data:
        scenario = json_data['scenario_analysis']
        for scenario_name in ['optimistic', 'base', 'pessimistic', 'weighted']:
            if scenario_name in scenario:
                scenario_data = scenario[scenario_name]

                # 检查是否使用了旧字段名cagr_5y
                if 'cagr_5y' in scenario_data:
                    warnings.append(f"⚠️  scenario_analysis.{scenario_name} 使用了旧字段名 'cagr_5y'，建议改为 'cagr'")

                # 检查cagr字段
                if 'cagr' in scenario_data:
                    scenario_cagr = scenario_data['cagr']
                    if scenario_name == 'weighted' and composite_cagr:
                        if abs(scenario_cagr - composite_cagr) > 0.1:
                            warnings.append(f"⚠️  scenario_analysis.weighted.cagr ({scenario_cagr}%) 与 composite_cagr ({composite_cagr}%) 不一致")
                    print(f"✅ scenario_analysis.{scenario_name}.cagr: {scenario_cagr}%")

    # 5. 检查废弃字段名
    deprecated_fields = ['cagr_input']
    for field in deprecated_fields:
        # 递归检查所有层级
        def check_deprecated(obj, path=''):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_path = f"{path}.{key}" if path else key
                    if key == field:
                        warnings.append(f"⚠️  发现废弃字段名: {new_path}，建议使用composite_cagr")
                    check_deprecated(value, new_path)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    check_deprecated(item, f"{path}[{i}]")

        check_deprecated(json_data)

    # 输出结果
    if errors:
        print("\n❌ 验证失败：")
        for error in errors:
            print(f"  {error}")
        return False

    if warnings:
        print("\n⚠️  警告：")
        for warning in warnings:
            print(f"  {warning}")

    if not warnings:
        print("\n✅ CAGR字段验证通过，符合v2.2.0标准")

    return True

# 使用示例
if __name__ == "__main__":
    # 示例JSON数据
    report_data = {
        "company_name": "迈瑞医疗",
        "composite_cagr": 19.2,  # ⭐ 标准字段
        "score": {
            "total_score": 7.2,
            "cagr": 19.2  # ⭐ 与composite_cagr一致
        },
        "key_metrics": {
            "revenue_cagr_5y": 19.2  # ⭐ 与composite_cagr一致
        },
        "scenario_analysis": {
            "weighted": {
                "cagr": 19.2  # ⭐ 统一使用cagr
            }
        }
    }

    # 验证
    is_valid = validate_cagr_fields(report_data)
    if is_valid:
        print("\n✅ 可以保存JSON文件")
    else:
        print("\n❌ 请修复CAGR字段后再保存")
```

### 5.5 保存操作流程（更新）

在报告完成后，按以下步骤执行：

#### 步骤1：创建输出目录
```python
import os

# 在当前工作目录创建 outputs 文件夹
output_dir = "outputs"
os.makedirs(output_dir, exist_ok=True)
print(f"✅ 输出目录已准备: {os.path.abspath(output_dir)}")
```

#### 步骤2：验证CAGR字段 ⭐️ 新增

```python
# 在生成JSON数据后，先验证CAGR字段
is_valid = validate_cagr_fields(report_data)
if not is_valid:
    print("❌ CAGR字段验证失败，请检查数据")
    return None, None
```

#### 步骤3：生成JSON文件
```python
import json
from datetime import datetime

# 准备JSON数据
company_name = "阿里巴巴"  # 使用中文名

report_data = {
    "company_name": company_name,
    "analysis_date": datetime.now().strftime("%Y-%m-%d"),
    "score": {
        "total_score": 5.3,
        "base_score": 5.21,
        "growth_quality": 0.2,
        "volatility": -0.5,
        "certainty": 0.55,
        "rating": "⚠️ 中性",
        "rating_text": "增长中枢下移，转型期科技巨头"
    },
    "summary": """## 核心结论

1. **增长中枢下移已成定局**：
   - 从2010-2020年的"高速增长期"(CAGR 30-50%)进入2020-2030年的"稳健增长期"(CAGR 10%)
   - 第一曲线(电商)从现金牛变为"瘦狗"(增长3-5%，市占率下滑)
   - 第二曲线(云+国际)是唯一希望(增长22-25%，2029年占比超50%)

2. **双曲线转换关键期(2025-2028)**：
   - 成功标志:2027-2028年第二曲线营收超过第一曲线
   - 失败风险:第一曲线加速衰退(<3%)，第二曲线不及预期(<15%)""",
    "key_metrics": {
        "current_revenue": 9412,
        "revenue_cagr_5y": 10.1,
        "first_curve_cagr": "3-5",
        "second_curve_cagr": "22-25",
        "first_curve_ratio": 48.6,
        "second_curve_ratio": 24.8
    },
    "scenario_analysis": {
        "optimistic": {
            "probability": 0.20,
            "cagr_5y": 16.4,
            "revenue_2029": 20087
        },
        "base": {
            "probability": 0.55,
            "cagr_5y": 10.1,
            "revenue_2029": 15219
        },
        "pessimistic": {
            "probability": 0.25,
            "cagr_5y": 4.5,
            "revenue_2029": 11718
        }
    }
}

# 保存JSON文件
json_path = f"outputs/RevGrowth_{company_name}.json"
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(report_data, f, ensure_ascii=False, indent=2)

print(f"✅ JSON摘要已保存: {os.path.abspath(json_path)}")
```

#### 步骤4：生成Markdown文件
```python
# 保存完整报告
full_report = """# 阿里巴巴集团营收增长预测分析报告

## 一、公司概况

### 基本信息与财务表现
**主营业务**:阿里巴巴是中国领先的多元化互联网科技公司...
**营收规模(2024财年)**:9,411.68亿元人民币，同比增长8%

...

## 九、总结与建议

### 核心结论
...

### 投资建议
**评级**:⚠️ **中性**(5.3/10分)

---

**报告生成时间**：2025-01-10 12:00:00
**分析框架版本**：v1.6.0
**分析师**：Claude AI
**数据来源**：公开财报、行业报告、新闻资讯等
"""

md_path = f"outputs/RevGrowth_FullReport_{company_name}.md"
with open(md_path, 'w', encoding='utf-8') as f:
    f.write(full_report)

print(f"✅ 完整报告已保存: {os.path.abspath(md_path)}")
```

### 5.5 完整示例代码

```python
import json
import os
from datetime import datetime
import re

def save_revenue_report(company_name, full_report_md, score_data, key_metrics, scenario_data):
    """
    保存营收增长预测报告到当前工作目录的 outputs 文件夹

    Args:
        company_name: 公司名称（中文，如"阿里巴巴"）
        full_report_md: 完整报告的Markdown文本
        score_data: 评分数据（字典）
        key_metrics: 关键指标（字典）
        scenario_data: 情景分析数据（字典）

    Returns:
        (json_path, md_path): 保存成功的文件路径（绝对路径）
    """

    # 1. 创建输出目录（在当前工作目录）
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    print(f"✅ 输出目录: {os.path.abspath(output_dir)}")

    # 2. 准备JSON数据
    report_data = {
        "company_name": company_name,
        "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "score": score_data,
        "summary": extract_summary_from_report(full_report_md),
        "key_metrics": key_metrics,
        "scenario_analysis": scenario_data
    }

    # 3. 保存JSON文件
    json_path = os.path.join(output_dir, f"RevGrowth_{company_name}.json")
    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        print(f"✅ JSON摘要已保存: {os.path.abspath(json_path)}")
    except Exception as e:
        print(f"❌ 保存JSON失败: {e}")
        json_path = None

    # 4. 保存Markdown文件
    md_path = os.path.join(output_dir, f"RevGrowth_FullReport_{company_name}.md")
    try:
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(full_report_md)
        print(f"✅ 完整报告已保存: {os.path.abspath(md_path)}")
    except Exception as e:
        print(f"❌ 保存Markdown失败: {e}")
        md_path = None

    return json_path, md_path

def extract_summary_from_report(full_report_md):
    """
    从完整报告中提取总结部分（第九章）

    Args:
        full_report_md: 完整报告Markdown文本

    Returns:
        summary_text: 总结部分的文本
    """
    # 查找"## 九、总结与建议"或"## 九、总结与建议"章节
    pattern = r'## 九、总结与建议\s*\n(.*?)(?=\n---|\Z)'
    match = re.search(pattern, full_report_md, re.DOTALL)

    if match:
        return match.group(1).strip()
    else:
        # 如果没找到，返回报告最后1000字
        return full_report_md[-1000:] if len(full_report_md) > 1000 else full_report_md

# 使用示例
if __name__ == "__main__":
    # 示例数据
    company_name = "阿里巴巴"

    full_report_md = """# 阿里巴巴集团营收增长预测分析报告

## 一、公司概况
...

## 九、总结与建议

### 核心结论

1. **增长中枢下移已成定局**：
   - 从2010-2020年的"高速增长期"(CAGR 30-50%)进入2020-2030年的"稳健增长期"(CAGR 10%)
   - 第一曲线(电商)从现金牛变为"瘦狗"(增长3-5%，市占率下滑)
   - 第二曲线(云+国际)是唯一希望(增长22-25%，2029年占比超50%)

### 投资建议

**评级**:⚠️ **中性**(5.3/10分)
...

---
**报告生成时间**：2025-01-10 12:00:00
**分析框架版本**：v1.6.0
"""

    score_data = {
        "total_score": 5.3,
        "base_score": 5.21,
        "growth_quality": 0.2,
        "volatility": -0.5,
        "certainty": 0.55,
        "rating": "⚠️ 中性",
        "rating_text": "增长中枢下移，转型期科技巨头"
    }

    key_metrics = {
        "current_revenue": 9412,
        "revenue_cagr_5y": 10.1,
        "first_curve_cagr": "3-5",
        "second_curve_cagr": "22-25",
        "first_curve_ratio": 48.6,
        "second_curve_ratio": 24.8
    }

    scenario_data = {
        "optimistic": {
            "probability": 0.20,
            "cagr_5y": 16.4,
            "revenue_2029": 20087
        },
        "base": {
            "probability": 0.55,
            "cagr_5y": 10.1,
            "revenue_2029": 15219
        },
        "pessimistic": {
            "probability": 0.25,
            "cagr_5y": 4.5,
            "revenue_2029": 11718
        }
    }

    # 保存报告
    json_path, md_path = save_revenue_report(
        company_name=company_name,
        full_report_md=full_report_md,
        score_data=score_data,
        key_metrics=key_metrics,
        scenario_data=scenario_data
    )

    print(f"\n✅ 报告保存完成！")
    print(f"当前工作目录: {os.getcwd()}")
    if json_path:
        print(f"JSON文件: {os.path.abspath(json_path)}")
    if md_path:
        print(f"Markdown文件: {os.path.abspath(md_path)}")
```

### 5.7 验证检查清单（更新）

保存报告后，进行以下验证：

- [ ] **CAGR字段验证** ⭐️ 新增
  - [ ] `composite_cagr` 字段存在且非零
  - [ ] 所有CAGR相关字段值保持一致（误差<0.1%）
  - [ ] 使用标准字段名（`cagr`而不是`cagr_5y`）
  - [ ] 未使用废弃字段名（`cagr_input`等）
- [ ] outputs 目录已创建在当前工作目录
- [ ] JSON文件格式正确（可通过 `json.load()` 验证）
- [ ] JSON包含所有必需字段（score、summary、key_metrics、scenario_analysis）
- [ ] Markdown文件可正常预览（格式正确、无乱码）
- [ ] 文件名使用公司中文名（如 `RevGrowth_阿里巴巴.json`）
- [ ] 文件大小合理（JSON < 50KB，Markdown < 500KB）

### 5.8 文件示例

**输出文件结构**：
```
C:\Users\郑曾波\Projects\Research\outputs\
├── RevGrowth_阿里巴巴.json
└── RevGrowth_FullReport_阿里巴巴.md
```

**JSON文件内容示例**：
```json
{
  "company_name": "阿里巴巴",
  "analysis_date": "2025-01-10 12:00:00",
  "score": {
    "total_score": 5.3,
    "rating": "⚠️ 中性"
  },
  "summary": "## 核心结论\n\n1. **增长中枢下移已成定局**...",
  "key_metrics": {...},
  "scenario_analysis": {...}
}
```

**Markdown文件内容示例**：
```markdown
# 阿里巴巴集团营收增长预测分析报告

## 一、公司概况
...

## 九、总结与建议
...
```

### 5.9 计算过程展示规范 ⭐️ v2.6.0新增

**核心原则**：每个关键结论必须采用**四段落结构**，先讲假设依据，再展示计算过程，最后给出结论数字。

#### 5.9.1 四段落结构模板

```markdown
### X.Y.1 假设依据
[说明参数来源、数据依据、判断逻辑]

### X.Y.2 计算过程
[展示公式、代入数值、逐步计算]

### X.Y.3 验证检查
[交叉验证、合理性检查]

### X.Y.4 结论
**结论**：[简洁明确的最终数字]
```

#### 5.9.2 情景预测章节示例

```markdown
### 4.1 乐观情景

#### 4.1.1 假设依据

海外业务假设CAGR = 30%，依据如下：
- 2024年海外实际增速为28%
- 北美市场新客户突破，预计贡献+5%增速
- 东南亚市场开拓，预计贡献+3%增速

国内业务假设CAGR = 15%，依据如下：
- 医疗新基建政策持续推进
- 国产替代率从35%提升至50%
- 集采降价压力部分缓解

#### 4.1.2 计算过程

| 年份 | 海外营收(亿) | 计算过程 | 国内营收(亿) | 计算过程 | 总营收(亿) |
|------|-------------|---------|-------------|---------|-----------|
| 2024 | 78.0 | 实际值 | 289.0 | 实际值 | 367.0 |
| 2025 | 101.4 | 78×1.30 | 332.4 | 289×1.15 | 433.8 |
| 2026 | 131.8 | 101.4×1.30 | 382.3 | 332.4×1.15 | 514.1 |
| 2027 | 171.3 | 131.8×1.30 | 439.6 | 382.3×1.15 | 610.9 |
| 2028 | 222.7 | 171.3×1.30 | 505.5 | 439.6×1.15 | 728.2 |
| 2029 | 289.5 | 222.7×1.30 | 581.3 | 505.5×1.15 | 870.8 |

#### 4.1.3 验证检查

```
CAGR = (870.8 / 367.0)^(1/5) - 1
     = (2.373)^(0.2) - 1
     = 1.189 - 1
     = 18.9%
```

#### 4.1.4 结论

**结论**：乐观情景5年CAGR = **18.9%**
```

#### 5.9.3 综合CAGR章节示例

```markdown
### 4.4 综合CAGR计算

#### 4.4.1 假设依据

采用默认概率分布：
- 乐观情景：25%（公司护城河深，但地缘政治风险存在）
- 基准情景：50%（最可能发生的情景）
- 悲观情景：25%（考虑外部不确定性）

#### 4.4.2 计算过程

| 情景 | 2029年营收(亿) | 概率 | 加权计算 | 加权营收(亿) |
|------|---------------|------|---------|-------------|
| 乐观 | 870.8 | 25% | 870.8×0.25 | 217.7 |
| 基准 | 747.4 | 50% | 747.4×0.50 | 373.7 |
| 悲观 | 525.9 | 25% | 525.9×0.25 | 131.5 |
| **合计** | - | 100% | 217.7+373.7+131.5 | **722.9** |

#### 4.4.3 验证检查

```
综合CAGR = (722.9 / 367.0)^(1/5) - 1
        = (1.970)^(0.2) - 1
        = 1.145 - 1
        = 14.5%
```

#### 4.4.4 结论

**结论**：综合5年CAGR = **14.5%**
```

#### 5.9.4 评分章节示例

```markdown
### 8.1 综合评分

#### 8.1.1 假设依据

**输入参数**：综合CAGR = 14.5%（来自第四章计算）

#### 8.1.2 计算过程

**查表结果**：

CAGR = 14.5% 命中区间：12-15%
对应评分区间：5.5-6.4

**线性插值**：
```
评分 = 下限评分 + (CAGR - 下限CAGR) / (上限CAGR - 下限CAGR) × (上限评分 - 下限评分)

评分 = 5.5 + (14.5 - 12) / (15 - 12) × (6.4 - 5.5)
     = 5.5 + 2.5 / 3 × 0.9
     = 5.5 + 0.75
     = 6.25
```

#### 8.1.3 验证检查

- CAGR = 14.5% ∈ [12%, 15%] ✅
- 评分 = 6.25 ∈ [5.5, 6.4] ✅
- 评级 = "适度配置" ✅

#### 8.1.4 结论

**结论**：综合评分 = **6.3分**（四舍五入）
**投资评级**：☑️ 适度配置
```

#### 5.9.5 结论格式规范

**单个数字结论**：
```markdown
**结论**：综合5年CAGR = **14.5%**
```

**多个数字结论**：
```markdown
**结论**：
- 综合5年CAGR = **14.5%**
- 2029年预测营收 = **722.9亿**
- 综合评分 = **6.3分**
```

**带条件的结论**：
```markdown
**结论**：
- 基准情景：CAGR = **15.3%**（概率50%）
- 乐观情景：CAGR = **18.9%**（概率25%）
- 悲观情景：CAGR = **7.5%**（概率25%）
- 综合CAGR = **14.5%**
```

#### 5.9.6 JSON输出增强

在JSON中增加 `calculation_trace` 字段：

```json
{
  "company_name": "迈瑞医疗",
  "composite_cagr": 14.5,

  "calculation_trace": {
    "scenario_analysis": {
      "optimistic": {
        "assumptions": {
          "overseas_cagr": {"value": 0.30, "basis": "2024年海外增速28%+新市场拓展"},
          "domestic_cagr": {"value": 0.15, "basis": "医疗新基建+国产替代"}
        },
        "annual_revenue": {"2025": 433.8, "2026": 514.1, "2027": 610.9, "2028": 728.2, "2029": 870.8},
        "cagr_verification": "(870.8/367)^(1/5)-1 = 18.9%"
      },
      "base": { "...": "..." },
      "pessimistic": { "...": "..." }
    },
    "weighted_average": {
      "formula": "乐观×25% + 基准×50% + 悲观×25%",
      "calculation_steps": ["870.8×25%=217.7", "747.4×50%=373.7", "525.9×25%=131.5", "合计=722.9"],
      "cagr_calculation": "(722.9/367)^(1/5)-1 = 14.5%"
    },
    "scoring": {
      "input_cagr": 14.5,
      "matched_range": {"min": 12, "max": 15},
      "score_range": {"min": 5.5, "max": 6.4},
      "interpolation": "5.5 + (14.5-12)/(15-12) × (6.4-5.5) = 6.25",
      "final_score": 6.3
    }
  }
}
```

