# B02 实施与验证记录（rev2，2026-09-12）

> 状态：**已实施 rev2**（F1 + F2 + F10）、**B.VR rev1 = rejected 的 7 条已逐条处置**、**待 B.VR rev2**。
> 本页只写**已落盘且可复跑**的事实；每条给命令与输出位置。未做到的一律写在 [§8 未做](#8-未做不得当作已完成)。
> 阅读顺序建议：§0 版本史 → §2 语义 → §3 偏差（S-10/S-11）→ §7 验证 → §8 未做。

## 0. 版本史（哪一版被判、哪一版在盘上）

| 版本 | wiki 提交 | 内容 | 状态 |
|---|---|---|---|
| rev1 | `cab1fd6` | 资格先于排序 + `candidate_rank`/`exclusion_reason`；有序合格清单逐份尝试；预算/取消；`_Selection` | **`B.VR` rev1 = rejected**（2×P1 / 2×P2 / 3×P3，记录 [reviews/B.VR-b02.json](reviews/B.VR-b02.json)） |
| **rev2** | **`350b67a`** | 按上述 7 条逐条修复（非首选副本只服务**验证通过**者、遗留注解契约恢复、预算按请求重置、理由带 source 组、`.rejections` 按路径段、水合掩码补 `RECALL_ON_OPEN`）+ 7 个回归用例 | **本页描述的版本**；待 `B.VR` rev2 |

逐条处置表见 [findings.md](findings.md) F-B02-4。**rev1 的两条 P1 都是作者自检未识别的真缺陷**（一条是相对 pre-B02 的 fail-open 回归，一条打断了未修改模块的既有不变量）。

## 1. 改了什么（落点与哈希）

| 落点 | 实施后位置 | 内容 |
|---|---|---|
| **F1** `src/company_wiki/source_catalog/service.py` | `_REJECTIONS_SEGMENT` `:26`；`_location_exclusion_reason` `:35-63`；`_location_order_key` `:66-80`；`_annotate_locations` `:670-717`；`_duplicate_summary` `:719-753` | **新增**复用资格轨（`candidate_rank` / `exclusion_reason`）；**保留**遗留注解契约（`is_canonical` / `duplicate_relation` / `duplicate_group_id` / 计数口径 = pre-B02） |
| **F2** `src/company_wiki/source_catalog/resolver.py` | 常量 `:152-161`；`_sha256_of_file` `:164`；`_needs_hydration` `:174`；`_ReadBudget`（含 `begin_request`）`:182`；`_local_copy_probe` `:229`；`_verify_candidate` `:248`；`_candidate_reason` `:281`；`_Selection` `:421`；`__init__(read_budget=…)` `:871`；`resolve`（预算重置 / 资格轨过滤 / trace）`:916-1135`；`_select_candidate` `:1319-1395`；`_handle` `:1397` | 只对**本版本自身 source 组**的有序合格候选逐份尝试；**首选可凭声明服务**、**非首选必须字节验证通过**；预算/取消；返回 `_Selection`（选了哪份 + 为什么） |
| **F10** `tests/contract/test_r4b02_candidate_selection.py` | 新增文件 | **23** 个用例：L01/L02/L03/L04、预算/取消/每请求重置、零网络/水合、**B-VR02-01…07 的 7 个回归**、S-7 棘轮表冻结 |

哈希与规模（rev2 实测）：

| 文件 | sha256(16) | 字节 |
|---|---|---|
| `service.py` | `fe2018305c805428` | 58 909 |
| `resolver.py` | `ae31884613bdd48a` | 68 984 |
| `test_r4b02_candidate_selection.py` | `01f2d340c685a22f` | 32 275 |

`git diff --stat cab1fd6 350b67a -- src tests` = **3 files changed, 382 insertions(+), 85 deletions(-)**。
file-scope §1 里 F1/F2 的 `6412b19e…`/`6962b258…` 是**开工前**的 A01 §0 冻结输入哈希（按 §5「B 开工即视为已消费」），rev1/rev2 的哈希为本表与 §0。

## 2. 语义（四段式，顺序即语义；rev2 的服务规则在段 3）

| 段 | 实现落点 | 规则 |
|---|---|---|
| 1 注册/能力 | locations SQL 的 `JOIN roots`（结构性）+ resolver `reusable_root_ids` | 未注册 root 不产生行；复用能力由 `reusable_root_kinds` 决定 |
| 2 状态与安全 | `_location_exclusion_reason` | `original_primary` + `location_status='active'` + `source_id` 非空 + 路径**段**不含 `.rejections`；**保持"排除"语义** |
| 3 可读且同 hash | `_local_copy_probe` → `_verify_candidate` | 先 `stat`（**不读字节、不触发水合**）→ 全文件流式 sha256；**首选副本（rank 1，属于本版本自身 source 组）可凭目录声明服务**（trace 记 `unverified_preferred_copy`），**非首选副本只有验证通过才被服务**，否则不返回句柄 |
| 4 健康/IO 偏好 | `_location_order_key` | 仅在**已合格集合内**按 `priority → root_id → relative_path → location_id` 排序，只决定"先用哪份" |

**输出**：每个 location 带 `candidate_rank`（1..N，0=被排除）与 `exclusion_reason`；候选集合被限定在**该文档自身 `source_id`** 的合格行内。**遗留注解**（`is_canonical`/`duplicate_relation`/`_duplicate_summary` 计数）仍按 pre-B02 规则在该组**全部 active original_primary** 上计算 —— 复用判定看资格轨，清理/导出看遗留轨（这正是 `B.VR` rev1 的 P1-02 要求的分离）。

**诊断**（`resolve.debug_trace`）：命中首选且无失败候选时保持既有 trace 形状（`…: matched`）；否则追加 `…: <selection_reason>` 与逐候选 `…: candidate <location_id>:<reason>`。理由形如 `verified_candidate_rank_1:<source sha 前 12>`（跨 source 组不歧义），`tried` **只要非空就写**。

## 3. 与设计正文的偏差（**S-10 / S-11**，待 owner 确认）

设计 §B02 段 3 要求"可读且同 hash"是**硬门**。实际实现（rev2 收紧后的精确表述）：

1. **首选副本**（rank 1，属于该文档自身 source 组）：可凭目录声明服务 —— 这是 **pre-B02 的信任级**，也是 A 侧冻结 fixture 仍能复用的唯一原因；trace 记 `unverified_preferred_copy` + 具体原因（`content_sha256_mismatch:<sha 前 12>` / `budget_exceeded` / `exceeds_candidate_cap` …）；
2. **非首选副本**：**只有字节验证通过才会被服务**；否则一律不返回句柄 → `unavailable`（MISSING）。**绝不"可读即用"**；
3. **字节级硬门归 B03 的读路径**（"只返回验证版本字节或明确失败"）——B03 落地前，首选副本的漂移不会被拦。

**为什么让步**：A 侧冻结断言构造的合成目录里，文件字节与其声明的 `content_sha256` **和** `byte_size` 都不一致（`test_source_catalog_sql_pushdown.py` 甚至把 13 B 的文件声明为 1000 B；`test_source_catalog_determinism.py` 用 `b"%PDF-fake"` 配 `sha256(b"same-bytes")`），任何"先验证再服务首选"的硬门都会失败这 4 条既有断言：

- `tests/contract/test_source_catalog_determinism.py::test_same_hash_three_roots_picks_priority_primary_preserves_all`
- `tests/contract/test_source_catalog_determinism.py::test_same_period_different_hash_is_ambiguous`
- `tests/contract/test_source_catalog_sql_pushdown.py::test_resolver_uses_sql_pushdown_not_all_table_query`
- `tests/contract/test_source_catalog_sql_pushdown.py::test_old_period_not_shadowed_by_cap`

复跑：`python -m pytest tests/contract/test_source_catalog_determinism.py tests/contract/test_source_catalog_sql_pushdown.py -q`（硬门实现下上述 4 条 FAILED；当前实现 5+5 全通过）。S-1 只批准**新增**测试、**不得修改既有断言** → 让步只能在实现侧。

**这不是"降级成不校验"**：段 3 仍真读字节；验证通过的候选优先；非首选副本一律硬门；`resolve` 本身从不授权下载（`download_allowed` 只回显 `request.allow_download`）。
**残余风险（如实）**：首选副本可能字节已漂移而被服务（trace 已标注），读路径在 B03 落地前不拦它。这**不宽于** pre-B02（pre-B02 对首选无条件信任且从不校验字节），并由 `test_r4b02_different_bytes_copy_is_never_served_as_the_same_version` 守住"非首选不得 fail-open"。

**S-11（另一处命名偏差）**：预算耗尽（`budget_exceeded`）对外**不是**设计写的 `blocked`，而是"按 pre-B02 信任级服务首选副本 + trace 标记"。理由：`ResolutionStatus` 只有五个值（A03 §2.4 不新增第六值）；若 owner 要真正的 `blocked`，需先改五值模型（另立工作包）。`_ReadBudget` 的计数**每次请求重置**（取消保持粘性）。

## 4. 预算与取消（L06/L12）

| 约束 | 默认 | 超限行为 |
|---|---|---|
| 每候选字节上限 | 256 MiB | `exceeds_candidate_cap`（不读） |
| 单请求候选数 | 64 | `budget_exceeded`（停止继续读） |
| 单请求流式读总量 | 2 GiB | `budget_exceeded` |
| 取消 | 调用方 `_ReadBudget.cancel()` | 不再读任何候选字节，且**不返回句柄**（`candidate_verification_cancelled`，即使首选也不返回） |
| 每请求重置 | `resolve()` 调 `budget.begin_request()` | 注入/复用同一 budget 不会让后续请求静默失去验证（B-VR02-04） |

## 5. 明确没改（边界）

- **不新增产品模块**（S-7/work-package：新增文件不在 allowed 集）；`test_r4b02_no_new_source_catalog_module_was_added` 断言这一点。
- **不改棘轮表**：`test_r4b02_complexity_ratchet_table_is_not_edited` 断言 `FROZEN_MAX["service.py"] == 45`、`["resolver.py"] == 103`。
- `SourceHandle` 字段**不变**（对外 payload 形状不变）；**遗留注解语义不变**（见 §2/§6）；新增的只是**读取期字典注记**（`candidate_rank` / `exclusion_reason` / `verified_sha256`），不落库、不改 schema。
- 其他排序锚点（`canonical_writer.py` / `duplicate_cleanup.py` / `normalizer.py` / `evidence_query.py` 等 6 处）按 file-scope §3 **仍归 C/D**，本步未动。
- 写面、外发面、worker 面一律未动。

## 6. 副作用（rev2 后）

1. **计数口径：无变化**（rev2 撤销了 rev1 的口径改动）——`exact_duplicate_location_count` / `exact_original_copy_count` / `canonical_*` 与 pre-B02 完全一致；被 provider 拒绝的副本**仍在**清理计划的可回收集合里（`test_r4b02_rejected_copy_stays_reclaimable_next_to_healthy_copies` 断言 2 组 / 3 个可回收副本 = reviewer 实测的 pre-B02 值）。
2. **读放大**：段 3 会真的读候选文件（只读、有上限）。生产上只有通过全部身份/期间门的文档才进入段 3。
3. **trace 变化**：仅在"不是首选"或"有失败候选"时新增行，正常命中保持原样。
4. `query_filing_candidates` 的返回**新增两个键**（`candidate_rank`/`exclusion_reason`）——加性变化，不改既有键的语义（B-VR02-05 亦确认没有泄漏进 DB / resolve envelope）。

## 7. 验证证据（命令 → 结果）

| 证据 | 命令 | 结果 |
|---|---|---|
| **独立复审（rev1）** | 新会话 subagent，记录 [reviews/B.VR-b02.json](reviews/B.VR-b02.json) | **rejected**：2×P1 / 2×P2 / 3×P3；它**独立逐位复现**了作者的全量/覆盖率/探针数字，并发现作者自检漏掉的两条 P1 |
| 新增用例（rev2） | `python -m pytest tests/contract/test_r4b02_candidate_selection.py -q` | **23 passed**（含 7 个 B-VR02 回归） |
| 目标回归 | `python -m pytest -q tests/contract/test_source_catalog_determinism.py tests/contract/test_source_catalog_sql_pushdown.py tests/contract/test_zr403_dedupe_resolver_generalization.py tests/contract/test_source_catalog_fail_closed.py` | **23 passed** |
| 根 token 门 | `python -m pytest -q tests/contract/test_fc1201_root_hardcode_gate.py tests/contract/test_future_root_config_only.py` | **10 passed**（rev1 首轮曾 3 条 FAILED：docstring 写了 `dropbox_stock`；已改写） |
| 单元测试 | `python -m pytest tests/unit -q` | **787 passed** |
| 全量 + 覆盖率 | `python -m pytest tests/ -q --tb=line --cov=src/company_wiki/source_catalog --cov-branch --cov-report=json` | **2691 passed, 7 skipped, 0 failed**（915 s；rev1 时 2684，新增 7 个回归用例） |
| 覆盖率棘轮 | `FC1204_COVERAGE_GATE=1 python -m pytest -q tests/contract/test_fc1204_coverage_ratchet.py`（**必须紧接上面的 `--cov` 运行**，见 §7 注） | **2 passed** —— `resolver.py` **87.29 %**（TIER2 门 86 → 容差底 85.5）、`service.py` **95.16 %**（TIER1 门 95 → 容差底 94.5） |
| 棘轮"有牙"的实证 | 同一次全量测量在**新增测试尚未落盘时**得到 `resolver.py` = **61.3 %**（FAILED `< 86 %`） | **S-9** 的约束是真的 |
| 复杂度棘轮 | `python -m pytest -q tests/contract/test_fc1204_complexity_ratchet.py` | **2 passed**（`service.py` 45 / `resolver.py` 103 未动） |
| 静态检查 | `python -m ruff check src tests/unit tests/contract scripts` | All checks passed |
| RED/GREEN 探针 | `evidence/b02_red_green_probe.py`（pre 用 `git worktree` 的 HEAD 源码） | pre：撤销首选后 `missing`（`placeholder_no_handle`）；post：`reused_exact`（dropbox 副本，`verified_candidate_rank_2`） |
| 汇总（可复跑） | `python evidence/b02_verify.py --fast` | **7/7 executed checks pass** → [b02-verification.json](b02-verification.json)（含命令、返回码、摘要行、`coverage.json` 时间戳与年龄、三个改动文件哈希、`gate_precondition`） |

> **§7 注（B-VR02-06）**：仓库**跟踪**着一份陈旧的 `coverage.json`（2026-08-17 测量），而棘轮门读的就是这个文件 → **单独**运行棘轮命令会红，这不是本次改动导致的。证据文件里已记录该前置条件与 `coverage.json` 的时间戳/年龄。

## 8. 未做（不得当作已完成）

- **B04 / B05 / B01 / B03 / B06 / B07 一步都没做**（本步只有 B02）。
- **B03 的"读后复验/TOCTOU 闭合"未实现** → 首选副本的字节漂移目前无人拦（S-10 的另一半）。
- **B-payload-hash 仍未执行**（包内无基线、取值需待批 CLI）；本步只声明"未改 `SourceHandle` 字段与 `export_policy`"，**没有**做过字节/哈希比对。
- 未在生产 catalog 上验证（全部为合成 fixture 与既有测试）；未使用 G8 隔离副本；未验证真实云占位层（本机不可得）。
- **S-10 / S-11 仍待 owner 裁定**；`B.VR` rev2 复审未做。
