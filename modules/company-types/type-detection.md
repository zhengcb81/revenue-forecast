# 公司类型判断逻辑

## 判断流程

### 步骤1：初步信息搜集
调用`modules/analysis/search-strategy.md`的基础搜索策略，搜索以下关键词：
- "{公司名} 主营业务"
- "{公司名} 行业分类"
- "{公司名} 产品类型"
- "{公司名} 年报 营收结构"

### 步骤2：特征提取与分析

基于搜索结果提取以下特征：

1. **主营业务描述**
   - 产品/服务类型
   - 目标市场（B端/C端/G端）
   - 供应链位置（上游/中游/下游）

2. **营收驱动因素**
   - 销售额驱动（品类/渠道/地域/价格提升）
   - 技术驱动（研发/专利/技术突破）
   - 资源驱动（价格波动/产能扩张/储量增长）

3. **业务特征**
   - 销售渠道模式（直销/经销/电商）
   - 产品形态（设备/消费品/原材料）
   - 客户类型（企业/个人/政府）

### 步骤3：类型规则匹配

#### 规则1：资源驱动型（最高优先级）
**匹配条件**（满足任一）：
- 主营业务包含关键词：采矿、矿山、矿产、能源、石油、天然气、煤炭、稀土、铁矿、钛矿
- 产品类型：大宗商品、原材料、资源储备、精矿、原矿
- 财务特征：营收与矿产/能源价格高度相关，周期性明显

**示例公司**：安宁股份、紫金矿业、中国神华、宁德时代（上游锂矿业务）

#### 规则2：爆发式增长型
**匹配条件**（同时满足）：
- 技术突破：打破国外垄断、实现国产替代
- 验证状态：已完成客户验证，具备量产条件
- 市场空间：国产化率<20%，替代空间巨大（目标市场>50亿元）
- 产品特征：关键零部件/材料（占设备成本>10%）

**示例公司**：珂玛科技（静电卡盘、陶瓷加热器）、拓荆科技（薄膜沉积设备）

#### 规则3：设备驱动型
**匹配条件**（满足任一）：
- 行业类别：半导体设备、工业母机、医疗设备、高端装备
- 产品特征：B2B销售、长订单周期（>3个月）、技术连续延伸
- 客户类型：晶圆厂、制造企业、医院（B端）
- 增长逻辑：技术突破+客户升级+国产替代

**示例公司**：中微公司、北方华创、迈瑞医疗、联影医疗

#### 规则4：服务驱动型（新增）
**匹配条件**（满足任一）：
- 行业类别：CXO、CRO、CDMO、CMO、医药研发外包、专业服务
- 业务特征：B2B服务、无实体产品交付、客户绑定度高
- 收费模式：服务费+里程碑+销售分成

**细分类型**：
- 人力密集型：研发人员占比高，CRO为主（药明康德）
- 产能密集型：固定资产占比高，CDMO为主（药明生物）

**示例公司**：药明康德、药明生物、康龙化成、泰格医药

#### 规则5：代工驱动型（新增）
**匹配条件**（满足任一）：
- 行业类别：半导体代工、晶圆代工、生物药CDMO、合同制造、电子制造服务
- 业务特征：资本开支密集（Capex/Revenue>15%）、产能驱动增长、技术代际升级
- 关键指标：产能利用率、每单位产能收入、技术节点领先度
- 增长逻辑：产能扩张×技术升级×客户绑定×定价能力

**细分类型**：
- 半导体代工：台积电、中芯国际、华虹半导体
- 生物药CDMO：药明生物、三星生物、Lonza
- 其他代工：富士康、比亚迪电子

**示例公司**：台积电、药明生物、中芯国际、三星生物

#### 规则6：资本驱动型（新增）

**匹配条件（满足任一）**：
- 行业类别：银行、保险、证券、信托、基金、财务公司
- 主营业务：金融服务、资产管理、投资银行、经纪业务
- 财务特征：资产负债表驱动、杠杆经营、资本金要求高
- 监管约束：资本充足率、偿付能力、风险管理要求严格

**核心驱动因素**：
- 银行：生息资产规模 × 净息差 + 中间业务 + 投资收益
- 保险：保费规模 × 投资收益率 - 负债成本 + 准备金
- 证券：经纪业务 + 投行业务 + 自营投资收益

**示例公司**：招商银行、中国平安、中信证券

#### 规则6：研发驱动型（新增）

**匹配条件（同时满足）**：
- 行业类别：创新药、生物科技、医疗器械（创新）、高科技
- 研发投入占比：>15%（vs 传统行业<5%）
- 增长逻辑：研发管线推进 + 临床试验成功 + 监管审批
- 估值方法：管线贴现（rNPV）为主，而非市盈率P/E

**关键特征**：
- 当前营收主要来自少数在售产品
- 未来增长高度依赖在研管线成功上市
- 高风险高回报，临床试验成功率是关键变量

**示例公司**：恒瑞医药、百济神州、信达生物、荣昌生物

#### 规则7：订阅驱动型（新增）

**匹配条件（满足任一）**：
- 商业模式：SaaS软件订阅、内容订阅、会员制、订阅电商
- 财务特征：经常性收入（Recurring Revenue）占比>60%
- 关键指标：MRR/ARR、留存率、净收入留存率(NRR)、LTV/CAC
- 客户行为：持续付费、升级套餐、高转换成本

**核心公式**：
营收增长率 ≈ 新增用户贡献 + 净收入留存率(NRR)贡献 + ARPU提升贡献

**示例公司**：金山办公（WPS订阅）、用友网络、广联达、爱奇艺

#### 规则8：平台驱动型（新增）
**匹配条件**（满足任一）：
- 收入模式：广告、佣金、服务费（非产品销售）
- 业务特征：双边市场、网络效应、平台撮合
- 毛利率：>50%（高毛利平台服务）
- 轻资产：存货占比<10%，现金占比>50%
- 典型公司：拼多多(PDD)、美团、阿里(BABA)

**判断逻辑**：
1. 营收结构：广告+佣金占比 > 60%
2. 平台指标：披露GMV、订单量、用户数
3. 资产结构：现金及等价物 / 总资产 > 50%
4. 毛利率：毛利率 > 50%

**评分**: 每满足1项得2分，≥6分判为platform-driven

#### 规则9：产品驱动型（默认）
**匹配条件**：
- 不满足以上八类
- 消费品特征：手机、家电、汽车、快消品、服装
- 增长逻辑：扩品类+扩渠道+扩地域+价格提升
- 决策主体：消费者（C端）

**示例公司**：小米集团、比亚迪、农夫山泉、安踏、贵州茅台

### 步骤4：置信度评估

**高置信度（>0.8）**：
- 多个特征同时匹配
- 搜索结果中明确描述公司类型
- 示例："中微公司是半导体设备龙头"

**中置信度（0.6-0.8）**：
- 主要特征匹配，部分特征模糊
- 示例：既有设备特征，又有消费品特征

**低置信度（<0.6）**：
- 特征模糊，难以归类
- 需要人工确认或提供默认类型

## 判断算法实现

```python
def detect_company_type(company_name, search_results):
    """
    判断公司类型

    Args:
        company_name: 公司名称
        search_results: 搜索结果列表

    Returns:
        {
            "company_type": "resource-driven" | "explosive-growth" | "equipment-driven" | "service-driven" | "foundry-driven" | "capital-driven" | "rd-driven" | "subscription-driven" | "platform-driven" | "product-driven",
            "sub_type": "人力密集" | "产能密集" | "半导体代工" | "生物药CDMO" | "其他代工" | None,
            "confidence": float (0-1),
            "evidence": [证据列表]
        }
    """
    # 初始化特征分数
    scores = {
        "resource-driven": 0,
        "explosive-growth": 0,
        "equipment-driven": 0,
        "service-driven": 0,
        "foundry-driven": 0,
        "capital-driven": 0,
        "rd-driven": 0,
        "subscription-driven": 0,
        "platform-driven": 0,
        "infrastructure-driven": 0,
        "project-driven": 0,
        "product-driven": 0
    }

    # ========== 资源驱动型规则 ==========
    resource_keywords = ["采矿", "矿山", "矿产", "能源", "石油", "天然气", "煤炭", "稀土", "铁矿", "钛矿", "精矿", "原矿"]
    for keyword in resource_keywords:
        if keyword in search_results:
            scores["resource-driven"] += 0.2

    # ========== 爆发式增长型规则 ==========
    explosive_keywords = ["打破国外垄断", "国产替代", "验证通过", "量产", "关键零部件", "市场份额极低"]
    if len([k for k in explosive_keywords if k in search_results]) >= 3:
        scores["explosive-growth"] += 0.15

    # ========== 设备驱动型规则 ==========
    equipment_keywords = ["半导体设备", "工业母机", "医疗设备", "晶圆厂", "长订单周期", "技术突破"]
    for keyword in equipment_keywords:
        if keyword in search_results:
            scores["equipment-driven"] += 0.1

    # ========== 服务驱动型规则 ==========
    service_keywords = ["CXO", "CRO", "CDMO", "CMO", "合同研发", "合同生产", "外包服务",
                        "B2B服务", "医药研发外包", "生物药CDMO", "大分子CDMO", "专业服务"]
    for keyword in service_keywords:
        if keyword in search_results:
            scores["service-driven"] += 0.15

    # ========== 代工驱动型规则 ==========
    foundry_keywords = ["半导体代工", "晶圆代工", "合同制造", "电子制造服务", "EMS", "产能利用率",
                       "资本开支密集", "Capex", "产能扩张", "技术节点", "先进制程", "生物药CDMO",
                       "万升产能", "晶圆厂", "制造服务", "代工厂"]
    for keyword in foundry_keywords:
        if keyword in search_results:
            scores["foundry-driven"] += 0.15

    # ========== 资本驱动型规则 ==========
    capital_keywords = ["银行", "保险", "证券", "信托", "基金", "财务公司", "金融服务",
                       "资本充足率", "净息差", "偿付能力", "投资银行", "经纪业务", "资产管理"]
    for keyword in capital_keywords:
        if keyword in search_results:
            scores["capital-driven"] += 0.15

    # ========== 研发驱动型规则 ==========
    rd_keywords = ["创新药", "生物科技", "医疗器械", "研发管线", "临床试验", "监管审批",
                  "临床试验I期", "II期", "III期", "NDA", "管线估值", "rNPV", "研发投入占比>15%"]
    for keyword in rd_keywords:
        if keyword in search_results:
            scores["rd-driven"] += 0.12

    # ========== 订阅驱动型规则 ==========
    subscription_keywords = ["SaaS", "订阅", "会员制", "WPS订阅", "软件订阅", "内容订阅",
                            "经常性收入", "MRR", "ARR", "留存率", "NRR", "LTV/CAC", "ARPU"]
    for keyword in subscription_keywords:
        if keyword in search_results:
            scores["subscription-driven"] += 0.12

    # ========== 平台驱动型规则 ==========
    platform_keywords = ["平台", "电商平台", "双边市场", "网络效应", "撮合交易", "GMV", "交易佣金",
                        "广告收入", "服务费", "DAU", "MAU", "ARPU", "货币化率", "take rate",
                        "内容平台", "短视频平台", "服务平台", "本地生活", "社交平台", "即时通讯",
                        "生态系统", "护城河", "用户规模", "订单量"]
    for keyword in platform_keywords:
        if keyword in search_results:
            scores["platform-driven"] += 0.12

    # ========== 基础设施驱动型规则 ==========
    infrastructure_keywords = [
        "电力", "电网", "发电", "水电", "风电", "光伏", "核电",
        "水务", "供水", "污水处理", "燃气", "天然气", "城市燃气",
        "高速公路", "港口", "机场", "铁路", "地铁", "公交",
        "特许经营权", "准许收益率", "RAB", "监管资产", 
        "输配电价", "配气价格", "污水处理费", "通行费",
        "固废处理", "垃圾发电", "供热", "管网"
    ]
    for keyword in infrastructure_keywords:
        if keyword in search_results:
            scores["infrastructure-driven"] += 0.15

    # ========== 项目制驱动型规则 ==========
    project_keywords = [
        "工程", "建筑", "施工", "房建", "基建", "土木工程",
        "EPC", "总承包", "项目", "工程项目", "施工项目",
        "在手订单", "新签合同", "新签订单", "合同额", "订单金额",
        "造船", "船舶", "军品", "军工", "武器装备",
        "交付周期", "项目收入确认", "完工百分比", "节点确认",
        "工程进度", "竣工验收", "质保金", "工程结算"
    ]
    for keyword in project_keywords:
        if keyword in search_results:
            scores["project-driven"] += 0.12

    # ========== 房地产/REITs驱动型规则 ==========
    realestate_keywords = [
        "房地产", "地产", "物业", "写字楼", "购物中心", "商业地产",
        "物流仓储", "高标仓", "产业园区", "长租公寓",
        "REITs", "不动产", "租金", "出租率", "Cap Rate",
        "资本化率", "NOI", "WALE", "租约", "资产价值",
        "物业管理", "资产运营", "投资性房地产"
    ]
    for keyword in realestate_keywords:
        if keyword in search_results:
            scores["realestate-driven"] += 0.15

    # ========== 产品驱动型（默认加分） ==========
    product_keywords = ["消费品", "手机", "家电", "汽车", "多渠道", "C端", "品牌"]
    for keyword in product_keywords:
        if keyword in search_results:
            scores["product-driven"] += 0.05

    # 确定最高分数的类型
    max_type = max(scores, key=scores.get)
    max_score = scores[max_type]

    # 计算置信度
    confidence = min(max_score, 0.95) if max_score > 0.4 else 0.5

    # 如果置信度<0.6，人工确认
    if confidence < 0.6:
        # 默认产品驱动型（覆盖多数消费品公司）
        max_type = "product-driven"
        confidence = 0.6

    # 细分类型判断
    sub_type = None
    if max_type == "service-driven":
        # 检查是否为产能密集型（CDMO）
        capacity_keywords = ["产能", "万升", "生产设施", "生物药CDMO", "大分子"]
        if len([k for k in capacity_keywords if k in search_results]) >= 2:
            sub_type = "产能密集"
        else:
            sub_type = "人力密集"
    elif max_type == "foundry-driven":
        # 检查代工子类型
        semiconductor_keywords = ["半导体代工", "晶圆代工", "先进制程", "晶圆厂", "纳米"]
        biopharma_keywords = ["生物药CDMO", "万升产能", "大分子", "ADC", "双抗"]

        semiconductor_count = len([k for k in semiconductor_keywords if k in search_results])
        biopharma_count = len([k for k in biopharma_keywords if k in search_results])

        if semiconductor_count >= 2:
            sub_type = "半导体代工"
        elif biopharma_count >= 2:
            sub_type = "生物药CDMO"
        else:
            sub_type = "其他代工"

    return {
        "company_type": max_type,
        "sub_type": sub_type,
        "confidence": confidence,
        "evidence": [f"包含关键词: {k}" for k in scores if scores[k] > 0]
    }
```

## 返回数据格式

```json
{
  "company_name": "中微公司",
  "company_type": "equipment-driven",
  "type_name": "设备驱动型",
  "confidence": 0.85,
  "matching_degree": "高置信度匹配",
  "analysis_module": "modules/company-types/equipment-driven.md",
  "key_evidence": [
    "主营业务: 半导体设备",
    "客户类型: 晶圆厂(B端)",
    "技术特征: 技术突破+客户升级+国产替代"
  ],
  "timestamp": "2026-01-11 15:25:30"
}
```

```json
{
  "company_name": "药明生物",
  "company_type": "service-driven",
  "sub_type": "产能密集",
  "type_name": "服务驱动型(产能密集)",
  "confidence": 0.90,
  "matching_degree": "高置信度匹配",
  "analysis_module": "modules/company-types/service-driven.md",
  "key_evidence": [
    "主营业务: 生物药CDMO",
    "客户类型: 全球药企(B端)",
    "核心资产: 30万升产能",
    "细分类型: 产能密集型（CDMO）"
  ],
  "timestamp": "2026-01-11 23:30:00"
}
```

```json
{
  "company_name": "台积电",
  "company_type": "foundry-driven",
  "sub_type": "半导体代工",
  "type_name": "代工驱动型(半导体代工)",
  "confidence": 0.92,
  "matching_degree": "高置信度匹配",
  "analysis_module": "modules/company-types/foundry-driven.md",
  "key_evidence": [
    "主营业务: 半导体代工",
    "技术特征: 先进制程领先(3nm/2nm)",
    "核心资产: 晶圆厂产能",
    "资本开支: Capex/Revenue>30%",
    "增长逻辑: 产能扩张×技术升级×客户绑定"
  ],
  "timestamp": "2026-01-17 10:00:00"
}
```

## 错误处理

- **搜索结果不足**：返回默认类型"product-driven"，置信度0.5
- **特征冲突严重**（两种类型分数相近）：选择分数最高的，置信度降低0.1
- **未知公司类型**：使用启发式规则，基于行业关键词猜测

## 更新机制

每次分析后将类型判断结果保存到metadata.json，后续分析可直接读取，无需重新判断（除非公司主营业务发生重大变化）。

## 混合类型判定逻辑

对于同时具备多种特征的公司（如阿里既有平台特征又有产品特征），采用以下判定逻辑：

```python
def resolve_hybrid_type(scores, search_results):
    """
    处理混合类型公司判定

    Args:
        scores: 各类型分数字典
        search_results: 搜索结果文本

    Returns:
        resolved_type: 解析后的公司类型
        confidence_adjustment: 置信度调整值
    """
    # 平台+产品混合型（阿里、京东等）
    if scores.get("platform-driven", 0) > 0.5 and scores.get("product-driven", 0) > 0.3:
        # 检查收入结构：平台收入占比 > 50% → 平台驱动型
        platform_income_keywords = ["广告收入", "佣金收入", "平台服务费", "在线营销"]
        product_income_keywords = ["商品销售", "自营收入", "产品销售"]

        platform_count = len([k for k in platform_income_keywords if k in search_results])
        product_count = len([k for k in product_income_keywords if k in search_results])

        if platform_count > product_count:
            return "platform-driven", 0.0  # 无需调整置信度
        else:
            return "product-driven", 0.0

    # 平台+订阅混合型（腾讯等）
    if scores.get("platform-driven", 0) > 0.5 and scores.get("subscription-driven", 0) > 0.3:
        # 检查收入来源：平台收入为主 → 平台驱动型
        return "platform-driven", 0.0

    # 产品+订阅混合型（小米等）
    if scores.get("product-driven", 0) > 0.5 and scores.get("subscription-driven", 0) > 0.3:
        # 小米虽然有互联网服务，但核心是产品销售
        return "product-driven", 0.0

    # 无显著混合特征，返回最高分类型
    return None, 0.0
```

**混合类型判定规则**：

1. **平台+自营混合型**（阿里、京东）
   - 判定标准：平台收入占比 > 50% → 平台驱动型
   - 关键词：广告收入、佣金收入 vs 商品销售、自营收入

2. **平台+订阅混合型**（腾讯）
   - 判定标准：平台生态为主，订阅为辅 → 平台驱动型
   - 典型公司：微信（社交平台）+ 腾讯视频（订阅）

3. **产品+订阅混合型**（小米）
   - 判定标准：产品销售为主，互联网服务为辅 → 产品驱动型
   - 典型公司：小米（手机销售 + 互联网服务）

**实施方式**：
在`detect_company_type`函数中，计算分数后调用`resolve_hybrid_type`，如果返回非None类型，则使用解析后的类型。
