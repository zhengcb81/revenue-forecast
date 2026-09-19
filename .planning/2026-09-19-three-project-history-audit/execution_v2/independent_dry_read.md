# 执行包 v2：有界独立干读

审查者：audit_independent；日期：2026-09-19。**这是文档干读及只读依赖核对，不是较弱模型的产品实施试验。** 本次未运行产品、provider、scan、审核 writer、worker、prune 或测试套件，也未授予任何产品卡 ready/accepted。

**修订后结论：四项干读发现已在文件中修正并独立复核；有界文档审查 accepted_scoped。最终 86 卡均 planned，显式依赖无环。** 该结论只支持继续进行专业决定/环境绑定及后续隔离试点，不证明产品已修或弱模型已经具备独立实施能力。下文保留初审原发现，末尾记录修正证据与最终检查版本。

## 范围与方法

完整阅读 START_HERE.md、root_cards.md、scenario_matrix.md、sample_manifest.json、review_and_handoff.md、pilot.md；读取最新 dispatch.json 的全部 85 卡依赖/状态，以及 build_dispatch.py 的父项展开规则。重点从不了解三仓历史的执行者视角走查 I-00-B、I-07-B、I-14-A。为了查隐含依赖，只补读模型卡的 A–C/D–E/F 资格分离说明和研究卡 I-11-B、I-12-A 等相关段落；**没有借此声称独立语义审完全部 85 张卡或 31 个模型**。

以独立只读 Python 代码从各原卡 JSON 和 root_cards.md 重新构图：当前 85 卡、18 parent，父项展开后没有显式环或未知依赖。特别是 I-12-A → I-07-E，而 I-07-E 对 I-10 的依赖已限定公式资格，公式卡没有反向依赖 I-12；因此先前担心的显式 I-07/I-12 循环当前不成立。这个图检查不检查正文中的隐藏前提，见下面 DR-02。

样本部分只核对字段、历史证据定位和所指 sidecar 是否存在，未重新核验财务事实、catalog 当前资格或来源安全状态。三份 raw 的规划时 hash 是主审 sample_manifest 的记录，不能表述为本次独立重哈希结果。

## 三张代表卡能否指出下一动作

| 卡 | 执行者的第一项具体动作 | 能独立判断的预期 | 必须停止的位置 |
|---|---|---|---|
| I-00-B | 在 I-00-A 隔离映射可读后，打开所领卡实际入口的参数解析与调用路径，把现有 argv/cwd/config/模块绑定到新 attempt。先不执行旧 download 命令。 | 明确指向生产 DB 或不存在参数的命令不能获准运行；合格只读入口须命中指定模块。 | 参数不存在、子进程回落生产默认路径、导入有未隔离副作用；新增实现尚不存在的命令适用 DR-01。 |
| I-07-B | 先核对展开的来源前置卡资格及 case 输入绑定，然后从固定 9 格中领取具体一个 case，建立该 case 的初始文件/catalog/事件清单。 | 已存 raw 两次下载均 0；工件第二次新调用 0；实际读取身份/hash/财期正确。C 层模拟首次下载 1 不能签 L 层。 | 所需 review/工件尚未真实完成、as-of/capture 不兼容、provider 不可达或 live 样本未绑定；禁止换公司或删除副本造绿。 |
| I-14-A | 读取 slo_probe.py 真实启动/返回码/输出/RSS 路径，再请运维 reviewer 冻结夹具 payload、内存进程的分配/持有/释放方式、采样间隔和可容许误差；随后由 I-00-B 绑定实参。 | exit 7 即使 stdout 像成功也失败；exit 0 业务失败也失败；内存样本必须在同 PID 存活期间取得，缺样本不能填峰值 0。 | 测量方法与夹具仍未冻结、实际目标 catalog/config 不一致、仅复制 exact 延迟冒充 bundle；不能改 5 秒/2 GB 门槛掩盖测量问题。 |

三张卡目前可以支持“读哪些文件、准备什么、停在哪里”的解释；这不是可立即无人监督实施的判定。共同协议中的专业冻结与命令绑定仍是必要工作。

## 发现及交主审的小修

### DR-01：新接口尚不存在时，绑定门需明确分阶段

严重性：高（可执行性阻塞），初审状态：changes_required。

START_HERE 要先把运行命令绑定才 ready；I-00-B 又要求命令/test nodeid 真实存在。I-02/I-06 多个获准的新恢复/审核入口要实施后才存在。如果把“本卡所有未来命令已存在并全绑定”解释为允许写代码的前提，执行者会卡在先有实现才能获准实现的循环。

建议明确两阶段：先冻结专业决定、允许编辑范围、隔离路径、现有 baseline 命令，释放该范围的实现；实现后重新核查新 test/CLI 实际入口、argv 和副作用，绑定完成后才执行新增命令。未绑定命令始终不能运行，也不能因 baseline 通过宣布产品完成。

### DR-02：披露适配与定性校准存在正文中的隐含循环

严重性：高（职责/资格歧义），初审状态：changes_required。

I-11-B 前提要求“模型卡披露适配口径已审定”；模型卡说明 D–E 由 I-07-E 承接核验，而 I-07-E 又依赖整个 I-11。显式依赖图虽然无环，不熟悉背景的执行者可能等 I-07-E 完成才愿意给 I-11-B 提供 D–E，或错误地将 M 卡公式 accepted 当成披露资格。

建议明确：所采用模型的 D–E 专业适配工作可以在 I-11-B 之前独立执行并形成具名、带源/模型版本的资格记录；I-07-E 只消费并复核这份先行记录，不能成为该记录的唯一生产者。若要用独立子卡调度，也应明确建卡及依赖，不留给弱模型自行跳级。

### DR-03：发布故障 F06 需要已冻结且已验收的事务前置

严重性：中（调度缺前置），初审状态：changes_required。

I-07-D 当前只依赖 I-07-B，但其范围含 F06 registry/第二输出/commit 的发布恢复，所需事务机制属于 I-09。建议将 F06 的启动显式挂到相应 I-09 子卡，或给 I-07-D 增加 I-09 前置。不能靠 I-07-B 来源链通过就测试尚未定义的发布恢复 oracle。

### DR-04：紫金未注册案例的 sidecar 需显式定位

严重性：低（样本交接），初审状态：changes_required。

sample_manifest 中 CN-ZIJIN-2025 无 sidecar 字段，I-07-A/B 的“原件和 sidecar 存在但未注册”案例又需要该输入。本次只读检查确认 raw.path + `.source.json` 实际存在，但未来执行者不该自行猜路径。建议主审清单显式加 sidecar 路径与规划时 hash，三样本在执行绑定时再复核；存在性本身不证明 provenance 合格。

## 已明确且不应撤掉的门

- H/C/R/L 层级、真实缺失与隔离模拟分开；外部 only 缺样本仍 blocked，不能伪造排他性。
- source-preparation 成功与正式预测、买方质量、准确性、持续运行资格分开；I-12 没证据可以得出未证明优于基准，不能宣称改善。
- 干读和结构检查不等于弱模型可独立执行；pilot.md 保留实际模型版本、独立保留案例、人工介入、上下文接续和失败，不据文档质量推断试点已过。
- 原始退出码、expected 退出码与业务结果分别保存；发现当前已修可限域复验，不人为造 RED 或改旧证据。
- 实际消费和计划选择、真实调用与产物行、自然时间与模拟时钟均分开。

## 初审结论与复核位置

初审为 **changes_required（仅上述执行歧义）**。计划对范围与证据层级的总体约束清楚；完成小修后可支持继续进行环境/专业决策绑定。它仍不能直接签发产品 ready、弱模型能力通过或实际修复完成。

主审完成修订后，本文件将在此处追加逐项复核；不会删除初审发现，亦不重跑产品。

## 修订后独立复核（2026-09-19）

已重新读取修订点和完整新增 I-10-A、I-11-B 的前置段，从原卡重新构建最终依赖，再与最新 dispatch.json 逐卡比较。没有重新全文审查全部 86 张卡。

| 原发现 | 实际修正与独立复核 | 最终状态 |
|---|---|---|
| DR-01 | START_HERE 固定步骤 2 及“命令不能猜”、I-00-B 步骤 4 明确：实现前绑定基线/设计/允许改路径，新接口 planned 不阻止获准编辑；实现后再绑定实际 argv/nodeid 才运行。另要求每个 command-run 使用新的测试目录，防止 pytest 清掉上次证据。 | resolved_in_document |
| DR-02 | 新增 [I-10-A](card_I-10-A.md)：来源链和公式资格先行，所用模型 D/E 的已披露历史映射先行完成；不依赖 I-11/I-07-E。I-11-B 显式依赖 I-10-A；I-07-E 只消费/复核该资格。新卡步骤 4 明确历史参数可同值映射，不将历史接线 probe 假称三情景预测。 | resolved_in_document |
| DR-03 | I-07-D 显式增加 I-09 依赖；最终展开包含 I-09-A、I-09-B、I-09-C。F06 不会在发布事务资格尚缺时被无条件释放。 | resolved_in_document |
| DR-04 | [sample_manifest.json](sample_manifest.json) 的三样本均有 sidecar 路径及 planning_time_sidecar_sha256。本次最后只读重算三份 sidecar，3/3 与清单相符；这只证明该文件绑定一致，不证明审核状态/财务事实合格。 | resolved_in_document |

最终独立静态检查结果：

```json
{
  "raw_cards": 86,
  "dispatch_cards": 86,
  "model_cards": 31,
  "all_planned": true,
  "cycles": [],
  "unknown_dependencies": [],
  "dispatch_dependency_mismatches": [],
  "sidecar_hash_matches": "3/3"
}
```

该检查未调用主审 build_dispatch.py 或产品。只读 Python 从 root_cards.md 标题/Parent/依赖，以及 wiki/filing/model/research JSON 卡列表生成 parent→child 表，按父项全部展开，再用 DFS 检查环，并逐卡对比 dispatch.effective_depends_on；它只证明显式依赖与索引一致，不能替代语义审查。DR-02 的闭环判断另由正文逐步阅读确认。

关键先后链现在为：I-07-B → I-10-A → I-11-B → I-11-C → I-07-E → I-12-A；I-10-A 另等 31 个公式卡，公式卡没有反向等待 I-12。所用模型的披露适配与尚未使用模型、未来准确性评价仍分别管理。

末次读取版本如下。后续若有实质修订，应重新审查受影响段，不能仅因文件同名继承本结论。

| 文件 | SHA256 |
|---|---|
| START_HERE.md | `4efb7d9e3293d39a7d474a1c3300ef759ff4b02ecdb8d3e9e7a82f942faed2d4` |
| root_cards.md | `ff125ee4a2692aafb98412d7f28c37c9cb279425c54d263891b9a3333f7dccac` |
| scenario_matrix.md | `0dec23cd10f00efd6ad82cf923552bd46c1763bcf9f740422f51f4973292299f` |
| sample_manifest.json | `7a563d98b060f875178ab3a97530adfaeac57d027aae3154c659a6aaa1098996` |
| review_and_handoff.md | `602cce399cace78abb8b369ed36ed6e12540361393d636979a12df51e6ff12b9` |
| pilot.md | `bfd22849020cbf8ef6159a1b6994011528b0a1533f39010f614b8b7fed21f6b0` |
| dispatch.json | `7c81f8ec193bdc62a7aee0d2ea22c515bc64cd62baf3f703b6b5b91611373da9` |
| research_cards.md（只复核相关段与 I-10-A，不宣称本册全文独立审完） | `a213d41cd27997e9470568d0f953c19a9f67a7025d8878bf0603b656e94d723b` |

最终结论为 **accepted_scoped：上述协议、矩阵及代表卡的有界文档干读问题已解决**。专业决定尚未签、命令仍 unbound 的卡继续 planned/blocked；本报告不释放产品执行、不签真实数据链/预测/统计准确性或生产运维资格。较弱模型是否能完成任务，仍须按 pilot.md 实际运行隔离试点并保留失败与人工介入。
