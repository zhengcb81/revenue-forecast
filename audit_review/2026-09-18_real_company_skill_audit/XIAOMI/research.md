# 小米集团：真实收入预测运行研究底稿

信息截止：2026-09-18。执行跨越 2026-09-18/19；继续沿用 9 月 18 日信息集。研究员：独立 forecast_hk agent。

**状态：研究及正式运行准备；本文件不是引擎验证后的 forecast.md，也不是投资建议。** 不以 schema 通过替代经济审核。source_preparation、filing-fetch 和跨目录 company-wiki 的写入由根代理串行执行，本文不声称已经完成这些步骤。

## 1. 真实来源访问记录

| 标识 | 一手资料/网址 | 发布或可用日期 | 本次访问与用途 |
|---|---|---|---|
| AR25 | [HKEX 2025 年报](https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0428/2026042800526.pdf) | 2026-04-28 16:30 HKT；已核对交易所目录 | web.open 成功，415 页；历史、分部基数及会计政策 |
| H126 | [2026 H1/Q2 业绩公告](https://ir.mi.com/static-files/4a85fc36-8a6d-4c24-b45b-b18d5d162e6c) | 文末 2026-08-18，交易所 17:25 HKT | web.click/open 成功，46 页；当年已实现收入、量价、补贴退出、新品 |
| P26 | [2026 Q2 业绩简报](https://ir.mi.com/static-files/bdeea0b9-246c-45be-8cb4-ab4faaddf80a) | 2026-08-18 业绩会议 | web.click/open 成功，37 页；交叉核验季度及业务战略 |
| P25 | [2025 年度业绩简报](https://ir.mi.com/system/files-encrypted/nasdaq_kms/assets/2026/03/24/6-20-53/Xiaomi%20Corp_25Q4_ER_ENG%20vF.pdf) | 2026-03-24 业绩会议 | web.click 成功，38 页；历史销量、MAU、渠道与研发计划 |
| IR | [官方季度业绩目录](https://ir.mi.com/financial-information/quarterly-results) | 动态目录；访问 2026-09-18/19 | 找到 Q1、Q2 2026、FY2025 正式公告及 webcast |
| HKEX | [1810 交易所公告目录](https://www1.hkexnews.hk/search/titlesearch.xhtml?category=0&market=SEHK&stockId=190371) | 动态目录，最新显示 2026-09-16 | 找到完整年报，核对年报/业绩发布时间；初步筛查年报后事项 |
| CALL26 | [官方业绩 webcast](https://edge.media-server.com/mmc/p/g4mz2qh6) | 2026-08-18 | web.open 得到空正文；不能视为已听完 Q&A，目标完整性仍待核验 |

访问失败也保留：ir.mi.com 年报原链接 `https://ir.mi.com/system/files-encrypted/nasdaq_kms/assets/2026/04/28/5-29-08/Xiaomi%202025%20AR_EN.pdf` 返回 403；FY2025 结果公告 static-files/a29b9ab3-8488-4032-9674-9075e9cb01ab 在 web 与 Tavily 均失败（Tavily request_id 89286ce5-1fc1-4326-95c9-39a933d9fca9）。之后通过 HKEX 目录找到年报，并成功阅读；因此不能把 IR URL 访问失败写成“没有年报”。

MiniMax 搜索结果及第三方电话会转写只用作线索。独立 Omdia/BusinessWire 2026-07-30 手机市场材料找到链接，但打开失败；没有登记成已核验独立证据。搜索命中内容显示部分二手转写将全球 MAU 写作 770 million，官方 H126 为 766.5 million：采用官方口径，不拼接二手数字。

所有本次 web 访问都是事实上的工具执行，但目前它们不是 source_preparation 返回的 capture-ready source；不得凭 URL 和工具名自行伪造其 host receipt。

## 2. 已核验基数与量纲

金额统一计划为 CNY million，财年 12 月 31 日。年度对照为 AR25 印刷页 6（PDF 第 8 页），分部为印刷页 335（PDF 第 337 页）。原始报表是 RMB 千元，以下明确除以 1,000；经营销量/ASP另有舍入精度。

| FY | 总收入，CNY million |
|---|---:|
| 2021 | 328309.145 |
| 2022 | 280044.016 |
| 2023 | 270970.141 |
| 2024 | 365906.350 |
| 2025 | 457286.687 |

| 已披露曲线 | FY2024 | FY2025 | H1 2025 | H1 2026 |
|---|---:|---:|---:|---:|
| 手机 | 191759.315 | 186439.777 | 96131.961 | 86392.014 |
| IoT/生活消费 | 104103.874 | 123200.191 | 71051.387 | 55959.160 |
| 互联网服务 | 34115.373 | 37440.346 | 18173.844 | 18512.009 |
| 手机×AIoT 其他 | 3174.148 | 4136.860 | 2048.907 | 2439.791 |
| EV、AI及创新 | 32753.640 | 106069.513 | 39843.329 | 44760.253 |
| 合计 | 365906.350 | 457286.687 | 227249.428 | 208063.227 |

H1 数据来自 H126 印刷页 36（PDF 第 36 页）的财务附注而非四舍五入管理讨论表。上表每年/半年均应逐项求和核对；不额外添加内部抵销（H126 附注指无重大分部间销售）。

AR25 印刷页 7/19/20：FY2025 手机出货 165.2 million；EV 交付 411082 台，ASP 251171 CNY/台；EV 收入仅在管理讨论披露为 103.3 billion，EV 其他为 2.8 billion。**不能把这两个舍入数伪装为精确分部审计数。** 可保留 EV 综合曲线的精确基数，未来用交付×净 ASP + 单独解释的 other_revenue；或者用舍入细分加显式基年舍入桥。六曲线模板是候选，最终选择尚未冻结。

H126 印刷页 4/10/11：Q2 手机出货 31.2 million（同比 -26.5%），ASP 1351（+25.9%）；Q1 33.8 million，故 H1 65.0 million 是相加的舍入近似值。Q2 EV 104199 台、ASP 229312（同比 -9.6%），H1 185055 台。手机与 EV 的“量升价升”假设方向不同，不能共同套用 FY2025 增速。

精简原文定位摘录：AR25 p298，`"when the products are accepted by the customers"`；H126 p10，`"the reduction in national subsidies"`。其余取数通过上述表格及明确页码查验，避免大量复制文稿。

## 3. 收入确认与模型选择

AR25 印刷页 297–300：产品按客户接受、控制权转移确认，扣折扣、退货和增值税；经销商采购和终端动销不同。展示广告按合同展示期间摊销，效果广告按实际点击/展示/下载完成；游戏按用户关系期，并依据主体/代理决定总净额；金融科技利息按资产和实际利率确认。

| 曲线与阶段 | 最小模型与真正驱动 | 当前不应采用的假细化 |
|---|---|---|
| 手机：成熟替换市场，成本/组合周期 | `unit_sales`，客户接受销量×净 ASP；分地区/档位仅在同口径量价可得时扩展 | 不用新增 IoT 连接设备数直接推手机销量；不将 ASP 组合变化重复加价 |
| IoT：成熟品类+新地区扩张，国内补贴回落 | 暂用 `direct_growth`，H1 实际+H2假设先形成全年，再有证据地细拆品类 | 无各品类收入权重时，不把空调增速加到 IoT 总增速；门店数不是直营销售额 |
| 互联网：成熟用户平台，广告成长+游戏收缩 | 暂用 `direct_growth` 或会计口径 `direct_revenue`；单列广告与非广告应有全期历史 | 不把期末 MAU 当平均付费用户；`subscription` 不是广告默认模型；混合确认政策不能整条标记为同一 point-in-time/gross |
| 手机其他：安装/材料业务 | 披露基础上的简单回退，跟随真实安装量/材料销售 | 不把所有收入强绑手机销量，安装服务主要受家电影响 |
| EV：新品商业化及扩张 | `unit_sales`，交付×净 ASP；年度新车/旧车型与投产、交付瓶颈在假设里显式核对 | 未核对订单、取消、期末订单前不使用 `delivery_pipeline`；产能公告不是交付 |
| EV服务/AI：装机售后与早期商业化混合 | 披露充足再拆 `installed_base_aftermarket` 与 AI usage；当前在 EV 的 other_revenue 中清楚披露回退 | AI Token 用量/榜单≠付费收入；研发投入≠收入目标；售后不能再算一次新车收入 |

H126 2026Q2 AI/EV其他约 1.0 billion；不能把该金额全部当 AI 付费收入，更不能据此给 AI 高 CAGR。境内补贴退出同时作用于需求、ASP、品类组合，需避免多处重复扣减。

## 4. 九维研究覆盖与尚未满足的买方研究

| 维度 | 现有结论及参数传导 | 证据边界/下一步 |
|---|---|---|
| 公司基础 | 精确公司/五曲线年度与半年收入可闭合 | 六曲线EV拆分需舍入处理；互联网混合确认尚未解决 |
| 增长曲线 | 量价分离，2026 H1 已实现收入必须锁住 | 年度引擎需要外部 H1/H2 桥；不能让全年模型自由覆盖已发生数据 |
| 行业市场 | 官方转述手机/乘用车市场下行 | 独立原始行业资料仍未打开，不能称多源三角验证 |
| 竞争 | 手机高端化伴随中低端量缩；EV Ultra组合回落 | 需要竞品同价位成交/净价与交期；评测与品牌话术不支持销量大小 |
| 产能 | EV交付轨迹可核验，新品供给需单独核对 | 缺可用产能/爬坡/订单取消；不得为通过模型捏造订单桥 |
| 技术 | 新架构/模型/新品可能影响采用与组合 | 性能或榜单不直接变成份额、ARPU；需有付费/订单证据 |
| 政策 | 国内补贴减弱已体现在IoT下行 | 下一年补贴强度未知，条件场景表达；不能假设永久反弹 |
| 客户 | 手机/TV MAU扩张，广告与游戏方向不一 | 期内平均/跨设备重复/地区变现/用户关系期资料缺口 |
| 需求 | H1量价与海外增长可观察 | 当年H2新品、渠道库存和补贴透支需检验；上市新品不自动创造全年需求 |

独立参考类还未完成：手机需至少覆盖库存周期；EV需包含交付延期/失败车型，不能只看成功新势力爬坡；没有真实冻结滚动起点，不主张预测准确性改善。

## 5. 管理沟通及目标覆盖

年报、最新结果与简报已实际打开；官方 webcast 页打开但没有可读音频转写，因此 earnings-call 不能标 `checked`。最新战略应结合已读新品/AI段落及额外公告，不能把季度简报自动冒充完整战略搜索。交易所目录已查看年报后事项，需逐项判断与收入是否相关，不能仅目录访问就宣称所有 material announcements 完成。

年度简报包含 2026–2030 研发及未来三年 AI 投资安排；它们属于支出安排，不是收入目标，不应塞进 management revenue target ledger。搜索线索中的 EV 年度交付目标必须回到官方原话；在尚未拿到原话和时间范围前，不把它填为 `management_guidance`。本次候选 high 中的 550000 台只是研究压力假设，不能标成已核验目标。

## 6. 方法/可用性发现（暂不改代码）

1. **真实数据会推翻漂亮的增长叙事。** FY2025公司增长25%，但FY2026H1下降8.4%；手机/IoT与新EV增长方向分化。全公司 CAGR 或统一增长倍数会对投资者造成实质误导。应强制审阅当年已实现+剩余期间桥及隐含H2增长。
2. **会计混合曲线不能由唯一时点枚举准确表达。** 互联网披露同时包含展示广告、效果广告、游戏、金融利息；简化为 single timing/presentation 会形式合规但经济失真。需要拆分证据或明确在已确认收入上做桥，不能假造全gross/全point-in-time政策。
3. **舍入引发虚假精确。** EV revenue 与其他收入以0.1bn披露，交付/ASP精度不同；精确乘法不必恰好等于审计分部。不能把差额未经解释称为其他业务增长。
4. **文档契约漂移。** `references/input-construction.md` 标题与组装示例仍3.6，称capture严格9键、任何额外键拒绝；当前SKILL/input-schema是3.7，真实模板生成 `host_receipt`。使用者按旧文档删除此键会出错。此项已实读，尚未修改。
5. **工具访问与正式来源不同。** web读到年报不等于filing-fetch正确存储/索引，也不等于已获得capture合同。本底稿必须与根代理真实source_preparation日志交叉审查。
6. **复杂模型可能比透明回退更差。** MAU无平均/地区变现、EV无取消/订单库、IoT无收入权重时，复杂公式只能增加未经验证自由参数；不应为显式模型评分强套。

## 7. 已执行的本地操作

- 读取工作区 `SKILL.md` 及 governance/compliance/research/buy-side/lifecycle/model/extended/input/output/management/growth/accounting/backtesting 文档；.agents镜像 SKILL 的直接读取出现 Access denied，工作区版可用。
- `python --version` → Python 3.13.9。
- `python scripts/generate_input_template.py --help` → exit 0。
- `python scripts/generate_input_template.py --name 'Xiaomi Corporation 1810.HK' --base-year 2025 --forecast-years 2026 2027 2028 --currency CNY --unit million --segments Smartphones IoT Internet SmartphoneOther EV EVAIother --segment-model Smartphones=unit_sales --segment-model IoT=direct_growth --segment-model Internet=direct_growth --segment-model SmartphoneOther=direct_growth --segment-model EV=unit_sales --segment-model EVAIother=direct_growth --output audit_review/2026-09-18_real_company_skill_audit/XIAOMI/input_template_unfilled.json` → exit 0。
- 模板默认 as_of_date=2026-06-30、source/claim占位值；**未当作真实输入运行，也未将FIXME哈希伪装为来源。** 等待根代理真实capture后才组装正式输入并记录真实验证。

所有写入限于本审计目录。产品代码、配置、已发布artifact未修改。
