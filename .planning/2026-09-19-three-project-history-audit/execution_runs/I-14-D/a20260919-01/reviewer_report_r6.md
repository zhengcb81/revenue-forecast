# I-14-D — INDEPENDENT REVIEWER REPORT (r6)

Card: **I-14-D** (narrow the redactor's greedy bare-value semantics to a single token — the C13 card)
Attempt: `execution_runs/I-14-D/a20260919-01`
Revision under review: **r6** (the fix for `F-REV-R5-01` / `F-REV-R5-02`, the `[^\s]+` pre-break token)
Reviewer: **independent reviewer** (not the implementer; no implementer artifact was edited)
Date of review: 2026-09-22
Review posture: read-only. The only files this review wrote into the attempt are this report and its
`.sha256` pin. All reviewer scratch (probe scripts, harness outputs) lives **outside** the attempt,
under `%TEMP%\i14d_review_r6\`. Every subprocess ran with `-B` / `PYTHONDONTWRITEBYTECODE=1` using the
attempt's **own** interpreter `<ATT>\iso\venv\Scripts\python.exe` (Python 3.13.9), so no `__pycache__`
under `iso/` was refreshed and nothing else in the attempt changed. No git write command was run; no
production file was written (production anchor recomputed read-only, §5).

Predecessor reports (read first, per dispatch): `reviewer_report_r2.md` (the prescription), `review.md`
(sections `## r3`..`## r6`), `handoff_r6.json`, and `task_plan.md` Round 76.

---

## 0. VERDICT

**`changes_required` — the r6 code fix is accepted on its merits; the record and the registration are
not.**

What is **verified by my own instruments** (§1–§6): the r6 harness runs reproduce their claimed counts
(oracle **40 cases, rc 0, verdict pass**; rule table **91 rows**, `credential_leaks []`, `touched []`,
`fidelity_ok true` — with the rc caveat in F-REV-R6-04); the core r6 claim — `_AUTH_PREBREAK_TOKEN =
r"[^\s]+"` at line 329 closes every printable character r4 closed and every printable character r4 or
r5 leaked, and the only printable character still leaking at that position is the space, which
persists as the registered `C10` residual byte-form — is **true within its domain (the 95 printable
ASCII characters at the pre-break position, input shape `Authorization: Bo<c>t\n<marker>`)**, measured
on my own probe over all 95 characters on all three generations; `C10` **is registered in both
instruments** (oracle `C3.3` + rule table `registered_open`, §3); the `F-REV-R2-03` corrections are in
place and the truth **now** is that only `N5c` fails on base (§4); generation isolation holds to the
byte (§5); `status` is still `review_pending` and no verdict was self-signed (§6).

What blocks acceptance, in two MEDIUM findings and one LOW:

* **F-REV-R6-01 (MEDIUM)** — an **unregistered, base-regressive credential-persistence family**
  outside the registered `C10` input shape: a bare credential on **line 3** of a wrapped
  `Authorization:` header, and control-whitespace characters (`\r`, `\v`, `\f`) at the pre-break
  position. `iso/product_base` redacts every one of these shapes; every card tree I probed (r1/M4, r2,
  r3, r4, r5, r6) persists the card's own marker. No oracle row and no rule-table row carries any of
  them. This is the `F-REV-R4-05` species (unregistered, base-regressive, **not introduced by r6** —
  domain: measured present on all six card trees listed above, absent on `product_base`).
* **F-REV-R6-02 (MEDIUM)** — r6's headline universal ("closes every character … except the space")
  appears at three carrier sites **without its domain on the same line**, which is the exact rule
  (`REM-79`) this round adopted, and read unscoped it is **false**: at that position, in shape
  `Bo<c>t\n`, the characters `\t \r \v \f \n` also persist the marker on r6 (domain: my sweep of all
  six whitespace characters × r4/r5/r6). This is the `F-REV-R4-06`/`F-REV-R5-02` species, fourth
  generation, in the round that legislated the cure.
* **F-REV-R6-03 (LOW)** — a wrong measured number: **`16`** (r4's leaking-character count) is carried
  by `oracle.md` C6.1's table, `handoff_r6.json`, and `task_plan.md` Round 76, while the generation's
  **own pinned evidence** `r6_measurement.json` lists **18** and my independent probe on the actual r4
  tree measures **18** (domain: shape `Bo<c>t\n`, 95 printable ASCII). I could not reconstruct `16`
  from any pinned artifact.

Plus two INFO notes (`F-REV-R6-04`, `F-REV-R6-05`). Nothing in this verdict touches the code fix
itself, which is sound, isolated, invertible, and closes `F-REV-R5-01` as prescribed.

---

## 1. THE r6 HARNESS, RE-RUN BY ME (dispatch item 1)

Interpreter: `<ATT>\iso\venv\Scripts\python.exe` (the global Python was not used). Outputs written to
`%TEMP%\i14d_review_r6\{oracle_r6,rules_r6}.json`, never into the attempt.

```
python -B harness/run_i14d_oracle_r6.py     --src iso/product_narrow_r6/src --label r6 --out <scratch>
  -> cases 40 | verdict "pass" | narrow_must_failed [] | keep_must_failed []
     registered_open [R3a-two-token-then-wrap, R3b-quoted-two-token], both confirmed
  -> rc = 0
  ACTUAL COUNT: 40 cases (claim: 40) ✓

python -B harness/run_rule_table_i14d_r6.py --src iso/product_narrow_r6/src --label r6 --out <scratch>
  -> entries 91 | credential_leaks [] | touched_but_should_not_be [] | fidelity_ok true
     credential_secret_leaks [open-two-token-then-wrap, open-quoted-two-token]
     verdict "negative"
  -> rc = 3
  ACTUAL COUNT: 91 rows (claim: 91) ✓ — but rc is 3, not 0; see F-REV-R6-04
```

The 40 = 36 (r5 harness) + 4 new `N5t`–`N5w` rows; the 91 = 87 (r5) + 4 new `cred-auth-*` rows — both
increments confirmed by running the r3-era oracle (28 cases) and reading the r5 pins (36/87).

---

## 2. MY OWN PER-CHARACTER PROBE (dispatch item 2)

`%TEMP%\i14d_review_r6\rev6_probe.py` — written from scratch for this review, not derived from the
attempt's harness. LEAK := the card's own marker `SYNTHETIC_AUDIT_TOKEN` survives `redact_text`.
Trees: `iso/product_narrow_r6/src`, `iso/product_narrow_r5/src`, `iso/product_narrow_r4/src` (all
three present). Two input shapes: **shape A** = the dispatch's `Authorization: Bo<c>\n<marker>`;
**shape B** = the carriers' sweep shape `Authorization: Bo<c>t\n<marker>` (`oracle.md` C6.1 line 653,
`measure_r6.py` line 71).

### 2.1 Representative set — shape A (`Authorization: Bo<c>\n<marker>`)

| c | r4 | r5 | r6 |
|---|---|---|---|
| `?` | **LEAK** | ok | ok |
| `&` | ok | **LEAK** | ok |
| `'` | ok | **LEAK** | ok |
| `\|` | ok | **LEAK** | ok |
| `/` | **LEAK** | ok | ok |
| `:` | **LEAK** | ok | ok |
| `@` | **LEAK** | ok | ok |
| `,` | **LEAK** | **LEAK** | ok |
| `;` | **LEAK** | **LEAK** | ok |
| space | ok | ok | ok |

(r6 shape A leaks none of the ten — domain: these ten characters; full shape-A sweep below.)

### 2.2 Representative set — shape B (`Authorization: Bo<c>t\n<marker>`)

| c | r4 | r5 | r6 |
|---|---|---|---|
| `?` | **LEAK** | ok | ok |
| `&` | ok | **LEAK** | ok |
| `'` | ok | **LEAK** | ok |
| `\|` | ok | **LEAK** | ok |
| `/` | **LEAK** | ok | ok |
| `:` | **LEAK** | ok | ok |
| `@` | **LEAK** | ok | ok |
| `,` | **LEAK** | **LEAK** | ok |
| `;` | **LEAK** | **LEAK** | ok |
| space | **LEAK** | **LEAK** | **LEAK** → `Authorization: <redacted>\nSYNTHETIC_AUDIT_TOKEN` |

This table reproduces `oracle.md` C6.1's per-character block (lines 656–658) for `? & ' | / : @`
exactly, and adds `, ; space`.

### 2.3 Full printable sweeps (my counts, 95 printable ASCII at the pre-break position)

| shape | r4 | r5 | r6 |
|---|---|---|---|
| A `Bo<c>\n<marker>` | 17 | 6 | **0** |
| B `Bo<c>t\n<marker>` | **18** | 7 | **1 (`" "` only)** |

r6's shape-B leaking set is exactly `{" "}` — the claim "only space still leaks" is **TRUE — domain:
95 printable ASCII, shape `Bo<c>t\n<marker>`, tree `iso/product_narrow_r6`**. r5's set is exactly the
7 the carriers list (`space " & ' , ; |`); r4's set is exactly **18**, not the `16` the carriers print
(F-REV-R6-03). r6's set is a subset of both r4's and r5's sets minus the registered space — so "closes
every printable character r4 closed and every printable character either leaked, except the space"
holds — domain: 95 printable ASCII, shapes A+B, trees `product_narrow_r4/r5/r6`.

The space leak's output is byte-identical in form to the registered `C10` residual:
`Authorization: <redacted>\n<credential>` ✓ (both the marker form and the 39-char credential form
probed).

### 2.4 Beyond printable ASCII — the same claim is FALSE without its domain

Whitespace characters at the same position, shape B, marker survival (my `rev6_ws_probe.py`):

| c | r6 | r5 | r4 | r3 | r2 | **product_base** |
|---|---|---|---|---|---|---|
| space | LEAK | LEAK | LEAK | LEAK | LEAK | **ok** (`Authorization: <redacted>`) |
| `\t` | LEAK | LEAK | LEAK | LEAK | LEAK | **ok** |
| `\r` | LEAK | LEAK | LEAK | LEAK | LEAK | **ok** |
| `\v` | LEAK | LEAK | LEAK | LEAK | LEAK | **ok** |
| `\f` | LEAK | LEAK | LEAK | LEAK | LEAK | **ok** |
| `\n` | LEAK | LEAK | LEAK | LEAK | LEAK | **ok** |

(shape A: r4/r5/r6 all leak `\v` and `\f` only; `space \t \r \n` close on r3+; every tree leaks
nothing else in this set beyond what the table shows.) So the unscoped sentence "closes every
character either of them leaked, **only** the space still leaks" — domain needed on that line: without
the printable-ASCII domain it is refuted by five characters per the table. See F-REV-R6-02.

### 2.5 Line-3 credential (the family in F-REV-R6-01), probed across generations

Input `X1 = "Authorization: Bearer\nfoo\n" + MARKER` (bare credential on line 3):

| tree | persists marker? | output |
|---|---|---|
| `product_base` | **no** | `Authorization: <redacted>` |
| `product_mut_authsplit` (r1-era) | **yes** | `Authorization: <redacted>\nfoo\nSYNTHETIC_AUDIT_TOKEN` |
| `product_narrow` (r2), `r3`, `r4`, `r5`, `r6` | **yes** (all five) | `Authorization: <redacted>\nSYNTHETIC_AUDIT_TOKEN` |

Variant `X2` (`…\nfoo\n<marker>\ndoc=17`) leaks the marker the same way while keeping `doc=17`.
Domain for the yes/no claim: the six card trees and `product_base` named in the table, this input.

---

## 3. IS `C10` REGISTERED IN oracle.md **AND** THE RULE TABLE? (dispatch item 3)

**YES — both.**

* `oracle.md` C3.3 (lines 412–421) carries the frozen registration table: `R3a-two-token-then-wrap`
  (input `Authorization: Bearer abc\n<39-char credential>` → declared residual
  `Authorization: <redacted>\n<39-char credential>`) and `R3b-quoted-two-token`, both kind
  `registered_open`. The r6 oracle harness implements the same two rows with the declaration checked
  exactly (`residual_is_declared`), and my run shows `registered_open_confirmed = [R3a, R3b]`.
* Rule table (`run_rule_table_i14d_r6.py`): rows `open-two-token-then-wrap` and
  `open-quoted-two-token`, kind `registered_open`, **both leaking as declared**
  (`registered_open_leaking` lists both) while `credential_leaks` stays `[]` because that list is
  filtered to kind `credential`. My run: both present, 91 rows total.

Two honest qualifications: (i) both registration rows carry the **39-char credential**, not the
marker — the marker form of the same shape is invisible to `credential_leaks`; this is the known,
registered-unaddressed `F-REV-R5-08` (carried per `review.md` ## r6 "What r6 did NOT do"), not a new
finding; (ii) the registration covers the **input shape** "multi-token value then wrap" — the space
and `\t` shape-B forms produce exactly the declared residual byte-form (my probe), but the line-3 and
`\r \v \ff` shapes in F-REV-R6-01 are **not** within it.

---

## 4. F-REV-R2-03 PERSISTENCE — WHICH IS TRUE NOW? (dispatch item 4)

**True now: only `N5c` fails on `iso/product_base`; `N5d` and `N5e` pass on `product_base`** —
domain: rows `N5c-auth-scheme-lf-secret` / `N5d-auth-scheme-obsfold` / `N5e-auth-token-key-lf-secret`,
tree `iso/product_base`, my runs of two harnesses: the r6 40-case oracle (rc 3,
`narrow_must_failed` contains `N5c` and does **not** contain `N5d`/`N5e`; per-row `ORACLE-FAIL` prints
show only N5c among the three) and the r3-era `run_i14d_oracle.py` 28-case oracle (same result for
the three rows).

What the three records say **now** (I read the bytes):

| record | still contains the false claim? | exact current text |
|---|---|---|
| `oracle.md:272` | **yes** (original bytes, append-only) | "On the pre-fix base tree all three FAIL, and on M4 (below) all three …" — superseded by CORRECTION / C3.5 (lines 438–451), which states the truth |
| `fix_record.md:85-86` | **yes** (original bytes) | "All three FAIL on the base tree, on M4, and pass on the fixed tree." — superseded by C3.6 (line 166–170), which states the truth |
| `after/r2_summary.json` | **yes**, and note the premise correction: it lists **two** ids, not three — `N5c` **and** `N5e`, omitting `N5d` — under `oracle.narrow_must_failed_base` (lines 24–33) | file not edited; superseded externally by `fix_record.md` C3.7 (lines 172–178), which names the over-report |

So: the false claims persist byte-wise in all three sites by the append-only discipline; the two
markdown carriers carry appended corrections that state the truth; the JSON has only an external
supersession pointer and still contains the wrong list. **The corrected statement (only N5c fails on
base) is the one my measurement reproduces; the original "all three" sentence is false — domain:
base-tree behaviour of these three rows under either oracle harness I ran.** No new defect here;
`F-REV-R2-03`'s remediation is landed as prescribed.

---

## 5. GENERATION ISOLATION AND THE BYTE-PINS (dispatch item 5)

**Harness pins — 10/10 files byte-untouched (my sha256, vs the pins in the carriers named):**

| file | bytes | my sha256 (prefix) | pin | matches |
|---|---|---|---|---|
| `harness/run_i14d_oracle.py` (r3) | 11043 | `f7c94c60…` | handoff_r3/r4/r5 | ✓ |
| `harness/run_rule_table_i14d.py` (r3) | 19378 | `01a3187e…` | handoff_r3/r4/r5 | ✓ |
| `harness/apply_i14d_narrow.py` | 19773 | `8204b2f9…` | handoff_r3 | ✓ |
| `harness/authsplit_probe.py` | 5699 | `649d5527…` | handoff_r3 | ✓ |
| `harness/run_i14d_oracle_r4.py` | 12316 | `240d181c…` | handoff_r4/r5 | ✓ |
| `harness/run_rule_table_i14d_r4.py` | 20006 | `610ce4b8…` | handoff_r4/r5 | ✓ |
| `harness/run_i14d_oracle_r5.py` | 13293 | `38a22101…` | handoff_r5 | ✓ |
| `harness/run_rule_table_i14d_r5.py` | 20600 | `1e51373a…` | handoff_r5 | ✓ |
| `harness/run_i14d_oracle_r6.py` (new) | 14243 | `8b47e0b7…` | handoff_r6 | ✓ |
| `harness/run_rule_table_i14d_r6.py` (new) | 21175 | `c7ea6efd…` | handoff_r6 | ✓ |

**r6 tree:** `iso/product_narrow_r6/src/.../observability.py` = **43746 B**, sha256
**`2f6449949c76b97c636d5d50e2ca848403116a85a1858bb9ba8f5a2808362464`**, CR 909 = LF 909 — matches
the handoff exactly. ✓

**r6↔r5 tree comparison (my script `rev6_tree_check.py`):** 152 files vs 152 files (excluding
`__pycache__`), no file added or removed, **exactly one differing file**: `observability.py`. Its
differences are 4 hunks, all confined to the comment block (r6 lines 290–329) plus the class line —
i.e. exactly "the class line and the comment block" as the handoff claims. Reverse-reconstruction:
generic reverse-apply of those hunks to the r6 bytes yields **43362 B / `ca13fb81aa2a1234ba760f49576a6409bbd3b1397f921f2e73311f90a263fc45`**
= the on-disk r5 file byte-for-byte = the pin in `handoff_r5.json`. The r6 class line is
`_AUTH_PREBREAK_TOKEN = r"[^\s]+"` at line 329; r5's is `[^\s,;&\"'|]+` at line 324. ✓

**Carrier and evidence pins:** `review.md` 22100 B / `8a2ff101…` ✓ and `oracle.md` 41469 B /
`468fb300…` ✓ against `handoff_r6.generation_carriers`; `oracle_r6_harness.json` 18362 /
`c77dd90b…`, `r6_measurement.json` 2651 / `6b43cd43…`, `rule_r6_harness.json` 32249 / `3c969983…`
✓ against `handoff_r6.measurement.evidence` — all recomputed from bytes.

**Production (read-only):** `scripts/model_registry.py` = 26446 B, sha256 `9ec65295…` = the declared
anchor. ✓

---

## 6. STATUS — NO SELF-SIGN (dispatch item 6)

* `handoff_r6.json.status` = **`"review_pending"`** ✓; `boundaries.verdict_expressed` = `false` ✓;
  `boundaries.status_transitions` = `0` ✓; `"it_states_no_verdict": true` ✓.
* `review.md` `## r6` (lines 341–368) is landed and states "**The implementer writes no verdict
  here**"; the file contains **no `## r6 verdict` section** — the last verdict section in the file is
  `## r5 verdict`. ✓
* No `accepted`/`accepted_scoped` string appears for r6 in `handoff_r6.json`, `review.md`, or
  `oracle.md` CORRECTION 6 (checked). ✓

---

## 7. FINDINGS

### F-REV-R6-01 — MEDIUM: an unregistered, base-regressive credential-persistence family outside the registered C10 input shape

Two shape groups, both measured by me (§2.4–§2.5), both **absent on `product_base` and present on
every card tree I probed (r1/M4, r2, r3, r4, r5, r6)** — domain: the exact inputs listed below:

1. **Line-3 bare credential (double wrap):** `Authorization: Bearer\nfoo\n<credential>` →
   `Authorization: <redacted>\n<credential>` (marker/credential persists); base →
   `Authorization: <redacted>`. Variant with `\ndoc=17` after leaks the same way.
2. **Control whitespace at the pre-break position:** shape `Bo<c>t\n` with `c ∈ {\r, \v, \ff}` (and
   the `\n` case, which is shape 1 by another route) → marker persists with a residual **byte-form
   that is not the registered one** (`…<redacted>\rt\n…`, `…<redacted>\x0b\n…`); base redacts. The
   space and `\t` shape-B forms are **excluded from this finding**: they produce the registered `C10`
   residual byte-form, and the r5 reviewer already ruled the two-token-wrap form registered by design
   (`reviewer_report_r5.md` line 117).

Registration status: **no oracle row and no rule-table row carries a bare credential in any of these
shapes** — domain: all 40 `CASES` and all 91 `TABLE` rows, which I read in full. The `over_redaction`
rows register that a *key* on line 3 survives (`over-auth-token-then-keys`), and `N5c` *requires* line
3 (`doc=17`) to survive — but no row puts a **credential** there. A targeted search of every
`reviewer_report*.md`, `oracle.md`, `fix_record.md`, `decision.md`, and `handoff_r6.json` for
third-line/line-3/two-break phrasings found no prior record of shape group 1 (the `F-REV-R5-03`
discussion quotes the source comment about "keys on the lines AFTER" but never tests a credential
there).

Why MEDIUM, not BLOCKER: **r6 did not introduce either group** — domain: both groups leak identically
on the r1-era M4 tree, r2, r3, r4 and r5 — and r6's change is strictly narrowing at the pre-break
position. That is the precedent grade of `F-REV-R4-05` (unregistered + base-regressive + not
introduced by the reviewed revision → MEDIUM). Why not accepted-as-carried: unlike `C10`, these shapes
are named **nowhere** in any carrier, so `credential_leaks == []` — domain: the r6 40-case oracle and
91-row rule table I ran — remains structurally blind to them, which is the standing exit-criterion
concern of this card since C2.1.

**Remedy:** register them the way `C10` was registered — oracle rows + rule-table `registered_open`
rows carrying **both** the marker and the 39-char credential, with `oracle.md` C6 text naming the
family and its domain — **or** fix (consume a run of post-break tokens up to a `key=`-shaped line, an
owner decision because it collides with `N5c`'s keep-line-3 requirement). Registration is the cheaper
half and matches the owner's accepted-as-registered posture for `C10`.

### F-REV-R6-02 — MEDIUM: the headline universal is written without its same-line domain (the round's own REM-79), and unscoped it is false

Sites (identical claim, no domain field on the line):

* `review.md` ## r6, line 349: "`[^\s]+` closes every character r4 or r5 closed and every character
  either leaked, except the space (which is the registered OPEN shape)" — domain missing on this line;
* `oracle.md` C6.1, lines 649–651: same sentence as a prose paragraph — domain missing on this line
  (the sweep domain is stated only 8 lines above, at line 641);
* `task_plan.md` Round 76, line 1994: "关闭了 r4 与 r5 关闭过的每一个字符、以及两者泄漏过的每一个字符，只剩空格"
  — 每一个/只剩 = universal form, 域 not on this line.

Read unscoped, the sentence is false — counterexamples from my probe (§2.4), domain: shape
`Bo<c>t\n<marker>`, trees `product_narrow_r6` vs r4/r5: `\t`, `\r`, `\v`, `\f`, `\n` all persist the
marker on r6, and **all five are also leaked by r4 and r5**, so "every character either of them
leaked, except the space" fails for five members of that set. Within the printable-ASCII domain the
sentence is exactly true (§2.3) — which is precisely why the domain has to travel with it.

This is the `F-REV-R4-06` / `F-REV-R5-02` species (an unscoped universal in the same three carrier
sites: oracle / review-carrier / task_plan), recurring in the round that (a) declared the species
three-strikes-dead, (b) registered `REM-79` (same-line domain for 只有/全部/没有/整个族/零代价 claims), and
(c) announced in `review.md` ## r6 itself that "r6's own record is written to the rule". Mitigating,
and stated for fairness: `handoff_r6.json.measurement.domain` **does** scope the sweep domain
correctly, and `oracle.md` C6.4 carries an explicit "not a claim about all inputs" domain block — the
violation is at the three claim sentences themselves. `REM-78`'s promised script-level check is
declared "still_to_do" in the handoff, so nothing mechanical caught this.

**Remedy:** append corrections (T1-12 style, bytes preserved) putting the domain on the same line at
all three sites — e.g. "… except the space — domain: 95 printable ASCII at the pre-break position,
shape `Bo<c>t\n<marker>`; the whitespace characters `\t \r \v \ff \n` also persist and are the subject
of F-REV-R6-01" — and add the sentence-scanning assertion REM-78 owes.

### F-REV-R6-03 — LOW: the number `16` in three r6 records contradicts the generation's own pinned evidence and my measurement

* `oracle.md` C6.1 table (line 646): "r4's tchar class | 4 | 4 | **16 characters**";
* `handoff_r6.json → responses.F-REV-R5-01.sweep_result.r4_class_leaking_count` = **16**;
* `task_plan.md` Round 76 (line 1990): "r4 的 tchar 类 | … | **16 个**".

Measured truth — domain: all 95 printable ASCII at the pre-break position, shape
`Authorization: Bo<c>t\n<marker>`: the pinned evidence `r6_measurement.json →
candidates["r4-tchar"].leaking_single_chars` contains **18** entries, and my probe on the actual
`iso/product_narrow_r4` tree counts **18** (byte-identical set). I tried and failed to reconstruct 16
from any pinned artifact: the four difference lists in `r6_measurement.json` are 17 / 6 / 14 / 3; my
shape-A count is 17; the r5 reviewer's control-inclusive record is 19 (`reviewer_report_r5.md` line
124). No instrument I own or any pinned file produces 16.

Same species as `F-REV-R2-03` (a hand-typed number contradicting the machine record), graded LOW by
that precedent: the error understates r4's holes, so it does not inflate r6's credit — the r6 row
(`' '` only) and the r5 row (7 characters) in the same table are both correct by my measurement.

**Remedy:** correct 16 → 18 at all three sites by appended correction, and derive such counts from
`r6_measurement.json` rather than by hand.

### F-REV-R6-04 — INFO: the r6 rule-table harness exits rc 3 (`verdict "negative"`) on its own deliverable, by a design that dates to r3

My run (§1): `entries 91`, `credential_leaks []`, `touched []`, `fidelity_ok true`, but
`credential_secret_leaks = [open-two-token-then-wrap, open-quoted-two-token]` → `negative` → **rc 3**.
Cause: `run_rule_table_i14d_r6.py` line 306 computes `secret_leaks` over **all** row kinds (not just
`credential`), and the two `registered_open` rows deliberately leak the 39-char secret. This is not an
r6 change: the attempt's pinned r5-era evidence `rule_r5_harness.json` records the same `negative`
verdict with the same two rows (87 entries), and my run of `rule_r6_on_r5harness`-equivalent arm is
identical in kind. None of the r6 carriers claims rc 0 for the rule table — domain:
`handoff_r6.json`, `review.md` ## r6, `oracle.md` C6.4 — and the pinned `rule_r6_harness.json`
honestly records `verdict "negative"`. Recorded so no downstream reader quotes "91 rows, rc 0": the
green facts are the three lists and `fidelity_ok`, not the exit code.

### F-REV-R6-05 — INFO: the C10 registration rows carry only the 39-char credential form

Both instruments register `C10` (§3), but every registered row's surviving value is the 39-char
credential; the **marker** form of the same shape produces the identical residual byte-form (my
probe) yet appears in no registered row, so it is invisible to `credential_leaks`. This is exactly the
known `F-REV-R5-08`, listed as registered-unaddressed in `review.md` ## r6 — carried here as
confirmation, not as a new finding.

### Carried unchanged (recorded, not addressed, as declared)

`F-REV-R3-02`, `-03`, `-05`, `-06`..`-10`, `F-REV-R4-02`, `F-REV-R5-03`..`-08`. I re-addressed none
of them; `handoff_r6.json` and `review.md` ## r6 both declare them carried (verified present in both
records).

---

## 8. UNVERIFIED LIST

1. **Pytest suites, real worker exit, real CLI exit, `run_exit_probe.py`, and the M1–M4 mutation
   arms were not re-run by me** — outside this dispatch's finite scope. The r5→r6 delta is confined to
   the comment block and the class line (§5), so no behaviour the suites pin is touched by r6, but I
   grant that statement as reasoning, not as a measurement of mine.
2. **Whether the r4 reviewer's 31-shape base-regressive list** (`reviewer_report_r4.md`) contains my
   exact `\r/\v/\ff` pre-break probes: the r5 report says the r4 sweep "included controls and found
   them in the family" (line 592), but I did not re-derive the r4 reviewer's list, so overlap is
   probable, not proven. (Registration status in the attempt's instruments is checked either way:
   none.)
3. **`handoff_r5.json` byte-untouched**: `handoff_r6.boundaries.r5_carrier_untouched` is asserted, but
   I found no independent sha256 pin for `handoff_r5.json` in `review.md`, `task_plan.md`, or
   `REMEDIATION_REGISTER.md`; content was read for consistency only, not byte-proven to a prior pin.
4. **`after/final_hashes.json` (the r2-era 74-entry pin) was not re-audited this round**; only the
   r6-generation pins named in §5 were recomputed.
5. **Venv provenance** (works, reports 3.13.9/pytest 9.1.1) — not diffed against I-00-A's or I-14-C's.
6. **Performance / ReDoS linearity, `disclosure_adaptation`, `accuracy`, mapping, promotion** — out
   of scope, unchanged from prior rounds' unverified lists.
7. **The derivation of the carriers' `16`** — I could not reconstruct it (that is finding
   F-REV-R6-03, not an open question I deferred).
8. **Whether any downstream consumer reads a credential-shaped line-3 field** — not investigated;
   the finding is about persistence in the append-only event log, which I established directly.

---

## 9. ADJUDICATION — WHAT FLIPS THIS TO `accepted_scoped`

The code half of r6 is done and verified; the record half owes three cheap, append-only corrections:

1. **Register or fix** the F-REV-R6-01 family (line-3 bare credential; `\r \v \ff` pre-break) with
   oracle + rule-table rows carrying marker **and** 39-char credential, and a C6 text paragraph with
   its domain — the `C10` precedent is the template. If the owner instead accepts these as open, that
   is an owner ratification, recorded with rows, not an omission.
2. **Put the domain on the same line** of the three universal sentences (F-REV-R6-02 sites), per the
   round's own `REM-79`.
3. **Correct `16` → `18`** (F-REV-R6-03 sites), sourced from `r6_measurement.json`.
4. Re-run the r6 oracle and rule table after any row addition; regenerate counts if rows change.

**What this review grants:** the `[^\s]+` fix closes `F-REV-R5-01` as prescribed — domain: all 95
printable ASCII at the pre-break position, both input shapes, trees r4/r5/r6 (§2); the harness counts
40/91 reproduce; `C10` is registered in both instruments; the `F-REV-R2-03` corrections state the
truth my measurement reproduces; generation isolation, all ten harness pins, the r6 tree pin, the
r5-reconstruction, the carrier/evidence pins and the production anchor all hold; `status` is
`review_pending` with no self-sign. **What it does not grant:** acceptance, promotion, a soundness
claim for `credential_leaks == []`, or the unscoped form of the round's headline sentence.

---

## 10. HOW TO REPRODUCE THIS REVIEW

Scratch root `%TEMP%\i14d_review_r6\`; `$A` = attempt dir; `$PY` = `$A\iso\venv\Scripts\python.exe`;
every run with `-B` and `PYTHONDONTWRITEBYTECODE=1`, outputs into the scratch root.

```powershell
# §1 harness counts
& $PY -B "$A\harness\run_i14d_oracle_r6.py"     --src "$A\iso\product_narrow_r6\src" --label r6 --out "$S\oracle_r6.json"
& $PY -B "$A\harness\run_rule_table_i14d_r6.py" --src "$A\iso\product_narrow_r6\src" --label r6 --out "$S\rules_r6.json"
# §4 base-tree truth, two harness generations
& $PY -B "$A\harness\run_i14d_oracle_r6.py" --src "$A\iso\product_base\src" --label base --out "$S\oracle_r6_on_base.json"
& $PY -B "$A\harness\run_i14d_oracle.py"    --src "$A\iso\product_base\src" --label base --out "$S\oracle_r3_on_base.json"
# §2 my probes (written for this review; scripts are in the scratch root)
& $PY -B "$S\rev6_probe.py"    --src "$A\iso\product_narrow_r6\src" --label r6 --out "$S\probe_r6.json"   # repeat for _r5, _r4
& $PY -B "$S\rev6_ws_probe.py" --src "$A\iso\product_narrow_r6\src" --label r6 --out "$S\ws_r6.json"      # repeat per tree
# §2.5 line-3 probe: inline script in this review's command log (see scratch\line3_*.py)
# §5 pins / diff / reconstruction / carrier pins / production anchor
& $PY -B "$S\rev6_tree_check.py"
```

## REM-79 self-audit of this report

Every assertion in this report that uses 只有 / 全部 / 没有 / 整个族 / 零代价 — or the English universal
forms "only", "every", "all", "none" — carries its domain on the same line as the assertion (tree set,
row/case set, character set, sweep shape, or file list, as applicable). Examples are marked inline
with "domain:" throughout §0, §2–§7. Counts this review states as facts (40 cases, 91 rows, 18 vs 16
characters, 43746 B, 152 files) are each bound to the artifact or sweep that produced them.
