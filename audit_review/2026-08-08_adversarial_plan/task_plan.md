# Revenue Forecast / Filing Fetch / Company Wiki 对抗性审查与分阶段实施计划

> 计划日期：2026-08-08  
> 审查基线：revenue-forecast `14770c1a3b90c4916d80240b72d74a73eae90743`；filing-fetch `43330550fb3ea77d36acd92e26861377564a7607`；company-wiki `325086af1a5d966f1f01b389109dd26d1b6a63bc`  
> 本轮边界：**只审查、只制定计划；未修改三个项目的产品代码、测试、配置或生产索引，未触发外部下载。**

## 1. 执行结论

### 1.1 总体判定

项目尚未完整达到本轮用户要求，也不能据现有 E2E 宣称“文件复用闭环已完成”。更准确的状态是：

- revenue-forecast 的预测核心、发布锚点、兼容登记、旧 owner 下线和模块拆分，相比前两次审查已有实质进步；现有 301 项测试全绿。但真实用户入口仍没有贯穿“多根发现 → 最新缺口 → 衍生物复用 → 预测消费”的 E2E，且产品范围 Ruff 有 185 个错误。
- filing-fetch 是较干净的薄客户端/契约层，离线基线 115 项通过、Ruff 通过；但它只会对明确 period/year 做“命中即复用、缺失且授权才下载”，没有 `latest_as_of`、gap plan、修订版选择、衍生物 bundle，也没有三根组合 E2E。
- company-wiki 已有强大的 catalog、artifact、section/evidence 和 canonical writer 基础，unit+contract 1608 项通过；但当前 resolver 全库物化、状态过滤 fail-open、衍生物读取缺完整性门，生产扫描持续带错误，且 11 个重复测试定义被 Ruff 豁免静默隐藏。
- 三个指定目录确实都已进入生产 catalog；**只有 companies 和 dayu 被允许复用，Dropbox 当前被两侧白名单同时排除**。因此“Dropbox 已索引”不等于“filing-fetch 会复用”。
- “已有旧财报时自动判断并补齐最新财报”当前没有产品语义；“已有 MD/摘要/sections 时 consumer 不再重新解析/调用 LLM”当前也没有跨仓契约和调用链。

结论标签：**部分达成，不能按用户关心的复用场景验收通过。**

新增不可变需求：Dropbox 不是可选增强，必须进入复用范围；其启用工作单元的 runtime 代码变更预算为 **0**，只允许配置、测试和文档变化。当前 schema 已能通过两处配置完成，见 §3.2 和 Phase 2A。

### 1.2 必须保留的已有成果

实施不得推翻以下已经有价值的约束：

1. company-wiki 是唯一 canonical writer；dayu/Dropbox 根默认只读，不为“复用”复制或改写外部资产。
2. historical/exact 请求命中本地时保持零 discovery、零下载；只有显式 current/latest 请求才允许轻量远端元数据发现。
3. 下载仍必须显式授权；未授权时返回可审计 gap plan，不得偷偷下载。
4. 弱身份匹配继续返回 ambiguous，不能靠文件名或模糊公司名猜测。
5. 原件、normalized、summary、sections、consumer analysis 各自有独立 lineage；不能把“有一个 MD”直接等同于“可安全复用”。
6. 发布锚点、source hash、as-of 和兼容登记处继续 fail-closed；修复复用链不能绕开 revenue 现有可信链。

## 2. 实施的强制执行协议

本节优先级高于后续任何任务描述。弱模型或新接手者必须逐条执行。

### 2.1 最小工作单元状态机

每个 `WU-*` 只能按以下状态迁移：

`pending → baseline_captured → red_proved → implemented → focused_green → repo_green → cross_repo_green → independently_reviewed → accepted`

规则：

- 没有保存 RED 失败输出，不得写实现。
- focused test 绿但仓库全量红，不得进入下一 WU。
- 需要跨仓契约的 WU，没有 consumer/producer 两侧测试与版本矩阵，不得 accepted。
- `skip`、`xfail`、缩小 collection、降低 coverage 阈值、扩大 ignore、删除反例断言均不算通过。
- 每个 WU 单独 commit；不得顺手重构无关代码。若工作区已有用户修改，先记录并避开，不得 reset/checkout。
- 真实三根和 49 GB catalog 只允许只读 shadow/采样；普通测试只能使用临时目录和临时 SQLite。

### 2.2 每个 WU 的证据回执

完成者必须在 `progress.md` 追加机器可读回执；缺任一字段即不能 accepted：

```json
{
  "work_unit": "WU-x.y",
  "baseline_commits": {"revenue": "...", "filing": "...", "wiki": "..."},
  "red_test_ids": ["E2E-..."],
  "red_exit_code": 1,
  "changed_files": ["absolute/or/repo-relative/path"],
  "focused_commands": ["..."],
  "repo_commands": ["..."],
  "cross_repo_commands": ["..."],
  "tests_collected_before": 0,
  "tests_collected_after": 0,
  "skipped_tests": [],
  "network_calls": 0,
  "parser_calls": 0,
  "llm_calls": 0,
  "real_root_writes": 0,
  "config_hashes": {"source_catalog": "...", "root_policy_export": "..."},
  "reviewer": "independent person/agent id",
  "review_findings": [],
  "status": "accepted"
}
```

计数不适用时写明 `not_applicable + reason`，不能省略。

### 2.3 每一步的禁止事项

- 在当前 schema 下，只有先证明 `kind=directory` 的 root IDs 严格等于 `{dropbox_stock}`，才可把 `directory` 加入 reusable；任何第二个 directory root 出现都必须 fail-fast。未来多 directory roots 时再迁移 root-id policy。
- 不用一次全盘重扫验证普通代码变更；必须先 temp fixture，再 production read-only snapshot。
- 不在 exact/history 请求中为了“检查最新”偷偷联网。
- 不因已有 summary/MD 就跳过 source hash、artifact hash、status、generator/version 和 as-of 验证。
- 不把 company-wiki 的事实性摘要升级为投资结论；consumer-owned analysis 必须单独登记其模型/提示词/输入/版本。
- 不把 mock 函数“未被调用”的局部测试冒充完整 E2E；最终必须在子进程边界用 spy adapter/spy parser/spy LLM 计数。
- 不把文档标题中的 `completed` 作为完成证据；完成只由回执、测试和独立审查决定。

### 2.4 Dropbox config-only 变更围栏

对 `WU-2A.*` 适用额外硬规则：

- 允许修改：company-wiki `config/source_catalog.yaml`；filing-fetch `config/company_wiki.json`；两仓 `tests/**`、`e2e/**` 和相关 Markdown。
- 禁止修改：company-wiki `src/**`、`scripts/**`；filing-fetch `scripts/**`、`tools/**`；revenue `scripts/**`。测试若失败，不能改 runtime 迎合测试。
- 实施前后都运行路径白名单 diff gate；发现任何禁止路径变更立即回滚该 WU 并标 `blocked`。
- “最好只改配置”被落实为：生产行为只由两处配置变化触发；新增测试/E2E 只用于证明，不改变 runtime。
- 这里的“不改代码”仅约束 Dropbox 启用工作单元。latest、artifact bundle、resolver 安全/性能等其它已知问题客观上需要 runtime 修改；若用户意图是三个项目全程不改任何代码，则那些工作包不可完成，必须另行确认而不能伪称完成。

### 2.5 弱模型逐 WU 执行清单

实现者不得仅凭本计划中的旧行号猜测代码。每个 WU 必须把下面 12 项复制到自己的执行记录并逐项打勾：

1. 重读三个 planning 文件和适用的 `AGENTS.md/SKILL.md`；写下本 WU 的单句目标与非目标。
2. 用 CodeGraph status/context/impact 确认当前符号、调用者和影响面；若与计划不符，先标 plan drift，停止编辑。
3. 记录三仓 commit、dirty files、配置 hash、测试 collection、用户文件保护范围。
4. 写出本 WU 的**文件 allowlist**和 forbidden paths；Dropbox WU 直接采用 §2.4，不得自行扩展。
5. 新增最小 RED 测试；运行并保存“因目标能力缺失而失败”的输出。语法/fixture 错误不算 RED。
6. 让另一 reviewer 检查 RED 是否真的能捕获问题；至少做一个 intentional mutation 证明测试会红。
7. 只做使该 RED 变绿的最小变更；不得顺手改下一 WU。
8. 运行 focused tests、静态门、仓库全量、跨仓场景；每层保存 exit code、数量、skip。
9. 检查 `git diff --check`、变更路径 allowlist、coverage/collection 未下降、ignore/xfail 未扩大。
10. 对昂贵或外部动作核对 spy counts；对真实根核对 before/after hash 和写入数 0。
11. 独立 reviewer 用原始需求而非实现描述验收，并随机破坏一个关键不变量确认测试红。
12. 只有回执完整才标 accepted；任一步失败回到对应状态，不能“带问题进入下一阶段”。

若弱模型无法回答“失败应停在哪里、谁能写哪个目录、哪条测试先红、绿灯需要哪些计数”，说明 WU 仍不够细，必须继续拆分，不得实施。

## 3. 目标架构和数据契约

### 3.1 责任边界

| 层 | 唯一职责 | 不应承担 |
|---|---|---|
| company-wiki | 扫描/索引、多根候选选择、原件与衍生物谱系、canonical write、只读 source bundle query | 用户授权决策、预测逻辑、投资结论 |
| filing-fetch | 将用户 filing 请求转为 exact/latest/gap workflow，执行授权检查，调用 company-wiki，返回强校验 receipt/bundle | 自建第二套 catalog、重新解析 PDF、自己判断公司身份 |
| revenue-forecast | 声明所需文档/sections/as-of，消费经验证的 source bundle，记录实际使用 artifact | 下载、扫描三根、信任未经验证的摘要 |

### 3.2 Dropbox 的立即配置路径与长期 RootPolicy

#### 立即路径（必须，config-only）

当前 `ROOT_KINDS={company_raw,directory,dayu_portfolio}`，生产 roots 中只有 `dropbox_stock` 使用 `directory`。因此目标配置差异必须精确为：

```yaml
# company-wiki/config/source_catalog.yaml
reusable_root_kinds: [company_raw, dayu_portfolio, directory]
```

```json
// filing-fetch/config/company_wiki.json 的 allowed_handle_roots 追加
"${USER_PROFILE}/Dropbox/Stock"
```

不得修改 Dropbox 的 `root_id/kind/path/priority`，不得重扫或搬移文件。配置加载后，resolver 会把当前唯一 directory root 映射为 reusable root；filing-fetch path fence 会允许该绝对路径。

为防未来配置漂移，测试必须断言：

- `directory` roots 的 root_id 集合严格等于 `{dropbox_stock}`；出现第二个 directory root 时 CI 立即失败，不能自动获得复用权限。
- 两侧展开后的 Dropbox realpath 完全相同；大小写、junction、符号链接按 Windows realpath 语义比较。
- 配置中 companies/dayu 保持原有授权，顺序与 token 展开稳定。

#### 长期路径（可选硬化，不是启用 Dropbox 的前置）

如果未来要增加第二个普通 directory root，才在获得新的 runtime 代码授权后把 kind 级授权升级为 root-id 级 RootPolicy。建议字段：

```yaml
root_id: dropbox_stock
path_token: dropbox_stock
path: C:/Users/郑曾波/Dropbox/Stock
scan: true
read_only: true
reusable: true
allowed_document_kinds: [annual_report, semi_annual_report, quarterly_report, regulatory_filing]
allowed_location_roles: [original_primary, original_attachment]
required_source_statuses: [active]
required_identity_strength: strong
priority: 30
```

硬约束：

- `root_id` 是权限主键；`kind` 只描述扫描器类型，不能充当安全白名单。
- 导出包含 schema version、生成时间、company-wiki commit、YAML hash、每根规范化绝对路径与策略 hash。
- filing-fetch 启动时校验导出签名/hash、路径存在与 containment；任何双配置漂移 fail-fast。
- external roots 强制 `read_only=true`；只有 company_raw 可由 canonical writer 写入。

长期 RootPolicy 不得被弱模型拿来扩大本次 Dropbox 工作范围，也不得以“架构更优”为理由绕开 config-only 验收。

### 3.3 FilingRequest / GapPlan

必须把两种语义拆开，不能用 `fiscal_year=None` 暗示“最新”：

- `mode=exact`：调用方提供 kind + fiscal_year/period；只在本地解析。命中则 discovery=0；缺失返回 missing，除非调用方对该确切文档显式授权下载。
- `mode=latest_as_of`：调用方提供 kind 集合、market/security identity、as_of；先做远端**元数据** discover，与本地 active 候选比较，生成 GapPlan。只有 `allow_download=true` 且授权 receipt 绑定 GapPlan hash 时，才下载 gap 中的明确项目。

“最新”的唯一判定：截至 `as_of` 已被官方 provider 发布/接收的最大 filing period；同 period 修订版按 provider accession/revision/accepted_at 排序，不能按文件 mtime 或文件名。provider 尚未发布的新期不得制造 gap。

GapPlan 至少包含：已有并复用、缺失待下载、已有但更旧 revision、ambiguous、provider unavailable、未到发布时间、拒绝原因、候选 source ids、远端 accession、授权 hash、计划有效期。

### 3.4 SourceBundle / ArtifactHandle

filing-fetch 成功结果不能只返回原件 handle，应可选返回：

- `source`: document_id/source_id/canonical_path/content_sha256/provider/url/filing_date/as_of/root_id/location_role/status。
- `normalized`: path/hash/source_id/source_sha256/status/generator/version/schema/created_at。
- `summary`: 同上，外加 prompt/model/policy version、summary type。
- `sections`: section index artifact + evidence span schema/version/count。
- `consumer_artifacts`: 仅登记明确 consumer schema 的分析产物，必须含 input bundle hash、engine/model/prompt/version/as_of；未知 MD 不得放入。
- `reuse_decision`: 每个 role 是 reused / stale / invalid / missing / recomputed，以及原因码。

ArtifactHandle 必须同时通过：`status=completed`、source/document 绑定、source_sha 与当前原件一致、artifact 文件存在且 hash 一致、generator/schema 在兼容登记处、created_at/as_of 合法、路径在允许根、没有 quarantine/rejection。任一失败都 fail-closed 到“不可复用”，并记录原因；不得静默信任。

## 4. 分阶段实施计划

### Phase 0：冻结真实基线与防污染（P0，所有后续前置）

#### WU-0.1 基线清单与只读保护

- 仓库：三仓。
- 动作：固定三个 commit、Python/pytest/ruff/SQLite 版本、测试收集数、配置 hash、root realpath、catalog schema/version/size、最近 scan 状态；记录已有 dirty files。
- 新增测试/工具：`tools/audit_baseline.py --read-only`，只能读，不允许打开 SQLite write transaction。
- RED：给脚本一个临时可写探针 root，若脚本创建/修改任何文件则失败；真实三根前后 tree metadata/hash 抽样一致。
- 门禁：三仓状态差异只包含实施者自己的 WU 文件；真实根写入计数为 0。

#### WU-0.2 生产快照夹具生成器

- 仓库：company-wiki。
- 动作：从生产 catalog 只导出匿名化 schema、root policy、候选状态分布和最多 N 条去路径化样本；不复制原件，不导出秘密/个人路径。
- 测试：临时 catalog 验证 deterministic output、字段脱敏、行数上限、read-only connection、busy timeout。
- 门禁：快照可在无三真实目录的 CI 重放；同一 snapshot 两次 hash 相同。

### Phase 1：先恢复测试和质量门的真实性（P0）

#### WU-1.1 消除 company-wiki 静默少收集

- 文件：`tests/contract/test_source_catalog_worker.py`、`pyproject.toml`，新增 `tools/check_unique_test_symbols.py`。
- RED：isolated Ruff F811 当前必须稳定报出 11 组重复定义；AST gate 对 module/class scope 的 `test_*` 重名返回非零。
- 实施：逐组比较前后定义；相同则保留一份并在回执说明，语义不同则重命名并保留两份。删除该文件 F811 ignore。
- 验证：pytest collection manifest 必须解释净变化；不能简单让 count 下降 11。运行 company unit+contract 全量两次，验证无 worker teardown 偶发失败。
- 门禁：isolated 和 configured Ruff 都不再需要 F811 例外；AST gate 进入 CI。

#### WU-1.2 清理并冻结静态质量范围

- revenue：修复产品相关目录当前 185 个 Ruff 问题；历史审计 probe 可单独配置为 archival scope，但不能让其错误污染产品门。
- filing：保留当前 Ruff 全绿，补 `compileall`/import smoke。
- wiki：修复当前 unused import，并把 `src tests scripts` 纳入 Ruff；docs prototype 若保留，归档为非产品并明确单独门。
- RED：三仓 workflow 在故意加入 unused import、重复 test、syntax error 时均失败。
- 门禁：`ruff check`、`compileall`、test-symbol gate 全绿；不得新增 per-file ignore，确需例外必须有 issue ID、到期日、owner。

#### WU-1.3 覆盖率与 collection 防降级

- 动作：按模块记录 branch coverage，不用单一总覆盖率掩盖关键链；冻结 test collection manifest 和关键 scenario IDs。
- 最低门：resolver/acquisition/artifact validator/root policy/filing contracts 各 branch ≥95%；跨仓 adapter ≥90%；全仓阈值不得低于当前有效基线。
- mutation：对 source status allowlist、allowed root、allow_download、source_sha、artifact status、latest revision comparator 各设至少一个 mutation canary，存活即 CI 失败。
- 门禁：不能通过排除新文件或降低阈值变绿。

### Phase 2A：用现有配置安全启用 Dropbox（P0，必须先完成，runtime 零改动）

#### WU-2A.0 配置能力 RED 探针

- 只新增/修改测试，不改配置、不改 runtime。
- 建立临时 company-wiki 配置：`dropbox_stock kind=directory` 且 `directory` 未列 reusable；建立临时 filing 配置：Dropbox 未列 allowance。真实 resolver+filing handle fence 必须分别表现为 MISSING/拒绝。
- 只在临时配置中加入 `directory` 和 Dropbox path，再跑同一 fixture；必须转为 REUSED_EXACT 且 handle 位于临时 Dropbox。
- fixture 必须位于 `重点关注/ACME/`，包含原件与 `.source.json`，sidecar 固定：annual_report、US/ACME、FY2025、10-K、SEC accession、filing date、HTTPS URL、ingest complete。不得依赖文件名猜 identity。
- RED 证据必须证明行为变化只来自两处 config；如果当前 runtime 无法通过正例，立刻 blocked，不能进入 WU-2A.1，也不能改 runtime。

#### WU-2A.1 配置不变量测试

- company-wiki 新增 `CONFIG-DBX-01`：生产 YAML 可加载，`dropbox_stock` 的 kind/path/priority 不变，`directory` 被列入 reusable。
- company-wiki 新增 `CONFIG-DBX-02`：所有 `kind=directory` 的 root IDs **严格等于** `{dropbox_stock}`；增加任意第二个 directory root 的 fixture 必须 RED。
- filing-fetch 新增 `CONFIG-DBX-03`：生产 JSON 展开后 allowance **严格等于** companies/dayu/Dropbox 三个 realpaths，不接受父目录 `Dropbox`、通配符或相似前缀。
- 跨仓新增 `CONFIG-DBX-04`：YAML 的 Dropbox realpath 与 JSON allowance 的 Dropbox realpath 相同；任一侧缺失、拼错、大小写/链接指向不同都失败。
- 门禁：四个测试先在当前配置上按预期 RED；保存失败原因，禁止通过放宽断言变绿。

#### WU-2A.2 仅修改两处生产配置

- 唯一允许的生产差异：
  1. `company-wiki/config/source_catalog.yaml` 的 `reusable_root_kinds` 追加 `directory`；
  2. `filing-fetch/config/company_wiki.json` 的 `allowed_handle_roots` 追加 `${USER_PROFILE}/Dropbox/Stock`。
- 不修改 schema version、root kind、root path、priority、companies/dayu 项；不运行 scan；不触碰 49 GB SQLite。
- diff gate：若 `git diff --name-only` 除上述两配置和本 WU 测试/文档外有任何文件，失败。
- runtime 零改动复核：company-wiki 的 `git diff --name-only -- src scripts`、filing-fetch 的 `git diff --name-only -- scripts tools`、revenue 的 `git diff --name-only -- scripts` 均必须为空；把输出写入 WU receipt。
- 门禁：CONFIG-DBX-01~04 全绿；两配置 parse/round-trip 全绿；runtime 禁止路径 diff 为 0。

#### WU-2A.3 隔离的 Dropbox 正反例 E2E

| ID | 临时 Dropbox 内容 | 预期 |
|---|---|---|
| E2E-DBX-01 | 有效 official annual + 完整 sidecar | REUSED_EXACT；discover/fetch/copy/write=0 |
| E2E-DBX-02 | 有效 semi-annual/quarterly | kind/period 精确命中；0 fetch |
| E2E-DBX-03 | 年报点评/研报 | annual request 不得命中 |
| E2E-DBX-04 | 公告、监管函、无允许类别证据 | admission 拒绝；0 fetch |
| E2E-DBX-05 | 原件缺 URL/provider/accession/identity 任一项 | capture incomplete/identity conflict；不得复用 |
| E2E-DBX-06 | retired/quarantined/upstream_rejected | 不得返回成功 handle；当前已知状态过滤缺口由 WU-3.1 修复 |
| E2E-DBX-07 | 文件在 Dropbox sibling、prefix-collision、symlink/junction 越界 | filing path fence 拒绝 |
| E2E-DBX-08 | companies/dayu/Dropbox 同 hash | 结果确定；不复制、不下载；记录所有等价 location |
| E2E-DBX-09 | 配置新增第二个 directory root | CONFIG-DBX-02 先于 resolver 失败 |
| E2E-DBX-10 | 完全相同二次运行 | receipt/hash 稳定；mtime 不变；昂贵调用仍为 0 |

- 必须从 filing-fetch CLI 子进程进入真实 company-wiki resolver，不能直接调用 selector 冒充 E2E。
- spy 记录写在测试临时目录；外部网络硬禁用。测试前后对临时 Dropbox 做 tree hash，除 spy 日志目录外内容完全相同。
- 门禁：10 个场景全绿；故意删除 `directory` 或 Dropbox allowance 时 DBX-01/02 必须红，证明测试能抓住配置回归。E2E-DBX-06 若按预期暴露当前 F-024，不得改 runtime 作为 Dropbox WU 的一部分；应保存 RED、先完成独立 WU-3.1，再回到本门禁。Dropbox 两处 config 仍是唯一启用差异。

#### WU-2A.4 生产只读 canary

- 前置：WU-3.1 已 accepted，E2E-DBX-06 已绿；否则不得在生产配置启用 Dropbox。
- 不扫描、不下载、不解析、不调用 LLM；以 SQLite read-only URI 和现有 resolver 做限时采样。
- 先产出 inventory：Dropbox official filing candidates、active/capture-ready/strong-identity counts，以及 rejected/quarantined/other counts；路径在报告中脱敏。
- 从 inventory 中固定至少 3 个已验证样本（若资产具备，覆盖 A/H/US 或 annual/semi/quarterly），用明确 entity/market/security/year/provider/accession 发 exact 请求。
- 每个样本必须：成功 handle 位于 Dropbox/Stock；source hash 与磁盘一致；download/copy/write=0；同请求二次结果一致。
- 同时抽 3 个 broker/announcement/rejected 负样本，必须不成功。
- **双层状态**：配置和隔离 E2E 通过可标 `configuration_enabled`；只有至少 1 个真实已有 official filing 成功复用且负样本全拒绝，才可标 `production_reuse_verified`。若 inventory 中没有 capture-ready 样本，不能伪称“实际复用完成”，应报告数据/metadata blocker；仍不得改 runtime。

#### WU-2A.5 回滚和持续门

- 回滚只删除 YAML 中 `directory` 和 JSON 中 Dropbox path；不修改 catalog、不删除文件。
- PR 必跑 CONFIG-DBX-01~04 与 E2E-DBX-01~10；daily 只读 canary 检查 Dropbox root 仍 indexed、scan freshness、成功/拒绝候选分布。
- 新增任何 directory root 的 PR 在 CONFIG-DBX-02 失败后，必须先提出 root-id policy 迁移，不能把新 root 顺手授权。

### Phase 2B：未来多 directory roots 时才做 RootPolicy（P2，可选且需另行代码授权）

#### WU-2B.1 root-id policy 和单一导出

- 触发条件：计划新增第二个 `kind=directory` root，或 CONFIG-DBX-02 无法继续成立。
- 主要符号：company-wiki `CatalogConfig`/config loader；filing-fetch allowance loader。
- RED：只在一侧加入 root、未授权同 kind root、路径/链接越界均失败。
- 实施：新增 root-id policy/版本化导出并替代 kind 级授权；这是 runtime 变更，必须单独获批。
- 门禁：配置 migration、双向兼容、rollback、config hash receipt 全绿；不得回归 Phase 2A 全部场景。

### Phase 3：修正 resolver 的安全性、正确性和性能（P0）

#### WU-3.1 fail-closed 状态和路径过滤

- 主要文件：company-wiki `source_catalog/service.py`、`resolver.py`。
- RED：`retired`、`quarantined`、`upstream_rejected`、`.rejections`、missing file、非 original role 均不得形成 handle；生产 snapshot 中同类候选也必须被拒绝。
- 实施：查询层用 active allowlist，resolver 再做 defense-in-depth；输出稳定 reason code。
- 门禁：状态 mutation canary 被杀死；零 rejected candidate 出现在成功 receipt。

#### WU-3.2 SQL 下推和索引

- 实施：新增专用 `query_filing_candidates(entity, kind, period, as_of, root_ids, statuses, limit)`，SQL 层联结/过滤；resolver 禁止调用 `query(limit=10_000_000)`。
- 索引：对 identity/entity、document kind/status/period/date、location document/root/status/role 建覆盖索引；migration 可重入、可回滚。
- RED：100k documents fixture 中 monkeypatch 通用全表 query，一旦被调用即失败；`EXPLAIN QUERY PLAN` 必须命中目标索引且候选上限 ≤100。
- SLO：CI 100k fixture warm p95 ≤500ms、RSS 增量 ≤100MB；生产只读采样 p95 ≤2s、RSS 增量 ≤250MB、trace ≤100 条。硬件/版本写入回执。
- 门禁：功能矩阵不变、性能 SLO 达标、SQLite migration backup/rollback 演练通过。

#### WU-3.3 多候选确定性和冲突语义

- 规则：同 content hash 跨根为 equivalent，按 root priority 选择但保留所有 locations；同 period 不同 hash 且无 revision 证据为 ambiguous；不能按扫描顺序决定。
- RED：三根同 hash、同 period 不同 hash、强/弱身份混合、主件/附件、同 accession 修订版、mtime 逆序。
- 门禁：随机打乱插入顺序 100 次，结果/receipt hash 恒定。

### Phase 4：实现“旧的复用、最新缺口才补”的明确语义（P0）

#### WU-4.1 versioned FilingRequest 和 LatestPolicy

- 仓库：company-wiki + filing-fetch + revenue adapter。
- 实施：新增 `mode`，禁止用 null year 猜 latest；定义 annual/semi/quarterly/regulatory 的 period 与 market calendar/provider mapping。
- RED：旧客户端 schema 兼容路径、unknown mode、latest 无 as_of、exact 无 period、future as_of、跨市场 form 混淆。
- 门禁：contract version/compatibility registry 两侧一致；旧调用获得明确 deprecation 而非行为暗变。

#### WU-4.2 metadata-only discovery 与 GapPlan

- 实施：latest 请求先 discover metadata，绝不下载；本地与远端按 provider accession/period/revision/accepted_at 对齐。
- RED：
  - 本地只有旧年 → gap 仅含官方已发布新年；
  - 本地已最新 → download=0；
  - 新年尚未发布 → gap=0；
  - 本地同 period 旧 revision → 仅列新 revision；
  - provider offline/rate-limit → 保留旧文件并返回 incomplete，不误称 up-to-date。
- 门禁：GapPlan deterministic hash；discover/fetch 分开计数；exact 路径 discover=0。

#### WU-4.3 授权绑定与最小下载

- 实施：授权 receipt 绑定 request hash、GapPlan hash、provider/accession、数量/大小上限、过期时间；下载器只能取 plan 中项目。
- RED：篡改 accession、plan 过期、下载重定向越域、内容 hash/格式错误、部分失败、重复并发请求。
- 并发：同 accession 两个请求只下载一次；失败不留下 capture-ready 半成品；重试可恢复。
- 门禁：旧文件 mtime/hash 不变；网络 fetch 次数精确等于有效缺口数；无授权为 0。

### Phase 5：让已处理内容成为可验证、可消费的 SourceBundle（P0/P1）

#### WU-5.1 ArtifactHandle validator

- 主要文件：company-wiki artifact/service/evidence/section query 模块。
- RED：pending/failed/stale status、wrong source_id、wrong source_sha、文件丢失、artifact hash 错、过期 generator/schema、future as_of、越界路径均拒绝。
- 实施：按 role 返回经过验证的 handle，不再直接暴露未筛选 `normalized_path`/`summary_path`。
- 门禁：validator mutation canaries 全杀；每个拒绝有 reason code 和 fallback policy。

#### WU-5.2 SourceBundle query

- 实施：一次查询返回 source + 可用 normalized/summary/sections/evidence；避免 consumer 自己拼表。bundle hash 绑定所有子 handle。
- 约束：事实摘要允许复用；生成的投资结论继续由 consumer 管理。consumer analysis 只有在 schema/input bundle/model/prompt/engine/as_of 全匹配时才可登记复用。
- RED：部分存在、两个 generator 版本、旧 source 新 summary、summary 合规但 sections stale、同 role 多 artifact、路径存在但 hash 不符。
- 门禁：选择确定性；无效子 artifact 不污染仍有效原件；返回明确 `reused/stale/missing/invalid`。

#### WU-5.3 filing-fetch 契约扩展

- 实施：成功 receipt 携带可选 SourceBundle 与 reuse decisions；handle 深校验继续覆盖 external root path。
- RED：伪造 bundle、仅改子 artifact、跨 root 越界、旧 filing-fetch 遇新字段、旧 company-wiki 无 bundle capability。
- 门禁：双向 compatibility suite 通过；版本不兼容 fail-closed，不退回“裸路径可信”。

#### WU-5.4 revenue consumer 零重复处理

- 实施：`filing_fetch_client.py`/`company_wiki_source.py` 优先消费有效 normalized/sections/summary；原件仍是最终 lineage anchor。具体 research step 声明它需要哪些 roles，不做全有或全无。
- RED：有效 normalized 时 PDF parser=0；有效 sections 时整篇 chunker=0；有效合规 summary 时对应 summarizer LLM=0；任一 artifact stale 时只重算该 role，不能全链重跑。
- 输出：forecast receipt 记录实际使用 artifact ids/hash/generator、fallback 原因和调用计数。
- 门禁：跨仓 E2E-D01~D06 通过；预测数值/来源引用 golden 不因切换物理载体漂移。

### Phase 6：建立真正的跨仓 E2E 测试金字塔（P0）

#### WU-6.1 可观测 spy 和 fixture builder

- 新建共享测试支持包，提供：三根临时目录、临时 catalog、官方 adapter spy、parser spy、LLM spy、可控 clock/as_of、故障注入、文件树 before/after hash。
- 所有 spy 以跨进程 append-only JSONL/localhost test server 记录，不能只靠进程内 mock。
- 每个 E2E 断言：exit/result、source/bundle lineage、discover/fetch/parser/LLM/scan/write 次数、真实根写入 0、二次运行幂等。
- 门禁：故意多调用一次任一 spy，测试必须红；否则断言强度不够。

#### WU-6.2 场景矩阵

| ID | 初始情景 | 请求 | 必须断言 |
|---|---|---|---|
| E2E-R01 | companies 有 exact 最新原件 | exact | reuse companies；discover/fetch=0 |
| E2E-R02 | 仅 dayu 有 exact | exact | reuse dayu；复制/写入/fetch=0 |
| E2E-R03 | 从 revenue 用户入口请求、仅 Dropbox 有 official exact | exact | 经 filing-fetch reuse Dropbox；写入/fetch=0；与 DBX-01 不同层级 |
| E2E-R04 | 三根同 hash | exact | 按 policy 选主 location；保留等价 locations；0 fetch |
| E2E-R05 | 同 period 不同 hash、无 revision | exact | ambiguous；0 fetch；不猜测 |
| E2E-R06 | 仅 retired/quarantined/rejected | exact | missing/rejected；0 fetch |
| E2E-R07 | catalog 有记录但文件丢失 | exact | stale reason；0 fetch；请求增量修复而非信任 |
| E2E-R08 | 弱 identity / broker PDF | exact | 不 admission；0 fetch |
| E2E-L01 | 只有旧年，本地最新请求 | latest_as_of | 复用旧年；discover=1；gap=新年；未授权 fetch=0 |
| E2E-L02 | 只有旧年且授权 | latest_as_of | 只 fetch 新年一次；旧文件不变 |
| E2E-L03 | 已有官方最新 | latest_as_of | discover=1；gap=0；fetch=0 |
| E2E-L04 | 新期尚未发布 | latest_as_of | gap=0；fetch=0；理由 not_published |
| E2E-L05 | 同期有新 revision | latest_as_of | 只列/取新 revision；旧版保留 provenance |
| E2E-L06 | provider offline/rate-limit | latest_as_of | 状态 unknown/incomplete；不误称最新；0 fetch |
| E2E-L07 | exact 历史请求且远端有新版 | exact | discovery/fetch=0；历史 as_of 不受未来污染 |
| E2E-D01 | 原件 + 有效 normalized MD | research | parser=0；使用 artifact hash |
| E2E-D02 | 原件 + 有效 summary | research | 对应 summarizer LLM=0 |
| E2E-D03 | 原件 + 有效 sections/evidence | research | 整篇 chunker=0；引用定位不变 |
| E2E-D04 | normalized source_sha 旧 | research | 只重解析 normalized；summary/section 按依赖 DAG 失效 |
| E2E-D05 | summary 绑定错误 source | research | 拒绝 summary；只重算 summary；记录 reason |
| E2E-D06 | consumer analysis 完全兼容 | forecast | 复用；模型/提示词/输入任一变化则不复用 |
| E2E-F01 | 下载返回 HTML/截断 PDF | latest+auth | quarantine staging；不生成 capture-ready handle |
| E2E-F02 | 两并发请求同 accession | latest+auth | fetch=1；两个 receipt 一致；无半文件 |
| E2E-F03 | root policy 两侧 hash 不同 | 任意 | doctor fail-fast；resolver 不启动 |
| E2E-F04 | symlink/junction 越出 root | exact | path fence 拒绝 |
| E2E-F05 | scan 只部分成功/有空文件错误 | exact/latest | 与目标无关可降级但披露；目标根陈旧则不宣称完整 |
| E2E-F06 | 二次完全相同运行 | 任意 | result/receipt hash 稳定；所有昂贵调用为 0（latest 的 metadata cache 策略按契约断言） |

#### WU-6.3 测试层级和命名纪律

- L0 pure unit：selector/status/hash/revision comparator。
- L1 repo contract：临时 SQLite + 真实 service/CLI。
- L2 cross-repo offline E2E：真实三个 CLI/子进程、临时三根、spy 外部系统。
- L3 controlled adapter E2E：只用固定小样本/recorded metadata，秘密由 CI environment 管理；失败不能污染生产。
- L4 production read-only canary：三真实根 + 生产 catalog，只采样/计时/验证 receipt，不下载、不写；定时运行，不阻塞普通 PR，但失败阻止发布并告警。
- 现有 `run_filing_fetch_e2e.py` 重命名/文档化为 `companies_reuse_only_e2e`；只有覆盖 user entry→catalog→optional adapter→bundle→consumer 的测试可称 full-chain。

### Phase 7：CI、兼容性和回归防护（P1）

#### WU-7.1 三仓 PR 门

| 门 | revenue | filing | wiki |
|---|---:|---:|---:|
| Ruff + compile/import | 必须 | 必须 | 必须 |
| unique test symbols / collection manifest | 必须 | 必须 | 必须 |
| unit + branch coverage | 必须 | 必须 | 必须 |
| mutation canaries | 可信链 + consumer | auth/root/bundle | status/root/artifact/latest |
| repo contract | 必须 | 必须 | 必须 |
| cross-repo offline E2E | consumer 端发起 | orchestration | producer |
| config/plan doctor | 必须 | 必须 | 必须 |

- 跨仓 CI 不能 clone 浮动 `main/master`；由 compatibility registry 指定 commit/tag 矩阵，PR 同时测试 oldest-supported/current/next fixture。
- coverage、ruff、E2E、plan verifier 均进入 workflow，不只留在本地脚本。
- 任何关键 scenario ID 从 collection 消失即失败。

#### WU-7.2 定时门与发布门

- nightly：L3 controlled adapter、100 次 deterministic insertion order、worker teardown stress、migration round-trip。
- daily/weekly：L4 production read-only canary、三根 scan freshness、error budget、resolver p95/RSS、catalog 增长率。
- release：所有 WU receipt、兼容矩阵、docs version、config export hash、零存活关键 mutation、独立审计签名。

### Phase 8：文档、可观测性和计划治理（P1）

#### WU-8.1 用户可解释 receipt

filing-fetch 输出必须能回答：

1. 用了哪一个根、哪份原件、为什么选它？
2. catalog 最近何时成功扫描，是否带错误？
3. 远端是否做过 metadata discovery，为什么认为是最新/未知？
4. 哪些缺口下载了，授权绑定哪份 GapPlan？
5. 哪些 MD/summary/sections 被复用，哪些因何失效？
6. 网络、解析器、LLM 各调用几次？

错误码固定、文档化、可测试；不能只给自由文本 debug trace。

#### WU-8.2 文档真实度

- 同步 SKILL、README、E2E_DESIGN、CHANGELOG、配置参考和架构图。
- 明确区分：indexed、admitted、reusable、capture-ready、up-to-date、artifact-valid、consumer-used。
- 不再写“full-chain”而只覆盖 synthetic companies reuse。
- “analysis reuse”说明信任边界：技术预处理/事实摘要与投资结论不是同一层。

#### WU-8.3 统一 planning claim verifier

- 覆盖三个仓库 `task_plan.md`、`progress.md`、`findings.md`、`docs/plans/**`、`audit_review/**` 的 active plan。
- 规则：标题 completed 与 checklist/Phase 状态/DoD 一致；需要 4 周观察的门在时间未满前不能完成；每项 complete 有测试回执；只做计划的文件不能同时宣称 production apply。
- RED：用 core-section 和 catalog-space-remediation 当前冲突做 fixture，verifier 必须报错。

### Phase 9：安全迁移和生产 rollout（P1）

#### WU-9.1 shadow 模式

- 新 resolver/latest/bundle（以及未来获批时的 root-id policy）先在生产只读 shadow 运行，不改变旧结果；比较 candidate、reason、延迟、误拒/误纳。
- 人工复核分层抽样：companies/dayu/Dropbox × annual/semi/quarterly × active/rejected × 有/无衍生物。
- 退出条件：0 个 rejected 被 admission；所有差异有归因；性能 SLO 连续 7 天满足。

#### WU-9.2 分根启用

- companies/dayu 保持现状；Dropbox 按 Phase 2A 的两处 config 作为一个原子发布单元启用，不能只部署一侧。
- 当前 schema 无法靠配置把 Dropbox 先限制为 annual，因此不得写虚假的“先 annual 后扩面”。安全性由 admission/identity/capture-ready/status 负例和只读 canary 证明；任一负例成功即回滚两处配置。
- 发布前后保存两配置 hash；观察至少一个完整 scan 周期。scan 有与目标候选相关的未解释错误、真实负样本误命中或 realpath 漂移时立即执行 WU-2A.5 回滚。

#### WU-9.3 latest 和 download rollout

- 先 metadata-only GapPlan，无自动 fetch；人工比对 provider 结果。
- 再开放显式授权的单文档下载；随后才开放多 gap batch，仍有数量/大小/域名上限。
- rollback 只关闭 latest/download feature，不破坏 exact reuse。

### Phase 10：独立验收与“可以宣称完成”的条件（P0 release gate）

#### WU-10.1 独立全链验收

必须由未实施相关 WU 的 reviewer 执行：

1. 重放全部 E2E scenario IDs，检查不是 mock-only。
2. 随机抽 3 个场景故意破坏 root/status/hash/latest/artifact 之一，确认测试红。
3. 检查三仓 diff，没有降低阈值、扩大 ignore、删除测试、真实根写入。
4. 对三真实目录各做只读 canary，验证 lineage 和零不必要调用。
5. 对一个本地只有旧期的实体做 metadata-only latest gap；未经额外授权不得下载。
6. 对一份已有 normalized+summary+sections 的文档从 revenue 用户入口运行，确认相应 parser/LLM=0。
7. 所有 WU receipt/schema/commit/config hash 可复现，planning verifier 全绿。

#### WU-10.2 已知问题逐项关闭账本

- 以 `findings.md` 的 F-001~F-034、历史矩阵每一行和风险 R-001~R-014 为全集，生成 closure ledger；不得只挑 P0/P1。
- 每行必须包含：最终状态、修复 WU、RED test ID、回归 test ID、生产/隔离证据、剩余风险、reviewer、commit/config hash。
- 信息性发现可以标 `not_a_defect`，但要说明理由；任何 `unresolved/partial/unverified` 行存在时，不能宣称“上述问题全部消除”。
- 对旧问题因架构变化失效的情况，必须用当前 CodeGraph/删除 guard/compat test 证明 `superseded`，不能直接删行。
- release manifest 对 closure ledger 做 schema 校验，并验证所引用的 test ID 实际被 pytest 收集、没有 skip/xfail。

只有以上全部满足，才允许在文档中声明：

- “三根均可安全复用”；
- “latest 请求能识别并只补有效缺口”；
- “有效已处理资产会被 consumer 实际复用”；
- “上述能力由跨仓 E2E 和生产只读 canary 持续守护”。

### 10.3 保证边界

若 WU-0~10 全部按闸门 accepted，可以高置信度保证：本审查已列举的、可测试的 F/N/P/C 问题均被修复，或被明确分类为已失效/非缺陷；三项核心用户场景有持续测试和生产只读证据，不能再靠文档声明冒充完成。

但工程验收不能提供数学意义的“所有未来问题绝对为零”。以下仍属于剩余风险：未知缺陷、未出现过的新文件格式、外部 provider/API 行为变化、操作系统/权限变化、生产数据在 canary 之间损坏、超出 as-of/market matrix 的输入。控制方式是 fail-closed、版本契约、daily canary、mutation、error budget 和 closure ledger；发现新问题必须新增 F-ID + RED test，再进入同一状态机。

因此最终可作出的严格承诺是：**消除并防回归本计划枚举的已知问题；把未知问题的发现和失败方式制度化。不能承诺软件永远不存在未知缺陷。**

## 5. 实施顺序与不可跳过的闸门

| 顺序 | 工作包 | 进入条件 | 退出条件 | 失败处理 |
|---:|---|---|---|---|
| 0 | WU-0.* baseline | 用户授权实施 | 只读基线/快照可复现 | 停止，不触碰功能 |
| 1 | WU-1.* test truth | baseline accepted | 无静默少收集，静态/coverage 门真实 | 停止；不得靠 ignore 过门 |
| 2 | WU-2A.* Dropbox config-only | WU-0.1/WU-1.1 accepted；可先做 RED/配置分支；生产启用另需 WU-3.1 | 两处配置、10 个 DBX E2E、production read-only canary；runtime diff=0 | 删除两处配置增量；不改 catalog |
| 2B | WU-2B.* root policy（条件性） | 未来新增第二个 directory root且另行获批 | root-id 策略替代 kind 级授权 | 保留 Phase 2A，回滚新 schema |
| 3 | WU-3.* resolver | WU-1.1 accepted；WU-3.1 是 Dropbox 生产 canary 前置，WU-2B 非前置 | fail-closed + SQL/SLO + deterministic | 回滚 migration/selector；Dropbox 配置保持未部署或执行独立回滚 |
| 4 | WU-4.* latest | resolver accepted | GapPlan/授权/最小下载 E2E | 保留 exact，关闭 latest |
| 5 | WU-5.* bundle | resolver accepted；可与 WU-4 实现并行但验收独立 | artifact/bundle/consumer 零调用 | 回退原件，不信任 artifact |
| 6 | WU-6.* cross E2E | 2–5 focused green | 全矩阵 + mutation strength | 不进入 rollout |
| 7 | WU-7/8 | E2E accepted | CI/文档/计划门实际启用 | 不发布 |
| 8 | WU-9 | release candidate | shadow/分根/最新观察门满足 | feature flag rollback |
| 9 | WU-10 | 所有 receipt 完整 | 独立复核签字 | 退回具体 WU |

## 6. 当前审查验证记录

| 项目 | 当前运行 | 结果 | 能证明 | 不能证明 |
|---|---|---|---|---|
| revenue-forecast | `python -m pytest tests -q` | 301 passed + 106 subtests，12.86s | 当前 unit/contract 定义通过 | 三根/latest/bundle 用户 E2E、静态质量 |
| filing-fetch | 离线 pytest，排除 real conformance/download | 115 passed、1 skipped + 27 subtests，55.58s | 薄契约和隔离行为 | 真实下载、三根、最新、衍生物 |
| company-wiki | `pytest tests/unit tests/contract` | 1608 passed，362.56s | 当前收集的 unit/contract | 被覆盖的 11 组测试、integration/acceptance/生产行为 |
| revenue Ruff | `ruff check scripts tests tools e2e --no-cache` | 185 errors | 静态门当前不合格 | 行为失败与否 |
| filing Ruff | 对代码/测试/tools/E2E | pass | 当前静态口径合格 | 业务闭环 |
| wiki Ruff | 配置口径 + isolated F811 | 1 unused；11 redefinitions | 默认门会隐藏重复测试 | 被覆盖测试原本是否语义相同 |

未运行并明确保留到实施阶段：任何会下载文件的 E2E、生产 catalog 写操作/重扫、真实三根 mutation、受控 provider live tests。原因是本轮只做计划，且生产 catalog 49.27 GB、后台 worker 活跃；本轮用静态代码、只读 DB/文件盘点和 hermetic 测试作为证据。

## 7. 本轮 planning-with-files 阶段状态

- [x] Phase 1：历史 planning 文档、前次两轮审查和原始目标恢复。
- [x] Phase 2：三仓架构、代码、配置、CI、文档对抗性审查。
- [x] Phase 3：三真实根、latest、衍生物复用专项核验。
- [x] Phase 4：安全现有测试与只读生产证据验证。
- [x] Phase 5：实施工作包、E2E 矩阵、弱模型闸门和 rollout 计划。
- [x] Phase 6：需求覆盖与“只做计划”边界自审。

产品实施状态：**全部 WU 仍为 pending，等待用户后续明确授权。**

## 8. 用户要求覆盖检查（含追加 Dropbox 硬需求）

| 用户要求 | 本计划/证据位置 | 自审结果 |
|---|---|---|
| 1. 全面审查三项目的设计、架构、代码、测试、文档和实际体验 | `findings.md` F-001~F-034、分维度验收、历史矩阵；本文件 §1、§3 | 已覆盖；结论不是“测试绿即完成” |
| 2. companies/dayu/Dropbox 复用、旧期补新、已处理内容复用 | `findings.md` F-012/F-015/F-018/F-020/F-024/F-025；本文件 WU-2/WU-4/WU-5 | 已分别核验；三项当前都不是完整闭环 |
| 2A. Dropbox 必须加入且启用过程不改 runtime 代码 | `findings.md` F-034；本文件 §2.4、§3.2、WU-2A.0~2A.5 | 已给出精确两配置差异、4 个配置测试、10 个 E2E、runtime diff=0、生产 canary 和回滚；长期 RootPolicy 明确为非前置 |
| 3. 用 E2E 固化问题并覆盖有/无/旧/错/冲突等情形 | 本文件 Phase 2A 的 10 个 E2E-DBX，加 WU-6.1~6.3 的 E2E-R/L/D/F 27 个场景，另有 mutation 和 production canary | 已覆盖；37 个唯一场景，每项含昂贵调用次数和真实根写入断言 |
| 4. 先独立思考，再参考前次 `audit_review` | 先以当前 CodeGraph/配置/代码/生产只读证据建立问题，再用 `findings.md` 历史矩阵逐项对照两轮旧审查 | 已覆盖；旧结论未直接继承 |
| 5. planning-with-files 详细计划，防弱模型跑偏 | 本文件 §2 状态机/回执/禁止项、WU-0~10、顺序闸门；`progress.md` 持续记录 | 已覆盖；每步必须 RED、全量绿、跨仓绿、独审后才能进下一步 |
| 6. 本轮只做计划，不实施 | 文件头边界、§7；git 范围仅新增本审查目录 | 已遵守；未改产品代码/测试/配置，未下载或写生产索引 |

## Errors Encountered

| 日期 | 错误 | 尝试 | 处置 |
|---|---|---:|---|
| 2026-08-08 | PowerShell 首次读取 UTF-8 中文时输出乱码 | 1 | 后续显式设置 Console/OutputEncoding 并用 `Get-Content -Encoding utf8`；未采用乱码内容作证据 |
| 2026-08-08 | SQLite 根表查询引用不存在的 `read_only` 列 | 1 | 用 `PRAGMA table_info(roots)`确认真实 schema 后重写查询 |
| 2026-08-08 | 一次 artifact/evidence 大 join 无输出 | 1 | 拆分成小查询和抽样；不在活跃 49 GB DB 做无界 join |
| 2026-08-08 | PowerShell 中误用 bash 反斜杠续行 | 1 | 改用 PowerShell 数组；不再混用 shell 语法 |
| 2026-08-08 | 一次并行 git-status JS 参数写法触发 SyntaxError | 1 | 修正对象字段后立即成功；未产生副作用 |
| 2026-08-08 | filing Ruff 首次指定不存在的 `src` 目录 | 1 | 按实际目录 `scripts tests tools e2e` 重跑并通过 |
| 2026-08-08 | 更新 Dropbox 计划的一次多文件 patch 因 closure-ledger 上下文已变化而校验失败 | 1 | 未产生部分写入；改用按文件/按小段精确 patch，不重复原大 patch |
