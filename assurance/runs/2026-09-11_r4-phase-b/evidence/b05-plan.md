# B05 落地计划（2026-09-12；**抽取子步已实施、保留键子步未开始**）

> 依据：[b-design.md](b-design.md) §B05（metadata 合并：来源优先、冲突保留）+ file-scope §3b（B05 = **F3 + F1**）+ `B.VR` 三轮复审确立的纪律（**文字不得超出代码**、差异要逐条列出）。
> 状态（如实）：**子步 1「等价抽取 `_merge_document_row`」已落盘并通过 823 用例**（尚未单独提交）；子步 2「保留键 + 读-改-写」、子步 3「逐列规则 + 读侧 blocked」**未开始**。下面是计划与实测依据。

## 1. 设计要点（b-design §B05 原文摘要）

1. 每个字段记录 **provenance**（来源标识 + 抓取时间 + **hash 或短规范化值**；**不得存原文片段**），放在 `documents.metadata_json` 的**保留键** `r4_provenance = {"schema_version": "1.0", "fields": {...}}` 里；既有键一律保留。
2. **逐列合并规则**：`:1078-1081` 那条 UPDATE 涉及的每一列都要有明确规则；**冲突不得按 priority 择一**。
3. **禁止整列替换 `metadata_json`**：含 `prefer_new` 路径（`:1073-1077`）与重扫分支（`:1095-1099`），一律**读-改-写**。
4. 冲突在**读侧**暴露为 `blocked`（不是 `ambiguous`——那个词留给 L07 的未知版本关系），并给出**字段级**明细；`capture_ready` 不变量在 L09 里断言。
5. 测试（F10）：L08 逐列合并，含"先缺后补"与 **json_extract 回归断言**（`fiscal_year` 过滤 + `prompt_injection_review` 门）。

## 2. 现状锚点（本机实测行号与语义，2026-09-12）

| 锚点 | 语义 |
|---|---|
| `scanner.py:1006-1008` | 读既有行 `metadata_priority, source_status, metadata_json` |
| `:1009-1027` | INSERT 分支（新文档）：`metadata_json = canonical_json(document_metadata)` |
| `:1028-1037` | `retired` 分支：只写 `last_seen_at`（**终态，不复活**） |
| `:1038` | 开关：`root.priority <= existing.metadata_priority` 才进入合并分支（数字越小优先级越高） |
| `:1044-1045` | 内层容器二选一：`dayu_meta` 或 `acquisition` |
| `:1059-1072` | `prefer_new` 三条件（source_url / market+security_id / provider_document_id） |
| **`:1073-1077`** | **整列替换**：`prefer_new` 时直接用 `canonical_json(document_metadata)`（会抹掉 `prompt_injection_review` 与任何 `r4_provenance`）→ **B05 必须改为读-改-写** |
| **`:1078-1081`** | UPDATE **全部列**取自"胜者"：`primary_source_id/title/source_type/document_kind/published_date/source_status/metadata_priority/metadata_json/last_seen_at` → **逐列规则要覆盖到每一列** |
| `:1095-1099` | 重扫分支（新 root 优先级更差）：只写 `last_seen_at`（**不是**整列替换，实测确认） |

## 3. 棘轮与覆盖率约束（**逐函数实测**，2026-09-12；本表已更正过一版）

| 约束 | 实测 | 对实现的硬性影响 |
|---|---|---|
| 复杂度棘轮（只数**模块级函数**，取文件内最大值） | `scanner.py` **ratchet-max 140 = FROZEN 140**，但 140 属于 **`_scan_root_v1`（:272）**，**不是**合并逻辑所在的函数 | **更正**：早先一版写"scanner.py 顶格、不能在任何被计入的函数里加判定点"**不准确**。逐函数实测（提取后）：`_scan_root_v1` **140**（B05 不触碰它）、`_scan_catalog_impl` **73**、`_classification` 37、**`_merge_document_row` 30**、`_observe_file` 26、`scan_catalog` 12 → 合并逻辑有**充足余量**（上限 140） |
| 为什么仍做"抽取" | `_merge_document_row` 已抽出（等价重构，823 用例通过） | 理由不是"顶格"，而是：① 合并逻辑可**独立测试**（不必经整个扫描流程）；② 让 `_scan_catalog_impl` 更小（73→更小）便于后续步骤；③ 表的**最大值**仍是 140，未动 |
| `NEW_FILE_MAX = 10` | 新文件每个函数 ≤10 | **本步不新增产品模块**；若新增文件，函数必须很小 |
| 覆盖率棘轮 | `scanner.py` 档 = **FROZEN 91**（容差底 90.5）；`service.py` TIER1 = 95 | 新分支必须由 F10 用例**真跑到**，否则 CI 直接红 |

> 更正记录：本表 v1 的"scanner.py 顶格 ⇒ 不能加判定点"结论建立在"140 属于 `scan_catalog`"的**未经验证的假设**上；实测后（`ast` 逐函数计数）发现 140 属于 `_scan_root_v1`。抽取本身仍按计划执行（它是 B02–B07 里唯一能安全承载 B05 逻辑改动的位置），但**理由与风险描述已按实测改写**。

## 3b. "禁止整列替换"的**具体后果**（本机核实，不是泛泛的风险提示）

- 先例：`prompt_injection.py:101-128` 的 `record_prompt_injection_review` **自己就是读-改-写**（读 `metadata_json`、写入保留键 `prompt_injection_review`、再整列写回）。→ 说明这张表里**已经存在**由别的模块写入的保留键，scanner 若整列替换就会把它们抹掉。
- 消费者：`resolver.py:676-686` 在构建 `ResolutionEnvelope` 时读该 receipt 并把它作为 `prompt_injection_status` 暴露；receipt 丢失 ⇒ 该字段退回 `not_reviewed`（对下游是"未复核"）。
- 因此 B05 的"读-改-写"要求有**可观测**的验收对象：`prefer_new` 路径跑完后，`prompt_injection_review` 与 `r4_provenance` 两个保留键都必须**仍在场**（F10 用例直接断言），而不是只断言"新键写进去了"。

## 4. 实施设计（草案，实施时按实测收敛）

1. **抽取**：把 `:1038-1099` 的合并逻辑抽成模块级 `_merge_document_row(...)`（纯函数：入参 = 既有行、新文档元数据、新 root 优先级、各列新值；返回 = 待 UPDATE 的列字典）。**行为先保持等价**，抽取后立刻跑既有套件确认零回归。
2. **加保留键**：`r4_provenance = {"schema_version": "1.0", "fields": {<field>: {"source_id", "observed_at", "value_hash"}}}`，只记 **hash/短规范化值**，绝不写原文片段；`metadata_json` 一律读-改-写，`prefer_new` 只影响**内层业务键**的选择，不再整列替换。
3. **逐列规则**（每条都要在计划评审时定稿）：`title/source_type/document_kind/published_date/source_status` 各自"何时接受新值、何时保留旧值、冲突如何标注"；`metadata_priority` 只作排序（B02 已确立）；`primary_source_id` 维持 `COALESCE` 语义（不为空则不改）。
4. **读侧暴露**（F1 `service.py`）：provenance 与冲突从 `metadata_json` 读出，冲突 → `blocked` + 字段级明细；不改 `SourceHandle` 字段（`B-payload-hash` 不可执行）。
5. **测试（F10，L08）**：逐列合并用例（含"先缺后补"）、`prefer_new` 不再抹列（`prompt_injection_review` 与 `r4_provenance` 存活）、`json_extract` 回归（`fiscal_year` 过滤 + 注入复核门）。

## 5. 风险与边界

- **不新增产品模块**（S-7 的替代路径是"抽新函数"，不是新文件）；**不改棘轮表**。
- **不动** `policy_2x.py` 导出路径、`export_policy` 输出（跨仓 policy_hash）。
- 抽取重构**先等价后扩展**：先抽（零行为变化 + 全量绿），再加保留键与逐列规则（各自独立 commit 亦可）。
- 若发现"逐列规则"需要改 DDL（新列/新表），**停下并请示**——那属写面/迁移工作包（file-scope §1 无 `store.py`）。
- 冲突判定不得引入第六种状态：读侧仍用五值模型（`blocked` 的载体见 §4.4）。

## 6. 步骤

1. 抽取 `_merge_document_row`（等价重构）→ 复跑既有套件 + 棘轮（`scanner.py` ratchet-max 应下降）→ 单独 commit。
2. 加 `r4_provenance` + 读-改-写（含 `prefer_new` / 重扫分支）→ F10 用例 → commit。
3. 逐列规则 + 读侧 `blocked`/字段级明细 → F10 用例 → commit。
4. 全量 + 覆盖率（`FC1204_COVERAGE_GATE=1`，先跑 `--cov`）、`ruff`、FC-1201 门、claim 审计与 checkpoint 回填 → 独立复审（`B.VR`，新会话）。
