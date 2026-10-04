# SPLIT REPORT — RATCHET-FIX-A (a20260927-01)

- **授权**: owner `§四十二 裁定一` — `FC-1204 complexity ratchet`
- **结局**: **零产品改动（0 files fixed）** —— 父派单的"实际值"系度量口径误报，4 文件在门禁自带口径下**无一违规**；按父停手指令已把本会话改过的文件回滚到前像。

## 1. 度量口径澄清（本单核心发现）

派单表的"实际 14/17/16/32"= 标准 McCabe（**多算 `IfExp` 三元**、`And/Or` 只按 `len(values)-1` 计）。
门禁自带口径 = `tests/contract/test_fc1204_complexity_ratchet.py::_max_complexity`
（`_mccabe` 计 If/For/While/And/Or/Except/comprehension/Assert/With + BoolOp `len(values)-1`，**不计 `IfExp`**）。

两个口径的实测对照（前像状态）：

| 文件 | 派单"实际"(口径B) | 门禁口径 A | 冻结 | 口径 A 判定 |
|---|---|---|---|---|
| `adapters/parity.py` | 14 | **13** | 13 | ✅ 本来就没违规 |
| `lock.py` | 17 | **15** | 15 | ✅ 本来就没违规 |
| `prompt_injection.py` | 16 | **15** | 15 | ✅ 本来就没违规 |
| `store.py` | 32 | **30** | 30 | ✅ 本来就没违规 |

**⇒ 门禁口径下 4 文件全部 `== 冻结值`，零真违规。**（父已回执确认：`metric_correction_acknowledged=true`）

## 2. 本会话做过的改动与回滚

会话中途曾按派单口径做过两处拆分（后按父停手指令全部撤销）：

| 文件 | 中途改动 | 回滚 | 回滚后 sha16 == 前像 |
|---|---|---|---|
| `adapters/parity.py` | 抽出 `_compare_fields`（12:58） | ✅ pre_image 回写 | `BBF35590271123AC` 全等 |
| `lock.py` | `_process_identity` 拆为 dispatcher + 2 平台 helper | ✅ pre_image 回写 | `2303D3E5A4A79007` 全等 |
| `prompt_injection.py` | **本会话未改**（11:53 mtime 是会话前他人改动，前像已含） | 未动 | `0DAEFC79FDC6070E` 全等 |
| `store.py` | **本会话未改** | 未动 | `1A7832404C39DA85` 全等 |

**回滚核验（自算 SHA256，worktree vs `pre_image/`）**：4/4 全等 —— 工作区回到本会话动手前字节。

## 3. 后像（回滚后复测，权威口径）

| 文件 | `_max_complexity`（后像） | 冻结 | 判定 |
|---|---|---|---|
| `adapters/parity.py` | 13 | 13 | ✅ |
| `lock.py` | 15 | 15 | ✅ |
| `prompt_injection.py` | 15 | 15 | ✅ |
| `store.py` | 30 | 30 | ✅ |

`post_image/*.py` 与 `pre_image/*.py` 逐字节相同（回滚态）。

## 4. 测试结果（回滚后工作区）

| 测试 | 结果 |
|---|---|
| `pytest -k "parity or operation_lock or prompt_injection or pipeline_status"` | **57 passed** |
| `pytest -k store` | **100 passed** |
| `pytest tests/contract/test_fc1204_complexity_ratchet.py` | `frozen_files_do_not_worsen` **PASS**；`new_files_stay_simple` **FAIL** —— 红因 `narrative_evidence.py`（新文件规则，非本单 4 文件、非本单改动引入，回滚前后均如此） |

## 5. 写入面核对

- 产品码：**0 处净改动**（中途 2 处已回滚，sha 全等前像）。
- 本产出目录：`oracle.md`、`split_report.md`、`handoff.json`、`pre_image/`、`post_image/`、测量/拆分脚本（`measure.py`、`perfunc.py`、`dual_metric.py`、`split_lock.py`、`verify_gate_metric.py` 等，均为本目录内工具，非产品码）。
- 未碰：冻结表、五份计划文件、git 写、`git status`、联网、`dayu-agent`。

**status: review_pending**
