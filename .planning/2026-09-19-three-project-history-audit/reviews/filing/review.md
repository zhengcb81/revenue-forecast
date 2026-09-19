# filing-fetch 历史承诺独立复审

审查日期：2026-09-19。作者为 history_filing，独立于本次真实预测执行者。只新增本审计目录材料，未下载、写生产索引、运行worker、同步安装或修复产品。

## 结论

历史修复中确实有有效资产：请求/身份/schema/文件哈希校验、基本错误分类、N/N-1 envelope规范化，以及用户预先暂停worker时不恢复的逻辑。当前隔离复跑为 **280 passed、78 subtests passed、1 skipped、2 deselected**；skip是Windows symlink支持，deselect是两个继承位置的真实生产stdin测试，均未算通过。安装面实际存在且34文件×3目录一致。

但这些绿灯不能推出真实用户链路已完成。历次PASS常绑定单个函数、synthetic company_raw fixture、旧triplet或旧config。真实运行使用的是活跃策略、真实新文件和下游安全审查条件。两者输入与验收终点不同。2026-09-06文档已明确指出deadline、失败计数、policy接线及完整真实E2E缺口；9/8再明确synthetic T1 only；9/18仍调用旧总完成状态解释能力，就会遮蔽这些已知未闭合工作。这不宜笼统称为“所有修复都回归”。

本目录覆盖11份Markdown的全部内容块：400条有语义结论，89个纯标题/表头/父容器另存排除映射，0未审内容块。计数不是测试通过数，也不是400项产品问题；保留每份原文版本、行号、hash、历史说法、现行证据和结论。原始日期/时延/历史执行无法由现有证据重放的，明确标historical_only。外链另一项目的状态只审其引用含义，由共享计划对应owner深入审查，未将外链存在当实施证明。

## 当前发现与历史对应

| ID | 判断 | 历史来源 | 当前独立证据及影响 |
|---|---|---|---|
| FF-01 | P1，deadline全称承诺被反证 | CHANGELOG v1.1/v1.2；SKILL:53；9/6 filing-audit F-F05已记录 | 纯clock重放：10秒预算、子调用9秒busy、继续sleep5秒，14秒才退出；PausedWorkerScope过期仍分配10秒。旧test_subprocess_receives_remaining_deadline等仍绿，说明测试未覆盖消耗时间后的重算。 |
| FF-02 | P1，并发暂停计数保证不足 | CHANGELOG v1.4:16宣称Concurrency-safe | 两线程都完成原始读取后才串行执行原始写入：两个register均first=true，最终只留1个pid。无锁read-modify-write会丢参与者；固定.tmp还存在额外竞争风险，后者未做OS复现。不真实暂停worker，未宣称发生生产误resume。 |
| FF-03 | P1，真实新文档入口不在绿灯矩阵 | 根Phase3/4、E2E_DESIGN、FC805测试 | synthetic fixture只建schema1.0 company_raw，FC805明确把v2_scan_shadow设false；实际生产v2_scan_shadow=true而company_raw缺adapter_id，两份新年报已落盘却未索引。旧provider能下载不等于新生产扫描策略能入库。这是环境/激活矩阵不一致，filing仅观察到后验resolve失败。 |
| FF-04 | P1，完成验证器不能验完成真实性 | PLANNING_STATUS:62已提示漏Phase4 | 本轮exit0/ok=true仍只识别1/2/3/5/6。额外最小反例只有Phase1的pytest passed，Phase2仅提名也被判evidence=true；它不要求阶段内命令/计数/日志hash。不能用于产品闭环总门。 |
| FF-05 | P1，FC903收据链不闭合 | 原REVIEWER_REPORT accepted；9/6已记录mismatch | implementer raw SHA=`010699...89d`，reviewer绑定=`010d0b...3df`；LF归一化也不同。Git历史可见初次封存提交，但未找到原签署字节，不能推定具体修改动机或机械改hash重签。局部9个函数测试通过仍不修复历史认证链。 |
| FF-06 | P2，测试名称扩大了实际覆盖 | WU-1002 bundle fidelity及FC903 sibling green | test_bundle_fidelity的5项测试仅测试自造dict的JSON round-trip/集合差异，不调用生产转发；unknown role测试只断言集合里有unknown，未调用fail-closed逻辑。它们当前全绿，但不能证明跨仓传输或拒绝语义。 |
| FF-07 | P2，技能/操作说明滞后 | SKILL1.4与已有schema1.2/多根升级 | 正文仍companies-only、request must1.1、exit0=capture-ready；实际支持policy多根、1.2 latest/gap且gap exit0。worker_resume_failed未结构化输出，仅stderr warning。E2E_DESIGN说live opt-in，但test_real_tool_conformance只有_wiki_available门，默认本机discover可能执行live；CI通过ignore避开。 |
| FF-08 | P2，green对安装缺失可无感，但本机不是这一原因 | WU-7.1 install-sync CI | installation_diff在安装目录不存在时返回空列表，--check打印MATCH，CI fresh runner可产生“无安装而MATCH”。本轮3目录确实存在，34文件一致，故本次失败不能归于filing安装漂移。 |
| FF-09 | P1，失败后的下载事实/策略仍有接线缺口 | 9/6 F-F01/F-F06和ZR205/405 | 当前stats只在完整handle通过后更新download_events，gap直接返回不加计数，generic fatal不带stats，close-gap失效只抛摘要；policy缺失自动按N-1回companies。局部zero-download成功正例不能覆盖已写后失败。未在生产重做故障注入。 |
| FF-10 | P2，硬约束被独立审查豁免却未改合同 | FC903 contract:62和report:37 | contract要求代码diff≤200，超出必须split；report承认213仍accepted、unresolved为空。该差异不证明功能错误，但说明independent accepted并不自动保证验收纪律一致。 |

详细逐原文判定见[item_ledger.csv](item_ledger.csv)与[item_ledger.jsonl](item_ledger.jsonl)。187 supported_scoped只表示所引用狭义行为，151 historical_only不是失败，24 superseded不是当前缺陷。16 contradicted和20 insufficient_evidence需按影响与依赖编排，不可简单加总成36个独立bug。

## 为什么之前检验没拦住

1. **验收输入改变**：根Phase3的HK简繁目录问题以改fixture目录解决，Phase4茅台歧义以换宁德时代解决，HK请求FY2024变FY2025后成功；这些是有效诊断，但原样本能力没有等价补测。损坏“恢复”则改成“拒绝损坏”，属于缩小目标。
2. **环境维度未绑定**：真实provider可在隔离旧scanner策略下成功；生产激活v2 scanner后未证明root配置/adapter全套兼容。CI的本地runtime、legacy seed和no-op provider不能代表生产policy。
3. **consumer终点不同**：filing的capture_ready只说明原件及来源元数据具备条件；revenue还需安全review和派生artifact绑定。旧raw-ready PASS并未证明正式来源准备入口可继续。9/18紫金被not_reviewed安全门拒绝本身正确，缺少受支持补审路径才是业务断点。
4. **局部属性变成全称**：当前合同测试通过仍能被独立clock/交错反例击穿；历史总测试数、coverage和mutation只证明其输入与断言，不证明所有真实状态组合。
5. **状态账本未自动继承例外**：root completed_historical_scope、TERMINAL closed_superseded_incomplete、117accepted、R4 pending并存。若界面/人工只展示绿色总数，后续计划债务、skip、failed canary会消失。
6. **测试可用性被当正确性**：live套件因config_doctor红而skip，安装不存在仍MATCH，计划phase没被regex识别仍OK；这些能让总门绿而未真实执行关键检查。必须把not-run、blocked与passed分开计数。

## 下一轮实施详细顺序（仅计划，尚未修改代码）

### FF-P0：冻结可复现基线并定义就绪层级

1. 为每请求保存三repo实际加载路径/HEAD/dirty hash、安装hash、config hash、runtime policy/epoch、root注册adapter和原件/index状态。
2. 明确raw_ready、review_ready、artifact_ready、consumer_ready，禁止capture_ready被解释成可直接预测。
3. 把本次小米/微软已落盘未索引作为恢复起点；保留原件及sidecar，先设计重索引/恢复，不再次下载造绿。
4. 独立审查门：把原请求、生产配置和失败输出固定成RED验收样本；不更换年份/公司/关闭flag来宣称同一问题修复。

### FF-P1：贯通真实入库及来源补审

1. 与wiki owner对齐scanner策略和每root adapter_id/metadata schema；真实生产配置必须通过同一预检，不能只校验字段存在。
2. canonical写入→扫描→exact resolve逐阶段输出结果；scan失败应保留原原因和已写文件/下载事实。
3. 提供受支持的已下载文件恢复索引路径，以及审查receipt生成/验证操作；不直接改库或手填not_detected。
4. 独立验收：现有小米/微软字节恢复后首消费成功，第二次同请求零下载；紫金真实补审后source_preparation成功。scope门同时校验原件hash不变、index可查、bundle与consumer就绪。

### FF-P2：修复请求执行上下文、并发和计数

1. 各重试异常后重新计算remaining；worker清理预算与请求deadline分别定义并显式输出，禁止悄悄minimum10秒突破整体期限。
2. refcount加跨进程原子互斥/唯一临时路径和owner generation；测试同pid重入、双注册、注册与退出交错、死pid、PID复用、status失败、pause失败、resume失败。
3. 请求执行上下文只加载一次并注入resolve/ensure/close-gap及finalize；N-1降级要显式peer版本而不是缺字段自动放行。
4. 分开fetch_started/completed、raw_committed、indexed、resolved；失败也保留已知计数。未知应null+reason，不用默认0。
5. 独立审查：本目录pure_probes先红后绿；使用真实生产函数的隔离故障矩阵，provider spy与文件/catalog双oracle对账。无需在生产故意制造失败。

### FF-P3：重建测试与闭环证明

1. 保留现有纯合同测试；把bundle fidelity测试接到实际转发函数/两个真实CLI边界，并增加字段删除/rename/hash篡改/未知role负例。
2. 测试矩阵增加runtime flags×root registry×exact/latest×首次/复用×raw/review/artifact状态；fixture必须显式声明与生产的差异。
3. 安装检查分MATCH/DRIFT/NOT_INSTALLED/UNREADABLE；live未授权/环境阻断不能算通过，CI和本地门使用相同状态统计。
4. 完成验证改为每条稳定ID绑定输入hash、精确命令、退出码、stdout/stderr artifact hash、triplet/config、scope和独立review；所有未识别项一律coverage error。
5. 修复FC903证据需找到原签署字节或新建独立复验收据并显式supersedes；不修改历史receipt伪装原审查成功。
6. 独立产品验收必须从revenue真实入口走三市场、已有/缺失两分支，并最终形成正式预测。关键断点失败则该journey失败，不能以单元测试补票。

### FF-P4：文档与运维收口

1. 以代码schema/契约单一来源生成技能请求/响应表及错误码；明确metadata discovery与download授权边界。
2. 将旧总完成状态降为历史记录并在每处入口展示未关闭范围；每次生产flag/config/peer版本改变自动使相关验收过期。
3. 部署新版本后验证实际安装和实际调用路径，保存不可变证据；未做生产验收时只能写“implemented, production validation pending”。
4. 独立review逐项检查无skip冒充passed、无换样本掩盖失败、无未识别phase漏计，并对计划变化记录批准依据与替代目标。

## 执行与限制

完整命令/退出码/stdout/stderr/hash在tests/。pure_probes仅使用导入函数、mock clock与审计目录临时文件；没有调用真实worker/CLI/provider。refcount探针证明read-modify-write逻辑丢更新，不能当作生产已发生事件。

审计自身操作错误已保留：runner一次父目录计算错误WinError267；提取器初次stdout默认GBK遇✓编码错误，JSON已写且改用-X utf8成功；Python子进程git读取遇dubious ownership，后续仅针对已知repo使用进程局部safe.directory读取，未改全局配置。这些是审计环境问题，不计入产品缺陷。
