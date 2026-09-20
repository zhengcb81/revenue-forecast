# MSFT 研究门槛与目标台账草案

状态：研究核对表；尚非引擎接受的正式 management_targets 或 research_coverage。不以填完表格宣称通过硬门。源正文已通过 web 读取的项目仍待 source_preparation capture 绑定。

## 九维度

| 维度 | 观察及拟传导 | 当前缺口 |
|---|---|---|
| company_foundation | FY2026总额与9月重述八产品线闭合；新两分部可重组 | 10-K正式链路未完成，收入确认政策未完成claim绑定 |
| growth_curve | 云消耗、订阅变现、许可迁移、设备收缩分别建曲线 | 72个候选增长率仍需单位经济校准 |
| industry_market | AWS当前强增长支持云需求方向，2023低增长显示优化周期 | 无可比市场规模/份额和失败样本完整组，不将同业增速硬套Azure |
| competition | 云和AI应用竞争经份额、价格、净留存影响收入 | 缺Microsoft客户流失、竞争折扣和多云工作负载分流数据 |
| capacity | 实际上线容量和客户消耗限制Azure确认 | 不用capex或数据中心数量替代可计费GPU时长；缺容量定量上限 |
| technology | AI效率与产品采用影响价格/消耗/升级 | 效率提升可能降单价也可能增使用，缺弹性估计，不能单向加增长 |
| policy | 安全、数据主权、竞争及出口规则可改变部署/捆绑/合同 | 尚未完成政策来源逐条量化，保持重大数据缺口 |
| customers | Copilot净付费、M365席位、RPO客户集中影响收入质量 | 缺同口径平均席位、续约率、OpenAI实际消费与合同取消风险量化 |
| demand | 企业预算、广告主需求、PC库存、游戏内容共同作用 | 公司自述占主导；需独立客户采购/预算证据 |

## 六类管理沟通

| 类别 | 已执行情况 | 正式化状态 |
|---|---|---|
| latest_annual_filing | FY2026 SEC10-K直开失败（超大小）；root已查reuse=not_found并准备授权download | 阻断；不能拿FY2025标为latest |
| latest_results_release | 7月29日FY2026Q4官方release实际打开 | 等待正式capture |
| latest_earnings_call | 7月29日官方event transcript实际打开 | 等待正式capture；需完整target claims |
| latest_investor_presentation | 9月2日SEC Exhibit99.1实际打开，官方IR链接印证 | 等待8-K/exhibit采集路由 |
| latest_strategy_communication | 同presentation中CEO关于新结构与AI策略实际打开 | 同源不等于独立三角验证 |
| material_announcements_since_last_filing | 搜索发现9月2日重述；IR首页9月15日股息公告不改变本收入边界 | 不声称网页检索穷尽；需源与检索记录绑定 |

## 目标/指引台账（研究表达，不伪造精确目标）

来源：7月29日[官方电话会](https://www.microsoft.com/en-us/investor/events/fy-2026/earnings-fy-2026-q4)；9月2日[Exhibit99.1 slides20–21](https://www.sec.gov/Archives/edgar/data/789019/000119312526380280/d291965dex991.htm)。

| 对象/期间 | 原意的简短释义 | 对模型处理 |
|---|---|---|
| 公司FY2027 | 全年收入双位数增长 | 可作独立benchmark；“双位数”只支持下界解释，不能捏成管理层精确20%或全年额 |
| Xbox FY2027 | 期望全年恢复增长 | Base略增，Low允许失败；不强迫所有情景达标 |
| Windows OEM/devices FY2027 | 全年high-teens降幅 | Base取-18%为分析师解释，Low/High保留不同条件；不是公司精确-18% |
| 旧M365 commercial products、server products FY2027 | 全年mid-single下降 | 不能直接与新Licensing全部边界等同；定性约束负增长并保留口径差异 |
| 公司FY2027 Q1 | 89.85–90.95bn | 季度指引，不能乘4当全年；年频引擎没有自然季度target period，需显式缺口 |
| Agents and Infra FY2027 Q1 | 75.15–75.75bn | 新口径季度，不能对比八线全年之和 |
| Devices and Consumer FY2027 Q1 | 14.7–15.2bn | 同上 |
| Azure FY2027 Q1 | CC增长44–45%，汇率小幅负影响 | 不是FY2027全年美元增长；可做第一季度校验和全年路径起点 |
| M365 commercial cloud FY2027 Q1 | CC约17%；调整确认基数约18% | 不能等同合计M365cloud的GAAP全年增速 |
| Productivity and server licensing FY2027 Q1 | low-single下降 | 与旧分部指引不能混用；保留产品/确认时点差异 |
| Industry solutions cloud FY2027 Q1 | high-single增长 | cloud不是含products的整条Industry solutions |
| Search and advertising FY2027 Q1 | ex-TAC mid-to-high-single增长 | GAAP总额与ex-TAC净KPI需TAC桥，不能当同口径精确值 |
| XBOX FY2027 Q1 | 内容服务mid-single下降、硬件下降 | 全年恢复需后续季度改善，不能忽略当期负面信号 |
| Windows OEM/devices FY2027 Q1 | low-twenties下降 | 季度去库存压力、全年恢复形状仍需证据 |

上述自然语言范围翻译为数值时应保留原文、翻译理由和不确定性，不能把分析师选择的区间中点做 exact_value 管理层claim。

## 负向参考样本

已真实打开Amazon [Q2 2023 release](https://ir.aboutamazon.com/files/doc_financials/2023/q2/Q2-2023-Amazon-Earnings-Release.pdf)：AWS当期仅增长12%，管理层描述从客户成本优化转向新工作负载。该样本说明长期云逻辑可与阶段性强烈减速并存，支持Azure压力研究；不主张不同年份、规模和AI阶段的增速可无调整直接复用。已打开微软FY2023Q4一手release，尚未完成其旧口径与当前口径数值映射，因此不冒充同口径长历史。

## 正式验证能否合法进行

在真实来源记录、完整输入和claims构造后，合法运行`--validate-only --verbose`并保留失败就是有效审计。当前未拿到capture-ready源/确认政策，直接把带FIXME的空模板送验证只证明模板未填，不证明真实技能完成。故暂不为制造“已跑”记录而执行空模板。不得将`not_reviewed`手改为`not_detected`、自行虚构宿主工具调用凭据、把9月19日访问日期回填9月18日，或以手写预测结果顶替发布门槛。
