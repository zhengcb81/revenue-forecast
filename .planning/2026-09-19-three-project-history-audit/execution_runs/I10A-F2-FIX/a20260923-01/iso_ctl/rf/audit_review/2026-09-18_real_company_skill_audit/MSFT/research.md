# Microsoft 实盘流程研究记录（2026-09-18）

本目录属于审计工作产物，不修改产品代码。数字在正式引擎输出前只作为已核实的历史事实或待验证研究假设；不冒充已发布预测。

## 研究问题与信息边界

- 公司：Microsoft Corporation，NASDAQ: MSFT；USD million；财年终止日 06-30。
- 信息截止：2026-09-18；最近完整财年 FY2026；拟预测 FY2027–FY2029。
- 生命周期：Azure 为快速扩张；M365 为成熟订阅叠加 AI 商业化；许可为迁移/收缩；Windows 为成熟周期；Xbox 为重组；广告为成熟增长；行业应用为扩张与成熟混合。
- 核心不确定性：可交付 AI 容量与实际消耗、AI 应用净付费渗透及替代、设备/许可的周期与云迁移。

## 实际打开的一手来源与检索过程

1. [FY2026 Q4 earnings release](https://www.microsoft.com/en-us/Investor/earnings/FY-2026-Q4/press-release-webcast)，2026-07-29。通过 web 打开核查全年与季度收入、三旧分部基数。FY2026 331,839，FY2025 281,724。旧分部 FY2026 为 PBP 139,996、IC 137,791、MPC 54,052，闭合总额。
2. [FY2026 Q4 官方电话会](https://www.microsoft.com/en-us/investor/events/fy-2026/earnings-fy-2026-q4)，2026-07-29。已实际打开；原先尝试 earnings/FY-2026-Q4/earnings-call-transcript 返回 404，未将不存在网页作为证据。管理层 FY2027 公司收入双位数增长；RPO 不能直接等同收入；旧指标与新指标需桥接。
3. [9月2日 8-K](https://www.sec.gov/Archives/edgar/data/789019/000119312526380280/d291965d8k.htm)及[Exhibit 99.1](https://www.sec.gov/Archives/edgar/data/789019/000119312526380280/d291965dex991.htm)，2026-09-02。检索年报后公告发现重大重分类，再打开 SEC 一手资料确认；废弃按三旧分部建模的初始路线。该项同时覆盖最新 investor presentation、strategy communication、material announcements 类别，但仍需独立保存 capture。
4. [FY2026 10-K](https://www.sec.gov/Archives/edgar/data/789019/000119312526323660/msft-20260630.htm)，已尝试 web 打开，返回内容超过 4 MB；并未声称已读该次失败响应的全文。等待 filing-fetch/source_preparation 正式来源链。Microsoft ar26/index.html 也未能打开。
5. [Amazon Q2 2026 release](https://ir.aboutamazon.com/news-release/news-release-details/2026/Amazon-com-Announces-Second-Quarter-Results/default.aspx?mode=light)，2026-07-30，已打开。AWS 季度同比 37%提供同业云需求的方向性交叉检验，但不同会计期间、业务范围与客户结构不能直接变成 Microsoft 三年增长参数。

## 9月重分类为何实质改变模型

Exhibit slide 17 的八条新口径业务曲线（USD million）：

| 曲线 | FY2025 | FY2026 | 建模路线 |
|---|---:|---:|---|
| Azure | 72,610 | 101,938 | usage 模型理想但缺可核实计费用量与净价；透明 direct_growth |
| Microsoft 365 cloud | 84,605 | 100,299 | subscription/ARR 理想但缺同口径平均付费席位、净ARPU、ARR桥；透明 direct_growth |
| Productivity and server licensing | 35,391 | 37,285 | 成熟许可迁移，避免重复加算迁入云收入 |
| Search and advertising | 22,171 | 24,835 | 展示与CPM未完整披露；ex-TAC KPI不能套入GAAP总额收入 |
| XBOX | 23,455 | 21,790 | 重组/内容周期，订阅、内容与硬件合计，不能假定统一用户ARPU |
| Industry solutions | 18,417 | 20,345 | 产品与订阅、LinkedIn重划部分混合；缺同口径单位数据 |
| Windows OEM and devices | 17,315 | 17,087 | OEM出货与自营硬件混合；生命周期成熟且FY27周期承压 |
| Frontier and support services | 7,760 | 8,260 | 缺计费工时/费率；不编造人员利用率 |

八线均保留新口径对比，不能把旧Azure and other cloud增长、旧LinkedIn整额及新口径数字混用。新两报告分部 Agents and Infra 为268,127，Devices and Consumer为63,712，合计331,839。模板 PBP/IC/MPC 仅保留为真实过程证据，不是最终输入。

## 买方建模与反证计划

- Azure：以最新增长、供应限制与同行云需求作方向证据；FY2027之后设置减速和容量兑现两条机制。按季度容量上线、实际消耗、OpenAI与其他客户RPO差异追踪。RPO包含多年合同与履约时间，不用 RPO/固定年数硬推收入。
- M365：席位增长、升级与Copilot净付费留存共同影响；期末席位不等于平均席位，公开标价不等于折扣后收入，AI usage billing可能使每席位解释力降低。不能用产品发布数直接加增长率。
- Licensing/Windows：分别验证云替代、产品发布/合同确认时点、Windows 10支持结束后的高基数、库存与部件价格；这些是负向路径，不因集团AI叙事抹掉。
- 广告：将广告需求/查询份额与价格、TAC变化分开，不能把 ex-TAC 增长照搬GAAP收入。
- Xbox：基于现有下滑、公司重组与新品节奏设条件恢复，不能直接把“return to growth”视为已实现。
- 独立基准：FY2026不变、两期新口径历史增速延续只是基准；两年不足以校准长期趋势或证明精度。记录缺少冻结预测滚动回测，禁止事后声称准确率提升。

## 已观察的流程与产品问题（待独立审查）

1. `generate_input_template.py --output <不存在目录>/input.template.json`首次执行报FileNotFoundError，创建父目录后成功。可用性问题，不是模型失真；未改代码。
2. 生成模板默认 as_of=2027-06-30、fiscal_year_end=12-31，并生成假来源/零哈希占位。必须修为真实截止与06-30；生成模板本身不是证据采集。
3. `references/input-construction.md`标题与示例仍写schema3.6、9-key capture，而实际模板schema3.7含host_receipt。文档与执行契约混杂增加真实输入构造成本。
4. 若只读最新年报或旧分部示例，会遗漏截至日已发布的重大重分类。六类管理沟通门槛有实际价值，但完全依赖代理真正检索，字段齐全不能证明最新。
5. 不能以更多模型注册数证明此公司已有足够经营数据。这里最诚实的八曲线 fallback 仍缺单位经济校准，其买方决策价值需要独立审计严格打分。

## 真实命令记录

- 读取安装 `.agents/skills/revenue-forecast/SKILL.md`遭路径权限拒绝；改读工作区当前 SKILL.md，不宣称安装副本已核对。
- 阅读工作区 data-governance、compliance-contract、research-coverage、buy-side-methodology、industry-lifecycle-routing、model-library、input-schema、input-construction、growth-driver-tree、management-targets、output-schema 与 trust-boundary 模板。
- 运行 `python scripts/generate_input_template.py --name 'Microsoft Corporation' --base-year 2026 --forecast-years 2027 2028 2029 --segments PBP IC MPC --segment-model PBP=direct_growth --segment-model IC=direct_growth --segment-model MPC=direct_growth --currency USD --unit million --output audit_review/2026-09-18_real_company_skill_audit/MSFT/input.template.json`。首次缺父目录失败；建立本目录后成功。

所有原始 web 调用在当前任务工具轨迹中；本文是过程索引，不伪装宿主签名/capture receipt。源抓取、公司身份、catalog mutation由root串行运行，待真实record后构建完整输入。
