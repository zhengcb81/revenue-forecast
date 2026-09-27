# WC-1 / I-14-D-R8 decision — per-item disposition table

- card: **WC-1** 「I-14-D r8 残差一轮（覆盖 REM-06 / REM-67③ / R5-08 / R3-07）」
- spec (authoritative input): `execution_runs\REGISTRY-CLOSURE\a20260923-01\decision.md`
  §WORK-CARD WC-1, L84-85 — sha256 `a68ed77f…fe79353` (recomputed by this card; equals
  REGISTRY-CLOSURE's own `binding.json.decision_sha256`).
- attempt: `execution_runs\I-14-D-R8\a20260923-01`｜NINE-STEP executed to `review_pending`
  (isolation + oracle-frozen-first + independent review pending + zero production merge).
- status of every verdict below: **proposed by the implementer, authority = the independent
  reviewer**; this card expresses no acceptance.

## 1. Per-item verdicts

| # | residual (citations) | disposition + fix site | verdict | judged evidence |
|---|---|---|---|---|
| ① **REM-06** | register L17 「`token2/secret2/password2/api_key2` 不是凭据键…」修法「补 rule-table 行 + 扩展凭据键集合」; WC-1 spec L85 clause ①; reviewer F-REV-D-03 (`I-14-D/reviewer_report.md` L305-318: `key_is_credential("token2") == False …`); A2 row (REGISTRY-CLOSURE decision L15: 「当前态实测未修…live probe `token2` 明文留存」) | **code fix (K1)**: `key_is_credential` strips each split component's trailing digit run before the atom-table lookup (+ `_KEY_TRAILING_DIGITS`); single AND pair families resolve through the unchanged split rules. 5 rule rows + 5 oracle rows + 4 untouched counter rows per instrument (过度脱敏定价). changes.diff hunks K1 × 2 targets | **fixed-with-rgm** | RED r8_base: exactly N14-N18 (oracle) + 5 `cred-digit-*` (rule) red (`evidence/red_*`); GREEN r8_fixed: 61/61 rc0 + 113 fidelity_ok (`evidence/green_*`); **MUT-A** (fix reverted) kills exactly those 5+5 rows, nothing else (`evidence/mutA_*`); key sweep **old\new = ∅**, new\old = 114 ⊆ digit-suffixed vocab (`evidence/key_domain_sweep.json`, count delta audited in `key_sweep_count_diag.json`: `secret_key2/3/12` were already old-true because `secret` is a single atom); counters monkey2/oauth2/secretary2/tokenizer2 untouched on every tree (`touched_but_should_not_be=[]` in all runs) |
| ② **R3-05 = REM-67③ = F-REV-R3-05** | `reviewer_report_r3.md` L448-454: 「`Authorization: Bot\n,<secret>`, `\n;`, `\n&`, `\n|`, `\n"`, `\n'` all leave the credential in the clear… Recorded for… the next row set」; A10③ row (L24 → routed into WC-1); WC-1 spec L85 clause ② 「补行——修脱敏或按 C10 先例 `registered_open`（须域内声明）」 | **code fix (K2)** — the `registered_open` alternative was available but NOT taken, per parent standing order 「发现的缺陷都要全部修复」: `_AUTH_SCHEME_SPLIT` gains a third after-break value alternative `[,;&|"']*` + unchanged `_AUTH_BARE_VALUE`, **quoted alternatives tried first** (terminated quotes byte-identical). Scope frozen (oracle 1/4a): after-break only, delimiter IMMEDIATELY followed by token; single-line `Authorization: Bot,<secret>` unchanged (N29 pins it); value-start `\r \v \f` out of set. 6 rule + 6 oracle rows + 2 over-redaction pricing rows. changes.diff hunks K2 × 2 targets | **fixed-with-rgm** | RED r8_base: exactly N23-N28 + 6 `cred-auth-break-*` + 2 `over-auth-break-*` red; GREEN r8_fixed all green incl. N29 scope guard + every pre-existing quoted row (N5k, `cred-auth-quoted-continuation`, R3b declaration); **MUT-B** (fix reverted) kills exactly those 8 rule rows + 6 oracle rows, REM-06 rows stay green (`evidence/mutB_*`); value sweep over 95 printable ASCII: **old\new = ∅**, **new\old = exactly {`,` `;` `&` `\|` `"` `'`}`** (`evidence/value_start_sweep.json`); over-redaction cost priced by the 2 `over-auth-break-*` rows |
| ③ **R5-08 = F-REV-R5-08** | `reviewer_report_r5.md` L534-554: 「`credential_leaks == []` does not see the marker form of the registered two-token shape … Worth one row on each instrument」; C10f row (REGISTRY-CLOSURE L60); WC-1 spec L85 clause ③ 「C10 对（R3a/R3b）补 marker 载荷行（每仪器一行）」 | **row-add (record)**: exactly one marker-payload row per instrument — rule `open-two-token-then-wrap-marker`, oracle `R3c-two-token-then-wrap-marker` — input `Authorization: Bearer abc\n<M>`, kind `registered_open`, declaring the exact leak `Authorization: <redacted>\n<M>` | **fixed-with-rgm (record-level)** | the marker form is now visible on both instruments: rule `registered_open_leaking` includes the marker row (7 rows, `evidence/green_rule_r8_fixed.json`); oracle `registered_open`/`registered_open_confirmed` include R3c (7/7, `evidence/green_oracle_r8_fixed.json`); declaration pinned by fidelity (a behaviour change flips the row red — RED/GREEN runs demonstrate the pin); disclosed base-regression of the declaration matches the r7 precedent (on `product_base` the row is unconfirmed because base collapses the input — `evidence/base_*`) |
| ④ **R3-07 = F-REV-R3-07** | `reviewer_report_r3.md` L465-474: 「`both_marker_and_non_marker` promises two things; the registered-open rows deliver one … neither contains `SYNTHETIC_AUDIT_TOKEN` … the key name over-promises」; C9b row (L50); WC-1 spec L85 clause ④ 「补全或改承诺」 | **closed by ③ completion (「补全」 branch)** — NO code of its own: after ③ the C10 residual family = {R3a `S39`, R3b `S39`, R3c marker} carries BOTH credentials in BOTH instruments, which is the reviewer's own family-level standard from the same paragraph (L471-473: for the main family 「there are marker rows and non-marker rows」 suffices). The sealed carrier `handoff_r3.json` key text is NOT edited (封存载体零回改); the completion + its asymmetry note live in oracle.md 4d (this card's carrier) | **closed-now-with-proof** | before = the frozen r3 measurement (neither C10 row carries `M`); after = R3c carries `M`, measured present in both instruments (`green_rule…registered_open_leaking`, `green_oracle…registered_open_confirmed`). **Declared residual of this closure** (not hidden): R3b's quoted variant has no dedicated marker twin — spec froze ③ as 每仪器一行 (one row per instrument); recorded in oracle.md 4d |

**Counts**: rule table 95 → **113** rows (95 pre-existing byte-untouched + 18 new); oracle 44 →
**61** cases (44 pre-existing untouched + 17 new). Harness logic otherwise byte-identical to the
r7-frozen r6 harnesses (pins `85a1b064…` / `8f5feffd…` re-verified before extension).

## 2. Frozen-cell matrix audit (freeze → measured)

| frozen cell (oracle.md) | measured | ok |
|---|---|---|
| §2 r8_base RED = exactly N14-N18 + N23-N28 (11); keep rows green; R3c green | `red_oracle_r8_base.json`: all_failed = those 11; keep_must_failed `[]`; R3c confirmed | ✅ |
| §2 r8_fixed: 61 cases rc 0 `pass`; registered_open 7/7; both failed-lists `[]` | `green_oracle_r8_fixed.json` exact | ✅ |
| §2 product_base: N14-N18 + N23-N28 red; N19-N22 + N29 green; R3c red (disclosed) | `base_oracle_product_base.json`: keep_must_failed `[]`, those 11 in narrow_must_failed, R3c in registered_open but NOT confirmed | ✅ |
| §3 r8_base: 113 rows; fidelity_failures = the 13 fixed-behaviour rows; touched `[]`; registered_open 7/7; negative rc 3 | `red_rule_r8_base.json` exact | ✅ |
| §3 r8_base `credential_leaks` `[]` | measured `[cred-digit-password2, cred-digit-api-key2]` — **FORECAST CELL WRONG**, instrument correct → **CORRECTION W1** (append-only; prefix proof `evidence/oracle_prefix_proof.json` matches the pre-run pin) | ⚠ corrected |
| §3 r8_fixed: fidelity_ok true; credential_leaks `[]`; touched `[]`; registered_open 7/7; negative rc 3 by design | `green_rule_r8_fixed.json` exact | ✅ |
| §6 MUT-A kills exactly the REM-06 rows; MUT-B exactly the R3-05 rows | mutA rule failures = 5 `cred-digit-*` / oracle = N14-18; mutB rule = 6+2 / oracle = N23-28 | ✅ |
| §5a key sweep old\new ∅, new\old ⊆ digit vocab | `key_domain_sweep.json` pass | ✅ |
| §5b value sweep old\new ∅, new\old = six forms | `value_start_sweep.json` pass (95/95 closed after fix) | ✅ |
| production target: edits land 1:1, compile, GREEN identical | `production_apply.json`: 3/3 edits, py_compile ok, oracle rc0/61 + rule fidelity_ok/113, `green_match_with_r8_fixed: true` | ✅ |

No rc 0 is claimed anywhere for the rule table: its rc stays 3 / verdict `negative` BY DESIGN
since r3 (F-REV-R6-04 disclosure rule in force — registered_open rows leak as declared).

## 3. changes.diff — genuinely-changed files (complete list)

One source file × two delivery targets = **6 hunks** (3 per target), `changes.diff` 9161 B /
sha256 `baec3153e853ae8eb20c7683c5c508d1336559e70d2b61e061ed11cc4e0a6925`:

| target | path header in diff | before sha256 | after sha256 | before→after bytes |
|---|---|---|---|---|
| r6 generation tree | `a/iso/product_narrow_r6/src/company_wiki/source_catalog/observability.py` | `2f6449949c76b97c636d5d50e2ca848403116a85a1858bb9ba8f5a2808362464` | `90b3fdc39ddc3b90395df459f298ce3bcb652bbb4f54542bb6f8060657d1cce0` | 43746 → 45774 |
| production company-wiki | `a/src/company_wiki/source_catalog/observability.py` | `edcbeccb9b13778efe2d80c58a401c345856bf04220462e1fbbe56ea96111f4e` | `081fdf5ee002f26415050adbdf0de4e8478712e282f5a9ea80c547159afc65f0` | 43707 → 45735 |

- production = r6 tree minus one dead line (r6 L400 `quote = text[value_start]`, 39 B); both fix
  regions precede it and are byte-identical across targets → one hunk body per region applies to
  both (verified: 3/3 literal edits landed once each; grafted `%TEMP%` tree ran both instruments
  GREEN — `evidence/production_apply.json`).
- NO other file changed: no harness file of the sealed predecessor, no test file, no config.
  The two r8 harness row-lists are NEW files in this attempt (carriers, not product diffs).
- Application: not applied by this card (sources read-only / production writes ZERO); landing =
  a later promotion/repair batch under the owner's standing rule.

## 4. Disclosures (hiccups, all retained raw)

1. **build attempt 1 failed** on a row anchor: the rule harness names its constants
   `MARKER`/`REVIEWER_SECRET`, my anchor used the oracle harness's `M`/`S39` → anchor assert
   fired, nothing half-written (`evidence/build_r8.attempt1_failed_anchor.*`). Fix: corrected
   anchor + row names; build re-run clean (`evidence/build_r8.rc.txt` = rc 0).
2. **sweep attempt 1**: module loaded by path without `sys.modules` registration → dataclass
   `_is_type` AttributeError (tooling, not SUT) — tracebacks kept
   (`evidence/*_attempt1_loadbug.stdout.txt`); fixed by registering the module before exec.
3. **sweep attempt 2**: value-sweep criterion compared lists, freeze defines a SET → order-only
   false FAIL (same 6 chars) — kept (`evidence/value_start_sweep.attempt2_orderbug.*`);
   comparison made set-based; criterion text unchanged.
4. **key-sweep count field**: naive 120 vs measured 114 — every missing key
   (`secret_key2/3/12` × case) was ALREADY credential-true on the old predicate (`secret` is a
   single atom) and is therefore correctly absent from new\old — audited in
   `evidence/key_sweep_count_diag.json` (verdict: fully explained).
5. **CORRECTION W1** (oracle append): one mis-forecast cell (§3 r8_base `credential_leaks`),
   corrected append-only with byte-proof of the untouched pre-run prefix; pre-correction pin
   retained in `binding.json.oracle_sha256_pre_correction`.
6. First prefix-proof attempt missed the original trailing LF (rc 3) → second attempt tested
   both reconstructions and matched `prefix + LF` exactly (`evidence/oracle_prefix_proof.json`).
7. `binding.json` first update attempt failed (`Set-Content -Raw` is not a parameter) → no-op;
   rewritten through a JSON load/dump; file parses and carries both pins.
8. **External input drift during this card (disclosed, not caused)**: `REMEDIATION_REGISTER.md`
   was appended by a PARALLEL card while this card ran (freeze pin `5348278f…`/218750 B →
   live `accddcc3…`/228888 B at close; the new §七十九 belongs to that other card, not to
   REGISTRY-CLOSURE's planned section). This card's command log contains no register write;
   accepted under ROW-LEVEL verification — every register row this card cites (L17 REM-06,
   L1665, L1713 WC-1) re-verified present verbatim (`evidence/final_integrity.json`
   → `register_drift.cited_rows_present_verbatim`). Likewise the REGISTRY-CLOSURE attempt
   received its own `reviewer_report.md` at 23:54 (concurrent reviewer of the spec card) —
   our SPEC there is content-pinned (`a68ed77f…` still matches). Zero files under the sealed
   I-14-D attempt or company-wiki/src carry an mtime at/after this attempt's creation
   (23:29:53); pre-cutoff same-day mtimes in those roots belong to earlier actors (r6 tree
   `__pycache__/observability…pyc` 22:41, three unrelated company-wiki modules) — none of
   them this card's commands, all pinned inputs content-verified unchanged.

## 5. carried (with downstream)

1. **changes.diff not applied** — delivery only; landing awaits the next promotion/repair batch
   (owner decision), exactly as REGISTRY-CLOSURE's J1/J2.
2. **WC-2..WC-6 untouched** (REM-07 swallow, REM-17 negatives, F12, REM-79 tooling, REM-95) —
   out of this card's frozen scope (oracle §7).
3. **I-14-C real-exit pytest suite not re-run here**: it spawns the product test dir under
   `company-wiki` (production-write risk) — declared non-goal (oracle §7); a future promotion
   batch should run it when landing K1/K2.
4. **R3b marker-twin asymmetry** declared (oracle 4d), not hidden.
5. `credential_leaks == []` must always be read together with `registered_open_leaking` —
   domain statement in oracle 4c (the instrument-design point of R5-08).
6. Value-start `\r \v \f` after the break and delimiter+space remain OPEN by scope declaration
   (oracle 1/4a) — registered, not silently implied closed.

## F-REV-R8 erratum (landing)

Recorded at landing of `reviewer_report.md` (27918 B, sha256
`57033339620bdf8085ec647bb0c049a41ebf20af62390f626148155bae44ca44`, verdict
`accepted_scoped`). This section is a transcribing erratum/bookkeeping append — it changes
no measurement, no row expectation, and no verdict of §1-§5 above; the reviewer's findings
F-REV-R8-01..05 and the parent-adjudicated collision sequence are recorded with their
dispositions:

- **F-01 (INFO, bookkeeping) — register close-figure measurement-timing drift**: §4.8 states
  the register's close-time drift as `accddcc3…`/228888 B, while later measurements recorded
  `5a9b8737…`/232018 (final_integrity, ~4 min later), `72e044d9…`/237713 and `bd83a61f…`/243062
  (reviewer). Each value is an external PARALLEL append (this card's command log contains no
  register write); **row-level holds at each point** — cited rows L17 (REM-06), L1665, L1713
  (WC-1) re-verified present verbatim at every measurement, §七十九 (L1575) belongs to the
  other card. Note only: measurement-timing bookkeeping, not a correctness defect; §4.8 and
  `binding.json.register_drift` stand as written with this timing note attached.
- **F-02 (INFO, bookkeeping) — REM-79 informational carrier-prose hits**: the mechanized scan
  (v1.2.0-correction2) flags 34 prose universal-quantifier lines across this card's 4 main
  carriers (oracle.md 14, decision.md 7, commands.md 10, handoff.md 3). These belong to the
  **REM-94 append-only bookkeeping track** (domain-qualifier repair, register L1456/L1494) and
  are **NOT a gate for this card's residual verdicts**; the reviewed spec card's carriers carry
  1 such hit and passed review. **Their report=0** (reviewer's own `reviewer_report.md` passes
  the same checker with 0 violations, §12).
- **F-03 (INFO, minor) — archive nit**: the two attempt-1 sweep runs archived only their stdout
  (`*_attempt1_loadbug.stdout.txt`) with no paired `.rc.txt`; their rc=1 lives in commands.md
  prose alone (tracebacks retained). Archive-consistency nit, no claim affected.
- **F-04 (INFO, tooling) — lossy newline field**: `build_r8.py` reports
  `"newline": nl.strip("\r")`, printing `"\n"` for BOTH LF and CRLF; the observability targets
  are in fact CRLF (937 CRLF lines). Content shas remain the real pins — **shas unaffected**,
  no claim changed; the field could mislead a future reproducer (literals need
  `old/new.replace("\n", nl)` as `build_mutants.py` does).
- **F-05 (INFO, positive) — freeze-first timestamp-anchored proof**: the pre-run-pin
  `c6cbf869…` is embedded in `build_r8.py` (mtime 23:39:56) and in the harness it generated
  (23:40:05), both BEFORE the first RED run (23:40:52); the post-RED CORRECTION W1 append
  (23:48) is prefix-proved against that pin.
- **Collision sequence record (parent-adjudicated + reviewer-grounded)**:
  - Parent ruling, verbatim: ① **CW-GATE-2 split first** → ② **WC-1 K1/K2 mechanical
    re-anchor into the split** (re-base the 3 hunks onto the post-split function layout) →
    ③ **complexity re-measure / targeted re-split if needed** → ④ **final ratchet green**.
  - Reviewer's on-disk grounding: CW-GATE-2's `changes.diff` (66831 B) includes
    `--- a/src/company_wiki/source_catalog/observability.py`; its decision.md records RC-2b
    `observability._redact_assignments` complexity 27 → 6 (split DONE, max 6), **pending
    re-verify + mutation** at review time. WC-1 hunks are written against the PRE-SPLIT file
    (both targets) — mechanical re-anchor REQUIRED at landing; do not apply this changes.diff
    verbatim onto a post-split file.

Status of this erratum: recorded by the landing carrier on the parent's authority; the
verdict `accepted_scoped` itself is the reviewer's (transcribed only — no self-signing).
`binding.json` pins are NOT rewritten here (see handoff.json bookkeeping).
