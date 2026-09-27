# ORACLE — DEF-I00C-GATE-NEG（冻结件 · 冻结于修复前）

- 缺陷卡：`DEF-I00C-GATE-NEG`
- 授权（`OWNER_DECISIONS.md` **§四十 裁定二** 逐字）：
  > **裁定二：两张新缺陷卡 —— 「本期开 2 张（建议）」**
  > | 新卡 | 缺陷 | 开卡 |
  > | **`DEF-I00C-GATE-NEG`** | `I-00-C` 验收/关闭门负例缺口：9 例仅 3 拒（**`N1/N2/N4/N5` 未拒** —— `closure_ready=True` 但无证据/错能力证据/空命令/空不变量均放行） | 本期 |

## 一、缺陷实证（逐字，回源核实）
- 证据件：`.planning/2026-09-19-three-project-history-audit/execution_runs/I-17-B/a20260926-01/six_negatives_result.json`（UTF-16）
- 实测：`negative_count=9 · negatives_rejected=3 · all_six_rejected=false`
- 组合指纹（与当前产物逐一比对 **全部吻合**，即缺陷在当前在役代码复现）：
  - `closure_py_sha256 = 952abfe0ea39ced076e3b83090de79e90ee95e5a39d94d8711377f65a446300e`（`uc/closure.py` 当前实测一致）
  - `scenarios_py_sha256 = 524fc1e6d6ba6a841e36f339c1aaf4e14bd7f26ec3ed6f04c83669d082544f29`（`uc/scenarios.py` 当前实测一致）
  - `registry_sha256 = d25e6f0600bab482a8ebd780ed307e4e58ddd5cc68ea4b2a5da19f832f377427`（当前实测一致）
- 九例逐条（原 runner 判语逐字）：
  | 案例 | 原判 | 原判据 detail（节选） |
  |---|---|---|
  | `N1_all_passed_but_no_evidence` | **未拒** | `closure_ready=True unsatisfied=0` |
  | `N2_read10_wrong_capability_evidence` | **未拒** | `closure_ready=True unsatisfied_ids=[]` |
  | `CTRL_read10_covering_capability_accepted` | ✓ 拒(对照成立) | `closure_ready=True (control, must be True)` |
  | `N3_stale_accepted_after_newer_fail` | ✓ 拒 | `stale accepted must not win` |
  | `N4_empty_commands` | **未拒** | `closure_ready=True unsatisfied_ids=[]` |
  | `N5_empty_invariants` | **未拒** | `closure_ready=True unsatisfied_ids=[]` |
  | `N45_both_empty` | **未拒** | `closure_ready=True unsatisfied_ids=[]` |
  | `N4b_receipt_layer_requires_commands` | ✓ 拒 | `required=(… 'commands' …)` |
  | `N6_original_obligations_still_pending` | ✓ 拒 | `pending=3` |
  | `N6b_narrowed_successor_flagged` | **未拒** | `narrowed_flagged=False` |

## 二、门 0 自探留档（回源记录）
- 先读派单指针件 `uc/closure.py`（sha `952abfe0…`）：其中**无** `closure_ready` —— 该 sha 是组合指纹之一；产生 `closure_ready` 的门在 `uc/scenarios.py::closure_report`（证据同件 `scenarios_py_sha256=524fc1e6…`）。两件均在授权写入面 `assurance/unified_completion/` 内。
- **根因定位**：
  1. `uc/scenarios.py::closure_report`（L143-156）**只看 `status`**：`closure_ready = not [s for s if status not in (passed, expected_failure_pass)]`，完全不校验 `evidence_path`/`fixture_hash`（N1）、`required_capability ∈ covered_capabilities`（N2）、`oracle.validated_commands`/`oracle.invariants` 非空（N4/N5/N45）。
  2. `uc/closure.py::closure_report` 的 reasons **不标记缩小后继卡**（N6b：`-narrow` 后继卡不出现于任何 reason）。
  3. 既有测试 `tests/test_scenarios.py::test_closure_report_green_when_filled` 将 197 例全置 `status=passed`（`evidence_path=None`）即断言绿 —— **固化了缺陷行为**，须随修同步改为"填证据才绿"。
- 调用面核查：`uc/cli.py` L407/L418 仅打印/聚合报告，键形状保持兼容即可。

## 三、修复判据（冻结，不得放水）
1. **绿**：修复后 `N1/N2/N4/N5` 四例全部 `rejected=true`；且回归对照 `N3`、`CTRL` 判定不变（`CTRL` 语义 = 覆盖能力的正例仍 `closure_ready=True`）。
2. **连带**：`N45`（双空）随 N4/N5 修复同判拒；`N6b` 随 closure.py 修复判拒 ⇒ 九例全量 **9/9 拒**（`negative_count=9 · negatives_rejected=9`），`CTRL` 保持成立。
3. **红**：回退修复（还原前像字节）必须复现原放行（未拒 ≥4 例，negatives_rejected 回落 3）。
4. **变异 ≥3**：对修复逻辑做 ≥3 个独立变异（在临时副本上），每个变异须使 ≥1 例由拒转放，证明判据有杀伤力。
5. **改前留前像 sha**（已录）：`scenarios.py=524fc1e6…`、`closure.py=952abfe0…`；改后录后像 sha。
6. **回归**：`tests/test_closure.py`、`tests/test_scenarios.py` 全绿（后者含随修更新）。
7. **纪律**：不改 `revision.py`/`receipt.py`（N3/N4b 路径零触碰）；不写 `.planning`；不联网；不 git 写；参数不放行；不自签。

## 四、失败出路
修不了 ⇒ `STOP` 判 `blocked`（fail-closed，合格）。

---

## 附：冻结后结果回填（非判据变更，仅记录执行结果）
- **红相基线**（前像在役代码）：`negatives_rejected=3/9`，runner `exit=3`（`nine_negatives_before_fix.json`）——与 I-17-B 证据逐例一致。
- **回退复现**（修复后回滚前像再跑）：`negatives_rejected=3/9`，`exit=3`（`nine_negatives_red_revert.json`）——判据 3 达成。
- **绿相**（修复在役）：`negatives_rejected=9/9`，`controls_ok=true`，`exit=0`（`nine_negatives_after_fix.json`）——判据 1/2 达成。
- **变异**：4 个独立变异（M1 丢证据校验→N1 翻放 · M2 丢能力覆盖→N2 翻放 · M3 丢 oracle 空校验→N4/N5/N45 翻放 · M4 丢缩小标记→N6b 翻放），4/4 killed，`exit=0`（`mutation_results.json`）——判据 4 达成。
- **回归**：`pytest tests/test_scenarios.py tests/test_closure.py` = **17 passed**（含随修更新的 `test_closure_report_green_when_filled` 与 4 个新负例测试）——判据 6 达成。
- **后像 sha**：`scenarios.py=2a262da8…`、`closure.py=09f13d38…`、`test_scenarios.py=68185a97…`（生产终态 = post_image 备份，已复核）。
