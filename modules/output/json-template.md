**文件内容(v2.2.0新格式)**：
```json
{
  "company_name": "迈瑞医疗",
  "sanitized_name": "迈瑞医疗",
  "analysis_date": "2026-01-11",
  "framework_version": "v2.2.0",

  // ⭐ 综合CAGR（顶层标准字段，便于工具提取）
  "composite_cagr": 19.2,

  "score": {
    "total_score": 7.2,
    "rating": "☑️ 适度配置",
    "rating_text": "稳健成长型,低波动",
    "cagr": 19.2  // ⭐ 与composite_cagr保持一致
  },

  "summary": "## 核心结论\n\n**1. 双曲线共振开启,海外再造迈瑞**:\n   - 从2015-2020年的\"高速成长期\"(CAGR 20%+)进入{{FORECAST_START_YEAR}}-{{FORECAST_END_YEAR}}年的\"稳健成长期\"(综合CAGR 19.2%)\n   - 第一曲线(国内业务)从\"主引擎\"变为\"压舱石\"(占比从78.75%降至40.8%)\n   - 第二曲线(海外业务)成为\"新引擎\"(占比从21.25%提升至59.2%,CAGR 25-30%)\n\n**2. 投资建议**:\n   - 评级: ☑️ 适度配置(7.2/10分)\n   - 预期收益:基准情景5年CAGR 19.2%,营收从367亿增长至{{FORECAST_END_YEAR}}年营收\n   - 推荐仓位:20-30%(核心底仓)\n   - 适合投资者:追求稳健增长,收益预期20-25%/年,持有周期3-5年",
  "key_metrics": {
    "current_revenue": 367.26,
    "revenue_cagr_5y": 19.2,  // ⭐ 标准字段，与composite_cagr保持一致
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
      "cagr": 24.4,  // ⭐ 统一使用cagr字段名
      "revenue_{{FORECAST_END_YEAR}}": 1094,
      "description": "海外业务超预期(CAGR 30%+),新兴业务爆发(CAGR 35%+),医疗新基建超预期,集采降价压力缓解"
    },
    "base": {
      "probability": 0.50,
      "cagr": 19.6,  // ⭐ 统一使用cagr字段名
      "revenue_{{FORECAST_END_YEAR}}": 898,
      "description": "国内市场稳健增长,海外业务按计划推进,新兴业务逐步放量,适度集采降价"
    },
    "pessimistic": {
      "probability": 0.25,
      "cagr": 11.6,  // ⭐ 统一使用cagr字段名
      "revenue_{{FORECAST_END_YEAR}}": 637,
      "description": "地产基建下行影响医院采购,集采大幅降价,地缘政治风险,国内竞争加剧"
    },
    "weighted": {
      "probability": 1.00,
      "cagr": 19.2,  // ⭐ 统一使用cagr字段名（与composite_cagr一致）
      "revenue_{{FORECAST_END_YEAR}}": 882,
      "annual_revenue_forecast": {
        "{{FORECAST_START_YEAR}}": 460,
        "{{FORECAST_START_YEAR+1}}": 553,
        "{{FORECAST_START_YEAR+2}}": 663,
        "{{FORECAST_START_YEAR+3}}": 765,
        "{{FORECAST_END_YEAR}}": 882
      }
    }
  },
  "key_drivers": [
    {
      "factor": "海外市场扩张(第二曲线)",
      "impact": "极高",
      "contribution": "25-30%营收增长",
      "certainty": "高",
      "time_window": "{{FORECAST_YEAR_RANGE}}"
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
      "time_window": "{{FORECAST_YEAR_RANGE}}"
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

**字段说明(v2.2.0更新)**：

**⭐ 重要说明 - CAGR字段标准化**：

**顶层CAGR字段（必须填写）**:
- **composite_cagr**：综合CAGR（顶层标准字段，便于工具提取）
  - 这是主要CAGR字段，所有其他CAGR相关字段应与此值保持一致
  - 工具如`generate_reports.py`会优先查找此字段

**评分信息**:
- **score.cagr**：评分中的CAGR（应与composite_cagr一致）

**关键指标**:
- **key_metrics.revenue_cagr_5y**：5年营收CAGR（应与composite_cagr一致）

**情景分析**:
- **scenario_analysis.*.cagr**：各情景的CAGR（使用统一字段名`cagr`，不再使用`cagr_5y`）
  - `scenario_analysis.weighted.cagr`：加权综合CAGR（应与composite_cagr一致）

**⚠️ 废弃字段名（不再推荐使用）**:
- ~~`cagr_input`~~ → 使用 `composite_cagr`
- ~~`cagr_5y`~~ → 使用 `cagr`
- ~~`score.cagr_input`~~ → 使用 `composite_cagr`

**基本信息**:
- **company_name**：公司中文名称
- **sanitized_name**：标准化公司名称（用于文件名，可选）
- **analysis_date**：分析日期(YYYY-MM-DD)
- **framework_version**：框架版本号（如"v2.2.0"）

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
  - revenue_{{FORECAST_END_YEAR}}: 预测结束年份营收(亿元)
  - description: 情景描述(有利因素列表)
- **scenario_analysis.base**：基准情景
  - 同上
- **scenario_analysis.pessimistic**：悲观情景
  - 同上
- **scenario_analysis.weighted**：⭐️v2.0.0新增综合结果
  - probability: 1.00(加权平均)
  - cagr_5y: 综合5年CAGR(%)
  - revenue_{{FORECAST_END_YEAR}}: 综合预测结束年份营收(亿元)
  - annual_revenue_forecast: ⭐️v2.0.0新增年度预测(从{{FORECAST_START_YEAR}}到{{FORECAST_END_YEAR}}每年加权平均营收)

**关键驱动因素、风险、竞争地位、双曲线分析**:
- 保持v1.8.0格式不变

**动态占位符说明**（运行时自动替换）:
- `{{FORECAST_START_YEAR}}` - 预测起始年份（如 2026）
- `{{FORECAST_END_YEAR}}` - 预测结束年份（如 2031）
- `{{FORECAST_YEAR_RANGE}}` - 预测年份范围（如 "2026-2031"）
- `{{FORECAST_START_YEAR+1}}` - 预测起始年份+1（如 2027）
- `{{FORECAST_START_YEAR+2}}` - 预测起始年份+2（如 2028）
- `{{FORECAST_START_YEAR+3}}` - 预测起始年份+3（如 2029）

---

## v2.6.0更新：计算过程追踪字段 ⭐️ 新增

### calculation_trace 字段定义

在JSON中增加 `calculation_trace` 字段，用于记录所有关键计算的中间过程，使分析更加透明、可验证。

**字段结构**：
```json
{
  "calculation_trace": {
    "scenario_analysis": {
      "[情景名]": {
        "assumptions": {
          "[参数名]": {
            "value": "参数值",
            "basis": "设定依据"
          }
        },
        "annual_revenue": {
          "[年份]": "营收值"
        },
        "cagr_verification": "CAGR验证公式和结果"
      }
    },
    "weighted_average": {
      "formula": "加权公式",
      "calculation_steps": ["步骤1", "步骤2", "..."],
      "cagr_calculation": "CAGR计算过程"
    },
    "scoring": {
      "input_cagr": "输入CAGR",
      "matched_range": {"min": "下限", "max": "上限"},
      "score_range": {"min": "评分下限", "max": "评分上限"},
      "interpolation": "插值计算过程",
      "final_score": "最终评分"
    },
    "monte_carlo": {
      "input_distributions": {
        "[变量名]": {
          "type": "分布类型",
          "params": {"参数": "值"}
        }
      },
      "simulation_results": {
        "iterations": "模拟次数",
        "mean": "均值",
        "std": "标准差",
        "percentiles": {"P10": "值", "P50": "值", "P90": "值"}
      }
    },
    "esg_adjustment": {
      "E_factor": {
        "[因素]": "调整值",
        "total": "E因子合计"
      },
      "S_factor": {
        "[因素]": "调整值",
        "total": "S因子合计"
      },
      "G_factor": {
        "[因素]": "调整值",
        "total": "G因子合计"
      },
      "total_adjustment": "总调整系数"
    },
    "stress_testing": {
      "[情景名]": {
        "probability": "发生概率",
        "impact_chain": ["传导链条"],
        "financial_impact": "财务影响量化",
        "survival_probability": "生存概率"
      }
    }
  }
}
```

### 完整示例

```json
{
  "company_name": "迈瑞医疗",
  "composite_cagr": 14.5,

  "calculation_trace": {
    "scenario_analysis": {
      "optimistic": {
        "assumptions": {
          "overseas_cagr": {
            "value": 0.30,
            "basis": "2024年海外增速28% + 北美新客户+5% + 东南亚+3%"
          },
          "domestic_cagr": {
            "value": 0.15,
            "basis": "医疗新基建 + 国产替代率提升至50%"
          }
        },
        "annual_revenue": {
          "2025": 433.8,
          "2026": 514.1,
          "2027": 610.9,
          "2028": 728.2,
          "2029": 870.8
        },
        "cagr_verification": "(870.8/367)^(1/5)-1 = 18.9%"
      },
      "base": {
        "assumptions": {
          "overseas_cagr": {"value": 0.25, "basis": "考虑地缘政治风险，增速略下调"},
          "domestic_cagr": {"value": 0.12, "basis": "行业平均8-10%，龙头略高"}
        },
        "annual_revenue": {
          "2025": 421.2,
          "2026": 484.4,
          "2027": 558.4,
          "2028": 645.2,
          "2029": 747.4
        },
        "cagr_verification": "(747.4/367)^(1/5)-1 = 15.3%"
      },
      "pessimistic": {
        "assumptions": {
          "overseas_cagr": {"value": 0.15, "basis": "美国制裁风险，高端产品出口受限"},
          "domestic_cagr": {"value": 0.05, "basis": "医院采购预算紧缩，集采大幅降价"}
        },
        "annual_revenue": {
          "2025": 393.2,
          "2026": 421.9,
          "2027": 453.3,
          "2028": 487.8,
          "2029": 525.9
        },
        "cagr_verification": "(525.9/367)^(1/5)-1 = 7.5%"
      }
    },
    "weighted_average": {
      "formula": "乐观×25% + 基准×50% + 悲观×25%",
      "probability_basis": "默认概率，公司护城河深但地缘政治风险存在",
      "calculation_steps": [
        "870.8 × 25% = 217.7",
        "747.4 × 50% = 373.7",
        "525.9 × 25% = 131.5",
        "217.7 + 373.7 + 131.5 = 722.9"
      ],
      "cagr_calculation": "(722.9/367)^(1/5)-1 = 14.5%"
    },
    "scoring": {
      "input_cagr": 14.5,
      "matched_range": {"min": 12, "max": 15},
      "score_range": {"min": 5.5, "max": 6.4},
      "interpolation": "5.5 + (14.5-12)/(15-12) × (6.4-5.5) = 5.5 + 0.75 = 6.25",
      "final_score": 6.3
    },
    "esg_adjustment": {
      "E_factor": {
        "carbon_cost": -0.006,
        "environmental_compliance": -0.005,
        "total": -0.011
      },
      "S_factor": {
        "labor_cost": -0.0072,
        "supply_chain": -0.003,
        "total": -0.0102
      },
      "G_factor": {
        "equity_pledge": -0.002,
        "disclosure": -0.001,
        "total": -0.003
      },
      "total_adjustment": -0.0242
    }
  },

  "scenario_analysis": {
    "optimistic": {"probability": 0.25, "cagr": 18.9, "revenue_2029": 870.8},
    "base": {"probability": 0.50, "cagr": 15.3, "revenue_2029": 747.4},
    "pessimistic": {"probability": 0.25, "cagr": 7.5, "revenue_2029": 525.9},
    "weighted": {"probability": 1.00, "cagr": 14.5, "revenue_2029": 722.9}
  }
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|-----|------|------|
| `calculation_trace.scenario_analysis` | object | 各情景的计算过程 |
| `calculation_trace.scenario_analysis.*.assumptions` | object | 假设参数及依据 |
| `calculation_trace.scenario_analysis.*.annual_revenue` | object | 逐年营收计算结果 |
| `calculation_trace.scenario_analysis.*.cagr_verification` | string | CAGR验证公式 |
| `calculation_trace.weighted_average` | object | 加权平均计算过程 |
| `calculation_trace.weighted_average.formula` | string | 加权公式 |
| `calculation_trace.weighted_average.calculation_steps` | array | 计算步骤列表 |
| `calculation_trace.weighted_average.cagr_calculation` | string | CAGR计算过程 |
| `calculation_trace.scoring` | object | 评分计算过程 |
| `calculation_trace.scoring.input_cagr` | number | 输入CAGR |
| `calculation_trace.scoring.matched_range` | object | 命中的CAGR区间 |
| `calculation_trace.scoring.score_range` | object | 对应的评分区间 |
| `calculation_trace.scoring.interpolation` | string | 插值计算过程 |
| `calculation_trace.scoring.final_score` | number | 最终评分 |
| `calculation_trace.monte_carlo` | object | 蒙特卡洛模拟过程（可选） |
| `calculation_trace.esg_adjustment` | object | ESG调整计算过程（可选） |
| `calculation_trace.stress_testing` | object | 压力测试计算过程（可选） |

