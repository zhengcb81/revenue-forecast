# I-09-C review.md — CARRIER LANDING (verdict transcribed by the carrier-landing executor; never self-signed)

Status: **`accepted_scoped`**. The independent reviewer wrote their verdict in
`reviewer_report.md` (the byte-pinned carrier), **not** in this file. This file is the
carrier-landing bookkeeping landing of that verdict: it transcribes the reviewer's verdict so
the attempt's `review.md` slot exists. **This is a pure bookkeeping transcription: it adds no
acceptance of its own.** Read `reviewer_report.md` itself for the reviewer's own words.
No verdict, review, or acceptance was authored in this pass.

`review.md` did not previously exist in this attempt (no implementer stub to preserve); this
file was created by the carrier-landing pass — not by the implementer and not by the reviewer.

## Verdict block (transcribed)

- Card: **I-09-C**（fault-injection / concurrency / crash-recovery acceptance），父项 **I-09**
- Attempt: `a20260922-01` (`<PLAN>\execution_runs\I-09-C\a20260922-01`)
- Verdict: **`accepted_scoped`** — the reviewer's literal label is written at
  `reviewer_report.md` **line 9**: `## VERDICT: **accepted_scoped**`
- Verdict author: **独立复核** (independent reviewer, sampled re-computation; line 5 boundary:
  工具仅 read / grep / pwsh；未 kill、未重跑任何测试、生产树只读、只写本报告两件文件;
  line 87: 本 reviewer 写入仅 `reviewer_report.md` + `reviewer_report.sha256`，未签署任何
  accepted 于 handoff/decision 等实现者文件)
- Verdict round: round 1 of this card (single independent review round; verdict is **scoped**,
  not clean — 7 numbered scope items at lines 13–18, 7 findings F-1..F-7 at lines 22–69, and an
  explicit 7-item unverified list at lines 73–81)
- This pass **does not self-sign**: `implementer_signed: false`,
  `implementer_never_signs_acceptance: true`; the verdict is **transcribed, not authored**.

### Carrier (byte-pinned)

| field | value |
|---|---|
| carrier file | `reviewer_report.md` |
| path inside attempt | `reviewer_report.md` |
| sha256 | `673c10bc24a2f093e152f464a6fe6ce9c6b0c07a8d1bc1a087b41362f1929b94` |
| bytes | 13666 |
| lines | 86 (UTF-8 no BOM, LF-only, 0 CR, single trailing LF) |
| pin sidecar | `reviewer_report.sha256` (present, 85 B, sha256 `ef516577f9f05fe4075b492cd6851c661ef94c72cf4890987d921e4bc4b23410`, content `673c10bc…29b94  reviewer_report.md`) |
| verdict line | 9 |
| first line of verdict | `## VERDICT: **accepted_scoped**` |
| verdict-line byte region | bytes 594..624 inclusive (31 B), sha256 `c7b900e370b4d5d2117b1bc396dab1ea0603765baf89915b28c5bab3e6b7ad57` |
| scope section (incl. the 7 scope-carry items) lines | 11–18 (bytes 627..1942, 1316 B, sha256 `a6bc7df73753237721a3cda21cb4fa6e74c7beefa3f80841efa0adab5583596c`); numbered items 1–6 at lines 13–18 (bytes 704..1942, 1239 B, sha256 `52344b4196832c384bae42063b5b9ed1b7313902d4365652f695b30aedfe45aa`) |
| findings section (F-1..F-7) lines | 22–69 (bytes 1950..11899, 9950 B, sha256 `4ebebf7c68ba258a0601c8b2069a7c86f6fc621e9969227583424ecc1c862d0b`) |
| minor defect F-7 lines | 68–69 (bytes 11453..11899, 447 B, sha256 `523dd4efe464c6471d88349dc8781f23ccaf80fe6df317c5fc06ecc562ac8b77`) |
| unverified section lines | 73–81 (bytes 11907..13252, 1346 B, sha256 `335ca55dc9aae1677d87ddced66b633bcad78c968b164873c74383552e81e32b`) |
| boundary section lines | 83–86 (bytes 13255..13665, 411 B, sha256 `2f19f202d5304079b6e00fbef5bcfee85f51be07fa8cfbe383c4eab225e2217c`) |
| reviewer role line | 5 |
| carrier region (whole file minus the single trailing LF) | bytes 0..13664 inclusive (13665 B), sha256 `cdf15a2596e052211d096419d61aa836aa82c0f4724e8c4c30e8e5b305327435` |
| producer | independent reviewer (独立复核), not the implementer |

Verification at landing time (read-only): file length = **13666 B** ✓, independent re-hash =
**673c10bc…1929b94** ✓ equals both the dispatch-pinned value and the sidecar value; line count =
**86** ✓; sidecar matches ✓; verdict line 9 reads `accepted_scoped` ✓. No byte of the carrier
was changed by this landing pass: `reviewer_report.md` and `reviewer_report.sha256` were
read-only here (this pass wrote only `review.md`, `handoff.json`, and
`evidence/I-09-C/qualification.json`).

## 7 scope-carry items — VERBATIM in substance (the verdict is void without all seven)

Carrier source: `reviewer_report.md` lines 11–18 (`接受范围（scope 必须随此判决一并携带，缺一不成立）`).
Items 1–4 and 7 are reviewer items 1/2/3/4/6; reviewer item 5 (line 17) carries two independent
requirements and is transcribed below as items 5 and 6.

1. **Everything tested = the I-09-B ISOLATED tree; production promotion undone.**
   「一切被测内容 = **I-09-B ISOLATED 树**（iso/rf，6/6 hash 与 I-09-B handoff 一致，见
   `after/production_and_iso_hashes_after.txt`）；**生产 promotion 未做**（context CF-I08C-1），
   本卡不构成任何生产等价声明。」 (line 13)
2. **F12 retained failure stays OPEN.**
   「**F12 保留失败（F-1/F12）仍为 OPEN**：frozen {0,2} 数值域未改、未 retry-to-green、case 保持
   red（verdict all_ok=false）；归属 I-09-B 产品修复轨 与 owner/I-09-A oracle-erratum 轨，二者本卡
   均未执行。」 (line 14) — i.e. it tracks **I-09-B product fix for broken-pipe exit normalization**
   *and* **owner/I-09-A oracle-erratum for the numeric domain {0,2}**.
3. **F5 signed gap stays OPEN.**
   「**F5 签名缺口（F-2/F5）仍为 OPEN**：signed UNCOVERED GAP（is_a_passing_fault_test=false），
   产品范围归 I-09-B；P-C3 单跑不构成“并发安全”。」 (line 15) — zero lock primitives confirmed by
   the reviewer's **own** grep of the iso tree (`iso/rf/scripts/publication_registry.py`) **and** of
   the production tree (`scripts/publication_registry.py`) (line 53).
4. **F-6 concurrency single-run limit.**
   「**F-6 并发单跑限制**：P-C3 仅单次无强制 lock-step 重叠运行，重复/高压重叠压力测试仍开放。」
   (line 16) — one P-C3 run, no forced lock-step overlap.
5. **Production I-16 / I-17 separately pending.**
   「生产侧 **I-16 / I-17 按本卡关闭标准另行 pending**」 (line 17, first half).
6. **`disclosure_adaptation=unmapped`, `accuracy=unproven` unchanged.**
   「`disclosure_adaptation=unmapped`、`accuracy=unproven` 不变。」 (line 17, second half).
7. **Zero-product-diff claim is domain-qualified (REM-79 phrasing).**
   「机制域限定（REM-79 句式）：本卡的“生产零改动”结论成立于 **`git status --porcelain -- scripts/`
   为空 + 6 个生产锚点 hash 等于 preflight 实测值（HEAD 6f74b056…）+ hooks 仅存在于本 attempt
   harness/ 且 `--fault none` 时不安装** 这一域内；不是无域全称断言。」 (line 18)

## Key verifications transcribed (reviewer's own, lines 22–66)

- **F-1 / PC2-K8**: independent end-to-end re-computation from raw bytes of
  `evidence/cases/PC2-K8_commit_after_response_lost/` — verdict **26 checks all ok, all_ok=true**,
  「与我的重算逐项吻合」(expected/actual 分列, raw 4242 vs expected "kill"; `writer_exited_11200.json`
  absent; distinct publication_id `c84a8ec8…`; audit_problems=[]). Conclusion: all_ok=true is
  recomputable from those bytes, 非自报. (lines 24–31)
- **F-2 / PC1-K6**: the five-link kill-arm chain verified link by link — `barrier_27488.json` →
  `pid_27488.json` (content = new_run manifest, **pid=27488 is the writer's `os.getpid()`, parent
  22488 = venv launcher recorded separately as launcher_pid — not the launcher being killed**) →
  `fault.json` (raw_returncode=4242, kill.ok=true, registered_in_manifest=true) →
  `writer_exited_27488.json` confirmed absent (finally did not run) → new reader 42980 (P0
  consumable, P1 committed_rows=0/logical=0/consumable=false, hook_trace stops at `commit:before`,
  audit_problems=[]); verdict 28 checks all ok. (lines 33–40)
- **F-3 / F12 attribution + handling**: A(pipe with reader)=**0** / B(pipe, no reader)=**120** /
  C(stdout→file)=**0** under identical harness/CLI/input/registry with stdout destination as the
  only variable; harness reserves only 4242 and `harness_maps_child_rc=false` (read-only
  `Popen.returncode`) → **attribution reliable**: rc=120 is the product CLI's own exit code.
  **Handling correct**: keep as a TRUE failure, no retry-to-green, no frozen-expectation change
  (case stays red, all_ok=false); F12 does **not** block this card (carried product finding;
  obligations beyond this card's modification authority). Dual track: ① I-09-B product fix
  (broken-pipe exit normalization) ② owner / I-09-A oracle-erratum for {0,2} — neither done here.
  (lines 42–49)
- **F-4 / F5**: `F5_lock_not_implemented/verdict.json` — constructed=false, `code_scan
  lock_keywords_found=[]`, `is_a_passing_fault_test=false`, `not_a_pass=true`, `checks=[]`;
  reviewer's own grep found zero lock primitives in iso **and** production trees; P-C3 live
  `lock_tokens_in_publication_registry_py=[]`. Ruling: signed-gap-as-nonpass correct, **not
  blocking**; F5 stays OPEN (lines 51–55).
- **F-5 / both supersessions confirmed**: `k_arms_first_attempt_supersession.md` complete —
  round-1 600s timeout → in-session observation → `--force` rmtree re-run; round-1 values
  transcribed per case (K1 182.83s / K2 182.62s / K3 182.89s), honest unrecoverable-bytes
  statement, launcher-PID root cause (Popen.pid=45816 ≠ os.getpid()=42452), criteria-unchanged
  statement (§5) — four elements present. **T-PUB**: run1 = 8 failed / 40 passed, exit=1, all 8
  failures `ModuleNotFoundError _cffi_backend` (reviewer counted 8 hits = 8 FAILED lines, all
  Ed25519 imports in `tests/test_attestation.py`) → this card's venv environment defect, not a
  product/test failure; run1 text preserved; run2 = **48 passed**, exit=0; **delta explained**:
  8+40 = 48 same tests, fix = copying back the missing `_cffi_backend.cp313-win_amd64.pyd`,
  same argv/env; plus `tpub_i09b.txt` = 11 passed. (lines 57–59)
- **F-6 / 4 stop conditions, none triggered**, each with evidence: ① no kill of an unregistered
  PID (barrier+manifest double precondition; round-1 unverifiable → refused kill, recorded as
  harness failure); ② no persistence below the claimed guarantee (fresh readers; errno arms rc=2
  with no partial visibility); ③ no history-row deletion (F7 registry byte-identical across both
  recoveries); ④ no "exception-path-only" passed off as real exits (2 sampled arms raw=4242 with
  `writer_exited` absent; 7 OSError arms explicitly labeled exception-path-only). Plus path
  boundary (allowed_write_roots=attempt, zero hits for real registry/user packages/site-packages),
  the reviewer's own read-only `git status --porcelain -- scripts/` = empty and `rev-parse HEAD`
  = `6f74b056631e0cb50a28b57bdcf979514dadb8f9`, handoff showed `status=review_pending` /
  `implementer_self_acceptance=false` at review time (no self-signing), and hook-position
  documentation cross-consistent. (lines 61–66)
- **Unverified list (lines 73–81)**: 22 remaining fault cases not individually recomputed; P-C5/P-C3
  not line-audited; some harness-defect/TIMEOUT rounds not line-audited; the "13 real process
  terminations" total not independently recounted (12 locatable, 1 unlocated); k_arms round-1 raw
  bytes unrecoverable by definition; `eol_reconstruction.txt` outputs not re-run by the reviewer;
  T-PUB "same argv/env" not diffed parameter-by-parameter. Carried as declared boundary.

## Reviewer's minor, non-blocking defect (registered, not new acceptance)

**F-7 (MINOR, non-blocking)** — `probe_f12.py:65` reuses the B-stage `err` variable, so control
**C**'s stderr field in `pipe_controls.json` carries B's stale text (C's own stderr was never
captured). **A/B/C returncodes were each captured correctly in their own branches, so the rc
attribution is unaffected**; the field must not be cited as an observation of C. Recommended fix
rides the **F12 product-fix / oracle-erratum track** (harness-level; not this card's obligation).
(lines 68–69)

## Not granted

`disclosure_adaptation` stays **unmapped**; `accuracy` stays **unproven**; no production write
authority (0 production bytes; the zero-product-diff claim holds only in the domain-qualified
form of scope item 7); F12 and F5 stay **OPEN_IN_ACCEPTED_SCOPE**; repeated/high-overlap
concurrency stress, production promotion, and production **I-16 / I-17** remain others'
decisions — this landing adjudicates none of them.

## Bookkeeping

- Landed by: carrier-landing bookkeeping executor (delegated subagent), 2026-09-22.
- Status transition: `review_pending` → `accepted_scoped` (performed in `handoff.json` by this
  pass on the parent's dispatch; the verdict itself was authored only in `reviewer_report.md`
  line 9 by 独立复核 — never by the implementer and never by this file's author).
- `status_before_bookkeeping_fix: review_pending` recorded; `status_authority` added pointing at
  the carrier with line ranges, sha256 and byte proofs; stale implementer-era fields asserting
  review-not-yet-done (`status_authority_note`, `next_action`, `reviewer_status`, and the step-9
  接续 reason) preserved under `*_historical_pre_verdict` / `reason_historical_pre_verdict`
  keys (REM-83 species) and re-pointed at `status_authority`.
- `implementer_signed: false`; `implementer_never_signs_acceptance: true`;
  `verdict_is_transcribed_not_authored: true`.
- This pass wrote exactly three files: `review.md` (created, this file), `handoff.json`
  (status + status_before_bookkeeping_fix + status_authority + bookkeeping + 7 scope-carry items
  appended as SC-1..SC-7 + F-1/F-2 marked `OPEN_IN_ACCEPTED_SCOPE` + four stale-field
  supersessions; all other pre-existing keys untouched), `evidence/I-09-C/qualification.json` (created). Zero bytes written
  to `reviewer_report.md`, `reviewer_report.sha256`, `iso/`, production, or any frozen/historical
  artifact. handoff.json pre-image: 19339 B / sha256
  `31caacf72cea2ecb21c09b4f4d50464fccd648858968f49980fbc620b07821df`.
