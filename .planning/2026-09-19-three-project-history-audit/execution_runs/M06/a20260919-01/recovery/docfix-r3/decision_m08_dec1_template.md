## DEC-M08-1 · r3 correction (this section supersedes the r1 wording above; the r1 text is preserved verbatim above it)

r1 的 DEC-M08-1 只写到「owner 需裁定哪个读法权威，若是 C 则更正 card_M08.md L42 与索引」。该措辞不足以构成可执行的处置，也**没有绑定「禁止换例子」的约束**。现更正为：**唯一出路是 `handoff.json` → `owner_action_required`（id `F-M08-02-remediation`）记录的三步**，此处逐条复述，使本决策记录自洽、不能被读成可自由选择：

1. **owner 或 I-10 专业人**：裁定读法 **C**（`+ contract_changes`，按带符号金额相加）为权威。依据为四处互证：`docs/buy_side_model_audit_2026-09-18.md:42`；`reviews/revenue/model_ledger.jsonl` 的 `RF-MODEL-project_backlog.original_claim`（第 8 行）；`scripts/model_registry.py:228`（及 `_project_backlog` 的 fsum，第 102 行）；`card_M08.md` L8（「变更与重估为带符号金额」）。两个符号探针已把实现唯一识别为 C（`contract_changes=+10` → 85.0；`contract_changes=-20` → 55.0）。
2. **索引 owner**：更正 `card_M08.md` L42 与索引副本 `model_cards.md`（M08 段）、`dispatch.md`，使印出的算例与权威读法一致。**约束：数值算例与冻结期望 `[50]` 不得改动** —— 读法 C 在同一合成输入上同样得 50，因此只更正**符号呈现**，不是改答案。**明确禁止**为了「让方便的那个读法过关」而重新挑选算例（`handoff.json.owner_action_required.steps[2].explicitly_forbidden` = `re-picking the example so that only the convenient reading passes`）。
3. **独立 reviewer**：索引更正完成后，在**同一 `code_root`**（`9ec65295…`）上复跑冻结卡并留档；此后该卡方可按 `accepted_scoped`（仅 `formula` 资格）签收。

**实施者与 reviewer 都不得执行第 1、2 步，也不得自行改卡**；本处置不允许任何产品改动。第 2 步完成前 `formula` 保持 **blocked**，且不授予 disclosure_adaptation 或 accuracy 资格。

被否决的替代方案（r1 已列，此处维持）：(1) 改 oracle 期望去迁就实现——那是拿结果反推期望；(2) 改 `model_registry.py`——没有独立反例、没有已裁定的规格，且会破坏上游公式串与既有测试。

### DEC-M08-1 不是「已决」

`decision.md` 是决策记录，不是裁定本身。**本节不构成 owner 裁定**：读法 C 的权威性仍待 owner/I-10 拍板，本卡维持 blocked。
