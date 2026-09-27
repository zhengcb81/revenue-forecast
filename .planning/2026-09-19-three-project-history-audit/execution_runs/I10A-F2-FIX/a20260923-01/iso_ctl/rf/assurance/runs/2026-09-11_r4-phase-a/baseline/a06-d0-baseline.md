# A06-D0 基线结果（机制层，CI 等价）—— 首次真实基线

> 执行时间：**2026-09-12 08:11:42 → 08:23:32（+01:00）**；执行者：作者会话（命令与 CI 逐字一致）。
> 证据：[evidence/a06_unit.txt](evidence/a06_unit.txt)、[evidence/a06_contract_junit.xml](evidence/a06_contract_junit.xml)（pytest junitxml，逐例状态）、[evidence/a06_skips.json](evidence/a06_skips.json)。
> 本文件是执行计划 §A06 的"**每例基线结果**"的**机制层（D0）**部分；**R1 真实本地层与只读 trace 仍未做**（需 [command-manifest-readonly.json](../command-manifest-readonly.json) 批准）。

## 1. 复现命令（与 `.github/workflows/ci.yml:46-59` 逐字一致）

```
# cwd = C:\Users\郑曾波\Projects\company-wiki ; PYTHONPATH=src
python -m pytest tests/unit -q --tb=short
python -m pytest tests/contract -q --tb=short --junitxml=<path> \
  --ignore=tests/contract/test_dropbox_config_invariants.py \
  --ignore=tests/contract/test_zr1005_artifact_backfill.py \
  --ignore=tests/contract/test_zr1006_broker_cohort.py \
  --ignore=tests/contract/test_zr409_fourth_root_real_journeys.py \
  --ignore=tests/contract/test_zr503_multi_entity_attribution.py \
  --ignore=tests/contract/test_zr504_page_fidelity.py \
  --ignore=tests/contract/test_zr505_table_fidelity.py \
  --ignore=tests/contract/test_close_gap_concurrency_fc804.py
```

## 2. 结果

| 层 | 命令 | 结果 | 耗时 |
|---|---|---|---|
| Unit | `pytest tests/unit` | **787 passed** | 37.49 s |
| Contract（CI 等价子集） | `pytest tests/contract`（8 个 `--ignore`） | **1748 passed / 7 skipped / 0 failed / 0 errors**（junit 共 1755 例） | 707.95 s（11:47） |

**7 个 skip 的逐条原因**（全部来自 junit，非人工判断）：

| 测试 | 原因 |
|---|---|
| `test_dropbox_root_policy_fc501 :: test_dbx05_symlink_escape_rejected` | **`symlinks not supported on this host`** |
| `test_fc1204_coverage_ratchet :: test_tier1_critical_chain_at_95` | `coverage gate runs as a separate step (FC1204_COVERAGE_GATE=1)` |
| `test_fc1204_coverage_ratchet :: test_tier2_and_frozen_do_not_regress` | 同上 |
| `test_r9_v1_removal_gate :: test_deleted_modules_are_unimportable` | `R9 wave not executed yet`（需 `R9_GATE=1`） |
| `test_r9_v1_removal_gate :: test_v1_scanner_function_is_absent` | 同上 |
| `test_r9_v1_removal_gate :: test_bridge_flag_removed_from_flags` | 同上 |
| `test_r9_v1_removal_gate :: test_allowlist_shrinks_after_scanner_cleanup` | 同上 |

## 3. 从基线得到的三个实质结论

1. **`symlink` 逃逸控制在"这台机器上"从未被执行**：`test_dbx05_symlink_escape_rejected` 因宿主不支持 symlink 而 **skip**（junit 原文 `symlinks not supported on this host`）。这与 owner **R-1**（`symlink_policy` 是假保证字段）以及 A07 的 **L05 负例**（symlink/reparse 逃逸 → 越界零读/写）直接相关：**本机既没有真正的策略读取点，也没有能跑的逃逸测试**——该项必须在**支持 symlink 的环境**（或隔离副本 + 显式创建的 reparse point）上验证，不能以本机"绿"为依据。
2. **机制层基线可复现且全绿**：1755 例中 0 fail / 0 error，说明 B02/B05 改动前的机制面是**干净基线**；B 实施后必须与此基线逐例对比（"基线已正确者记保留回归"，执行计划 §A06 原文）。
3. **本机跑 CI 等价套件会打开生产 catalog（只读）**（见下条 F-A01-11）——基线本身不是"零副作用"的。

## 4. 与阶段 B 的关系

- B02/B03/B05/B07 的改动完成后，B.VR 必须在**同一套用例 + 同一隔离方式**下重跑本基线（B08 要求），并逐例说明"保持/改变/新增"。
- 本文件只覆盖 **D0 机制层**；**R1（真实字节）与 L12 的独立观察仍未做**，因此**不得**据此声称任何 L01–L12 的"真实验收通过"。
