# M22 · milestone_royalty · 里程碑与销售分成 - implementer review record

Card M22 (`milestone_royalty`), Parent I-10. Attempt `execution_runs/M22/a20260919-01`.

> ## PENDING independent review
> **Nothing in this file is an acceptance.** The implementer is not the reviewer. `formula` is
> recorded as `review_pending`; `disclosure_adaptation` stays `unmapped`; `accuracy` stays
> `unproven`. A separate session must read the artefacts below and issue its own verdict
> (`accepted_scoped` / `changes_required` / `blocked` / `not_applicable_with_reason`).

## 1. What was done

| Step | Result | Evidence |
|---|---|---|
| A binding | production code copied read-only into an attempt-local snapshot; hashes recorded and equal | `binding.json`, `evidence/M22/source_manifest.json` |
| B positive | actual `[55.0]` vs independent oracle `[55.0]`, within `1e-9*max(1,|e|)` | `evidence/M22/formula_result.json` |
| continuity positive | actual `[55.0, 4.0]` vs oracle `[55.0, 4.0]` | `evidence/M22/negative_results.json` |
| defaults case | actual `[40.0]` vs oracle `[40.0]` (not gating) | `evidence/M22/negative_results.json` |
| C negatives | 11/11 rejected with `ModelRegistryError` | `evidence/M22/negative_results.json` |
| D mapping | **NOT DONE** - needs a signed industry/accounting review | `evidence/M22/qualification.json` |
| E probe | **NOT DONE** - belongs to I-10-A | `evidence/M22/qualification.json` |
| F accuracy | **NOT DONE** - needs the I-12 frozen design | `evidence/M22/qualification.json` |

Raw exit code of the product run: **0** (0=pass / 2=no-verdict / 3=negative not rejected as
expected / 1=harness error). stderr is 0 bytes.

## 2. Independence of the oracle (the point of this card)

- Expected values come from `scripts/oracle_M22.py`, which imports only `argparse`,
  `hashlib`, `json`, `os`, `sys` and `decimal` - see the `import_lines` list inside
  `evidence/M22/oracle_selfcheck.json`; `product_import_present` is `false`.
- The oracle document `oracle.md` (sections 0-11) was written **before** any product run. Its
  frozen body is 10026 bytes, sha256
  `88de6bf9b8012bac6c6e05ee836977e9b54cc08c75287af66d7e55e92275b0da`; the exact reconstruction identity
  `oracle.md == frozen_body + b"\n---\n\n" + run_section` is verified by
  `scripts/verify_prefix_chain.py` in all four attempts of this batch.
- `evidence/M22/oracle.json` is **byte-identical when regenerated** (re-run performed).
- The runner `scripts/run_card.py` calls exactly one product function,
  `calculate_registered_model(model_id, base_revenue, drivers, years)`, and reads expectations
  only from `evidence/M22/oracle.json`.
- Negative cases are built in memory from a fresh `deepcopy` each time - never round-tripped
  through a JSON parser - so a JSON-parser rejection cannot masquerade as a model rejection
  (N01a uses a real `bool`, N01b-d use real `float('nan'/'inf'/'-inf')`).
- `PASS_rejected` requires `isinstance(exc, ModelRegistryError)`. `ImportError`,
  `ModuleNotFoundError` and `FileNotFoundError` are recorded as **FAIL**, never as pass.
- The same `run_card.py` (sha256 `a5ee7599c37e1e8ed5a2f3e212df22cae936fd1c1da29b9db0d44232f406b1a3`) was used for
  M05-M08 and for all four attempts of this batch; there is no card-specific runner to drift.

## 3. Results in detail

- Registry formula observed from the isolated copy: `revenue = eligible_sales * royalty_rate + milestone_revenue + service_revenue`
- Registry required: `['eligible_sales', 'royalty_rate']`; optional: `['milestone_revenue', 'service_revenue']`; defaults: `{}`
- Rejections and their messages:
- `NEG-CARD`: ModelRegistryError - `driver milestone_royalty.royalty_rate must be between 0.0 and 1.0: FY2027`
- `N01a`: ModelRegistryError - `milestone_royalty.eligible_sales.FY2027 must be numeric`
- `N01b`: ModelRegistryError - `milestone_royalty.eligible_sales.FY2027 must be finite`
- `N01c`: ModelRegistryError - `milestone_royalty.eligible_sales.FY2027 must be finite`
- `N01d`: ModelRegistryError - `milestone_royalty.eligible_sales.FY2027 must be finite`
- `N02`: ModelRegistryError - `driver milestone_royalty.eligible_sales must contain one value per forecast year`
- `N03`: ModelRegistryError - `missing drivers for milestone_royalty: eligible_sales`
- `N04`: ModelRegistryError - `unsupported drivers for milestone_royalty: unknown_driver`
- `N05a`: ModelRegistryError - `milestone_royalty.years must contain fiscal years`
- `N05b`: ModelRegistryError - `milestone_royalty.years must contain fiscal years`
- `CONT-BREAK`: ModelRegistryError - `milestone_royalty.years must be consecutive and increasing`

## 4. Observations (NOT pass/fail, recorded because they are design-relevant)

- `OBS-BASE-IGNORED`: raised=None actual=[55.0]
- `OBS-DEFAULT-EQUIV`: raised=None actual=[40.0]

## 5. Judgement calls the reviewer should attack first

1. NEG-CARD is the card's literal negative, but it is also the case that most obviously tests a CONTRACT question rather than an economic one: a tiered royalty agreement can have an effective rate above 1.0 of a narrow base. The registry's [0,1] ratio domain answers it, and the card's own text does not state that 1.01 is impossible; a reviewer should decide whether that is the intended contract.
2. `milestone_revenue` and `service_revenue` are optional with a DECLARED default of 0, so the defaults case is a genuine default test; `millestone`/`service` amounts are signed (any real number), so a negative milestone adjustment is accepted by the contract - this card does not test that.
3. the second year of the continuity positive has eligible_sales = 0 and a milestone only; this is the deliberate 'no sales, milestone only' shape and asserts nothing about probability-weighted contingent payments (which the card refuses).

## 6. What this card does NOT claim

- It does **not** claim the model is accurate, nor that one company's mapping generalises.
- It does **not** claim `disclosure_adaptation`; D needs a signed industry/accounting review
  plus a production forecast-entry-point mapping reviewed independently.
- It does **not** rewrite the formula. With no independent counter-example and no adjudicated
  specification, the existing implementation is retained.
- It does **not** claim that a formula pass on this card implies anything about the other 30
  models: the parent card explicitly forbids extrapolating accuracy from formula passes.

## 7. Reviewer checklist (suggested)

1. Re-run `scripts/oracle_M22.py --card M22 --out-root <scratch>` and diff the generated
   `oracle.json` against the frozen one; then re-run `scripts/run_card.py` against
   `iso/checkout_scripts` and diff `run_result.json`.
2. Re-run `scripts/verify_prefix_chain.py <plan>` to confirm the oracle.md frozen-body chain.
3. Confirm the isolated copy hashes still equal production
   (`evidence/M22/source_manifest.json`).
4. Pick a case the implementer did not use and freeze its expectation BEFORE running it.
5. Re-run `scripts/enumerate_oq_rulings.py` and compare the counts with
   `evidence/M22/oq_rulings_enumeration.json`.
6. Adjudicate the OQ items in `decision.md` and `handoff.json`.

## 8. Exit-code mutation self-check (red then green)

Scratch tree: `recovery/selfcheck/` (the frozen evidence is never mutated).

| probe | raw rc | expected rc |
|---|---|---|
| D_pristine_uncorrupted | 0 | 0 |
| A_corrupted_positive_expectation | 3 | 3 |
| B_corrupted_negative_assertion | 3 | 3 |
| C_corrupted_positive_input | 2 | 2 |
| F_corrupted_expected_type | 3 | 3 |
| G_corrupted_message_requirement | 3 | 3 |
| H_message_requirement_points_at_another_guard | 3 | 3 |
| R4_required_message_ids_gate_removed | 3 | 3 |
| R5_required_message_requirement_emptied | 3 | 3 |
| D_restored_uncorrupted | 0 | 0 |

`frozen_hashes_unchanged` = `True`. Full record:
`recovery/selfcheck/selfcheck_result.json`.

<!-- BEGIN independent-review verdict (round 2, transcribed verbatim) -->

> **独立复核裁决（revision r2 后）：`accepted_scoped`（仅 formula）。由 `changes_required` 转正。**
> 上轮唯一的阻塞项（无判定性值域负例）已关闭，并经我独立验证：`cases.json` 的 NEG-CARD 现为 `royalty_rate = [1.01]`（= 卡片 `card_M22.md:38` 原文的"替换整个 driver"），我自行构造并调用隔离快照得到 **`driver milestone_royalty.royalty_rate must be between 0.0 and 1.0: FY2027`**——**值域守卫**，不再是长度守卫。
> 通过判据已冻结进 `cases.json`（`expect_message_contains = "must be between 0.0 and 1.0: FY2027"`），且 runner 现按**消息子串**判定。我做了三个独立变异探针：把 `expected` 改成 `ValueError` → rc=3；把消息要求改成不可能子串 → rc=3；把消息要求指向长度守卫措辞 `must contain one value per forecast year` → rc=3。**该控制有区分度，不是"非空即过"。**
> 公式本身无回归：`rc=0`、`stderr` 0 字节、正例 `[55.0]`、连续性 `[55.0, 4.0]`、defaults `[40.0]`、11/11 负例；我自造输入另证 `royalty` 与 `milestone` 可分离（`1000×0.05+0+0=50.0`；`0×0.5+77+11=88.0`）。
> 正文改动经我逐节复算：只改 NEG-CARD 行 1 行（+新增第 12 节），`## 2./3./4./8./10.` 与正例/连续性/defaults 的期望与容差、每个既有负例的 `expected` 值**逐字节未变**；前像 = 上轮冻结体（sha256 `d83ce296…`），变更行数 6 = 我独立重算值，白名单外 0 行。
> 签收边界：**仅 `formula`**。`disclosure_adaptation` 保持 `unmapped`，`accuracy` 保持 `unproven`。
> 遗留（时间性，不阻塞）：消息要求目前可被"删除字段"绕过（我实测删掉后 rc 回到 0）；建议加 `required_message_ids` 使闸门闭合。第 12 节关于本卡的 `not_applicable_with_reason` 判断正确。

<!-- END independent-review verdict (round 2) -->

<!-- BEGIN independent-review verdict (round 3, transcribed verbatim) -->

> **独立复核裁决（round 3 终裁）：`accepted_scoped`（仅 formula）。由 `changes_required` 转正并终裁。**
>
> 上轮唯一阻塞项已关闭并经我独立验证：NEG-CARD 现为 `royalty_rate = [1.01]`（= 卡片 `card_M22.md:38` 原文），实测 `driver milestone_royalty.royalty_rate must be between 0.0 and 1.0: FY2027`（**值域守卫**，非长度守卫）；通过判据已冻结为 `expect_message_contains`，runner 按消息子串判定。我做的三个变异探针（`expected`→`ValueError`、消息要求→不可能子串、消息要求→长度守卫措辞）全部 rc=3，证明该控制有区分度。
>
> 追加闸门已闭合：`required_message_ids = ["NEG-CARD"]` 冻结进 `cases.json`；我实测"保留闸门但删掉 `expect_message_contains`"→rc=3、"把成员要求置空"→rc=3、"连闸门字段一起删"→rc=3。11 个用例输入互不相同（我按 `cases.json` 重建并做 canonical sha256，无重复）。
>
> `oracle.md` 0–12 节自 round 2 起逐字节未改（`88de6bf9…`/10026 B）；`final_verify.txt` False 计数 0；`verify_prefix_chain.py` ALL-OK。
>
> 签收边界：**仅 `formula`**；`disclosure_adaptation` 保持 `unmapped`，`accuracy` 保持 `unproven`。

<!-- END independent-review verdict (round 3) -->
