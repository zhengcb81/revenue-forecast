# I-12-BE / a20260926-01 · A 级独立复审（reviewer_report）

**VERDICT: ACCEPT —— P1 = 0**（无数值错 / OPEN-2 红线未破 / 封盘未动 / 段 D `metric_numeric_oracle`+负例先于真实样本）；附 **P3 × 9、P2 = 0**

- 复审工位：**独立复审**（统计面 + 行业面知识）· 对象 = 合并单元 **`I-12-BE`**（原 `I-12-B/C/D/E` 四段，各 attempt `a20260926-01`，`handoff=True`、`status=review_pending`）· **一次复审覆盖四段**
- 产出面 = **2 新文件（新目录）**：`execution_runs/I-12-BE/a20260926-01/reviewer_report.md` + `reviewer_report.sha256`；**四段与上游全部只读**（收尾复哈希见 §5）；**不写任何卡 `status`/`decision`/`decision_sha256`**
- 判级规则：`P1` 仅限 数值错 / 红线破 / 封盘动 / 段 D 未先跑 oracle ⇒ `changes_required`；否则 `ACCEPT`（可带 P2/P3）。本轮 **P1=0、P2=0、P3=9**
- `I-12-A` 的 **`STOP①`（专业签署未解）是上游状态**：四段只要如实登记「未解封、测试/准确性结果封存未读」即合规 ⇒ **不因 `STOP①` 判 P1**（本轮亦未判）。四段 4/4 均登记 `test_results_unsealed=false` + `accuracy_results_read=false`（handoff/verification 双处，实测各 1 处 ×4）

## §0 复审基线（本工位实测 bytes / sha256 / mtime；**父落定请复哈希此表，勿用派单尺寸**）

| 段 | 件 | bytes | sha256 | mtime |
|---|---|---|---|---|
| B | `oracle.md` | 12,443 | `d5402c9bb3ccd750f3a3e909ed7aba8006e3e5f007f940d16d0c24220ff7b5be` | 20:55:27 |
| B | `verification.json` | 14,017 | `c7d04b137ffd42945ffbddefca4486a83fd035a2a848bed954e5ecbd3012ed41` | 21:28:16 |
| B | `handoff.json` | 16,408 | `a11c16010c795bc6f54ef8f5d9a325e95ba0eee9380e807857704d76a71ed19c` | 21:28:46 |
| C | `oracle.md` | 13,681 | `e0836fa4752116456fc38a8cf52c72802b54bc9b199bc5fcb970e1bf7668873f` | 21:05:53 |
| C | `verification.json` | 16,463 | `771f70a9bbc09c7706c8e2d9fa3c683c69d8875ad60bc95b60a6c5128f71f370` | 21:28:16 |
| C | `handoff.json` | 16,154 | `90f915c09935504c0b070b03a9c1cbcb28c5ac0f688d1bc2f9800780f45b0c74` | 21:28:46 |
| D | `oracle.md` | 14,057 | `c631c201571218cc688a969c22412aeac5e35802903c86396bdf1ec4e4eb0daa` | 21:15:33 |
| D | `verification.json` | 16,634 | `b31fb2510bce5afeabd0e0a8e5dca2835b0917f0cbcd76e2e91dade839156de3` | 21:28:16 |
| D | `handoff.json` | 16,609 | `105d883374b6f013d06656098605358a592f9803301dd241bf02f5ecf7e1131e` | 21:28:46 |
| E | `oracle.md` | 13,495 | `f03e5223613907d5e85e22eb6f11eeb3bb9a9d74dbd06a8d61fe7f84b848a890` | 21:23:19 |
| E | `verification.json` | 17,701 | `d3377777f2139b1d3e3a9e866057aeab6700dd23f72c9e41b0c3fdaf4d01267c` | 21:28:16 |
| E | `handoff.json` | 14,992 | `2e9feff3697eec94a8775face68aaae4bbbb2daea15990d9af080a8cff446196` | 21:28:46 |

> `ACCEPT` 语义边界：本报告只出复审裁决，**不写任何卡 `status`/`decision`/`decision_sha256`**；四段的落定（`accepted_scoped`）与 `blocked/limited/descriptive_only/inconclusive` 档位的最终裁定权仍在编排层/父落定。

## §1 裁决行 + 发现清单（逐段记 `id / 级 / 摘要`）

**裁决行定位**：本文件 L3（`VERDICT: ACCEPT …`）为唯一裁决行；判级依据见 L6 规则行。四段**自身**无裁决行（实现者不自签）：其结论登记于各自 `handoff.card_stop` / `handoff.accuracy=unproven` + `verification.conclusion`，`status` 全部 = `review_pending`（实测 4/4）。

| 段 | 裁决行/结论载体 | 本工位结论 | 发现 |
|---|---|---|---|
| **I-12-B** | `handoff.card_stop.acceptance_state`（`blocked`-`limited`） | **ACCEPT** | B-1/P3、B-2/P3 |
| **I-12-C** | `handoff.card_stop` + `forecast_manifest.stop_registration` | **ACCEPT** | C-1/P3、C-2/P3 |
| **I-12-D** | `verification.conclusion` + `paired_comparison.state=blocked_no_scorable_samples` | **ACCEPT** | D-1/P3、D-2/P3 |
| **I-12-E** | `accuracy_qualification.premise` + `comparisons[6].verdict=inconclusive` | **ACCEPT** | E-1/P3、E-2/P3 |
| **全局** | 本报告 §2⑥ | **ACCEPT** | G-1/P3 |

**发现清单（9 条，全部 P3；无 P1/P2）**

- **B-1（P3 · 已登记未决）** `u-N4`：`US-MSFT-10K-FY2026` 注册 sha 为 **63 位**（`…40ecff`）而实测 64 位（`…40ecfff`），段 B 只登记 `registered_not_corrected` 并列入 `open_questions`，未更正 U15/U17（正确处置：不由本卡改上游）。裁定权=独立复审/编排层，**至今未裁**。
- **B-2（P3 · 能力边界）** 段 B 全部来源 sha 均为**转录**（`hash_verified_this_station=false`，3 信息输入 + 2 豁免输入逐行声明），本卡不自证 raw ⇒ 独立 reviewer 追溯止于 I-11-A `source_map` 层；raw 回源重哈希不在本批授权面。
- **C-1（P3 · 待追认）** `seasonal_same_quarter` 已按卡文动作 2 标 `not_applicable`（年度序列无同季序列），但 `approval=pending_reviewer`（本卡不自批）；缺历史期实为 **0 例**（紫金 FY2024–FY2025 / 微软 FY2025–FY2026 均 origin 前披露）⇒ 该 `not_applicable` **需本复审/编排层追认**后才算获批。
- **C-2（P3 · 自指尾）** `run_logs.json` 中 `verify_green_after_runlogs` / `verify_final` 两条 `rc=null`（声明"由 verification.json / final_green_output.txt 记录，不预写"）。实跑 rc 未在 run_logs 内复现，须由复审复跑确认（本工位实读两件原始输出：`RESULT ALL_INVARIANTS_OK`）。
- **D-1（P3 · 措辞不精确）** 段 D 把设计字段 11 写作「`PENDING/unsigned`」（oracle §2、`paired_comparison.interval_method_pending_items`），而 `evaluation_design.json` 实际 `fields[11].status = filled_threshold_unsigned`（**已填未签**）；真正 `PENDING` 的是字段 **5/10/12**。实质结论（"无可批准方法 ⇒ 不算区间"）不受影响，措辞应分档。
- **D-2（P3 · 登记面不完整）** 四段签署状态只引 U9 `professional_approval.json`（双 `unsigned`），**未并入**已落地的两个载体：`I-12-A-STAT-SIGN`（handoff mtime **20:58:18**，`signed=3/not_signed=3`：S3 CI 95%、S4 B=10,000+seed、S5 Holm 已签；S1/S2/S6 拒签）与 `I-12-A-IND-SIGN`（**21:02:39**，`signed=10/not_signed=IND-07`）。段 D（oracle 21:15:33）、段 E（21:23:19）冻结时点**晚于**两者却仍登记「双双 unsigned / 6 项全 PENDING」。**结论不变**：`design_manifest` 未重冻（sha `ad46a6e6…` 实测未变）、`unseal_gate.currently_satisfied=false`、S1/S2/S6 + IND-07 未签 ⇒ `STOP①` 仍成立、字段 10/12 仍无值、n=0 ⇒ 区间仍不可算。属登记完整度问题，**不判 P1**。
- **E-1（P3 · 口径混用）** 披露栏用 **case 口径**「4 signed（`ZJ-MIN-M09`/`ZJ-SMT-M09`/`XM-PHONE-M03`/`XM-EV-M03`）+ 2 STOP + 3 段无 case」（分母 9 个 case，含已排除小米的 2 个），段 C 用 **样本段口径** `disclosure_qualification_counts = {signed:2, stop:2, uncovered:3}`（分母 = 7 样本段）。两口径并存且未标注换算（in-sample 实为 signed=2），读者易把「4 signed」读成样本内 4 段。三栏禁覆盖（accuracy=`unproven`）不受影响。
- **E-2（P3 · 绿臂返工，已如实登记）** `GREEN_FIRST rc=3`（`FAIL E5: limitations.md missing token '生命周期'`，覆盖表用了英文 `lifecycle`）→ 补中文标签后 `GREEN_AFTER_FIX rc=0` → `GREEN_FINAL rc=0`。证据在 oracle 冻结**之后**修改属正常（oracle 冻结判据、不冻结证据），且 `verification.green_arms` 三态留痕；提示 E5 判据含 **token 硬匹配**，后续措辞编辑易再次触发。
- **G-1（P3 · 记录性）** 四段 `verification.json`/`handoff.json`/`final_green_output.txt` 的 mtime **完全同秒**（21:28:16 / 21:28:46 / 21:29:01），提示收尾为**一次性批量定稿**；各段的独立冻结点（gate0 20:54:24 / 21:04:49 / 21:14:27 / 21:22:34 → oracle 20:55:27 / 21:05:53 / 21:15:33 / 21:23:19）仍逐段独立成立，sha 自洽（§0、§5）。

## §2 六项复核（A 级全量档，四段都要）

### ① 裁决行 + 发现清单
见 §1（裁决行 L3；发现 9 条，全 P3，P1=0、P2=0）。四段 `status=review_pending` 4/4、`gate0_passed=true` 4/4、`releases_nothing=true` 4/4、`git_diff_non_planning=0` 4/4、`params_released=false` 4/4、`implementer_signed=false` 4/4、`open2_ban_observed=true` 4/4（实测自 handoff.json）。

### ② 段 B —— 样本与实际值
1. **`sample_id` 唯一**：`sample_manifest.jsonl` **7 行 / 7 唯一**（自算），且 `SMP-<ENTITY>_<SEGCODE>_<ORIGINYYYYMMDD>_<HORIZON>` 与四键逐字一致 **7/7**（自算，0 处不符）。
2. **筛选/排除全量表**：`exclusions.jsonl` = EX-001（entity 级：小米，gap-U1/gap-U2，`banned_substitution`="不补选表现更好的公司"）+ EX-002/EX-003（row 级：紫金/微软 `TOTAL` 合并行，设计字段 2 duplicate_rule）+ `conservation_summary`。自算守恒：`3 = 2 + 1` ✓、`9 = 7 + 2` ✓、`included_rows(7) = manifest 行数(7)` ✓、`missing_count=0`。
3. **`available_at<=origin` 逐条**：7/7 样本 `available_at_le_origin=true` 且 `available_at<=origin` 字符串序比较自算 **0 违例**；`source_vintages` 5 行 = 3 信息输入（`CN-ZIJIN-AR2025` 2026-03-20==origin、`US-MSFT-10K-FY2026` 2026-07-29==origin，均 `pass`）+ 2 豁免（协议/转录，各带 `exemption_reason`）；`HK-XIAOMI-AR2025` `available_at=null` ⇒ **`state=quarantined_unavailable`、`quarantine=true`、`used_by_samples=[]`**（疑义隔离，未事后补值）✓
4. **vintage 保留 / reconstructed 单列**：7/7 `vintage_class=true_vintage`、`reconstructed=false`、`reconstructed_mixed_into_true_vintage=false`（J4，`reconstructed=0`）；实际值 7/7 `actual_value=null`、`scorable=false`、`actual_state=target_period_not_yet_existing_and_sealed`；`split_manifest` 四集全 0 + `state=PENDING_unsigned`（字段 5 未签，不自选切点）。
5. **判据/变异**：`J1–J9` 全绿（`final_green_output.txt` 逐行 `CHECK … OK` + `RESULT ALL_INVARIANTS_OK`）；红臂 **M1–M5 五臂 rc=3**（重复 id / future leakage / 计数不守恒 / 红线字面量 / `params_released=true`），`pre_post_sha_match=true`。
6. **停止条款**：停止① `STOP_DATASET=false`（7/7 通过、缺 origin 0）；停止② `limited=true`（可评样本 0：目标期 FY2027 未结束 + 解封门未满足）⇒ `acceptance_state=blocked`（合格形态，非绕过），`traceable_to_actual_value=false` 已如实登记。

### ③ 段 C —— 冻结预测与基线
1. **同 sample 只用 origin 前资料**：`forecast_vintages.jsonl` 7 行，逐行 `information_set = "origin 以前资料 only（本行未使用任何 origin 后信息；构造驱动的模型运行=0）"`、`vintage_class=true_vintage_information_set`、`reconstructed=false`；`forecast.low/base/high` 全 `null`、`forecast_value_state=not_produced_params_not_released`（`params_released=false` + `binding_status=unbound` ⇒ **授权边界，非造数**）。
2. **模型/配置/参数/manifest/日志齐**：五件证据齐（2 jsonl + `forecast_manifest.json` + `run_logs.json` + `unblind_receipt.json`）；`run_logs.model_runs=[]` + 原因、`commands` 全落本 attempt 目录、`network_used=false`/`git_used=false`/`writes_outside_attempt=0`；`forecast_manifest.input_hashes` 两个 jsonl 与本工位实测**逐位一致**；`low_high_semantics=scenario_band_not_probabilistic`（设计字段 9）；`reruns_performed=0`。
3. **读实际值前冻结（时间序证据）**：`gate0 21:04:49 → oracle 21:05:53 → 证据 21:08:51（forecast/baseline/manifest/unblind 同批）→ run_logs 21:10:32 → verification 21:28:16`；内容面 `freeze_before_unblind=true`、`actuals_read_by_this_station=false`、`target_period_actuals_read=false`、`unblind_receipt.issued=false / issued_by=null / this_station_cannot_issue=true`、`preconditions_unmet` 6 项（双签、13 字段、manifest 重冻、解封指令、FY2027 未结束、零数值预测）⇒ 零暴露 ⇒ 停止①「冻结晚于读值 ⇒ exploratory」**不触发**（`exploratory_downgrade_required=false`）。
4. **缺历史期标 `not_applicable`**：`seasonal_same_quarter = not_applicable` + 理由 + `approval=pending_reviewer`（见 C-1）；缺必需历史期 **0 例**（逐样本 origin 前披露期齐备），**未用未来资料补齐**。
5. **基线**：`baseline_vintages.jsonl` **14 行 = 7 primary + 7 secondary**，每样本各 1 条；全部 `value_state=frozen_rule_output_from_disclosed_origin_available_actuals`、`is_released_parameter=false`、`params_released=false`、`future_information_used=false`、`available_at<=origin=true`、`applicable=true`；`not_applicable` 字面在 jsonl 中 0 次（因无缺期样本，符合 manifest 声明）。**披露资格按段**：signed 2 / stop 2 / uncovered 3 = 7 ✓；`STOP_MODEL_ADAPTATION` 触发（MS-PBP-M05/MS-IC-M06）但按卡文"不阻止其他已合格模型继续"；未覆盖段另码登记，不混同"通过"。

### ④ 段 D —— 指标与不确定性
1. **`metric_numeric_oracle` + 负例先跑（硬前置）—— 在**：
   - 产物在：`evidence/I-12-D/metric_oracle_result.json`（8,415 B）+ `metric_negative_results.json`（5,988 B），**两件 mtime = 21:17:29**；真实样本面（`sample_errors.csv`/`metrics_by_stratum`/`paired_comparison`/`interval_diagnostics`/`metric_reproduction`）**mtime = 21:18:11** ⇒ **oracle 早于真实样本 42 秒**；脚本序 `_metric_oracle.py 21:17:22 → _build_sample_evidence.py 21:18:07`；oracle.md 21:15:33 先于两者。
   - 结果：`synthetic=true`、`qualification=metric_implementation_only_not_accuracy_evidence`；`expected_comparisons` **14/14 `pass=true`**（期望值独立来源 = `research_cards.json metric_numeric_oracle.expected`，sha `4a22e266…` 实测一致）；`probabilistic_interval_subcase.precondition_met=false` / `computed=false`（未算）。
   - 负例 **5/5 `pass=true`**：①零分母 ⇒ WAPE/NormalizedBias/normalized_width = `undefined`+`zero_denominator`、MAE 仍可定义、**未加 epsilon**；② `forecast_sample_ids=[S1,S3,S2]` ⇒ `rejected`/`sample_id_misalignment`（拒按位置评分）；③ baseline loss=0 ⇒ `skill=undefined`（未记 100%）；④ high<low ⇒ `interval_data_error`、`mean_width=undefined`；⑤ 无名义覆盖 ⇒ `interval_score`/`pinball` 请求即拒。`stop_triggered=false`。
2. **逐样本 signed/abs 明细**：`sample_errors.csv` **仅表头（14 列，含 `signed_error`/`abs_error`/`baseline_abs_error`/`scorable`/`exclusion_reason`）、0 数据行** —— 与上游 `scorable_samples=0`、`forecast_values_frozen=0` 一致（**不是"只留平均数"**，是无可评观测）。
3. **成对比较 + 分层报告**：`paired_comparison.json` `n_pairs=0`、`state=blocked_no_scorable_samples`、`cluster_unit=entity`/`block_unit=origin`（重复年度非独立公司）、`paired_differences=[]`、`skill_vs_baseline.value=null/defined=false`、`uncertainty_interval=null` + `interval_method_not_approved=true` + **5 项未批清单**；`metrics_by_stratum.json` **7 层**逐层 `n_companies`/`n_origins`/`n_scorable=0`/`state=descriptive_only`、`significance_claimed=false`、零分母与缺失计数器在位。
4. **动作 4 四类并报 + 禁用统计区间得分**：`interval_diagnostics.json` `probabilistic_claim_made=false`、`interval_score.enabled=false`（无 1-alpha 事前声明）、`pinball.enabled=false`、`confidence_intervals.computed=false`（未签 ⇒ 无"已批准方法"）+ `no_seed_fixed_by_implementer=true`；情景包含率/宽度 `n=0 ⇒ null/defined=false`。
5. **不换指标**：指标集合 = 冻结 `metric_definitions`（sMAPE/MASE/interval_score/pinball 未事前声明 ⇒ 不启用）；`metric_reproduction.md` 含手算过程 + 复跑命令 + limitation 逐字。
6. **判据/变异**：`D1–D10` 全绿（final green 逐行 OK）；红臂 **P1–P5 五臂 rc=3**（改 oracle 期望 / 零分母塞 epsilon / 伪造明细行 / 未签却出 95% CI / `significance_claimed=true`）。

### ⑤ 段 E —— 分范围判定
1. **按冻结阈值判三态**：卡文前提实测 **0/2**（阈值未在结果前批准 + 全量结果不可见）⇒ 6 个预注册比较 **全部 `inconclusive`**（`supported=0`、`unsupported=0`、`inconclusive=6`），逐条 `threshold_state=unsigned`、`threshold_applied=null`、`verdict_is_fail_closed_default_not_professional_determination=true`、`judge_authority=统计+行业 reviewer（not_assigned）`；`negative_skill_preserved_rule=true`、`failed_strata_preserved_rule=true`（负 skill/失败层以字段冻结，n=0 无值可删）。
2. **限定六键 + 未覆盖分层标 `unproven`**：`scope_limitation` 六键齐全（`dataset`/`model_version`/`industry`/`lifecycle`/`disclosure_quality`/`horizon`）+ `no_generalization`；`uncovered_strata` **7 项全 `unproven`**（market=H、industry、lifecycle、披露 STOP 段、无 case 段、model_version、dataset 外推），**0 项被标 `proven`**。
3. **三栏未互相盖**：`formula_qualification=pass_scoped`（M01–M31，仅 A–C 公式面）/ `disclosure_adaptation=partial` / `accuracy=unproven`；`no_cross_column_pass_override=true`、`formula_pass_does_not_imply_accuracy=true`、`disclosure_signing_does_not_imply_accuracy=true`、`accuracy_improvement_claimed=false`，并列 3 条 `override_examples_forbidden`。
4. **停止条款**：`STOP_CLAIM=false`、`STOP_RELEASE_WORDING=false`（均附 basis）；`limitations.md` 含 `unproven`/`inconclusive`/`descriptive_only`/`STOP_CLAIM`/`STOP_RELEASE_WORDING`/覆盖缺口/负结果与不确定性保留/n=0，且无"准确率提升"式结论。
5. **动作 4**：`error_taxonomy.json` **6 类**（`data/definition/driver/timing/structure/random`）各 ≥1 条、`follow_up_questions` **6 条**（≥3）、每条带 `source_ref`、`forecast_fixed_this_round=false`。
6. **独立统计复审件**：`independent_statistical_review.md` `reviewer_assigned=false`、`reviewer_signed=false/unsigned`、`implementer_signed=false`、`verdict_issued=false`、`produces_ACCEPT=false`，明确"本件是状态登记、不是签署"，并列出交本工位的 6 项复审清单。
7. **判据/变异**：`E1–E10` 全绿；红臂 **Q1–Q5 五臂 rc=3**（改 `supported` / 一栏盖另一栏 / 31 公式说成准确率提升 / 红线字面量 / 删 `random` 类 + 清空后续问题）。

### ⑥ 全局 —— 红线 / 封盘 / 上游 sha / 变异
- **OPEN-2 红线（`124,248.63`，真值 `38,175.95`）只登记未消费**：四段 `evidence/**` 扫描 `124248.63|124,248.63|38175.95` = **0 命中 ×4**；`consumed_for_forecast` 在四段（oracle/handoff/verification/evidence）= **0 命中**。字面仅出现于各 `oracle.md` §4 登记行（B L73/L87/L103、C L83/L96/L114、D L78/L93、E L80/L94/L110）、B/C/E `handoff.dispatch_verbatim` 转引与 `verification.red_arms` 红臂描述（B L224/L228、C L270/L274、E L268/L272）。⇒ **红线未破（P1 不成立）**。
- **红线自算**：`109,977,556,345 ÷ 885,141 = 124,248.63`；`÷ 2,880,807 = 38,175.95` ⇒ 与登记值逐位一致。
- **封盘**：`execution_runs/I-11-A/a20260919-01/evidence/I-11-A/hypotheses.json` 本工位自算 = **`f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28` / 51,697 B** ⇒ 与派单 `f2178768…` 逐字节一致，**零字节改动（封盘未动 = P1 不成立）**；store `hypotheses_v3.json` = `b2063ac8…` / 61,231 B 一致。
- **四段上游 sha 一致性**：各 `verification.upstream_consistency` 声明 B `17/17`、C `21/21`、D `18/18`、E `21/21`；本工位对四张 §2 表**去重后的 33 个上游路径全部现场重算 ⇒ 33/33 一致**（含 4 张卡文、`research_cards.json`、`common_research_cards/START_HERE/review_and_handoff/OWNER_DECISIONS`、I-12-A 三件 + handoff、I-07-E 三件、I-11-A `source_map`、披露适配 v2 + I-10-A 前像、以及 **B→C→D→E 互引的 12 件段内证据**）。
- **四段自产物 sha**：各 `handoff.written_files` 逐条复算 **46/46 一致**（B 11 + C 11 + D 14 + E 10）。
- **红绿变异（合并卡验收"全局红绿 ≥3 覆盖四段"）**：B `M1–M5`、C `N1–N5`、D `P1–P5`、E `Q1–Q5` = **20 红臂全部 rc=3**；绿臂 B 3 / C 3 / D 2 / E 3 全 rc=0（E `GREEN_FIRST rc=3` 见 E-2）⇒ **四段各 ≥3，达成**。
- **`I-12-A` 三件上游**：`evaluation_design` **13 字段自算** = 9 `filled`(idx 1,2,3,4,6,7,8,9,13) + 1 `filled_threshold_unsigned`(idx 11) + 3 `PENDING`(idx 5,10,12) + 0 `not_applicable` ✓（与 I-12-A reviewer_report 断言一致）；`professional_approval` 仍 `status=BLOCKED_PROFESSIONAL_DECISION`、双 reviewer `unsigned`、6 项阈值 `PENDING`、`test_results_read_before_signing=false`；**双面签署结果**（另两载体）= 统计 **3 签/3 不签**、行业 **10 签/1 不签**、**`STOP①` 未解除**（两载体 handoff 均自记 `BLOCKED_PROFESSIONAL_DECISION_still_triggered`、`unseal_gate_unchanged`）⇒ 四段登记的"未解封 + 结果封存未读"**属实**。
- **`I-07-E` summary**：sha `a2304fdd…` / 26,132 B 实测一致；被四段转引的两个红线数字由本工位自算复核（见上）。

## §3 三处 spot-check（本工位自算，非复用被审数字）

- **SC-①（段 B · 样本表与守恒）** 读 `sample_manifest.jsonl` + `exclusions.jsonl` 自算：行数 7、唯一 `sample_id` 7；`SMP-<ENTITY>_<SEGCODE>_<ORIGIN>_<HORIZON>` 与四键逐字一致 **7/7**；`available_at<=origin` 违例 **0**；`entity_ex=1`、`row_ex=2` ⇒ `3 = 2+1` ✓、`9 = 7+2 = manifest(7)+excluded(2)` ✓、`included_true=7`、`vintage_class` 唯一值 = `true_vintage` ⇒ **与 J1/J2/J3/J4 及 conservation_summary 全部吻合 ✅**
- **SC-②（段 C · 基线精确算术）** 对 `BL-S-CN-ZIJIN_MINERAL_20260320_FY2027` 自算 `R(base)³ / R(prev)²`（BigInteger 精确）：`109977556345³ = 1330185461539019155329647609763625`、`74089365354² = 5489234058558495545316` ⇒ 与 `value_exact.numerator/denominator` **逐位相等**；浮点复算 `≈ 242,326,242,122.08` ⇒ 与 `decimal_2dp_half_up` 一致；primary `109,977,556,345`（FY2025 同口径，origin 2026-03-20 前已披露）作为 `value_state=frozen_rule_output…` ⇒ **基线确为规则输出、非放行参数 ✅**
- **SC-③（段 D · 指标手算）** 用冻结 fixture `actual=[100,0,200] / forecast=[110,10,180] / baseline=[100,0,150] / low=[90,0,170] / high=[120,20,190]` 自算：`signed=(10,10,−20)`、`Σ|e|=40`、`分母=300`、`MAE=40/3=13.3333…`、`WAPE=40/300=2/15=0.13333…`、`Bias_U=0`、`NormalizedBias=0`、`skill=1−40/50=0.2`、`contained=(T,T,F)⇒2/3`、`mean_width=70/3`、`normalized_width=7/30` ⇒ 与 `research_cards.json metric_numeric_oracle.expected`（冻结独立来源）及 `metric_oracle_result.computed` **逐项一致 ✅**
- **旁证（红线自算）** `109,977,556,345 ÷ 885,141 = 124,248.63`、`÷ 2,880,807 = 38,175.95` ✅

## §4 `unverified`（超出回源清单 / 未做，不背书）

1. **未重跑**任何 `_verify.py` / `_run_mutations.py`；红臂 rc=3、`_mut/**/verifier_output.txt` 原文与 `mutation_results.json` **未复现**（派单禁重跑变异）；`_mut/**` 目录零触碰。
2. **未读任何测试集/准确性结果**（封存令）；`accuracy=unproven` 未评估、不评估。
3. `_build_evidence.py` / `_metric_oracle.py` / `_verify.py` / `_run_mutations.py` **源码未逐行审计**（仅对产物、判据、mtime 时间序做核）。
4. **raw 源文件**（紫金 AR2025 / 微软 10-K / 小米 AR2025）**未回源重哈希**（不在本工位授权面）；`u-N4` 63/64 位差异同此未裁。
5. `I-07-E/calibration_validation_summary.md` 全文未逐行复核：只核 sha 与被转引的两个红线数字；`I-07-E/verification.json`、`handoff.json` 只核 sha。
6. `metrics_by_stratum` 7 层的**标签语义**未逐层回源设计字段（只抽 `n_companies`/`n_origins`/`n_scorable`/`state`/`significance_claimed`）。
7. `I-12-A-STAT-SIGN` / `I-12-A-IND-SIGN` 两载体**只读 handoff 关键字段**（签署计数、`stop1_state`、`unseal_gate_unchanged`）；`ruling_*.md`、`stat_signatures.json`(35,760 B)、`ind_signatures.json`(37,009 B) 全文与其红臂未读。
8. `evaluation_design.json` 13 字段只核 `index`/`status`（+字段 8 `not_applicable` 子项），字段**取值内容**未逐字核。
9. 本报告**不裁定**档位：B 的 `blocked-limited`、C/E 的 `blocked`、D 的 `descriptive_only`、E 的 6×`inconclusive` 最终改档权 = 编排层/父落定 + 统计/行业 reviewer 签署。

## §5 收尾复哈希（只读件；本工位实测）

| 件 | bytes | sha256 | 结论 |
|---|---|---|---|
| `I-11-A/…/hypotheses.json`（**封盘**） | 51,697 | `f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28` | 与派单一致，零字节 ✅ |
| `OPEN2-C2-REGISTRATION/…/hypotheses_v3.json`（store） | 61,231 | `b2063ac8533a96ba0be8095293e30191cc0796a7eb84dcd16dac0b71aff413ff` | 与四段登记一致 ✅ |
| `execution_v2/card_I-12-B.md` | 1,549 | `f61906a9900a9ddab8f32284937728bede34f95c219112dd3486c2bf9fae695b` | 与 B/C oracle 一致 ✅ |
| `execution_v2/card_I-12-C.md` | 1,604 | `49dbb572c7fc996721c1f096fc1743df67974c9020c4faf226a123929d0a6d91` | 与 B/C/D oracle 一致 ✅ |
| `execution_v2/card_I-12-D.md` | 1,776 | `c6595cef4b3523c4fd4a879cd8f4106675130463f5573d09efb812fc6dbd4f69` | 与 D/E oracle 一致 ✅ |
| `execution_v2/card_I-12-E.md` | 1,469 | `3c7d6da514dc9897bd7575a2e8e883bd9f883be89d1bdda6075d23a7f1ed497b` | 与 E oracle 一致 ✅ |
| `execution_v2/research_cards.json` | 40,058 | `4a22e26608d421799e2b8adde0d0424fa48a634509a0559c51d279e06d918263` | 与四段 U 表一致 ✅ |
| `I-12-A/…/evaluation_design.json` | 22,317 | `203dd4a8a138b6456de2b9f7e6b7e34855d137b8d2324caea21185fbb136f2c0` | 一致（13 字段自算通过）✅ |
| `I-12-A/…/professional_approval.json` | 5,334 | `0befb15460985140476e953e070531592fdbac6d30986e7d163e82637be36bb1` | 一致（双 unsigned / STOP① 在）✅ |
| `I-12-A/…/design_manifest.json` | 5,618 | `ad46a6e69dc9fc5c826cf71bb91102e9c86e6d5506e8c9b2c525a73be7fb7178` | 一致（**未重冻** ⇒ 与 D-2 自洽）✅ |
| `I-12-A/handoff.json` | 16,285 | `7bf747b15bf97032f75f9377a9c7bf1c2c023c54c272975cc8b30450ef11c714` | 一致 ✅ |
| `I-07-E/…/calibration_validation_summary.md` | 26,132 | `a2304fdd082583e7a0395955db9629106b546df549f2f560218f7bd8a8b906eb` | 一致 ✅ |
| `I-12-B/…/sample_manifest.jsonl` | 11,085 | `679a7a496e87ed953311d8d8139b47576ab84ddf7f0f0a4238991695d4ef0702` | B 产物 = C/D/E 上游引用，一致 ✅ |
| `I-12-C/…/forecast_manifest.json` | 5,467 | `03cdb01c71b232b8797e2eedf1503d3d8b0b5407a6c93cf7cb9e0384da26922a` | C 产物 = D/E 上游引用，一致 ✅ |
| `I-12-D/…/metric_oracle_result.json` | 8,415 | `0d64d62e0f60df0a253bea58b9cb0841b0377198631cccdc7a0109e7366e83ca` | D 产物 = E 上游引用，一致 ✅ |
| `I-12-D/…/metrics_by_stratum.json` | 12,085 | `ad14f515bcb4f796bf063957a5a005f26b08babea312b94a6367de98b3392e2e` | 一致 ✅ |
| `I-12-D/…/paired_comparison.json` | 1,961 | `5709203bac2753c37fe6c56853f4f6d875d5149a1fd56edc993f275ce6e2e0d5` | 一致 ✅ |
| 四段 `oracle.md` / `verification.json` / `handoff.json` ×12 | 见 §0 | 见 §0 | 与 §0 基线一致 ✅ |
| 四段 `handoff.written_files` 46 条 sha+bytes | — | — | **46/46 复算一致** ✅ |
| 四张 oracle §2 表去重上游 33 路径 | — | — | **33/33 复算一致** ✅ |

**写入本报告后的二次复哈希**：上表 29 件（含封盘、store、四张卡文、I-12-A 三件 + handoff、I-07-E summary、段间互引证据、四段 `oracle/verification/handoff` ×12）在本文件写入后重算 ⇒ **29/29 逐位一致、0 处不符**；结合 §0/§2⑥ 的 33 上游 + 46 自产物复算，**四段与上游零字节改动**。

## §6 没做的事（纪律自宣）

**只写 2 个新文件**（`reviewer_report.md` + `reviewer_report.sha256`，新目录 `execution_runs/I-12-BE/a20260926-01/`）· **不写卡状态**（零 `status`/`decision`/`decision_sha256` 改动）· 四段与上游**只读**（§5 复哈希佐证，含封盘零字节）· **禁 git 写、禁 `git status`（零 git 调用）** · **禁联网（零外部检索）** · **不读测试/准确性结果（封存令）** · 不重跑校验器/变异（`_mut/**` 未触碰）· 不改原四卡一字 · 不派卡、不触发任何 falsifier/自动动作 · 未做的事见 §4（9 项 `unverified`）。
