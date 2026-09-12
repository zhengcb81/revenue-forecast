# B02 实施与验证记录（2026-09-12）

> 状态：**已实施**（F1 + F2 + F10）、**待独立复审**（B.VR）；本页只写**已落盘且可复跑**的事实，每条给命令与输出位置。
> 纪律：本页出现的每个"已验证"都必须能用给出的命令重现；未做到的写在 [§8 未做](#8-未做不得当作已完成)。

## 1. 改了什么（落点与哈希）

| 落点 | 实施后位置 | 内容 |
|---|---|---|
| **F1** `src/company_wiki/source_catalog/service.py` | `_REJECTIONS_SEGMENT` `:26`；`_location_exclusion_reason` `:35-59`；`_location_order_key` `:62-76`；`_annotate_locations` `:666-706`；`_duplicate_summary` `:709-741` | 资格（段 1/2）与排序（段 4）分离；逐候选 `candidate_rank` + `exclusion_reason` |
| **F2** `src/company_wiki/source_catalog/resolver.py` | 常量 `:152-157`；`_sha256_of_file` `:160-167`；`_needs_hydration` `:170-175`；`_ReadBudget` `:178-208`；`_local_copy_probe` `:211-227`；`_verify_candidate` `:230-262`；`_Selection` `:411-423`；`__init__(read_budget=...)` `:861`；`resolve` 预算/理由入 trace `:1090-1109`；`_select_candidate` `:1300-1362`；`_handle` `:1366-1452` | 在**有序合格候选清单**上逐份尝试（段 3/4）；预算/取消；返回值携带"选了哪份+为什么" |
| **F10** `tests/contract/test_r4b02_candidate_selection.py` | 新增文件 | B02 验收：L01/L02/L03/L04 + 预算/取消 + 零网络 + S-7 棘轮表冻结，共 **16** 个用例 |

哈希与规模（实施后实测）：

| 文件 | sha256(16) | 字节 |
|---|---|---|
| `service.py` | `ae45537d3740816d` | 57 997 |
| `resolver.py` | `b7b7fa9b37ccd9a6` | 67 157 |
| `test_r4b02_candidate_selection.py` | `a61e32ffaa4dd802` | 22 538 |

`git diff --stat -- src tests` = **2 files changed, 315 insertions(+), 46 deletions(-)**（+1 个新增测试文件）。
file-scope §1 里 F1/F2 的 `6412b19e…`/`6962b258…` 是**开工前的冻结输入哈希**（A01 §0），按 §5「B 开工即视为已消费」不再改写，新值即本表。

## 2. 语义（四段式，顺序即语义）

| 段 | 实现落点 | 规则 |
|---|---|---|
| 1 注册/能力 | locations SQL 的 `JOIN roots`（结构性）+ resolver `reusable_root_ids` | 未注册 root 不产生行；复用能力仍由 `reusable_root_kinds` 决定 |
| 2 状态与安全 | `_location_exclusion_reason` | `original_primary` + `location_status='active'` + `source_id` 非空 + 路径不含 `.rejections`；**保持"排除"语义，不是"只标记"** |
| 3 可读且同 hash | `_local_copy_probe` → `_verify_candidate` | 先 `stat`（**不读字节、不触发水合**）→ 大小快筛 → 全文件流式 sha256 比对；任何"合格"结论都由**整文件**摘要支撑（抽样只用于排除） |
| 4 健康/IO 偏好 | `_location_order_key` | 仅在**已合格集合内**按 `priority → root_id → relative_path → location_id` 排序，只决定"先用哪份" |

**输出**：每个 location 带 `candidate_rank`（1..N，0=被排除）与 `exclusion_reason`（被排除者的机器可读原因）；`is_canonical` = 该 source 组内 rank 1。`rank` 是**按 source_id 分组**的：一个文档若同时挂两个修订，会有两条 rank 1，段 3 的字节校验负责把它们区分开。

**诊断**（`resolve` 的 `debug_trace`）：正常命中且就是首选时保持既有 trace 形状（`…: matched`）；一旦**不是**首选（切换、字节未验证、预算/取消），追加 `…: <selection_reason>` 与逐候选 `…: candidate <location_id>:<reason>`。

## 3. ⚠️ 与设计正文的一处偏差（待 owner 确认，编号 **S-10**）

设计 [§B02 段 3](../b-design.md) 要求"可读且同 hash"是**硬门**（不满足即不合格）。实施采用：

> **优先**选字节已验证的合格副本；若清单里**没有任何**候选的字节验证通过、但存在**本地可读**的合格副本，则仍然返回该副本，并在 trace 里标注 `unverified_bytes`（绝不静默）。**字节级硬门归 B03 的读路径**（"只返回验证版本字节或明确失败"）。

**理由（可复跑）**：A 侧冻结断言构造的合成目录里，文件**字节**与其**声明的** `content_sha256` 本来就不同（fixture 反复写 `b"%PDF-fake"`，而 hash 是 `sha256(b"same-bytes")`/`sha256(b"other-bytes")`）。硬门实现下这 4 条既有断言必然失败：

- `tests/contract/test_source_catalog_determinism.py::test_same_hash_three_roots_picks_priority_primary_preserves_all`
- `tests/contract/test_source_catalog_determinism.py::test_same_period_different_hash_is_ambiguous`
- `tests/contract/test_source_catalog_sql_pushdown.py::test_resolver_uses_sql_pushdown_not_all_table_query`
- `tests/contract/test_source_catalog_sql_pushdown.py::test_old_period_not_shadowed_by_cap`

复跑：`python -m pytest tests/contract/test_source_catalog_determinism.py tests/contract/test_source_catalog_sql_pushdown.py -q`（硬门实现下上述 4 条 FAILED；当前实现 5+5 全通过）。S-1 只批准**新增**测试、**不得修改既有断言** → 让步只能在实现侧。

**这不是"降级成不校验"**：段 3 仍然真的读字节并比对，验证通过的候选会被优先选中并记 `verified_sha256`；只有"全都没验过"时才回退，且回退事实写入 trace。`resolve` 本身从不授权下载（`download_allowed` 只回显 `request.allow_download`）。

## 4. 预算与取消（L06/L12）

| 约束 | 默认 | 超限行为 |
|---|---|---|
| 每候选字节上限 | 256 MiB | `exceeds_candidate_cap`，**不读** |
| 单请求候选数 | 64 | `budget_exceeded`，停止继续读取 |
| 单请求流式读总量 | 2 GiB | `budget_exceeded` |
| 取消 | 调用方 `_ReadBudget.cancel()` | 不再读任何候选字节，且**不返回句柄**（`candidate_verification_cancelled`） |

- 预算是**每次 `resolve` 请求**一个实例（可经 `SourceResolver(catalog, read_budget=…)` 注入，测试与取消用）；计数器 `candidates`/`bytes_read` 留在对象上作为证据。
- 生产上只有**已通过全部身份/期间/身份冲突门**的文档才会进入段 3（`_handle` 调用点在那些门之后），因此每请求的真实读取量很小；64/2 GiB 是安全阀而非常态限制。
- 预算耗尽 → 回退到第一份可读副本（同 §3 偏差）；**取消 → 不回退**（被取消的请求不得用未验证字节作答）。

## 5. 明确没改（边界）

- **不新增产品模块**（S-7/work-package：新增文件不在 allowed 集）；`test_r4b02_no_new_source_catalog_module_was_added` 断言这一点。
- **不改棘轮表**：`test_r4b02_complexity_ratchet_table_is_not_edited` 断言 `FROZEN_MAX["service.py"] == 45`、`["resolver.py"] == 103`。
- `SourceHandle` 字段**不变**（对外 payload 形状不变）；新增的只是**读取期字典注记**（`candidate_rank` / `exclusion_reason` / `verified_sha256`），不落库、不改 schema。
- 其他排序锚点（`canonical_writer.py` / `duplicate_cleanup.py` / `normalizer.py` / `evidence_query.py` 等 6 处）按 file-scope §3 **仍归 C/D**，本步未动。
- `_duplicate_summary` 之外的写面、外发面、worker 面一律未动。

## 6. 需要知晓的副作用

1. **重复计数口径**：`exact_duplicate_location_count` / `exact_original_copy_count` 现在只统计**合格**副本 —— 被 `.rejections` 排除的行不再计入"副本"。理由：全代码只有一份"合格"定义；影响面仅在 `.rejections` 泄漏场景（`test_r4b02_l04_*` 断言新口径）。
2. **读放大**：段 3 会真的读候选文件（只读、有上限）。对同一文档的每个合格候选最多一次流式读；首选验证通过即停止。
3. **trace 变化**：仅在"不是首选"时新增行，正常命中保持原样。

## 7. 验证证据（命令 → 结果）

| 证据 | 命令 | 结果 |
|---|---|---|
| **RED/GREEN 探针** | `python evidence/b02_red_green_probe.py --label pre-b02 --out evidence/b02-red-green-pre-b02.json`（`PYTHONPATH` 指向 `git worktree` 的 HEAD 源码）与 `--label post-b02` | pre：撤销首选副本后 `missing`（trace `placeholder_no_handle`）；post：`reused_exact`（dropbox 副本，trace `verified_candidate_rank_2`）。JSON 记录 `module_file` 以证明用的是哪份源码 |
| RED 源码取得方式 | `git worktree add --detach "$env:TEMP\r4b02-preb02" HEAD` | 干净 HEAD（`c986c7a`），不改工作区 |
| 新增用例 | `python -m pytest tests/contract/test_r4b02_candidate_selection.py -q` | **16 passed** |
| 目标回归 | `python -m pytest tests/contract/test_source_catalog_determinism.py tests/contract/test_source_catalog_sql_pushdown.py tests/contract/test_zr403_dedupe_resolver_generalization.py tests/contract/test_source_catalog_fail_closed.py -q` | **23 passed** |
| 根 token 门 | `python -m pytest tests/contract/test_fc1201_root_hardcode_gate.py tests/contract/test_future_root_config_only.py -q` | **10 passed**（首轮 3 条 FAILED：`_needs_hydration` docstring 里写了 `dropbox_stock`/`Dropbox`，触发 FC-1201 根 token 门；已改写为与 root 无关的措辞后通过） |
| 单元测试 | `python -m pytest tests/unit -q` | **787 passed** |
| 全量 + 覆盖率 | `python -m pytest tests/ -q --tb=line --cov=src/company_wiki/source_catalog --cov-branch --cov-report=json` | **2684 passed, 7 skipped, 0 failed**（914 s）；`coverage.json` 时间戳 2026-09-12T12:27:31 |
| 覆盖率棘轮 | `FC1204_COVERAGE_GATE=1 python -m pytest tests/contract/test_fc1204_coverage_ratchet.py -q` | **2 passed** —— `resolver.py` **87.36 %**（607/675 行、222/274 分支；TIER2 门 = 86 → 容差底 85.5）、`service.py` **95.16 %**（362/372 行、110/124 分支；TIER1 门 = 95 → 容差底 94.5） |
| 覆盖率棘轮"有牙"的实证 | 同一次全量测量在**新增测试尚未落盘时**得到的 `resolver.py` = **61.3 %**（FAILED `< 86 %`） | 说明 **S-9** 的约束是真的：B02 改 `resolver.py` 必须自带覆盖新代码的测试，否则 CI 直接红 |
| 复杂度棘轮 | `python -m pytest tests/contract/test_fc1204_complexity_ratchet.py -q` | **2 passed**（`service.py` 45 / `resolver.py` 103 未动，且实测值远低于表值） |
| 静态检查 | `python -m ruff check src tests/unit tests/contract scripts` | All checks passed |
| **汇总（可复跑）** | `python evidence/b02_verify.py --fast` | **7/7 executed checks pass** → [b02-verification.json](b02-verification.json)（含命令、返回码、摘要行、`coverage.json` 时间戳与三个改动文件的哈希） |

## 8. 未做（不得当作已完成）

- **B04 / B05 / B01 / B03 / B06 / B07 一步都没做**（本步只有 B02）。
- **B03 的"读后复验/TOCTOU 闭合"未实现** → 因此 §3 的偏差有另一半：目前**没有任何一层**对"读出来的字节"做返回前复验；B03 落地前，"字节级硬门"整体缺失（这正是 S-10 要 owner 知情的原因）。
- **B-payload-hash 仍未执行**（包内无基线、取值需待批 CLI）；本步只声明"未改 `SourceHandle` 字段与 `export_policy`"，**没有**做过字节/哈希比对。
- 未在生产 catalog 上验证（全部为合成 fixture 与既有测试）；未使用 G8 隔离副本。
- 未做独立复审（B.VR 是下一步）。
