# B06 实施记录（**worktree 内完成，待移植**）——2026-09-12

> 状态：**已在隔离 worktree 实现并自测通过**（分支 `r4b06-wip`，基线 `f0aacbf`），**尚未落到主检出**——原因是 `B.VR`（B03）复审正在主检出上测量，移植会污染它的对象（见 §6 的流程规则）。
> 计划：[b06-plan.md](b06-plan.md)；允许集：F2 `resolver.py` + F10（仅新增测试）。

## 1. 交付物（worktree 内）

| 交付 | 位置 | 内容 |
|---|---|---|
| 产品代码 | `src/company_wiki/source_catalog/resolver.py` | `ResolutionEnvelope.qualification`（**加法，默认 `None`**，`to_dict()` 同步）+ 三个模块级新函数：`_qualification_gaps` / `_qualification_label` / `_metadata_conflict_reason` |
| 验收用例（新增，F10） | `tests/contract/test_r4b06_qualification.py` | **11 用例** |

## 2. 规则（与计划 §2 一致）

| 情形 | 标签 | 缺口码 |
|---|---|---|
| 身份（`entity_ids` 非空）+ 期间（`fiscal_year` 或 `published_date`）+ 来源（`source_id` 与 64 位 hash）齐备 | `verified_input` | `[]`，`reason=""` |
| 仅 provenance 有缺口（缺 URL / 缺捕获日志） | `preview` | `url_missing` / `capture_log_missing` |
| 身份不明 | **`blocked`** | `identity_missing` |
| 期间不明（既无 fiscal_year 也无 published_date） | **`blocked`** | `period_missing` |
| 来源/字节身份缺失（`snapshot_sha256` 缺口：无 source_id 或 hash 非 64 位） | **`blocked`** | `source_missing` |
| **存在真字段冲突**（B05 保留键 `r4_provenance` 里任一字段有 `conflicts`） | **`blocked`** | 冲突字段名列在 `reason` 里 |

- **失败值口径**：`blocked` 是**响应级**的，放在**新字段** `qualification.label` 里——**不能**放进 `outcome`（消费者 `filing-fetch/filing_contracts.validate_resolution_envelope` 要求 `outcome` 落在它自己的**八值**内，其中**没有 `blocked`**；放进去 = 消费者直接 `upstream_error`）。
- **加法性**：该验证函数**不拒绝未知键**（函数体内无 unknown/extra 检查，并对旧信封做 N/N-1 规范化）⇒ `envelope_schema_version` 保持 `"1.0"`；用例 `..._qualification_is_additive_for_pre_b06_consumers` 钉住这一点。
- **S-13 的接线**：`build_resolution_envelope` 用**只读** `store` 读该文档的 `metadata_json.r4_provenance`（键常量从 `scanner.R4_PROVENANCE_KEY` **导入**，不复制字面量，避免漂移），有冲突即响应级 `blocked` —— 与读侧 `metadata_status="blocked"` 是**同一个事实**，不是第二套口径。

## 3. **实施期发现（重要）：设计里的 `preview` 情形在当前 `resolve` 下不可达**

- 实测（worktree 探针）：一个**本地可读但无 `source_url`** 的副本，`resolve` 直接返回 `MISSING`，trace = `capture_incomplete` —— 命中的是 `resolver.py` 里既有的拒绝分支（`if not handle.capture_ready:`，注释原文："a capture-incomplete handle (e.g. missing https_url) cannot be consumed by filing-fetch; offering it as reusable deadlocks the download path"）。
- 含义：**本步交付的是"标签 + 规则 + S-13 的响应级 `blocked`"**；`preview` 这个取值**已定义、已测规则，但当前没有任何入口能产生它**。三条出路都要**改跨仓行为或加入口**：(a) 放宽 `capture_incomplete` 门（会让消费者看到它明确声明无法消费的句柄）；(b) 由 **B07 的版本化读取合同**提供显式的 preview 入口；(c) 保持现状，preview 仅作为**合同词汇**存在。
- **作者决定（在边界内，最保守）**：**选 (c)** —— 不放宽既有门（不改跨仓行为），把 `preview` 登记为"**已定义、当前不可达**"，并把 (a)/(b) 作为**范围问题**上呈 owner。**不声称 preview 已交付**。
- 用例据此分成两类：**可达的**（`verified_input` / `blocked`，经真实 `resolve` + 信封断言）与**规则级的**（`preview`，在真实句柄上注入缺口后断言规则本身），后者在 docstring 里写明"这是规则、不是可达结果"。

## 4. 用例清单（11 条，全绿）

可达路径：`..._complete_handle_is_verified_input`、`..._missing_url_is_refused_before_any_preview_label`（钉住 `capture_incomplete` 事实 + 无句柄时 `qualification is None`）、`..._unknown_identity_blocks_the_formal_contract`、`..._unknown_period_blocks_the_formal_contract`（含"只有 published_date 也算期间已知"）、`..._missing_source_identity_blocks_the_formal_contract`、`..._field_conflict_blocks_the_formal_contract`（S-13）、`..._an_unanswered_request_carries_no_qualification`、`..._qualification_is_additive_for_pre_b06_consumers`。
规则级：`..._url_gap_rule_is_preview_and_invents_nothing`、`..._missing_capture_trace_is_preview`、`..._preview_is_not_inherited_by_a_formal_input`。

> 冲突夹具的**关键前提**（踩过一次）：扫描器只在**新捕获的 root priority 不低于已存值**时才走合并/来源记录分支；用更高（数值更大）的 priority 写第二份捕获 ⇒ **根本不合并**，也就不会记录冲突。用例已把两个 root 都设为 `priority=10` 并写明原因。

## 5. 门（worktree 内实测）

```
python -m pytest tests/contract/test_r4b06_qualification.py -q      -> 11 passed
python -m ruff check tests/contract/test_r4b06_qualification.py     -> All checks passed
python -m pytest tests/contract/test_fc1204_complexity_ratchet.py   -> 2 passed
```

## 6. 待办（下一步，按流程规则排队）

1. **等 `B.VR`（B03）复审落地**（它在主检出上测量）→ 处置其发现。
2. 再把 B06 以补丁形式**移植**到主检出（分支 `r4b06-wip` 的 diff + 新测试文件），落盘后重跑 ruff + 棘轮 + 邻域。
3. **推送前**按 F-B01-9 的规则**本地跑一遍 `pytest tests/contract`**（CI 的失败步骤），确认无新 reason 码/跨机器常量/平台相关行为引入的红。
4. 一处**已知待改精确**的文本（等 B03 复审落地后再改，避免污染其测量）：`tests/test_fc1001_isolated_lake.py` 的 `strict xfail` 理由句暗示"B06 实现后即 XPASS"；实际上按 §3 与 F-B01-7 的分析，**B06 单独不会**让它 XPASS（需要 F3 或 F5/F6 侧机制）。

## 7. 一处更正（精确化，2026-09-12）

本节曾写"新增键改变响应 payload 字节 ⇒ `B-payload-hash` 基线须在 B06 之后"。**过度概括**：`B-payload-hash` 指的是 **policy_export payload**（`cli._policy_export_payload` 的输出），**不是** `ResolutionEnvelope`；B06 只改后者 ⇒ **不影响** `B-payload-hash`。已在 [b06-plan.md](b06-plan.md) §2.0 与 [b07-plan.md](b07-plan.md) §2④ 更正，并把该门的**可执行化路径**（pre-B worktree + 固定 `project_root` 逐字节比较）写进 B07 的计划。
