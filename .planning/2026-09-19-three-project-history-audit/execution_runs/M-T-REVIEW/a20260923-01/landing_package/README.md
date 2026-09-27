# landing_package/ — 给父 landing 批次的安装载体（M-T-REVIEW 不代装、不写旧 attempt）

两个落槽（D9 关闭判据第二项）+ 一个附带件：

1. **`review_flips_M01-M20.md`** —— 20 个 review.md 追加式翻转块（status_authority 形态）。
   覆盖：M05–M07/M17–M20 的 r2 态验收补足、M09–M12 的卡内裁决区补录（`in_card_transcription_owed` 清账）、
   全 20 卡的独立裁定落卡。安装 = **追加**到各卡 `review.md` 末尾（T1-12 ① 形态，不改既有字节），
   并按块内指示对齐 `handoff.json.reviewer_status`（只动该键）。
2. **`sampled_and_namecheck_M21-M31.md`** —— 抽验/点名表（M21–M31 终裁有效性抽查记录）。
   安装 = 作为编排层登记件归档（可入 REMEDIATION_REGISTER / findings 引用），**不**改 M21–M31 旧 attempt
   （其终裁本已落定，无需翻转）。
3. **`t1_review_flips.md`**（附带）—— T1-\* 各卡的独立验收裁定块。T1 attempt 无 review.md，
   块供父按需落 `review.md` 新建或编排层登记（含 T1-10 `changes_required` 的返修要求）。

安装规则（每块顶部重复声明）：

- **追加不改**：任何既有字节不动；安装后附前缀哈希证明（append-only proof）。
- **字段对齐**：`handoff.json.reviewer_status` 可按块内 `reviewer_status_note` 更新；`status` 仅在块内
  `status_authority.status` 与现值不一致时按其更新；其余键不动。
- **权威出处**：全部裁定载体 = 本 attempt 的 `reviews/*.md` + `acceptance_rulings.md`（块内引 sha256）。

（各文件的 sha256 见 `../evidence/self_manifest.json`，由 `scripts/finalize_self.ps1` 生成。）
