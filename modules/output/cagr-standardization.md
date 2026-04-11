# CAGR字段标准化规范

## 📋 标准字段名定义

### 🔑 统一标准字段

所有JSON输出**必须**使用以下标准字段名：

```json
{
  "company_name": "公司名称",
  "analysis_date": "分析日期",

  // ⭐ 标准CAGR字段（顶层，便于提取）
  "composite_cagr": null,  // 综合CAGR（主要字段）

  // 详细评分信息
  "overall_score": {
    "score": 6.0,
    "max_score": 10,
    "cagr": 13.6,  // ⭐ 从composite_cagr复制
    "rating": "适度配置",
    "score_range": "12-15% → 5.5-6.4分"
  },

  // 关键指标（保留原有结构）
  "key_metrics": {
    "current_revenue": 9411.68,
    "revenue_cagr_5y": 13.6,  // ⭐ 标准字段，与composite_cagr一致
    "currency": "亿人民币",
    ...
  },

  // 情景分析
  "scenario_analysis": {
    "weighted": {
      "cagr": 13.6,  // ⭐ 统一使用cagr，而不是cagr_5y
      "revenue_2029": 17991,
      ...
    },
    "optimistic": {
      "cagr": 19.0,  // ⭐ 统一使用cagr
      ...
    },
    "base": {
      "cagr": 13.8,   // ⭐ 统一使用cagr
      ...
    },
    "pessimistic": {
      "cagr": 7.7,    // ⭐ 统一使用cagr
      ...
    }
  }
}
```

### 📊 字段优先级规则

**提取CAGR时的查找顺序**（用于`generate_reports.py`等工具）：

1. **`composite_cagr`** (顶层) - 最高优先级
2. **`key_metrics.revenue_cagr_5y`**
3. **`scenario_analysis.weighted.cagr`**
4. **`overall_score.cagr`**
5. **`key_metrics.cagr`**
6. 其他包含"cagr"的字段

## 🔄 迁移策略

### 旧格式 → 新格式映射

| 旧字段路径 | 新字段路径 | 说明 |
|-----------|-----------|------|
| `score.cagr_input` | `composite_cagr` | 药明生物格式 |
| `composite_cagr` | `composite_cagr` | Arkema格式（已正确） |
| `overall_score.cagr` | `composite_cagr` | 阿里巴巴格式 |
| `cagr` (顶层) | `composite_cagr` | Avantium格式 |
| `scenario_analysis.weighted.cagr_5y` | `scenario_analysis.weighted.cagr` | 统一字段名 |
| `scenario_analysis.base.cagr_5y` | `scenario_analysis.base.cagr` | 统一字段名 |
| `scenario_analysis.optimistic.cagr_5y` | `scenario_analysis.optimistic.cagr` | 统一字段名 |
| `scenario_analysis.pessimistic.cagr_5y` | `scenario_analysis.pessimistic.cagr` | 统一字段名 |

### 兼容性处理

**原则**：新格式应该**同时包含**旧字段和新字段，确保向后兼容：

```json
{
  // 新标准字段
  "composite_cagr": 13.6,

  "scenario_analysis": {
    "weighted": {
      "cagr": 13.6,        // ⭐ 新标准
      "cagr_5y": 13.6      // 保留旧字段（兼容）
    }
  },

  // 旧格式字段（保留兼容）
  "key_metrics": {
    "revenue_cagr_5y": 13.6,
    "cagr": 13.6           // 可选的额外字段
  }
}
```

## ✅ 验证规则

### 必需字段检查

生成JSON时，必须确保以下**至少一个**CAGR字段存在且非零：

```python
def validate_cagr_fields(json_data):
    """验证CAGR字段是否符合标准"""

    # 必需字段（至少一个）
    cagr_fields = [
        json_data.get('composite_cagr'),
        json_data.get('key_metrics', {}).get('revenue_cagr_5y'),
        json_data.get('scenario_analysis', {}).get('weighted', {}).get('cagr'),
        json_data.get('overall_score', {}).get('cagr')
    ]

    # 过滤None值
    valid_cagrs = [c for c in cagr_fields if c is not None and c != 0]

    if not valid_cagrs:
        raise ValueError("❌ 错误：未找到有效的CAGR字段！请确保至少填写以下字段之一：\n"
                        "  - composite_cagr\n"
                        "  - key_metrics.revenue_cagr_5y\n"
                        "  - scenario_analysis.weighted.cagr\n"
                        "  - overall_score.cagr")

    # 验证字段一致性
    primary_cagr = valid_cagrs[0]
    for i, cagr in enumerate(valid_cagrs):
        if abs(cagr - primary_cagr) > 0.1:
            print(f"⚠️  警告：CAGR字段值不一致！字段{i}: {cagr} vs 主字段: {primary_cagr}")

    return True
```

### 字段命名规范

**禁止使用的字段名**（已废弃）：
- ❌ `cagr_input` (使用 `composite_cagr`)
- ❌ `cagr_5y` (使用 `cagr`)
- ❌ `score.cagr` (使用 `composite_cagr`)

**推荐使用的字段名**：
- ✅ `composite_cagr` (顶层综合CAGR)
- ✅ `key_metrics.revenue_cagr_5y` (关键指标中的5年CAGR)
- ✅ `scenario_analysis.*.cagr` (情景分析中的CAGR)

## 📝 实施指南

### 1. 修改 `json-template.md`

在模板中明确标注标准字段：

```markdown
**标准CAGR字段（必须填写）**:
- **composite_cagr**：综合CAGR（顶层字段，便于工具提取）
- **key_metrics.revenue_cagr_5y**：关键指标中的5年CAGR
- **scenario_analysis.weighted.cagr**：加权情景的CAGR

**注意**：以上三个字段值应保持一致
```

### 2. 添加自动验证函数

在 `save-report.md` 中添加验证步骤：

```python
def validate_json_output(json_data):
    """验证JSON输出符合标准"""

    # 检查CAGR字段
    cagr_found = False
    cagr_value = None

    # 检查标准字段
    if 'composite_cagr' in json_data:
        cagr_value = json_data['composite_cagr']
        cagr_found = True
        print(f"✅ 找到composite_cagr: {cagr_value}%")

    if 'key_metrics' in json_data and 'revenue_cagr_5y' in json_data['key_metrics']:
        if cagr_value is None:
            cagr_value = json_data['key_metrics']['revenue_cagr_5y']
        cagr_found = True
        print(f"✅ 找到key_metrics.revenue_cagr_5y: {json_data['key_metrics']['revenue_cagr_5y']}%")

    if not cagr_found:
        print("⚠️  警告：未找到标准CAGR字段，建议添加composite_cagr字段")

    # 检查情景分析字段命名
    if 'scenario_analysis' in json_data:
        for scenario in ['optimistic', 'base', 'pessimistic', 'weighted']:
            if scenario in json_data['scenario_analysis']:
                data = json_data['scenario_analysis'][scenario]
                if 'cagr_5y' in data:
                    print(f"⚠️  警告：{scenario}使用了旧字段名'cagr_5y'，建议改为'cagr'")

    return True
```

### 3. 更新文档示例

所有示例JSON都应使用新标准格式。

## 🎯 预期效果

实施此标准后：

1. **字段统一**：所有JSON使用相同的CAGR字段名
2. **工具兼容**：`generate_reports.py`等工具可以准确提取CAGR
3. **向后兼容**：保留旧字段名，确保现有工具不受影响
4. **自动验证**：生成JSON时自动检查字段完整性

## 📚 参考资料

- 当前问题分析：`scripts/generate_reports.py` 中的 `extract_company_data()` 函数
- 模板定义：`json-template.md`
- 保存逻辑：`save-report.md`

---

**版本**: v1.0
**创建日期**: 2026-01-20
**维护者**: Claude AI Assistant