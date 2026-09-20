# M27 · implementer review record

Card M27 (`renewable_generation`), Parent I-10. Attempt `execution_runs/M27/a20260919-01`.

> ## PENDING independent review
> **Nothing in this file is an acceptance.** The implementer is not the reviewer. `formula` is recorded as `review_pending`; `disclosure_adaptation` stays `unmapped`; `accuracy` stays `unproven`.
> A separate session must read the artefacts below and issue its own verdict (`accepted_scoped` / `changes_required` / `blocked` / `not_applicable_with_reason`).

## 1. What was done

| Step | Result | Evidence |
|---|---|---|
| A binding | production code copied read-only into an attempt-local snapshot; hashes recorded and equal | `binding.json`, `evidence/M27/source_manifest.json` |
| B positive | `[264000.0]` vs independent oracle `[264000.0]`, within `1e-9*max(1,|e|)` | `evidence/M27/formula_result.json` |
| continuity positive | actual `[264000.0, 564100.2000000001]` vs oracle `[264000.0, 564100.2]` | `evidence/M27/negative_results.json` |
| defaults case | actual `[262800.0]` vs oracle `[262800.0]` (not gating) | `evidence/M27/negative_results.json` |
| C negatives | 11/11 rejected with `ModelRegistryError` | `evidence/M27/negative_results.json` |
| mutation proof | A/B/D red (rc=3), C green (rc=0), E byte-identical | `recovery/selfcheck/selfcheck_result.json` |
| D mapping | **NOT delivered**: no real disclosure was adapted; the per-driver mapping is explicitly `missing` and the professional decisions are PROPOSED only | `evidence/M27/disclosure_mapping.json`, `evidence/M27/accounting_decision.md` |
| E probe | `not_applicable_with_reason`; NOT a scenario set and NOT accuracy evidence | `evidence/M27/historical_mapping_probe.json` |
| F accuracy | **NOT DONE** - needs the I-12 frozen design | `evidence/M27/qualification.json` |

## 2. Independence of the oracle (the point of this card)

- Expected values come from `scripts/oracle_M25_M28.py`, which imports only `argparse`, `hashlib`, `json`, `os` and `decimal` (see the `import_lines` list inside `evidence/M27/oracle_selfcheck.json`). It never imports `model_registry` or `model_extensions`; `product_import_present` is `false`.
- The runner `scripts/run_card.py` calls exactly one product function, `calculate_registered_model(model_id, base_revenue, drivers, years)`, and reads expectations only from `evidence/M27/oracle.json`.
- Negative cases are built in memory from a fresh `deepcopy` each time - never round-tripped through a JSON parser - so a JSON-parser rejection cannot masquerade as a model rejection (N01a uses a real `bool`, N01b-d use real `float('nan'/'inf'/'-inf')`).
- `PASS_rejected` requires `isinstance(exc, ModelRegistryError)`. `ImportError`, `ModuleNotFoundError` and `FileNotFoundError` are recorded as **FAIL**, never as pass.
- The frozen oracle is reproducible: case E regenerated `input.json`, `cases.json` and `oracle.json` byte-for-byte from the generator alone.

## 3. Results in detail

- Registry formula observed from the isolated copy: `revenue = average_commissioned_mw * period_hours * pre_curtailment_capacity_factor * (1-curtailment_rate) * (contracted_share*contract_price_per_mwh + (1-contracted_share)*merchant_price_per_mwh) + other_revenue`
- Registry required: `['average_commissioned_mw', 'period_hours', 'pre_curtailment_capacity_factor', 'curtailment_rate', 'contracted_share', 'contract_price_per_mwh', 'merchant_price_per_mwh']`; optional: `['other_revenue']`; defaults: `{}`; driver_bounds: `{'contract_price_per_mwh': [None, None], 'merchant_price_per_mwh': [None, None], 'other_revenue': [None, None]}`
- Rejections and their messages:
- `NEG-CARD`: ModelRegistryError - period_hours must be positive: FY2027
- `N01a`: ModelRegistryError - renewable_generation.average_commissioned_mw.FY2027 must be numeric
- `N01b`: ModelRegistryError - renewable_generation.average_commissioned_mw.FY2027 must be finite
- `N01c`: ModelRegistryError - renewable_generation.average_commissioned_mw.FY2027 must be finite
- `N01d`: ModelRegistryError - renewable_generation.average_commissioned_mw.FY2027 must be finite
- `N02`: ModelRegistryError - driver renewable_generation.average_commissioned_mw must contain one value per forecast year
- `N03`: ModelRegistryError - missing drivers for renewable_generation: average_commissioned_mw
- `N04`: ModelRegistryError - unsupported drivers for renewable_generation: unknown_driver
- `N05a`: ModelRegistryError - renewable_generation.years must contain fiscal years
- `N05b`: ModelRegistryError - renewable_generation.years must contain fiscal years
- `CONT-BREAK`: ModelRegistryError - renewable_generation.years must be consecutive and increasing

## 4. Observations (NOT pass/fail, recorded because they are design-relevant)

- `OBS-BASE-IGNORED`: raised=None actual=[264000.0] matches_compared=True expect_equal=None - rowwise calculator discards base_revenue; design observation only, not a pass condition
- `OBS-NEG-PRICE`: raised=None actual=[88800.0] matches_compared=None expect_equal=None - card_M27.md L54 says a negative power price may be entered; the registry declares merchant_price_per_mwh = (None, None). The probe records whether the blended price path accepts it, with NO expectation and NO verdict asserted on the price.

## 5. Judgement calls the reviewer should attack first

1. **The oracle history, and where the earlier narrative was wrong.** The v1 generation had a defect, the first product run exposed it, and the generator was re-run before the definitive run. THREE corrections to the earlier write-up are recorded rather than glossed over: (a) the claim 'the correction was applied BEFORE `oracle.md` was written' is **not supported by mtime** and is withdrawn - the final generator's mtime is later than all four `oracle.md` files and later than the first product run; what IS supported is that no GATING expectation was ever rewritten and that only M25's non-gating defaults block changed; (b) the claim that the M27 crash meant 'no `oracle.json` was produced at all' is **wrong** - a complete valid v1 `oracle.json` exists and is byte-identical to the frozen one; (c) the v1 generator SOURCE and the M27 traceback were **never persisted**, so that accident is not reproducible and is recorded as a provenance gap. Also note the r2 re-freeze: the M26/M27/M28 NEG-CARD patch was corrected (review finding P2-1) and `cases.json` re-frozen before the definitive run. If the owner insists on the stricter rule '`oracle.json` must predate ANY product run', this attempt does not satisfy it and the honest answer is `oracle_json_precedes_the_first_ever_run = false`.
2. **NEG-CARD's rejection mechanism is now declared AND enforced.** For M26/M27/M28 the r1 patch used `kind=set_driver` with a `{"__float__": X}` envelope, so the driver was assigned a dict and the generic per-year length guard refused the case before the card-specific guard ran - the r1 coverage claim was unsupported. The patch is now a one-element list, and `run_card.py` verifies the declared mechanism message as a GATING condition (`neg_card_mechanism_check`). M25 never had the defect.
3. **Silent zero-fill.** `scripts/model_registry.py:335` turns an omitted optional driver without an explicit default into `0.0`; for this card that asserts "other_revenue = 0" with no disclosure saying so (OQ-M25M28-01, 24 models of the 31-model registry are affected; the reviewer recorded 31 optional driver SLOTS). No product change was made.
4. **Disclosure adaptation is 0/N.** No real company disclosure was adapted in this attempt, so no historical reconciliation exists; a mapping probe would have to invent the series.
5. **Isolated-checkout provenance.** I-00-B binds the isolation *plan* and the two-stage command rule but does not materialise a checkout tree; this attempt materialises its own read-only snapshot (`iso/checkout_scripts`, hashes equal to production). If the intended binding is a checkout materialised by I-00-B, that is a scope deviation to record - the code under test is byte-identical either way.
6. **`defaults` case for M25/M26 is an all-zero identity input, not an omission case.** With `optional = ()` there is nothing to omit; the case only shows that the rowwise calculator starts from zero. It is marked not gating.

## 6. What this card does NOT claim

- It does **not** claim the model is accurate, nor that one company's mapping generalises.
- It does **not** claim `disclosure_adaptation`; D needs a signed industry/accounting review plus a production forecast-entry-point mapping reviewed independently.
- It does **not** rewrite the formula. With no independent counter-example and no adjudicated specification, the existing implementation is retained.
- It does **not** treat the two-year continuity example as a scenario set or as accuracy evidence.

## 7. Known uncovered surfaces (offered to the reviewer as reserve cases)

- R6: no negative case exercises a ratio driver outside [0,1] (NEG-CARD is refused by the period_hours positivity check)
- OBS-NEG-PRICE deliberately asserts NO verdict (a legitimate negative price being refused would be a failure in the OPPOSITE direction and it is entangled with the non-negative-revenue rule)

## 8. Reviewer checklist (suggested)

1. Re-run `scripts/oracle_M25_M28.py --card M27 --out-root <scratch>` in a scratch tree and diff the generated artefacts against the frozen ones (case E already did this; repeating it independently is the point).
2. Re-run `scripts/run_card.py` against `iso/checkout_scripts` and confirm `[264000.0]` / `[264000.0, 564100.2]` / `[262800.0]` with 11/11 negatives rejected.
3. Confirm the isolated copy hashes still equal production (`evidence/M27/source_manifest.json`).
4. Confirm `oracle.md` was not edited after the definitive run (compare `sha256` with `source_manifest.oracle_document.sha256_before_the_definitive_product_run`); the r2 revision section at the end of `oracle.md` is an APPEND made after that run and is declared as such.
5. Confirm the r2 re-freeze only changed `cases.json` for M26/M27/M28 (the NEG-CARD patch), compare `evidence/%s/revision_r2.json` `p2_1_cases_json_refreeze.cases_json_sha256`, and confirm no gating expectation moved.
6. Pick a case the implementer did not use (section 7) and freeze its expectation BEFORE running.
7. Adjudicate the DEC items in `evidence/M27/accounting_decision.md` and the OQ items in `evidence/M27/oq_rulings.json`.

---

## 独立复核 r2（定点再复核，reviewer 署名：独立会话，非实现者）

> 转录说明（实现者）：本节由 reviewer 的报告 `%TEMP%\m25m28-review-20260920-035254\REPORT-r2.md`
> 第 8.1 节原文转录，`<>` 占位符按第 8.2 节逐卡填入。**只追加**：追加前的 `review.md`
> sha256 = `03ce281b293a37d2f81dd3313e2c273d0493591bbf6b54eb4a5c2e8eb92214b3`（`10500` B），追加后新文件以该旧文件字节为前缀（脚本实测
> `new_bytes.startswith(old_bytes)`，记录见 `evidence/M27/append_record_r3.json`）。
> 本节的裁决由独立 reviewer 作出，**不是实现者的签名**。

**verdict: accepted_scoped —— 仅 `formula`。**
`disclosure_adaptation = unmapped`、`accuracy = unproven` 维持；本裁决不涉及 D/E/F。

### 复核范围与方法（可复现）
- 解释器：本 attempt `iso/venv/Scripts/python.exe`，`-B -X utf8`；只读生产与冻结证据，reviewer 只写 `%TEMP%\m25m28-review-20260920-035254\`。
- **r1 冻结内容的不可变基线**：commit `ddc81ab6`（及 `e954449`）的 blob 经 CRLF 还原后，与本 reviewer 在 r1 记录的四件套 sha256 逐项相等（16/16），故以该提交为 r1 基准做逐字段 diff。
- 独立重跑：reviewer 用同一 argv 重跑 `scripts/run_card.py`，`rc=0`，且新生成的 `run_result.json` 与冻结件**逐字节相同**（sha256 见下）。
- 期望值复算：reviewer 以自造输入 + `Fraction` 精确算术独立复算正例/连续性/defaults（未采信本卡 oracle.json 的推导过程）。

### 对上一轮发现的处置核验
- **P2-1（NEG-CARD 覆盖声明）已闭合**。r1→r2 的 `cases.json` **唯一** per-case 改动是 `NEG-CARD.value` 由 `{"__float__": X}` 改为单元素列表 `[X]`（`expected`、id 清单与其他 10 例 value 全部不变），并新增 `case_contract`。
  - 实测拒绝机制（reviewer 复跑）：`period_hours must be positive: FY2027`，即本卡专属守卫**确实**被求值；第 8 节 R1 的"是（NEG-CARD）"现在成立。
  - `negative_summary = {total: 11, passed: 11, failed: []}`；正例 `[264000.0]`、连续性 `[264000.0, 564100.2]`、defaults `[262800.0]` 全部与 r1 一致（本卡 defaults 案例省略 `other_revenue`）。
- **P2-2（oracle 事故叙述）已按更正清单改写**：撤回"no oracle.json was produced at all"（v1 `oracle.json` 存在且与冻结件逐字节相同）；撤回"correction before oracle.md"（mtime 不支持），改为"闸门期望在首次产品运行前已定稿 / M25 的 non-gating defaults 块在首次运行之后更正 / 定版运行在冻结件写入之后"。reviewer 独立复核了首次运行 `run_result.json` 的期望值，支持上述口径。v1 生成器源码与 traceback **未留档**已如实登记为 provenance gap。
- **P3-1..P3-8** 已逐条处置；其中三处措辞与一处残留见下"遗留观察"。

### 遗留观察（P3，不影响本次签收；只许追加修正）
1. 新闸门 rc 归类：`expected`/`expected_count`/`expected_ids`/缺 `case_contract` → **rc=1**；**机制子串不匹配或声明无反引号片段 → rc=3**。本卡 r2 修订节写的"一律 rc=1"与此不符，应改为两类分别表述（reviewer 实测：G5/G6/G7/G8 均 rc=3）。
2. `evidence/M27/line_ending_and_blob_hashes.json` 的 25 条中有 3 条（`evidence_hashes.json`、该文件自身、`revision_r2.json`）为自指条目，写入后即不可复现（reviewer 复算 22/25 一致）；冻结四件套全部可复现。
3. `revision_r2.json.p3_7_precorrection_is_not_uniform` 的 `identical:false` 是 CRLF-vs-LF 的裸字节比较，与同段"byte-identical"叙述冲突；LF 归一后确为逐字节相同（reviewer 用 git 基线与 CRLF 还原两法证明）。
4. LF 修复未覆盖 `recovery/**`（仍有 72 个 CRLF JSON：selfcheck scratch、`rerun_check.json` 等）；`recovery/precorrection/*` 保留 CRLF 属**正确**的 v1 冻结字节。

### 签收范围与失效条件
- 签收值：`formula`（A–C）。基于以下复算值：正例 `[264000.0]`、连续性 `[264000.0, 564100.2]`、defaults `[262800.0]`（non-gating）、负例 11/11 全部 `ModelRegistryError`。
- 冻结件哈希（reviewer 复核时点，LF 版本）：
  `input.json=44f217af85a25c688aad12940abc38d175eedbb505cea0612df6f38956e23223`、`oracle.json=00cbaab6992ad1da5e572052fbb78db1515707406bfec57d41d7c40e31fd531e`、`cases.json=482a4f160d384e16887bf7ff3fc1180eb1ae8004c445d24e1b105cd926dec4de`、`run_result.json=f7287494fd2830277d3784fce693b6e7268b02da5c700dc3721ef8cbd6fe3a2c`。
- **失效条件**：上述任一冻结件、`iso/checkout_scripts/{model_registry,model_extensions}.py`（须恒等于生产 `9ec65295…/9939480b…`）、或 `scripts/run_card.py`（`eab01162…`）发生任何变化，本裁决自动失效并须重新复核。
- 本裁决**不**覆盖：D 披露映射（`unmapped`）、E 历史对账、F 精度/回测（`unproven`），也不得据此外推为行业级准确度。

### 实现者补充（非裁决的一部分；只作对本次转录与 P3 更正的定位说明）
- **阅读顺序提示（只追加，不撤回任何既有行）**：本文件上方的正文写于 r1 时点，其中
  "PENDING independent review" 横幅与第 1 节表格里的 `D mapping = NOT delivered`、`E probe =
  not_applicable_with_reason` 等行，都是**该时点**的记录，按 append-only 规则**保持原样、不修改**。
  本文件末尾的"独立复核 r2"节及其 `verdict: accepted_scoped —— 仅 formula` 是**在它们之后**出现的
  更晚事实；两者并存不是矛盾，而是时间顺序。任何引用本文件的状态时，须引用**最后**那一节。
  （本卡 `formula` 仍记为 `review_pending`：实现者不自签，与裁决并存不冲突。）
- 本次追加不含任何期望值、阈值或判定条件的改动；四卡冻结件（`input.json`/`oracle.json`/
  `cases.json`/`run_result.json`）**未触碰**，哈希见 `evidence/M27/append_record_r3.json` 的
  `frozen_four_piece_unchanged_after_append`。
- 对遗留观察 1–4 的**只追加更正**落在 `evidence/M27/revision_r3.json`（含 P3-A 两类 rc 归类、
  P3-B 自指条目与 `files_with_crlf` 口径、P3-C 字段命名更正、P3-D LF 覆盖边界），并在
  `evidence/M27/revision_r3.json` 中给出改前→改后对照与仍存缺口。
- **生产漂移窗口（追加事实）**：本文件组装期间，生产 `scripts/model_registry.py` 曾在
  `2026-09-20 04:35:31–04:40:53` 窗口内**不是**锚定态（编排层 git 门的 `git checkout -- .`
  返回 255 导致补丁未回放），随后由 owner 用同一补丁 `--exclude=.planning/*` 恢复；
  恢复后该文件 sha256 回到锚定值 `9ec65295…`，四卡 `iso/checkout_scripts/*` 与生产重新逐字节一致。
  窗口内的"生产哈希未变 = false"是**正确告警**，未被用来改动任何期望或冻结件。详见
  `recovery/production_drift_and_restoration_r3.json` 与
  `execution_runs/_isolation_incidents/20260920-model-registry-extension-rollback/INCIDENT.md`。
- 四卡通用：`status` 保持 `review_pending`（本文件不构成实现者签名）；
  `disclosure_adaptation = unmapped`、`accuracy = unproven` 不外推。
