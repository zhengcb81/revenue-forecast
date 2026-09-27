# Guard-face addendum — corrections note + merge-batch pin

- Card / attempt: **RF-STEP9-TRIAGE / a20260923-01**, face = **#8 守卫收窄 (guard-narrowing)**.
- Carrier: `reviewer_report_guard8.md` sha256 `86a5e0f71fc4f05c429fb330aeaf4c25eeba0ca76b7240c465574f73b5dde5f7` (14947 B, 176 lines), pinned by `reviewer_report_guard8.sha256` — verdict **ACCEPT-ADDENDUM**, **0 changes_required-for-face** (0 blocking).
- Base card (DO-NOT-TOUCH): `handoff.json` = `3942a3384d5801d8b5078a36f2d944199d68cfdc794921a6983351284a715611` (24218 B, `accepted_scoped`) — byte-frozen; re-asserted untouched by this pass before and after its writes.
- Written by the addendum carrier-transcription pass (delegated subagent of `session-bfecd191-fbc3-4a66-8ed1-6562479bf102`), 2026-09-24. **No git; no network; 0 production writes.**

## F-1 — stale register citation: §八十四 → **§八十五 守卫收窄裁定**

- As landed, three places cite **"REMEDIATION_REGISTER section 84"**: `handoff_guard8.json.ruling_source`, the `changes.diff` header L10 justification line for file #8, and the in-file comment.
- The register's own collision correction contradicts that numbering:
  - **`REMEDIATION_REGISTER.md` L1655** = section heading 「八十四、【REGISTRY-CLOSURE 处置汇总（AUDIT-GOAL ③ 残留排干：10 零处置行 + 10 隐式行 + 16 登记未修 + REM-78/79 编号注记 + REM-95/96）】2026-09-23 深夜」 → **§八十四 is now REGISTRY-CLOSURE**, not the guard ruling.
  - **`REMEDIATION_REGISTER.md` L1731** = 「（撞号消歧：本节与 REGISTRY-CLOSURE 汇总节曾同号八十四；现更正：REGISTRY-CLOSURE 42 行处置汇总=八十四、本节（守卫收窄裁定）=八十五；两节内容零改。）」 → **the guard-narrowing ruling section = §八十五 (85)**; both sections' content unchanged (zero content edits — correction is numbering only).
- **Correct pointer to cite from now on: `REMEDIATION_REGISTER` §八十五 守卫收窄裁定 (previously §84).** `OWNER_DECISIONS.md section 22 (L473-475)` remains correct as cited.
- Disposition: **cite-only.** The landed `changes.diff` is **not edited** (byte-frozen at `c178a118…`), and no landed file's bytes are changed to fix this pointer. The corrected pointer lives in this note and in the `review.md` addendum section; the register's own L1731 note is the authority.

## F-2 — `handoff.md` prose-currency (post-landing appends + the two shas)

- `handoff.md` is **prose** (not the DO-NOT-TOUCH `handoff.json`) and was appended after the base landing: **mtime 2026-09-23 23:50:40** local — after `handoff.json` (23:46:54) and `review.md` (23:46:17); the appended content is the guard-face receipt prose.
- Its 交付九步对账 item 5 still says **"8 文件 10 hunk"**, while the **final corrected count = 9 hunks** (the implementer's `ci_step9_hunkfix.sh` corrected `10 hunks` → `9 hunks` and re-verified `git apply --check` rc=0; header first line reads "8 files, 9 hunks").
- sha drift — the register's "handoff.md `7961ccd5…` 原件保留" record vs live bytes:
  - recorded pre-image: **`7961ccd5ee70b1724a30a6365373bce70a4835945300670a7870d6bf2036bf7f`** (4402 B, pre-append, status_at_pre_image `review_pending`)
  - live file: **`c915fb7b8427a318d7638b48e500fa5060b7718a63052c4d4ec96f40c27ddc3c`** (5415 B, mtime 23:50:40)
- **All authoritative carriers still match their recorded shas** (checked read-only at this pass): `handoff.json` `3942a338…` / 24218 B; `review.md` pre-append `978577d1c252b0ed4c46d9bea050690a6d1b717eab45aa7e8d6ded327664c9db` / 19837 B (== the register's recorded `978577d1…`) (changed only by this addendum's authorized append); `reviewer_report.md` `9904e708cd3c83f0ec9ed9ee0385264e233d0ba197f5564ff0bfdec6b6efb913` == its sidecar / 18639 B; `qualification.json` pre-append `a734747dd36cd2d2a9736665c8d104e30cde44f40c5a7e56aff0f493b2b8e4de` / 18086 B; `decision.md` `c501794bbc310a52346624c136215315ed183b4d997718d5661a2101e796366e` / 14804 B.
- Disposition: **prose-currency note only** — read the register's handoff.md sha as the pre-append pre-image; `handoff.md` may be reconciled by the parent at commit time; **no re-review needed**; `handoff.json`/`review.md`/`qualification.json` match.

## Standing merge-batch pin (TRIAGE `changes.diff` — re-verify at merge)

- **CURRENT sha256 (pin reference)** = **`c178a118bd9f1d1a683279b709613728bbc124a462d11facbca0f0519221ee0a`**, **11211 B**, **mtime 2026-09-23 23:58:11** local — observed read-only by this addendum pass.
- Counts: **8 files / 9 hunks / +56 −23** (header first line "8 files, 9 hunks"); `git apply --check` **rc=0** twice (implementer + the independent guard-face reviewer, on the full file incl. the `#` preamble); byte-identical reconstruction proven by the reviewer (8241 B body + 2970 B header; CJK `守卫收窄` intact).
- **Standing pin: this sha must be re-verified at merge time.** If `changes.diff` re-hashes to anything other than `c178a118…`, stop and re-verify before the single apply→commit→push batch. The change set (**8/9/+56−23**) rides the merge batch unchanged (carrier "Scope if accepting", L157–L163).

## F-3 / F-4 quick reference (carried for completeness)

- **F-3 (INFO)**: the key name `status` exists in both handoffs with different scopes — base = **`accepted_scoped`** (in `handoff.json`, untouched) and face = **`accepted`** (in `handoff_guard8.json`, set by this addendum). The two statuses are kept separated; the base key is never edited; `doc`/`status_note` in `handoff_guard8.json` remain the disambiguation (base attribution verdict = ACCEPT `9904e708`, guard face reviewed separately).
- **F-4 (INFO — 3 disclosure-only transients)**: (a) harness raw of the H6 read-before-edit rejection, (b) PS5.1 corrupt-at-93 intermediate diff, (c) misname46 transient RC=4 raw. Disclosed at decision §7.3-7.5 / commands events ③-⑤; the surviving raws (`guard_run.log`, `ci_step9_changes_finalize.sh`/`ci_step9_hunkfix.sh` final state, the two misname46 `PYTEST_RC=1` raws) are internally consistent with the disclosures; **the transients themselves are not independently re-verifiable** — accepted as disclosure-only, non-blocking.
