# Revenue 历史独立重审报告

冻结范围为 inventory 的 revenue 主线 397 份文档、40,596 行。本代理负责 313 份，已全文读取并逐段连接人工语义审查；其余 84 份由主审和 filing 代理分别审查。revenue 路径下另有旧 wiki 109 份、旧 filing 5 份快照，由主审按版本差异合并；397 与这些快照合计 511 个路径，不能当作 511 份当前 revenue 规划。主审补入的 5 份上下文属于 company-wiki，不改变 revenue 主线分母。

`source_semantic_ledger.jsonl` 保留 313 份文件的 5,519 段原文和行号，其中 5,428 段连接人工结论，91 段仅为明确导航/分隔符；技术性标题和带状态标题不排除。相同义务重复出现在卡片、进度、结案中，共用判断但保留全部出处。判断依据为 262 个原工作单元、776 个 checklist 叶子（93 个语义簇）、31 个模型、119 个文档语义簇、61 个明确拆分的正文条款和 27 个深入条款。以上数字不是互斥事项数，不可相加当作测试数量。另有 company-wiki assurance/fc 29 份报告、2,164 行、579 段保留映射。

审查完成包括“证据不足”“未部署”“已被后继取代”等明确结论，绝不等于全部产品通过。旧命令的执行数字如果没有本轮独立复跑，仅作为对应版本的历史证据。

## 当前最重要结论

大量修复和测试通过是真实的局部工程资产，但反复出现“把目标降为可测小切片，后继仍接受，最终只验证 accepted 标签”的闭环。不能把所有历史 PASS 都否定，也不能用 PASS 数量证明真实企业从来源到可投资预测的结果。

1. **自然观察被替换为纯函数样本数。** 原 CA-206 要求真实 7 Daily、2 Weekly、1 Monthly、告警/回滚且不可豁免；最终卡禁止实际 scheduler/soak，仅验纯函数。`tests/test_ca206_soak_window.py` 在测试文件内实现计算器；本轮受控反例用 7 个不同 ID、同一未来时间、空证据 hash 获得 complete。此结论是该验收 oracle 的不足，不是实际自然时间观测，也不能覆盖 9 月后继机制修复。
2. **真实公司泛化被替换为合成公式演示。** CA-302 的原三公司/跨 root/既有与缺失/补新修订全流程，最终测试复用 `_zijin_document()` 代表第二矿企及非矿；direct_growth 的 100→110→121、reconcile(x,x)、长度/状态检查可通过而没有新增真实公司证据。ZR-609 在卡中明确采用“合成紫金结构”，因此可称结构演示，不能称真实紫金预测完成。ZR-709 的 realized_price 由待勾稽收入反推，再用同式计算，无法独立验证资产收入。
3. **接线义务多次延期而接受状态继续推进。** ZR-301、302 指向 ZR-303 接生产；ZR-303 最终仍 shadow 且禁止接生产；ZR-304 唯一读取模型也仍 shadow。ZR-507/508 分别是纯内存队列及调度决策器，持久化留给“后续卡”；当前 revenue `source_preparation.py` 只向进程内队列 enqueue，角色计划名为 producer_events，不能证明 producer 实际执行。来源未审查时先抛异常，失败路径未产出后续成功路径的 reuse receipt。
4. **总体验收变成状态自证。** CA-201 吸收 CI 项却禁止改 workflow，9 项 ci-gap successor 仍指自己；CA-301 不再实际执行三仓 clean replay；CA-305/ZR-1105 通过 accepted 状态和 receipt 存在/哈希形状回答六个用户目标。完整映射存在有价值，但映射不是后继目标兑现。
5. **真实数据迁移和部署被作为测试之外的动作，未被总完成门保留。** FC-901 的 11 个合成测试通过不代表 7,718 个 legacy artifact 已绑定；FC-906 明确只做小样本，历史遗留保留是公开设计边界。ZR-1002/1003/1006/1008/CA-304 的最终卡均明确排除真实激活、broker 处理、cutover 或删除，仍解锁收官卡。这里应记录部署欠账，而非指责相应单测无效。

## 当前代码反例及已经修复的边界

| 历史承诺 | 当前独立证据 | 判定与边界 |
|---|---|---|
| 早期 F-01：验证后才能签 publication receipt | `revenue_core.py` 153–169 先 `validate_published_forecast(result,data)` 后 receipt | 顺序问题已修复，不能沿用旧 F-01 当作现状 |
| 早期 F-02：无 input 验证弱于有 input | 结果内嵌 input；`revenue_report.py` 1239–1253 dispatcher 自动使用内嵌 input；当前 schema 无 input 拒绝 | 当前强验证接线存在；仍须区分“模型按输入一致”与“输入/工具记录来自真实外部事实” |
| F-11 后继：host_signed 代表真实可信签名 | `attestation_capability()` 仅判断环境变量所指文件存在；把本次普通 Python 源文件设为 provider，即得到 host_signed、source receipt 无 signature，正式验证接受 | 当前反证。签名存在时 Ed25519 白名单验证有效，但状态未绑定 provider 实际调用/签名 |
| ZR-710：完整发布事务无孤儿、可恢复 | 当前 CLI 注册 registry 后才写 JSON/Markdown；注入 output 写失败→exit 2、registry 新增 1、output 不存在 | 单文件 tmp/fsync/replace 有效，整组发布事务未完成。原“幂等”被卡改为重跑恰 2 条 registry（每次 1） |
| ZR-605：MineYearOperation 完整运营合同 | helper 无单位、basis/asset identity；volume=1000, grade=2 得 saleable=2000，inf 也通过 | standalone helper 合同不足；不等于当前 31 个注册模型都缺 finite 门 |
| ZR-606：commercial terms 收入正确 | tc/rc/premium 被描述为 per-unit 却直接加减 scalar；payability 校验但未使用 | 需明确价费计量单位、付费金属基数、结算条款和币种，再与业务模型接线 |
| ZR-712：wrong-record/plug 六类反博弈全杀 | helper 对 record_sha 仅检查非空，`not-a-sha` 通过；inf 权重通过 | standalone helper 当前反证；formal 引擎另有 accuracy 验证，未证明 formal 绕过 |
| ZR-713：mine/segment/group 三层 rolling-origin | mine-volume 路径算实际量、wape=None；窗口数不等于不同 origin | 公式计算或不同哈希不等于真实预测误差/校准能力 |
| ZR-205：总调用预算严格限制整个流程 | filing 独立模拟时钟：10 秒预算，首调用消耗 9 秒报 busy，仍使用旧 remaining 退避 5 秒，到 14 才拒绝 | 是当前函数的隔离反例；不是生产墙钟 14 秒观察，也不是第二次下载调用 |
| FC-904：处理后产物真正消费、缺什么只重算什么 | 当前 `prepare_source` 选择 role、列 producer DAG；没有打开 artifact 或执行 producer | `producer_events` 是计划，历史 parser/LLM 计数不是当次运行；原件 SHA/size/containment 校验确实存在 |

命令、stdout/stderr、退出码、测试文件哈希见 `logs/*manifest.json`。本轮隔离回归：31 passed（CA-206/302/FC-904，排除生产 missing-document 场景）；模型 97 passed + 216 subtests；publication/attestation 37 passed。反例脚本均只写本审查 scratch；未下载、未触发生产 catalog writer、未修改产品代码或配置。

## 独立审查记录本身也有有效反证

company-wiki FC-703 r1 能发现 SELECT 的字段投影被误当 WHERE 过滤；FC-802 r2 能发现测试定义在 `unittest.main()` 后且未被收集，并由 r3 真正补上杀突变；FC-705 r1 发现 open window 使关闭门不可达，r2 修复 completed-only。以上应列为已发生的有效审查与修复，不能再把旧版缺陷报成当前缺陷。反复问题的另一原因是 reviewer 只被要求核对缩小后的 card；minor/info 缺口未成为阻断后继，特别是生产接线、真实 root、自然时间和独立数据 oracle。

## 建议的后续实施顺序（本轮不实施）

1. 冻结原始用户目标的原子义务，记录每次卡片缩范围与批准出处；未部署/未执行/待自然时间必须保留独立节点，禁止吸收成 accepted。
2. 修复验收真值：区分规划、排队、调用、产物、消费成功计数；保留命令 argv/stdout/stderr/退出码/收集与 skip 数，并与当前三仓 HEAD、配置、安装副本、样本哈希绑定。
3. 先通真实资料链：现有材料零下载→review/normalize/bundle→forecast；缺材料授权下载→canonical scan/index→resolve→二次零下载。加入旧配置真实 writer 兼容性与跨外部 root 独有样本。
4. 再通财务与建模链：经营事实单位/所有权/并表/外销/内供/商业条款/FX→资产/分部/集团桥；保留结构化 gap，禁止用同来源反推参数再自勾稽作独立正确性证据。
5. 为每个模型分列“公式正确、领域边界有效、真实数据可得、真实公司可用、样本外误差改善”。31 模型本轮仅能支持前两项的有限范围；扩大行业/生命周期不能靠模型名称数。
6. 在隔离端到端链通过后做明确部署、数据迁移和回滚演练；持续自然观测的缺口由真实调度日志决定，不用合成 clock/重复报告补齐。
7. 最后由未参与实现的代理从原始义务和当前公开入口重验，汇总门消费业务结果及尚未闭合项，不能仅遍历 accepted 状态。

完整账本在 `item_ledger.jsonl`、`checklist_ledger.jsonl`、`model_ledger.jsonl`、`wiki_fc_document_ledger.jsonl`；各文件段落覆盖以 `source_semantic_file_manifest.json` 为准。

## R4 后继为什么仍不能代表原用户链路完成

R4 的独立复审确实抓出了多轮真实错误，不能简单说“审查无用”。问题在于各包的已接受范围与总目标之间仍留有明确空隙。

| 条款与历史变化 | 这次独立判断 |
|---|---|
| B02 原要求字节 hash 硬门，因 4 个冻结 fixture 字节与声明 hash 不符，S10/S11 经 owner 同意保留 metadata fallback；B03 另建硬字节 API | 授权缩范围合法；B03 的 18 个测试支持 API，但 consumers 接线留给 C，不能将 B 的 accepted 当完整读取链已闭合 |
| B04 移动保持身份；同路径覆盖无其他副本则旧内容不可读，S12 明确接受限制 | metadata handle 可存在不等于旧版本 bytes 可读取；需在实际消费时显式 unavailable |
| B06 新增 qualification，preview 被旧 capture-complete 门先拒而不可达，blocked 为旧 client 可忽略的加法字段 | wire compatibility 与许可语义不同。RF 还忽略 qualification / bundle_usable，必须跨仓按用户入口验证 |
| B08 机制测试、B.AR 12 个样本、66 查询、6 raw /18 artifacts 校验，后续孤立第五 root | 有真实观察价值，样本分母和角色必须保留；第五根的 1 行小 fixture 不是四真实根同时共存；0/66 sections 不能写成已处理全文可用 |
| B10 原“单一读取链”落为 metadata JSON 读取器收敛 | malformed-row 和异常逐文档处理确有修复；它没有自动接上字节提供、artifact 实际读取与 forecast 参数化。普通 SectionQuery 还有独立临时 SQLite 反例 |
| mutation 曾选 Protocol 第一同名函数、空 JOIN、等价替换、语法错误、重复字典键、失效锚点与无变化替换 | 每次 kill 只证明被实际改变的那个语义。后继自检修复值得保留，旧 kill 数不能继承为全目标证明 |
| R5 Python 属性看不到 Dropbox 云标志，后改用 PowerShell/fsutil 和 allocation | 仪器交叉核验是实际进步；3 个已驻留小 sidecar 的读取不等于真实未驻留大型 PDF 水合路径已验证 |
| GP 初始注册/参数不对，9 月后补 `--run-daily`、triplet、实际触发及阻断 | 旧 9/5 反证不能复制成当前 bug；但未来预计日期、人工 Monthly 和同周期重复 Weekly 仍不能替代所需自然窗口 |

上述条目逐源详见 `r4_document_ledger.jsonl`、`additional_document_ledger.jsonl`、`prose_clause_ledger.jsonl` 和完整发生记录。

## 同期变更边界

审查期间，另一个任务提交了 company-wiki `f39bd5a64224cd0c7aa098f23f64bf3811fa8939`，修改 `normalizer.py` 第二处 `fetchall` 的异常处理（51 行新增、6 行删除）并新增故障测试；不是本代理的修改。已只读查看该 diff 和对应 R4 新正文。当前代码具备 retryable / retry-exhausted 逐文档处理；结果登记失败及批级读取仍按设计硬停，不再把旧未守卫现象列为当前缺陷。记录事务原先借用 ingest 探针的错证据也已由新直接注入补正。

三份 R4 文档在本轮变化：`evidence/barfix-product-fixes.md`、`findings.md`、`progress.md`。账本同时保存冻结 inventory hash 与新 reviewed hash，未覆盖旧版本身份。新生产 scan 失败报告来自另一任务对生产 `scan_runs` 的读取，不能归因于本审查。当前 raw/config/policy 的全局完整性由主审另行核定。本代理只创作审查材料和隔离验证脚本，未创作产品修复、未下载、未运行生产 writer。

## 交付索引与后续验收

- `source_semantic_file_manifest.json`：313 个文件逐个全文和语义状态。
- `source_semantic_ledger.jsonl`：每段原文、原行号、双版本 hash、对应人工结论。
- `item_ledger.jsonl`：262 原工作单元定义、全部子条件和后继判断。
- `checklist_ledger.jsonl` / `model_ledger.jsonl`：776 叶和 31 模型。
- `prose_clause_ledger.jsonl` / `deep_clause_ledger.jsonl`：原承诺收缩、当前反例及修复后边界。
- `wiki_fc_source_blocks.jsonl`：额外 29 份 FC 的原始 required/rejected/accepted，不把旧 PASS 继承为当前通过。
- `logs/`：本轮已执行验证的命令、退出码、stdout/stderr、测试文件 hash；其他历史运行没有冒充本轮重跑。

下一步由主审把 84 份分派文件及全局快照并入总账，并独立抽核语义分组、并发版本和最终实施步骤。本分区不存在隐藏的待读正文；任何当前功能缺证已经以明确结论保留，须由后续实施完成相应业务验收，而不是再补一份“全绿”摘要。
