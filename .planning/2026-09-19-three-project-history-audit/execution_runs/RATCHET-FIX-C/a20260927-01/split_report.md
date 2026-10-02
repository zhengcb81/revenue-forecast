# split_report — RATCHET-FIX-C (a20260927-01)

- **授权**: owner `§四十二 裁定一` — `FC-1204 complexity ratchet`（棘轮拆分）
- **角色**: `implementer_ratchet_c` · **日期**: 2026-09-27 · **status**: review_pending
- **权威度量**: `tests/contract/test_fc1204_complexity_ratchet.py::_max_complexity`（下称 **TEST**）；另测派单口径复核用 **M**（TEST 但 BoolOp 只计 n-1、加计 IfExp 三元 —— 父两轮更正已确认 M 即其原"实际"列的误差来源）
- **纪律**: 写入面 = 3 个目标文件 + 本产出目录；无 git 写、未用 `git status`、无联网、`dayu-agent` 零接触、未改冻结表

## 1. 前像（动手前 sha256，已拷贝 `pre_image/`）

| 文件 | 前像 SHA256 | 前像 TEST/M | 冻结 | 前像门禁判定 |
|---|---|---|---|---|
| `observability.py` | `563CDF1D95817665F91BED01FEA76C2D632E082F3C4751316EE0FF87D818993E` | 6 / 6 | 6 | 达标（拆分体已在 working tree：mtime 11:56:21 未提交，`git log -S` 证其从未入库；**HEAD 版本 = TEST 27 / M 20**，即派单"20~27"） |
| `prune_retired_evidence.py` | `0C99BBE0C5F4EF16E7F84BA8AAE0548EF6F59A0080274D5BD1CE83A7D37990B0` | **27 / 25** | 12 | **违规**（基线门禁原文 `prune_retired_evidence.py max complexity 27 exceeds frozen 12` —— 冻结表唯一红） |
| `adapters/conformance.py` | `D99BDF79BE4A055500B25A5846BC59C85E88C45C005AC8EE70E4438B31ECFD99` | 8 / 13 | 8 | TEST 达标（M=13 是父 IfExp 多算，已撤回） |

派单"实际"列复现：prune M=**25** ✓ · conformance M=**13** ✓ · observability HEAD M=**20**/TEST=**27** ✓（"20~27"）。

## 2. 拆分（仅拆分，行为零变；注释已注明 `Complexity ratchet (FC-1204, owner §四十二 裁定一, 2026-09-27): split only; behaviour unchanged.`）

### `prune_retired_evidence.py` —— 本轮唯一实体拆分（27 → 12）
- `prune_retired_evidence` **27 → 6**：入口只做校验 + 分派。新顶层函数（均 ≤12）：
  - `_select_plan` (3) —— 原 `if plan is None / else + plan-hash 校验` 分支
  - `_due_and_oldest` (5) —— `due` 计算与 `oldest` 归并
  - `_apply_prune` (4) —— 锁内 apply 编排（D4 前置复核 → D5 pending 收据 → 批量删除 → finalize）
  - `_pre_delete_check` (5) —— 首删前逐 span 复核（absent / not-retired / changed 三拒）
  - `_delete_batch` (7) —— 单事务内"读回+复核+删除"（`max(rowcount,0)` 等价搬移）
  - `_pending_receipt` (2) —— D5 收据载荷（键序/值逐字保留）
- `_load_verified_archives` **16 → 4**：11 级验证梯拆为 `_verify_one_manifest` (5) + `_manifest_decl_problem` (3) + `_archive_bytes_problem` (4) + `_verified_archive` (5) —— **检查顺序与 11 条 problem 文案逐字保留**
- `_build_plan` 12（原样，恰在冻结线）、其余函数 ≤8；ruff 全过

### `observability.py` —— 保留拆分态 + 补棘轮注释（本轮对它的 diff = 注释 4 行，`git diff --no-index` 已证）
- 拆分体（11:56 已在 working tree、未提交）：`_redact_assignments` 内联键回扫/值回扫/引号处理抽为 `_credential_key_before_separator` `_scan_left_over` `_is_credential_key` `_assignment_value_start` `_assignment_value_end` `_unquoted_assignment_end`（各 ≤6），主函数 5 只做分派；`exception_cause_types` 的 `while True/break` 抽出 `_next_unseen_cause` (6)。逐分支比对：边界检查、未闭合引号吞尾、C13 单 token 收束与原内联完全同构，**无一分支删除**。
- HEAD 27 → 6（前像已达标 6/6，本轮保持）。

### `adapters/conformance.py` —— 按父更正**还原前像**
- 本轮曾按派单"13→8"拆为 `run_conformance`(1) + 6 个 `_record_*`（TEST 4/M 5）；父以门禁口径复核确认 conformance 前像 8/8 本就达标（13 为 IfExp 多算），**已回写 `pre_image/conformance.py`**。
- 还原核对：`current sha == pre_image sha == D99BDF79BE4A055500B25A5846BC59C85E88C45C005AC8EE70E4438B31ECFD99`（= 入手时首采 sha = HEAD），且不再出现在 `git diff --name-only HEAD`。

## 3. 后像（`post_image/`）

| 文件 | 后像 SHA256 | 后像 TEST / M | 冻结 | 判定 |
|---|---|---|---|---|
| `observability.py` | `18DDCEC4F8FE207C0E4E65C6AA31F30CC09ABA93B11BB935E5D9B03BCC75BCCE` | **6 / 6** | 6 | ✅ |
| `prune_retired_evidence.py` | `70CC807A2FA59883E503DE0F43B21951A16408BD4F30AFCAE0632E747907334C` | **12 / 10** | 12 | ✅ |
| `adapters/conformance.py` | `D99BDF79BE4A055500B25A5846BC59C85E88C45C005AC8EE70E4438B31ECFD99` | **8 / 13** | 8 | ✅（==前像，TEST 达标） |

## 4. 验证（全文见 `verification_output.txt`）

| 门禁/测试 | 结果 |
|---|---|
| `test_fc1204_complexity_ratchet::frozen_files` | **PASSED**（三文件全 ≤ 冻结；基线时此测试因 prune 27>12 红） |
| `-k redact` | **9 passed** |
| `tests/contract/test_observability.py`（redaction 单测，含 `test_obs08_redaction_preserves_adjacent_diagnostic_fields`） | **8 passed** |
| `-k conformance` | **14 passed** |
| `ruff check`（两改文件） | All checks passed |
| **prune 行为双跑探针**（`prune_probe.py`：17 场景 = 11 条坏 manifest 梯 + 冲突授权 + 保留期内外 + 冻结 plan apply + 幂等二跑 + 篡改/hash 漂移/状态漂移/归档字节漂移四类 PruneRefused + naive-now TypeError + 收据内容） | **pre_image vs post 逐字节相同**：`sha256 = 6DB7D1FA262C5BD224AED6EAE036DC4566040BFFA2B9BA2E63DE8ED5585F5E57`（两跑一致，`probe_pre.json`/`probe_post.json`） |
| prune 签名 pre/post（`signature_check.py`） | IDENTICAL（`now: datetime` 无默认、keyword-only） |

## 5. 既有红（非本轮造成，未在我写入面内，未处理）

1. **`-k prune` 3 条红（既有 5 天）**：`tests/contract/test_source_catalog_prune_retired.py` 调用点不传 `now` → `TypeError: missing keyword-only 'now'`。`now: datetime` 是 **ac4ebd0（09-22）** 加入签名的（`git log -S`），该测试文件自 **b6c97b8** 后从未更新 ⇒ ac4ebd0 起即红；TypeError 在调用绑定处抛出，与函数体无关，且 pre/post 签名逐字节相同（上表）⇒ **与本轮拆分无关**。测试文件不在授权写入面，未改。
2. **ratchet new-files 红**：`narrative_evidence.py 363 > 10` —— 未跟踪新文件，并发 agent（`tests/.tmp-narrative-ratchet-agent/`）正在处理，非本单写入面。

## 6. git 写入面核对

- `git diff --name-only HEAD` 动手前基线 13 文件（含 `observability.py`、`test_observability.py` 等他人既有改动）→ 收尾 = 基线 + **`prune_retired_evidence.py`（本轮）** + `docs/plans/painpoint-outcome-audit-2026-09-05/*`（并发他方新增）。`conformance.py` 还原后已退出 diff 列表。
- **本实现者在 `company-wiki` 的落盘 = 授权 3 文件（conformance 还原为字节等同前像/HEAD）+ 本产出目录 ⇒ `git_diff_non_planning = 0`**（他方脏文件为动手前既有/并发产生，非本单写入）。
