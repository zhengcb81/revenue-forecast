# R4 Phase B 进度（progress）

## 2026-09-12（实施期）— **B05 已实施**（3 子步：抽取 / 保留键+读-改-写 / 逐列规则+读侧 blocked）

- **提交**：`6909e78`（等价抽取 `_merge_document_row`）、`bdd99dc`（保留键 `r4_provenance` + 读-改-写，修掉"整列替换抹掉复核收据"这一真实缺陷）、`9db3394`（逐列规则 + 读侧 `blocked`）；记录 [evidence/b05-implementation.md](evidence/b05-implementation.md)、计划 [evidence/b05-plan.md](evidence/b05-plan.md)。
- **核心修复**：B05 之前 `prefer_new` 分支用新字典**整列替换** `documents.metadata_json`，会抹掉 `prompt_injection.py` 写在同一列的复核收据（`resolver` 把它作为 `prompt_injection_status` 暴露给下游）——现在读-改-写，**其他模块的键一律存活**。
- **新增**：保留键 `r4_provenance`（设计形状 `{schema_version, fields:{<列/键>:{value,sources,conflicts}}}`，**只存 hash 不存原文**）；逐列规则（补空 / 保留已确认值 / 声明压派生 / 真冲突保留全部候选）；`source_status` 取最新观测；`primary_source_id` 每次扫描按 B02 顺序重选；读侧 `query_filing_candidates` 新增 `provenance` / `conflicts` / `metadata_status`（有冲突 = `blocked`）。
- **两条需复审/owner 过目的发现**：**F-B05-1** —— "声明值 vs 派生值"是实施期细化（设计正文没定义"声明"），它由一条**冻结断言**逼出（`test_writer_dedup_ignores_dayu_portfolio_locations`，`git stash` 对照确认）；**F-B05-2** —— 两处行为变化（已确认单值不再被更优先捕获覆盖；`published_date` 不再无条件 COALESCE），后果是冲突场景下解析可能 **fail-closed** 并需要重新获取，读侧会显示 `blocked`。
- **验收/复跑**：F10 `test_r4b05_metadata_provenance.py` **6 用例**通过；全量 **2706 passed / 7 skipped**，唯一失败 `test_pytest_temp_worker_governance_fixture_is_autouse_safe` 是**环境残留**（早先被中断的运行留下的 worker 进程；在 pre-change 代码上同样失败，清理后通过）；覆盖率 `scanner.py` **91.31 %**（冻结底 90.5）、`service.py` 95.20 %；两张棘轮表 **4 passed**；`ruff` clean。
- **待办**：B05 的独立复审（`B.VR`，新会话）；随后 B01 → B03 → B06 → B07。owner 待裁：S-10、S-11、S-12。

## 2026-09-12（实施期）— **B04 已实施**（验收 + 发现登记；产品代码零改动）+ `B.VR` b04 复审 `accepted_with_findings`

- **交付**：`company-wiki/tests/contract/test_r4b04_reference_stability.py`（4 用例，sha256(16) `6039984dfb394e46`，提交 `bc3590f`）+ 发现 **F-B04-1 / F-B04-2** + 变异 harness `evidence/b04_mutation_check.py`（5 变异全 KILLED，跑完还原）；记录 [evidence/b04-implementation.md](evidence/b04-implementation.md)、原始输出 [evidence/b04-test-run.txt](evidence/b04-test-run.txt)（绑定 `bc3590f`）。
- **验收结论**：① 搬家（同 root 换路径 + 重扫）**不破坏引用**——`document_id`/`source_id`/`content_sha256` 不变、`download_required=false`，只有 locator 变化，旧行被标 `missing`；② `location_id` 是 `(root_id, relative_path)` 的纯函数 = 定位子提示；③ 请求钉住 `provider_document_id` 时，另一修订**不会**被当成它服务。
- **发现**：
  - **F-B04-1**（**原措辞经复审更正**）：同一路径被新修订覆盖 ⇒ 旧副本 **active locator 消失 + 旧字节被物理销毁**；若旧版本在别处仍有副本，引用照常 `reused_exact`；`reader.resolve_handle`（只读 documents/sources、不看 locations）**仍会作答**——所以"引用不可再解引用"的旧说法不成立。设计 §B04 目标 3 因此是**有条件**成立。补救 (ii) 快照 vs (iii) 合同级限制 → 待 owner（**S-12**）；(iv) 读侧诊断细化由作者**明确否决**（理由在 F-B04-1）。
  - **F-B04-2**（reviewer 发现）：只搬 PDF、不搬 sidecar ⇒ 文档掉出 `annual_report` 候选切片，`resolve` 返回 `MISSING` 且 **trace 为空**（静默）→ 登记，建议在 B06/B07 的 preflight/资格标签里处理。
- **复跑**：新用例 4 passed；B04+B02+门+棘轮合集 **69 passed**；`ruff` clean；变异 M3/M4/M5/M6/M7 **全 KILLED**（原始输出见 [evidence/b04-test-run.txt](evidence/b04-test-run.txt) 与本文档提交说明）。
- **复审要点（已全部落盘）**：`B.VR` b04 复现了全部数字，指出 2×P2（F-B04-1 后果陈述夸大、"L03 由 B02 组限定保证"归因错误）+ 4×P3（含"设计目标已在 B02 后成立"过度概括、补救表未标注各自恢复什么、证据未绑定被审提交、本步缺变异记录）。
- **待办**：B05（落地计划已写：[evidence/b05-plan.md](evidence/b05-plan.md)），随后 B01 → B03 → B06 → B07。

## 2026-09-12（实施期，第二轮复审后）— **B02 rev3**（B.VR rev2 = accepted_with_findings，5 条已逐条处置）

- **独立复审 rev2**：新会话，记录 [reviews/B.VR-b02-rev2.json](reviews/B.VR-b02-rev2.json)，verdict = **accepted_with_findings**（0×P0/0×P1/2×P2/3×P3）。它**原样重跑**了 rev1 的两条 P1 反例并确认真的修好；独立复现了 23/23/10/787、覆盖率 87.29 %/95.16 %、复杂度棘轮、ruff；做了 7 个变异（6 个被杀）。
- **两条 P2（真问题）**：
  1. **B-VR02R2-01**：rev2 把"凭声明回退"写成 rank-1 验证失败就**立即返回** → 漂移的首选副本压过了同组内**可验证**的副本（claim「第一个验证通过的候选被服务」不成立）。
  2. **B-VR02R2-02**：**S-10 的登记理由被反例证伪** —— `.rejections` 副本占最优优先级 + 唯一合格副本漂移时，pre-B02 = `missing`、rev2 = `reused_exact` 服务了 hash 不匹配的字节 → "不宽于 pre-B02"不成立（若带着这句话去请 owner 批准，就是**误导**）。
- **rev3 处置**：凭声明回退**移到整轮遍历之后**（验证副本永远优先）；读取中途取消不再返回句柄；补外 source 组回归用例（杀掉存活的 M6）；重生成探针 JSON、重写测试 docstring、核对证据行锚。**当时写的"锚定到 pre-B02 会服务的那一行（构造性保证不宽于 pre-B02）"随后被 `B.VR` rev3 证伪** → 最终口径 = [evidence/b02-implementation.md](evidence/b02-implementation.md) §3 的 a–d 差异清单（单一权威处）。
- **逐条处置表**：[findings.md](findings.md) F-B02-5；S-10 已在 [owner-scope-decisions](owner-scope-decisions-2026-09-12.md) §9 按 rev3 规则重述。
- **B04 计划**已排布（[evidence/b04-plan.md](evidence/b04-plan.md)），待 B02 rev3 复审关闭后实施。

### 本步实际副作用（如实，含 rev3）

- **执行过**：修改 `company-wiki` 的 2 个 allowed 产品文件 + 1 个测试文件；本机运行 `pytest`（含全量套件与覆盖率）、`ruff`、只读探针（合成 fixture，临时目录）；`git worktree`（干净 HEAD 源码，用于 RED 对照）。
- **未执行**：任何网络/下载/LLM、任何产品写入、DB 写入、任务注册、worker 操作、删除；**未**在生产 catalog 上做行为探针。
- **注意**：全量 `pytest` 中的既有用例会**只读**打开生产 catalog（阶段 A 已归因，属已知限制）；并发负载下 2 条 SLO/真实旅程用例可能瞬时失败（单独重跑通过，reviewer 亦复现此现象）。

## 2026-09-12（实施期，复审后）— **B02 rev2**（B.VR rev1 = rejected，7 条已逐条处置）

- **独立复审**：`B.VR`（新会话）verdict = **rejected**，记录 [reviews/B.VR-b02.json](reviews/B.VR-b02.json)：2×P1 / 2×P2 / 3×P3。它独立复跑了全套并**逐位复现**了作者的数字（全量 2684 passed / 7 skipped、覆盖率 resolver 87.36% / service 95.16%、复杂度表 45/103、RED/GREEN 探针、S-10 的因果实验、变异测试证明新用例"有牙"），同时发现作者自检**漏掉的两条 P1**。
- **两条 P1（真缺陷）**：
  1. **B-VR02-01**：rev1 的"回退到任意可读副本"会把**不同修订**当本版本发出（reviewer 反例：删首选+第三份、把存活那份改成不同字节 → rev1 返回 `reused_exact`，pre-B02 返回 `missing`）——既是相对 pre-B02 的 fail-open，也违反本 run 自己的 L03 验收。
  2. **B-VR02-02**：rev1 让 `is_canonical` 变成"有资格才选"，使**未修改的** `duplicate_cleanup.list_groups()`（`next(...)` 无默认值）在同文档两份 `.rejections` 副本时抛 `StopIteration`，`duplicates` CLI 整条命令 exit 1。
- **rev2 处置**：非首选副本只在**字节验证通过**时服务（否则不返回句柄）；恢复遗留注解契约（`is_canonical`/`duplicate_relation`/`_duplicate_summary` 全部回到 pre-B02 口径），B02 只新增资格轨；`_ReadBudget` 计数**每请求重置**（取消粘性）；理由带 source 组后缀、`tried` 非空必写；`.rejections` 改**按路径段**匹配；水合掩码补 `RECALL_ON_OPEN`。新增 7 个回归用例（共 **23** 个）。
- **逐条处置表**：[findings.md](findings.md) F-B02-4；偏差重述为 **S-10**（首选副本信任级 vs 非首选硬门）与 **S-11**（预算耗尽不是 `blocked`）。
- **完整记录**：[evidence/b02-implementation.md](evidence/b02-implementation.md)（rev2 更新）；机器可读结果：[evidence/b02-verification.json](evidence/b02-verification.json)。

### 本步实际副作用（如实，含 rev2）

- **执行过**：修改 `company-wiki` 的 2 个 allowed 产品文件 + 新增 1 个测试文件；本机运行 `pytest`（含全量套件与覆盖率）、`ruff`、只读探针（合成 fixture，临时目录）；`git worktree`（干净 HEAD 源码，用于 RED 对照）。
- **未执行**：任何网络/下载/LLM、任何产品写入、DB 写入、任务注册、worker 操作、删除；**未**在生产 catalog 上做行为探针。
- **注意**：全量 `pytest` 中的既有用例会**只读**打开生产 catalog（阶段 A 已归因，属已知限制）。

## 2026-09-12（实施期）— **B02 已实施**（F1+F2+F10；待 B.VR 独立复审）

- **授权**：owner「全按推荐：定 S-7/S-8 并开始实施」→ [owner-scope-decisions-2026-09-12.md](owner-scope-decisions-2026-09-12.md) §8。
- **本步改了什么**：`service.py`（资格先于排序 + `candidate_rank`/`exclusion_reason`）、`resolver.py`（有序合格清单上的逐份尝试 + 段 3 字节校验 + 预算/取消 + `_Selection`）、新增 `tests/contract/test_r4b02_candidate_selection.py`（16 用例）。**没有**新增产品模块、**没有**改棘轮表、**没有**改 `SourceHandle` 字段。
- **完整记录**：[evidence/b02-implementation.md](evidence/b02-implementation.md)（含 RED/GREEN 探针、命令、副作用、未做清单）；机器可读结果：[evidence/b02-verification.json](evidence/b02-verification.json)。
- **本步新发现**：
  1. **F-B02-1（P1，需 owner 知情）**：设计 §B02 段 3 的"同 hash 硬门"与 A 侧 4 条**冻结断言**的合成 fixture 冲突（fixture 的字节与声明 hash 本来就不同）→ 实施为"优先 + 逐候选诊断"，硬门归 B03；登记为待定项 **S-10**。
  2. **F-B02-2（P2）**：`exact_duplicate_location_count` / `exact_original_copy_count` 口径改为**只统计合格副本**（`.rejections` 行不再计入）。
  3. **F-B02-3（P3）**：首轮实现把 `dropbox_stock`/`Dropbox` 写进 docstring，被 **FC-1201 根 token 门**挡下 → 改为与 root 无关的措辞后通过（门按设计生效，非误报）。

### 本步实际副作用（如实）

- **执行过**：修改 `company-wiki` 的 2 个 allowed 产品文件 + 新增 1 个测试文件；本机运行 `pytest`（含全量套件与覆盖率）、`ruff`、只读探针（合成 fixture，临时目录）；`git worktree`（干净 HEAD 源码，用于 RED 对照）。
- **未执行**：任何网络/下载/LLM、任何产品写入、DB 写入、任务注册、worker 操作、删除；**未**在生产 catalog 上做行为探针。
- **注意**：全量 `pytest` 中的既有用例会**只读**打开生产 catalog（阶段 A 已归因，属已知限制）。

## 2026-09-12 07:43 — B 阶段启动（设计，DESIGN_ONLY；时间戳为实测，v0.1.2 更正）

- **授权**：owner「接着做 B 阶段，一直做不要停」（2026-09-11 夜）。按 handbook §1 第 5 项 + §3 解释为：**B 的设计可连续推进**；产品代码写入与 `--help` 之外的命令执行**仍需精确批准**。
- **起点**：阶段 A 收口 —— A.DR rev3 = `accepted_with_findings`（0×P0/P1）、owner 六项裁定（G2）已定、A02 封版（`root-contract v0.4` → 现 **v0.4.2**）、CI 全绿（当前 revenue #153 / wiki #107）。
- **本 run 建立**：`revenue-forecast/assurance/runs/2026-09-11_r4-phase-b/`（**不在审计证据目录内**）。

### 1. 本轮交付（全部为文档）

| 文件 | 内容 |
|---|---|
| [task_plan.md](task_plan.md) | B01–B10 状态、B.DR/B.VR/B.AR/D.SAFE 门、停止条件、交付边界 |
| [b-design.md](b-design.md) | **v0.1.6**（B01 含 12 行/16 字段 owner 与版本映射表）、B02（四段式 + `_handle` 同改 + 禁联网资格判定）、B03（读后复验闭合 TOCTOU）、B04、B05（覆盖整条 UPDATE；持久化决策）、B06（preview 合同归 B06）、B07（范围重划表） |
| [file-scope.md](file-scope.md) | **v0.1.6**：8 个候选文件 + F10 新增测试 + §1b 只读调用目标的绝对路径、符号、行号、冻结哈希与"是否 A01 冻结项"逐行标注；`policy_2x` 的**在产导出路径**改为禁区首行；owner R-6 的排序锚点分类（11 个） |
| [test-acceptance-map.md](test-acceptance-map.md) | B 步骤 → L/P/O/M 映射、**裁定↔测试绑定表**、反覆盖更正（O03 = 交叉）、完成定义 |
| [risk-and-stop-rules.md](risk-and-stop-rules.md) | H01/D.SAFE 交叉、10 条硬停止、6 类"看起来跑通"陷阱、引用口径更正 |
| [findings.md](findings.md) | **F-B01-1：B.DR 20 条发现逐条处置表**；F-B00-1…5 |
| Phase A 侧 | [a05-corpus-sample-plan.md](../2026-09-11_r4-phase-a/a05-corpus-sample-plan.md)、[a06-baseline-plan.md](../2026-09-11_r4-phase-a/a06-baseline-plan.md)、[command-manifest-readonly.json](../2026-09-11_r4-phase-a/command-manifest-readonly.json) |

### 2. 关键设计结论（一句话版）

1. **B02 与 B05 同根**："位置/优先级被当成业务判据"——B02 把它从**资格**降为**排序**，B05 把它从 **metadata 真伪**彻底移除；两次改动一次收敛。
2. **B03 的字节安全**靠"固定句柄 → 受控快照 → 显式失败"三级，**禁止**只信 mtime/文件名，**禁止**在 query/open 内隐式建快照还宣称零写。
3. **B06/B07** 靠 `preview` 与 `verified_input` 的**资格标签**分离，配一个版本化读取合同 + 边界 adapter；缺 policy **不得**静默退回 `companies`。
4. **B08 的隔离副本不必是 50 GB 拷贝**：机制层用小 catalog（既有测试机制），只有 R1 真实读取需要真实字节——已写入 findings F-B00-3。

### 2b. 实际副作用（v0.1.3 更正为"已发生"，B-DR3-11）

| 动作 | 状态 | 证据 |
|---|---|---|
| 推送本 run 目录（`1b4bab4`/`4c37ca3`/`9d21963`/`472bd206`/`8e3396b`） | **已发生**（`origin/main` = `8e3396b`；CI #145/#146/#147 全 success） | GitHub Actions |
| 推送触发的强制 gate 打开生产 catalog（只读） | **已发生**（`-shm` 前移：2026-09-12 08:32:21 等） | [../2026-09-11_r4-phase-a/boundary-audit.md](../2026-09-11_r4-phase-a/boundary-audit.md) |
| A06-D0 基线运行（`pytest`，CI 等价子集） | **已发生**，且**打开了生产 catalog（只读）**（`-shm` 08:11:45 / 08:13:46） | [../2026-09-11_r4-phase-a/baseline/a06-d0-baseline.md](../2026-09-11_r4-phase-a/baseline/a06-d0-baseline.md) |
| 本 run 内的 CLI（含 `--help`） | **未执行** | 作者声明（无独立观测产物——该限制已登记为 G5） |

> v0.1.2 之前此处用**将来时**描述推送，属陈述失真；现按实际发生登记。

### 3. 本步实际副作用（如实）

- **执行过**：只读文件读取（源码/grep/哈希/行号）、文档写作。
- **未执行**：任何 CLI（含 `--help`）、任何数据命令、网络、产品写入、任务/worker 操作、删除。
- **注意**：本 run 的推送仍会触发 revenue 的强制 pre-push gate，其 real-data 套件会**只读**打开生产 catalog（阶段 A 已归因并披露）。

### 4. 未完成 / 阻塞（不阻塞设计，阻塞实施）

1. **B.DR rev6 = rejected**（3×P1 / 6×P2 / 4×P3，均为文本与落点级）；v0.1.6 已逐条处置，并新增**可复跑**的双向自证工具 `evidence/claim_fact_audit.py`（早期版本只有断言没有模式/命令/输出，已被 rev6 正确驳回）。
2. **B 的 DEV 工作包与文件范围批准**（[file-scope.md](file-scope.md)）——owner 一句话即可，之后才能改代码。
3. **隔离副本（G8）**——建议按 findings F-B00-3 分两级；B.DR 已独立复核该技术前提（wiki 既有测试确实用 `tmp_path` 造 catalog）。
4. **A05 样本清单（G7）与只读命令 manifest**——已写好待确认。
5. **A-AR-02 的桥接表**（13 行无法指派 → E01–E13 / U117 / FC903 / CL·AC → L/P/O/M）——A08 的整改项，待做。
6. **B05 的 provenance 持久化**——本轮决定**不落库**；若 owner 要求持久化，需独立工作包（含 `store.py` DDL/迁移）。

### 5. 变更记录（真实时间）

| 时间（本地） | 变更 |
|---|---|
| 2026-09-12 07:43–07:46 | 建立 B run 目录；交付 v0.1 六份文档 + Phase A 三份准备件；提交 `B.DR` 复审（**已推送**：`1b4bab4`/`4c37ca3` 在 revenue #145） |
| 2026-09-12 07:54–08:05 | **B.DR = rejected**（20 条 / 8 条 claim 未复现）、**A07 = accepted_with_findings**、**A08 = rejected**（三份复审共同命中同一 P0） |
| 2026-09-12 08:05–11:20 | 阶段 A → **v0.4.1** 再 → **v0.4.2**；B → **v0.1.1 → v0.1.2 → v0.1.3 → v0.1.4 → v0.1.5 → v0.1.6**（对应 B.DR rev1–rev6 六轮）；A06-D0 基线产出（787 unit / 1748 contract passed）；两份 checkpoint 重建（`reviews/**` 纳入产物清单）；上述提交**已推送**，CI #146 success |
| 2026-09-12（实施期） | owner 授权实施 → **B02 实施**（`service.py` + `resolver.py` + 新增 F10 测试 16 用例）；RED/GREEN 探针（`git worktree` 对照）落盘；全量套件 + 覆盖率/复杂度棘轮 + ruff + FC-1201 门复跑；**偏差登记 S-10**；B 设计/file-scope/task_plan → **v0.1.7**（实施回填，正文语义未变） |
