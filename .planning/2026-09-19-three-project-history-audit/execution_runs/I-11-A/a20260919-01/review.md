# I-11-A 实现者自检报告（**不是验收结论**）

card_id: I-11-A · attempt_id: a20260919-01 · 角色：实现者（弱模型）
**本文件不包含 verdict 字段，也不授予任何资格。** `accepted_scoped` / `changes_required` /
`blocked` / `not_applicable_with_reason` 只能由未参与本卡的独立 reviewer 在独立审查后写入
（`review_and_handoff.md` 第 9 条；START_HERE 第 26 行"实现者不能自签 accepted"）。
为本 attempt 保留的 reviewer 结论位置见本文件 §5。

---

## 1. 一句话结论

本 attempt 把 8 条定性判断冻结为带来源、机制链、已注册 driver、时点、双计排除与可推翻条件的
命题，其中 6 条 `pending_professional_decision`、2 条 `unquantified`、**0 条 approved**；
14 个先冻结的反例全部按预期被拒；7 条算术恒等式用有理数精确复算差为 0；
生产三仓零改动。**本卡不产生任何参数幅度、不产生预测、不产生准确性证据。**

## 2. 自检数字（全部来自脚本输出，非手抄）

| 项目 | 值 | 来源 |
|---|---|---|
| 命题数 | 8 | `evidence/I-11-A/validation_report.json` → `counts.hypotheses` |
| `pending_professional_decision` / `unquantified` / `approved_frozen` | 6 / 2 / **0** | 同上 → `counts.states` |
| 来源类型 | company_disclosure 7；management_target 1 | 同上 → `counts.source_types` |
| independence_group | ZIJIN-AR2025 4；ZIJIN-MGMT-PLAN-2026 1；MSFT-10K-FY2026 3 | 同上 → `counts.independence_groups` |
| 参数（含附加） | 14 | 同上 → `counts.parameters` |
| 引用原值条目 | 46 | `evidence/I-11-A/source_map.json` → `counts.cited_values_total` |
| falsifier 阈值依据 | arithmetic_identity 4；professional_judgement_required 4 | `counts.threshold_bases` |
| `refuted_by` 条目 | 24 | `counts.refuted_by_total` |
| 反例套件 | 14 例 / 14 例按预期被拒 / 0 例误接受 | `counterexample_summary` |
| 正例校验 | pass（0 errors） | `positive_case.verdict` |
| 算术 oracle | 7/7 pass（差 0；A4 为符号检验） | `evidence/I-11-A/extract/arithmetic_oracle.json` |
| 不可读来源 | 1（HK-XIAOMI-AR2025） | `source_map.counts.sources_not_readable` |
| 交付文件数 | 见 `attempt_hashes.json` 的 `file_count`（不含 `iso/venv`） | `evidence/I-11-A/attempt_hashes.json` |
| 最终自检 | `complete_for_review`（在写入本文件与 handoff 之前运行；两者写入后重跑） | `evidence/I-11-A/final_selfcheck.json` |

## 3. 卡验收条件 → 证据对照（逐条）

卡正文验收："每命题有可追溯来源、机制、driver、时点、双计排除和明确 unquantified/approved 状态；
不要求全部强行量化。"

| 验收要素 | 本 attempt 的实现 | 可直接复核的证据 |
|---|---|---|
| 可追溯来源 | 每条命题 `source.doc_id` + 原始文件 sha256 + `page_index_basis` + `page_span` + `anchor_text` + `cited_value_key`；46 条引用原值逐条绑定原始串与页码/表号 | `hypotheses.json`、`source_map.json`、`extract/P1_zijin_pages.json`、`extract/P1_msft_tables.json` |
| 机制链 | 每条 4 环，末环为收入确认/期间归属；见 `mechanism_chain` | `hypotheses.json`；`mechanism_review.md` §2.3 |
| 落到模型 driver | 每条给出 `model_id` + `driver_name`，取值逐字来自 `model_cards.md` 的 31 个已注册模型；未注册名会被判 `E_UNKNOWN_MODEL`/`E_UNKNOWN_DRIVER` | `hypotheses.json`；`tools/validate_hypotheses.py` 的 `REGISTERED` 表 |
| 时点 | `published_at`/`available_at`/`as_of` 逐条填写；falsifier 带 `observation_date` | `hypotheses.json` |
| 双计排除 | 每条 `double_count_exclusion`；跨命题风险单列（命题 5） | `hypotheses.json`；`mechanism_review.md` §2.2 |
| 状态明确 | 五态状态机；本 attempt 无 approved（可执行检查 `E_STATE_APPROVED_BY_IMPLEMENTER`） | `validation_report.json` |
| 不强行量化 | 2 条 unquantified；"品牌/竞争力"类判断一律不进入命题；4 个拒绝对量化的理由 | `mechanism_review.md` §4 |
| 计数有脚本 | 所有计数由 `build_hypotheses.py` / `validate_hypotheses.py` / `hash_attempt.py` 产出 | `source_map.counts`、`validation_report.counts`、`attempt_hashes.file_count` |
| oracle 先冻结 | `oracle.md` §0–§9 先写（含 14 个错误码与 O-1…O-17 期望），并如实披露两项先于冻结发生的观测 | `oracle.md` §0.1 |
| 停止条件 | S1–S5；实际触发并登记 1 次（HK 不可读 → `STOP_EVIDENCE`） | `oracle.md` §8；`source_map.not_readable_in_this_attempt` |

## 4. 我自己发现的缺陷与限制（reviewer 应优先看这些）

1. **转写错误（已修，已披露）**：命题 2 初稿把推导值写成 `… ÷ 885,141 = 124,242.28`，
   该数无法由任何被引用原始串复算（正确值 `109977556345/885141 ≈ 124,248.63`）。
   已改为精确有理数，并在 `mechanism_review.md` §6.5 与 `decision.md` DEC-10 如实登记。
   这是"必须能复算"规则真正起作用的一次，不是形式主义。
2. **我自己的定位错误（已修，已披露）**：`verify_arithmetic.py` 首轮把 FY2024 的分部数据与抵销数
   定位到第 327 页（实际 328 页），A2/A3 被自动判 `rejected`；修正页号后通过。
3. **oracle 内部不一致（未改正文）**：`oracle.md` O-6 用了 prior artifact 的页号而未先测定偏移，
   实测 offset = +1。已按 OPEN-8 登记，未回改 oracle 正文（oracle 只能以 R2 附录修订）。
4. **港股来源不可读**：HK-XIAOMI-AR2025 在本 attempt 的两条路径下都无法读出可引用原文
   （标准库路径 0 字符；`pdftotext` 输出乱码），判 `STOP_EVIDENCE`，**零**条港股命题。
5. **MSFT FY2027 分部口径不确定**：10-K 仍按 PBP/IC/MPC 编制（`Agents and Infra` 出现 0 次），
   as_of 之后的重分类 8-K 原文不在本地可核来源，故八线口径既未引用也未否定（OPEN-3）。
6. **取文器能力边界**：`tools/pdf_text.py` 不做表格结构还原，同排相邻字段会被拼接
   （例如 `109110.45`）。**禁止**用它做列对齐级引用；引用一律以字段级原始串为准。
7. **页面索引口径未规范化**：本 attempt 用 `pdf_leaf_1based` / `table_index_0based`，
   与 schema 层枚举的关系未定（OPEN-4）。
8. **占位阈值**：4 条 falsifier 阈值标 `professional_judgement_required`，**未审定**（OPEN-6）。

## 5. 交给独立 reviewer 的空位（实现者留白，禁止实现者填写）

```
reviewer_verdict:            <accepted_scoped | changes_required | blocked | not_applicable_with_reason>
reviewer_identity:           <未参与本卡的人/会话>
reviewer_recomputed_oracle:  <至少一条卡片专属 oracle 的独立复算记录>
reviewer_reserved_case:      <审查前预先保留、实现者未用于编写修复的变化案例>
qualifications_granted:      <仅限本卡明示资格>
qualifications_not_granted:  <公式/披露适配/准确性三栏的边界>
```

## 6. 本卡不授予的资格（明确声明）

- **formula**：本卡不运行任何模型，`not_applicable_here`；
- **disclosure_adaptation**：`not_granted`（属 I-10-A；本卡只做"原文 → 原始串/页码/单位"的取证）；
- **accuracy**：`not_granted`（属 I-12）；
- **发布/部署/自然观察**：不适用（本卡无产品改动）；
- **I-11-B / I-11-C / I-07-E 的解锁**：**未解锁**。本 attempt 产出 0 条 `approved_frozen`，
  且 OPEN-2/3/5/6 明确阻塞 I-11-B 的参数校准。

## 7. 生产仓库零改动的证明

- `evidence/I-11-A/state_before.json` 与 `state_after.json`：三仓 HEAD、porcelain 条目、
  关键文件 sha256 完全一致（`final_selfcheck.json` 的 `production_state_unchanged` 检查项）；
- revenue-forecast porcelain 中与本卡相关的条目只有一条
  `?? .planning/.../execution_runs/I-11-A/`（本 attempt 自身，未跟踪），
  其余 125 条为**本次工作之前已存在**的用户改动与其他卡的 attempt（before/after 一致）；
- 未执行 `git add` / `commit` / `restore` / `stash`；
- PLAN/reviews 未被写入：`state_before/after` 记录其 mtime；
  另经独立枚举确认 reviews 下 285 个文件中**没有**任何文件的最后写入时间晚于
  本 attempt 开始工作的时间（详见 handoff `current_source_hashes.plan_reviews_note`）。
  **注意一个与用户口径不符的既有事实**：`reviews` 目录的 LastWriteTime 实测为
  `2026-09-19 09:14:20`，而不是任务说明里的 `10:05`；本 attempt 无法改变它（未写入），
  该差异登记为 OPEN-10 供 owner 核对。
