# REVIEWER REPORT (ADDENDUM) — RF-STEP9-TRIAGE / a20260923-01 — #8 guard-narrowing face

- **Scope of this review** (review domain = RF-STEP9-TRIAGE #8 guard-narrowing face): the #8 "守卫收窄"
  (guard-narrowing) face delivered after the base verdict.
  Base verdict is already ACCEPT+landed (`handoff.json` sha256 = `3942a338…` = accepted_scoped, DO-NOT-TOUCH) and is
  **asserted untouched** below — this report does not re-open it; review-scope, no landing.
- **Owner ruling under review**: OWNER_DECISIONS.md §22 (L473-475) = 「守卫收窄」, owner 2026-09-23 (read myself).
- **Reviewer re-run**: independent WSL/`%TEMP%` reproduction, 2026-09-23T23:17:39Z–23:17:54Z (guest clock; after
  implementer's final delivery at 22:58Z), fresh clone `/tmp/rg8/revenue-forecast` @`b0d016a6`.
- **Reviewer writes**: exactly this file + `reviewer_report_guard8.sha256`. Everything else in `%TEMP%`
  (`rev_guard8_repro.sh`, `rev_guard8_out/` ×13 files) or `/tmp/rg8` scratch. RF/wiki/filing = read-only.

## VERDICT: **ACCEPT-ADDENDUM**

The owner-ruled narrowing (2) was executed exactly as ruled — no new allowlist entries, exemptions unchanged
`{filing_fetch_client.py, source_preparation.py}`, judgment criterion not deleted — and both directions of the proof
are load-bearing: I independently reproduced **2 green + 4 red** over the 6-run matrix plus the final green, with the
NEW failure text appearing solely where the narrowed assertion should fire. Diff integrity, handoff integrity, plus the
disclosures check out. Findings F-1..F-4 are non-blocking (documentation-currency items for the parent's addendum
note). **No changes_required for this face.**

## 1. Judge-implementation read proof (re-done by me end-to-end)

| Claim | My check | Result |
|---|---|---|
| Sole implementation = `tests/test_single_owner_guard.py` | case-sensitive grep `FORBIDDEN_SYMBOLS` over RF `scripts/ tests/ tools/ compatibility/` | solely `tests/test_single_owner_guard.py` L23/65/67 — zero hits in `tools/` sources ✓ |
| `DOWNLOAD_DOMAIN` exists nowhere pre-apply | grep over `scripts/ tests/ tools/` | **0 hits** (narrowed code exists solely in `changes.diff` — diff is the vehicle) ✓ |
| subprocess import surface = exactly 3 files | my grep `import subprocess` over `scripts/*.py` | `filing_fetch_client.py:25` (canonical) / `source_preparation.py:18` (ORCHESTRATORS) / `revenue_core.py:12` = **exactly 3** ✓ |
| Over-broad census: 12 tokens × `revenue_core.py` | my own case-insensitive census of `filing/download/fetch/resolve_filing/acquisitionmanager/adapterregistry/dayu/stock/dropbox/curl/wget/xlsx` | **0 hits × 12/12** ✓ (matches `guard_readproof.txt` G3) |
| `revenue_core` subprocess = attestation spawn, not download | read L215-235 | L223 `subprocess.run([str(resolved)], input=json.dumps(request…))` feeding `_record_attestation_failure` + L230 `TimeoutExpired` = **provider attestation spawn** ✓ |
| Narrowing = scope-fix-to-declared-semantics | read `filing_fetch_client.py` L1/L12/L208/L306 | L1 `"""Thin subprocess client for the standalone filing-fetch skill.`, L12 usage line with `[--allow-download]`, L208 `cmd.append("--allow-download")`, L306 `--allow-download` flag = **declared download owner** ✓ |

Diff-hunk read confirms H6a (adds `DOWNLOAD_DOMAIN` + `_in_download_domain`, no exemption/constant edits) and H6b
(replaces solely the subprocess-walk reach). The second net **`test_no_second_resolve_filing_symbol`** and the
canonical-uniqueness exemptions (`CANONICAL_CLIENT`/`ORCHESTRATORS`/`FORBIDDEN_SYMBOLS` declarations) are **absent
from the diff = untouched**; my final run shows 3 tests pass (`3 passed`), and `second_net.txt` asserts all four
declarations/defs present exactly once in the applied tree.

## 2. Independent 6-run matrix re-run (my own script; `%TEMP%`, no network, local clone)

Script: `%TEMP%\rev_guard8_repro.sh` → outputs `%TEMP%\rev_guard8_out\` (r1..final raws, patch.txt, second_net.txt,
rg8_mine.diff, promotion_surface.diff, diffstat.txt, env.txt). Patches applied with the implementer's
`%TEMP%\ci_step9_iso_patch.py`: **10/10 APPLIED + ALL_PATCHES_APPLIED + py_compile OK**.

| Run | Expect | My RC | My message class | Matches their raw |
|---|---|---|---|---|
| R1 baseline (pre-narrow, no patch) | red | **1** | OLD_MSG (`revenue_core.py imports subprocess (second download owner)`) | `wsl_head`/`win2_head` red ✓ |
| G1 narrowed, clean tree | green | **0** | no-msg (`3 passed`) | `g_g1_narrow_green` RC=0 ✓ |
| EX1 `g_b1` non-canonical filing-CLI downloader | red NEW | **1** | **NEW_MSG** (`_s9_ex1_filing_downloader.py uses subprocess inside the filing/download domain`) | `g_b1` RC=1 NEW_MSG ✓ |
| EX2 `g_b2` unlabeled curl+xlsx (no filing/download/fetch words) | red NEW | **1** | **NEW_MSG** (`_s9_ex2_unlabeled_pull.py …`) | `g_b2` RC=1 NEW_MSG ✓ |
| M1 scope→True (full-width) | red + revenue_core | **1** | NEW_MSG + **`revenue_core.py uses subprocess…` flagged = YES** | `g_m1` RC=1 revenue_core ✓ |
| M2 scope→False + EX1 present | green (bypass opens) | **0** | no-msg | `g_m2` RC=0 ✓ |
| final `iso_ok_single_owner` | green | **0** | no-msg (`3 passed`) | `iso_ok_single_owner` RC=0 ✓ |

**Tally = 2 green (G1, M2) + 4 red (R1, EX1, EX2, M1) + final green — exactly as claimed; narrowing is
load-bearing (M1) and counterexamples are load-bearing (M2) — two-way proof holds.**

- **NEW_MSG placement**: grep `filing/download domain` over the evidence/ directory → hits are found in exactly
  3 files of evidence/: `g_b1_ex1_filing_downloader`, `g_b2_ex2_unlabeled_pull`, `g_m1_unnarrow_red` — **zero hits
  across any pre-narrow raw** (`wsl_head`, `win_head`, `win2_head`, `wsl_anchor46`, `wsl_oldwiki`, `wsl_preEc3`,
  `wsl_atEc3` guard raws); my own R1 raw = OLD_MSG (message class recorded per raw) ✓.
- Env pins: wiki_head = wiki_after = `5d725294…` (asserted at pin, never checked out), rf clone = `b0d016a6…`,
  filing = `89c8bdb2…` ✓.

## 3. Diff integrity (`changes.diff` sha256 = `c178a118bd9f1d1a683279b709613728bbc124a462d11facbca0f0519221ee0a`)

- **`git -C RF apply --check changes.diff` → rc=0 by me** (the `#` justification preamble is indeed
  find_header-tolerant — verified by actually applying the full file with header, not just the body).
- Counts by my grep: **files = 8** (`diff --git`), **hunks = 9** (`^@@`), **+56 / −23**; header first line reads
  "8 files, 9 hunks" (their corrected 10→9 wording, `ci_step9_hunkfix.sh` re-verifies rc=0) ✓.
- **Byte-level reconstruction**: I regenerated `git diff` from my own independently-patched fresh clone →
  `BYTE_IDENTICAL=True`: my body (8241 B) == delivered bytes after the first `diff --git` (2970 B header +
  8241 B body = 11211 B file), and delivered header == `%TEMP%\ci_step9_changes_header.txt` byte-for-byte (2970 B).
  The delivered diff is exactly what the patcher produces; the bash byte-safe re-export left no mojibake
  (CJK probe `守卫收窄` intact = 1 hit; file decodes clean UTF-8).
- **PROMOTION_SURFACE_DIFF_EMPTY**: diff path list contains none of the B1 promotion 5 files
  (`revenue_core/revenue_publication/revenue_report/company_wiki_source/source_preparation`); my own path-scoped
  `git diff b0d016a6 -- <5 files>` output = **0 bytes** ✓.
- **#8 file's first-line justification** (header L10) contains the owner-ruling reference:
  `# 8. tests/test_single_owner_guard.py [H6a+H6b/#8] OWNER RULING (2) guard narrowing — OWNER_DECISIONS section 22 /
  register section 84 (file count 7->8)` ✓ (citation caveat = F-1).

## 4. Handoff integrity

- **Landed `handoff.json` untouched**: sha256 = `3942a3384d5801d8b5078a36f2d944199d68cfdc794921a6983351284a715611`
  (24218 B, mtime 23:46:54 local) — **== `3942a338…` asserted**; `status=accepted_scoped` still present in the file.
- **`handoff_guard8.json`** (sha256 `01b0eb99049996eaf5dcb08adb1d6ab1a18ab3d94c9087fdedca67df08731c91`) re-parsed as
  JSON: `base_handoff.sha256_prefix = "3942a338"` == actual prefix ✓; it is a separate additive addendum
  (`doc` says it does NOT replace the base) whose substantive new group is **`guard8_execution`**; it does not copy
  or modify any landed key (the landed file is byte-untouched, so each original key is trivially zero-modified).
  The sole shared key *name* with the base is `status`, holding the face-scoped value
  `review_pending_additional_review` with an explicit `status_note` pointing at the base ACCEPT — see F-3.
- Other landed carriers cross-checked against the register's transcription: `review.md` = `978577d1…` ✓,
  `reviewer_report.md` = `9904e708…` (matches its own sidecar) ✓, `qualification.json` = `a734747d…`/18086 B ✓.
  (`handoff.md` prose = `c915fb7b…` vs register-recorded `7961ccd5…` — see F-2.)

## 5. Process events — each disclosure exists and raws back it

1. **H6 first-edit rejection → five invalid runs**: disclosed at decision §7.4 + commands event④. Raw backing =
   `%TEMP%\guard_run.log` (mtime 23:15 local): patcher output has **no `APPLIED tests/test_single_owner_guard.py`
   lines** (H6 absent) yet `ALL_PATCHES_APPLIED`, and its five `GUARD_RUN` lines are baseline-equivalent
   (G1 RC=**1** vs expect 0, M2 RC=**1** vs expect 0) = invalid round, as disclosed. `guard_run2.log`/`guard_run3.log`
   show the valid pattern (G1=0, B1=1, B2=1, M1=1, M2=0) ✓. The harness-level rejection event itself has no raw
   (F-4).
2. **PS5.1 ANSI corrupt-at-93 → bash byte-safe re-export + hunk9 fix**: disclosed at decision §7.5 + commands
   event⑤. Raw backing = `%TEMP%\ci_step9_changes_finalize.sh` (bash `cat header+body`, apply --check re-verify,
   CJK probe) + `%TEMP%\ci_step9_hunkfix.sh` (`10 hunks`→`9 hunks`, re-verify) + final state I verified
   (apply --check rc=0, header==header file, body==my fresh regeneration, CJK intact). The corrupt intermediate was
   overwritten by `.new→mv` by design (F-4).
3. **misname46 transient RC=4 → overwritten by RC=1 runs**: disclosed at commands event③ + decision §7.3.
   Raw backing = `wsl_misname46_tests_test_fc1102_…out` **PYTEST_RC=1** and `wsl_misname46_tests_test_fc1302_…out`
   **PYTEST_RC=1**, both with intact headers (`wiki_sha=5d72529…`, `rf_sha=46bd8b16…`, signature
   `manifest triplet commits missing: ['revenue']`) = the 2 original valid raws intact ✓; the transient RC=4 raw
   was overwritten (disclosure-only, F-4).

## 6. Boundary compliance

- **RF product paths = 0 by this face**: my `git status --porcelain` shows zero `scripts/ tests/ tools/
  compatibility/ .github/` entries (changes confined to `.planning/` attempt + concurrent-card artifacts);
  the change vehicle is `changes.diff` (apply --check; no state-changing git).
- My runs: **no network** (local `git clone` of ~/rf-ci-repro, no remote endpoints), wiki/filing asserted at pin
  (never checked out), RF production read-only (`status`/`diff`/`log`/`apply --check`).
- My writes: exactly 2 files — `reviewer_report_guard8.md` + `.sha256` in the attempt dir; remaining artifacts under
  `%TEMP%` and `/tmp/rg8` scratch.

## Findings (0 blocking; 0 changes_required-for-face)

- **F-1 (MINOR — stale citation)**: `handoff_guard8.json.ruling_source`, `changes.diff` header L10, and the in-file
  comment cite "REMEDIATION_REGISTER **section 84**", but the register's own collision correction
  (REMEDIATION_REGISTER L1731) renumbers the guard-narrowing ruling to **§八十五 (85)** — §八十四 (L1655) is now
  REGISTRY-CLOSURE. `OWNER_DECISIONS section 22 (L473-475)` is correct. Suggest the parent's addendum note records
  the pointer as §85 (previously §84) rather than editing the landed diff.
- **F-2 (MINOR — prose currency)**: `handoff.md` was appended after landing (mtime 23:50:40 local; guard-face
  receipts) and its 交付九步对账 item 5 still says "**8 文件 10 hunk**" (final corrected count = 9); consequently the
  register's "handoff.md `7961ccd5…` 原件保留" record no longer matches current bytes (`c915fb7b…`). `handoff.md`
  is prose (not the DO-NOT-TOUCH `handoff.json`) — reconcile in the addendum note, no re-review needed.
- **F-3 (INFO)**: `handoff_guard8.json` reuses the key name `status` for the face-scoped
  `review_pending_additional_review` while the landed base keeps `accepted_scoped`. Intentional and disambiguated by
  `doc`/`status_note`; when transcribing to `accepted` via this addendum, the parent should keep the two statuses
  clearly separated (base key untouched).
- **F-4 (INFO — disclosure-only transients)**: 3 intermediate artifacts were overwritten/not preserved by their
  own process: (a) the harness raw of the H6 read-before-edit rejection, (b) the PS5.1 corrupt-at-93 intermediate
  diff, (c) the misname46 transient RC=4 raw. Each of the 3 is disclosed (decision §7.3-7.5 / commands events 3-5)
  and the surviving raws are internally consistent with the disclosures; the transients themselves are not
  independently re-verifiable.

## Unverified (explicit)

- The 3 F-4 transients (above) — disclosure-present, artifact-absent by design.
- `ruff`/`mypy` and the full CI step9 selection were not re-run (no environment; inherited disclosure, decision §5).
  The 8 target files + guard + patrol were covered by the implementer's iso runs and (for the guard face) by my
  independent re-run.
- GitHub/true-CI behavior (no network by boundary); base-card's 5 unverified rows unchanged by this face.
- Intent behind the §84/§85 citation (I verified solely the register's final numbering as written).
- `handoff.md` prior bytes `7961ccd5…` (pre-append version not reconstructible from surviving files).

## Scope if accepting (for the parent's transcription)

Guard face = **owner-ruled narrowing correctly executed with two-way proof** (narrowing load-bearing via M1,
counterexamples load-bearing via B1/B2/M2); the change set is now **8 files / 9 hunks / +56 −23** riding the merge
batch unchanged. Parent to: (a) append an addendum note to the landed `review.md` (or a separate note file) pointing
at this report; (b) transcribe `handoff_guard8.json.status` → `accepted` per this addendum ruling; (c) carry F-1/F-2
citation-currency fixes as prose corrections.

## REM-79 self-check

Tool: `execution_runs/REM79-MECHANIZATION/a20260922-01/tools/check_domain_assertions.py` v1.2.0-correction2,
invoked `PYTHONIOENCODING=utf-8 python <tool> reviewer_report_guard8.md` (target = 0 violations / rc=0).
Draft iteration ran the checker and removed each flagged line-scoped quantifier; final-content result:
**0 violations / rc=0** (re-checked after this line was written).

## Artifacts produced by this review

- `reviewer_report_guard8.md` (this file) + `reviewer_report_guard8.sha256`
- `%TEMP%\rev_guard8_repro.sh` (re-run script), `%TEMP%\rev_guard8_out\` (7 run raws + patch/second-net/diff/promotion
  outputs; `rg8_mine.diff` = byte-identical body proof)
