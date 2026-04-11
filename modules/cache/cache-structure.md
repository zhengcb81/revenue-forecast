# 缓存目录结构与文件规范

## 目录结构

```
{当前工作目录}/revenue-forecast-cache/
└── {公司名称}/ (文件系统安全名称)
    ├── metadata.json                       # 公司元数据
    ├── 双曲线业务分析.md
    ├── 宏观环境分析.md
    ├── 产业变革分析.md
    ├── 业务板块分析.md
    ├── 竞争力评估.md
    ├── 产能与运营分析.md
    ├── 市场拓展潜力.md
    ├── 定价能力与盈利分析.md
    ├── 技术创新与突破.md
    └── search-results/ (可选)
        ├── 双曲线业务搜索_20260111_1430.json
        ├── 宏观环境搜索_20260111_1430.json
        └── ...
```

## 公司目录命名规范

### 命名规则
使用URL编码或文件系统安全名称：

| 公司名称 | 目录名 |
|---------|-------|
| 小米集团 | 小米集团 |
| 贵州茅台 | 贵州茅台 |
| 中微公司 | 中微公司 |
| 珂玛科技 | 珂玛科技 |
| Apple Inc. | Apple_Inc |
| Tesla（有括号） | Tesla |

### 命名规则说明
1. 优先使用中文公司名称
2. 移除特殊字符：`/\:*?"<>|`
3. 替换空格为下划线
4. 长度限制：≤50字符
5. 大小写：统一使用原名称大小写

### Python实现示例
```python
def sanitize_company_name(name):
    """
    清理公司名称，生成文件系统安全的目录名

    Args:
        name: 原始公司名称

    Returns:
        safe_name: 安全的目录名称
    """
    import re

    # 移除非法字符
    safe_name = re.sub(r'[\\/:*?"<>|]', '', name)

    # 替换空格和特殊字符
    safe_name = re.sub(r'[\s\-]+', '_', safe_name)

    # 限制长度
    safe_name = safe_name[:50]

    # 移除首尾下划线
    safe_name = safe_name.strip('_')

    return safe_name

# 示例
sanitize_company_name("小米集团")  # -> "小米集团"
sanitize_company_name("Tesla Inc.")  # -> "Tesla_Inc"
sanitize_company_name("Company/Name")  # -> "CompanyName"
```

## metadata.json 结构

### 字段说明
```json
{
  "company_name": "小米集团",
  "sanitized_name": "小米集团",
  "company_type": "product-driven",
  "type_name": "产品驱动型",
  "type_confidence": 0.85,
  "first_analysis_date": "2026-01-05",
  "last_analysis_date": "2026-01-11 14:30:25",
  "analysis_count": 3,
  "cache_version": "v2.1.0",
  "dimension_cache_status": {
    "双曲线业务分析": {
      "last_updated": "2026-01-11 14:30:25",
      "cache_status": "fresh",
      "source_count": 4,
      "file_size": 2387
    },
    "宏观环境分析": {
      "last_updated": "2026-01-10 09:15:30",
      "cache_status": "stale",
      "source_count": 3,
      "file_size": 1876
    },
    "产业变革分析": {
      "last_updated": "",
      "cache_status": "not_exists",
      "source_count": 0
    }
  },
  "search_keywords_history": {
    "双曲线业务分析": ["小米 第二曲线", "小米 汽车", "小米 AIoT", "小米 战略"],
    "宏观环境分析": ["中国GDP 2025", "消费电子政策", "货币政策 2026"]
  }
}
```

### 字段详细说明

**基本信息**
- `company_name`: 原始公司名称
- `sanitized_name`: 安全的目录名称
- `company_type`: 公司类型标识（resource-driven/explosive-growth/equipment-driven/product-driven）
- `type_name`: 人类可读的公司类型名称
- `type_confidence`: 类型判断置信度（0-1）

**分析历史**
- `first_analysis_date`: 首次分析日期（YYYY-MM-DD）
- `last_analysis_date`: 最近分析日期（YYYY-MM-DD HH:MM:SS）
- `analysis_count`: 分析次数
- `cache_version`: 缓存版本（用于兼容性检查）

**维度缓存状态**
缓存状态："fresh"（很新鲜）| "stale"（较陈旧）| "outdated"（已过期）| "not_exists"（不存在）

```json
"dimension_cache_status": {
  "维度名称": {
    "last_updated": "最后更新时间戳",
    "cache_status": "缓存状态",
    "source_count": "数据来源数量",
    "file_size": "文件大小（字节）"
  }
}
```

## 维度缓存文件格式

### 文件命名
- 文件名：与研究维度完全一致的名称
- 编码：UTF-8
- 扩展名：.md

### 文件内容模板

```markdown
# 宏观环境分析

**缓存时间**：2026-01-11 14:30:25
**数据来源**：web_search × 3次
**下次更新建议**：2026-01-18（7天后）
**分析员**：Claude AI

---

## 关键发现

### 1. GDP增长预测
- 2025年：5.2%（世界银行预测）
- 2026年：5.0%（IMF预测）
- 对行业影响：稳定增长有利于消费电子需求

### 2. 货币政策
- 当前政策：稳健偏宽松
- 预期措施：预计2026年降准50bp
- 传导机制：降低融资成本，刺激企业投资

### 3. 行业监管
- 新能源补贴：延续至2027年
- 碳减排政策：制造业企业需达到碳排放标准
- 影响评估：增加合规成本，但长期有利于龙头企业

---

## 详细分析

[详细分析内容，约500-1500字]

---

## 信息来源

1. **世界银行《全球经济展望》**（2026-01-10）
   - 链接：https://www.worldbank.org/...
   - 关键数据：中国经济增速5.2%

2. **IMF《世界经济展望》**（2025-12-28）
   - 链接：https://www.imf.org/...
   - 关键数据：全球经济增长预测3.1%

3. **工信部《电子信息制造业发展规划》**（2025-12-15）
   - 链接：http://www.miit.gov.cn/...
   - 关键政策：新能源汽车补贴延续

4. **央行《货币政策执行报告》**（2025-11-30）
   - 链接：http://www.pbc.gov.cn/...
   - 关键观点：预计降准50bp

---

## 数据标签

**重要度**：高 ⭐️
**确定性**：中高
**时效性**：较新（7天内）
```

### 内容结构说明

1. **头部信息**：固定格式，包含元数据
2. **关键发现**：3-5个核心要点，每点包含数据支撑
3. **详细分析**：完整分析内容，约500-1500字
4. **信息来源**：至少2-3个来源，包含URL和关键数据点
5. **数据标签**：重要度、确定性、时效性评估

## 搜索历史存储

### 存储位置
`search-results/` 子目录

### 文件命名规则
`{维度名称}_搜索_{YYYYMMDD}_{HHMM}.json`

### JSON结构
```json
{
  "search_timestamp": "2026-01-11 14:30:25",
  "dimension": "双曲线业务分析",
  "keywords": ["关键词1", "关键词2", "关键词3"],
  "search_results": [
    {
      "query": "小米 第二曲线",
      "results": [
        {
          "title": "小米战略转型：汽车业务成为第二增长极",
          "url": "https://example.com/article123",
          "snippet": "小米汽车2024年首年交付超10万台...",
          "date": "2026-01-08",
          "source_rank": 1
        }
      ]
    }
  ]
}
```

## 缓存管理工具函数

### 1. 初始化公司目录
```python
def init_company_cache(company_name):
    """
    初始化公司缓存目录

    Args:
        company_name: 公司名称
    """
    base_cache_dir = "revenue-forecast-cache"
    company_dir = sanitize_company_name(company_name)
    full_path = os.path.join(base_cache_dir, company_dir)

    # 创建目录
    os.makedirs(full_path, exist_ok=True)
    os.makedirs(os.path.join(full_path, "search-results"), exist_ok=True)

    # 创建初始metadata.json
    metadata = {
        "company_name": company_name,
        "sanitized_name": company_dir,
        "first_analysis_date": datetime.now().strftime("%Y-%m-%d"),
        "last_analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "analysis_count": 0,
        "cache_version": "v2.1.0",
        "dimension_cache_status": {},
        "search_keywords_history": {}
    }

    metadata_path = os.path.join(full_path, "metadata.json")
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"✅ 公司缓存目录已创建: {full_path}")
    return full_path
```

### 2. 获取缓存文件路径
```python
def get_cache_file_path(company_name, dimension):
    """
    获取维度缓存文件路径

    Args:
        company_name: 公司名称
        dimension: 研究维度名称

    Returns:
        file_path: 缓存文件路径
    """
    base_dir = "revenue-forecast-cache"
    company_dir = sanitize_company_name(company_name)
    return os.path.join(base_dir, company_dir, f"{dimension}.md")
```

### 3. 检查缓存新鲜度
```python
def check_cache_freshness(company_name, dimension):
    """
    检查缓存新鲜度

    Args:
        company_name: 公司名称
        dimension: 研究维度名称

    Returns:
        {
            "status": "fresh" | "stale" | "outdated" | "not_exists",
            "last_updated": datetime object,
            "days_diff": float,
            "reason": str
        }
    """
    cache_path = get_cache_file_path(company_name, dimension)

    if not os.path.exists(cache_path):
        return {
            "status": "not_exists",
            "last_updated": None,
            "days_diff": float('inf'),
            "reason": "缓存文件不存在"
        }

    # 读取文件时间戳（可以在文件头部，也可以用文件创建时间）
    with open(cache_path, 'r', encoding='utf-8') as f:
        first_line = f.readline().strip()

        # 解析时间戳
        if first_line.startswith("**缓存时间**"):
            timestamp_str = first_line.split("：**")[1].strip()
            last_updated = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        else:
            # 使用文件创建时间
            last_updated = datetime.fromtimestamp(os.path.getctime(cache_path))

    current_time = datetime.now()
    days_diff = (current_time - last_updated).total_seconds() / 86400

    # 判断新鲜度
    if days_diff < 1:
        status = "fresh"
        reason = "很新鲜（\u003c24小时）"
    elif days_diff < 7:
        status = "fresh"
        reason = "新鲜（1-7天）"
    elif days_diff < 30:
        status = "stale"
        reason = "较陈旧（7-30天）"
    else:
        status = "outdated"
        reason = "已过期（\u003e30天）"

    return {
        "status": status,
        "last_updated": last_updated,
        "days_diff": days_diff,
        "reason": reason
    }
```

### 4. 更新metadata.json
```python
def update_metadata(company_name, dimension, search_count, file_size):
    """
    更新metadata.json中的维度状态

    Args:
        company_name: 公司名称
        dimension: 研究维度名称
        search_count: 使用数据源数量
        file_size: 缓存文件大小（字节）
    """
    base_dir = "revenue-forecast-cache"
    company_dir = sanitize_company_name(company_name)
    metadata_path = os.path.join(base_dir, company_dir, "metadata.json")

    # 读取现有metadata
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)

    # 更新维度状态
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    metadata["dimension_cache_status"][dimension] = {
        "last_updated": current_time,
        "cache_status": "fresh",
        "source_count": search_count,
        "file_size": file_size
    }

    # 更新总分析次数
    metadata["analysis_count"] += 1
    metadata["last_analysis_date"] = current_time

    # 保存回文件
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"✅ metadata.json已更新: {metadata_path}")
```

## 缓存策略

### 何时复用缓存？

| 缓存状态 | 时间范围 | 复用策略 |
|---------|---------|---------|
| **新鲜（fresh）** | < 7天 | 完全复用，跳过搜索 |
| **较陈旧（stale）** | 7-30天 | 复用+少量验证搜索（1-2次） |
| **已过期（outdated）** | > 30天 | 重新搜索，但保留旧缓存作为参考 |
| **不存在（not_exists）** | - | 全新搜索 |

### 数据保留策略

1. **保留所有历史缓存**：不自动删除旧缓存文件
2. **metadata.json维护最近10次分析记录**
3. **维度更新时覆盖原文件**，但保留历史版本在Git中
4. **search-results/目录按季度归档**（可选功能）

## 兼容性考虑

### 版本兼容性
- `cache_version`: "v2.1.0"
- 版本升级时，保留旧缓存，提供迁移工具

### 文件编码
- 统一使用UTF-8编码
- 包含BOM的文件会自动检测并处理

### 系统兼容性
- Windows/Linux/macOS通用路径
- 使用`os.path.join()`处理路径分隔符
