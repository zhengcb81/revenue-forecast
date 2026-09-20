# i-10 模型卡 M09 / M10 / M11 / M12 独立复核报告（对抗式定点评测）

- reviewer：独立 reviewer session（非实现者、未参与本批任何写入）
- 复核窗口：2026-09-20 03:56:49 → 04:03:10 (+01:00)
- 计划根：`C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit`
- attempt：`execution_runs/{M09,M10,M11,M12}/a20260919-01`
- 写入范围：仅 `%TEMP%\m09m12-review-20260920-035628\`（本报告、脚本、probe/mutation 输出）。生产三仓与 attempt 目录**只读**；所有 python 调用带 `-B`，无 `__pycache__` 落盘。
- 解释器：attempt 内隔离 `iso\venv\Scripts\python.exe`（全局 Miniconda 未使用）。
- 判定前提交的 hash（时点 03:56:49 与 04:03:09 两次复算一致）：
  - `scripts\model_registry.py` = `9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f`
  - `scripts\model_extensions.py` = `9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911`
  - 四个 attempt 的 `iso\checkout_scripts\*` 与上述两值逐字节相同（4/4 卡、2/2 文件）。

---

## 1. 结论汇总

| 卡 | model_id | verdict | 授予资格 | 未授予 |
|---|---|---|---|---|
| M09 | `resource` | `accepted_scoped` | 仅 `formula` | disclosure_adaptation（unmapped）、accuracy（unproven） |
| M10 | `reserve_depletion` | `accepted_scoped` | 仅 `formula` | 同上 |
| M11 | `infrastructure` | `accepted_scoped` | 仅 `formula` | 同上 |
| M12 | `bank_revenue` | `accepted_scoped` | 仅 `formula` | 同上 |

P1：**0 条**。P2：**1 条**（非阻塞整改，见 §4）。P3：**4 条**。

P2 的定义（本报告自定口径，便于对齐）：需要在**下一次尝试**整改、但经独立证据判定**不影响本卡 `formula` 资格正确性**的缺陷。
P3：记录 / 格式 / 完备性瑕疵，不改变结论。

---

## 2. 逐项复核（对应"必做"1–7）

### 2.1 从卡片原文取期望 + 自造输入（必做 1）

我自己从卡片原文抄录正例并**手算**（未调用任何产品函数生成期望）：

| 卡 | 卡片原文手算（我算的） | 卡片声称 | 一致 |
|---|---|---|---|
| M09 | 30×4+2 = **122** | `[122]`（L33） | ✓ |
| M10 | 1000+100−50−200=850；200×0.8×3+10 = 480+10 = **490** | `[490]`（L48） | ✓ |
| M11 | 400×0.5+10 = 200+10 = **210** | `[210]`（L33） | ✓ |
| M12 | 1000×0.04−800×0.02+8+2 = 40−16+10 = **34** | `[34]`（L42） | ✓ |

我用隔离副本实跑（`probe.py`，argv 见下），并把四个 attempt 的 `evidence/<card>/input.json → positive` 与卡片原文逐字段比对：**四卡正例输入与卡片 L13–31 / L13–45 / L13–31 / L13–39 原文完全一致**（含 `base_revenue=0`、`years=[2027]`）。

命令（示例，M09 的 code-root；四卡同理）：

```
<attempt>\iso\venv\Scripts\python.exe -X utf8 -B %TEMP%\m09m12-review-20260920-035628\probe.py ^
    <attempt>\iso\checkout_scripts %TEMP%\...\probe_result.json
```

原始输出摘录（`probe.py` 控制台，完整见 `probe_result.json`）：

```
M09.positive   PASS      card text 30*4+2                                           [122.0]
M09.defaults   PASS      omit other_revenue 30*4+0                                  [120.0]
M09.continuity PASS      2-year cross-year 30*4+2 / 45*5+0                          [122.0, 225.0]
M09.extra      PASS      X1 3yr 1200*3.25+40 / 900*2.5-10 / 700*1.75+0              [3940.0, 2240.0, 1225.0]
M09.extra      PASS      X2 fractional 2.5*1.5+0.5                                  [4.25]
M10.positive   PASS      card text 200*0.8*3+10                                     [490.0]
M10.continuity PASS      card 2-year continuity positive                            [490.0, 0.0]
M10.extra      PASS      X1 3yr 300*.9*12+5 / 420*.85*11 / 300*.95*13               [3245.0, 3927.0, 3705.0]
M10.extra      PASS      X2 recovery_rate 1.0 then 0.0                              [70.0, 3.0]
M10.extra      PASS      X3 omit both optionals (other_revenue, reserve_revisions)  [480.0]
M11.positive   PASS      card text 400*0.5+10                                       [210.0]
M11.extra      PASS      X1 3yr 400*.5+10 / 520*.55+12 / 610*.62+0                  [210.0, 298.0, 378.2]
M12.positive   PASS      card text 1000*.04-800*.02+8+2                             [34.0]
M12.extra      PASS      X1 2yr negative rates ...                                  [4.0, 23.0]
M12.extra      PASS      X2 total revenue exactly 0 accepted                        [0.0]
```

我自造的**卡片之外**输入（≥2/卡，含跨年/连续性）：

- M09：3 年跨年 `saleable_volume=[1200,900,700] / realized_price=[3.25,2.5,1.75] / other_revenue=[40,-10,0]`，手算 `[3940,2240,1225]` → 实测一致；另有小数与零边界例。
- M10：3 年带增量/修订/变动回收率的桥，手算 `[3245,3927,3705]` → 实测一致；`recovery_rate` 取 `1.0`/`0.0` 两端点；同时省略两个可选 driver。
- M11：3 年跨年 `[400,520,610]×[0.5,0.55,0.62]+[10,12,0]`，手算 `[210,298,378.2]` → 实测一致。
- M12：2 年**负利率**例 `asset_yield=[-0.01,0.02] / funding_cost=[-0.005,0.01]`，手算 `[4.0,23.0]` → 实测一致；总量恰为 0 → 接受；总量为负 → 拒绝。

我另外用 attempt 自己的 defaults / continuity 输入独立手算核对：M10 defaults `250×0.8×3+0=600`（对账 1000+100+0−250=850 自洽）、M11 continuity `210/300`、M12 continuity `34/38` —— **与 `after/final_audit.txt` 记录的 `[600.0]` / `[210.0, 300.0]` / `[34.0, 38.0]` 一致**。

### 2.2 负例（必做 2）

四卡负例清单**结构完全一致且与计划口径吻合**：卡片专属负例 1 + `N01a..d` 4 + `N02..N05b` 5 + `CONT-BREAK` 1 = **11/卡**，共 44 条。`cases.json` / `oracle.json:negative_ids` / `negative_results.json` 三处的 id 序列逐一相同。

卡片专属负例与卡片原文逐条对照（`cases.json` 原始 json）：

| 卡 | 卡片原文要求的负例 | `cases.json` 实际构造 | 结果 |
|---|---|---|---|
| M09 | 仅替换 `{"saleable_volume":[-1]}`（L35） | `set_driver_element saleable_volume[0]=-1` | `ModelRegistryError: driver resource.saleable_volume must be between 0.0 and inf: FY2027` |
| M10 | 仅替换 `{"closing_reserves":[851]}`（L50） | `set_driver closing_reserves=[851]` | `ModelRegistryError: reserve stock-flow balance failed: FY2027` |
| M11 | 仅替换 `{"billable_volume":[-1]}`（L35） | `set_driver_element billable_volume[0]=-1` | `ModelRegistryError: driver infrastructure.billable_volume must be between 0.0 and inf: FY2027` |
| M12 | 仅替换 `{asset_yield:0, funding_cost:0.1, fee_revenue:0, other_revenue:0}`（L44） | `set_driver_multi`（同四值） | `ModelRegistryError`（`guard_hint` 明确标注为**总量闸**而非利率域闸） |

逐条复算 44 条：`is_target_type=true`、`verdict=PASS_rejected`、`is_import_or_file_error=false`、`raised == expected`，**无一例外**；`negative_summary` 四卡均为 `{"total":11,"passed":11,"failed":[],"import_or_file_errors":[]}`。

`CONT-BREAK` 与卡片的关系：M10 的 CONT-BREAK 精确复刻卡片 L106–116 的 `negative_patch`（`opening_reserves=[1000,851]`、`closing_reserves=[850,851]`，两年各自平衡但跨年断裂）；M09/M11/M12 卡片未给连续性用例，batch 用 `years=[2027,2029]`（财年不连续）作为该卡连续性反例，并在各自 `oracle.md §4` 明确写出理由与"存量为 not_applicable"的口径 —— 与卡片 L54 的 `not_applicable` 分支一致。

**我自造的不在清单内的负例（每卡 10 条 + 2 条跨模型，全部被目标异常拒绝）**：

```
MY1  string digit "1" in the 1st required driver        -> ModelRegistryError
MY2  string digit "1" in a 2nd required driver          -> ModelRegistryError
MY3  years=[2027.0] (float year)                        -> ModelRegistryError
MY4  NaN in the 2nd required driver (N01 only used the 1st) -> ModelRegistryError
MY5  +inf in the optional other_revenue                 -> ModelRegistryError
MY6  unknown model_id                                   -> ModelRegistryError
MY7  years=[2027,2027] (duplicate)                      -> ModelRegistryError
MY8  base_revenue=-1                                    -> ModelRegistryError
MY9  driver array longer than years                     -> ModelRegistryError
MY10 True in the 2nd required driver                    -> ModelRegistryError
MY11 M10 recovery_rate=1.5 (bounded ratio out of range) -> ModelRegistryError
MY12 M12 funding_cost=1.5 (explicit unbounded rate)     -> [350.0]  ACCEPTED (by design, card L48)
```

`应拒而被接受`：**0 条**（MY12 是"应接受"的对照例）。MY4 有价值：卡片 N01 只攻击首个必填 driver，我把它换到第二个必填 driver，守卫仍触发，说明值域/有限性检查是逐 driver 而非只查首个。

### 2.3 oracle 冻结与只追加（必做 3）

我**自己读 mtime**（不采信 `mtime_ordering.json`）：

| 卡 | `oracle.md` | `oracle.json` | `input.json` | `cases.json` | `stdout.txt`（首次产品运行） | 冻结早于运行 |
|---|---|---|---|---|---|---|
| M09 | 03:35:06.479 | 03:46:26.385 | 03:46:26.385 | 03:46:26.385 | 03:46:26.743 | ✓ |
| M10 | 03:36:22.200 | 03:46:34.083 | 03:46:34.081 | 03:46:34.082 | 03:46:34.472 | ✓ |
| M11 | 03:35:36.120 | 03:46:42.516 | 03:46:42.514 | 03:46:42.515 | 03:46:42.914 | ✓ |
| M12 | 03:36:33.813 | 03:46:49.130 | 03:46:49.129 | 03:46:49.130 | 03:46:49.546 | ✓ |

- **"修订 r2" 节数量 = 0**（四卡 `oracle.md` 全部标题已逐行列出，无任何 r2 标题）。`revision_r2.json` 如实写 `r2_present=false`、`appended_sections=0`、理由为"独立复核尚未返回，卡在 review_pending"，并预写了将来只允许追加**一节** r2 的规则。**未发现任何原地改写痕迹**（正文只追加这一条只能间接证明，见 §6）。
- **`oracle.json` 可逐字节重生成（我自己做的，未采信其 `regeneration_check.json`）**：把不 import 产品的生成器 `scripts/oracle_cards_M09_M12.py` 跑到我自己的临时 root：

```
M09 regenerate rc=0 all_match=True {'input.json': True, 'oracle.json': True, 'cases.json': True,
                                    'observation_expected.json': True, 'oracle_selfcheck.json': True}
M10 regenerate rc=0 all_match=True {...同 True}
M11 regenerate rc=0 all_match=True {...同 True}
M12 regenerate rc=0 all_match=True {...同 True}
```

- **冻结期望与 `cases.json` 自运行后未变**：`binding.json:input_hashes` 的三个 hash 与当前文件逐一相同（4/4 卡 × 3 文件全 match）；`recovery/regenerate/evidence/<card>/*` 与冻结件逐字节相同（4 文件 × 4 卡）；`evidence_hashes.json:files` 中 `oracle.json` 的 hash 与磁盘一致。
- 生成器独立性自检（`oracle_selfcheck.json`）：`product_import_present=false`，import 行只有 `argparse/hashlib/json/os/decimal`；`forbidden_tokens` 含 `model_registry`。此自检为**实现者自报**，但其结论可被我上面的重生成实验间接支持，且我的期望来自独立手算而非该生成器。

### 2.4 变异证明（必做 4）

**先点名退出码口径**：本批 `scripts/run_card.py` L48–51 定义为

```
EXIT_PASS = 0 ; EXIT_HARNESS = 1 ; EXIT_NO_VERDICT = 2 ; EXIT_NEGATIVE = 3
precedence: "1 harness > 2 no-verdict/fidelity > 3 negative > 0 pass"
```

即 **M09–M12 用的是"1 = harness"这一套（与 M13–M28 相同），不是 M05–M08 的"2 = harness"**。这一点由源码常量、`exit_code_semantics.verdict` 字符串与我的实测三者互证。

**我自己的变异（与实现者 `selfcheck_mutations.py` 的 A–E 不同的用例）**，把 attempt 的 runner + 冻结证据复制到我的临时目录后施加，实测真实退出码（`mutate.py` 原始输出）：

```
M09  F_control_unmodified           rc=0   verdict=pass
M09  A_positive_plus1               rc=2   verdict=no_verdict_fidelity
M09  C_continuity_plus1             rc=2   verdict=no_verdict_fidelity
M09  D_defaults_plus1               rc=2   verdict=no_verdict_fidelity
M09  E_observation_plus1            rc=0   verdict=pass
M09  B_negative_expect_ValueError   rc=3   verdict=negative_failed
... M10 / M11 / M12 六例完全相同（rc = 0,2,2,2,0,3）
```

补充 harness 例（`extra_checks.py`）：

```
M09  H1_bad_code_root     rc=1   verdict=harness_error
M09  H2_missing_input     rc=1   verdict=harness_error
M12  H1_bad_code_root     rc=1   verdict=harness_error
M12  H2_missing_input     rc=1   verdict=harness_error
```

结论：四个码位全部落在其登记口径内；`E_observation_plus1 → rc 0` 还独立证实了其"观察项不参与退出码"的声明（`gating=false`）。实现者自带的 `recovery/selfcheck/{A..E}` 亦为 `A/D→2, B/C→3, E→0`，与我的方向一致但用例不同（我用 continuity、defaults、观察项、N05b 而非 NEG-CARD）。

### 2.5 计数与跨批一致性（必做 5）——见 §5 裁决

### 2.6 生产与隔离（必做 6）

- 生产两文件 hash 复算两次（03:56:49 / 04:03:09）均等于任务锚点；`iso/checkout_scripts` 四卡 8 个文件全部逐字节相同。
- 三仓 porcelain（03:59:58）：
  - `company-wiki`：仅 ` M CLAUDE.md`、` M README.md`（与题述既有改动一致）。
  - `filing-fetch`：**空**。
  - `revenue-forecast`：` M scripts/model_registry.py` 等既有脏文件 + `?? execution_runs/{M09,M10,M11,M12}/`（本批新建的 attempt 目录）等；`before/git_status_revenue-forecast_filtered.txt` 与 `after/..._filtered.txt` 我逐行 `Compare-Object` → **identical**（114 行 vs 114 行）。
- `<PLAN>\reviews` 未被写：其最新 mtime 为 `2026-09-19 10:05:32`（`second_wave/final_review_checks.json`），**早于本批窗口**；attempt 亦记录了同一锚点。
- 并发事实（我实测，非缺陷）：`scripts/*.py` 13 个文件在窗口内被外部写入者重写；`before/production_file_mtimes.txt` 记录的是 `03:41:57`，而我此刻实测为 **`03:54:04`（第二批）**，两次内容 hash 均等于锚点。故本报告的 hash 断言只对 03:56:49–04:03:09 时点有效。

### 2.7 诚实性与资格（必做 7）

- `qualification.json`（4/4 卡）：`formula.state = "review_pending"`，且 `granted_by = "a separate independent reviewer only; the implementer never writes 'accepted'"`；`disclosure_adaptation.state = "unmapped"`；`accuracy.state = "unproven"`。**未自签 accepted**（全批 `accepted` 字样只出现在"实现者不自签"的否定句与"负利率被接受"这类业务语义里）。
- D/E/F 未产出**如实标注**：`deferred_work.json` 逐项列 `not_produced` / `draft_only` 并标 `owner`（I-10-A step D / step E / I-12）；`disclosure_mapping.json` 全部 driver `state=missing`、`no_values_invented`、不含任何数值；`disclosure_source_survey.json` 只是"候选公司目录 + 是否存在本地财报文件"的存在性勘察；`accounting_decision.md` 声明 PROPOSED/unsigned。`evidence/<card>/` 下**不存在** `historical_reconciliation.json` / `forecast_integration.json` / `accuracy_result.json` —— 未虚填。
- **未把"历史 97 tests / 216 subtests"当成本卡结果**：我在四卡 attempt 全量文本（排除 `iso/venv`）中检索 `\b97\b`/`\b216\b`，**零命中**；`qualification.historical_97_tests_216_subtests = "not used as a substitute for this card's new results"`。
- `decision.md` 指向 owner 项：四卡均有 `## Escalated to the owner (not decided here)` 与 `## Owner hand-off`，明确 `handoff.json` 的 `open_questions / next_action / blocked_by` 为权威接续记录；无 owner 门的部分以 `recovery/README.md` 的 **`not_applicable_with_reason`**（纯函数、无持久状态、无锁、无部分发布）处理。

---

## 3. attempt 目录完备性

四卡均齐备：`binding.json`、`oracle.md`、`commands.json`、`decision.md`、`handoff.json`、`changes.diff`、`review.md`、`before/`、`after/`、`evidence/<card>/`、`scripts/`、`iso/`、`recovery/`。`evidence/<card>/` 下任务点名的 16 个文件（`input/oracle/cases/formula_result/negative_results/qualification/oq_rulings/integrity/oracle_selfcheck/revision_r2/source_manifest/command_manifest/stdout/stderr` + `observation_expected`/`run_result`）**全部存在**；`stderr.txt` 四卡均为 0 字节（与"无异常输出"一致）。`changes.diff` 为"无产品改动"的声明文件（四卡均声明并在文件中复算了两文件 hash）。

---

## 4. 编号发现

### P1 —— 无

44 条登记负例 + 40 条我自造反例中，**没有任何"应拒而被接受"**。

### P2-1（非阻塞整改）：`binding.json` 与 `before/` 实为"运行后采集"，与 START_HERE §2「先做编辑前绑定」的字面要求不符

- 证据（原文摘录）：
  - `binding.json`：`"binding_record_written_at": "after the frozen inputs existed and after the card run; ..."`，末尾 `"created_before_runs": "frozen inputs: yes (see binding_record_written_at); this JSON record: written after the run by scripts/pack_evidence.py"`。
  - `before/README.md`：`"This card modifies nothing, so before/ and after/ are the same capture point, taken after the card runs. That is stated plainly here rather than dressed up as a pre-run capture."`
- 影响：绑定与 before 快照本身不是运行前产物；对**会改代码**的卡，这一模式会打开"事后拟合"的口子，而 `drive_card.ps1` / `pack_evidence.py` 是可复用的模板。
- 为何**不**因此降级本卡结论：本批零改动（`changes.diff` 声明 + 过滤前后 porcelain 相同 + 生产 hash 等于锚点）；`oracle.md` 的 mtime 早于首次产品 stdout；`oracle.json` 可由不 import 产品的生成器逐字节重生成；我的期望来自独立手算。三条独立证据关闭了 false-pass 路径。
- 要求：下一次尝试（或复用该模板的任何卡）必须真正前置 `binding.json` 与 `before/`，或显式在 `binding.json` 里给出"零改动卡豁免 + 前置锚点 hash"的机器可读字段。

### P3-1：`commands.json` 未采用 START_HERE 模板的字段名

`units[]` 的键为 `argv/cwd/expected_rc/network/note/purpose/raw_rc/unit_id`，**没有**模板要求的 `id`、`binding_status`、`command_run_id`、`timeout_seconds`、`before_after_evidence`；模板里"含 null/unbound 不能运行"的门因此无法被机器校验。实质（绝对隔离解释器 argv、cwd、`expected_rc`、`raw_rc`、`network`）是齐的，且 `command_manifest.ledger_vs_run_result_rc = {"ledger_b_unit_rc":0,"run_result_exit_code":0,"match":true}`。影响：人工可读、机器契约不完整。

### P3-2：`handoff.json` 的退出码表不完整

`after/rc_ledger.txt` 有 22 行（含 `Z3/Z4/Z7-Mxx-hash-refresh`），而 `handoff.json.raw_exit_codes` 只列 18 个键（缺 Z3/Z4/Z7）；`expected_exit_codes` 只覆盖 10 个 unit（`commands.json` 有 19 个）。且 note 写"a null means that unit had not been recorded"，但缺失是**键不存在**而非 null。影响：接续者据 handoff 无法完整重建 rc 台账（须回读 `after/rc_ledger.txt`）。

### P3-3：`oq_rulings.json` 只给"非 [0,1] 的 ratio 计数"，没有给全库 ratio 总数

四卡 `OQ_2.enumerated_counts` 里只有 `ratio_drivers_whose_effective_bounds_are_not_0_1_count = 4` 及其 4 元素清单，**没有**"ratio driver 总数"字段（我复算为 41）。这正是跨批 40/3 与 41/4 冲突难以自动比对的原因（见 §5）。影响：跨批一致性需要重跑枚举，无法靠读 JSON 直接裁决。

### P3-4：A1（离线 pytest 安装）的"期望 0 / 实际 1"只存在于文本注释

`handoff.exit_code_notes.A1` 与 `rc_ledger` 都如实写了，但 `qualification.json` 与 `command_manifest.json` 的机器可读层没有"known_non_pass"标记；读者若只看 `final_audit.txt`（`failures: none`）可能误以为 A1 通过。影响：低（本卡不依赖 pytest，且四卡测试均未运行 —— 卡片也未要求）。

---

## 5. 跨批计数裁决（必做 5）

### 我的复算（两条独立路径）

1. **重跑其枚举脚本**（`scripts/enumerate_registry_facts.py`，`--out` 指向我的临时目录）：

```
registry model count 31
registry optional drivers without a declared default total 31
ratio_non_default bank_revenue.asset_yield [-inf, inf] explicit driver_bounds
ratio_non_default bank_revenue.funding_cost [-inf, inf] explicit driver_bounds
ratio_non_default direct_growth.growth_rate [-1.0, inf] implicit
ratio_non_default store_cohorts.new_store_productivity [0.0, inf] explicit driver_bounds
reserve_volume drivers 5 non_negative 4 signed 1
--- M09 rerun rc=0 ---  byte-identical to their evidence: True
--- M12 rerun rc=0 ---  byte-identical to their evidence: True
```

2. **我自己的等价枚举 + 谓词对照**（`count_split.py`，只读 `MODEL_REGISTRY` 元数据与 `driver_value_bounds`，不调用 `calculate_registered_model`）：

```
A declared-ratio_drivers only      : total = 40  not[0,1] = 3
   not[0,1]: ['bank_revenue.asset_yield', 'bank_revenue.funding_cost', 'store_cohorts.new_store_productivity']
B declared OR dimension=='ratio'   : total = 41  not[0,1] = 4
   not[0,1]: ['bank_revenue.asset_yield', 'bank_revenue.funding_cost', 'direct_growth.growth_rate', 'store_cohorts.new_store_productivity']
difference (B-A): ['direct_growth.growth_rate']
direct_growth spec: ratio_drivers = []  dimensions = {'growth_rate': 'ratio'}  bounds = (-1.0, inf)
```

### 裁决

- **M09–M12 属于 41 / 4 这一边（即更正后的权威值一边）**，不属于 40/3。
- 依据：四卡 `oq_rulings.json` 与 `registry_enumeration.json` 报 `ratio_drivers_whose_effective_bounds_are_not_0_1_count = 4`，且清单**显式包含** `direct_growth.growth_rate`，其 `bounds = [-1.0, Infinity]`、`bound_source = implicit`；其枚举谓词（脚本 L99）为 `d in s.ratio_drivers or s.dimensions[d] == "ratio"`，与我的谓词 B 完全一致，重跑逐字节相同。我另用 products 的 `driver_value_bounds` 独立核出 41/4，两路径互证。
- **40/3 错在何处（我的判定）**：唯一差异是 `direct_growth.growth_rate`。它的 `ratio_drivers` 声明为**空**（`model_registry.py:221` 未传 `ratio_drivers=`），只通过 `dimensions={"growth_rate":"ratio"}` 表达 ratio 语义；其有效定义域由 `driver_value_bounds` 的**特例分支** `if driver == "growth_rate": return (-1.0, math.inf)`（`model_registry.py:287-288`）给出，即 **(-1, inf)**，因此"bound 不是 [0,1]"。只统计"声明在 `spec.ratio_drivers` 里的 driver"的枚举会把 `direct_growth.growth_rate` 整个漏掉 → 恰好得到 **40 / 3**（我实测 A 谓词就是 40/3，且 3 元素清单与 4 元素清单只差 growth_rate）。所以 40/3 是**口径错误（漏用 dimension=='ratio' 兜底 + 漏用 growth_rate 特例）**，不是数据差异。
- M09–M12 **没有**写"总数 41"这一数字（也未写 40），因此它既不属于错误一侧，也不能被当作"41"这一数字的书面来源；它的价值在于**给出了正确的 4 元素清单**（含 growth_rate），跨批比对应以该清单为准。（见 P3-3：建议后续补一个 `ratio_drivers_total` 字段。）

### 我对退出码口径差异的意见

- M09–M12 用 `1 = harness / 2 = no-verdict-fidelity / 3 = negative / 0 = pass`（M13–M28 口径），且**四个码位我都实测到了**。这套口径比 M05–M08 的"2 = harness"更有区分度：它把"期望缺失/保真不符"（实现方问题）与"负例未被拒"（产品问题）分开，而两者都不该与"harness 自己坏了"混为一谈。
- 但**跨批不统一本身就是缺陷**：同一个 `rc=2` 在 M05–M08 意味着 harness 崩溃、在 M09–M12 意味着期望不符，任何跨批复用 runner 或聚合统计的脚本都会误判。建议 owner 冻结**一个**码表并回填旧批的 `exit_code_semantics` 解释字段（无需改历史 rc，只要在每批 `commands.json`/`handoff.json` 里带一份自描述的 `exit_code_legend`）。本批已经在 `exit_code_semantics.precedence` 里自描述，这点值得保留。

---

## 6. 我未能验证的部分（不编造）

1. **"正文只追加"只有间接证据**：我只能证明 `oracle.md` 的最后写入时间早于首次产品运行、`r2` 节数量为 0、`oracle.json` 可逐字节重生成，以及四份关键 JSON 的冻结 hash 自运行后未变。文件系统不保留历史版本，我**无法**证明 `oracle.md` 在 03:35 之后的某个瞬间被原地改写过（若有改写则 mtime 会更新，故这属于理论缺口而非可疑迹象）。
2. **未读其它批次的 attempt**：父 agent 给出的 M05–M08 = 41/4、M13–M16 = 40/3、M17–M28 = 41/4 是转述。我**只**独立确认了 (a) M09–M12 报 4 且含 growth_rate、(b) 40/3 与 41/4 的差异恰为 `direct_growth.growth_rate` 且可由谓词 A/B 解释。我**没有**验证 M13–M16 的产物里到底写了什么，因此"哪一批实际写了 40/3"未经我核实。
3. **未验证 `disclosure_source_survey.json` 的候选清单与实际磁盘的一致性**：我只核对了其字段结构（`company/company_dir/exists/financial_reports/applicability_reason`）与"不含数值"这一性质，**没有**逐个 stat 它声明的 `exists`。同样未评估 `candidates` 是否覆盖了该行业应有的公司集合。
4. **未运行仓库自带测试**：attempt 内离线 pytest 安装失败（rc 1，已如实登记），我也没有在隔离 venv 中安装 pytest；`97 tests / 216 subtests` 这一历史数字我未复现，也未用于本裁决（卡片明确它不能代替本卡结果）。
5. **未验证 `iso/venv` 与 I-00-A 模板 venv 的等价性 / 依赖闭包**：我只把它当作解释器成功运行了脚本（含 `subprocess` 调用其自身），未做 `pip freeze` 比对或 site-packages 审计。
6. **并发窗口之外的时点不明**：03:54:04 的第三批产品文件重写、以及其它 session（`_m2931_build`、I-11-A、I-14-C、M29–M31 等在同一分钟仍在写盘）的活动，我无法归因；我的 hash/porcelain 结论只覆盖 03:56:49–04:03:10。
7. **`oq_rulings.json` 的 OQ-1..OQ-6 业务裁决本身未经独立评审**：我核对了它们的**计数与来源脚本**（可复现），但没有以会计/行业 reviewer 身份裁断这些开卷问题 —— 它们本就是留给 owner 的，`reviewed_by` 字段也如实写着 PENDING。

---

## 7. 可原样粘贴进每卡 `review.md` 的裁决正文

### M09 · resource

**独立复核裁决（独立 reviewer session，2026-09-20 04:03 +01:00，attempt `a20260919-01`）**

**结论：`accepted_scoped` —— 仅就 `formula` 授予通过；`disclosure_adaptation` 与 `accuracy` 不授予。**

已独立复验（未采信实现者摘要）：我从 `card_M09.md` L13–31 原文抄录输入并**手算** 30×4+2=122，用隔离副本 `iso/checkout_scripts/model_registry.py`（sha256 `9ec65295…`，与生产逐字节相同）实跑得 `[122.0]`；defaults `[120.0]`、连续性 `[122.0, 225.0]` 亦一致；我另造跨年（3 年，`other_revenue` 含负值）与小数/零边界输入，手算 `[3940,2240,1225]`、`[4.25]` 均一致。卡片专属负例（`saleable_volume=[-1]`）与 N01a–d/N02–N05b/CONT-BREAK 共 **11/11** 均由 `ModelRegistryError` 拒绝（`is_target_type=true`、无 import/file 错误），且我自造 10 个清单外反例（字符串数字 `"1"`、`years=[2027.0]`、第二个必填 driver 注入 NaN、`other_revenue=[inf]`、未知 model_id、重复年份、负 `base_revenue`、数组长于 years、Boolean 冒充数值）全部被目标异常拒绝，**无"应拒而被接受"**。`oracle.md` 的 mtime（03:35:06）早于首次产品 stdout（03:46:26），无任何"修订 r2"节，`oracle.json` 可由不 import 产品的生成器在我自己的临时目录**逐字节重生成**，冻结输入 hash 与 `recovery/regenerate` 留档三处互证。变异测试：正例期望 +1 → rc 2；负例期望异常名改 `ValueError` → rc 3；仅观察项被改 → rc 0；伪造 code-root / 缺 `input.json` → rc 1，与 `run_card.py` L48–51 登记口径一致（本批为 **1=harness、2=no-verdict/fidelity、3=negative、0=pass**，即 M13–M28 口径）。

未授予：`disclosure_adaptation` 保持 `unmapped` —— `disclosure_mapping.json` 全部 driver `state=missing`、未填任何数值，仅有一份来源存在性勘察与未签署的 PROPOSED 会计决策；`accuracy` 保持 `unproven` —— 不存在 I-12 冻结设计。D/E/F 未产出已在 `deferred_work.json` 如实标注（含 owner），`qualification.json` 未自签 accepted，未把"历史 97 tests / 216 subtests"当作本卡结果。

待 owner / 后续（不阻塞本卡 formula）：
1. **OQ-1**：`scripts/model_registry.py:335` 对无声明默认值的可选 driver 静默补 0 —— 本批 5 个可选 driver 全部属此类（注册表全局 31 个）；本卡的 `other_revenue` 静默补零会把"副产品已含在实售价内"的风险隐藏起来。
2. **OQ-3**：`revenue_per_unit` 默认域 `[0, inf)`，负实售价不可表达（全库 23 个此类 driver 中仅 2 个可为负）。
3. **OQ-5**：窗口内 `scripts/*.py` 13 个文件被外部写入者以字节相同内容重写（`03:41:57`，我 04:03 复算 hash 仍等于锚点），故 mtime 不能作为"未触碰"证据。
4. **R7/R8/R9（不可运行验证项）**："不得混矿石吨/精矿吨/金属吨""回收/应付/TC-RC 只扣一次""生产量不得当销量"是披露层业务门，本模型无单位字段，运行时**不可**验证 —— 不得把它们的缺席读作已覆盖。
5. **非阻塞整改（P2-1）**：`binding.json` 与 `before/` 实为运行后采集（文件内已自认）；下一次尝试须真正前置绑定与 before 快照，或给出机器可读的"零改动卡豁免 + 前置锚点"字段。
6. **P3**：`commands.json` 未用 START_HERE 模板的 `binding_status/id` 字段名；`handoff.json.raw_exit_codes` 缺 `Z3/Z4/Z7`；A1（离线 pytest 安装）expected 0 / actual 1 只在文本注释里标记为非通过。

### M10 · reserve_depletion

**独立复核裁决（独立 reviewer session，2026-09-20 04:03 +01:00，attempt `a20260919-01`）**

**结论：`accepted_scoped` —— 仅就 `formula` 授予通过；`disclosure_adaptation` 与 `accuracy` 不授予。**

已独立复验：我从 `card_M10.md` L13–45 原文抄录输入并**手算** 1000+100−50−200=850、200×0.8×3+10=**490**，用隔离副本（sha256 `9ec65295…`，与生产逐字节相同）实跑得 `[490.0]`。卡片 L56–118 的两年连续性正例我的手算为 `[490, 0]`（第二年无任何流量、`opening=上期 closing`）→ 实测一致；其 `negative_patch`（`opening_reserves=[1000,851]`、`closing_reserves=[850,851]`，两年各自平衡但跨年差 1）→ 实测 `ModelRegistryError`，且 batch 的 `CONT-BREAK` 精确复刻了该 patch。defaults 例（同时省略 `other_revenue` 与 `reserve_revisions`，用 `depletion=250` 使 1000+100+0−250=850 自洽）我的手算为 **600** → 实测一致。我另造 3 年桥（含增量、负修订、变动的回收率与单价）手算 `[3245,3927,3705]`、`recovery_rate` 取 1.0/0.0 两端点手算 `[70,3]`，均一致。11/11 负例（专属 `closing_reserves=[851]` + N01a–d/N02–N05b/CONT-BREAK）全部由 `ModelRegistryError` 拒绝，另有我自造 11 个清单外反例（含 `recovery_rate=1.5` 比例越界、第二个必填 driver 注入 NaN、字符串数字、`years=[2027.0]` 等）全部被目标异常拒绝，**无"应拒而被接受"**。oracle 冻结（03:36:22）早于首次产品 stdout（03:46:34），无"修订 r2"节，`oracle.json` 可由不 import 产品的生成器逐字节重生成，冻结 hash 三处互证。变异测试与退出码口径同 M09（**1=harness、2=no-verdict/fidelity、3=negative、0=pass**，实测 rc = 0/2/3/1 全部落位）。

未授予：`disclosure_adaptation` 保持 `unmapped`（7 个 driver 全部 `state=missing`、无签署、无已结束期间收入对账）；`accuracy` 保持 `unproven`（无 I-12 冻结设计）。D/E/F 未产出如实标注，未自签 accepted，未把历史 97/216 当作本卡结果。

待 owner / 后续（不阻塞本卡 formula）：
1. **OQ-4（本卡最相关）**：`reserve_volume` 维 5 个 driver 中 4 个下界为 0（`opening_reserves/additions/depletion/closing_reserves`），只有 `reserve_revisions` 为显式有符号 —— 向下的储量变动**必须**走修订科目，符号路由是契约事实而非业务约定，需 owner 确认与披露口径一致。
2. **OQ-1**：`other_revenue` 与 `reserve_revisions` 都属"无声明默认值却被静默补 0"的 5 个可选 driver 之一（全局 31 个）；"没有修订"与"没找到修订"在输入层不可区分。
3. **R10（不可运行验证项）**：消耗量不当然等于当期销售量、储量若已含回收率则不得重复扣 —— 披露层业务门，运行时不可验证。
4. **OQ-5**：窗口内产品文件被外部以字节相同内容重写（我 04:03 复算 hash 等于锚点），mtime 不可作未触碰证据。
5. **非阻塞整改（P2-1）**：`binding.json` 与 `before/` 实为运行后采集；下一次须真正前置。
6. **P3**：`commands.json` 字段名未按模板；`handoff.json.raw_exit_codes` 缺 `Z3/Z4/Z7`；A1 的 expected 0 / actual 1 只在文本注释标记。

### M11 · infrastructure

**独立复核裁决（独立 reviewer session，2026-09-20 04:03 +01:00，attempt `a20260919-01`）**

**结论：`accepted_scoped` —— 仅就 `formula` 授予通过；`disclosure_adaptation` 与 `accuracy` 不授予。**

已独立复验：我从 `card_M11.md` L13–31 原文抄录输入并**手算** 400×0.5+10=**210**，用隔离副本（sha256 `9ec65295…`，与生产逐字节相同）实跑得 `[210.0]`；defaults `[200.0]`、连续性手算 `[210, 300]`（实测一致）。我另造 3 年跨年输入 `[400,520,610]×[0.5,0.55,0.62]+[10,12,0]`，手算 `[210,298,378.2]` → 一致；零计费量、以及"负 `other_revenue` 但总收入非负"（100−40=60）→ 一致。卡片专属负例（`billable_volume=[-1]`）与 N01a–d/N02–N05b/CONT-BREAK 共 **11/11** 由 `ModelRegistryError` 拒绝，我另造 10 个清单外反例（字符串数字 `"1"` 于两个必填 driver、`years=[2027.0]`、`tariff` 注入 NaN 与 True、`other_revenue=[inf]`、未知 model_id、重复年份、负 `base_revenue`、数组长于 years）全部被目标异常拒绝，**无"应拒而被接受"**。`oracle.md`（03:35:36）早于首次产品 stdout（03:46:42），无"修订 r2"节，`oracle.json` 逐字节可重生成，冻结 hash 三处互证。变异测试与退出码口径同 M09（**1=harness、2=no-verdict/fidelity、3=negative、0=pass**）。

未授予：`disclosure_adaptation` 保持 `unmapped`（3 个 driver 全部 `state=missing`，来源勘察只证明"存在本地财报文件"，未提取任何字段）；`accuracy` 保持 `unproven`。D/E/F 未产出如实标注，未自签 accepted，未把历史 97/216 当作本卡结果。

待 owner / 后续（不阻塞本卡 formula）：
1. **OQ-3（本卡最相关）**：`tariff` 属 `revenue_per_activity`，默认域 `[0, inf)` —— **返还/负费率型资费在当前入口无法表达**（全库 23 个此类 driver 中仅 `renewable_generation.contract_price_per_mwh`、`merchant_price_per_mwh` 两个可为负）。若某管网/收费公路披露存在负费率或返还，须停适配并请 owner 裁定契约扩展，**禁止裁零**。
2. **OQ-1**：`other_revenue` 静默补 0；补贴/容量费"不可重复加入"这一业务负例在运行时不可观测。
3. **R10/R11（不可运行验证项）**：吞吐量不当然全额计费、阶梯费率须按监管生效日切分、补贴与容量费不得重复 —— 披露层业务门，运行时不可验证。
4. **OQ-5**：窗口内产品文件被外部以字节相同内容重写（我 04:03 复算 hash 等于锚点）。
5. **非阻塞整改（P2-1）**：`binding.json` 与 `before/` 实为运行后采集；下一次须真正前置。
6. **P3**：`commands.json` 字段名未按模板；`handoff.json.raw_exit_codes` 缺 `Z3/Z4/Z7`；A1 的 expected 0 / actual 1 只在文本注释标记。

### M12 · bank_revenue

**独立复核裁决（独立 reviewer session，2026-09-20 04:03 +01:00，attempt `a20260919-01`）**

**结论：`accepted_scoped` —— 仅就 `formula` 授予通过；`disclosure_adaptation` 与 `accuracy` 不授予。**

已独立复验：我从 `card_M12.md` L13–39 原文抄录输入并**手算** 1000×0.04−800×0.02+8+2 = 40−16+10 = **34**，用隔离副本（sha256 `9ec65295…`，与生产逐字节相同）实跑得 `[34.0]`；defaults 手算 40−16+8+0=**32**、连续性手算 34 与 1200×0.045−1000×0.025+9+0=**38**，均实测一致。我另造**负利率**两年例（`asset_yield=[-0.01,0.02]`、`funding_cost=[-0.005,0.01]`），手算 `[4.0, 23.0]` → 一致；总量恰为 0 → **被接受**（证明只拒 `<0`）；总量为负 → 被拒；`funding_cost=1.5` 这种"大利率" → **被接受**（证明显式 `(None,None)` 边界生效，未强加 0–1 限制）。卡片专属负例（`asset_yield=0, funding_cost=0.1, fee_revenue=0, other_revenue=0`）与 N01a–d/N02–N05b/CONT-BREAK 共 **11/11** 由 `ModelRegistryError` 拒绝；该专属负例的拒绝来自**总收入闸**（0−80+0+0=−80<0）而非利率域闸，`guard_hint` 已明确标注，与卡片 L48"负利率允许、不能重加 0–1 限制"的口径一致，**未把总量拒绝误记为利率拒绝**。我另造 10 个清单外反例（字符串数字 `"1"` 于 `average_earning_assets` 与 `fee_revenue`、`years=[2027.0]`、第二个必填 driver 注入 NaN/True、`other_revenue=[inf]`、未知 model_id、重复年份、负 `base_revenue`、数组长于 years）全部被目标异常拒绝，**无"应拒而被接受"**。`oracle.md`（03:36:33）早于首次产品 stdout（03:46:49），无"修订 r2"节，`oracle.json` 逐字节可重生成，冻结 hash 三处互证。变异测试与退出码口径同 M09（**1=harness、2=no-verdict/fidelity、3=negative、0=pass**，实测 rc = 0/2/3/1 全部落位）。

未授予：`disclosure_adaptation` 保持 `unmapped`（6 个 driver 全部 `state=missing`，无签署、无已结束期间收入对账）；`accuracy` 保持 `unproven`。D/E/F 未产出如实标注，未自签 accepted，未把历史 97/216 当作本卡结果。

待 owner / 后续（不阻塞本卡 formula）：
1. **OQ-2（本卡最相关）**：本卡唯一被拒的卡片专属负例是**总收入拒绝**，不是利率域拒绝 —— 利率 driver 保持显式 `(None, None)`，负数与大于 1 的利率都可表达；任何把它读成"银行比率被限制在 0–1"的结论都是错的。`common_model_cards.md` L11 亦声明：真实银行可能出现负营业收入；若披露落在契约外，停适配并请专业 reviewer 审定扩展，**禁止裁零或改会计口径造通过**。
2. **OQ-1**：`other_revenue` 静默补 0；本卡"手续费为已确认净额""净息差不等于资产收益率""不得用期末余额冒充平均余额"等业务负例在运行时不可观测。
3. **R10（不可运行验证项）**：生息资产/付息负债的平均余额口径与费用净额口径是披露层业务门。
4. **OQ-5**：窗口内产品文件被外部以字节相同内容重写（我 04:03 复算 hash 等于锚点）。
5. **非阻塞整改（P2-1）**：`binding.json` 与 `before/` 实为运行后采集；下一次须真正前置。
6. **P3**：`commands.json` 字段名未按模板；`handoff.json.raw_exit_codes` 缺 `Z3/Z4/Z7`；A1 的 expected 0 / actual 1 只在文本注释标记。

---

## 附：本次复核产出的脚本与原始输出（均在 `%TEMP%\m09m12-review-20260920-035628\`）

| 文件 | 用途 |
|---|---|
| `probe.py` / `probe_result.json` | 卡片正例 + 自造输入 + 自造负例 + 独立注册表枚举 |
| `mutate.py` / `mutation_result.json` | 我自己的 runner 退出码变异测试（24 次运行） |
| `extra_checks.py` / `extra_checks.json` | harness 码位（rc=1）与 oracle 逐字节重生成（4 卡） |
| `count_split.py` | 40/3 与 41/4 的谓词差异定位 |
| `summarize.py` / `summarize2.py` / `verify3.py` / `peek*.py` | attempt 证据的结构化核对（负例、hash、资格、命令台账） |
| `enum/{M09,M12}/registry_enumeration.json` | 重跑其枚举脚本的输出（与其证据逐字节相同） |
