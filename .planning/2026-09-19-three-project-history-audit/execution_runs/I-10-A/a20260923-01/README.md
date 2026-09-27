# I-10-A · a20260923-01 — 先行完成实际采用模型的专业披露适配

Live working document (防灾令: deliverable-first, incremental). Status: implementing →
target `review_pending` (independent review is a separate step; the implementer never signs acceptance).

- Card: `execution_v2/card_I-10-A.md` (sha256 `FE169C83…3B947`, 31 lines) — the sole spec source.
- Protocol: START_HERE 固定九步执行法 + review_and_handoff.md 独立验收 + common_research_cards.md.
- Attempt root: `execution_runs/I-10-A/a20260923-01/` (all `evidence/I-10-A/…` paths are relative to here).
- Interpreter: attempt-local iso venv cloned from I-00-A template (global Miniconda FORBIDDEN per I-00-B).
- Product code runs only against the isolated copy `iso/rf/`; production trees are read-only anchors.
- Production writes = 0 · company-wiki writes = 0 · git writes = 0 · network = none.

## Deliverables (card line 31, relative to attempt root)

1. `evidence/I-10-A/selected_model_manifest.json`
2. `evidence/I-10-A/disclosure_mapping.json`
3. `evidence/I-10-A/accounting_decision.md`
4. `evidence/I-10-A/historical_reconciliation.json`
5. `evidence/I-10-A/historical_mapping_probe.json`
6. `evidence/I-10-A/model_DE_evidence_manifest.json`
7. `evidence/I-10-A/disclosure_qualification.json`
8. `evidence/I-10-A/independent_adaptation_review.md`

Plus protocol-minimum: `binding.json`, `oracle.md` (frozen before first judged run),
`commands.json`, `decision.md`, `changes.diff`, `handoff.json`, `before/`, `after/`, `recovery/`,
per-case raw under `evidence/I-10-A/`. `review.md` is the independent reviewer's carrier — NOT
written by this implementer.

## Inherited carries (from I-07-B a20260923-01 accepted_scoped) — MUST travel downstream

- Three verbatim declarations (see handoff.carries / decision.md §0).
- `overall_three_market_pass = false` (overall NEGATIVE).
- Measured fact: zero RevenueSourceRecord produced in any market (stricter than declaration 1).
- Findings F1/F2/F3 carried (routes recorded), F4 L-cells blocked ×3 stands as measured.

## Progress log

- [x] Step 1 领取 — card + shared rules + dependency reads pinned in binding.json.
- [x] Step 2 绑定 — binding.json + commands.json written before any judged run.
- [x] Step 3 读证据 — three sources fully readable (incl. HK glyph-decode 0-unmapped); 量价/政策/分部注 pinned by line+page.
- [x] Step 4 冻结预期 — oracle.md (sha 5CDD7331…) + oracle_expected.json frozen before first judged run (run_log ORACLE-FREEZE record).
- [x] Step 5 修改前检查 — probe red_conv arms 4/4 rejected (rc2); validator RED fixtures 5/5 families detected (rc2).
- [x] Step 6 最小修改 — 8 card-named evidence files + forecast_integration.json (isolation surface only).
- [x] Step 7 修改后检查 — probe normal 4/4 rc0 == frozen hand values (counts 24/9/3/3); mut_swap_ids 4/4 killed; mut_swap = equivalent mutant (F-I10A-3); mut_omit_optional = product defect evidence (F-I10A-2); validator GREEN-4 clean + MUT3 5/5 killed; red→green chain preserved.
- [x] Step 8 交审 — decision.md + changes.diff (anchors_identical=true) + handoff.json + recovery/README.md + before/after hash table.
- [x] Step 9 接续 — status `review_pending`; first unfinished action = independent review (see handoff.next_action).
