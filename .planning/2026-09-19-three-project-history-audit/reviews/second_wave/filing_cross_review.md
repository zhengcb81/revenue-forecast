# 第二波独立交叉复核：Revenue 模型、补充结论与实施计划

2026-09-19，reviewer：history_filing。本轮只读，不重复运行测试，不写生产资料、catalog 或 registry。已经完整读取 `reviews/revenue/model_ledger.jsonl` 的 31 项、`deep_clause_ledger.jsonl` 的 24 项、该分区报告、两个反例脚本与原 stdout/stderr/manifest，并读取主 `implementation_plan.md` 全文。使用 CodeGraph 获取当前结构，再核相关已定位源码。

结论：**核心结论得到源码和原始日志支持，可以合并；模型的 supported_scoped 没有被外推为实际预测准确性。** 两处表述应继续限定：商业 TC 示例的条件口径，以及单文件原子性的故障边界。没有发现应把 F01/F02 已修问题重新列为当前故障的证据。

## 1. 独立证据核对

`filing_cross_review_checks.json` 保留读取版本：11 份模型/发布回归测试文件与原 manifest 的 hash 全匹配；24 条深层条款的原文件 hash 全匹配。日志显示模型 97 passed +216 subtests，发布/attestation 37 passed，与报告一致。这只能认证这些受控套件的结果，不能替代真实资料准备、自然观察或统计准确性。

| 结论 | 本轮独立核查 | 判断 |
|---|---|---|
| F01 验证前签 receipt | `revenue_core.py:153–169` 先 `validate_published_forecast`，后 receipt；强门失败不进入签发步骤 | 已修的有限顺序问题保留，不能与后面的文件提交事务混为一谈 |
| F02 无显式 input 弱验证 | core:95 内嵌 input；report:1207–1214 校验绑定并强复算，1230–1235 当前 schema 缺 input 拒绝；1248–1253 dispatcher 用内嵌 input | 已修的当前 formal 入口保留；模型与输入一致不证明输入来自真实原文 |
| 普通文件被视为 host_signed 能力 | core:121–125 只 `which` 或 Path 后 `isfile`；167 直接根据布尔设置 label；publication:222–225 只检查 label 枚举。原 probe 设置为自身 Python 文件，日志示无 source signature、issuer=fixture-host，正式 validator 接受 | 反例支持“host_signed 标签未绑定实际签名/调用”。不是 Ed25519 密码算法被破解，也未证明任何真实公司数据被伪造 |
| registry 先写，输出失败留孤儿 | core:180 注册后返回；CLI:109 调用 formal，再115写 JSON、119写 Markdown。原注入 `_atomic_write_text` 抛 OSError，日志 exit2/新增1行/output不存在 | 反例支持整个发布包事务不足。单文件写临时→fsync→replace仍有有效局部保障 |
| 单文件不会半写 | CLI:22–35 保留旧文件直到 replace，普通异常 finally 清 tmp；37测试通过 | 只支持单目标文件的该调用路径。不能解释为进程强杀后无残留 tmp、目录 fsync 的掉电持久性或多文件原子提交；原 deep ledger 已明确不覆盖强杀/多文件，应保留 |
| 相同输入“幂等” | 原卡重跑恰2条、每次1条是审计事件语义；没有逻辑 publication ID 的恢复 exactly-once 证明 | 报告正确要求明确重复正式发布与允许的历史登记，不应仅因为2行就一概说是bug |
| mine grade/单位 | `mine_year_operation.py:6–22` 允许 kt/Mt、g/t/%语言；59–65数据类却无单位/basis；109–115直接相乘。`_positive_numeric` 仅>0，inf通过。原probe输出2000/inf与代码相符 | 支持 standalone helper 单位/有限性合同不足；`grade=2` 本身可有多种口径，不预设它一定是2%。不能将此扩展为31注册模型均接受inf |
| TC/RC/premium量纲 | commercial_terms:14–16称per-unit；118–126直接加减金额scalar，没有数量乘法。payability被接收但102–136不读取 | 支持契约不一致。probe的800仅在TC=2/每saleable单位、100为已payable销售量时成立；不是所有冶炼合同唯一正确收入。若100是未扣payability量，基数另变，应先明确口径，避免重复扣payability |
| ConfidencePolicy helper | weights:48–57无finite门；hash:136–144只非空；原 `not-a-sha`/inf结果与源码一致 | 只支持该helper反例；主formal历史记录有另一路校验，原报告未误称成功攻击formal，范围正确 |
| 自然soak/三公司/rollback/可达性 | 与本分区已阅读全文的8/13强规格、后继卡及reviewer缺口互证 | 合成测试本身有效；是原义务被窄卡取代并错误升级总体状态，不是“允许mock时间”本身错误 |

## 2. 31 模型逐项复核

31 行均显式写 `accuracy_conclusion=insufficient_evidence`，缺行业×生命周期×期限的真实无泄漏滚动回测。当前 23 个原 registry 公式及8个 extension公式、stock-flow桥和 `calculate_registered_model:296–354` 有限性/非负域已核。以下支持的是这些输入约束下的数学/代码和领域边界描述；真实数据可得、参数可识别、会计确认与外样本准确性仍独立待验。

| 模型 | 本轮对原 supported_scoped 的独立边界判断 |
|---|---|
| direct_growth | 支持递推、允许-100%；零基数无法凭增长率商业化，不能当因果驱动模型 |
| direct_revenue | 支持直接金额路径及有限非负；少字段不等高信心，需独立来源 |
| unit_sales | 支持销量×净单价；年度实际销售不能再用时间因子重复折算，退货折扣不重复计 |
| capacity_utilization | 支持产能×利用率×良率；投入/良品产能和库存转销量边界仍须数据核对 |
| subscription | 支持期间平均客户×年ARPU；期末客户、月ARPU、usage重叠不是数值门可自动判定 |
| usage_platform | 支持活动×货币/活动；GMV与净佣金、补贴和principal/agent需独立桥 |
| services | 支持收费活动产能×利用率×费率；人数不是工时，固定项目确认另判断 |
| project_backlog | 支持含signed重估的存量变化恒等式和连续性；未解释残差不能默认收入 |
| resource | 支持已售量×实现价；不把standalone矿业helper缺口扩到该注册公式，也不反向把公式绿扩到完整会计桥 |
| reserve_depletion | 支持储量桥/修订/连续性；耗用不自动等于已售量，品位和库存仍外置 |
| infrastructure | 支持可结算活动量×费率；免费量、阶梯价、特许权终止另查 |
| bank_revenue | 支持资产利息减负债利息及signed利率；不是完整ALM、信用损失模型；净收入非负域仍限制 |
| asset_management | 支持收费平均AUM×费率+已确认业绩费；市场涨跌不等申赎，结晶条件须核对 |
| retail_franchise | 支持直营与加盟费/供应收入拆分；体系销售不等公司收入、内销抵销和递延不可省 |
| transport | 支持运力×利用率×单位有效运量收入；yield分母须匹配客公里/吨公里/航次 |
| real_estate_rental | 支持已占用面积×年度租金；不得再乘入住率，现金与直线租金需桥 |
| licensing_commercial | 支持治疗单位×净价+独立许可收入；人数/剂量分母和事件条件不能靠成功概率代替 |
| advertising | 支持CPM除1000及fill；已售展示不可再乘fill，无效流量和平台净额需证据 |
| gaming | 支持活跃用户×付费率×ARPPU；DAU/MAU/年去重用户不互换，流水和递延另查 |
| cohort_subscription | 支持新增/流失时点与客户桥；同年新增再流失及异质ARPU仍受限 |
| delivery_pipeline | 支持订单桥和跨期连续性；交付不自动代表控制权转移 |
| milestone_royalty | 支持合格销售×版税率及已确认里程碑；概率加权研发收益不能冒充披露收入 |
| insurance_service | 支持可对账保险服务收入分解；原ledger明确不是完整IFRS17/精算覆盖，限定充分 |
| subscription_arr_bridge | 支持GRR损失、存量扩张、新ARR和时间分开；NRR不可再乘，ARR与确认收入差异待桥 |
| installed_base_aftermarket | 支持装机桥/退役上限/附着；不代表同年新装再退役、年龄维修周期全部覆盖 |
| store_cohorts | 支持新开/关闭时点、生产率>1；所有期初店在函数里按成熟价，超过一年的成熟曲线须拆年龄桶 |
| renewable_generation | 支持MW×小时→MWh、限电及负价；加权MW已含投产时点，不能再折算；小时数需匹配期间 |
| aum_fee_bridge | 支持市场变化与净流拆分、非负时间暴露；线性权重不是每日净值/申赎真实路径 |
| commercial_launch | 支持条件成立时需求/供给min及商业化时间；未把获批概率暗乘会计收入，边界正确 |
| finite_adoption | 支持剩余市场桥限制超采用；合资格市场口径、替换需求及预算渠道仍需证据 |
| inventory_sellthrough | 支持生产/采购/报废/已售桥；厂商、寄售、渠道库存不可混用 |

没有因模型名称数增加推断行业准确率提高，也未把 `math.fsum` 的数值稳定性直接等同投研预测准确性。关于扩行业/生命周期，主计划以每模型实际披露映射与样本外评价为退出条件是合适的；无需为每行业再建一套重复引擎。

## 3. 对主 implementation_plan 的意见

现版顺序和边界可用：先配置/扫描/索引/ready实际链，签名/事务与模型经济约束可并行，最后真实评估；保留已修F01/F02和已退休旧链；优先扩既有格式而不再造框架。未发现阻止继续采用的原则性问题。

建议补四个可直接加入现有步骤的小条款：

1. 在 I-00/I-17 明确将本次 **READ10证据错配、197条只有单status而无逐tier结果、CA206/301/302缩范围** 纳入现有接受门反例。不要再用新增一份scope表的存在证明语义已被保护；未做部署/自然观察必须实际阻断对应业务节点。
2. I-04 中 deadline 必须每次子调用返回后、sleep前重算。当前10→14反例是模拟时钟的9秒调用+5秒旧预算退避，不是已测真实14秒墙钟；未来修复验证需要受控真实延迟和结构化elapsed双证据。
3. I-10 矿业条款明确 commercial payability 与上游 `payable` 的唯一归属、TC/RC对应干矿石/含金属/应付金属数量基数。先定义单位/口径合同再选期望值，不通过把800或998写死造另一种弱测试。
4. I-05/I-06 应在consumer需要的角色集下检查actual read与生成成功；不要求所有公司都拥有summary/section或一律进入LLM，保留 `not_applicable` 和资料不足的可解释结果。现版已有适用性和最小DAG表述，实施时务必保留。

主文若将本轮判断概括为“31模型全部正确”“系统能达到买方准确率”“所有自然观察都是假的”，都会超出证据。当前分区报告及实施计划没有这样外推，建议维持现有谨慎范围。
