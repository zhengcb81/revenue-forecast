# 扩展收入模型：经济恒等式、确认时点与适用边界

本次新增八类可执行模型，补足原有单期乘法模型不能验证的存量连续性、投产时点、存量服务、市场耗尽和供需约束。实现位于 `scripts/model_extensions.py`，通过 `model_registry.py` 统一注册；不存在第二套预测引擎。模型复杂度增加本身不证明预测更准，只有冻结信息集的样本外回测能检验准确性。

所有下列公式均按一个完整财政年度计算；金额必须事先转为公司统一币种与 scale，单位数量与每单位收入必须互相匹配。库只识别抽象 dimension，不自动把 MW、kW、MWh、kWh 或千台、台进行换算。若年度平均值不可靠，应先用有证据的月度/季度 cohort 计算时间暴露量，作为年度参数；不能以增加小数位替代数据。

## 共同执行门槛

- 必填 driver 的每年值、情景、量纲、证据按既有合同登记；下表所列可选金额默认 0，其余时点比例均为必填，无隐藏的 0.5 假设。
- 比例原则上在 `[0,1]`，新店相对成熟店生产率可超过 1；AUM 市场变动、电价、发电其他收入和已确认绩效费可为负，后两项用于有凭据的冲回。计算后的收入仍须有限且非负。负收入业务尚不在当前聚合合同内。
- 所有存量桥都检查年度平衡和 `opening[t] = closing[t-1]`。这些检查只能证明输入自洽，不能证明披露或估计真实。
- 六个存量模型还需要对应的基年锚点参数 ID，见末表；各情景第一年 opening 必须与同一个已核验基年余额一致。
- 若一个流量驱动改变会影响 closing 和后续 opening，敏感性分析必须联动重算整条桥；不可让余额断裂后继续出具“弹性”。不要把 closing 当作独立的经济杠杆。
- 每个公式已经包含所列服务暴露/商业化时点；不得在收入确认层再乘同一时点比例。仍需按合同政策登记 point-in-time/over-time 与 gross/net，必要时使用独立、未重复的会计确认桥。

## 1. `subscription_arr_bridge`：订阅 ARR 到年度收入

适用于有可靠 ARR 桥的 SaaS、数据订阅、软件维护。区别于客户数量桥：它直接区分存量流失/收缩、存量客户扩张、新客户 ARR，并处理各自发生时点。

必填 `opening_arr`, `gross_retention_rate`, `expansion_arr`, `new_arr`, `closing_arr`, `lost_arr_revenue_fraction`, `expansion_revenue_fraction`, `new_arr_revenue_fraction`；可选 `usage_revenue`。ARR 的 dimension 使用 `revenue`，但参数定义必须写明“年化 run-rate”，不可写成已确认年度收入。

```text
lost_arr = opening_arr × (1 − gross_retention_rate)
closing_arr = opening_arr − lost_arr + expansion_arr + new_arr
revenue = opening_arr − lost_arr × lost_arr_revenue_fraction
          + expansion_arr × expansion_revenue_fraction
          + new_arr × new_arr_revenue_fraction + usage_revenue
```

`lost_arr_revenue_fraction=1` 表示期初立即流失、损失全年收入；0 表示期末才流失。新增/扩张的 fraction 则是当年实际贡献收入的年分数，期末签约并开始服务为 0，期初开始服务为 1。因此相同 closing ARR 可对应不同年度收入。没有留存的期初 ARR 时不得出现存量扩张。

GRR 不包含扩张；不能输入 NRR 后再加扩张，运行时也不接受额外 NRR driver。假设期初存量符合可持续履约的年化收入，新增 ARR 为同年未流失的新增 cohort。年内新增又流失、多年阶梯价格、复杂多履约义务分摊、usage-based ARR、FX/M&A ARR 变动必须另建 cohort/转换证据，不能塞入 expansion。`usage_revenue` 仅限 ARR 未包含的部分。

一手参照：Similarweb 在 [2026 年二季度披露的 Other Metrics](https://www.sec.gov/Archives/edgar/data/1842731/000184273126000042/a6-kxexhibit991xq230062026.htm) 区分了 ARR、NRR 与履约确认的 GAAP 收入。上述 bridge 是据此提出的建模约束，并非该公司公布的收入计算方法。

## 2. `installed_base_aftermarket`：装机基数与耗材/维保

适用于医疗设备、实验室仪器、工业设备的耗材和服务。必填 `opening_installed_units`, `new_installed_units`, `retired_units`, `closing_installed_units`, `new_unit_revenue_fraction`, `retirement_lost_fraction`, `attach_rate`, `annual_revenue_per_attached_unit`。

```text
closing_installed_units = opening_installed_units + new_installed_units − retired_units
active_unit_years = opening_installed_units
                   + new_installed_units × new_unit_revenue_fraction
                   − retired_units × retirement_lost_fraction
revenue = active_unit_years × attach_rate × annual_revenue_per_attached_unit
```

退役仅对应期初 cohort，不得超过期初装机量；新增设备同年退役需更细 cohort。attach 指实际付费耗材/服务覆盖，不能重复包含在“每台已附着设备收入”中。硬件销售独立建模，跨分部内部供货须消除。设备使用强度、耗材单价、第三方耗材替代、保修转付费可进一步分解年化单机收入，不能把设备新装增速直接作为耗材收入增速。

一手参照：[Bio-Rad 2025 年报 Clinical Diagnostics](https://www.sec.gov/Archives/edgar/data/12208/000001220826000010/bio-20251231.htm) 描述了装机平台带来的试剂和耗材复购。这说明需要存量驱动，但不意味着所有设备都具有相同 pull-through。

## 3. `store_cohorts`：直营门店开关店与爬坡

必填 `opening_stores`, `new_stores`, `closed_stores`, `closing_stores`, `new_store_revenue_fraction`, `closure_lost_fraction`, `new_store_productivity`, `annual_revenue_per_mature_store`。

```text
closing_stores = opening_stores + new_stores − closed_stores
mature_store_years = opening_stores − closed_stores × closure_lost_fraction
new_equivalent_store_years = new_stores × new_store_revenue_fraction × new_store_productivity
revenue = (mature_store_years + new_equivalent_store_years) × annual_revenue_per_mature_store
```

`new_store_productivity` 是营业期间相对成熟店的单位时间生产率，不再含营业月数；旗舰店可超过 1。期初门店在本模型内视为成熟，若爬坡超过一年，应拆分年龄 cohort。关店仅来自期初门店。成熟店收入已含同店量价和本地竞争影响，不再额外叠加同店增长乘数。店型/区域差异大时拆分。特许经营仍用原 `retail_franchise`，不能把加盟系统销售额作为直营收入。

## 4. `renewable_generation`：投运发电量与电价结构

必填 `average_commissioned_mw`, `period_hours`, `pre_curtailment_capacity_factor`, `curtailment_rate`, `contracted_share`, `contract_price_per_mwh`, `merchant_price_per_mwh`；可选 `other_revenue`。

```text
delivered_mwh = average_commissioned_mw × period_hours
                × pre_curtailment_capacity_factor × (1 − curtailment_rate)
energy_price = contracted_share × contract_price_per_mwh
               + (1 − contracted_share) × merchant_price_per_mwh
revenue = delivered_mwh × energy_price + other_revenue
```

MW 是按投运日期加权的年均已投运容量，不是期末容量或公告项目。小时数按财政年度显式提供，不硬编码 8760。capacity factor 需重构为限电前口径，且包括一次设备可用性、资源条件和衰减效应；若数据只有实际净容量因子，就设额外 curtailment 为 0 并披露限制，不能重复扣限电/可用率。合同与市场份额划分同一份已交付电量；电价是随发电时段加权的捕获价格，不是简单市场均价。负电价允许，但收入不得为负。

一手参照：[EIA capacity factor 定义](https://www.eia.gov/tools/glossary/index.php?id=Capacity_factor) 给出实际发电量与连续满功率可能发电量的比值。这里另设“限电前”驱动是为了单独检验限电影响，不能将 EIA 的实际净值直接再打折。模型不支持逐时调度、储能套利、金融衍生品净结算、复杂最低购买量或证书确认；这些必须单独建模。

## 5. `aum_fee_bridge`：资管规模流量到管理费

必填 `opening_aum`, `inflows`, `outflows`, `market_change`, `closing_aum`, `inflow_revenue_fraction`, `outflow_lost_fraction`, `market_change_revenue_fraction`, `management_fee_rate`；可选 `recognized_performance_fees`。

```text
closing_aum = opening_aum + inflows − outflows + market_change
fee_average_aum = opening_aum + inflows × inflow_revenue_fraction
                  − outflows × outflow_lost_fraction
                  + market_change × market_change_revenue_fraction
revenue = fee_average_aum × management_fee_rate + recognized_performance_fees
```

规模和流量为 `monetary_balance`，市场变动可正可负；市场变动金额已包含流量发生之后的实际市场暴露，不能再乘期初规模收益率。时间权重用于近似年内费基，平均费基必须非负。若实际收费按日均/月均、承诺资本、成本、阶梯费率或份额级别计费，优先按合同重构费基并使用原 `asset_management`；不要把简单期末均值冒充精确日均。复杂多资产组合应分桶，净流量和市场上涨可能有相反的费率结构影响。

绩效费只接受已经单独按 high-water mark、hurdle、结算/转回条款与收入政策推导的收入金额，可为有凭据的负冲回，本模型不从正收益率自动生成绩效费，也不将本金/AUM计入收入。并购/汇率不在此简化存量桥内，须预先独立分解和说明。

一手参照：[BlackRock 2025 Form 10-K](https://www.sec.gov/Archives/edgar/data/2012383/000130817926000264/blk015204-arsa.pdf) 分开披露基础费与绩效费，并解释市场和流量对平均 AUM 的影响。这里的年度暴露桥是分析近似，不替代其具体计费合同或披露口径。

## 6. `commercial_launch`：前收入到商业化的条件情景

必填 `eligible_units`, `adoption_rate`, `annual_supply_capacity`, `commercial_year_fraction`, `net_revenue_per_unit`。

```text
annualized_deliverable_units = min(eligible_units × adoption_rate, annual_supply_capacity)
conditional_revenue = annualized_deliverable_units × commercial_year_fraction × net_revenue_per_unit
```

适用于可明确需求单位和供给上限的新品/药品商业化。eligible 是该年度可服务人群/单位，不是整个流行病学存量；adoption 为商业化期间的年化采用水平。供给能力也须同口径年化，商业化份额统一作用于需求和供给。年内爬坡复杂时应把实现的年化等效量作为有来源的年度参数，不能重复乘上市月数。

未批准、失败或推迟至期末的条件情景设商业化时间为 0。代码不接受 `success_probability`，low/base/high 表示对应事件条件下的完整收入路径；只有在外层明确构建互斥、完备且有校准依据的情景后才计算 `Σ p_s × revenue_s`。已经以概率加权的销量/收入不能再用同一成功事件的概率打折。阶段转换概率、临床相关性、多个适应症重叠、里程碑确认均未由此模型自动解决。

一手参照：[FDA Drug Review](https://www.fda.gov/patients/drug-development-process/step-4-fda-drug-review) 区分提交申请、审评与能否批准上市。本模型将商业化条件和时间显式化，不预测监管决定；不能使用药物管线“储量消耗”恒等式替代批准后的真实患者需求。

## 7. `finite_adoption`：有限未渗透市场与成熟期饱和

必填 `opening_unserved_market`, `new_eligible_units`, `removed_eligible_units`, `adopted_units`, `closing_unserved_market`, `net_revenue_per_unit`。

```text
closing_unserved_market = opening_unserved_market + new_eligible_units
                         − removed_eligible_units − adopted_units
revenue = adopted_units × net_revenue_per_unit
```

用于一次性首次采用、换代批次或有限可交付项目池，adopted 必须是已经具备收入确认条件的交付采用量。不能将预订采用量或采购意向直接放入。非负期末池与桥平衡共同限制销量不超过可用市场。新增人口/需求只能进入一次，竞争对手夺走和资格失效进入 removed。若客户会复购，另设重复购买/售后曲线，不能重新加入首次采用池。采用速度仍来自有证据的产品优势、渠道触达与预算，不默认套 logistic/Bass 曲线；仅有 TAM 并不足以构建此模型。

## 8. `inventory_sellthrough`：可售成品库存与收入

必填 `opening_inventory`, `saleable_production`, `purchased_units`, `scrapped_units`, `sold_units`, `closing_inventory`, `net_revenue_per_unit`。

```text
closing_inventory = opening_inventory + saleable_production + purchased_units
                    − scrapped_units − sold_units
revenue = sold_units × net_revenue_per_unit
```

用于库存影响交付的制造/消费/分销业务。库存是统一 SKU 等效单位的可售成品，不能混入原材料/WIP的成本金额。production 已经包含良率损耗，不能重复打良率折扣；scrapped 为成品进入可售池之后的损失。sold 是对模型所对应收入主体满足确认条件的销售数量；制造商售往经销商与经销商售给最终消费者必须分开，不能把两次销售都作为同一公司外部收入。净价包含一次折扣/返利；退货重入库、寄售、买断退回、跨 SKU mix 变化要额外桥接，本版本不自动处理。

## 首年余额锚点与生命周期路由

| 模型 | segment 基年锚点字段 | opening driver | dimension |
|---|---|---|---|
| `subscription_arr_bridge` | `base_arr_parameter_id` | `opening_arr` | `revenue`（年化 run-rate 定义） |
| `installed_base_aftermarket` | `base_installed_units_parameter_id` | `opening_installed_units` | `quantity` |
| `store_cohorts` | `base_stores_parameter_id` | `opening_stores` | `quantity` |
| `aum_fee_bridge` | `base_aum_parameter_id` | `opening_aum` | `monetary_balance` |
| `finite_adoption` | `base_unserved_market_parameter_id` | `opening_unserved_market` | `quantity` |
| `inventory_sellthrough` | `base_inventory_parameter_id` | `opening_inventory` | `quantity` |

| 企业阶段 | 建模优先级 | 首要证伪点 |
|---|---|---|
| 前收入/研发 | `commercial_launch` 条件路径；里程碑独立核验 | 获批/验收时间、真实可服务客户、供给资格 |
| 初始商业化 | 上市时间与供给上限；新店/新装机显式暴露 | 销量是否依赖免费试用、首批铺货或渠道囤货 |
| 快速扩张 | ARR新增与扩张拆分、门店年龄、装机耗材 | 新增质量、NRR口径、爬坡速度与组织容量 |
| 成熟 | 存量留存、替换/复购、有限渗透池、AUM费率结构 | TAM可达性、同店竞争、收费压降、客户预算 |
| 周期下行 | 成品去库存、发电捕获价、市场负变动 | 产量是否继续被错当销量、峰值价格是否被永续 |
| 衰退/退出 | ARR流失、退役/关店大于新增、有限池耗尽 | 负增长是否被不合理终值或新增抵销，剩余业务是否可持续 |
| 转型/第二曲线 | 原曲线衰退与新曲线上市分别建模，再审查迁移/替代 | 同一客户迁移是否被算成两次新增、内部收入是否已消除 |

这些是可组合的经济模型，不表示专用行业覆盖已经完备。保险 IFRS 17 合同组、矿山复杂回收与冶炼结算、银行期限重定价、储能逐时调度、多层基金绩效费、航司网络收益管理、多阶段药物概率树等仍需要专用模块或明确的数据缺口。

## 验证与准确性声明

`tests/test_model_extensions.py` 检查八类公式、六类存量桥、连续性、年底新增零贡献、完全流失/限电边界、供给约束、市场耗尽、生产不等于销售、负市场变动/负电价、超 100% 新店生产率、未知 NRR/POS 拒绝、非有限值拒绝和输入不可变。与全引擎的行业测试共同验证注册、参数解析、会计确认及输出合同。

这些属于模型正确性与边界测试，尚不是预测准确性证据。对新增模型的正式采用，应比较原简单模型与新增模型在同一信息日、同一公司/分部/预测期的滚动样本外误差；参数更多但 WAPE/MASE 未改善时，应保留更简单模型或明确记录数据不足。
