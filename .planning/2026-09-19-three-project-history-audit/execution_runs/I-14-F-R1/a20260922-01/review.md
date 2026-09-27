# I-14-F-R1 review.md — CARRIER LANDING / STATUS FLIP（簿记转录；实现者从不自签）

Status: **`accepted_scoped`**（attempt `a20260922-01`）。独立复核（独立 reviewer）把裁决写在
`reviewer_report.md`（字节钉载体）——**不是**本文件。本文件是该裁决的**落定簿记转录**：
它翻转此前 implementer stub 的 `review_pending` 状态口径，使本 attempt 的状态口径与
reviewer_report 一致（消除 AUDIT-DESIGN D4 所记「同一 attempt 两个状态口径」双口径）。
**这是纯簿记转录：不新增任何接受。** 裁决原话请读 `reviewer_report.md` 本身。
`verdict_is_transcribed_not_authored: true`；`implementer_signed: false`；`implementer_never_signs_acceptance: true`。

## Verdict block（转录，不改判）

- Card / attempt：**I-14-F-R1 / `execution_runs\I-14-F-R1\a20260922-01`**。
- verdict：**`accepted_scoped`** —— reviewer 原词在载体 **L16**：`## VERDICT: **accepted_scoped**`。
- 裁决作者：**独立复核（独立 reviewer）**，N=1；本文件作者=BOOKKEEP-REPAIR 簿记执行者（父派单），**从不自签**。
- 接受域（转录）：按 owner `OWNER_DECISIONS.md` §16 E-1「E-1: 150/60」（`GENERATION_RESERVE=150`
  ⇒ relocate iff `len + 150 > 210 ⇔ len > 60`）落 product-side 短 basetemp 约定；边界 60/61 钉住
  （60 → unrelocated，61 → relocated）；尺寸扫描 61/69/76/82/86 relocate+pass、40/60 unrelocated（7/7 guard ok）；
  12 控制翻转各带逐字 superseded 理由「owner §16 E-1 chose 150/60; this control's unrouted expectation is superseded」；
  RED/GREEN/MUT 由 reviewer 亲自深登录复跑复现（RED rc1 含 `WinError 206`、GREEN rc0 `relocated=true`、
  MUTATION rc1 `relocated=false`）；unit suite 15 passed rc0（reviewer 自跑）；封存的 I-14-F attempt 与生产零触碰。
- 随行限定（转录）：CF-I14FR1-3 / Gap-5 裁**不阻断** ⇒ 晋升期采样义务（另卡、未授予）；R-2 立（I-14-E 域）；
  N-1（low）/N-2（info）/N-3（info）；`disclosure_adaptation = unmapped`、`accuracy = unproven`；
  `iso/` 晋升=独立 owner 决定，**未授予**。

## Carrier（byte-pinned；本转录所依据的裁决载体）

| field | value |
|---|---|
| carrier file | `reviewer_report.md`（单轮；verdict `accepted_scoped`） |
| path | `execution_runs/I-14-F-R1/a20260922-01/reviewer_report.md` |
| sha256 | `8ce87ef6d31087da65e556be4736a8c8f7734594575cf868149df383e5f62a1c` |
| bytes | 15841（2026-09-23 复算 = 侧车值 ✓） |
| sidecar | `reviewer_report.sha256`（321 B，sha256 `dbbe3e2935804c89f09f2e4fddcb678da1ed46ff69dc47a0926d1b4f4c557d604`；内容=`sha256:` + `bytes: 15841` + `verdict: accepted_scoped`、`pinned_at_local: 2026-09-22T09:29:07+01:00`）——内容相符，0 字节写入 |
| verdict line | 16（`## VERDICT: **accepted_scoped**`） |
| scope limits | L35–48；Gap-5 ruling §6 L143–163；findings §7 L165–174；signature §9 L202–211 |
| producer | 独立复核 only —— 从不是 implementer、从不是本文件作者 |

Verification at flip（read-only，2026-09-23）：15841 B ✓；复算 `8ce87ef6…2a1c` ✓ == 侧车值；
L16 `accepted_scoped` ✓。**`reviewer_report.md` 与 `reviewer_report.sha256` 0 字节改动。**

## review_stanb_stub_historical（原值留痕：翻转前 review.md 全文，一字不删）

- **字节权威留存件**：`review_stanb_stub_historical_20260923.md`（6029 B，sha256
  `7f1808993e4e30884aeca26ad14d5ce2ac149e77e452646ed5a64a53e48a8a83`）= 翻转前 `review.md` 的
  **逐字节副本**（含 implementer stub 全文 L1–41 + 2026-09-22 CARRIER LANDING 块 L43–93）。**从不删除。**
- 下框 = 该留存件**全文逐字注入**（与兄弟件字节等同；如有毫厘差以兄弟件+其 sha 为准）：

```text
# I-14-F-R1 review.md — STUB (no verdict; the implementer does NOT self-sign)

Status: **`review_pending`**. No review of this attempt has been performed yet. Acceptance is
the exclusive responsibility of an independent reviewer (never the implementer, never the
owner, never this file's author). This stub must be replaced only by a reviewer's own verdict
block (or a carrier landing that transcribes a byte-pinned reviewer report, as happened on
I-14-F a20260919-01).

## What this attempt claims (for the reviewer to verify, not to believe)

- Card: **I-14-F-R1** — apply owner ruling `OWNER_DECISIONS.md` §16 E-1 (verbatim
  「E-1: 150/60」: `GENERATION_RESERVE = 150` ⇒ relocate threshold **60**) to the product-side
  short-basetemp convention, in a NEW isolated attempt. I-14-F's attempt
  (`execution_runs/I-14-F/a20260919-01`) is sealed/accepted and was read-only input.
- The oracle was frozen BEFORE any run: `oracle.md`, sha256 sidecar `oracle.sha256`.
- Expected evidence: 15-case unit suite with boundary 60/61 pinned; RED on the pristine tree
  (deep cwd → WinError 206); GREEN (deep cwd → relocated, passes); mutation
  (`CW_SHORT_BASETEMP_DISABLE=1` → both nodes fail, frozen signatures); size sweep
  (61/69/76/82/86 relocate + pass; 40/60 unrelocated).
- Errata registry for I-14-F's sealed doc defects F-2/F-3/F-4/F-6 lives in this attempt's
  `decision.md` (append-only; each cites the carried-finding ID).

## Reviewer checklist (suggested)

1. `oracle.sha256` pin predates every run artifact (mtimes under `before/`, `after/`).
2. Re-derive the criterion from `iso/tree/conftest.py`: `len + 150 > 210 ⇔ len > 60`.
3. Re-run the unit suite; confirm 15 passed, boundary 60/61 pinned, flips carry written reasons.
4. Re-run RED/GREEN/mutation at cwd 166/167 (driver `--target-root-len 140` guard).
5. Check the sweep table in `after/sizes/summary-placement.json` against oracle §8.
6. Confirm zero writes: production repos, and I-14-F's sealed attempt (compare against its
   `after/final_hashes.json`).
7. Confirm `commands.json` entries carry real argv/cwd (F-6 fixed for this attempt).
8. Confirm `handoff.json.status == "review_pending"` was true before your verdict, and that no
   acceptance language appears in any implementer-authored file.

## Boundaries

`disclosure_adaptation = unmapped`, `accuracy = unproven`; test-infrastructure only; promotion
to any production tree is a separate, ungranted step.

---

## CARRIER LANDING — verdict block (bookkeeping transcription, 2026-09-22)

This block supersedes the `review_pending` status declared by the implementer stub above; the
stub text is retained verbatim as implementer-authored history (append-only).

- **verdict**: `accepted_scoped`
- **reviewer**: 独立复核 — independent review; the verdict was authored solely by the
  independent reviewer, never by the implementer.
- **carrier**: `reviewer_report.md` — **15841 B**, sha256
  `8ce87ef6d31087da65e556be4736a8c8f7734594575cf868149df383e5f62a1c`, pinned by sidecar
  `reviewer_report.sha256` (`sha256:` + `bytes: 15841` + `verdict: accepted_scoped`,
  `pinned_at_local: 2026-09-22T09:29:07+01:00`).
- **byte proof**: re-hashed at carrier landing — 15841 B, digest matches the sidecar exactly.
- **carrier line ranges**: verdict L16; scoped residuals L35–48; Gap-5 ruling §6 L143–163;
  findings §7 L165–174; signature §9 L202–211 (`accepted_scoped`, N-1..N-3 + inherited CFs
  as scope).
- **nature of this block**: a bookkeeping transcription of a byte-pinned reviewer report. It
  adds **no acceptance of its own** — no verdict is authored or re-adjudicated here.
  `implementer_signed: false`; the implementer never signs acceptance.

### Scope as accepted (transcribed, not re-adjudicated)

- **threshold 150/60 adopted per owner §16 E-1** (`GENERATION_RESERVE=150` ⇒ relocate iff
  `len + 150 > 210 ⇔ len > 60`).
- **boundary 60/61 pinned**: 60 → unrelocated, 61 → relocated (unit cases + sweep halves).
- **size sweep**: 61/69/76/82/86 **relocate + pass**; 40/60 **unrelocated** (7/7 guard ok).
- **12 control flips, each under the verbatim superseded reason** 「owner §16 E-1 chose 150/60;
  this control's unrouted expectation is superseded」 — recorded as 8 flip rows in decision.md
  §4 (basetemps 69/68, 76/75, 82/81, 86 + unit 84/82/78 + `decide()` 64 = 11 datapoints) plus
  4 inline reason comments in the unit file = 12 flip records; the 52-char datapoint is
  deliberately NOT flipped; the reason sits at the §4 table head rather than restated per row
  (**N-1**).
- **RED / GREEN / MUT reproduced by the reviewer** in own deep-logon runs: RED rc 1 with
  literal `WinError 206` and no decision file; GREEN rc 0 with `relocated=true`,
  `generation_reserve=150`, `threshold=60`, `cleanup removed=true`; MUTATION
  (`CW_SHORT_BASETEMP_DISABLE=1`) rc 1 with `relocated=false`, `reason=disabled-by-env` and
  the literal `WinError 206` back.
- **unit suite: 15 passed, rc 0** (reviewer's own run).
- **sealed I-14-F attempt + production untouched**: I-14-F's 3 pinned files re-hash unchanged
  (`c22be9f3…`, `b0402b56…`, `2e6709e0…`); production `company-wiki` at HEAD `f39bd5a6` with
  exactly the 3 pre-existing user modifications.

Scope limits transcribed together with the verdict: CF-I14FR1-3 / Gap-5 ruled **not blocking**
⇒ promotion-time sampling obligation (the separate, ungranted promotion card must sample a
broader company-wiki suite before merge); **R-2 stands** (I-14-E scope, load band
unadjudicated by design); **N-1** (low), **N-2** (info, per-row env not in commands.json —
rerunner must read the harness for `PYTHONPATH`), **N-3** (info, tree-vs-red-tree import
asymmetry, immaterial); reviewer-disclosed unit-run1/run2 failures retained (harness
invocation + pathlib 63-vs-64 construction bugs; test fixed, not the oracle — mtime ordering
08:34 < 08:35 < 08:42); `disclosure_adaptation = unmapped`, `accuracy = unproven`;
promotion of `iso/` = separate owner decision, **ungranted**.
```

原状态口径（留痕摘要）：stub 首行 `# I-14-F-R1 review.md — STUB (no verdict; the implementer does NOT self-sign)`、
`Status: **`review_pending`**`；2026-09-22 CARRIER LANDING 块已转录 verdict `accepted_scoped` 并声明
「supersedes the `review_pending` status declared by the implementer stub above」——但文件**头行状态**仍为
`review_pending`（=D4 双口径本体）。本次翻转把**头行状态**落为 `accepted_scoped`，stub 与旧块全文保留在上方字段。

## Bookkeeping

- 翻转者：BOOKKEEP-REPAIR / a20260923-01 簿记执行者（delegated subagent），2026-09-23，父派单
  （parent session `session-bfecd191-fbc3-4a66-8ed1-6562479bf102`；AUDIT-DESIGN D4 修复项 #3）。
- before/after：`review.md` before = `7f180899…48a8a83` / 6029 B → after（见本卡 `binding.json`）；
  before 全文字节 = 兄弟件 `review_stanb_stub_historical_20260923.md`（同 sha）。
- `handoff.json` 已于 2026-09-22 落定翻转（`status: accepted_scoped`、`status_before_bookkeeping_fix: review_pending`、
  `status_authority` 在）——本次**不动** handoff.json。
- 0 字节写入 `reviewer_report.md` / `reviewer_report.sha256` / 任何冻结件 / 任何产品树 / 任何 git 状态。
  **无自签**：裁决由独立复核写就，本文件只是转录，不授予任何新资格
  （`disclosure_adaptation = unmapped`、`accuracy = unproven`、晋升未授予）。
