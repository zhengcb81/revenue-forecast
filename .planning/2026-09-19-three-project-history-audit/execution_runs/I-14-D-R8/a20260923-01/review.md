# WC-1 / I-14-D-R8 a20260923-01 — landing review (transcription-only)

## VERDICT BLOCK

- **status: `accepted_scoped`** — 4/4 residuals FIXED/CLOSED with rgm (red/green/mutation
  evidence) + REM-79-style bidirectional sweeps, reproduced by the independent review;
  delivery = merge-wave content layer behind the CW-GATE-UNBLOCK-2 split (see COLLISION §8).
- **Carrier (status authority)**: `reviewer_report.md` — **27918 B**, sha256
  `57033339620bdf8085ec647bb0c049a41ebf20af62390f626148155bae44ca44` (recomputed at landing ==
  sidecar `reviewer_report.sha256`, 85 B, sha256
  `704ac4148e1609673f5f1f7673e851e23fc65326af8e837c6d3f5a69494b23af`, content
  `57033339…ca44␠␠reviewer_report.md`, content-match verified).
- **N = 1** — one independent reviewer, one signed report; this file is **transcription-only**:
  every verdict word below is copied from that carrier. The landing writer adds no
  acceptance language of its own (**no self-signing**); the implementer's carriers remain
  `implementer_signed: false`.
- Scope of the transcription: verdict §VERDICT (L17-18), per-item §3 (L83-167), counts §4
  (L169-185), diff §5 (L187-216), disclosures §6 (L218-248), integrity §7 (L250-282),
  collision §8 (L284-305), scope/carries §9 (L307-323), findings §10 (L325-354), unverified
  §11 (L356-376), REM-79 self-check §12 (L378-382), signature (L386-387) — all present and
  byte-ranged in the carrier.

## 1. Transcribed 4-item verdict table (reviewer §3, confirmed 4/4)

| # | residual | transcribed verdict | reviewer grounding (carrier §) |
|---|---|---|---|
| ① | **REM-06 (K1)** — digit-suffix credential keys `token2/secret2/password2/api_key2` | **fixed-with-rgm (K1)** | RED: exactly N14-N18 + 5 `cred-digit-*` (rule) / 13 fidelity failures; GREEN: oracle rc 0 61/61, rule 113 fidelity_ok; MUT-A kills exactly 5+5, nothing else; key sweep old\new = ∅ (§3①) |
| ② | **R3-05 = REM-67③ (K2)** — value-delimiter family after the break | **fixed-with-rgm (K2, code fix — registered_open alternative NOT taken per parent standing order 「发现的缺陷都要全部修复」)** | RED: N23-N28 + 6 `cred-auth-break-*` + 2 `over-auth-break-*`; GREEN: all closed incl. N29 single-line guard + every pre-existing quoted row; MUT-B kills exactly 6 oracle + 8 rule rows, REM-06 rows stay green; value sweep 95/95 closed, new\old = exactly the six forms (§3②) |
| ③ | **R5-08** — marker-payload row per instrument | **fixed-with-rgm (record-level)** | rule `open-two-token-then-wrap-marker` + oracle `R3c-two-token-then-wrap-marker` exist on each instrument; GREEN re-run: registered_open 7 / registered_open_leaking 7 incl. marker; oracle 7/7 R3c confirmed; disclosed product_base regression (R3c registered_open, NOT confirmed) matches r7 precedent (§3③) |
| ④ | **R3-07** — `both_marker_and_non_marker` half-delivery | **closed-now-with-proof (「补全」 branch, no code of its own)** | before = frozen r3 measurement (neither C10 row carried `SYNTHETIC_AUDIT_TOKEN`); after ③ the C10 family carries BOTH credentials in BOTH instruments (S39 rows + M rows in both lists, 7/7); satisfies the reviewer's own family-level standard L471-473. **Sealed carrier untouched**: `handoff_r3.json` = 9788 B, sha `3e9648c88bd97379f2eebb8ddd1b6fadfb585b5beed79ccdad8219c3240e02fe`, mtime 2026-09-22 00:28:52 ⇒ zero re-write. **R3b marker-twin asymmetry declared** (oracle 4d + decision §5.4), carried-open (§3④) |

## 2. Transcribed re-verification evidence (reviewer §3-§5, §2)

- **10 instrument re-run field-identity**: all 10 archived-vs-rerun JSON pairs
  (`red_oracle`, `red_rule`, `green_oracle`, `green_rule`, `base_oracle`, `base_rule`,
  `mutA_oracle`, `mutA_rule`, `mutB_oracle`, `mutB_rule`) IDENTICAL field-for-field except the
  expected `src`/`label` paths; archived sweeps match the fresh re-derivations cell-for-cell.
- **Key sweep re-derived (fresh script)**: domain **350**, `old_true` **86**, `new_true`
  **200**, **old\new = ∅**, **new\old = 114, ⊆ digit-suffixed vocab**, near-miss never
  credential — matches archived `key_domain_sweep.json` cell-for-cell. **Count diag**:
  expected 120 (20 vocab × {2,3,12} × 2 cases) − actual 114 = **6** missing =
  `secret_key2/3/12 × {lower,UPPER}`, each already old-true under the OLD predicate
  (`secret` is a single atom ⇒ split part `secret` matches pre-fix), `extra=[]` ⇒ 120−114=6
  fully explained.
- **Value sweep re-derived (fresh script, 95 printable ASCII 0x20-0x7E)**: `closed_old` 89,
  **`closed_new` 95/95**, **old\new = ∅**, **new\old = exactly `{",", ";", "&", "|", "\"",
  "'"}`** — matches archived `value_start_sweep.json`.
- **Mutant purity**: reviewer rebuilt both mutants from `iso/r8_fixed` (inverse edits,
  CRLF-preserving, anchor count==1) → MUT-A tree sha
  `9ea513915bede6787a2c300a741ff65ee143a21cb8eefa1dde4abb2d62504621` and MUT-B tree sha
  `8217f10026fd846a014d42c7d2bf5734c6cb2a14d12a05536f0bd64213775931` **both equal the card's
  recorded hashes** (genuinely "fix reverted"); kill counts on the rebuilt trees: **MUT-A
  5 oracle (N14-N18) + 5 rule (`cred-digit-*`)**; **MUT-B 6 oracle (N23-N28) + 8 rule
  (6 form rows + 2 pricing rows)**; R3-00 rows green as appropriate.
- **changes.diff verification**: 9161 B / `baec3153…` (re-hash); **`git apply --check` rc 0
  and `git apply` rc 0 on FRESH scratch copies of BOTH targets** → after-shas
  **`90b3fdc3…`/45774 (r6 target, == `iso/r8_fixed`) and `081fdf5e…`/45735 (production
  target)** — equal to the claimed after-values; **3/3 hunk bodies byte-identical across the
  two targets** (8/25/22 lines); in-memory `compile()` OK for both applied files;
  **grafted %TEMP% production tree ran BOTH instruments GREEN** (oracle rc 0 / pass / 61/61 /
  open 7 confirmed 7; rule rc 3 negative, fidelity_ok true, 113, credential_leaks [], touched
  [], open 7/7) — independently reproducing `production_apply.json`
  (`green_match_with_r8_fixed: true`).
- **Prefix proof re-derived exactly (from raw bytes, both reconstructions)**: CORRECTION W1
  marker at byte **idx 17998**; `data[:17991]` → sha `3e23e74c…` (≠ pin, as recorded);
  **`data[:17991] + LF` (17992 B) → sha
  `c6cbf8691c838ddb5c0e06d803ebff364dfff8b8870e0e00202ed8bc6e50c16c` == the pre-run freeze
  pin**; timestamped anchor: pin embedded in `build_r8.py` (mtime 23:39:56) and the generated
  harness (23:40:05), both before the first RED run (23:40:52), append at 23:48 (§2, F-05).
- **Counts + rc semantics (§4)**: rule table **95 → 113**, oracle **44 → 61** (re-counted by
  importing both harness pairs; r8 row lists minus the 18/17 new ids are tuple-identical to
  the r6 lists ⇒ pre-existing rows byte-untouched). Rule instrument stays **rc 3 / verdict
  `negative` BY DESIGN since r3** (F-REV-R6-04 disclosure rule); **grep across the 6 carriers
  found NO rc0-claim for the rule table** — every "rc 0" mention pairs with the ORACLE, and
  decision L40 / oracle L139 explicitly disclaim an rc-0 claim for the rule.
- **Deliverables 10/10 present** (§2): oracle+sidecar `cd8b05e0…`, CORRECTION W1 prefix
  proof, binding (parse + pins), commands (9 steps), decision (4-row table + matrix audit),
  changes.diff, handoff.md, recovery.md, evidence (61 files, final_integrity rc=0/pass),
  harness (10 scripts).
- **Integrity re-pins (§7)**: all 10 pins re-hashed and matched (production `edcbeccb…`/43707
  == HEAD per porcelain; r6 tree `2f644994…`; product_base `c5608c4b…`; r7 report+sidecar
  `cc6da8d3…`; spec `a68ed77f…`/23413; changes.diff `baec3153…`; r6 harnesses
  `85a1b064…`/`8f5feffd…`; r8 trees `2f644994…`/`90b3fdc3…`; r8 harnesses `ad7861ee…`/
  `ffe3372b…`; oracle `cd8b05e0…` + pre-correction pin). Reviewer's own boundary scans
  (cutoff 2026-09-23 23:29:53): sealed I-14-D attempt **0 files** ≥ cutoff,
  `company-wiki\src` **0 files** ≥ cutoff ⇒ implementer's `zero_write_ok=true` holds.

## 3. Disclosures — 9/9 located and verified (reviewer §6)

1 build attempt 1 (anchor name, rc 1) → commands Step 3 + `evidence/build_r8.attempt1_failed_anchor.*`
2 sweep attempt 1 loadbug → commands Step 8 + 2 × `*_attempt1_loadbug.stdout.txt`
3 sweep attempt 2 orderbug → commands Step 8 + `value_start_sweep.attempt2_orderbug.*`
4 key-sweep count field → `key_domain_sweep.attempt2_countfield.*` + `key_sweep_count_diag.json`
5 CORRECTION W1 → oracle.md L219-237 append-only + binding dual pins (prefix proof §2)
6 prefix-proof attempt 1 miss → commands Step 9 + both reconstructions retained
7 binding Set-Content no-op → commands Step 9 (JSON load/dump rewrite; parse re-checked)
8 final_integrity iterations → commands Step 9 (3 failed attempts + final rc 0 / pass)
9 external drift (register + concurrent REGISTRY reviewer) → decision §4.8 + binding
  `register_drift` — **row-level re-verified by the reviewer**: L17 / L1665 / L1713 present
  verbatim NOW, §七十九 at L1575 = the other card's section; REGISTRY-CLOSURE's own
  `reviewer_report.md` (19887 B, 23:54:03) + sidecar exist there, SPEC still content-pinned
  `a68ed77f…`.

## 4. COLLISION NOTE §8 — verbatim transcription (parent-adjudicated)

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

## 5. F-REV-R8-01..05 dispositions (recorded in decision.md `## F-REV-R8 erratum (landing)`)

| finding | class | disposition at landing |
|---|---|---|
| F-REV-R8-01 | INFO, bookkeeping | register close-figure measurement-timing drift (`accddcc3…`/228888 → `5a9b8737…`/232018 → `72e044d9…`/237713 → `bd83a61f…`/243062); external parallel appends, **row-level holds at each point**; note appended to decision.md erratum — no measurement changed |
| F-REV-R8-02 | INFO, bookkeeping | 34 carrier-prose lines = **REM-94 append-only bookkeeping track, NOT a gate** for this card; **their report=0** (§12 self-check); carried downstream |
| F-REV-R8-03 | INFO, minor | attempt-1 sweep stdout lacks paired `.rc.txt` = archive nit; tracebacks retained; rc in commands.md prose |
| F-REV-R8-04 | INFO, tooling | `nl.strip("\r")` lossy newline field; targets are CRLF; **content shas unaffected**, no claim changed |
| F-REV-R8-05 | INFO, positive | freeze-first timestamp-anchored proof: pre-run pin `c6cbf869…` embedded in `build_r8.py`@23:39:56 (+ generated harness 23:40:05) < first RED@23:40:52 < correction@23:48, prefix-proved |

## 6. Unverified / not run by this review (transcribed §11)

1. `build_r8.py`, `build_mutants.py`, `make_changes_diff.py`, `final_integrity.py` not
   re-executed verbatim (write boundary) — equivalent coverage substituted (independent
   mutant rebuild, prefix proof, diff parse + apply on scratch, pin re-hash + boundary scans,
   10 field-identical instrument re-runs).
2. "make_changes_diff run twice, byte-identical" — historical; artifact sha + independent
   after-state reproducibility verified instead.
3. I-14-C real-exit pytest suite — not run (declared non-goal; carried).
4. r6/r7 lineage depth — verified by pins + row-list tuple-identity; the r7 review's own
   findings not re-adjudicated.
5. Register byte-history between freeze (218750) and close — not reconstructable; accepted
   under row-level verification.
6. CW-GATE-UNBLOCK-2 landing status — its decision.md still marks the observability split row
   ⏳ re-verify+mutation at review time; the §8 sequence starts once its diff lands.
7. Landing/production application of `changes.diff` — out of scope for both implementer and
   reviewer (delivery-only discipline).

## 7. Scope of acceptance (transcribed §9 + carrier status note)

- **Accepted scope**: 4/4 residuals FIXED/CLOSED with rgm + bidirectional sweeps, reproduced
  by the review; **`changes.diff` = the merge-wave CONTENT layer landing AFTER the
  CW-GATE-UNBLOCK-2 split, with mechanical re-anchor REQUIRED** (§4/§8 sequence above).
  Nothing here lands code: `changes.diff` remains unapplied by design.
- Carries passed downstream as ledger notes (not blockers): I-14-C real-exit pytest;
  declared-open items (a) R3b marker-twin asymmetry, (b) value-start `\r \v \f`, (c)
  delimiter+space, (d) single-line delimiter values (N29), (e) changes.diff unapplied,
  (f) WC-2..WC-6 untouched.
- **binding status untouched-note**: the reviewer's §9 records `binding.json` left untouched
  by the reviewer and the status flip as a bookkeeping step for the parent/owner; this
  landing likewise does **NOT** rewrite `binding.json` (its pins — spec `a68ed77f…`, trees,
  harnesses, oracle dual pins, `changes_diff_sha256 baec3153…`, `register_drift` — remain
  byte-untouched, sha256
  `4df744a9d9a07d129ce023cdc1c9dfce5dc75c08ab2f039eee111e17c9fb9054`). Status lives live in
  `handoff.json` (`status_authority`) and `evidence/I-14-D-R8/qualification.json`
  (`formula.state`); `binding.json` still reads `status: review_pending` as its historical
  pre-verdict value — recorded in bookkeeping, not rewritten.

---

**Transcribed at landing, 2026-09-24.** Status authority =
`reviewer_report.md` sha `57033339…ca44` (N=1, independent). This file contains no
verdict of its own.
