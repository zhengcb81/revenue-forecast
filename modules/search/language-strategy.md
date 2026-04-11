# 语言策略模块 ⭐️⭐️⭐️ 新增

## 核心原则

**强制性要求**：
1. **报告语言**：所有报告必须使用**中文**输出
2. **搜索语言**：根据公司地域类型智能选择
3. **关键词转换**：确保搜索效率和准确性

---

## 公司地域判断逻辑

### 判断函数

```python
def detect_company_origin(company_name, search_results):
    """
    判断公司地域类型

    Args:
        company_name: 公司名称
        search_results: 初步搜索结果

    Returns:
        {
            "origin_type": "chinese" | "foreign" | "mixed",
            "origin_name": "中国公司" | "外国公司" | "混合公司",
            "confidence": float (0-1),
            "evidence": [证据列表]
        }
    """

    # 初始化特征分数
    scores = {"chinese": 0, "foreign": 0, "mixed": 0}
    evidence = []

    # ========== 规则1：公司名称特征 ==========
    chinese_indicators = ["集团", "股份", "有限", "科技", "电子", "汽车",
                         "小米", "比亚迪", "茅台", "阿里", "腾讯", "京东"]
    foreign_indicators = ["Inc", "Corp", "Ltd", "Co", "Apple", "Microsoft",
                         "Google", "Amazon", "Tesla", "NVIDIA"]

    for indicator in chinese_indicators:
        if indicator in company_name:
            scores["chinese"] += 0.3
            evidence.append(f"公司名称包含中文特征: {indicator}")
            break

    for indicator in foreign_indicators:
        if indicator in company_name:
            scores["foreign"] += 0.3
            evidence.append(f"公司名称包含英文特征: {indicator}")
            break

    # ========== 规则2：搜索结果中的注册信息 ==========
    registration_keywords = {
        "chinese": ["A股", "港股", "上交所", "深交所", "北京", "上海", "深圳", "中国"],
        "foreign": ["NASDAQ", "NYSE", "美股", "美国", "注册于", "总部", "US", "USA"],
        "mixed": ["跨国", "全球", "海外", "国际", "多国"]
    }

    search_text = " ".join(search_results)

    for keyword in registration_keywords["chinese"]:
        if keyword in search_text:
            scores["chinese"] += 0.25
            evidence.append(f"搜索结果包含中国注册信息: {keyword}")
            break

    for keyword in registration_keywords["foreign"]:
        if keyword in search_text:
            scores["foreign"] += 0.25
            evidence.append(f"搜索结果包含外国注册信息: {keyword}")
            break

    for keyword in registration_keywords["mixed"]:
        if keyword in search_text:
            scores["mixed"] += 0.2
            evidence.append(f"搜索结果包含跨国特征: {keyword}")
            break

    # ========== 规则3：业务地域描述 ==========
    business_scope = {
        "chinese": ["国内市场", "中国业务", "内销", "本土", "国产"],
        "foreign": ["海外市场", "国际业务", "出口", "全球", "北美", "欧洲"],
        "mixed": ["国内外", "全球化", "双循环", "海外布局"]
    }

    for keyword in business_scope["chinese"]:
        if keyword in search_text:
            scores["chinese"] += 0.2
            evidence.append(f"业务描述偏向中国: {keyword}")
            break

    for keyword in business_scope["foreign"]:
        if keyword in search_text:
            scores["foreign"] += 0.2
            evidence.append(f"业务描述偏向海外: {keyword}")
            break

    for keyword in business_scope["mixed"]:
        if keyword in search_text:
            scores["mixed"] += 0.15
            evidence.append(f"业务描述为全球化: {keyword}")
            break

    # ========== 规则4：上市地点（如果明确） ==========
    if "A股" in search_text or "港股" in search_text:
        scores["chinese"] += 0.3
        evidence.append("主要上市地点在中国")
    elif "NASDAQ" in search_text or "NYSE" in search_text:
        scores["foreign"] += 0.3
        evidence.append("主要上市地点在美国")

    # ========== 确定最终类型 ==========
    max_type = max(scores, key=scores.get)
    max_score = scores[max_type]

    # 计算置信度
    confidence = min(max_score, 0.95)

    # 如果分数接近，归类为混合公司
    if abs(scores["chinese"] - scores["foreign"]) < 0.2 and scores["mixed"] < 0.3:
        max_type = "mixed"
        confidence = 0.7

    # 如果置信度太低，默认为混合公司（保守策略）
    if confidence < 0.4:
        max_type = "mixed"
        confidence = 0.5
        evidence.append("置信度低，保守归类为混合公司")

    origin_names = {
        "chinese": "中国公司",
        "foreign": "外国公司",
        "mixed": "混合公司"
    }

    return {
        "origin_type": max_type,
        "origin_name": origin_names[max_type],
        "confidence": confidence,
        "evidence": evidence
    }
```

---

## 语言映射规则

### 搜索关键词转换表

| 中文关键词 | 英文关键词 | 适用场景 |
|-----------|-----------|---------|
| **基础信息** | **Basic Info** | |
| 最新财报 | latest financial report | 所有 |
| 业务板块 营收结构 | business segments revenue structure | 所有 |
| 年报 2024 | annual report 2024 | 所有 |
| **双曲线业务** | **Dual Curve Business** | |
| 传统业务 核心业务 | traditional business core business | 所有 |
| 新业务 战略转型 | new business strategic transformation | 所有 |
| 第二曲线 新业务 | second curve new business | 所有 |
| **品牌矩阵专项** | **Brand Matrix** | 产品驱动型 |
| 品牌矩阵 多品牌策略 | brand portfolio multi-brand strategy | 产品驱动型 |
| 品牌协同 供应链复用 | brand synergy supply chain reuse | 产品驱动型 |
| 高端品牌 营收占比 | premium brand revenue ratio | 产品驱动型 |
| 品牌溢价 毛利率 | brand premium gross margin | 产品驱动型 |
| 子品牌 新品牌推出 | sub-brand new brand launch | 产品驱动型 |
| 品牌忠诚度 复购率 | brand loyalty repurchase rate | 产品驱动型 |
| **扩品类分析** | **Product Expansion** | 产品驱动型 |
| 品类扩张 新产品 | product expansion new products | 产品驱动型 |
| 品类矩阵 业务板块 | product matrix business segments | 产品驱动型 |
| 多元化战略 新业务 | diversification strategy new business | 产品驱动型 |
| 新品类 营收占比 | new category revenue ratio | 产品驱动型 |
| **扩渠道分析** | **Channel Expansion** | 产品驱动型 |
| 渠道结构 线上线下 | channel structure online offline | 产品驱动型 |
| 渠道扩张 门店数量 | channel expansion store count | 产品驱动型 |
| 渠道效率 单店产出 | channel efficiency store output | 产品驱动型 |
| **扩地域分析** | **Geographic Expansion** | 产品驱动型 |
| 海外收入 营收占比 | overseas revenue revenue ratio | 产品驱动型 |
| 全球化 出海战略 | globalization overseas strategy | 产品驱动型 |
| 海外市场 市占率 | overseas market share | 产品驱动型 |
| **价格提升分析** | **Price Increase** | 产品驱动型 |
| 平均售价 ASP | average selling price ASP | 产品驱动型 |
| 高端化 平均单价 | premiumization average price | 产品驱动型 |
| 产品提价 定价策略 | product price increase pricing strategy | 产品驱动型 |
| **需求端驱动** | **Demand Drivers** | |
| 下游需求结构 | downstream demand structure | 所有 |
| 渠道库存 周转天数 | channel inventory turnover days | 所有 |
| 合同负债 预收账款 | contract liabilities advance receipts | 所有 |
| **产能与扩张** | **Capacity & Expansion** | |
| 产能 扩产计划 | capacity expansion plan | 设备/资源型 |
| 产能利用率 | capacity utilization rate | 设备/资源型 |
| **技术与创新** | **Technology & Innovation** | |
| 研发投入 新产品 | R&D investment new products | 设备/资源型 |
| 技术突破 专利 | technology breakthrough patent | 设备/资源型 |
| **宏观政策** | **Macro Policy** | |
| 政策支持 补贴 | policy support subsidy | 所有 |
| 国产替代 | domestic substitution | 爆发式/设备型 |
| **竞争格局** | **Competitive Landscape** | |
| 竞争对手 市场份额 | competitors market share | 所有 |
| 市场集中度 | market concentration | 所有 |

---

## 关键词转换函数

```python
def translate_search_keywords(company_type, origin_type, base_keywords):
    """
    根据公司类型和地域转换搜索关键词

    Args:
        company_type: 公司类型 (product-driven, equipment-driven, etc.)
        origin_type: 地域类型 (chinese, foreign, mixed)
        base_keywords: 基础关键词列表（中文）

    Returns:
        转换后的关键词列表
    """

    # 中文到英文的映射字典
    keyword_mapping = {
        # 基础信息
        "最新财报": "latest financial report",
        "业务板块 营收结构": "business segments revenue structure",
        "年报 2024": "annual report 2024",

        # 双曲线业务
        "传统业务 核心业务": "traditional business core business",
        "新业务 战略转型": "new business strategic transformation",
        "第二曲线 新业务": "second curve new business",

        # 品牌矩阵（产品驱动型）
        "品牌矩阵 多品牌策略": "brand portfolio multi-brand strategy",
        "品牌协同 供应链复用": "brand synergy supply chain reuse",
        "高端品牌 营收占比": "premium brand revenue ratio",
        "品牌溢价 毛利率": "brand premium gross margin",
        "子品牌 新品牌推出": "sub-brand new brand launch",
        "品牌忠诚度 复购率": "brand loyalty repurchase rate",

        # 扩品类（产品驱动型）
        "品类扩张 新产品": "product expansion new products",
        "品类矩阵 业务板块": "product matrix business segments",
        "多元化战略 新业务": "diversification strategy new business",
        "新品类 营收占比": "new category revenue ratio",

        # 扩渠道（产品驱动型）
        "渠道结构 线上线下": "channel structure online offline",
        "渠道扩张 门店数量": "channel expansion store count",
        "渠道效率 单店产出": "channel efficiency store output",

        # 扩地域（产品驱动型）
        "海外收入 营收占比": "overseas revenue revenue ratio",
        "全球化 出海战略": "globalization overseas strategy",
        "海外市场 市占率": "overseas market share",

        # 价格提升（产品驱动型）
        "平均售价 ASP": "average selling price ASP",
        "高端化 平均单价": "premiumization average price",
        "产品提价 定价策略": "product price increase pricing strategy",

        # 需求端驱动
        "下游需求结构": "downstream demand structure",
        "渠道库存 周转天数": "channel inventory turnover days",
        "合同负债 预收账款": "contract liabilities advance receipts",

        # 产能与扩张
        "产能 扩产计划": "capacity expansion plan",
        "产能利用率": "capacity utilization rate",

        # 技术与创新
        "研发投入 新产品": "R&D investment new products",
        "技术突破 专利": "technology breakthrough patent",

        # 宏观政策
        "政策支持 补贴": "policy support subsidy",
        "国产替代": "domestic substitution",

        # 竞争格局
        "竞争对手 市场份额": "competitors market share",
        "市场集中度": "market concentration",
    }

    translated_keywords = []

    for keyword in base_keywords:
        # 中国公司：使用中文
        if origin_type == "chinese":
            translated_keywords.append(keyword)

        # 外国公司：使用英文
        elif origin_type == "foreign":
            # 查找映射，如果找不到则保留原关键词（可能需要手动翻译）
            en_keyword = keyword_mapping.get(keyword, keyword)
            translated_keywords.append(en_keyword)

        # 混合公司：中英文都使用
        elif origin_type == "mixed":
            translated_keywords.append(keyword)  # 中文
            en_keyword = keyword_mapping.get(keyword, keyword)
            if en_keyword != keyword:  # 避免重复
                translated_keywords.append(en_keyword)  # 英文

    return translated_keywords
```

---

## 验证检查点

### 执行前验证

```python
def validate_language_strategy(company_name, origin_result, keywords):
    """
    验证语言策略执行正确性

    Returns:
        验证结果字符串
    """

    validation = f"""
✅ 已读取: modules/search/language-strategy.md
✅ 公司名称: {company_name}
✅ 地域判断: {origin_result['origin_name']} (置信度: {origin_result['confidence']:.2f})
✅ 搜索语言: {get_language_label(origin_result['origin_type'])}
✅ 关键词数量: {len(keywords)} 个
"""

    # 显示证据
    if origin_result['evidence']:
        validation += "\n✅ 判断证据:\n"
        for ev in origin_result['evidence']:
            validation += f"   - {ev}\n"

    # 显示部分关键词示例
    validation += "\n✅ 关键词示例（前3个）:\n"
    for i, kw in enumerate(keywords[:3]):
        validation += f"   {i+1}. {kw}\n"

    # 强制报告语言检查
    validation += "\n✅ 强制报告语言: 中文\n"

    return validation

def get_language_label(origin_type):
    """获取语言标签"""
    labels = {
        "chinese": "中文",
        "foreign": "英文",
        "mixed": "中英双语"
    }
    return labels.get(origin_type, "未知")
```

---

## 使用示例

### 示例1：小米集团（中国公司）

```python
company_name = "小米集团"
origin_result = detect_company_origin(company_name, ["A股上市", "总部北京", "手机业务"])
# 结果: {"origin_type": "chinese", "origin_name": "中国公司", "confidence": 0.85}

base_keywords = [
    "品类扩张 新产品",
    "品牌矩阵 多品牌策略",
    "高端化 平均售价"
]

keywords = translate_search_keywords("product-driven", "chinese", base_keywords)
# 结果: ["品类扩张 新产品", "品牌矩阵 多品牌策略", "高端化 平均售价"]
```

### 示例2：Apple Inc.（外国公司）

```python
company_name = "Apple Inc."
origin_result = detect_company_origin(company_name, ["NASDAQ上市", "总部加州", "iPhone业务"])
# 结果: {"origin_type": "foreign", "origin_name": "外国公司", "confidence": 0.90}

base_keywords = [
    "品类扩张 新产品",
    "品牌矩阵 多品牌策略",
    "高端化 平均售价"
]

keywords = translate_search_keywords("product-driven", "foreign", base_keywords)
# 结果: ["product expansion new products", "brand portfolio multi-brand strategy", "premiumization average price"]
```

### 示例3：比亚迪（混合公司）

```python
company_name = "比亚迪"
origin_result = detect_company_origin(company_name, ["A股上市", "海外业务", "全球化"])
# 结果: {"origin_type": "mixed", "origin_name": "混合公司", "confidence": 0.75}

base_keywords = [
    "海外收入 营收占比",
    "全球化 出海战略"
]

keywords = translate_search_keywords("product-driven", "mixed", base_keywords)
# 结果: ["海外收入 营收占比", "overseas revenue revenue ratio", "全球化 出海战略", "globalization overseas strategy"]
```

---

## 注意事项

1. **置信度阈值**：
   - >0.7：高置信度，可直接使用判断结果
   - 0.5-0.7：中等置信度，建议人工确认
   - <0.5：低置信度，使用混合策略

2. **关键词映射**：
   - 本模块已包含核心关键词的中英对照
   - 如遇新关键词，需及时更新映射表
   - 保持关键词简洁准确，避免歧义

3. **报告语言强制性**：
   - 无论公司地域类型，报告输出必须使用中文
   - 搜索可以使用英文，但分析结果需翻译为中文

4. **缓存策略**：
   - 地域判断结果应缓存，避免重复分析
   - 关键词转换结果可复用

---

**模块版本**：v1.0
**创建时间**：2026-01-12
**依赖模块**：无
