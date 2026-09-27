# WC-1 / I-14-D-R8 oracle — FROZEN before any run of the code under test

- card: **WC-1** work-card 「I-14-D r8 残差一轮（覆盖 REM-06 / REM-67③ / R5-08 / R3-07）」，
  spec = `execution_runs\REGISTRY-CLOSURE\a20260923-01\decision.md` §WORK-CARD WC-1 (L84-85)
  → authoritative input list for this card.
- attempt: `execution_runs\I-14-D-R8\a20260923-01`｜freeze date 2026-09-23｜NINE-STEP step 2/9.
- **Freeze discipline**: every expectation below was derived from the residual rows' text, the
  pinned sources (read-only) and pure string arithmetic (`harness/freeze_arithmetic.py`, which
  never touches the SUT) BEFORE this card executed anything against `redact_text` /
  `key_is_credential`. Nothing here is copied from an observed run.
- base: iso copy of `I-14-D/iso/product_narrow_r6` (pin `2f6449949c76b97c636d5d50e2ca848403116a85a1858bb9ba8f5a2808362464`, 43746 B) — spec clause "基=iso 复制 product_narrow_r6（pin 2f644994…）；oracle 先冻结".
- instruments: r8 copies of the two r6 harnesses (row lists extended; harness logic byte-identical
  except the row insertions): `harness/run_i14d_oracle_r8.py`, `harness/run_rule_table_i14d_r8.py`.
- constants (verbatim from the harnesses): `M = SYNTHETIC_AUDIT_TOKEN` (21), `S39 =
  ghp_ZQ7ReviewerFakeCredential0123456789` (39), `R = <redacted>` (10).

## 0. The four residuals — verbatim spec rows and chosen dispositions

| # | residual (source, verbatim key text) | spec clause (WC-1 verbatim) | disposition FROZEN |
|---|---|---|---|
| ① REM-06 | register REM-06 (L17): 「`token2/secret2/password2/api_key2` 不是凭据键（而 `refresh_token/access_token/token_2` 是）」修法「补 rule-table 行 + 扩展凭据键集合」; WC-1 A2 row: 「当前态实测未修（r6 树 `_SINGLE_ATOMS/_PAIR_ATOMS` 无数字后缀键；95 行 rule table 无该族行；live probe `token2` 明文留存）」 | 「①凭据键集扩数字后缀族（token2/secret2/password2/api_key2；参照 `_PAIR_ATOMS` 分词规则），rule-table+oracle 各补行，**过度脱敏定价**（monkey/oauth/secretary 等对照行必绿）」 | **FIXED (code)**: `key_is_credential` strips a trailing digit run from each split component before the atom-table lookup (single + pair families both). + 5 rule rows + 5 oracle rows + 4 untouched counter rows per instrument. Red/green/mutation + bidirectional key-domain sweep required. |
| ② R3-05 (= REM-67③ = F-REV-R3-05) | reviewer_report_r3.md L448-454: 「`Authorization: Bot\n,<secret>`, `\n;<secret>`, `\n&<secret>`, `\n|<secret>`, `\n"<secret>`, `\n'<secret>` all leave the credential in the clear … Recorded for completeness and for whoever writes the next row set.」 | 「②break 后值分隔符族（`\n,<secret>` 等 6 形）补行——修脱敏或按 C10 先例 `registered_open`（须域内声明）」 | **FIXED (code)** — chosen over `registered_open` per parent standing order 「发现的缺陷都要全部修复」: the after-break value alternative gains an optional leading `_VALUE_STOP_CHARS` prefix (`[,;&|"']*`), quoted forms tried FIRST (terminated quotes keep byte-identical behaviour). + 6 rule rows + 6 oracle rows + 2 over-redaction pricing rows + 1 scope-guard row. |
| ③ R5-08 (= F-REV-R5-08) | reviewer_report_r5.md L534-554: 「`credential_leaks == []` does not see the marker form of the registered two-token shape … Worth one row on each instrument」 | 「③C10 对（R3a/R3b）补 marker 载荷行（每仪器一行）」 | **ROW-ADD (record)**: exactly one marker-payload row per instrument = the R3a shape carrying `M`: rule `open-two-token-then-wrap-marker`, oracle `R3c-two-token-then-wrap-marker`, kind `registered_open`, declaring the exact leak. Makes the marker form visible on the instruments' `registered_open_leaking` path. |
| ④ R3-07 (= F-REV-R3-07) | reviewer_report_r3.md L465-474: 「`both_marker_and_non_marker` promises two things; the registered-open rows deliver one … the key name over-promises」 | 「④核 `both_marker_and_non_marker` 半交付：补全或改承诺」 | **CLOSED BY ③ COMPLETION** (「补全」branch): after ③ the C10 residual family carries BOTH a marker row (new) and non-marker rows (R3a/R3b) in both instruments — the promise is met at row level. The sealed carrier `handoff_r3.json` is NOT edited (封存载体零回改); this oracle row + decision.md carry the completion note. Domain frozen below (§4d). |

## 1. Code changes being frozen (exact semantic scope)

### FIX-1 (REM-06) — `key_is_credential`, `observability.py`

Before lookup, each `_KEY_COMPONENT_SPLIT` component is normalized:
trailing digit run stripped (`token2→token`, `secret2→secret`, `password2→password`,
`api_key2→[api,key]`); a component that is nothing but digits is left as-is. Split rules,
atom tables, pair adjacency and everything else are untouched.

- Direction prediction (bidirectional, domain §5a): **old \ new = ∅** — a pure-letter component
  is its own normalization, so every previously-accepted key is still accepted;
  **new \ old = exactly the digit-suffixed credential family** within the declared domain.
- No existing rule-table/oracle key contains a trailing digit component
  (`AWS_ACCESS_KEY_ID`, `request_id`, `next=1`… verified by inspection) → no existing row may
  change outcome.

### FIX-2 (R3-05) — `_AUTH_SCHEME_SPLIT`, `observability.py`

The after-break value gains a third alternative (tried AFTER both quoted alternatives):
`[,;&|"']*` + the unchanged `_AUTH_BARE_VALUE` (+ the same quantifier suffix as before).
Scope frozen verbatim:

- applies ONLY after the break run (single-line `Authorization: Bot,<secret>` must keep its
  current bounded behaviour — row N29 pins this);
- the delimiter must be IMMEDIATELY followed by the token (`, <secret>` with a space stays
  open — declared, not silently widened);
- value-start control whitespace `\r \v \f` after the break is OUT of this row set (pre-BREAK
  control whitespace was r7's family; R3-05's six forms are `, ; & | " '` only);
- terminated quoted forms are tried first → byte-identical output for every currently-matching
  input (N5k, `cred-auth-quoted-continuation`, R3b declarations re-verified by run).

- Direction prediction (bidirectional, domain §5b): **old \ new = ∅** (95 printable ASCII at the
  after-break value-start position, input `Authorization: Bot\n<c><S39>`); **new \ old = exactly
  `{, ; & | " '}`** — the six reported forms; everything old already closed stays closed.
- Over-redaction cost of the new prefix is fail-closed in the SAME registered class as
  `Authorization: Bearer\ndoc=17` and must be priced by rows `over-auth-break-comma-then-key`
  and `over-auth-break-dquote-then-key`.

## 2. NEW oracle rows (instrument `run_i14d_oracle_r8.py`) — frozen expectations

Kinds follow the existing harness semantics: `narrow_must` = must be red on `product_base` and
green on the fixed r8 tree; `keep_must` = must be green on r8_base AND r8_fixed AND
product_base; `registered_open` = passes only by leaking EXACTLY the declared string.

| id | kind | input | expected (exact) | expect_len | contains |
|---|---|---|---|---|---|
| N14-digit-token2-pair | narrow_must | `token=<M> token2=<S39> b=2` | `token=<redacted> token2=<redacted> b=2` | 38 | `b=2` |
| N15-digit-secret2 | narrow_must | `secret2=<S39>` | `secret2=<redacted>` | 18 | — |
| N16-digit-password2 | narrow_must | `password2=<M>` | `password2=<redacted>` | 20 | — |
| N17-digit-api-key2 | narrow_must | `api_key2=<M>` | `api_key2=<redacted>` | 19 | — |
| N18-digit-env-secret2 | narrow_must | `export SECRET2=<S39>` | `export SECRET2=<redacted>` | 25 | — |
| N19-untouched-oauth2 | keep_must | `oauth2=abc123 request_id=req-1` | unchanged | 30 | — |
| N20-untouched-monkey2 | keep_must | `monkey2=banana` | unchanged | 14 | — |
| N21-untouched-secretary2 | keep_must | `secretary2=alice` | unchanged | 16 | — |
| N22-untouched-tokenizer2 | keep_must | `tokenizer2=whitespace` | unchanged | 21 | — |
| N23-auth-break-comma | narrow_must | `Authorization: Bot\n,<S39>` | `Authorization: <redacted>` | 25 | — |
| N24-auth-break-semicolon | narrow_must | `Authorization: Bot\n;<S39>` | `Authorization: <redacted>` | 25 | — |
| N25-auth-break-ampersand | narrow_must | `Authorization: Bot\n&<S39>` | `Authorization: <redacted>` | 25 | — |
| N26-auth-break-pipe | narrow_must | `Authorization: Bot\n\|<S39>` | `Authorization: <redacted>` | 25 | — |
| N27-auth-break-dquote | narrow_must | `Authorization: Bot\n"<S39>` (unterminated) | `Authorization: <redacted>` | 25 | — |
| N28-auth-break-squote | narrow_must | `Authorization: Bot\n'<S39>` (unterminated) | `Authorization: <redacted>` | 25 | — |
| N29-auth-sameline-comma-kept | keep_must | `Authorization: Bot,<S39>` | `Authorization: <redacted>,<S39>` | 65 | — |
| R3c-two-token-then-wrap-marker | registered_open | `Authorization: Bearer abc\n<M>` | `Authorization: <redacted>\n<M>` + residual = same string | 47 | `M` |

Frozen direction predictions (per tree):

- **r8_base** (unfixed r6 copy): RED for N14-N18 and N23-N28 (11 rows); GREEN for N19-N22, N29;
  R3c GREEN (declaration of existing behaviour). ⇒ oracle rc 3, all_failed = exactly those 11.
- **r8_fixed**: ALL 61 cases GREEN ⇒ rc 0 / `pass`; `registered_open` = 7 (R3a, R3b, R7a-R7d,
  R3c), `registered_open_confirmed` = 7; `narrow_must_failed` = `[]`, `keep_must_failed` = `[]`.
- **product_base** (direction run): N14-N18 RED (base key predicate rejects the digit family;
  N14 additionally collapses under base's greedy swallow), N23-N28 RED (base leaves the
  credential — reviewer's own R3-05 observation), N19-N22 + N29 GREEN, all pre-existing
  keep_must GREEN; R3c RED on base = the same disclosed base-regression of the registration the
  r7 rows already carry (base redacts where the r6 generation persists).

## 3. NEW rule-table rows (instrument `run_rule_table_i14d_r8.py`) — frozen expectations

95 existing rows + 18 new = **113**; every new row's `expected` is the exact string frozen here.

| id | kind | input | expected (exact) |
|---|---|---|---|
| cred-digit-token2-pair | credential | `token=<M> token2=<S39> b=2` | `token=<redacted> token2=<redacted> b=2` |
| cred-digit-secret2 | credential | `secret2=<S39>` | `secret2=<redacted>` |
| cred-digit-password2 | credential | `password2=<M>` | `password2=<redacted>` |
| cred-digit-api-key2 | credential | `api_key2=<M>` | `api_key2=<redacted>` |
| cred-digit-env-secret2 | credential | `export SECRET2=<S39>` | `export SECRET2=<redacted>` |
| untouched-oauth2 | untouched | `oauth2=abc123 request_id=req-1` | unchanged |
| untouched-monkey2 | untouched | `monkey2=banana` | unchanged |
| untouched-secretary2 | untouched | `secretary2=alice` | unchanged |
| untouched-tokenizer2 | untouched | `tokenizer2=whitespace` | unchanged |
| cred-auth-break-comma-secret | credential | `Authorization: Bot\n,<S39>` | `Authorization: <redacted>` |
| cred-auth-break-semicolon-secret | credential | `Authorization: Bot\n;<S39>` | `Authorization: <redacted>` |
| cred-auth-break-ampersand-secret | credential | `Authorization: Bot\n&<S39>` | `Authorization: <redacted>` |
| cred-auth-break-pipe-secret | credential | `Authorization: Bot\n\|<S39>` | `Authorization: <redacted>` |
| cred-auth-break-dquote-secret | credential | `Authorization: Bot\n"<S39>` | `Authorization: <redacted>` |
| cred-auth-break-squote-secret | credential | `Authorization: Bot\n'<S39>` | `Authorization: <redacted>` |
| over-auth-break-comma-then-key | over_redaction | `Authorization: Bearer\n,doc=17` | `Authorization: <redacted>` |
| over-auth-break-dquote-then-key | over_redaction | `Authorization: Bearer\n"doc=17` | `Authorization: <redacted>` |
| open-two-token-then-wrap-marker | registered_open | `Authorization: Bearer abc\n<M>` | `Authorization: <redacted>\n<M>` |

Frozen counts / verdicts:

- **r8_base**: `entries` 113; `fidelity_failures` = exactly the 13 new rows whose expectation is
  the FIXED behaviour (5 cred-digit + 6 cred-auth-break + 2 over-auth-break); all 95 pre-existing
  rows + 4 untouched counters + `open-two-token-then-wrap-marker` fidelity-OK;
  `credential_leaks` `[]`, `touched_but_should_not_be` `[]`, `registered_open_rows` 7 (7
  leaking), `fidelity_ok` false, verdict `negative`, rc 3.
- **r8_fixed**: `entries` 113; `fidelity_ok` true; `credential_leaks` `[]`;
  `touched_but_should_not_be` `[]` (all monkey/oauth/secretary/tokenizer/keyboard/key/url/doc/
  stage rows INCLUDING the four new digit counters stay untouched — the 过度脱敏定价 clause);
  `registered_open_rows` 7, `registered_open_leaking` 7 (incl. the marker row ⇒ R5-08's
  instrument now SEES the marker form); verdict `negative` rc 3 BY DESIGN (registered_open
  leaks as declared — F-REV-R6-04 disclosure rule in force, no rc 0 claim is made for the rule
  table).
- **product_base**: direction run, raw captured; no rc claim, no pass claim (base predates the
  whole card).

## 4. Frozen declarations (domain-limited, REM-78 style — domain on the same line)

(a) **R3-05 closure domain**: closed = the six value-delimiter starts `, ; & | " '` when the
delimiter is IMMEDIATELY followed by a token after the break run, on the r8_fixed tree (and its
delivery targets). NOT closed and declared open: delimiter + space + token; value-start
`\r \v \f` after the break; single-line delimiter values (N29 pins the unchanged behaviour).

(b) **REM-06 closure domain**: keys reachable by splitting on `_-` whose components carry a
TRAILING digit run, within the §5a key domain. NOT in the family: leading-digit components
(`2token`), interior-digit components (`tok2en`), digit components used as pair separators
(`api_2_key` stays non-credential), non-suffix words (`oauth`, `secretary` unchanged).

(c) **R5-08 closure domain**: the marker form of the C10 R3a shape is now a row on BOTH
instruments (rule `open-two-token-then-wrap-marker`, oracle `R3c-…`), visible via
`registered_open_leaking` (marker_survives) and the oracle's `registered_open_confirmed` list.
`credential_leaks == []` stays filtered to kind `credential` by design and must always be read
together with `registered_open_leaking` — domain: this card's two instruments.

(d) **R3-07 closure domain**: `both_marker_and_non_marker` is now satisfied at ROW level for
the C10 residual family = {R3a (S39), R3b (S39), R3c (marker)} across both instruments; the
quoted variant R3b has no dedicated marker twin (spec froze ③ as 每仪器一行) and that
asymmetry is declared here rather than hidden. The sealed `handoff_r3.json` key text is NOT
edited.

## 5. Frozen bidirectional criteria (REM-79 双向差集判据, per WC-1)

(a) **Key domain sweep** (`harness/sweep_key_domain.py`, old = r8_base module, new = r8_fixed
module, same function name loaded by file path): domain = {8 single atoms} ∪ {12 pair composites}
∪ {15 near-miss words: monkey, oauth, secretary, tokenizer, keyboard, key, url, digest, flag,
doc, stage, code, document, request, next} × suffix {"", "2", "3", "12", "_2"} × {lower, UPPER}.
Criteria: `old \ new = []` (no accepted key lost); `new \ old` ⊆ digit-suffixed variants of the
atom/pair vocabulary only (near-miss words never enter). Evidence: `evidence/key_domain_sweep.json`.

(b) **Value-start sweep** (`harness/sweep_value_start.py`): for each of the 95 printable ASCII
chars `c` (0x20-0x7E), input = `Authorization: Bot\n` + c + `S39`; "closed" = `S39` absent from
output; old tree = r8_base, new tree = r8_fixed. Criteria: `old_closed \ new_closed = []`;
`new_closed \ old_closed = {, ; & | " '}` exactly (the six R3-05 forms).
Evidence: `evidence/value_start_sweep.json`.

## 6. Frozen protocol (NINE-STEP, this card)

1. read card + pin inputs (shas in `binding.json`); 2. **this freeze** (oracle.md + sha, pure
arithmetic only); 3. isolated copies `iso/r8_base` (pin-verified) + `iso/r8_fixed` (built by
`harness/build_r8.py`, literal-replacement with count assertions); 4. RED: both instruments on
r8_base → `evidence/red_*`; 5. GREEN: both instruments on r8_fixed → `evidence/green_*`;
6. product_base direction run → `evidence/base_*`; 7. MUTATION: two mutants in %TEMP%
(MUT-A reverts FIX-1 ⇒ exactly the REM-06 rows go red; MUT-B reverts FIX-2 ⇒ exactly the
R3-05 rows go red) → `evidence/mut_*`; 8. bidirectional sweeps §5 → `evidence/*_sweep.json` +
`py_compile` of both fixed targets → `changes.diff` built for BOTH delivery targets
(generation r6 tree + production company-wiki copy) with a temp-copy apply check; 9. carriers
(`decision.md`, `commands.md`, `evidence\`, `recovery.md`, `handoff`) written; status
`review_pending`, unsigned, verdict authority = independent reviewer.

Frozen red/green/mutation matrix (what counts as success, decided now):

- RED is successful iff the failures are EXACTLY the frozen sets above (no collateral row flips;
  any collateral flip = a regression of my fix, to be fixed in the fix, never in the oracle).
- GREEN is successful iff oracle 61/61 rc 0 AND rule 113 rows fidelity_ok with the frozen count
  cells above.
- MUTATION is successful iff each mutant kills EXACTLY its own family's rows and nothing else.
- No acceptance/verdict language may appear in any carrier of this attempt.

## 7. Explicit non-goals (frozen)

- WC-2 (value-less `Authorization:` swallow / REM-07) NOT touched; WC-3..WC-6 NOT touched.
- No sealed carrier (I-14-D a20260919-01 files, handoff_r3.json, register history rows, review
  reports) is edited; no register append is made by this card.
- No production write: `company-wiki` and `revenue-forecast` sources are read-only; delivery is
  `changes.diff` only (application = a later promotion/repair batch, owner's decision).
- The I-14-C real-exit pytest suite is NOT re-run by this card (it spawns the product test dir
  under `company-wiki` — production-write risk outside WC-1's frozen scope); disclosed in
  decision.md §carried.

---

# CORRECTION W1 (2026-09-23, appended after the RED run; original bytes above unchanged)

Appended, not a rewrite: every byte above this line is the pre-run freeze and is left exactly
as it was (prefix proof in `evidence/oracle_prefix_proof.json`).

- **One frozen forecast cell was wrong**: §3's r8_base row says `credential_leaks` `[]`. The RED
  run measured `credential_leaks = [cred-digit-password2, cred-digit-api-key2]`
  (`evidence/red_rule_r8_base.json`). The MEASUREMENT is the correct instrument behaviour — on
  the UNFIXED tree the marker of those kind-`credential` rows survives, which is precisely what
  `credential_leaks` exists to surface (and the S39 forms surface in `credential_secret_leaks`).
  On r8_fixed the frozen cell holds as written (`credential_leaks = []`,
  `evidence/green_rule_r8_fixed.json`). **No row expectation, kind, failure-set, count or
  verdict prediction changed**: the frozen RED sets (11 oracle / 13 rule), the frozen GREEN
  cells (61/61 rc 0; 113 fidelity_ok; registered_open 7/7; touched `[]`), the frozen
  product_base direction predictions and both bidirectional sweep criteria were all verified
  exactly as frozen (per-cell audit in `decision.md` §matrix).
- Retained as superseded: `oracle_sha256` `c6cbf8691c838ddb5c0e06d803ebff364dfff8b8870e0e00202ed8bc6e50c16c`
  (the pre-run freeze pin) — re-pinned alongside this correction in `oracle.sha256` and
  `binding.json` (field `oracle_sha256_pre_correction` keeps the old value).
