# 三项目根因级改进路线图（revenue-forecast / filing-fetch / company-wiki）

编制日期：2026-08-08 │ 依据：`review_audit/findings.md`（N-01~N-11 + 历史 F-01~F-14 复核）
状态：**待批准，未实施**。批准后按本文件执行；执行期间本文件是唯一计划可信来源。

---

## 0. 总原则（不可违反）

1. **根因优先**：每个阶段必须先写明它消灭的根因；禁止只修表象。同一根因的多个表象
   （N-01 在 result/snapshot/invest 三处的表现）必须在同一阶段一次性闭环。
2. **RED 先行**：每个行为修复必须先落一个能稳定复现缺陷的失败测试（攻击即测试），
   确认红，再最小修复，再转绿。攻击探针从 `review_audit/` 升级为产品测试资产。
3. **Fail closed**：无法验证时必须拒绝/降级，不得静默放行；所有门禁 exit≠0 必须阻断。
4. **可执行验收**：每个阶段的"完成"定义 = 验收命令全绿 + 证据写入 progress.md。
   禁止"标题 completed、清单未勾选"的伪完成（N-02/F-11 教训）；禁止按现状下调目标
   （N-07 教训）——要改目标必须走用户裁定并留痕。
5. **不信任自述**：文档声称、计划状态、receipt 声明一律需要机器复验（动态发现能力，见 §3）。
6. **单一 owner、单一可信状态**：filing 获取、配置、安装副本、版本发布各只有一个权威来源。

---

## 1. 根因分析（本次审查 + 两轮历史审计的共性结论）

| 根因 | 派生问题 | 证据 |
|---|---|---|
| RC-1 信任链只靠自哈希，缺少"输入锚点绑定"与"外部可查询的发布登记" | N-01（嵌入输入可替换、锚点可冒用、穿透 invest）、历史 F-02 | probe_embedded_input / probe_anchor_swap / probe_invest_cross 全部动态复现 |
| RC-2 验收靠人写状态，无可执行完成标准 | N-02（Phase 10 伪完成）、F-11（Phase 8 伪完成）、N-07（覆盖率目标被悄悄下调）、task_plan 164[x]/387[ ] | commit 89b2d0c 自认 "never wired in"；阈值 40% vs 计划 90% |
| RC-3 旧实现"弃而不删"，双 owner 代码层存活 | N-03（filing_acquisition 库级下载仍在）、F-04 复发风险 | filing_acquisition.py:1931-1985 完整下载路径实测可导入 |
| RC-4 环境不自包含：测试/会话可写穿生产状态，安装副本无强制同步 | N-05（生产配置被夹具污染）、N-06（.agents/.codex 漂移）、F-08 | 实测 config/source_catalog.yaml 为 fake JSON；sync exit 1 |
| RC-5 attestation 只有结构契约，无能力门与签名机制 | N-04/F-11：自填 host_receipt 可出 formal | 全库无 trusted/capability 判断；compliance-contract 自认 host trust |
| RC-6 问题发现靠人工审计轮次，无常态化对抗测试与漂移探测 | 每轮审计都发现新绕过（Critical-1→F-02→N-01 同族三代） | 三代绕过均为"改结果+重签哈希"变体 |
| RC-7 版本/发布纪律松弛 | N-08（3.10.0 挂大量破坏性 Unreleased、CHANGELOG 自相矛盾）、F-03/F-05 | 实测常量与 CHANGELOG |

---

## 2. 阶段设计

> 依赖约定：R1 是其它一切的地基（P0）；R2/R3 依赖 R1 契约面；R4-R7 可并行；
> R8 最后（文档对齐必须在实现之后，禁止反向适配）。所有阶段 RED 先行。

### R1（P0，根因 RC-1）：输入锚点绑定 + 发布登记处（Trust Anchor）

目标：让"input_sha256 锚点"从自报变成**可机器复验、可外部查询**的事实，一次性关闭
N-01 及其全部变体，并为 invest-* 提供拒绝伪造的结构性依据。

#### R1.1 输入绑定不变式（binding invariant）

- 文件/符号：
  - 新增 `scripts/trust_anchor.py`：唯一函数 `verify_input_binding(result) -> None`，
    要求 `result` 含 `input_document` 时 `canonical_sha256(input_document) == input_sha256`；
    `validate_published_forecast(result, data)` 内**先**对实际使用的 `data` 计算哈希并要求
    等于 `result["input_sha256"]`（验证器从此绑定"实际验证了什么"，而不是结果声称什么）。
  - `scripts/revenue_report.py::_validate_forecast_output`：current schema 一律调用
    `verify_input_binding`；无 `input_document` 且无 `data` 的 current-schema 工件直接拒绝
    （legacy read-only 路径除外，且 legacy 路径显式标注 `binding="not_verified"`）。
  - `scripts/revenue_backtest.py::validate_snapshot`：改为复用同一 `verify_input_binding`
    （删除本地重复实现，防止两处规则漂移）。
  - invest-core `scripts/invest_contracts.py::validate_revenue_forecast`：强路径前调用
    revenue 侧 `verify_input_binding`（通过 runtime 导出），绑定失败即
    `InvestmentArtifactError`。
- RED 测试（先红）：
  1. `tests/test_output_report.py`：移植 probe_anchor_swap D2——膨胀参数重跑引擎后锚定
     合法哈希，`validate_forecast_output` 必须 REJECTED（当前 ACCEPTED，红）。
  2. 同文件：D1 整体替换嵌入输入必须 REJECTED。
  3. `tests/test_backtest.py`：snapshot 路径同一攻击保持 REJECTED（回归钉住）。
  4. invest-core `tests/test_revenue_adapter.py`：移植 probe_invest_cross——伪造工件
     `validate_revenue_forecast`/`adapt_revenue` 必须拒绝（当前 ACCEPTED，红）。
- 验收命令：
  ```powershell
  python -m pytest tests -q                      # revenue 全绿（含 4 个 RED 转正）
  python review_audit/probe_anchor_swap.py       # D2 行必须打印 REJECTED
  python review_audit/probe_invest_cross.py      # invest 两行必须 REJECTED
  ```
- 迁移/回滚：schema 不变、字段不变，纯验证收紧；旧合法工件（绑定自洽）不受影响。
  回滚 = revert；探针回到 ACCEPTED 即风险复活，必须阻断发布。

#### R1.2 发布登记处（Publication Registry，外部锚点）

- 动机：R1.1 之后，攻击者仍可"自造一份自洽工件"。要区分"用户批准的输入 X"与"攻击者
  输入 Y"，需要一个工件之外的权威记录。这是从根上解决"锚点冒用"的唯一途径。
- 文件/符号：
  - 新增 `scripts/publication_registry.py`：append-only JSONL 登记
    `artifacts/registry/publications.jsonl`（行：`{registered_at, input_sha256,
    result_sha256, receipt_sha256, engine_version, schema_version, publisher,
    input_summary_sha256, note}`），写入即 fsync，禁止改写/删除（create-once，
    文件级只读属性 + 写前校验）。
  - `run_forecast(mode="formal")` 成功后**必须**登记；登记失败则整个发布失败（fail closed）。
  - `revenue_backtest.py create`：登记 snapshot_id ↔ input_sha256。
  - 新增 CLI：`python scripts/publication_registry.py lookup --input-sha X`
    （返回该锚点的全部发布历史）；`audit`（检测同一 input_sha256 对应多个不同
    result_sha256 的冲突、或 result 声称的锚点从未登记）。
  - invest-core：`adapt_revenue` 增加**策略开关** `require_registered_input`
    （默认 ON，可配置降级并留痕）：锚点不在登记处 → 拒绝。
- RED 测试：
  1. 未登记工件（绕过 run_forecast 手工构造）→ invest adapt 拒绝。
  2. 同一 input_sha256 出现两个不同 result_sha256 → `audit` 报冲突（exit≠0）。
  3. 登记文件被篡改（改一行）→ 行级哈希校验失败，lookup 报损坏。
  4. 登记处缺失/不可写时 run_forecast formal 必须失败（不允许静默跳过）。
- 验收命令：`python -m pytest tests -q`；`python scripts/publication_registry.py audit` exit 0。
- 迁移/回滚：现存历史工件无登记记录 → invest 策略提供 `legacy_unregistered=read_only`
  兼容档（不得创建新 leaf artifact）。回滚 = 策略开关降级 + revert。

#### R1.3 跨仓库伪造 conformance 链（固化 R1）

- 在 invest-framework 增加三跳 fixture：revenue 生成 → 攻击重签 → revenue→invest-core→
  framework 三处必须全部拒绝（audit_review 阶段 A3 的原计划，一直未实施）。
- 该 fixture 作为共享测试资产，三仓库 CI 各跑一遍（见 R6.3）。

### R2（P0，根因 RC-5）：Attestation 能力门 + 主机签名契约

目标：把 F-11/N-04 的"host trust 文档声明"变成**可执行的能力门**，并给出真正的主机签名
路径，消灭"自填字符串即 formal"。

#### R2.1 runtime 能力门（fail-to-draft）

- 文件/符号：
  - `scripts/revenue_core.py`：新增 `attestation_capability()`——读取环境
    `REVENUE_ATTESTATION_PROVIDER`（指向外部签名器命令）；无可用签名器 →
    `run_forecast(mode="formal")` 拒绝，只能 `mode="draft"`，或 formal 但
    `attestation_status="unattested"`（**invest-core 默认拒绝 unattested**，策略可配）。
  - receipt 增加 `attestation_status ∈ {host_signed, unattested}` 字段（schema 3.7，见 R7）。
- RED 测试：无签名器环境请求 formal+host_signed → 拒绝；unattested formal →
  invest-core 默认拒绝；策略降级必须显式参数且写入 receipt。
- 验收：`python -m pytest tests -q`；新增 attestation 对抗套件全绿。

#### R2.2 主机签名器参考实现（最小可信根）

- 新增独立小工具 `tools/host_signer/`（独立进程，用户手工运行，agent 无法直接调用）：
  - 输入：工具事件日志（tool/action/request_hash/response_hash/timestamp 的 JSONL）；
  - 用 Ed25519 私钥（用户生成、文件权限保护）对规范化事件哈希签名，输出 host_receipt
    扩展字段 `signature` + `public_key_fingerprint`。
  - `validate_host_receipt`（contracts/evidence.py）升级：有 `signature` 字段时必须用
    受信公钥集（config 白名单）验签通过；无签名 → 按 R2.1 能力门降级。
- RED 测试：伪造签名（错密钥/改事件后旧签名）→ 验签失败；公钥白名单外的签名 → 拒绝。
- 回滚：签名器纯增量；关闭能力门配置即回到现状（但必须同步 invest 策略）。

### R3（P0，根因 RC-3）：filing 所有权终局收敛

目标：代码层消灭第二 owner，使"唯一 canonical owner"成为结构事实而非文档声明。

- 文件/符号：
  - `scripts/filing_acquisition.py`：删除 `AcquisitionManager`/`AdapterRegistry`/
    `CanonicalSourceWriter`/subprocess 适配器与 `resolve_filing` 下载能力；仅保留
    测试 fixture 所需的纯数据构造函数，文件改名为 `tests/fixtures/legacy_filing_data.py`
    （移出 scripts/，发布 manifest 不再包含）。
  - `tools/sync_installations.py` manifest 同步剔除该文件；所有安装副本清理。
  - 新增结构守卫测试 `tests/test_single_owner_guard.py`（AST 级）：
    1. `scripts/` 下除 `filing_fetch_client.py` 外不得出现 subprocess 下载适配器模式
       （StockInfo/dayu CLI 调用特征）；
    2. 不得存在第二个 `resolve_filing` 公开符号；
    3. SKILL.md/references 不得引用旧入口（文档守卫，扩展现有 test_skill_documentation.py）。
- RED 测试：先写守卫测试（当前必红：旧 owner 仍在），再删除，转绿。
- 验收：`python -m pytest tests -q`；守卫测试绿；`python scripts/filing_acquisition.py`
  路径不存在（ImportError/文件缺失）。
- 回滚：git revert；fixture 数据保留在 tests/ 不受影响。

### R4（P1，根因 RC-4）：环境与安装不变性

目标：生产配置、安装副本、测试写路径全部纳入 fail-closed 防护，N-05/N-06 类问题
"发生时即报警"，而不是等下一轮审计。

#### R4.1 生产配置完整性（company-wiki）

- 新增 `scripts/config_doctor.py`：校验 `config/source_catalog.yaml` 是合法 YAML（拒绝
  JSON 单行夹具）、schema 字段齐全、`catalog_dir` 解析后必须存在且含
  `security_master/*.json`、roots 路径必须绝对/可解析；异常 exit≠0。
- 立即修复：恢复 `config/source_catalog.yaml` 到 git HEAD 版本（当前被污染，N-05），
  并把恢复前后哈希记入 progress.md。
- 测试写路径守卫：company-wiki/filing-fetch 所有会写 `source_catalog.yaml` 的测试必须
  使用 tmp 目录夹具；新增守卫测试断言测试套件运行前后生产配置文件哈希不变
  （conftest session fixture，改动即红）。
- filing-fetch `_wiki_available()` 升级：config 存在 + config_doctor 通过才跑 live 测试，
  否则 skip 并注明原因（N-05 的 skip 缺口）。

#### R4.2 安装同步强制门

- `tools/sync_installations.py --check`（默认三目标）加入：
  - revenue pre-commit（pytest/E2E 之前，漂移直接阻断提交）；
  - revenue CI（quality.yml 新增步骤）；
  - filing-fetch 等价工具（当前 filing-fetch 无 sync 工具，需移植同一实现，参数化 skill 名）。
- 安装副本自报 manifest：skill 运行时入口（filing_fetch_client/revenue_forecast CLI）
  `--version` 输出自身安装目录 manifest 哈希，便于使用中肉眼发现漂移。
- RED：人为改动一个安装文件 → pre-commit/CI 必须红。

#### R4.3 会话级配置卫生（流程 + 工具）

- `tools/session_checklist.md`（revenue）与 company-wiki AGENTS.md 增加硬性收尾项：
  会话结束前 `git status` 必须解释每一个未提交的 config 变更；无法解释 = 事故，
  立即恢复并记录。
- company-wiki worker 控制面板（source_catalog_control.cmd）菜单增加"配置体检"
  （调用 config_doctor），把动态发现能力交到用户日常入口。

### R5（P1，根因 RC-2）：可执行验收与计划治理

目标：让"completed"只能由机器证据支撑，伪完成在提交时即失败。

- 新增 `tools/verify_plan_claims.py`：
  1. 解析 task_plan.md 的 `状态：completed` 声明；
  2. 每个 completed Phase 必须在 `progress.md` 有对应证据块（测试命令 + 通过数 + 日期），
     否则报"无证据完成声明"；
  3. 统计 `[x]/[ ]` 比例，completed 段落内未勾选项 > 0 时要求显式豁免说明；
  4. 输出机器可读报告，进 CI（revenue 仓库）。
- 结构目标可执行化：把 Phase 10 类结构承诺转成测试——
  `tests/test_structure_targets.py`：声明每个模块的行数上限/职责边界（例如
  revenue_core ≤ 2500 行，或拆分完成前该测试显式红着并在 task_plan 标注"未达成"），
  禁止无声超标（N-02：3922 行无人拦截）。
- 球门移动留痕规则：任何阈值/目标变更（如 coverage 阈值）必须在 CHANGELOG 单列
  "目标变更"条目并给出理由；verify_plan_claims 对比计划原文与实际阈值，不一致即红。

### R6（P1，根因 RC-6）：常态化对抗测试与动态发现能力

目标：把"审计轮次驱动"的被动发现，变成"每次提交驱动"的主动发现。

#### R6.1 产品级对抗套件（攻击即测试）

- 新建 `tests/adversarial/`（revenue），把 review_audit 全部探针转正为常驻测试：
  - `test_rehash_attacks.py`：概率/目标/敏感性/禁止字段四类原始变异（已有，保持）；
  - `test_anchor_attacks.py`：D1/D2/D3 锚点攻击（R1 的 RED 测试转正后归此）；
  - `test_receipt_attacks.py`：无 VerificationContext 自签、context 伪造、gate_ids 虚报；
  - `test_attestation_attacks.py`：自填 host_receipt、伪签名（R2 后）。
- 规则（写入 AGENTS.md/SKILL 维护契约）：**任何新增可信声明（新 gate/新 receipt 字段/
  新"不可绕过"承诺）必须同提交附带至少一个攻击测试**，否则 CI 拒绝（用测试命名约定
  + verify_plan_claims 检查）。

#### R6.2 模糊变异巡检（动态发现）

- 新增 `tools/mutation_patrol.py`：对 golden fixture 结果做系统化变异
  （字段删除/类型替换/数值缩放 ±5%/±50%/哈希重签/嵌入输入交换/顺序打乱，
  每类 N 个样本，固定种子可复现），对每个变异样本运行全部验证入口
  （validate_forecast_output / validate_snapshot / invest validate_revenue_forecast），
  统计"接受率"；任何**语义类变异被接受**即 exit≠0 并输出样本。
- 进 CI（每日定时 + push 触发可配置）；输出趋势报告存 `artifacts/mutation_reports/`。
- 这是本次 N-01 的教训制度化：三代绕过（Critical-1→F-02→N-01）都是同族变异，
  模糊巡检可以在下一次变体出现时自动捕获，而不是等人审计。

#### R6.3 跨仓库 conformance CI

- R1.3 的三跳伪造 fixture 在 revenue/invest-core/invest-framework 三仓库 CI 各跑一遍；
- filing-fetch↔company-wiki 契约版本矩阵测试（identify/resolve/ensure schema 版本
  组合表）作为共享 fixture，防上游契约漂移（filing-fetch 已有版本检查，补矩阵测试）。

#### R6.4 漂移探测器（定时自检）

- 新增 `tools/drift_patrol.py`（可作为周任务）：
  1. 版本漂移：SKILL_VERSION vs CHANGELOG Unreleased 存在天数（>14 天报警，N-08）；
  2. 安装漂移：三目标 sync check；
  3. 配置漂移：company-wiki config_doctor；
  4. 文档漂移：test_skill_documentation 扩展断言（签发顺序/必填字段声明 vs 代码 AST）；
  5. 依赖漂移：filing-fetch 对 company-wiki CLI 子命令的契约快照比对。
- 输出单页报告；任何红项进 progress.md 并建修复任务。

### R7（P1，根因 RC-7）：版本与发布纪律

- 立即（随 R1 落地）：`SKILL_VERSION` bump 到 3.11.0（若 R1.2/R2 改变 receipt/attestation
  契约则 4.0.0，由用户裁定），forecast schema bump 3.7（receipt 新字段、绑定不变式），
  schema 3.6 转 legacy read-only；补 `references/schema-migration-3.6-to-3.7.md` +
  旧 schema fixture 迁移测试（计划规则 0.3.10 全额执行）。
- CHANGELOG 清理：删除/修正与 Phase 6 矛盾的旧 Unreleased 条目（"先签后验"陈述，N-08）；
  每个 Unreleased 条目附 commit 哈希。
- 发布检查单（`tools/release_checklist.py` 自动执行）：版本号、CHANGELOG 闭合、
  迁移 fixture、sync 全绿、对抗套件全绿、mutation_patrol 最新报告无新接受样本。
- 输入契约兼容性守卫：新增测试对比相邻版本"必填字段集合"，新增必填字段而无迁移路径
  → 红（host_receipt 事件的制度化补救）。

### R8（P2，收尾）：文档对齐与目标回填

- 依赖：R1-R7 实现完成后才允许改文档（禁止反向适配，F-12 教训）。
- 内容：compliance-contract（search_event 必填表述修正，N-04 文档漂移）、SKILL.md
  （filing_acquisition 状态、attestation 能力门、registry 说明）、company-wiki README
  （tests/e2e 名实不符：要么补真 e2e，要么改名 config 测试）、三仓库 AGENTS.md
  （新增规则：攻击测试随声明、配置收尾卫生、球门移动留痕）。
- task_plan.md 治理：按 R5 工具输出回填真实状态；历史伪完成条目改标
  `completed_in_name_only → reopened`（Phase 10 重开，见下）。

### R9（P2，根因 RC-2 遗留）：Phase 10 重开——真模块拆分（可延后，但必须立项）

- 决定：revenue_core.py 3922 行 + 空壳包（analysis/research/forecast）是持续积累
  审查债的温床。重开 Phase 10，采用"行为锁定式拆分"：
  1. 先用 golden fixture（≥5 个模型族：volume/capacity/subscriber/backlog/bank）锁定
     输入→输出 canonical hash 基线；
  2. 每次迁移一个职责组（按原 10.1 清单），迁移 = 物理移动 + re-export + 全量测试 +
     golden hash 比对（除版本字段外逐字节一致）；
  3. 完成标准可执行化（R5 的 test_structure_targets 转绿）；
  4. 禁止"抽出不接入"：每个新模块必须有调用者迁移证据（codegraph callers 非空断言）。
- 预估：独立 2-3 个会话；与 R1-R3 不冲突但建议在其后（避免合并噪音）。

---

## 3. 动态发现问题能力（横切能力汇总）

| 能力 | 载体 | 触发 | 覆盖根因 |
|---|---|---|---|
| 攻击即测试 | tests/adversarial/（R6.1） | 每次提交 | RC-1/RC-5 |
| 模糊变异巡检 | tools/mutation_patrol.py（R6.2） | 每日+push | RC-1/RC-6 |
| 跨仓库伪造链 | R1.3 fixture + 三仓 CI | 每次提交 | RC-1 |
| 计划声明核验 | tools/verify_plan_claims.py（R5） | 每次提交 | RC-2 |
| 结构目标守卫 | tests/test_structure_targets.py（R5） | 每次提交 | RC-2 |
| 单 owner 守卫 | tests/test_single_owner_guard.py（R3） | 每次提交 | RC-3 |
| 配置体检 | company-wiki config_doctor（R4.1） | 测试会话+控制面板 | RC-4 |
| 安装漂移门 | sync check 进 pre-commit/CI（R4.2） | 每次提交 | RC-4 |
| 漂移巡检 | tools/drift_patrol.py（R6.4） | 每周 | RC-2/4/7 |
| 发布登记审计 | publication_registry audit（R1.2） | 每次消费前可选 | RC-1 |
| 冲突检测 | registry 同锚点多结果告警（R1.2） | 登记时 | RC-1 |

---

## 4. 依赖图与优先级

```
R1（锚点绑定+登记处）──┬──→ R1.3（三仓 conformance）──→ R6.3（CI 固化）
                       └──→ R7（schema 3.7 发布）──→ R8（文档对齐）
R2（能力门+签名）────────→ R7 ──────────────────────→ R8
R3（单 owner）───────────→ R4.2（manifest 同步）
R4（环境不变性）          （可并行）
R5（可执行验收）          （可并行，R9 依赖其结构测试）
R6（动态发现）            （R6.1 依赖 R1/R2 的 RED 转正）
R9（真拆分）              （最后，依赖 R5 守卫）
```

优先级：R1 > R2 ≈ R3 > R4 ≈ R5 ≈ R6 > R7 > R8 > R9。
R1 必须第一个完成：在锚点绑定修复前，任何新发布工件都暴露在 N-01 攻击面下。

## 5. 立即行动（批准后第一步）

1. 恢复 company-wiki `config/source_catalog.yaml` 至 git HEAD（止血，N-05）。
2. R1.1 四个 RED 测试落盘并确认红。
3. 用户裁定：R1.2 登记处方案（本地 JSONL vs 更重的方案）与 R7 版本号策略
   （3.11.0 vs 4.0.0）、R2.1 默认策略（unattested 是否默认拒绝）。

## 6. 风险与回滚

| 风险 | 缓解 |
|---|---|
| R1 收紧验证导致历史合法工件被拒 | legacy read-only 通道保留；迁移 fixture 先行 |
| R1.2 登记处成为新的单点 | append-only + 行级哈希 + 可从工件重建（登记是索引不是来源） |
| R2 能力门影响无签名器环境的日常使用 | draft 模式不受影响；formal unattested + 显式策略降级可用 |
| R3 删除旧 owner 伤及未知调用方 | AST 守卫先红一周观察调用方；删除前进 CHANGELOG 公告 |
| R9 拆分改变数值 | golden hash 逐字节比对 + 禁止同 patch 改算法 |

## 错误记录

| 错误 | 尝试 | 处理 |
|---|---:|---|
| （本计划编制过程中无执行错误；审查取证错误见 progress.md） | | |
