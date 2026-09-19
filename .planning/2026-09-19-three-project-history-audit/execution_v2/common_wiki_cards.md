# Company-wiki 执行卡：配置、注册、工件、审核与精确维护

状态：**planned；12 张卡尚未释放执行**。本轮仅制定计划，没有产品实现、测试运行或生产写入。先读 [统一执行协议](<C:/Users/郑曾波/Projects/revenue-forecast/.planning/2026-09-19-three-project-history-audit/execution_v2/START_HERE.md>) 与 [独立验收与接续](<C:/Users/郑曾波/Projects/revenue-forecast/.planning/2026-09-19-three-project-history-audit/execution_v2/review_and_handoff.md>)。本文权威，JSON 用于调度；任何差异先更正，不择宽松版执行。

## 共同前提

源码锚点是本次只读观察，不是未来安装版本保证。I-00-B 为每 attempt 冻结绝对 isolated paths、解释器、子进程加载模块、配置/policy/worker 状态、允许写目录、输入 hash、完整 argv 和 expected rc。任何模板仍有 <>、null 或 unbound 均不可运行。

D-W 条目给出建议方案与必须冻结的决策字段，由具名高级 reviewer 在该 attempt/decision.md 明确选择、反例、兼容/回滚后才释放。弱模型不得自行选 schema/事务/安全审核机制。新的接口未冻结不是现有可运行命令。

本轮已先用 CodeGraph context/search 找结构，再读已定位文件。部分索引的旧行号/代码片段已漂移（scanner/resolver/prompt_injection 等），所以按当前字节读取得到下面路径/行/sha256；禁止以旧节点片段覆盖现代码，也未运行 index 重建。

每卡输出 execution_runs/<card>/<attempt>/；该路径相对总计划目录，不能覆写 reviews/、audit_review/ 或此前 attempt。相对证据路径在 JSON 中以 RF workspace 为基准，../company-wiki 是相邻只读仓。新 tests/harness 均需 I-00-B 绑定；未存在的命令不假装已验证。

顺序 I-01-A→I-02-A/B/C/D/E；I-05-A 与 I-06-A 可在独立文件范围并行，I-06-B 依赖两者；I-05-B→I-05-C 在之后。I-15-A 可独立。卡片接受只解锁所述范围，不证明 I-07 真实公司链或预测准确性。

CW/RF/FF 分别指 company-wiki/revenue-forecast/filing-fetch 的**本次隔离 checkout**；当前源码锚点指原仓只读观察。

- 本卡全为隔离实现与验收；provider disabled。真实市场端到端由 I-07 另验。
- 生产 config/runtime_policy/worker_control/raw/catalog、旧审计证据、主规划文件均不可写；不启动/恢复后台 worker，不做生产 prune。
- 不补假 capture/review/schema/来源字段，不改旧 PASS 状态作为新验收。
- 保留当前有证据的修复；若修改前已经满足固定 oracle，走无需产品修改的复验，不造 RED。
- 同一公共 schema/文件单 owner 顺序实施。I-02-B 与 I-04 的错误信封先协调，I-05/I-06 共用 source_preparation 不并发写。
- 失败停止本卡后保留 scratch、raw、journal 和日志；回滚只撤本卡差异。两次相同失败按 START_HERE 停盲重试。

每卡共同证据：binding.json、decision.md、修改前冻结 oracle.md、commands.json、完整 stdout/stderr/raw_returncode/expected_returncode、diff 与前后 hash、逐 case_results.json、handoff.json、独立 reviewer 的 review.md。不能用 passed 数或文件存在自签。

## 高级 reviewer 先冻结的决定

以下为明确建议与待签决定，不是弱模型自由设计项。reviewer 如选择不同方案，须先更新受影响卡的 oracle/兼容/恢复表，再释放卡；不能一边实现一边移动预期。

### D-W01

Owner：company-wiki 架构 reviewer + filing 消费 reviewer。影响：I-01-A、I-02-A。

建议：使用一个 effective-root/activation 解析结果同时驱动 doctor 与真实 scan。保留 adapter-declared root 强制适配器规则、无 adapter 的 legacy 行为仅在批准的 legacy 状态允许；生产形状 true/true/true/false + 三根缺 adapter 必须报不一致。不得以关闭 v2 或打开 legacy bridge 作为修复。三个 adapter ID 已实现，但 Dropbox 目录真实布局不能猜成 sidecar；先以只读样本核对能力并在副本给出逐 root 映射。

必须明确：

- root/route 优先级及每个当前 root 的 adapter/profile/version 兼容表
- 合法 activation 组合表与未实施 adapter 的错误
- write target 与 read_only/admission profile 的冲突判据
- doctor、scan 和 resolver 接受的单一结构及版本

### D-W02

Owner：canonical writer 单一实施 owner + 独立恢复 reviewer。影响：I-02-A、I-02-B、I-02-C、I-02-D、I-02-E。

建议：演进现有 AcquisitionJournal 和唯一 canonical writer，显式区分 fetched/raw_saved/provenance_saved/registered/qualified/resolved；此为待冻结的语义阶段，不宣称已有这些枚举。恢复键至少绑定 request、provider/document identity、bytes hash、目标 root 与 policy。恢复只消费已证明成功的持久阶段，不能由文件存在推定 capture 合法或由 scan 返回推定注册完成。

必须明确：

- ScanReport 完成状态、每根结果、目标 hash/location 结果的确切 schema
- 错误信封版本/字段映射与 N/N-1；上游 code/retryable/request_id/cause_chain 保留规则
- journal 的持久化/事务边界、损坏尾行处理、幂等键、锁与重启算法
- raw 无 sidecar 时可用的持久 download receipt；无可靠 receipt 的拒绝规则
- 已存在 raw 注册的具体 API/CLI 与允许调用者；是否延伸现有 ensure 入口
- 兼容性测试与阶段对应恢复操作表

### D-W05

Owner：wiki producer owner + revenue 消费 reviewer。影响：I-05-A、I-05-B、I-05-C。

建议：保留当前 ArtifactHandle schema 1.0 及已有 producer 字段修复，不因旧数据失效无端升级 schema。对历史无来源绑定的数据只能重算/可证明回填，不填猜测字段。取消活动计算图对冗余 catalog markdown producer 的必需依赖：normalized 已是可读 markdown，summary/sections 直接依赖适用 normalized；历史 markdown 工件仅兼容读取。consumer_analysis 由 revenue owner 提供。选择、待生成计划、读取事件、真实调用事件分别命名。

必须明确：

- 角色适用性及新活动 DAG 的确切映射、旧 DAG/markdown 的兼容说明
- schema 权威位置、冲突优先/拒绝规则、旧工件迁移准入
- raw 与 artifact 的 verified-read API（不能把原件 SourceHandle API 生硬用于 ArtifactHandle）
- 事件 schema：role/artifact/hash/bytes_read/调用 ID/尝试次数/失败归属；成功读取的必要条件
- 每个需求角色对应的现有 producer 入口、是否存在、缺失时返回值；LLM 能力缺失的阻断语义

### D-W06

Owner：wiki 来源审核 owner + 安全 reviewer + RF 消费 owner。影响：I-06-A、I-06-B。

建议：两仓现有 DemandQueue 都是内存实现；选定 company-wiki 单一持久需求 owner，RF 只提交/查询，不再增加第二套持久队列。先记录需求，再保持 not_reviewed 阻断。只允许真实执行审核方法形成回执；检测命中由 reviewer 决定隔离或有证据地 detected_and_ignored。显式同步消费某一需求不能自动恢复后台 worker。

必须明确：

- 现有 catalog/store 扩展的确切表/迁移/API，而非令弱模型自行挑 DB/队列框架
- 需求幂等键（source bytes、审核 policy、角色集合、原请求绑定）及跨进程 claim/lease/完成规则
- 审核方法、完整输入边界、提取器/工具版本、证据内容、reviewer 身份与 source/policy 双绑定
- 可执行审核/消费命令、安装解析及原请求恢复接口；该接口目前不得假装已存在
- 失效/失败/注入命中/缺文本/取消的状态与恢复表；trusted reviewer 与文档内容严格区分

### D-W15

Owner：存储维护 owner + 独立数据恢复 reviewer。影响：I-15-A。

建议：复用现有 archive/prune 模块，但 prune 绑定一份可验证 archive 集合清单，不以目录年龄为授权。每一待删 span 必须能从归档恢复且与当前 row/source identity 对应；仍 active、归档后新增或变更行全部保留。空/损坏/过期但无内容目录一律不能删除。

必须明确：

- archive manifest 的字段/版本、catalog 身份、行 ID/行摘要/文件 hash/完成时间及完整性证明
- 保留期从经过验证的完成时间计算，固定时钟接口
- dry-run 计划 hash 与 apply 的再核查/并发 TOCTOU 规则
- 精确集合分批提交、崩溃 receipt、重复 apply、恢复到 scratch 的具体协议
- 旧无 manifest 归档如何验证升级；禁止猜测补造证明

## 已核查入口与命令模板

这些是本轮读过的源码/测试入口，**不是本轮重跑通过清单**。所有 `binding_status=unbound`；I-00-B 替换路径、核实所有导入/子进程及用例 nodeid 后才执行。pytest 的 basetemp 必须是新建的本次目录，不能指向旧证据。保留 PYTHONDONTWRITEBYTECODE=1 与隔离依赖路径；不能从默认安装副本悄悄加载产品。

### CMD-W01

工作目录：绑定的 company-wiki。已读入口：

- `scripts/config_doctor.py:diagnose(config_path, project_root, filing_fetch_config)`
- `tests/test_config_doctor.py`

argv 模板：

```json
["<bound-python>","-X","utf8","-B","-m","pytest","-p","no:cacheprovider","--basetemp","<fresh-command-run>/pytest","tests/test_config_doctor.py"]
```

- 现有 doctor CLI 只有 --filing-fetch-config，没有 --config；禁止编造 config_doctor --config。隔离新形状调用 diagnose API 或先由获准卡扩展 CLI。
- 旧 test_e2e_f03_second_directory_root_fails_fast 反映旧 allowlist；新 oracle 需 D-W01 对齐，不为兼容旧期待拒绝合法第五根。

### CMD-W02

工作目录：绑定的 company-wiki。已读入口：

- `tests/contract/test_gp002_scan_v2_wiring.py`
- `tests/contract/test_r4bar10_adapter_declared_root.py`
- `src/company_wiki/source_catalog/service.py:SourceCatalog.scan`

argv 模板：

```json
["<bound-python>","-X","utf8","-B","-m","pytest","-p","no:cacheprovider","--basetemp","<fresh-command-run>/pytest","tests/contract/test_gp002_scan_v2_wiring.py","tests/contract/test_r4bar10_adapter_declared_root.py"]
```

- 现有命令只回归 forwarding/adapter declared 行为；I-01/I-02 新配置形状/目标注册案例必须另绑定新测试 nodeid。
- 不得把 dry_run 默认 v1 与真实 snapshot v2 混为同一路。

### CMD-W03

工作目录：绑定的 company-wiki。已读入口：

- `tests/contract/test_source_catalog_canonical_writer.py`
- `src/company_wiki/source_catalog/canonical_writer.py:CanonicalSourceWriter.import_staged`

argv 模板：

```json
["<bound-python>","-X","utf8","-B","-m","pytest","-p","no:cacheprovider","--basetemp","<fresh-command-run>/pytest","tests/contract/test_source_catalog_canonical_writer.py"]
```

- 现有 tests 用 tmp_path；不是已存在 register-existing/crash CLI 的证明。D-W02 冻结后新增的入口及 crash harness 必须在 I-00-B 写实参 argv 并核查。
- 本轮没有独立现成可安全直接执行的恢复/prune scratch CLI；不能编造 --repair/--resume/--register-existing。

### CMD-W04

工作目录：绑定的 revenue-forecast。已读入口：

- `tests/test_source_preparation.py:test_prepare_source_raises_on_client_failure`

argv 模板：

```json
["<bound-python>","-X","utf8","-B","-m","pytest","-p","no:cacheprovider","--basetemp","<fresh-command-run>/pytest","tests/test_source_preparation.py::test_prepare_source_raises_on_client_failure"]
```

- 不要直接跑该文件全套：test_process_red01_uses_real_subprocess_chain 未提供隔离 catalog 参数会启动真实默认链。此 node 只 mock subprocess，不能关闭跨进程错误传播卡。

### CMD-W05

工作目录：绑定的 revenue-forecast。已读入口：

- `scripts/source_preparation.py:main，已读 argparse --request-file/--company-wiki-config/--filing-fetch-root/--timeout-seconds`

argv 模板：

```json
["<bound-python>","-X","utf8","-B","scripts/source_preparation.py","--request-file","<fresh-attempt>/request.json","--company-wiki-config","<bound-isolated-cw-config>","--filing-fetch-root","<bound-isolated-ff-checkout>","--timeout-seconds","30"]
```

- 必须绑定安装模块/全部子进程配置到隔离三仓，网络 disabled 且 provider deny-on-call；仅指定顶层 config 不足证明无默认落回。
- 此模板没有 --allow-download，适合已存 raw/审核/复用；具体 request 字段用固定样本及现有 parser 绑定。
- source_preparation 当前没有受支持 review-run 命令；D-W06 将来选定接口前不可臆造。

### CMD-W06

工作目录：绑定的 company-wiki。已读入口：

- `tests/contract/test_source_catalog_artifact_handle.py`
- `tests/contract/test_source_catalog_source_bundle.py`
- `src/company_wiki/source_catalog/service.py:normalize/extract_sections/summarize/summarize_with_llm`

argv 模板：

```json
["<bound-python>","-X","utf8","-B","-m","pytest","-p","no:cacheprovider","--basetemp","<fresh-command-run>/pytest","tests/contract/test_source_catalog_artifact_handle.py","tests/contract/test_source_catalog_source_bundle.py"]
```

- 现有 fixture/validator 测试不能替代新 default-producer→bundle→实际消费案例；summary LLM 能力与 extractive summary 分开。

### CMD-W07

工作目录：绑定的 revenue-forecast audit copy。已读入口：

- `.planning/2026-09-19-three-project-history-audit/reviews/wiki_legacy/section_probe.py`

argv 模板：

```json
["<bound-python>","-X","utf8","-B","<fresh-attempt>/section_probe_bound.py"]
```

- 已逐行核查原脚本：source 为生产绝对路径，HERE 为旧证据目录且写 section_probe.json。禁止原地运行。
- I-00-B 先复制到新 attempt、把 source 替成绑定的隔离 section_query.py；确认临时 SQLite 与 JSON 输出均在新 attempt，再冻结副本 hash。
- 原探针 minimal schema 只支持修改前反例。实现后必须补充真实 catalog/源/span fixture 正例；不能删严格校验去迎合 minimal fixture。

### CMD-W08

工作目录：绑定的 company-wiki。已读入口：

- `tests/contract/test_zr507_processing_demand.py`

argv 模板：

```json
["<bound-python>","-X","utf8","-B","-m","pytest","-p","no:cacheprovider","--basetemp","<fresh-command-run>/pytest","tests/contract/test_zr507_processing_demand.py"]
```

- 只证明纯内存状态机。持久、审核执行与原请求恢复测试尚需获准实现，实际命令由 D-W06/I-00-B 冻结。

### CMD-W09

工作目录：绑定的 revenue-forecast。已读入口：

- `tests/test_fc904_artifact_selection.py`

argv 模板：

```json
["<bound-python>","-X","utf8","-B","-m","pytest","-p","no:cacheprovider","--basetemp","<fresh-command-run>/pytest","tests/test_fc904_artifact_selection.py"]
```

- 包含 selection/mock receipts，只能保留已有语义；实际读取/producer 调用必须由 W05B/W05C 新独立 IO cases 证明。

### CMD-W10

工作目录：绑定的 company-wiki。已读入口：

- `tests/contract/test_source_catalog_archive_retired.py`
- `tests/contract/test_source_catalog_prune_retired.py`
- `src/company_wiki/source_catalog/prune_retired_evidence.py:prune_retired_evidence(config,archive_root,apply=False,retention_days=90)`

argv 模板：

```json
["<bound-python>","-X","utf8","-B","-m","pytest","-p","no:cacheprovider","--basetemp","<fresh-command-run>/pytest","tests/contract/test_source_catalog_archive_retired.py","tests/contract/test_source_catalog_prune_retired.py"]
```

- 仅允许 isolated tests 内 apply；不用生产 CLI。旧固定日期与空目录期待有误，修改前结果仅是 baseline；冻结时钟及新 exact-set oracle 后再验收。
- 原 archive/prune API 可用，不存在已核查可直接恢复任意归档的 CLI；restore harness/manifest 接口由 D-W15 先定。

## 卡片


本文仅共用前提；领取具体卡见[调度表](dispatch.md)。
