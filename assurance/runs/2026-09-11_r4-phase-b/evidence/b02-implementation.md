# B02 实施与验证记录（rev3，2026-09-12）

> 状态：**已实施 rev3**（F1 + F2 + F10）；`B.VR` rev1 = **rejected**（7 条已处置）、rev2 = **accepted_with_findings**（5 条已处置）；**S-10 / S-11 待 owner**。
> 本页只写**已落盘且可复跑**的事实；每条给命令与输出位置。未做到的一律写在 [§8 未做](#8-未做不得当作已完成)。
> 阅读顺序建议：§0 版本史 → §2 语义 → §3 偏差（S-10/S-11）→ §7 验证 → §8 未做。

## 0. 版本史（哪一版被判、哪一版在盘上）

| 版本 | wiki 提交 | 内容 | 状态 |
|---|---|---|---|
| rev1 | `cab1fd6` | 资格先于排序 + `candidate_rank`/`exclusion_reason`；有序合格清单逐份尝试；预算/取消；`_Selection` | **`B.VR` rev1 = rejected**（2×P1 / 2×P2 / 3×P3，[reviews/B.VR-b02.json](reviews/B.VR-b02.json)） |
| rev2 | `350b67a` | 非首选副本只服务验证通过者、遗留注解契约恢复、预算按请求重置、理由带 source 组、`.rejections` 按路径段、水合掩码补 `RECALL_ON_OPEN` | **`B.VR` rev2 = accepted_with_findings**（2×P2 / 3×P3，[reviews/B.VR-b02-rev2.json](reviews/B.VR-b02-rev2.json)） |
| rev3 | `182846b` | 凭声明回退**移到遍历之后**（验证副本永远优先）+ 锚定到 legacy canonical + 读取中途取消 + 外 source 组用例 | **`B.VR` rev3 = accepted_with_findings**（1×P2 / 6×P3，[reviews/B.VR-b02-rev3.json](reviews/B.VR-b02-rev3.json)） |
| **rev4** | **`da5e0f5`** | 规则 2 的**精确表述**（列出与 pre-B02 的两处差异，撤销"由构造保证"的说法）+ 锚点谓词删死条件 + 理由报告**锚点自身**的失败状态 + 3 个回归（收尾取消 / 理由 / 差异钉住）；M5/M6/M7 三个存活变异全部被杀 | **本页描述的版本**；待 `B.VR` rev4 定点复核 |

逐条处置表见 [findings.md](findings.md) F-B02-4（rev1）、F-B02-5（rev2）、F-B02-6（rev3）。**三轮独立复审各抓到作者自检漏掉的真实缺陷**（rev1：fail-open 回退 + `duplicate_cleanup` `StopIteration`；rev2：凭声明回退提前返回 + S-10 理由被证伪；rev3：**S-10 的理由句再次为假** + 3 个存活变异 + 4 处证据文字不实）。

## 1. 改了什么（落点与哈希）

| 落点 | 实施后位置 | 内容 |
|---|---|---|
| **F1** `src/company_wiki/source_catalog/service.py` | `_REJECTIONS_SEGMENT` `:27`；`_location_exclusion_reason` `:35`；`_location_order_key` `:65`；`_annotate_locations` `:670`；`_duplicate_summary` `:726` | **新增**复用资格轨（`candidate_rank` / `exclusion_reason`）；**保留**遗留注解契约（`is_canonical` / `duplicate_relation` / `duplicate_group_id` / 计数口径 = pre-B02） |
| **F2** `src/company_wiki/source_catalog/resolver.py` | 常量 `:152-158`；`_sha256_of_file` `:161`；`_needs_hydration` `:171`；`_ReadBudget`（含 `begin_request`）`:181`；`_local_copy_probe` `:224`；`_verify_candidate` `:243`；`_is_rejections_path` `:278`；`_candidate_reason` `:285`；`_Selection` `:435`；`__init__(read_budget=…)` `:885`；`resolve`（预算重置 / 资格轨过滤 `:1090` / trace）`:930-1149`；`_select_candidate` `:1326`；`_handle` `:1444` | 只对**本版本自身 source 组**的有序合格候选逐份尝试；**验证通过的副本永远优先**，仅在无一通过时按目录声明服务**本版本的 legacy canonical**（规则 2，差异见 §3）；预算/取消（含读取中途与收尾守卫）；返回 `_Selection`（选了哪份 + 为什么） |
| **F10** `tests/contract/test_r4b02_candidate_selection.py` | 新增文件 | **30** 个用例：L01/L02/L03/L04、预算/取消/每请求重置/读取中途取消/收尾取消、零网络/水合、外 source 组、验证副本优先、规则 2 的锚定与理由、**与 pre-B02 的两处差异被显式钉住**、rev1 的 7 条 + rev2 的 4 条 + rev3 的 3 条回归、S-7 棘轮表冻结 |

哈希与规模（rev4 实测）：

| 文件 | sha256(16) | 字节 |
|---|---|---|
| `service.py` | `fe2018305c805428` | 58 909 |
| `resolver.py` | `419938604e6a8495` | 71 210 |
| `test_r4b02_candidate_selection.py` | `eca0d54f4a7b7ad0` | 41 685 |

`git diff --stat`（rev3 → rev4）= **2 files changed, 111 insertions(+), 19 deletions(-)**（`resolver.py` 规则 2 谓词与理由串、测试文件新增 3 例）。
`git diff --stat`（步骤起点 `c986c7a` → rev4 `da5e0f5`）= **3 files changed, 1436 insertions(+), 38 deletions(-)**（`resolver.py` +364、`service.py` +80/−…、测试文件 +1030）。
file-scope §1 里 F1/F2 的 `6412b19e…`/`6962b258…` 是**开工前**的 A01 §0 冻结输入哈希（按 §5「B 开工即视为已消费」），rev1/rev2/rev3/rev4 的哈希见 §0 与本表。

> 行锚由脚本从**最终代码**重新解析（`ast`/逐行匹配），不是手写；rev3 的复审（B-VR02R3-04）指出过上一版行锚偏移 1–11 行，本版已按最终代码重算。

## 2. 语义（四段式，顺序即语义；rev2 的服务规则在段 3）

| 段 | 实现落点 | 规则 |
|---|---|---|
| 1 注册/能力 | locations SQL 的 `JOIN roots`（结构性）+ resolver `reusable_root_ids` | 未注册 root 不产生行；复用能力由 `reusable_root_kinds` 决定 |
| 2 状态与安全 | `_location_exclusion_reason` | `original_primary` + `location_status='active'` + `source_id` 非空 + 路径**段**不含 `.rejections`；**保持"排除"语义** |
| 3 可读且同 hash | `_local_copy_probe` → `_verify_candidate` → `_select_candidate` | 先 `stat`（**不读字节、不触发水合**）→ 全文件流式 sha256。**服务规则只有两条**：① **验证通过的副本永远优先被服务**（无论 rank）；② 只有在**没有任何**副本通过验证时，才允许**一行**凭目录声明被服务 —— 且必须是"**pre-B02 会服务的那一行**"（legacy `is_canonical` 且 active / `original_primary` / 非 `.rejections` / 属于本版本），trace 记 `unverified_<状态>_on_pre_b02_canonical`。其余情况一律不返回句柄 |
| 4 健康/IO 偏好 | `_location_order_key` | 仅在**已合格集合内**按 `priority → root_id → relative_path → location_id` 排序，只决定"先用哪份" |

**输出**：每个 location 带 `candidate_rank`（1..N，0=被排除）与 `exclusion_reason`；候选集合被限定在**该文档自身 `source_id`** 的合格行内。**遗留注解**（`is_canonical`/`duplicate_relation`/`_duplicate_summary` 计数）仍按 pre-B02 规则在该组**全部 active original_primary** 上计算 —— 复用判定看资格轨，清理/导出看遗留轨（这正是 `B.VR` rev1 的 P1-02 要求的分离）。

**诊断**（`resolve.debug_trace`）：命中首选且无失败候选时保持既有 trace 形状（`…: matched`）；否则追加 `…: <selection_reason>` 与逐候选 `…: candidate <location_id>:<reason>`。理由形如 `verified_candidate_rank_1:<source sha 前 12>`（跨 source 组不歧义），`tried` **只要非空就写**。

## 3. 与设计正文的偏差（**S-10 / S-11**，待 owner 确认）

设计 §B02 段 3 要求"可读且同 hash"是**硬门**。实际实现（rev3 定稿的精确表述）：

1. **验证通过的副本永远优先**：整轮遍历里第一个字节真正等于请求版本的候选被服务（无论 rank）——这既是"撤首选→自动切换"的落点，也保证漂移的首选不会压过一份**可验证**的同版本副本；
2. **只有在没有任何候选通过验证时**，才允许**一行**凭目录声明被服务：**本版本的合格候选中那一行 legacy `is_canonical`**。理由串记 `unverified_<该行自身的失败状态>_on_pre_b02_canonical`（如 `unverified_content_sha256_mismatch_on_pre_b02_canonical`），逐候选原因在 `tried` 里；
3. 其余任何副本都必须字节验证通过，否则不返回句柄（→ `unavailable`/MISSING）；
4. **取消永不回答**（读取中途取消、收尾守卫、粘性取消都算）；**字节级硬门归 B03 的读路径**（"只返回验证版本字节或明确失败"）——B03 落地前，规则 2 的那一行仍可能字节漂移而被服务（trace 已标注）。

**与 pre-B02 的两处差异（必须列出，不能省略）**：规则 2 的那一行**不是**"pre-B02 会服务的那一行"的逐位复制——pre-B02 有两个缺陷，rev4 **没有恢复**它们：

| # | pre-B02 的谓词 | rev4 的谓词 | 差异方向 |
|---|---|---|---|
| a | `.rejections` 按**子串**匹配 → 路径里只要含该子串就被拒 | 按**路径段**匹配（与 `adapters/dayu.py` 的既有约定一致） | rev4 **更宽**：`my.rejections_backup/2025.pdf` 这类路径在 pre-B02 会被拒、rev4 视为普通候选（`test_r4b02_documented_difference_from_pre_b02_is_pinned` 把这一角显式钉住） |
| b | 不做 source 组限定 → 可能选中并服务**另一版本**的行 | 限定在文档自身 source 组 | rev4 **更严**：外组可读副本不能顶替本版本（`test_r4b02_other_source_group_is_never_served`） |

因此**正确说法**是："rev4 的凭声明信任范围 = pre-B02 的那一行**减去 a、b 两个缺陷**"。在 a（`my.rejections_backup` 类路径）**且**字节漂移的组合下，pre-B02 会 `missing` 而 rev4 会按声明服务该副本（trace 已标注）——这是**刻意保留的差异**（a 本身是缺陷修复），已在 [S-10](owner-scope-decisions-2026-09-12.md) 逐条列出。**除这两处外没有第三种差异**：`B.VR` rev3 用两个反例把这句话逼到当前这个可证伪的形态（[reviews/B.VR-b02-rev3.json](reviews/B.VR-b02-rev3.json) B-VR02R3-01），rev4 据此改写。

**为什么让步**：A 侧冻结断言构造的合成目录里，文件字节与其声明的 `content_sha256` **和** `byte_size` 都不一致（`test_source_catalog_sql_pushdown.py` 甚至把 13 B 的文件声明为 1000 B；`test_source_catalog_determinism.py` 用 `b"%PDF-fake"` 配 `sha256(b"same-bytes")`），任何"先验证再服务首选"的硬门都会失败这 4 条既有断言：

- `tests/contract/test_source_catalog_determinism.py::test_same_hash_three_roots_picks_priority_primary_preserves_all`
- `tests/contract/test_source_catalog_determinism.py::test_same_period_different_hash_is_ambiguous`
- `tests/contract/test_source_catalog_sql_pushdown.py::test_resolver_uses_sql_pushdown_not_all_table_query`
- `tests/contract/test_source_catalog_sql_pushdown.py::test_old_period_not_shadowed_by_cap`

复跑：`python -m pytest tests/contract/test_source_catalog_determinism.py tests/contract/test_source_catalog_sql_pushdown.py -q`（硬门实现下上述 4 条 FAILED；当前实现 5+5 全通过）。S-1 只批准**新增**测试、**不得修改既有断言** → 让步只能在实现侧。

**这段文本被独立复审连续收紧两次**：rev2 写"首选副本（rank 1）凭声明服务"，被反例证明比 pre-B02 **更宽**（`.rejections` 占最优优先级时 pre-B02 = `missing`、rev2 = `reused_exact` 服务了 hash 不匹配的字节，[reviews/B.VR-b02-rev2.json](reviews/B.VR-b02-rev2.json) B-VR02R2-02）；rev3 改成"锚定到 pre-B02 会服务的那一行、故不宽于 pre-B02 由构造保证"，又被两个反例证明**该句为假**（上表 a/b，[reviews/B.VR-b02-rev3.json](reviews/B.VR-b02-rev3.json) B-VR02R3-01）；rev4 才改成上面这张**列出差异**的可证伪写法。

**这不是"降级成不校验"**：段 3 仍真读字节；验证通过的候选优先；其余副本一律硬门；`resolve` 本身从不授权下载（`download_allowed` 只回显 `request.allow_download`）。

**S-11（另一处命名偏差）**：预算耗尽（`budget_exceeded`）对外**不是**设计写的 `blocked`，而是"按 pre-B02 信任级服务首选副本 + trace 标记"。理由：`ResolutionStatus` 只有五个值（A03 §2.4 不新增第六值）；若 owner 要真正的 `blocked`，需先改五值模型（另立工作包）。`_ReadBudget` 的计数**每次请求重置**（取消保持粘性）。

## 4. 预算与取消（L06/L12）

| 约束 | 默认 | 超限行为 |
|---|---|---|
| 每候选字节上限 | 256 MiB | `exceeds_candidate_cap`（不读） |
| 单请求候选数 | 64 | `budget_exceeded`（停止继续读） |
| 单请求流式读总量 | 2 GiB | `budget_exceeded` |
| 取消 | 调用方 `_ReadBudget.cancel()` | 不再读任何候选字节，且**不返回句柄** —— 预取消、读取中途取消、以及取消后同一 budget 的后续请求（粘性）都如此（B-VR02R2-03） |
| 每请求重置 | `resolve()` 调 `budget.begin_request()` | 注入/复用同一 budget 不会让后续请求静默失去验证（B-VR02-04） |

## 5. 明确没改（边界）

- **不新增产品模块**（S-7/work-package：新增文件不在 allowed 集）；`test_r4b02_no_new_source_catalog_module_was_added` 断言这一点。
- **不改棘轮表**：`test_r4b02_complexity_ratchet_table_is_not_edited` 断言 `FROZEN_MAX["service.py"] == 45`、`["resolver.py"] == 103`。
- `SourceHandle` 字段**不变**（对外 payload 形状不变）；**遗留注解语义不变**（见 §2/§6）；新增的只是**读取期字典注记**（`candidate_rank` / `exclusion_reason` / `verified_sha256`），不落库、不改 schema。
- 其他排序锚点（`canonical_writer.py` / `duplicate_cleanup.py` / `normalizer.py` / `evidence_query.py` 等 6 处）按 file-scope §3 **仍归 C/D**，本步未动。
- 写面、外发面、worker 面一律未动。

## 6. 副作用（rev4 后）

1. **计数口径：无变化**（rev2 撤销了 rev1 的口径改动）——`exact_duplicate_location_count` / `exact_original_copy_count` / `canonical_*` 与 pre-B02 完全一致；被 provider 拒绝的副本**仍在**清理计划的可回收集合里（`test_r4b02_rejected_copy_stays_reclaimable_next_to_healthy_copies` 断言 2 组 / 3 个可回收副本 = reviewer 实测的 pre-B02 值）。
2. **读放大**：段 3 会真的读候选文件（只读、有上限）。生产上只有通过全部身份/期间门的文档才进入段 3。
3. **trace 变化**：仅在"不是首选"或"有失败候选"时新增行，正常命中保持原样。
4. `query_filing_candidates` 的返回**新增两个键**（`candidate_rank`/`exclusion_reason`）——加性变化，不改既有键的语义（B-VR02-05 亦确认没有泄漏进 DB / resolve envelope）。
5. **`handle.content_sha256` 的取值有一处会变**（B-VR02R3-05）：当 location 的 `manifest_json.content_sha256` 与 `documents`/`sources` 行的声明**互相冲突**时，句柄报告的是**被验证的字节摘要**（rev2 起），而 pre-B02 报的是目录声明值。这是**有意**的（句柄应当描述它实际指向的字节），但**必须在 B-payload-hash 仍不可执行的情况下如实登记**：没有做过逐字节的 payload 比对，因此**不声称** payload 契约已验证。

## 7. 验证证据（命令 → 结果）

| 证据 | 命令 | 结果 |
|---|---|---|
| **独立复审（rev1）** | 新会话 subagent，记录 [reviews/B.VR-b02.json](reviews/B.VR-b02.json) | **rejected**：2×P1 / 2×P2 / 3×P3；它**独立逐位复现**了作者的全量/覆盖率/探针数字，并发现作者自检漏掉的两条 P1 |
| **独立复审（rev2）** | 新会话 subagent，记录 [reviews/B.VR-b02-rev2.json](reviews/B.VR-b02-rev2.json) | **accepted_with_findings**：0×P0 / 0×P1 / 2×P2 / 3×P3；确认 rev1 两条 P1 **真的修好**（原样重跑反例），抓到"凭声明回退提前返回"与"S-10 理由被证伪" |
| **独立复审（rev3）** | 新会话 subagent，记录 [reviews/B.VR-b02-rev3.json](reviews/B.VR-b02-rev3.json) | **accepted_with_findings**：0×P0 / 0×P1 / **1×P2** / 6×P3；确认前两轮 **4 条反例全部 fixed**，逐位复现 27/23/10/787、覆盖率 87.70 %/95.16 %、棘轮门 2 passed、claim 28/28、`b02_verify` 7/7、探针 JSON 与文件哈希；8 个变异里 **M5/M6/M7 存活**（已全部处置） |
| 新增用例（rev4） | `python -m pytest tests/contract/test_r4b02_candidate_selection.py -q` | **30 passed**（rev1 的 7 条 + rev2 的 4 条 + rev3 的 3 条回归） |
| 变异复查（rev4） | `python evidence/b02_mutation_check.py --all` | **M5 / M6 / M7 全部 KILLED**（rev3 复审时三者存活）；harness 以字节读写、跑完把 `resolver.py` 还原到同一 sha256(16)，并打印前后哈希以便核对 |
| 目标回归 | `python -m pytest -q tests/contract/test_source_catalog_determinism.py tests/contract/test_source_catalog_sql_pushdown.py tests/contract/test_zr403_dedupe_resolver_generalization.py tests/contract/test_source_catalog_fail_closed.py` | **23 passed** |
| 根 token 门 | `python -m pytest -q tests/contract/test_fc1201_root_hardcode_gate.py tests/contract/test_future_root_config_only.py` | **10 passed**（rev1 首轮曾 3 条 FAILED：docstring 写了 `dropbox_stock`；已改写） |
| 单元测试 | `python -m pytest tests/unit -q` | **787 passed** |
| 全量 + 覆盖率 | `python -m pytest tests/ -q --tb=line --cov=src/company_wiki/source_catalog --cov-branch --cov-report=json` | 见下方"全量结果" |
| 覆盖率棘轮 | `FC1204_COVERAGE_GATE=1 python -m pytest -q tests/contract/test_fc1204_coverage_ratchet.py`（**必须紧接上面的 `--cov` 运行**，见 §7 注） | 见下方"全量结果" |
| 复杂度棘轮 | `python -m pytest -q tests/contract/test_fc1204_complexity_ratchet.py` | **2 passed**（`service.py` 45 / `resolver.py` 103 未动） |
| 静态检查 | `python -m ruff check src tests/unit tests/contract scripts` | All checks passed |
| RED/GREEN 探针 | `evidence/b02_red_green_probe.py`（pre 用 `git worktree` 的 HEAD 源码） | 在 rev3 代码上重新生成：pre = `missing`（`placeholder_no_handle`）；post = `reused_exact`（dropbox 副本，`verified_candidate_rank_2:e5a09d70ca5c`）；rev4 未改这段行为 |
| 汇总（可复跑） | `python evidence/b02_verify.py --fast` | **7/7 executed checks pass** → [b02-verification.json](b02-verification.json)（含命令、返回码、摘要行、`coverage.json` 时间戳与年龄、改动文件哈希、`gate_precondition`） |
| claim 审计（双向） | `python evidence/claim_fact_audit.py` | 见下方"全量结果" |

> **§7 注（B-VR02-06）**：仓库**跟踪**着一份陈旧的 `coverage.json`（2026-08-17 测量），而棘轮门读的就是这个文件 → **单独**运行棘轮命令会红，这不是本次改动导致的。`b02_verify.py` 现在把"陈旧的 coverage.json"报成 **SKIPPED + 年龄**而不是假红。
> **§7 注 2（B-VR02R3-07，更正）**：早先一版 §7 写过"新增测试未落盘时 `resolver.py` = 61.3 %（FAILED）"——那是 **rev1 树**（`cab1fd6` 之前、且新测试文件尚不存在）上的一次测量；**在当前树上不成立**：`B.VR` rev3 用"排除新测试文件的全量 `--cov`"实测 **86.34 %**，棘轮仍 PASS。该数字不再作为当前证据使用。

### 全量结果（rev4，本次测量）

- 命令：`python -m pytest tests/ -q --tb=line --cov=src/company_wiki/source_catalog --cov-branch --cov-report=json`
- 结果：**2698 passed, 7 skipped, 0 failed**（786 s）；`coverage.json` 时间戳见 [b02-verification.json](b02-verification.json) 的 `coverage` 段。
- 覆盖率：`resolver.py` **87.72 %**（620/687 行、223/274 分支；TIER2 门 86 → 容差底 85.5）、`service.py` **95.16 %**（362/372 行、110/124 分支；TIER1 门 95 → 容差底 94.5）。
- 棘轮门：`FC1204_COVERAGE_GATE=1` 的覆盖率棘轮 + 复杂度棘轮合计 **4 passed**。
- 注：先前两次全量在同一台机器上各出现 2 条**负载抖动**失败（`test_100k_candidate_lookup_within_slo`、`test_zr409_…::test_c2_journey_dayu_only_real_sample`），单独重跑必过；本轮全量 0 失败。

## 8. 未做（不得当作已完成）

- **B04 / B05 / B01 / B03 / B06 / B07 一步都没做**（本步只有 B02）；B04 的落地计划已写（[b04-plan.md](b04-plan.md)）但**未实施**。
- **B03 的"读后复验/TOCTOU 闭合"未实现** → 规则 2 那一行的字节漂移目前无人拦（S-10 的另一半）。
- **B-payload-hash 仍未执行**（包内无基线、取值需待批 CLI）；本步只声明"未改 `SourceHandle` 字段与 `export_policy`"，**没有**做过字节/哈希比对。
- 未在生产 catalog 上验证（全部为合成 fixture 与既有测试）；未使用 G8 隔离副本；未验证真实云占位层（本机不可得）。
- **S-10 / S-11 仍待 owner 裁定**；`B.VR` rev1/rev2/rev3 三轮已做，**rev4 定点复核待做**。
