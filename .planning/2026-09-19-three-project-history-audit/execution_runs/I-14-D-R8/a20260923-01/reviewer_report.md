# WC-1 / I-14-D-R8 a20260923-01 — independent reviewer report

- card: **WC-1** 「I-14-D r8 残差一轮（REM-06 / REM-67③=R3-05 / R5-08 / R3-07）」 — work card of
  REGISTRY-CLOSURE; attempt `execution_runs\I-14-D-R8\a20260923-01`.
- spec (re-hashed by me): `execution_runs\REGISTRY-CLOSURE\a20260923-01\decision.md` =
  `a68ed77fe922f768a845a6497000de93baab922f1d2128ffe9bbc5727fe79353` / 23413 B — matches
  binding.json `spec.sha256`; §WORK-CARD WC-1 rows **L84-85 read verbatim** (基=iso 复制
  product_narrow_r6 `2f644994…`；oracle 先冻结；①扩数字后缀凭据键族+过度脱敏定价 ②break 后
  值分隔符族 6 形 ③C10 对 marker 载荷行 每仪器一行 ④`both_marker_and_non_marker` 半交付
  补全或改承诺；红绿+变异+双向差集+独立复审).
- reviewer: independent (this report IS the review signature; the implementer stayed
  `implementer_signed: false` — verified in binding.json).
- discipline for THIS review: read/grep/pwsh as the toolset; zero product writes; no state-changing git;
  no network; scratch confined to `%TEMP%\wc1rev_a20260923`; `PYTHONIOENCODING=utf-8`;
  python `-B` + `PYTHONDONTWRITEBYTECODE=1` on each import run.

## VERDICT: **accepted_scoped** (4/4 residuals FIXED/CLOSED with rgm + bidirectional sweeps;
delivery = merge-wave content layer behind the CW-GATE-UNBLOCK-2 split — see COLLISION NOTE)

Scope of this acceptance: the four WC-1 residuals on the two delivery targets, as recorded by
the carriers of this attempt, with the implementer's declared carries passed downstream as
ledger notes (§9). Nothing here lands code: `changes.diff` remains unapplied by design.

---

## 1. What I re-ran myself (method)

Reviewer-generated outputs went to `%TEMP%\wc1rev_a20260923` — the attempt's `evidence\`
and `changes.diff` were treated as read-only.

- 10 instrument re-runs through the card's own harness scripts (4 RED/GREEN + 2 product_base
  direction + 4 mutant) with `--out` under `%TEMP%`; field-by-field comparison against the
  archived JSONs.
- Both bidirectional sweeps re-derived by a FRESH script I wrote in `%TEMP%` (loads
  `iso/r8_base` + `iso/r8_fixed` observability by path; re-implements the frozen domains and
  criteria from oracle.md §5); count-diag re-derived with the card's stated logic.
- Mutants REBUILT from `iso/r8_fixed` by my own `%TEMP%` script (inverse of
  `build_r8.PRODUCT_EDITS`, CRLF-preserving, anchor count==1 asserted) → purity check, then
  4 instrument runs against my rebuilt trees.
- `changes.diff`: independent sha256/size; `git apply --check` + `git apply -p1` on FRESH
  copies of both targets under `%TEMP%` (git used read-only against the real repos — the
  apply ran in scratch); post-apply shas; in-memory `compile()` of both applied files;
  2 instrument runs on my own grafted production tree.
- Pins re-hashed with `Get-FileHash -A SHA256` for: WC-1 spec, r6 tree, production copy,
  product_base, both r6 harnesses, r7 report + sidecar, register, changes.diff, oracle.md +
  sidecar, r8_base/r8_fixed, both r8 harnesses.
- CORRECTION W1 prefix proof re-derived from raw bytes (both reconstructions).
- Hunk-body identity: parsed `changes.diff` into its 2 file sections, compared the 3+3 hunk
  bodies line-for-line.
- Zero-mtime boundary scan (my own, cutoff = attempt-dir creation 2026-09-23 23:29:53) over
  the sealed I-14-D attempt and `company-wiki\src`; `git -C company-wiki status --porcelain`
  (read-only) + production file mtime.
- Register row-level re-verification at review time (L17 / L1665 / L1713 + §七十九).
- REM-79 mechanized check (`execution_runs\REM79-MECHANIZATION\a20260922-01\tools\
  check_domain_assertions.py` v1.2.0-correction2) over this report and, informationally, over
  the implementer's carriers.

## 2. Deliverables check (item 1) — 10/10 present

| deliverable | measured |
|---|---|
| `oracle.md` + `oracle.sha256` | sidecar `cd8b05e0… oracle.md` == my re-hash of the file (19489 B) ✓; freeze-first attested: the pre-run pin `c6cbf869…` is embedded in `build_r8.py` L158 and in the harness it generated (mtime 23:39:56/23:40:05) — BEFORE the first RED run (evidence mtime 23:40:52); CORRECTION W1 appended 23:48 (oracle.md mtime reflects that disclosed append) |
| CORRECTION W1 prefix proof | **re-derived exactly**: marker at byte idx 17998; `data[:17991]` → sha `3e23e74c…` (≠ pin, as recorded); `data[:17991] + LF` (17992 B) → sha `c6cbf8691c838ddb5c0e06d803ebff364dfff8b8870e0e00202ed8bc6e50c16c` == pre-run freeze pin ✓ |
| `binding.json` | parses; `status=review_pending`, `implementer_signed=false`, `disclosure_adaptation=unmapped`, `accuracy=unproven`; carries `oracle_sha256_pre_correction=c6cbf869…`, `changes_diff_sha256=baec3153…`, `register_drift.row_level_verified=true` ✓ |
| `commands.md` | 9 steps incl. each failed attempt with rc + evidence pointers ✓ (§6 lists each) |
| `decision.md` | per-item table (4 rows) + spec citations + frozen-cell matrix audit (9 rows) + diff target table + WC-1 spec sha `a68ed77f…` matched to REGISTRY-CLOSURE decision L84-85 ✓ (I re-hashed and re-read L84-85) |
| `changes.diff` | 9161 B, sha `baec3153e853ae8eb20c7683c5c508d1336559e70d2b61e061ed11cc4e0a6925` == binding + production_apply + final_hashes ✓; **apply --check re-run by me (rc 0)** — §5 |
| `handoff.md` | `review_pending` / `implementer_signed: false` / `disclosure_adaptation: unmapped` / `accuracy: unproven` + r6/r7 lineage (r7 `accepted_scoped`, `cc6da8d3…` pin re-computed by me = sidecar ✓) ✓ |
| `recovery.md` | reproduce block, scratch locations, undo facts, resume point ✓ |
| `evidence\` | **61 files** (my count) incl. `final_integrity.rc.txt` = `rc=0` + verdict pass, `final_hashes.json` (deliverable/harness/evidence sha manifest) ✓ |
| `harness\` | **10 scripts** (matches final_integrity HARIFEST list): freeze_arithmetic, build_r8, build_mutants, sweep×2, diag, make_changes_diff, final_integrity, both run_*_r8 ✓ |

Evidence spot-check (>15 items touched directly): `final_integrity.json`, `final_integrity.rc.txt`,
`final_integrity.stdout.txt`, `final_hashes.json`, `oracle_prefix_proof.json`,
`production_apply.json`, `mutants_build.json`, `key_domain_sweep.json`,
`value_start_sweep.json`, `key_sweep_count_diag.json`, `red_*` (json+rc), `green_*` (json+rc),
`base_*` (json+rc), `mutA_*`/`mutB_*` (4 json+rc), `prodapply_*` (2 json),
`build_r8.stdout.txt`, `build_r8.attempt1_failed_anchor.{stdout,rc}.txt`,
`*_attempt1_loadbug.stdout.txt` ×2, `value_start_sweep.attempt2_orderbug.*`,
`key_domain_sweep.attempt2_countfield.*`, `make_changes_diff.stdout.txt`,
`evidence\README.md` — 18 rc.txt files enumerated and consistent with commands.md.

## 3. Per-item re-verification (item 2) — 4/4 reproduced

### ① REM-06 → **fixed-with-rgm** (K1) — CONFIRMED

- RED on `iso/r8_base` (re-run): oracle **rc 3**, `all_failed` = exactly
  **N14-digit-token2-pair, N15, N16, N17, N18 + N23..N28** (11); `keep_must_failed=[]`;
  rule **rc 3**, fidelity_failures = exactly **5 `cred-digit-*` + 6 `cred-auth-break-*` +
  2 `over-auth-break-*`** = 13; `touched_but_should_not_be=[]`.
- GREEN on `iso/r8_fixed` (re-run): oracle **rc 0**, **61/61**, `registered_open` 7 /
  `registered_open_confirmed` 7; rule rc 3 (§4), `fidelity_ok=true`, 113 rows,
  `credential_leaks=[]`, `touched=[]`, `registered_open_leaking`=7 incl. the marker row.
- **MUT-A**: I rebuilt the mutant from `r8_fixed` (inverse of `const`+`func`) — my tree hashes
  to `9ea513915bede6787a2c300a741ff65ee143a21cb8eefa1dde4abb2d62504621` == the card's recorded
  mutant sha ⇒ the %TEMP% mutant is genuinely "fix reverted". My runs: oracle kills exactly
  **N14-N18 (5)**, rule kills exactly **the 5 `cred-digit-*`**, R3-05 rows stay green ✓.
- **key sweep re-derived** (fresh script): domain **350**, `old_true` 86, `new_true` 200,
  **old\new = []**, **new\old = 114, ⊆ digit-suffixed vocab, near-miss never credential** —
  matches archived `key_domain_sweep.json` cell-for-cell. **count diag re-derived**: expected
  120 (20 vocab × {2,3,12} × 2 cases), actual 114, missing 6 =
  `secret_key2/3/12 × {lower,UPPER}`, each **already old-true** under the OLD predicate
  (`secret` is a single atom ⇒ `secret_key2` split part `secret` matches pre-fix), `extra=[]`
  ⇒ 120−114=6 fully explained, verdict "all missing keys were ALREADY true".
- over-redaction price counters: `untouched-oauth2/monkey2/secretary2/tokenizer2` rows are
  fidelity-OK and `touched_but_should_not_be=[]` on **each measured tree** (r8_base,
  r8_fixed, product_base, MUT-A, MUT-B); oracle N19-N22 keep_must green on each tree
  (`keep_must_failed=[]` in all 10 runs).

### ② R3-05 → **fixed-with-rgm** (K2, code fix — registered_open alternative NOT taken per
parent standing order 「发现的缺陷都要全部修复」) — CONFIRMED

- RED: oracle the same 11 (N23-N28 ⊆ failures with credential left in the clear after the
  break — measured `Authorization: <redacted>\n,<S39>` etc.); rule 6 `cred-auth-break-*` +
  2 `over-auth-break-*` among the 13.
- GREEN: N23-N28 closed; **N29 single-line guard green** (keep_must) on each tree; the
  pre-existing quoted rows (N5k, `cred-auth-quoted-continuation`, R3b declaration) stay green.
- **MUT-B**: rebuilt by me (`auth` inverse) → sha
  `8217f10026fd846a014d42c7d2bf5734c6cb2a14d12a05536f0bd64213775931` == recorded; my runs kill
  exactly **6 oracle (N23-N28) + 8 rule (6 form rows + 2 pricing rows)**, REM-06 rows green ✓.
- **value sweep re-derived** (fresh script, 95 printable ASCII 0x20-0x7E at
  `Authorization: Bot\n<c><S39>`): `closed_old` 89, **`closed_new` 95/95**,
  **old\new = []**, **new\old = exactly `{",", ";", "&", "|", "\"", "'"}`** — matches
  archived `value_start_sweep.json` ✓.
- frozen scope held: the new alternative applies after the break (N29 pins the single-line form unchanged);
  value-start `\r \v \f` declared OUT of this row set (oracle 1/4a — carried-open, §9);
  delimiter+space declared open (oracle 1/4a); quoted alternatives first (byte-identical
  terminated-quote behaviour re-confirmed by N5k/N5l/N5m/R3b green).

### ③ R5-08 → **fixed-with-rgm (record-level)** — CONFIRMED

- Marker-payload row exists on **each instrument**: rule
  `open-two-token-then-wrap-marker`, oracle `R3c-two-token-then-wrap-marker`, input
  `Authorization: Bearer abc\n<M>`, kind `registered_open`, declaring
  `Authorization: <redacted>\n<M>`.
- My GREEN re-run: rule `registered_open_rows` = 7 and `registered_open_leaking` = 7 **incl.
  the marker row**; oracle `registered_open` = 7 / `registered_open_confirmed` = 7 (R3c
  confirmed); **`credential_leaks=[]` remains readable alongside** `registered_open_leaking`
  (the design point: the two lists answer different questions — oracle 4c domain).
- Declaration pinned by fidelity (a behaviour flip turns the row red — visible in RED/GREEN);
  disclosed base-regression matches the r7 precedent: on product_base R3c is
  registered_open but **NOT confirmed** (`registered_open_confirmed = [R3b] only` in my
  direction re-run) — disclosed, not hidden.

### ④ R3-07 → **closed-now-with-proof** (「补全」 branch, no code of its own) — CONFIRMED

- Before-state = the frozen r3 measurement: `reviewer_report_r3.md` L465-474 read verbatim —
  `open-two-token-then-wrap` and `open-quoted-two-token` each contain the 39-char credential
  and **neither** contains `SYNTHETIC_AUDIT_TOKEN` (L468-469).
- After ③: C10 residual family carries **both credentials in both instruments**, measured by
  my runs — rule family rows `open-two-token-then-wrap` (S39) + `open-two-token-then-wrap-marker`
  (M) both in `registered_open_leaking`; oracle `R3a` (S39) + `R3c` (M) both in
  `registered_open_confirmed` (7/7). This satisfies the reviewer's own family-level standard
  from L471-473 (marker rows + non-marker rows in the main family).
- Sealed carrier untouched: `handoff_r3.json` = 9788 B, sha
  `3e9648c88bd97379f2eebb8ddd1b6fadfb585b5beed79ccdad8219c3240e02fe`, **mtime 2026-09-22
  00:28:52** (≈1.5 days before this session) ⇒ zero re-write; the completion + asymmetry note
  live in this card's oracle.md 4d.
- R3b marker-twin asymmetry **declared** (oracle 4d + decision §5.4): R3b has no dedicated
  marker twin because spec froze ③ as 每仪器一行 — carried-open, §9.

### Field-level equivalence of my re-runs vs archived evidence

The **10** archived-vs-rerun JSON pairs are IDENTICAL field-for-field except the expected
`src`/`label` paths: `red_oracle`, `red_rule`, `green_oracle`, `green_rule`, `base_oracle`,
`base_rule`, `mutA_oracle`, `mutA_rule`, `mutB_oracle`, `mutB_rule`. The archived sweeps match
my fresh re-derivations, cell for cell.

## 4. Counts + rc semantics (item 3) — verified

- rule table **95 → 113**, oracle **44 → 61**: re-counted by importing both harness pairs —
  r6: 95/44; r8: 113/61; the r8 row lists minus the 18/17 new ids are **tuple-identical** to
  the r6 lists (pre-existing rows byte-untouched) ✓.
- `iso/r8_fixed` oracle re-run: **rc 0, verdict `pass`, 61/61, registered_open 7/7** ✓.
- rule instrument stays **rc 3 / verdict `negative` BY DESIGN since r3** (`fidelity_ok=true`,
  `credential_leaks=[]`, `touched=[]`; rc 3 is driven by the declared `registered_open`
  secret leaks — F-REV-R6-04 disclosure rule). **Grep across the 6 carriers found NO rc0-claim
  for the rule table**: each "rc 0" mention pairs with the ORACLE (decision L38
  `oracle rc0/61 + rule fidelity_ok/113`; commands L88 same pairing) and decision L40 /
  oracle L139 explicitly disclaim an rc-0 claim for the rule ✓.
- product_base direction: `keep_must_failed=[]`, the frozen 11 (N14-N18+N23-N28) ⊆
  `narrow_must_failed` (31 = the frozen 11 + the pre-existing narrow rows that are red on base
  by definition), N19-N22+N29 green, R3c registered_open-not-confirmed = **disclosed
  base-regression**; rule direction run rc 3 with `touched=[]` and no rc/pass claim ✓ — my
  re-run is field-identical to `base_*` evidence.

## 5. changes.diff content (item 4) — verified

- 9161 B / `baec3153…` (my re-hash) — **6 hunks** = K1 (const + func) + K2 (auth) × both
  targets: `--- a/iso/product_narrow_r6/src/company_wiki/source_catalog/observability.py`
  (3 hunks) and `--- a/src/company_wiki/source_catalog/observability.py` (3 hunks) ✓.
- **Hunk bodies byte-identical across the two targets** (my parse+line-diff: 3/3 pairs equal,
  8/25/22 lines) ✓.
- Production target before = **re-hashed live file** `edcbeccb9b13778efe2d80c58a401c345856bf04220462e1fbbe56ea96111f4e`
  / **43707 B** == binding's pin ✓; r6 target before = `2f644994…` / **43746 B** ✓ (I copied
  these exact files into scratch as the apply base).
- **`git apply --check` rc 0, `git apply` rc 0** on my scratch copies → after-shas
  `90b3fdc3…`/45774 (r6 target; == `iso/r8_fixed` sha) and `081fdf5e…`/45735 (production
  target) — equal to the claimed after-values in decision/production_apply/final_hashes ✓.
- in-memory `compile()` of both applied files + `iso/r8_fixed` observability: OK (no .pyc
  written) ✓.
- **production NOT written by this card**: live file mtime **2026-09-22 22:22:42** (before
  session start 2026-09-23 23:29:53); `git -C company-wiki status --porcelain` shows 3 dirty
  files from other actors (CLAUDE.md, README.md, artifact_dag.py) with
  `src/.../observability.py` **clean/absent** ⇒ working tree observability == HEAD ==
  `edcbeccb…` ✓.
- **grafted %TEMP% two-instrument GREEN**: the card's `production_apply.json`
  (oracle rc 0/61 + rule fidelity_ok/113, `green_match_with_r8_fixed: true`) **independently
  reproduced by me**: full copy of production `src` + my applied observability
  (`081fdf5e…`) → oracle **rc 0 / pass / 61/61 / open 7 confirmed 7**; rule **rc 3 negative,
  fidelity_ok true, 113, credential_leaks [], touched [], open 7/7** ✓. (My first attempt used
  a too-minimal graft without `__init__.py` and imported an installed package — reviewer-side
  method note, not a card defect; redone properly as above.)
- Harness write-target audit: `make_changes_diff.py` confines its writes to scratch + `changes.diff` +
  `evidence/production_apply.json`; production handled in memory (`production_file_written:
  false`) — consistent with the observed production state ✓.

## 6. Disclosures (item 5) — each located and verified

1. **build attempt 1 (anchor name, rc 1)** → commands.md Step 3 + 
   `evidence/build_r8.attempt1_failed_anchor.{stdout,rc}.txt` (rc=1; stderr shows the anchor
   assert firing on the r6 rule harness with the oracle-harness constant names; guard
   semantics = nothing half-written) ✓.
2. **sweep attempt 1 loadbug** → commands Step 8 +
   `evidence/key_domain_sweep.attempt1_loadbug.stdout.txt` + 
   `value_start_sweep.attempt1_loadbug.stdout.txt` (dataclass `_is_type` tracebacks; tooling,
   module-load path) ✓.
3. **sweep attempt 2 orderbug** → commands Step 8 +
   `evidence/value_start_sweep.attempt2_orderbug.*` (rc 3, verdict FAIL with the SAME six
   chars — list-vs-set comparison) ✓; final criterion is set-based with criterion text
   unchanged.
4. **key-sweep count field** → `evidence/key_domain_sweep.attempt2_countfield.*` (rc 0 with
   `expected_new_minus_old_count:120` inside `criteria`) + `key_sweep_count_diag.json`
   explanation ✓ (re-derived in §3①).
5. **CORRECTION W1** → oracle.md L219-237 (append-only block), decision §matrix ⚠ row +
   §4.5, binding `oracle_sha256_pre_correction` + `oracle_correction`; prefix proof verified
   by me (§2): one mis-forecast cell (§3 r8_base `credential_leaks` predicted `[]`, measured
   `[cred-digit-password2, cred-digit-api-key2]`), instrument correct, row expectations and
   the remaining frozen cells unchanged (my RED re-run reproduces the measured value) ✓.
6. **prefix-proof attempt 1 miss** → commands Step 9 + `oracle_prefix_proof.json` retains
   both reconstructions (without-LF mismatch; with-LF match) ✓ — I reproduced both numbers.
7. **binding Set-Content no-op** → commands Step 9 (first rewrite attempt failed, no-op;
   rewritten via JSON load/dump; file parses and carries both pins) — parse re-checked by me ✓.
8. **final_integrity iterations** → commands Step 9 (attempt 1 rc 1 path-depth bug; attempt 2
   rc 3 midnight-cutoff misattribution; attempt 3 label fix; final rc 0) +
   `final_integrity.rc.txt`=`rc=0` + stdout verdict `pass` ✓.
9. **External drift (register + concurrent REGISTRY reviewer)** → decision §4.8 + binding
   `register_drift` — see §7.

## 7. Integrity + boundary (item 6) — re-verified

**final_integrity rc 0 / verdict pass** recorded; I re-computed the pins myself:

| pin | expected | my measurement |
|---|---|---|
| production `observability.py` | `edcbeccb…` / 43707 | **match** (also == HEAD per porcelain) |
| r6 generation tree | `2f644994…` / 43746 | **match** |
| product_base | `c5608c4b…` / 40060 | **match** |
| r7 report + sidecar | `cc6da8d3…` | **match** (sidecar re-read) |
| WC-1 spec decision | `a68ed77f…` / 23413 | **match** |
| changes.diff | `baec3153…` / 9161 | **match** |
| r6 harnesses | `85a1b064…` / `8f5feffd…` | **match** (frozen bases of the r8 row extension) |
| r8_base / r8_fixed | `2f644994…` / `90b3fdc3…` | **match** |
| r8 harnesses | `ad7861ee…` / `ffe3372b…` | **match** |
| oracle.md / sidecar | `cd8b05e0…` | **match** (+ pre-correction pin reproduced) |

**My own boundary scans** (cutoff = attempt-dir creation 2026-09-23 23:29:53): sealed
I-14-D attempt = **0 files** with mtime ≥ cutoff; `company-wiki\src` = **0 files** with
mtime ≥ cutoff — the implementer's `zero_write_ok=true` claim holds at review time.

**EXTERNAL drifts (not this card) — row-level re-verified by me:**

- `REMEDIATION_REGISTER.md` freeze pin `5348278f…`/218750 B; card's decision §4.8 cites
  close-time `accddcc3…`/228888; final_integrity (00:04) measured `5a9b8737…`/232018; my
  review measured `72e044d9…`/237713 and, minutes later, `bd83a61f…`/243062 — parallel cards
  keep appending (see finding F-1). Cited rows **present verbatim NOW**: **L17** (REM-06 row
  with `token2/secret2/password2/api_key2` text), **L1665** (WORK-CARD WC-1 routing row),
  **L1713** (WC-1｜I-14-D r8 残差轮 with `iso 基=product_narrow_r6(2f644994…)`); new
  **§七十九 exists at L1575** = the other card's section ✓ (register now 1977 lines).
- REGISTRY-CLOSURE concurrent reviewer: `reviewer_report.md` (19887 B, 23:54:03) +
  `.sha256` exist in the spec attempt ✓ — matches final_integrity's 2 external hits; our SPEC
  file there is content-pinned (`a68ed77f…` still matches at review time).

## 8. COLLISION NOTE (parent-adjudicated — transcribed for the executor)

- **Collision**: this card's `changes.diff` targets
  `company-wiki src\company_wiki\source_catalog\observability.py`, which
  **CW-GATE-UNBLOCK-2 is ALSO refactoring** — I confirmed on disk: its attempt
  (`execution_runs\CW-GATE-UNBLOCK-2\a20260923-01`) has its own `changes.diff` (66831 B)
  whose headers include `--- a/src/company_wiki/source_catalog/observability.py`, and its
  decision.md records **RC-2b: `observability._redact_assignments` complexity 27 → 6
  (split DONE, max 6)** with ratchet/mutation evidence.
- **Parent ruling (merge sequence) — transcribed as adjudicated**:
  1. **CW-GATE-2 split diff lands FIRST**;
  2. **then WC-1's K1/K2 content is re-based into the split structure** (mechanical
     re-anchor of the 3 hunks onto the post-split function layout);
  3. **then complexity is re-measured** — WC-1 content bumps = targeted re-split if needed;
  4. **→ final ratchet test green.**
- **Recorded dependency for the executor**: WC-1's hunks are **written against the
  PRE-SPLIT** `observability.py` (both targets, verified byte-identical bodies §5) — a
  **mechanical re-anchor is REQUIRED** when landing after CW-GATE-2; do not apply this
  `changes.diff` verbatim onto a post-split file. WC-1 content itself (K1 key predicate region
  ~L254-264, K2 `_AUTH_SCHEME_SPLIT` region ~L329-343) precedes the dead line at r6 L400 and
  is independent of the split helpers, so re-anchoring is expected to be mechanical; complexity
  re-measurement at step 3 is the backstop.

## 9. Scope-if-accepting + carried (ledger notes)

- **Accepted scope**: 4/4 residuals FIXED/CLOSED with rgm (red/green/mutation evidence) +
  REM-79-style bidirectional sweeps, reproduced by this review; `changes.diff` = the
  **merge-wave content layer**, landing post CW-GATE-2 split with the re-anchor disclosed in
  §8.
- **I-14-C real-exit pytest suite**: non-goal carried (it would spawn the product test dir
  under company-wiki — production-write risk); run it in the promotion batch that lands K1/K2.
- **Declared-open items (from the implementer's own declarations — ledger notes, not
  blockers)**: (a) R3b marker-twin asymmetry (oracle 4d); (b) value-start `\r \v \f` after the
  break; (c) delimiter+space; (d) single-line delimiter values (N29 pins current behaviour);
  (e) `changes.diff` unapplied — landing awaits the owner's promotion/repair batch;
  (f) WC-2..WC-6 untouched (REM-07 swallow, REM-17 negatives, F12, REM-79 tooling WC-5,
  REM-95).
- Status after this report: implementer carriers remain `review_pending`/unsigned as written;
  this report is the reviewer's verdict record (binding.json left untouched by me — status
  flip is a bookkeeping step for the parent/owner).

## 10. Findings (reviewer-numbered)

- **F-REV-R8-01 (INFO, bookkeeping)** — decision.md §4.8 states the register's close-time
  drift as `accddcc3…`/228888 B, while final_integrity.json (run ~4 min later) records
  `5a9b8737…`/232018 B; my review measured two further external states (`72e044d9…`/237713,
  then `bd83a61f…`/243062). Each value is an external parallel append (this card's command log
  contains no register write), and **row-level verification holds at each measurement point**
  — the discrepancy is measurement-timing bookkeeping, not a correctness defect.
- **F-REV-R8-02 (INFO, bookkeeping)** — REM-79 mechanized scan (v1.2.0-correction2) over the
  implementer's 4 main carriers flags **34 lines** (oracle.md 14, decision.md 7, commands.md
  10, handoff.md 3) — prose universal-quantifier lines lacking a same-line domain qualifier.
  Calibration: the reviewed spec card REGISTRY-CLOSURE's carriers carry 1 such hit and passed
  review; the standing treatment is REM-94 / append-only domain-qualifier repair as
  bookkeeping (register L1456/L1494). Treated as carried bookkeeping here — **not** a gate for
  this card's residual verdicts. **This reviewer's own report passes the same checker with 0
  violations** (§12).
- **F-REV-R8-03 (INFO, minor)** — the two attempt-1 sweep runs archived just their stdout
  (`*_attempt1_loadbug.stdout.txt`) with no paired `.rc.txt`; their rc=1 is recorded in
  commands.md prose alone. Each of the other runs has a `.rc.txt`. Archive-consistency nit; the
  tracebacks themselves are retained.
- **F-REV-R8-04 (INFO, tooling)** — `build_r8.py` reports `"newline": nl.strip("\r")`, which
  prints `"\n"` for BOTH LF and CRLF targets; the r6/r8 observability files are in fact
  **CRLF** (937 CRLF lines — I hit this when rebuilding mutants: literals need
  `old/new.replace("\n", nl)`, exactly as `build_mutants.py` does). Content shas remain the
  real pins, so no claim is affected; the field is lossy and could mislead a future
  reproducer.
- **F-REV-R8-05 (INFO, positive)** — freeze-first has a timestamped anchor beyond the prose:
  the pre-run oracle pin `c6cbf869…` is embedded in `build_r8.py` (mtime 23:39:56) and in the
  harness it generated (23:40:05), both BEFORE the first SUT run (23:40:52), and the
  post-RED append (23:48) is prefix-proved against that pin.

## 11. Unverified / not run by this review

1. **`build_r8.py`, `build_mutants.py`, `make_changes_diff.py`, `final_integrity.py` were not
   re-executed verbatim** — their outputs target the attempt's `evidence\`/`changes.diff`,
   which my write boundary forbids. Equivalent coverage substituted: independent mutant
   rebuild (hash-identical), independent prefix proof, independent diff parse + `git apply`
   on scratch copies, independent pin re-hash + boundary scans, field-identical re-runs of the
   10 instrument jobs.
2. **"make_changes_diff run twice, byte-identical"** — the two-run determinism claim is
   historical; I verified the artifact sha + independent reproducibility of the after-states,
   which is the claim's substance.
3. **I-14-C real-exit pytest suite** — not run (declared non-goal; carried).
4. **r6/r7 lineage depth** — verified by pins (tree, harnesses, r7 report = sidecar,
   counts 44/95) and by row-list tuple-identity; I did not re-adjudicate the r7 review's own
   findings.
5. **Register byte-history between freeze (218750) and close** — not reconstructable
   (external parallel appends); accepted under row-level verification as the card did.
6. **CW-GATE-UNBLOCK-2 landing status** — its decision.md still marks the observability split
   row ⏳ re-verify+mutation at review time; the §8 sequence starts once its diff lands.
7. **Landing/production application of `changes.diff`** — out of scope for both implementer
   and reviewer (delivery-only discipline).

## 12. REM-79 self-check (mechanized)

`python REM79-MECHANIZATION\a20260922-01\tools\check_domain_assertions.py reviewer_report.md`
with `PYTHONIOENCODING=utf-8` → **0 violations, rc 0** (tool v1.2.0-correction2, stdlib,
read-only).

---

**Signed: independent reviewer, 2026-09-24.** Verdict `accepted_scoped` per §VERDICT with
findings F-REV-R8-01..05 and carries §9. Sidecar: `reviewer_report.sha256`.
