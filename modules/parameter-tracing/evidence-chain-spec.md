# 证据链全链路溯源规范 v1.0

> 创建日期: 2026-06-13
> 框架版本: v2.6.0
> 关联模块: `modules/parameter-tracing/通用参数溯源系统框架.md`、`modules/output/save-report.md` 第 5.10 节

---

## 一、三级证据强度（强制 Level 3 全链路）

### Level 1 - 来源标注（最低，本项目不采用）

关键数字后注明来源机构名。

> 例: "营收 $82.9B（来源: 微软Q3财报）"

### Level 2 - 可追溯链接 + 原文摘录（中等，本项目不采用）

提供可点击 URL + 10-50 字原文摘录。

### Level 3 - 全链路溯源（最高，本项目强制）⭐

每个关键参数必须包含以下 9 个字段：

| 序号 | 字段 | 说明 |
|------|------|------|
| 1 | **search_query** | 触发该数据的搜索查询字符串 |
| 2 | **source_url** | 原始来源 URL（可点击） |
| 3 | **source_title** | 来源标题 |
| 4 | **source_date** | 来源发布日期（YYYY-MM-DD） |
| 5 | **source_type** | 来源类型（company_report / industry_research / news / government / other） |
| 6 | **quote** | 原文片段（10-100 字，必须能在 URL 页面中找到）。**外国公司**允许使用中文译文摘录，但必须保留 source_url 可追溯（完整英文原文保存在 search-results 中） |
| 7 | **extracted_value** | 从原文提取的数值 |
| 8 | **reliability** | 可靠度（高 / 中 / 低） |
| 9 | **timestamp** | 数据采集时间（ISO 8601） |

---

## 二、强制覆盖的参数清单

以下参数必须 100% 全链路溯源（缺失则 `validate_report.py` 验证失败）。

### 2.1 财务数据（必溯）

- `current_revenue`（当前营收）
- `revenue_growth_yoy`（营收同比增速）
- `operating_margin`（运营利润率）
- `net_margin`（净利率）
- `capex`（资本支出）
- `fcf`（自由现金流）
- `rpo`（商业剩余履约义务）

### 2.2 业务指标（必溯）

- `market_share`（市场份额）
- `segment_revenue`（分板块营收）
- `customer_count`（客户数）
- `seat_count`（席位 / 订阅数）
- `growth_rate_by_segment`（分板块增速）

### 2.3 预测假设（必溯）

- `scenario_probability`（情景概率）- 来源: 行业基准 + 主观判断
- `growth_assumption`（增速假设）- 来源: 历史数据 + 行业增速 + 公司指引
- `market_growth_rate`（行业增速）- 来源: 第三方研究机构

### 2.4 评分输入（必溯）

- `composite_cagr`（综合CAGR）- 来源: 本报告加权计算
- `score_lookup`（评分查表）- 来源: `modules/scoring/scoring-framework.md`

---

## 三、JSON 输出格式（v2.6.0 增强）

在 `RevGrowth_{公司}.json` 顶层增加 `evidence_chain` 字段：

```json
{
  "evidence_chain": {
    "version": "1.0",
    "level": 3,
    "total_params_traced": 15,
    "params": [
      {
        "param_name": "revenue_q3_fy2026_b_usd",
        "value": 82.9,
        "unit": "亿USD",
        "evidence": {
          "search_query": "Microsoft FY2026 Q3 earnings revenue",
          "source_url": "https://www.microsoft.com/en-us/investor/earnings/fy-2026/q3/press-release-webcast",
          "source_title": "FY26 Q3 - Press Releases - Investor Relations",
          "source_date": "2026-04-29",
          "source_type": "company_report",
          "quote": "Revenue was $82.9 billion and increased 18%",
          "extracted_value": 82.9,
          "reliability": "高",
          "timestamp": "2026-06-13T11:45:00"
        }
      }
    ],
    "untraced_critical_params": [],
    "coverage_pct": 100.0
  }
}
```

### 字段约束

- `source_url` 必须以 `http://` 或 `https://` 开头
- `quote` 长度 10-500 字符
- `source_date` 必须符合 `YYYY-MM-DD`
- `reliability` 取值限定：`高` / `中` / `低`
- `timestamp` 必须符合 ISO 8601（如 `2026-06-13T11:45:00`）

---

## 四、Markdown 报告呈现

每个关键数字后用**脚注式溯源**：

```markdown
## 关键财务指标

| 指标 | 数值 | 来源 |
|------|------|------|
| Q3 FY2026 营收 | $82.9B[^1] | 微软Q3财报 |
| 营收同比增速 | +18%[^1] | 微软Q3财报 |
```

报告末尾「参数溯源」章节的脚注区：

```markdown
## 参数溯源

[^1]: Microsoft FY26 Q3 Press Release (2026-04-29)
      URL: https://www.microsoft.com/en-us/investor/earnings/fy-2026/q3/press-release-webcast
      原文摘录: "Revenue was $82.9 billion and increased 18%"
      可靠度: 高
      数据采集时间: 2026-06-13T11:45:00
```

---

## 五、双向链接要求

- Markdown 脚注 `[^ref1]` ↔ JSON `evidence_chain.params[].evidence`
- 编号必须一一对应、数据一致
- `validate_report.py` 会交叉校验两者数量与字段完整性

---

## 六、覆盖率要求

| 类别 | 最低溯源率 |
|------|----------|
| 关键财务数据（必溯清单） | **100%** |
| 关键业务指标 | ≥ 90% |
| 预测假设（允许 reliability=低） | ≥ 80% |
| **综合** | **≥ 85%** |

- `total_params_traced` 必须 ≥ 10
- `untraced_critical_params` 必须为空数组（否则验证失败）
- `coverage_pct` 必须 ≥ 85.0

---

## 七、搜索结果原文保存要求（与 `skill.md` 第四步联动）

每次 `web_search` 调用后，必须立即保存结果到缓存，作为后续溯源引用的依据：

- 文件路径: `revenue-forecast-cache/{公司}/search-results/search-{N}-{简短关键词}.md`
- 内容: 查询字符串 + 前 3-5 条结果（含 `url` / `title` / `snippet` / `published_date`）
- 缺失则 `validate_steps.py` Step4 证据检查失败

详见 `modules/output/save-report.md` 第 5.10.3 节。

---

## 八、可靠度评级标准

| 等级 | 适用场景 |
|------|---------|
| **高** | 公司官方财报、年报、季报、投资者关系页面、监管机构披露（SEC、巨潮） |
| **中** | 一线券商研报、权威行业研究机构（Gartner、IDC、Bloomberg）、主流财经媒体（Reuters、Bloomberg、财新） |
| **低** | 二手转载、博客、估算值、主观判断（需在 quote 中说明判断依据） |

---

## 九、与 `validate_report.py` 的对应关系

| 规范条款 | 验证方法 |
|---------|---------|
| 第三节 JSON 格式 | `validate_evidence_chain()` |
| 第六节 覆盖率 | `validate_evidence_chain()` |
| 第五节 双向链接 | `validate_evidence_chain()`（脚注数 ≥ 10） |
| `save-report.md` 5.10 计算过程 | `validate_calculation_trace()` |
| 计算正确性 | `validate_calculation_consistency()` |
