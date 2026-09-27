# Mandatory 测试、真实 E2E 与故障场景矩阵

## 1. 基线场景不可丢失

旧矩阵中的95个 `EX/DBX/DL/LT/AR/SAFE/CTRL/OPS/PORT/IDX/UJ/AUD/MIG` 场景继续全部 mandatory，冻结来源：

- `audit_review/2026-08-09_full_completion_assurance_plan/scenario_matrix.md`
- SHA-256：`21e9201296aa048bd61e1125525a0eadb8ac1deb5bed76a641f05b3099f1d3c5`

未来 machine registry 必须导入这95项并加入本文的新场景。若来源 hash 变化，registry build 必须失败并要求独立审查；不得静默采用新版本或减少场景。旧 `DBX-*` 验证 Dropbox filing 安全边界，不能替代下列 broker-research 场景。

## 2. 测试层级

| 层级 | 数据/边界 | 能证明什么 | 不能替代 |
|---|---|---|---|
| T0 | temp memory/files；纯函数/contract/property | 局部不变量、错误码、公式、schema | 生产接线、三进程、真实数据 |
| T1 | temp 三 roots/catalog；真实 revenue→filing→wiki subprocess；provider/LLM边界spy | current-triplet真实接线、调用预算、幂等 | 真实49GB catalog/私人PDF/provider |
| T2 | 真实 catalog、companies/dayu/Dropbox 只读；audit 输出隔离 | 生产数据可查可复用、真实SLO和零写 | 网络下载、生产切换 |
| T3 | 真实 provider + 临时 wiki/canonical target | CN/HK/US首次下载、二次零下载、provider漂移 | 生产 cohort |
| T4 | 明确授权的最小生产 cohort | cutover/rollback/观察 | 长期动态健康 |

Mandatory real tier 因权限、凭据或样本缺失只能 `blocked`；closure 不接受 blocked，不能 skip/xfail/pass。

## 3. 统一事件与 oracle

每个跨进程场景必须输出：

- 八阶段 `identity/resolution/freshness/acquisition/safety/artifact/semantic/consumer`；
- `provider_discover/fetch`、`canonical_write/external_root_write`；
- `parser/llm/artifact_read` 按 role；`processing_demand` enqueue/dedupe/run；
- DB read/write/DDL/migration/commit attempts、lock waits/retries；
- source/artifact/fact/publication registry deltas；
- `triplet/policy/schema/activation_epoch/cohort/command/scenario` hashes；
- root 文件 count/bytes/path-token/hash set 的 before/after fingerprint；
- duration、peak memory、collected/passed/skipped 和 trace hash。

oracle 必须来自独立 spy/journal/OS fingerprint/公式重算；被测函数自己的 summary 不能作为唯一真相。

## 4. READ：真只读、并发和错误分类

| ID | 层级 | 场景 | 必须结果 |
|---|---|---|---|
| READ-01 | T0/T1 | Reader 指向不存在 DB/父目录 | 结构化 not_found；文件/目录不创建 |
| READ-02 | T1 | DB 和目录 ACL 只读 | identify/query/status/resolve/bundle 成功；write/DDL/commit attempts=0 |
| READ-03 | T1 | monkeypatch writer initializer/`mkdir`/DDL 为调用即失败 | 全部只读入口仍成功 |
| READ-04 | T1 | current schema | Reader 验证版本后查询，不执行 migration/seed |
| READ-05 | T1 | future/unknown schema | fail closed；DB bytes/hash不变；不自动升级 |
| READ-06 | T1/T2 | live writer 长事务同时 exact resolve | Reader有界完成；不抢 `BEGIN IMMEDIATE`；download=0 |
| READ-07 | T1 | raw SQLite locked/busy、operation lock、worker paused | 统一版本化 reason；retryability精确 |
| READ-08 | T1 | permission/corruption/schema error含“lock”相似文本 | 不得误归 catalog_locked/retry |
| READ-09 | T1 | 锁释放前两次失败、第三次成功 | deadline内退避；attempt/jitter/elapsed可对账；只返回一次结果 |
| READ-10 | T1 | 锁持续超过deadline | 到期结构化失败；不超时长预算；保留此前reuse/download阶段证据 |
| READ-11 | T2 | 49GB/大证据表查询 | p50/p95/p99、内存、锁等待在冻结SLO；无Python全表扫描 |
| READ-12 | T0/T1 | 删除某一只读入口的Reader接线 mutation | architecture/production-caller gate 必须红 |

## 5. BR：券商研报、PDF、表格、chunk、tag 与隐私

| ID | 层级 | 场景 | 必须结果 |
|---|---|---|---|
| BR-01 | T1/T2 | 七份紫金PDF | 7/7 source hash/page count/publisher/date/role 与独立黄金集一致 |
| BR-02 | T1 | PDF + `.source.json` | 一个文档group；sidecar仅metadata；primary sidecar=0 |
| BR-03 | T1 | random JSON/图片位于Dropbox | 不因路径自动成为broker report |
| BR-04 | T1 | 无sidecar但首页可验证 | identity proposal→verified；路径/文件名只作弱证据 |
| BR-05 | T1 | 文件名与首页实体/日期/标题冲突 | assertion conflict/review；不静默覆盖 |
| BR-06 | T1/T2 | 长江紫金vs陕西煤业比较报告 | 多实体；陕西煤业2028E ROE不归紫金；错归率=0 |
| BR-07 | T1 | 文档主实体+局部表比较实体 | section/table/row attribution覆盖文档默认值 |
| BR-08 | T1 | published_date NULL | 不参与latest排序；进入identity remediation |
| BR-09 | T1 | 旧深度报告+新短点评 | `latest`与`most_complete`分别返回且as-of正确 |
| BR-10 | T1 | 修订版/同券商不同日期 | revision family与supersedes可追；旧facts保留 |
| BR-11 | T1 | 双栏、重复页眉脚、图片页 | MD阅读顺序/页码locator正确；quality flags完整 |
| BR-12 | T1/T2 | 多级表头/merged cells/跨页表 | table matrix、header hierarchy、caption、footnote、bbox保真 |
| BR-13 | T1 | 嵌入字体/字符解码异常 | raw+normalized保留；低置信flag；不得产accepted错误fact |
| BR-14 | T1 | scanned/encrypted/truncated/corrupt PDF | OCR demand或结构化失败；不产可信facts |
| BR-15 | T1 | 表级/列级单位及脚注 | 每个关键cell可回页/表/行/列；单位不凭空补 |
| BR-16 | T1 | 2024A/2026E/2028目标同行 | actual/broker_estimate/management_target正确分开 |
| BR-17 | T1 | table跨chunk | 每片重复必要表头/单位/脚注引用；不跨实体/actual-estimate |
| BR-18 | T1 | entity/asset/commodity/metric/period检索 | recall/precision达到冻结黄金阈值；结果带source SHA+locator |
| BR-19 | T1 | source bytes/parser version/artifact bytes变化 | 只失效DAG相关节点；篡改artifact不复用 |
| BR-20 | T1 | 相同SHA跨三roots | 一document、一套artifacts/facts；处理一次 |
| BR-21 | T1 | private_user Dropbox无外部LLM授权 | 外发调用=0；结构化privacy blocked；本地能力可选 |
| BR-22 | T1 | 10并发同ProcessingDemand | 单producer event；相同receipt/dedupe key |
| BR-23 | T1 | already-ready/partial/worker重启 | ready时parser/LLM=0；partial只补缺失；重启无重复事件 |
| BR-24 | T1 | interactive/background混合队列 | deadline/配额/公平性；无永久饥饿或priority全局篡改 |
| BR-25 | T1 | 官方HTML 200且hash有效但title/entity错误 | identity gate拒绝；错误strategy页不得入facts/model |
| BR-26 | T1/T2 | 有效官方公告/新闻 | capture→review→index→MD/table/chunk/tag；再次消费零处理 |

## 6. MINE：资产事实、口径、运营与会计桥

| ID | 层级 | 场景 | 必须结果 |
|---|---|---|---|
| MINE-01 | T0/T1 | single mine/mine group/operating company/project | asset_scope正确；公司聚合不能冒充单矿 |
| MINE-02 | T0/T1 | Timok/Čukaru Peki/丘卡卢-佩吉别名 | 同asset ID；歧义/碰撞fail closed；别名有时效 |
| MINE-03 | T1 | country/region/parent-child/运营方 | 层级可检索且不循环；parent/child不能重复加总 |
| MINE-04 | T1 | resource与reserve同行 | predicate严格分离；含标准/measurement date/basis |
| MINE-05 | T1 | 100%/attributable/consolidated/equity-accounted | basis必填；未知material fact不进模型 |
| MINE-06 | T1 | Kamoa/Porgera已是attributable production | 不再次乘ownership |
| MINE-07 | T1 | 受控80%子公司 | consolidated revenue inclusion=100%，不是80% |
| MINE-08 | T1 | equity-accounted 44.2%项目 | consolidated revenue inclusion=0；运营指标仍可披露 |
| MINE-09 | T1 | acquisition/ownership/commissioning半年度变化 | timeline和timing factor正确；不后见泄漏 |
| MINE-10 | T1 | Bisha 763,100kt vs 763,101t | 两原值保留+数量级conflict；不得自动择一 |
| MINE-11 | T1 | 3Q在建/已投产冲突 | 双assertion+有效期/conflict；不覆盖成单真相 |
| MINE-12 | T1 | disclosed项目之和与集团总量不等 | 保存residual/unallocated；不得擅自归属 |
| MINE-13 | T0 | g/t、%、吨、盎司、LCE/Li2O换算 | 显式unit conversion；错维度/数量级fail |
| MINE-14 | T0/T1 | ore→contained→recovery→payable→saleable | 每步可重算；缺值为gap，不默认为0/1 |
| MINE-15 | T0/T1 | concentrate/doré/cathode/refined、多商品副产品 | product form、byproduct、payability不重复计价 |
| MINE-16 | T0/T1 | realized price含/不含TC-RC、premium、FX、royalty | 商业定义显式；不得重复扣减/换算 |
| MINE-17 | T1 | mine内部销售到集团冶炼 | mining/smelting external revenue不双计；elimination可追 |
| MINE-18 | T1 | mine subledger+minor asset residual | 精确勾稽矿产品外部收入；residual不藏入other plug |
| MINE-19 | T1 | 完整bridge缺字段 | 只能operating indicator/range/data gap；不输出伪逐矿营收 |
| MINE-20 | T1 | 来源只覆盖到2028，模型到2030 | 后两年只能显式analyst assumption；不能继承source claim |
| MINE-21 | T1 | Low/Base/High mine-year | 每资产/产品逐年low≤base≤high；集团/分部也满足 |
| MINE-22 | T1 | source/fact/assumption改动 | 只影响相关asset/year/scenario并重新对账 |
| MINE-23 | T1/T2 | 紫金主要资产coverage | 国家/矿种/resource/reserve/ownership/product/period覆盖报告和冲突完整 |
| MINE-24 | T1 | 第二家不同结构矿企 | 不改产品代码即可建模；公司/矿名hardcode=0 |

## 7. REV：输入、验证、发布、模型、置信度与回测

| ID | 层级 | 场景 | 必须结果 |
|---|---|---|---|
| REV-01 | T0 | SchemaSpec vs constants/validator/linter/generator/docs | current版本和字段完全一致；3.6只在migration allowlist |
| REV-02 | T0/T1 | generator最小模板经placeholder filler | lint→validate_document→draft full run一次通过 |
| REV-03 | T0 | 删除management_targets/growth tree/claims/host_receipt等随机字段 | linter false-clean=0；稳定error code |
| REV-04 | T0 | direct model/driver dimension、recognition policy | 错配fail；generator不产错骨架 |
| REV-05 | T1 | CLI `--validate-only` valid/invalid | signer/registry/subprocess/network/write调用=0；文件树与registry不变 |
| REV-06 | T0/T1 | 合法draft validate+render | 成功，明确draft水印/limitations；publication registry不变 |
| REV-07 | T0/T1 | 合法formal validate+render+publish | 强门全部重算；registry精确一次committed记录 |
| REV-08 | T0 | draft/formal receipt mode/gates/input/payload互换或重hash攻击 | 全部fail closed；invest拒draft |
| REV-09 | T1 | formal output/registry/sign/rename在各阶段失败 | 无静默孤儿/半发布；pending可审计恢复；append-only |
| REV-10 | T1 | source safety失败但filing已exact reuse | 顶层保留reused_existing/download=0并指明safety blocker |
| REV-11 | T1 | valid artifacts / partial / legacy_unbound | ready零producer；partial最小重算；legacy不读且给next action |
| REV-12 | T1 | mine显式模型与direct fallback混合 | explicit share按收入权重；fallback/gap/rating cap准确 |
| REV-13 | T0 | duplicate claim/参数拆分/other_revenue plug/零影响sensitivity | 不得提高confidence |
| REV-14 | T0 | 单个低误差backtest、错公司/模型/as-of accuracy record | 不得复用/满分；sample-size/recency/horizon生效 |
| REV-15 | T1 | immutable rolling-origin backtest | input cutoff无future actual；snapshot/result/actual/record四层hash |
| REV-16 | T1 | trade gross/net混合、other时点/时段混合 | schema能分流或明确gap；不靠单错误presentation近似 |
| REV-17 | T1 | source covers_until与forecast horizon | 超期claim拒绝；source-free外推明确 |
| REV-18 | T1 | current Zijin draft复现 | 五年三情景/CAGR/对账/claims可重算；native renderer成功 |
| REV-19 | T1/T2 | 紫金完整资料旅程 | filing+broker+official web bundle实际读取；processing/download决策receipt完整 |
| REV-20 | T1 | 第二次同请求 | file/artifact/analysis缓存按兼容性复用；无新增下载/无不必要处理 |
| REV-21 | T0/T1 | formal 3.7与additive 3.8 opt-in | 3.7 hash零回归；converter不猜矿山字段；flag rollback恢复 |
| REV-22 | T1 | 紫矿shadow vs旧direct-growth | 每年/分部diff有原因；未解释差异阻断cutover |

## 8. ZJ：紫金真实回归旅程

| ID | 层级 | 场景 | 必须结果 |
|---|---|---|---|
| ZJ-01 | T2 | FY2025/FY2024 年报在多roots | exact file reuse、0下载；安全/artifact阶段可见 |
| ZJ-02 | T2 | 年报旧MD/summary无binding | 不盲用；migration/demand action精确；原artifact不删除 |
| ZJ-03 | T2 | 七份Dropbox研报 | 7/7可消费；表格/多实体/隐私/标签质量门 |
| ZJ-04 | T2 | 官方Results/Norton及错误strategy页 | 有效页可消费；错误身份页拒绝并保留负例 |
| ZJ-05 | T1/T2 | 矿种/国家/主要资产/resource/reserve | 覆盖和冲突可查；resource不冒充reserve |
| ZJ-06 | T1 | 逐矿2026–2030信息不足 | 输出明确gap/模型估计边界，不伪称披露营收 |
| ZJ-07 | T1 | 旧报告+provider新报告，有/无授权 | 无授权0下载；授权只补新期；第二次0下载 |
| ZJ-08 | T1/T2 | live worker同时用户预测 | Reader无写初始化；锁分类/重试有界；用户阶段receipt完整 |
| ZJ-09 | T1 | draft模型、render、backtest、confidence | 全链成功；registry零写；评分抗博弈 |
| ZJ-10 | T1/T2 | 同一完整请求第二次 | 已有原文、处理、事实和分析按合同复用；权威昂贵调用为0或仅必要失效节点 |

## 9. 动态审核自证补充

| ID | 层级 | 故障 | 必须结果 |
|---|---|---|---|
| AUD2-01 | T0/T1 | workflow有runner但无实际schedule/最近run | release blocked；脚本存在不算动态运行 |
| AUD2-02 | T0/T1 | daily/weekly/monthly report过期 | 不沿用旧绿；明确stale |
| AUD2-03 | T0/T1 | wrapper吞掉scheduled command非零 | release gate非零；半报告不原子发布 |
| AUD2-04 | T0/T1 | 伪造download/parser/LLM=0 | journal对账失败 |
| AUD2-05 | T0/T1 | broker黄金样本或root unique sample缺失 | blocked，不自动换易样本 |
| AUD2-06 | T0/T1 | renderer或consumer-ready率回归 | business SLI阻断发布，即使unit tests绿 |
| AUD2-07 | T0/T1 | plan/registry并发hash变化 | 当前WU停止；receipt拒绝last-write-wins |
| AUD2-08 | T0/T1 | reviewer=implementer/不干净checkout | closure拒绝 |

## 10. 黄金集与版权边界

- CI 提交合成小PDF/HTML；真实七份券商PDF只在受控本地 T2 registry，以hash ID引用，不上传原文或长摘录。
- 黄金预期由两名独立审阅者从原页标注 publisher/date/entity/table boundary/header/unit/actual-estimate/ownership；待测parser不能生成自己的expected。
- 关键表 detection recall=100%；关键cell normalized accuracy≥99%，但任何material错列/错单位/错实体直接失败，不能用总体均值掩盖。
- 固定样本保证确定性；轮换样本保证泛化。样本失效是blocked，不是skip。

## 11. 单场景完成定义

只有以下全部满足才是 `passed`：

1. 行为正向断言；
2. 明确负向断言；
3. side-effect budget；
4. stage receipt/错误码；
5. 独立oracle重算；
6. 输出、trace和样本hash；
7. 对应fault/mutation被杀；
8. 指定层级实际运行且证据新鲜；
9. current triplet与registry一致；
10. collected数量无下降、skip/xfail=0。

任何 mandatory 场景不满足，所属ZR/Phase不得进入 accepted/complete。
