# ORACLE — RATCHET-FIX-C (a20260927-01)

- **授权**: owner `§四十二 裁定一` — `FC-1204 complexity ratchet`（棘轮拆分）
- **角色**: `implementer_ratchet_c`（C 组 · 3 文件 · 超幅最大）
- **目标仓**: `C:\Users\郑曾波\Projects\company-wiki`（授权改产品码）；`dayu-agent` 绝对只读
- **产出目录**: `C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\RATCHET-FIX-C\a20260927-01\`
- **日期**: 2026-09-27

## 责任文件与棘轮目标（不动冻结表）

| 文件（相对 `src/company_wiki/source_catalog/`） | 实际 | 冻结(须≤) | 最复杂函数 | 前像 SHA256 |
|---|---|---|---|---|
| `observability.py` | 20~27 | **6** | `_redact_assignments` | `563CDF1D95817665F91BED01FEA76C2D632E082F3C4751316EE0FF87D818993E` |
| `prune_retired_evidence.py` | 25 | **12** | `prune_retired_evidence` | `0C99BBE0C5F4EF16E7F84BA8AAE0548EF6F59A0080274D5BD1CE83A7D37990B0` |
| `adapters/conformance.py` | 13 | **8** | `run_conformance` | `D99BDF79BE4A055500B25A5846BC59C85E88C45C005AC8EE70E4438B31ECFD99` |

**不在本单范围**：`identity_cli.py`（B 组，绝不触碰）；冻结表本身（`test_fc1204_complexity_ratchet.py::FROZEN_MAX` 不改）。

## 修法（门禁明示）
1. **仅拆分**：每个顶层函数 `_max_complexity` ≤ 目标；**行为零变**。
2. 注释注明：`Complexity ratchet (FC-1204, owner §四十二 裁定一, 2026-09-27): split only; behaviour unchanged.`
3. `observability._redact_assignments` 20/27 → ≤6：逐类节点处理拆成独立顶层函数（各 ≤6），主函数只做分派；**redaction 是安全面，一行脱敏逻辑都不能丢**，拆后以 `-k redact` 单测全绿自证。
4. fail-closed：拆不动/测试红 ⇒ 回滚该文件前像并报 `blocked`。

## 纪律
- 写入面 = 3 个目标文件 + 本产出目录；禁五份计划文件；禁 git 写；**禁 `git status`**；禁联网；`dayu` 零接触。
- 权威度量 = `tests/contract/test_fc1204_complexity_ratchet.py::_max_complexity`。
- 验证：① 每文件 `_max_complexity`（按函数）≤ 目标 ② `-k redact` / `-k prune` / `-k conformance` 全绿。

## 基线实测（权威度量 = 测试自带 `_max_complexity`，即 TEST 指标；另测 M 指标复核派单"实际"列）

| 文件 | HEAD TEST/M | 前像 TEST/M | 冻结 | 结论 |
|---|---|---|---|---|
| `observability.py` | 27 / 20（`_redact_assignments`） | **6 / 6** | 6 | 前像已达标：working tree 于 2026-09-27 11:56:21 已存在未提交拆分（`git log -S` 证明该拆分从未入库），派单"20~27"= HEAD 版本；我验证其为纯拆分 + 单测全绿 |
| `prune_retired_evidence.py` | 27 / 25 | **27 / 25** | 12 | **超标，本次要拆**（`prune_retired_evidence` 27、`_load_verified_archives` 16 双双 >12） |
| `adapters/conformance.py` | 8 / 13 | **8 / 13** | 8 | 派单"13"= M 指标实测值；TEST=8 恰在冻结线上，但 M=13 超标 → 拆到双指标 ≤8 |

- M 指标 = 测试指标但 BoolOp 只计 n-1、另计 IfExp（三元）——派单"实际"列 20~27/25/13 由此复现：prune M=25 ✓、conformance M=13 ✓、observability HEAD M=20/TEST=27 ✓。
- 门禁实测：`pytest tests/contract/test_fc1204_complexity_ratchet.py` 现状 = 冻结表测试仅 `prune_retired_evidence.py 27 > 12` 一条红；new-files 测试红在 `narrative_evidence.py 363`（未跟踪新文件，非本单写入面，另一 agent 正在处理，报告为"没做的事"）。
- `-k redact` 基线：9 passed（前像红action 面全绿）。

## 状态（2026-09-27 收尾）
- [x] 前像 SHA256 留痕 + `pre_image/` 拷贝
- [x] 基线复杂度实测（TEST + M 双指标；复现派单 20~27/25/13 = M 口径 + observability 取 HEAD）
- [x] `prune_retired_evidence.py` 拆分：**27 → 12**（`prune_retired_evidence` 27→6、`_load_verified_archives` 16→4；`_build_plan` 12 原样）· ruff 过
- [x] `observability.py`：**6 → 6**（拆分体 11:56 已在前像；本轮 diff = 棘轮注释 4 行；HEAD 曾 27）
- [x] `adapters/conformance.py`：曾按派单拆 8→4，**按父两轮更正回写前像**（sha `D99BDF79…` == 前像 == HEAD，已退出 git diff）
- [x] 复测双指标：observability 6/6 · prune 12/10 · conformance 8/13 → **全部 ≤ 冻结（TEST 口径门禁 PASS）**
- [x] 测试：ratchet 冻结表测试 **PASSED**（基线红）· `-k redact` **9 passed** · `test_observability` **8 passed** · `-k conformance` **14 passed** · ruff 过
- [x] 行为零变自证：prune 17 场景探针 pre/post **逐字节相同**（`6DB7D1FA…`）；prune 签名 pre/post IDENTICAL；observability pre→post diff=注释 only
- [x] 既有红（非本轮、非写入面）：`-k prune` 3 条（ac4ebd0 加 `now` 后测试未跟进，b6c97b8 起未改）；ratchet new-files `narrative_evidence.py 363`（并发他方）
- [x] `post_image/` · `split_report.md` · `handoff.json`（`status=review_pending` · `implementer_signed=false` · `releases_nothing=true` · `git_diff_non_planning=0`）

**status: review_pending（已回父，等待评审）**
