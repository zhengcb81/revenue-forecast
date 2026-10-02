# ORACLE — RATCHET-FIX-A (a20260927-01) 【先冻结】

- **授权**: owner `§四十二 裁定一` — `FC-1204 complexity ratchet`（棘轮拆分）
- **角色**: `implementer_ratchet_a`（A 组 · 4 文件）
- **目标仓**: `C:\Users\郑曾波\Projects\company-wiki`（授权改产品码）；`dayu-agent` 绝对只读
- **产出目录**: `C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\RATCHET-FIX-A\a20260927-01\`
- **日期**: 2026-09-27

## 1. 责任文件与棘轮目标（不动冻结表）

| 文件（相对 `src/company_wiki/source_catalog/`） | 派单实际 | 冻结(须≤) | 派单指名最复杂函数 | 前像 SHA256 |
|---|---|---|---|---|
| `adapters/parity.py` | 14 | **13** | `run_parity` | `BBF35590271123ACD7C4A74516F35D4AB743223595C176F6A853307581AE501F` |
| `lock.py` | 17 | **15** | `_process_identity` | `2303D3E5A4A790070B253CBF3A319B38BE25D4D412DA8F8E067726D0553D5B4C` |
| `prompt_injection.py` | 16 | **15** | `record_prompt_injection_review` | `0DAEFC79FDC6070E5864E81FD26E649734F2D4D82A0F787689148B6D7C56F476` |
| `store.py` | 32 | **30** | `read_pipeline_status` | `1A7832404C39DA858400A99D2F7E9495E8B169498DACAD591FDA5447B2DA9615` |

**不在本单范围**：冻结表本身（`tests/contract/test_fc1204_complexity_ratchet.py::FROZEN_MAX` 不改）；`prune_retired_evidence.py`（C 组）；`producer_events.py`/`identity_cli.py`/`artifact_read_model.py`（B 组）；`narrative_evidence.py`（新文件规则，非本单）；`dayu-agent`（只读）。

## 2. 度量口径（冻结在先，实测记录于 2026-09-27 12:0x）

- **权威度量（验收口径 A）**：`tests/contract/test_fc1204_complexity_ratchet.py::_max_complexity`
  （顶层 `FunctionDef`、`1 + _mccabe`；`_mccabe` 计 If/For/While/And/Or/Except/comprehension/Assert/With，并对 `BoolOp` 再加 `len(values)-1`；**不计 `IfExp`**）。
- **派单口径 B（派单“实际”数字的来源，实测可复现）**：标准 McCabe = `测试 _mccabe` − `#(And/Or 节点)` + `#(IfExp)`，即计 `IfExp` 且不双计 `And/Or`。
  实测 4 文件口径 B = **14 / 17 / 16 / 32**（`run_parity` / `_process_identity` / `record_prompt_injection_review` / `read_pipeline_status`），与派单表逐格吻合。
- **验收双口径（本单自定，从严）**：拆后每文件 **口径 A ≤ 冻结** 且 **口径 B ≤ 冻结** —— 同时满足派单“要求：每文件 `_max_complexity` ≤ 冻结值 ⇒ 通过”与派单“实际→冻结”的收敛意图。

### 基线实测（前像）

| 文件 | 口径 A（权威 `_max_complexity`） | 口径 B（派单口径） | 冻结 |
|---|---|---|---|
| `adapters/parity.py` | 13 (`run_parity`) | 14 (`run_parity`) | 13 |
| `lock.py` | 15 (`_owner_status`)；`_process_identity`=12 | 17 (`_process_identity`) | 15 |
| `prompt_injection.py` | 15 (`record_prompt_injection_review`) | 16 (`record_prompt_injection_review`) | 15 |
| `store.py` | 30 (`read_pipeline_status`) | 32 (`read_pipeline_status`) | 30 |

> 注：`prompt_injection.py` 前像（本会话 12:00:59 拷贝）已含一处**会话前**未提交改动（11:53:57，`_disposal_gate` 拆出 `_require_disposal_metadata`，无棘轮注释、非本会话所为）；前像 = 派单交接时的工作区状态，本单不回滚他人改动，只叠加自己的拆分并补注释。

## 3. 修法（门禁明示）

1. **仅拆分**：把目标大函数的决策点移出到新的小顶层函数；每个顶层函数（含新函数）口径 A、B 均 ≤ 冻结；**行为零变**。
2. 每处拆分加注释：`Complexity ratchet (FC-1204, owner §四十二 裁定一, 2026-09-27): split only; behaviour unchanged.`
3. **不动冻结表**（表只能下调；拆到 ≤ 旧冻结值即可）。
4. **fail-closed**：任一文件拆不动或相关测试变红 ⇒ 该文件回滚到 `pre_image/<name>.py` 并如实报 `blocked`。

## 4. 变异/测试清单（验收动作，事先冻结）

| # | 动作 | 判据 |
|---|---|---|
| T1 | 权威度量：`_max_complexity(每文件)` | 每文件 ≤ 冻结（13/15/15/30） |
| T2 | 口径 B 复测（派单口径） | 每文件 ≤ 冻结（13/15/15/30） |
| T3 | `python -m pytest tests -q -k ratchet` | 全过（`test_fc1204_complexity_ratchet.py` 2 项） |
| T4 | `python -m pytest tests -q -k parity` | 全过 |
| T5 | `python -m pytest tests -q -k lock` | 全过 |
| T6 | `python -m pytest tests -q -k prompt_injection` | 全过 |
| T7 | `python -m pytest tests -q -k store` | 全过 |
| T8 | `python -m pytest tests -q -k pipeline_status`（若命中） | 全过 |
| T9 | 定向单测：`run_parity` / `_process_identity` / `record_prompt_injection_review` / `read_pipeline_status` 所在测试 | 全绿 |
| T10 | 语法冒烟：`python -m py_compile` 4 文件 | 通过 |

**已知非本单红项（预先声明，不回滚本单）**：T3 若因 `prune_retired_evidence.py`（C 组在修）或 `narrative_evidence.py`（新文件规则，非本单四文件）失败，按文件级断言单独验证本单 4 文件（T1/T2），并在 split_report 如实记录“红因在本单范围外”。

## 5. 写入面

- 4 个目标文件（`adapters/parity.py`、`lock.py`、`prompt_injection.py`、`store.py`）
- 本产出目录（`oracle.md`、`split_report.md`、`pre_image/`、`post_image/`、`handoff.json`、测量脚本）
- 禁：五份计划文件、git 写、`git status`、联网、`dayu-agent` 任何接触。

## 6. 状态（终）

- [x] 前像 SHA256 留痕（见 §1 表）
- [x] 前像拷贝 `pre_image/`（12:00:59，4 份）
- [x] oracle 冻结
- [x] **度量纠错（本单核心发现）**：派单“实际 14/17/16/32”系口径 B（多算 `IfExp` 三元）；门禁自带口径 A 实测 **13/15/15/30 ≤ 冻结 13/15/15/30** ⇒ **4 文件零真违规、无需拆分**（父回执 `metric_correction_acknowledged=true`）
- [x] 父停手指令执行：本会话中途拆过的 `adapters/parity.py`、`lock.py` 已回滚 `pre_image`；4 文件 sha256 == 前像（全等）
- [x] 测试：`-k "parity or operation_lock or prompt_injection or pipeline_status"` 57 passed；`-k store` 100 passed；ratchet `frozen_files_do_not_worsen` PASS（`new_files_stay_simple` 红因 `narrative_evidence.py`，新文件规则、非本单范围、回滚前后同样存在）
- [x] `post_image/` · `split_report.md` · `handoff.json`（`files_fixed=0`、`reverted_files` 已列）

**status: review_pending**
