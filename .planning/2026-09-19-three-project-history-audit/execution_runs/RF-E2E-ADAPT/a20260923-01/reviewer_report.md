# reviewer_report.md — RF-E2E-ADAPT / attempt a20260923-01 (independent review)

- **Card:** `RF-E2E-ADAPT` (gate root-fix for real-roots E2E RED), attempt `a20260923-01`
- **Plan:** `.planning/2026-09-19-three-project-history-audit`
- **Reviewer:** independent delegated reviewer (read/grep/pwsh only; runs into `%TEMP%`; no product writes; git used **read-only** — `status`/`diff`/`log`/`rev-parse` only; this report + sidecar are the reviewer's only writes（域：本行 only 指本会话的写入面）)
- **Reviewed:** 2026-09-23 (local), all 7 dispatch verify-items executed live（域：dispatch 7 项核验清单）
- **Verdict: ACCEPT (sign-off as reviewer, 4 findings — none blocking)**（域：4 项 findings 对 verdict 的影响面）

Scope if accepting (parent): commit the four RF test files (worktree already
carries them) → push batch-5c (gate full run incl. real-roots + real-data with
these fixes); full-gate / mypy / install-sync / the other 8 real-data files
remain in the gate's own hands (handoff unproven item 1) — CI re-run after push.

---

## 1. Oracle frozen-first — VERIFIED (with one honest nuance)

Live timestamps (NTFS CreationTime/LastWriteTime, 2026-09-23):

| artifact | time | vs oracle |
|---|---|---|
| `evidence/red_raw.txt` (RED repro) | 02:36:49 | **before** freeze |
| `evidence/probe_receipt_read.out` | 02:37:08 | **before** freeze |
| `oracle.md` (C == W, immutable since) | **02:41:58** | — |
| `diffs/before/*` copies created | 02:41:59 (+1 s) | after freeze |
| `evidence/red_prep_e2e_raw.txt` | 02:42:15 | after freeze |
| `evidence/red_zr709_raw.txt` | 02:42:21 | after freeze |
| `evidence/red_zr803_lock_raw.txt` / `probe_zr803_chain.out` | 02:44:10 / 02:44:25 | after freeze |
| **first edit of the four files** (live `isolated_lake.py` W) | **02:53:53** (others 02:54:14–02:54:39) | after freeze ✓ |

- `oracle.md` CreationTime (02:41:58) **< first edit** (02:53:53) — margin 11 min 55 s.
  Before-copies carry inherited LastWriteTime of 09-20 16:23/16:34, i.e. the
  four files had no edit in the 3 days before freeze.
- **Nuance (F-1):** the RED reproduction (02:36:49) and receipt probe
  (02:37:08) ran *before* the freeze, not after. This matches the oracle's own
  text (`Frozen: … pre-edit; RED already reproduced, no fixture/test file
  touched yet`) and commands.md's reproduce-first phasing, so "frozen-first"
  holds for every **edit** and for the family-red/attribution runs; it holds（域：本卡 4 个被编辑文件的时间线）
  for runs only from `red_prep` onward.（域：run 次序按本 attempt 时间线判定）Dispatch wording "CreationTime <
  first edit/run" is therefore satisfied for edits, and satisfied for runs
  except the pre-freeze RED/probe pair that the protocol itself stages first.
- Expectations **(a) root-cause citation, (b) RED, (c) GREEN = gate's exact
  selection, (d) mutation, (e) zero CW writes / stop-condition, (f) no
  bypass** — all six clauses present in `oracle.md` as dispatched（域：oracle.md a–f 六条款）(plus the
  separate zr803 attribution clause).

## 2. Root cause — BOTH cited ends verified live

- **RF end:** `scripts/source_preparation.py:150-156` read live — matches the
  quoted envelope→`not_reviewed`→`RuntimeError` block byte-for-byte.
  Live SHA-256 = `91A6DC32466E9D67B9D034AC345349EE683F6D5FD9486A67CD3ADE009C6EBF4D`
  = the `91a6dc32`-era pin ⇒ untouched by this card.
- **CW gate end:** `company-wiki/src/company_wiki/source_catalog/prompt_injection.py:449-452`
  read live — the C7 `state_domain` fail-closed `return None` is present as
  quoted (docstring `:425-426` also present). Live SHA-256 =
  `88154DE4AB7630606C2545CDCDF9C3AC44FAF32BCAE0F83F33A1CEBC6D490F33`
  = committed merged `88154de4…` (CW `git status --porcelain` shows this file
  **clean**; CW HEAD `5d72529` commit message pins `prompt_injection
  (88154de4)`). Guard twin `prompt_injection_guard.py:201-203` re-read: same
  C7 clause present. Writer contract `prompt_injection.py:118-122` (P5-c dual
  binding MANDATORY), `:313-322` (payload binding), `:343-358` with `:352`
  `"state_domain": STATE_DOMAIN_REVIEW` — all as cited.（域：本节所引 6 处 CW 行号）
- **Resolver default + read path:** `resolver.py:1078`
  (`prompt_injection_status = "not_reviewed"`) and `:1083-1088`
  (`read_prompt_injection_review` → only a non-None receipt（域：resolver.py:1083-1088 代码块）replaces the
  default) — read live, as cited.
- **Eval path:** `filing-fetch/scripts/fetch_filing.py:685-691` spawns
  `[sys.executable, "-m", "company_wiki.source_catalog.cli", …]` — live, as
  cited (path is sibling `Projects\filing-fetch`, not under RF).
  `tests/test_fc1002_three_process_e2e.py:29` — `sys.path.insert(0,
  str(WIKI_ROOT / "src"))` with `WIKI_ROOT = PROJECT_ROOT.parent /
  "company-wiki"` (`:27`) — live, as cited.
- **Live probe re-read:** `evidence/probe_receipt_read.out` (SHA
  `BA9542B1…` = binding pin): fixture receipt keys
  `[evidence_sha256, reviewed_at, reviewer, schema_version, status]` →
  `read_prompt_injection_review -> None` → `not_reviewed`; adding（域：probe 两分支对照）only
  `state_domain: review` → `not_detected`. Single-field proof of the gate,
  exactly as the oracle/decision claim.

**Root-cause clause (a): CONFIRMED on live code, not taken on trust.**

## 3. The four edits — re-hashed, diff independently regenerated, assertions compared

Re-hash live (all match `binding.md`):（域：下表 4 行 pins）

| file | BEFORE (frozen copy) | AFTER (live worktree) |
|---|---|---|
| `tests/e2e_support/isolated_lake.py` | `210FB643…5F1A37` | `867AC82B…AA2883` |
| `tests/test_zr803_chaos_recovery.py` | `B426F774…9655A0B` | `17A4FAEB…285417C` |
| `tests/test_preparation_e2e_success.py` | `1CECA7AB…D95A22C` | `7FA37BD6…628F931` |
| `tests/test_zr709_zijin_journey.py` | `1A4E0B26…D180FA3D` | `2929461B…E1F60D` |

- **Independent `changes.diff` regeneration** (reviewer's own difflib,
  same parameters as `make_diff.py`, written to `%TEMP%`): line content is
  **identical — 0 differing opcodes across 173 lines**; byte-level the file
  differs only by EOL write-mode translation:（域：两份 diff 文件的字节差） their on-disk `changes.diff`
  SHA-256 = `ed5fa8bb…d73cb8e` (CRLF, Windows `write_text` default), my LF
  regen = `cb06a61f…081a7980`, and my LF→CRLF-normalized regen SHA-256 =
  `ed5fa8bb…d73cb8e` = **byte-identical to theirs**. (Known EOL-hash
  sensitivity class — REM-86/CF-I08C-2 precedent; content identity proven by
  reconstruction.)
- **Cross-check vs git (read-only):** changed-line extraction of
  `git diff` (HEAD→worktree) for the four files vs `changes.diff` →
  **106 lines = 106 lines, CHANGED-LINES-IDENTICAL** (after UTF-8 console
  normalization of em-dashes). Consequence: the worktree delta of these four
  files versus HEAD *is* exactly this card's diff — before-copies represent
  the committed pre-state, no smuggled extra hunks.
- **Business assert conditions:** reviewer-extracted（域：4 文件 66 行 assert）every `assert` line in
  before vs after: 66 lines before = 66 after; identical line sets in
  `isolated_lake` (1), `prep_e2e` (8), `zr709` (41); in `zr803` (16 vs 16)
  the **only** delta is the message expression（域：zr803 16 行 assert）
  `assert proc.returncode == 0, proc.stderr.decode("utf-8","replace")[-400:]`
  → `assert proc.returncode == 0, proc.stderr[-400:]` — **condition
  `proc.returncode == 0` byte-identical**, message-only change (diagnostics;
  `run()` uses `text=True` per the card, so `.decode` on `str` raised and
  masked the real chain error).
- **skip/xfail:** `skip|xfail` scan of before vs after in the four files →
  0 occurrences before and 0 after (new lines = 0).
- **Receipt construction vs CW's unit-test writer shape:** CW
  `tests/unit/test_prompt_injection_guard.py` live SHA-256 =
  `D3BDE1A3…23EEC3F` = the pinned `d3bde1a3…`. Its `_write_receipt`
  (`:79-98`) calls
  `record_prompt_injection_review(con, "d1", status=…, reviewer=…,
  evidence_sha256=…, now=…, source_sha256=…, policy_hash=RULESET_HASH,
  evidence_payload=…)` + `commit`. Spot-compare of the three RF call sites in
  `changes.diff`: **argument-for-argument match** of that shape —
  `isolated_lake` (source_sha256 from `sources.content_sha256`, payload =
  `body`), `prep_e2e` (`PDF_SHA`/`pdf_body`), `zr709`
  (`pdf_sha`/`pdf_path.read_bytes()`), each with `policy_hash=RULESET_HASH`.
  `state_domain` is stamped by the writer (`prompt_injection.py:352`) and the
  payload/dual bindings are enforced at write time (`:118-122`, `:313-322`) —
  no hand-shaped dict remains in the four files.

## 4. Counts — RED / GREEN / MUTATION re-verified, plus reviewer's own re-run

- **RED** `evidence/red_raw.txt` SHA-256 = `50B6C2A5…96EE577` ✓ → content:
  `FFFF` + `4 failed in 30.64s` = the 3 fc1002 chain tests with
  `{"error_code":"upstream","error":"prompt injection not reviewed …
  (prompt_injection_status=not_reviewed)"}` rc=3 + zr803 lock masked by
  `AttributeError: 'str' object has no attribute 'decode'` at `:119` —
  matches the dispatch's "4F (3×fc1002 rc=3 + zr803 masked)".
- **GREEN** `evidence/green_raw.txt` SHA-256 = `B161EA33…ECF8F1B` ✓ →
  content: 55 dots + `55 passed in 187.50s`, zero `FAIL/ERROR` markers
  (scan = no matches). Gate selection re-read live:
  `tools/pre_push_gate.py:141-149` `REAL_ROOTS_TESTS` = the same 7 files as
  the oracle quote; `:178-181` command form =
  `[sys.executable, "-m", "pytest", "-q", "--tb=short", *REAL_ROOTS_TESTS]`.
  Reviewer ran `pytest -q --collect-only` on that exact 7-file selection in
  the live worktree → **55 tests collected** ⇒ the 55-passed green raw covers
  the gate's exact selection (nothing else could contribute a test).
- **Reviewer's own re-run (dispatch item 4):**
  `python -m pytest -q "tests/test_fc1002_three_process_e2e.py::test_chain_is_three_real_processes"
  --basetemp=%TEMP%\rf-review-fc1002 --tb=short` → **`1 passed`, exit 0** ✓.
- **MUTATION** `evidence/mutation_raw.txt` SHA-256 = `1C2BA4A4…7B1F1AAE` ✓ →
  content: `4 failed in 26.16s`, fc1002 ×3 with the `not_reviewed` block, and
  **zr803 now showing the REAL unmasked error**
  (`tests\test_zr803_chaos_recovery.py:122: AssertionError: {"error_code":
  "upstream", …not_reviewed…}`) — i.e. pre-edit fixture `210FB643…` restored
  ⇒ red returns, and the message fix demonstrably unmasks. Restore verified:
  live `isolated_lake.py` = `867AC82B…AA2883` = AFTER pin (re-hashed now) and
  `diffs/after/…` copy = same.

## 5. zr803 attribution — reviewer AGREES

Re-read `evidence/probe_zr803_chain.out` (SHA `6C4C083D…` = pin):
`LOCK-HELD: returncode = 3` and `AFTER-RELEASE: returncode = 3`, both with the
byte-identical stderr `{"error_code": "upstream", "error": "prompt injection
not reviewed … (prompt_injection_status=not_reviewed)"}`.

**AGREE with SAME-FAMILY + dependent mask.** Reasons: (1) both legs of the
test's own chain fail identically with the receipt error, so the lock holder
is not causal — the failure is independent of lock state, and identical to
the fc1002 root-cause error ⇒ same family; (2) the `.decode` AttributeError
is *dependent*, not independent:（域：zr803 断言行求值时机）it only evaluates when `returncode != 0`,
and with the receipt fixed the chain returns 0 and the message expression is
never evaluated (mutation arm proves the converse direction: fixture
reverted → unmasked real error appears, still rc=3). It does not reproduce
with the receipt issue absent ⇒ correctly fixed in-scope as diagnostics with
the assert condition untouched; not a flake (2 of 2 legs deterministic).

## 6. Pre-emptive family fixes — reds genuinely pre-existing, green after fix

- Both files are gate real-data members: `pre_push_gate.py:150-161`
  `REAL_DATA_TESTS` contains `tests/test_preparation_e2e_success.py` (`:157`)
  and `tests/test_zr709_zijin_journey.py` (`:158`); `_real_data()` runs at
  `main()` `:271-276`.
- **Pre-existing proof (timestamps, not testimony):**
  `red_prep_e2e_raw.txt` (SHA `499A16C7…`, `1 failed in 7.64s`) written
  **02:42:15** and `red_zr709_raw.txt` (SHA `F5D29AF9…`,
  `1 failed, 8 passed in 13.96s`) **02:42:21** — both **after** the oracle
  freeze (02:41:58) and **before** any edit of those files
  (02:54:14 / 02:54:39; even `isolated_lake.py` not yet edited — first edit
  02:53:53). Their failure content is the same root-cause
  `not_reviewed` upstream block at `test_preparation_e2e_success.py:165` /
  `test_zr709_zijin_journey.py:693`. Manufactured-red would require editing
  the worktree before those runs; the mtimes rule that out.
- **Green after fix:** `green_family_raw.txt` (SHA `E283CF87…`) =
  `10 passed in 28.86s` (= 1 + 9 tests in the two files).
- **Reviewer's own re-run:** `python -m pytest -q
  tests/test_preparation_e2e_success.py --basetemp=%TEMP%\rf-review-prep
  --tb=short` → **`1 passed`, exit 0** ✓.

## 7. No-bypass + boundaries — VERIFIED

- `tools/pre_push_gate.py` live SHA-256 =
  `3DF161A7CEEA17DE95B36845BDB3C4CEE729DCA215C56853868780DCE7331484`
  = pin ⇒ gate untouched (selection, flags, baselines unchanged).
- **CW writes: none during this attempt.**（域：09-23 02:36–03:03 窗口）CW porcelain = exactly 3 dirty
  files (`CLAUDE.md`, `README.md`, `artifact_dag.py` — the dispatched
  "dirty-3") + our commits (HEAD `5d72529` merge carrying `88154de4`);
  all three dirty files have LastWriteTime 02:13:17（域：CW porcelain 3 个脏文件）(before the attempt's
  first logged command at 02:36), and `prompt_injection.py` is clean with
  LastWriteTime 09-22 22:53 (merge time). No CW file inside the attempt
  window 02:36–03:03.
- **No skip/xfail added:** 0 `skip|xfail` markers in the four files before
  and after (section 3). **Host guard re-run by reviewer:**
  `python tools/host_assumption_guard.py --roots tests tools scripts e2e`
  → `violations=24; new(not baselined/registered)=0; baseline=16;
  registered_hashes=3`, exit 0 — matches the card's claim, no baseline
  additions.
- **No git verbs in `commands.md`:** regex scan for
  `git (add|commit|push|checkout|restore|reset|stash|merge|rebase|switch|clean|fetch|pull)`
  → no hits (only the two prose occurrences "No git")（域：commands.md 全文）. The card's own
  operations were file copies + pytest + hashing.
- **Business assertions unchanged** — reviewer's own extraction (section 3),
  independent of the card's `changes.diff` claim.
- RF worktree (read-only `git status --porcelain`): the four card files ` M`,
  plus `.planning/…` register edit, `RF-E2E-ADAPT/` attempt dir (untracked),
  two unrelated untracked items — see F-2 for the fifth modified test file.

## 8. Findings (0 blocking, 4 recorded)

- **F-1 (info, ordering nuance):** RED repro + receipt probe ran *before*
  `oracle.md` freeze (02:36–02:37 vs 02:41:58). Disclosed inside the oracle
  itself and consistent with reproduce-first protocol;（域：本卡时间线）all edits and all
  other evidence runs are after the freeze. No action needed — record the
  exact meaning of "frozen-first" = frozen-before-first-edit.
- **F-2 (provenance flag for parent):** RF worktree carries a **fifth**
  modified test file outside this card's edit set:
  `tests/test_fc905b_trusted_receipt.py` (` M`, +14/−2, SHA
  `DB8BBB48…F19903E1`, LastWriteTime **02:22:04** — before this attempt's
  first logged command 02:36:49; content = "FIX-W06-GAPS P4-SCOPE" verbatim
  sentence pins; `REMEDIATION_REGISTER.md` LastWriteTime 02:22:35 same
  minute, and the register at `:1109` attributes `fc905b` writes to
  FIX-W06-GAPS' authorized test surface). Timestamps place it **outside** this
  attempt; the card's "edits = exactly the 4 files" holds for a20260923-01.
  Parent should confirm that file's commit provenance when committing the
  four card files (it should ride with its own card's commit, not silently
  into batch-5c).
- **F-3 (cosmetic, doc-vs-actual interleaving):** file times show the two
  long GREEN runs started concurrently (~02:56:41: family ended 02:57:10,
  gate-selection green ended 02:59:49) and that `make_diff.py` /
  `changes.diff` (02:56:44/02:57:05) and `decision.md`/`commands.md`
  (02:58:59) were written while the 187 s green run was still in flight —
  `commands.md` presents these as strictly sequential phases.（域：attempt 内 8 份 md 文档）Checked every
  doc's cited result against that doc's write time: **no document claims a
  result that did not exist yet** (green's `55 passed` appears（域：55 passed 字样的出处）only in
  `handoff.md`/`binding.md`, both ≥ 03:01: after green ended 02:59:49 and
  after mutation 03:00:43). Evidence-dependency intact; ordering prose is
  idealized.
- **F-4 (info, EOL):** `changes.diff` on disk is CRLF (Windows text-write
  default); any future byte-pin of it must normalize EOL first (see §3 —
  content identity proven by reconstruction).

## 9. Unverified / residual (agreed with handoff; stays with the gate + CI)

1. Full `pre_push_gate.py` end-to-end, the mypy step, the install-sync step,
   and the other 8 real-data files were **not** re-run by card or reviewer —
   they remain the gate's own item at batch-5c push (dispatch agrees).
2. Receipt freshness (TTL/`evaluate_review`) not exercised by this chain —
   fixtures keep fixed `reviewed_at` (2026-08-12 / 2026-01-01); grep-level
   claim (no chain caller of `evaluate_readiness` today) not independently
   re-proven by the reviewer this round.
3. CI-side verification pending until after the push (self-monitor protocol).
4. Green/mutation raws are single runs; no repeated-run stability check by
   either side (zr803-family flake ruled out（域：本 attempt 2/2 探测腿）only within this attempt's 2/2
   probe legs).

## 10. REM-79 self-check

`python <REM79 attempt>/tools/check_domain_assertions.py` (v1.2.0-correction2,
`execution_runs/REM79-MECHANIZATION/a20260922-01/tools/`) run on this report
with `PYTHONIOENCODING=utf-8` — result recorded in `reviewer_report.sha256`
sidecar (exit code + first-line output).

## Sign-off

Independent review verdict: **ACCEPT** —（域：7 项 dispatch 核验）all seven dispatch verify-items pass
on live re-execution; the four RF test files are root-cause fixes with
byte-identical business assertions, pinned before/after, mutation-proven, and
no bypass markers found in the scanned surfaces. Findings F-1…F-4 are
non-blocking and recorded above. Card signature remains the **parent's** to
apply (reviewer does not self-sign the card); this report is the reviewer's
signature of the review itself.
