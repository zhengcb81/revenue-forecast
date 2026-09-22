# I-14-D — INDEPENDENT REVIEWER REPORT (r4)

Card: **I-14-D** (narrow the redactor's greedy bare-value semantics; r4 applies the two code fixes
the r3 review required, adds the rows that register them, and carries its own harnesses)
Attempt: `execution_runs/I-14-D/a20260919-01`
Revision under review: **r4** —
`iso/product_narrow_r4/src/company_wiki/source_catalog/observability.py`,
sha256 `15446f4da6ba256f039e684eaa4bd0c6f45889dc86a624717c6a0ec836e3f2a1`, 42829 bytes.
Pre-image r3: sha256 `a551cc45efcd11925d6c647dec0564d5d0684ce5c675794136f465d33dc22fda`, 42839 bytes.
Reviewer: **independent** — not the author of the r4 code, the r4 measurement, or the r4 record.
Posture: read-only w.r.t. the attempt. The only file this review writes into the attempt is this
report. All reviewer instruments and outputs live outside it, under
`execution_runs/_review_i14d_r4_20260922/`. Nothing was deleted, moved or cleaned up.
Line endings: this report is LF-only (CR=0), matching `reviewer_report_r2.md` and
`reviewer_report_r3.md`.
Date of review: 2026-09-22.

---

## 0. VERDICT

**`changes_required` — the r4 revision is NOT accepted as delivered.**

The two fixes are real, they are the fixes the carrier says they are, they are class-level rather
than instance-level, and they are regression-free. **All eleven claims reproduce.** Nothing in
`handoff_r4.json` overstates its measurements. The rows that register the fixes are load-bearing
(every one of the eight goes red on the r3 tree) and their expectations **are** derivable from the
specification independently of the code, which is the specific question this review was asked to
settle — I settle it in the affirmative, by derivation from the already-frozen r2/r3 rows.

The revision is not acceptable because of what it *leaves standing* and what its own record *says
about that*:

* **F-REV-R4-05 (MEDIUM).** An unregistered, `product_base`-regressive credential-persistence family
  remains on the auth path. Shape: `Authorization: <W>\n<credential>` where `<W>` is a single
  pre-break token that is not an RFC-7230 `tchar` token. Measured: `redact_text('Authorization:
  Bo?t\n<S39>')` → `'Authorization: <redacted>\n<S39>'` on r4, where `product_base` redacts the
  credential. **The card's own synthetic marker is affected**: `Authorization: Bo?t\nSYNTHETIC_AUDIT_TOKEN`
  persists the marker on r4 and is redacted on base. This is not introduced by r4 (r2 and r3 leak it
  too, and r4 strictly reduces the family), and no r4 record claims the family is closed — but it is
  enumerated nowhere, and the card's own standard (F-REV-R2-01, reaffirmed by the r3 review) is that
  a residual must be *registered* before `credential_leaks == []` can be offered as exit-criterion
  evidence. The registered `C10` row is the precedent.
* **F-REV-R4-06 (MEDIUM).** `oracle.md` CORRECTION 4 **C4.5** — the r4 generation's own correction
  carrier — says of the measured candidates: *"`fix_A_and_B` leaves only the registered `C10`
  residual."* That is **false as written**: it is true of the 19-probe set `measure_r4.py` actually
  runs, and false of the code. The same unqualified universal is repeated in
  `REMEDIATION_REGISTER.md` REM-67② ("`fix_A_and_B` 下**仅剩登记的 `C10`**") and in
  `task_plan.md` Round 72's measurement table ("仅 `C10`"). This is the F-REV-R3-02 species — a
  measurement cited as if it were general — recurring in the generation that was supposed to be
  answering F-REV-R3-02.
* **F-REV-R4-01 (LOW).** The source comment at `observability.py:295-298` still asserts the ABNF
  justification the r3 review proved false, and now **contradicts the code three lines below it**:
  it says the class "starts with `[A-Za-z]`" while line 317 is the full tchar class. The comment is
  byte-identical between r3 and r4 (proved by the 4-region diff). This is the unlanded half of
  F-REV-R3-04, which the carrier lists as fixed.
* **F-REV-R4-02 (LOW).** `_r4_measure_20260922/measure_r4.py`'s module docstring and
  `r4_measurement.json`'s `fix_b_measured_but_not_applied` key both state that fix B is *not* in the
  tree, contradicting the same file's `main()` and the tree. The measurement itself is correct and
  reproduces byte-for-byte; the description of it is not.

**Scope this verdict covers.** The r4 product copy `iso/product_narrow_r4/src` at the byte-pin
above; the two r4 harnesses and the two r3 harnesses at their byte-pins; the r4 generation carriers
(`oracle.md` CORRECTION 4, `review.md` §r4, `handoff_r4.json`); the recorded measurement
(`_r4_measure_20260922/`); the recorded r3 runs (`scratch/oracle_r3.json`, `scratch/rule_r3.json`);
and the round-72 register/task-plan entries. Every registered hash was recomputed from the bytes.
The three product trees (`product_base`, `product_narrow_r3`, `product_narrow_r4`) and the r2 tree
(`product_narrow`) were all exercised.

**Scope this verdict does NOT cover.** (a) The correctness of the r2 generation beyond what r4
inherits; I used the r2 tree only as a comparison arm. (b) The copied pytest suites and the real
worker/CLI exit: I did **not** run `harness/tests/test_i14c_real_exit_redaction.py`,
`harness/tests/test_i14d_single_token.py`, `run_exit_probe.py` or `run_real_cli_exit.py`, so every
leak I report is measured at the `redact_text` helper, not end-to-end. (c) The mutation trees
M1/M2/M3; I used no mutation arm (the r3 tree and `product_base` served as the differential arms).
(d) Promotion, `disclosure_adaptation`, accuracy or any mapping question. (e) Whether any
downstream consumer depends on the over-redacted diagnostic key. (f) ReDoS/timing — not re-timed.
(g) The internal consistency of `task_plan.md`/`REMEDIATION_REGISTER.md` outside the I-14-D
sections. (h) I did not attempt to reconstruct the r3 generation's pre-pin history (see
F-REV-R4-04 and UNVERIFIED §5).

---

## 1. THE ELEVEN CLAIMS

### Claim 1 — the two fixes are what the carrier says (byte-level) — **CONFIRMED**

Read from the bytes (`rev_claim1_bytes.py`, `rev_line_endings.py`, `rev_addendum.py`).

`difflib.SequenceMatcher(autojunk=False)` on the two byte strings finds **exactly four** non-equal
regions, and all four are on lines 317 and 320:

| # | r3 byte range | r3 bytes | r4 | line |
|---|---|---|---|---|
| 0 | `r3[18729:18737]` | `][A-Za-z` (8 B, deleted) | — | 317 |
| 1 | `r3[18756:18757]` | `*` | `+` | 317 |
| 2 | `r3[18933:18934]` | `?` (deleted) | — | 320 |
| 3 | `r3[18947:18948]` | `?` (deleted) | — | 320 |

Net: 42839 → 42829 B (−10). Region 0+1 are F-REV-R3-04 (`[A-Za-z][A-Za-z0-9!#$%&'*+.^_\`|~-]*` →
`[A-Za-z0-9!#$%&'*+.^_\`|~-]+`); regions 2+3 are F-REV-R3-01 (**two bytes**, exactly as the carrier's
`bytes_changed: 2` says).

**Inversion reproduces r3 byte for byte, line endings included.** Applying the reverse of all four
regions to r4 yields sha256 `a551cc45efcd11925d6c647dec0564d5d0684ce5c675794136f465d33dc22fda`, equal
to r3. The reconstruction is *load-bearing*: dropping **any one** of the four regions makes it
differ from r3 (`rev_addendum.py`).

**Line endings.** r3 CR=897 LF=897 CRLF=897, bareCR=0, bareLF=0; r4 identical. The self-inflicted
`\r\r\n` corruption is absent from the `.py` source. (The 50 files in the r4 tree that do contain a
`\r\r` byte pair are all `__pycache__/*.pyc`, and the same 50 files with the same counts are in the
r3 tree — compiled-bytecode noise, not a corruption artefact.)

**Whole-tree check.** The r4 tree differs from the r3 tree in **exactly one file**:
`src/company_wiki/source_catalog/observability.py`. Same file list (202 files each).

**`observability.py:319` is deliberately untouched, and that is correct.** r4 line 319 is
`                      r"(?:(?:\r?\n)[ \t]*)+"`. The `\r?\n` sits inside the non-capturing group
`(?:\r?\n)`, **outside any character class**, so `?` there is the optional-`\r` quantifier and the
group accepts both LF and CRLF — which is what `cred-auth-split-bearer-crlf`
(`Authorization: Bearer\r\n<marker>`) needs and what it measures. The two `?` that were wrong were
the ones *inside* `[^"\r?\n]` / `[^'\r?\n]`. Confirmed by reading the bytes of both lines and by the
CRLF row passing on r4.

### Claim 2 — the `?` leak is closed, at the class level — **CONFIRMED**

**Both quote styles, both credentials.** 16 probes of the form
`Authorization: Bot\n<q><cred><suffix><q>` (q ∈ {`"`, `'`} × cred ∈ {`S39`, `SYNTHETIC_AUDIT_TOKEN`} ×
suffix ∈ {``, `?x`, `?`, `??`, `?`mid-credential, `https://x/y?a=b `}):

```
r4   leaks 0 of 16
r3   leaks 16 of 16
base leaks 20 of 20   (also the 4 `?`-free forms)
```

(`rev_probe.py` family `Q`; outputs in `probe_product_narrow_r4.json` / `_r3.json` / `_base.json`.)

**Class level, not instance level.** A character sweep over all 95 printable ASCII plus
`\t \n \r \x0b \x0c`, inserted into a quoted continuation, for both quote styles (200 probes):

| tree | characters that leave the quoted continuation unredacted |
|---|---|
| `product_base` | 100 characters (essentially the whole alphabet) |
| `product_narrow_r3` | `?` (0x3f), `\n` (0x0a), `\r` (0x0d) |
| **`product_narrow_r4`** | **`\n` (0x0a), `\r` (0x0d) only** |

`r3 \ r4 = {0x3f}` — the leak r4 closed. **`r4 \ r3 = ∅` — r4 introduced no new leaking character.**
The two remaining characters are exactly the ones `_QUOTED_VALUE` excludes, i.e. a raw newline
cannot occur inside a quoted string; that is the specification's own class, not a defect.

**The cleanest statement of class closure.** The after-break quoted alternatives on r4 line 320 are
now **byte-identical** to `_QUOTED_VALUE` (line 285):

```
_QUOTED_VALUE   (285) = \"[^\"\r\n]*\"|'[^'\r\n]*'
line 320 r4     (320) = ...r"+|\"[^\"\r\n]*\"|'[^'\r\n]*')")     <- identical
line 320 r3     (320) = ...r"+|\"[^\"\r?\n]*\"|'[^'\r?\n]*')")  <- not identical
```

So the fix is not "the two strings the rows name are now matched"; it is "the after-break quoted
class *is* the module's canonical quoted class". That is the class-level property the r3 review
found missing in r2.

**Why the leak happened, restated so the closure is legible.** Inside a character class `?` is a
literal member of the negated set, so `[^"\r?\n]` excluded `?` as well as CR and LF; a leading `"` is
also a delimiter for `_AUTH_BARE_VALUE`, so the whole `_AUTH_SCHEME_SPLIT` alternative failed and
only the scheme word was redacted.

### Claim 3 — the non-letter-scheme family is closed, compared against `product_base` — **CONFIRMED**

30 probes of the form `Authorization: <W>\n<S39>\ndoc=17`, where `<W>` is `<c>foo` for every
non-letter tchar `c` (`! # $ % & ' * + - . ^ _ \` | ~` and `0`–`9`), plus `<c>` alone, plus
`_foo`, plus the letter control `afoo`:

| tree | leaking probes |
|---|---|
| `product_base` | 3 (`&`, `'`, `\|` — the value-delimiter members) |
| `product_narrow_r3` | **28** (every non-letter initial) |
| **`product_narrow_r4`** | **0** |

So r4 is **strictly better than `product_base`** on this family: it leaks nothing base does not, and
it closes all 28 that r3 leaked. The r3 review's F-REV-R3-04 regression is closed. Both credentials
are covered: `N5n`/`cred-auth-nonletter-bang` carry the marker, `N5o`/`cred-auth-nonletter-digit`
carry the 39-char credential.

Also confirmed from the fix-separated measurement, which I re-ran: `fix_A_only` leaks
`C10 + non-letter-bang-scheme + non-letter-digit-scheme + non-letter-marker`; `fix_A_and_B` leaks
`C10` only — i.e. fix B is load-bearing and does what the carrier says.

**Boundary of this claim, stated so it is not read as more than it is.** Claim 3 is about the
non-letter-**tchar-initial** family, and that family is closed. There is an *adjacent* pre-break
family that is not closed and is not registered — see F-REV-R4-05. It is not the family this claim
names, and r4 does not claim to have closed it.

### Claim 4 — the new rows are registered, and their expectations are sound — **CONFIRMED**

**Registered.** Four oracle rows and four rule-table rows exist, in the new files only:

```
oracle  32 rows (was 28): N5l-auth-dq-question-mark, N5m-auth-sq-question-mark,
                          N5n-auth-nonletter-scheme-marker, N5o-auth-nonletter-scheme-secret
rule    83 rows (was 79): cred-auth-dq-question-mark, cred-auth-sq-question-mark,
                          cred-auth-nonletter-digit, cred-auth-nonletter-bang
```

**Load-bearing.** All eight go red on the r3 tree, and the four oracle rows also go red on
`product_base`:

```
r4 oracle harness on r4   : 32 cases, narrow_must_failed [], keep_must_failed [], verdict pass, rc 0
r4 oracle harness on r3   : narrow_must_failed = [N5l, N5m, N5n, N5o]                 rc 3
r4 rule harness  on r3    : fidelity_failures = [the 4 new rows];
                            credential_leaks = [cred-auth-nonletter-bang];
                            credential_secret_leaks += [dq-question-mark, sq-question-mark, nonletter-digit]
```

So the rows are not vacuous: on the pre-fix tree each fails, and `cred-auth-nonletter-bang` even
lands in `credential_leaks` there.

**The evidence-standard question this review was asked to settle: are the four expectations
derivable from the specification independently of the code?** **Yes.** The disclosure is real — the
expected strings were read off the r4 tree and frozen, which is weaker than the hand-computation
`oracle.md` §2 requires. But the expectations are *forced*, because each new row is a pre-existing
frozen row with one named substitution, and the substitution's semantics are exactly what the
corresponding fix states:

| new row | derived from (already frozen, already reviewed) | substitution | expectation identical? |
|---|---|---|---|
| `N5l-auth-dq-question-mark` | `N5k-auth-quoted-continuation` → `Authorization: <redacted>`, len 25 | insert `?x` inside the double quotes | **yes** (25) |
| `N5m-auth-sq-question-mark` | same, single-quote twin | insert `?x` inside the single quotes | **yes** (25) |
| `N5n-auth-nonletter-scheme-marker` | `N5c-auth-scheme-lf-secret` → `Authorization: <redacted>\ndoc=17`, len 32 | scheme `Bearer` → `2foo` | **yes** (32) |
| `N5o-auth-nonletter-scheme-secret` | same, with the 39-char credential | scheme `Bearer` → `!foo` | **yes** (32) |

The derivation is: F-REV-R3-01 says a quoted continuation is matched by the same class as
`_QUOTED_VALUE`, so adding `?x` inside the quotes cannot change the output — the answer is N5k's
answer. F-REV-R3-04 says the pre-break token is any RFC-7230 `tchar` run, so `2foo` and `!foo` are
scheme tokens exactly as `Bearer` is — the answer is N5c's answer. Both are one-line consequences of
the specification text, and both agree with the frozen expectations. **I therefore judge the
expectations sound despite the weaker provenance**, and I record that this is a *judgement on
derivability*, not on provenance: had any of the four expectations differed from its parent row's,
or had it contained the credential, the provenance would have been disqualifying. None does
(`credential/marker absent from expected: True` for all four).

One coverage note, not a defect: within the `?` family the eight new rows carry only the 39-char
non-marker credential (no marker row); within the non-letter family both credentials are carried.
The behaviour covers both credentials for both families (measured in Claim 2), so this is a
row-coverage note for whoever writes the next row set.

### Claim 5 — no regression in the pre-existing rows — **CONFIRMED**

The r3 harnesses (byte-identical to their pins) run on both the r3 and the r4 trees, compared row by
row on every field:

```
28 r3 ORACLE rows      : same id set, same order, rows with any field difference = 0
79 r3 RULE-TABLE rows  : same id set, same order, rows with any field difference = 0
```

Cross-checks: my re-run of the r3 oracle and r3 rule harnesses on the r3 tree reproduces the
recorded `scratch/oracle_r3.json` and `scratch/rule_r3.json` with **0 differing rows**; and my re-run
of the r4 harnesses on the r4 tree reproduces the recorded `oracle_r4_harness.json` and
`rule_r4_harness.json` with **0 differing rows**. So the r4 tree moves no pre-existing row and the
recorded runs are faithful.

### Claim 6 — the over-redaction family is unchanged, still 9 rows — **CONFIRMED**

```
over_redaction_rows on the r3 tree = 9    over_redaction_touched = 9
over_redaction_rows on the r4 tree = 9    over_redaction_touched = 9
recorded r4 rule harness (83 rows) = 9
```

Identical id lists in all three:
`over-auth-scheme-then-key`, `-reqid`, `-stage`, `over-auth-token-then-keys`,
`over-auth-crlf-then-key`, `over-auth-obsfold-then-key`, `over-proxy-auth-then-key`,
`over-auth-scheme-then-marker`, `over-auth-generic-then-key`. All 9 are `fidelity_ok` (each asserts
the loss exactly), so the cost stays measured rather than invisible.

### Claim 7 — the generation isolation is real — **CONFIRMED**

```
harness/run_i14d_oracle.py       11043 B  f7c94c60ce8dffda8d58786d6b20787ff11e4c5c22f06ec1ba1e0307d96a4fe2  == r3 carrier pin
harness/run_rule_table_i14d.py   19378 B  01a3187e9d5062db316fa89e3fc0feb40f862c782a7ce782aa458c6a0f4f7ed6  == r3 carrier pin
harness/run_i14d_oracle_r4.py    12316 B  240d181c9fb8f21c42d2d4aaa364936b0fabde7d23dedf0bdd356d497765d13f  == r4 carrier pin
harness/run_rule_table_i14d_r4.py 20006 B 610ce4b84903d224aef60a54dd4a5f46872efadeddad869989d86e0418e45aa5  == r4 carrier pin
```

The two r3 pins are the values the **r3 carrier** (`handoff_r3.json.what_changed.harness`) registers,
and they are unchanged. The r4 rows live **only** in the new files: the string
`N5l|N5m|N5n|N5o|question-mark|nonletter` occurs **0** times in `run_i14d_oracle.py` and **0** times
in `run_rule_table_i14d.py` (and the grep instrument is responsive — see §6). The r3 recorded runs
are also still at their r3-carrier pin (`scratch/oracle_r3.json`, `c436d621…`).

**Why it matters, and why r4 got it right.** The r3 carrier pins the r3 harnesses, and the r3 tree's
reproduction basis is "run *these* harnesses against *that* tree". Adding rows in place would
invalidate both pins *and* silently change what reproducing the r3 run means: the r3 tree would then
fail rows that did not exist when it was measured. r4 avoids this by carrying its own files, which
is the correct handling of an append-only audit trail — and it is a fix for a real, previously
incurred loss: the r2→r3 step extended in place, so the r2 generation's reproduction basis is gone
(registered as REM-70). The rationale in `oracle.md` C4.4 and `handoff_r4.json.why_new_files` is
accurate.

### Claim 8 — the carrier does not overstate — **CONFIRMED**

I read `handoff_r4.json` sentence by sentence and recomputed **every** hash in it from the bytes:

| carrier claim | measurement |
|---|---|
| `product_copy` 42829 B / `15446f4d…` | **matches** |
| `differs_from_r3_in_exactly: "4 byte regions"` | **matches** (4 regions, lines 317/320) |
| `inverse_reconstruction_reproduces_r3: "byte for byte, line endings included"` | **matches** (all 4 regions needed) |
| r3 harness pins, r4 harness pins | **all 4 match** |
| `generation_carriers` oracle.md/review.md before/after bytes+sha256, `prefix_preserved: true` | **all match**, and both are *pure* byte prefixes (`oracle.md[:27119]` = `e85cb05b…`; `review.md[:10630]` = `4d245fbf…`) |
| `measurement.evidence` 3 pins | **all 3 match** |
| `fixes_measured_apart` | **reproduced** (re-ran `measure_r4.py`; output byte-identical) |
| `oracle` 32 cases / `pass`; `rule_table` 83 rows / `credential_leaks []` / `touched []` / `fidelity_ok true` | **all match** |
| `over_redaction_unchanged: true`, `pre_existing_rows_changed: 0` | **both match** |
| `production_anchor` `scripts/model_registry.py` `9ec65295…` / 26446 B | **matches, unchanged** |
| `status: review_pending`, `verdict_expressed: false`, `it_states_no_verdict: true` | **matches** |
| `who_wrote_it_and_on_what_basis.basis`: "every hash here is computed from the bytes" | **verified for all 13 registered values** |

Critically, `handoff_r4.json` **does not repeat** the r3 carrier's overstatement
`credential_leaks_is_sound_again: true`; it reports `credential_leaks: []` as a measurement and
lists `not_addressed_here`. Two things I record as *scoping gaps* rather than overstatements, because
the numbers are right and the fields are nested under `measurement`: (i) `fixes_measured_apart` does
not state that its `oracle_failures`/`rule_failures` are computed over the **r3** (28/79-row) tables
rather than the r4 (32/83-row) ones; (ii) the field `leaking: ["C10"]` is not accompanied by the
probe set it is a leak set *of*. Both matter only because a different r4 record states the same
result as an unqualified universal — see **F-REV-R4-06**. `handoff_r4.json` itself is clean.

### Claim 9 — the three self-inflicted errors are honestly recorded — **CONFIRMED**

All three are recorded in `handoff_r4.json.self_inflicted_errors_recorded` and in `task_plan.md`
Round 72; two of the three are also in `review.md` §r4 (see F-REV-R4-03). Each record's *fix* is
verifiable, and I verified it:

1. **Text-mode round trip doubled every CR** (`CR 897 → 1794`, i.e. `\r\r\n`), "content still
   correct". The number is arithmetically consistent (897 × 2 = 1794), and the end state is
   verifiable: the r4 tree has **CR=897, CRCR=0** in the source, and the inverse reconstruction
   reproduces r3 byte for byte. The stated fix ("rebuilt on bytes; the inverse reconstruction is the
   proof") is exactly what I independently reproduced.
2. **State leaked between measurement candidates** — the candidate that rebinds the module global
   `_AUTH_PATTERN` ran first, so the tree-as-it-stands candidate read the rebound pattern and the
   report said fix B changed nothing. The fix is verifiable in the artefact: `measure_r4.py:146`
   captures `tree_pattern = ob._AUTH_PATTERN` **before any candidate runs**, and `measure()` uses the
   captured pattern for the tree candidate (`token_class is None` branch, lines 93-96). The recorded
   output now shows fix B *does* change the leak set, i.e. the corrected behaviour is what is on
   disk.
3. **A second text-mode round trip in the harness build** — "source CR=0, output CR=251; the prefix
   check caught it". Consistent and verifiable: `run_i14d_oracle_r4.py` is **CR=0, LF=251**, matching
   the LF-only convention of `run_i14d_oracle.py` (CR=0, LF=233). The stated fix ("write bytes, never
   through text mode") holds for all four harness files (all CR=0).

So the record is accurate as far as it can be checked, and the fixes address the causes. The
generation's own generalisation — "text-mode round trips are the wrong tool for files whose line
endings are part of their identity" — is correct and is the right lesson.

### Claim 10 — what r4 did NOT do is honestly scoped — **CONFIRMED**

`handoff_r4.json.not_addressed_here` lists exactly `F-REV-R3-02, -03, -05, -06, -07, -08, -09, -10`.
Each is registered rather than dropped:

| finding | registration |
|---|---|
| `F-REV-R3-02` (carrier cited a verification that no longer reproduces) | `REMEDIATION_REGISTER.md` **REM-66**, status 已登记 |
| `F-REV-R3-03` (false "breaks stay OUTSIDE the match" comment) | **REM-67 ①**, 待修 |
| `F-REV-R3-05` (value delimiter immediately after the break) | **REM-67 ③**, 待修 |
| `F-REV-R3-06`…`-10` (five INFO) | **REM-68**, 已登记 |

`review.md` §r4 and `task_plan.md` Round 72 both say the same, and Round 72's boundary line
("未处理：`F-REV-R3-02`…`-10` —— 已登记，不在 r4 范围") matches. I confirmed the two the carrier
claims to have landed are the two that were landed (REM-65 → F-REV-R3-01; REM-67② →
F-REV-R3-04), and the other eight are exactly the eight that were not. One imprecision inside this
otherwise-correct scoping: REM-67 ①/③'s parenthetical asserts "r4 的注释已按事实改写" (r4's comment
was rewritten per the facts) while also saying F-REV-R3-03's correction was not made; the source
comment is in fact **byte-identical** between r3 and r4 (see F-REV-R4-01).

### Claim 11 — no verdict was pre-empted — **CONFIRMED**

```
handoff_r4.json : "status": "review_pending"   "verdict_expressed": false   "it_states_no_verdict": true
handoff_r3.json : "status": "review_pending"   "status_remains": "review_pending"
binding.json    : "verdict": "changes_required"        (the r1 verdict, unchanged)
task_plan.md    : Round 72 "不表达任何裁决"; "未做 status 转移（仍 review_pending）；未表达裁决；未代签"
REMEDIATION_REGISTER.md: REM-69 "r4 待独立复核 … verdict_expressed: false、status: review_pending"
```

`accepted_scoped` occurs in only three files in the whole attempt: `binding.json:19` (about
**I-14-C**'s r5 status, read-only), `reviewer_report_r2.md` and `reviewer_report_r3.md` (both in the
reviewers' own "why not accepted_scoped" reasoning). `review.md:111` and `:171` say explicitly that
r3 is *not* accepted. No record says r4 is accepted, and the card is still `review_pending`.

---

## 2. FINDINGS

### F-REV-R4-01 — **LOW: the source comment asserts the false ABNF justification and now contradicts the code it documents (the unlanded half of F-REV-R3-04)**

`observability.py:295-298` reads, unchanged from r3:

```
# It is now ONE RFC-7235 scheme token: `scheme = 1*<any CHAR except CTLs or
# separators>`, which always begins with a letter, so the class starts with
# `[A-Za-z]`; `|` is kept in it because the value delimiter class used everywhere
# else already stops at `|`, so nothing can gain a delimiter by this widening.
```

while `observability.py:317` is now

```
_AUTH_SCHEME_TOKEN = r"[A-Za-z0-9!#$%&'*+.^_\`|~-]+"
```

Two falsehoods in one sentence. (i) "which always begins with a letter" is the claim the r3 review
proved wrong — RFC 7230's `tchar` includes DIGIT and the specials, and RFC 7235 defines
`auth-scheme = token`. (ii) "so the class starts with `[A-Za-z]`" now describes a class that is not
in the file. The comment is **byte-identical between r3 and r4** — proved by the 4-region diff, which
contains no comment byte — so F-REV-R3-04's "narrower than the ABNF **the comment cites**" half was
not landed; only the class was widened. `oracle.md` C4.2 does correct the *reasoning* in the record,
so a reader of the record is not misled, but the code's own comment is, and it is the artefact a
maintainer reads. This is the F-REV-R3-03 species (a false source comment) recurring, and it also
makes `REMEDIATION_REGISTER.md` REM-67 ①/③'s parenthetical ("r4 的注释已按事实改写") inaccurate.

Reproduce:
```
"$PY" -B "$S/rev_addendum.py"          # prints the comment's class claim vs line 317
sed -n '295,298p;317p' "$A/iso/product_narrow_r4/src/company_wiki/source_catalog/observability.py"
diff -u <(sed -n '295,298p' "$A/iso/product_narrow_r3/src/company_wiki/source_catalog/observability.py") \
        <(sed -n '295,298p' "$A/iso/product_narrow_r4/src/company_wiki/source_catalog/observability.py")   # empty
```

### F-REV-R4-02 — **LOW: the measurement script and its pinned JSON both state that fix B is not in the tree**

`_r4_measure_20260922/measure_r4.py` lines 3-7 (module docstring):

> "r4 as built carries ONLY fix A … Fix B … is NOT in the tree; it is measured here by rebinding the
> pattern in memory, so the two fixes can be judged apart."

`measure_r4.py` lines 141-145 (`main()`, the same file):

> "The tree now carries BOTH fixes, so the two candidates are separated by REBINDING the token class
> in memory rather than by two trees: fix_A_only = the tree's own pattern rebuilt with the r3 token
> class … fix_A_and_B = the tree exactly as it stands"

The tree carries both: `observability.py:317` is the widened tchar class. So the docstring inverts the
method *and* states a false fact about the tree, and `r4_measurement.json` repeats it in the key
`"fix_b_measured_but_not_applied"`. That JSON is **byte-pinned by the carrier**
(`17f9ba52cc8a622cc187a4b5b290ded940d5e683c7a5e300683aaadb1f371a5a`), so the false statement is
frozen into the evidence. The measurement itself is correct: I re-ran the script and its output is
byte-identical to the recorded JSON, and the `fix_A_and_B` arm leaks only `C10` over the 19-probe set
while `fix_A_only` leaks the three non-letter probes too — which is only possible if the tree
carries fix B. This is a description defect, not a measurement defect, but it is the same species
(a record that does not match the tree) that produced F-REV-R3-02.

Reproduce:
```
sed -n '1,20p;134,150p' "$S/../../_r4_measure_20260922/measure_r4.py"
"$PY" -B "$S/measure_r4_rerun.py"        # writes $S/r4_measurement.json; cmp against the recorded one
cmp "$S/r4_measurement.json" "$S/../../_r4_measure_20260922/r4_measurement.json"
```

### F-REV-R4-03 — **INFO: `review.md` §r4 records two of the three self-inflicted errors**

`review.md:200` is headed "### Two self-inflicted errors, recorded rather than quietly fixed" and
lists the product-tree round trip and the measurement state leak. The third — the harness-build
`write_text` (source CR=0, output CR=251) — appears in `handoff_r4.json`
(`self_inflicted_errors_recorded`, 3 entries) and in `task_plan.md` Round 72, but not in `review.md`.
So claim 9 holds for the generation as a whole but not for every named carrier: a reader of
`review.md` alone sees two. Severity is INFO because the same generation discloses all three
elsewhere and `review.md` is a summary carrier.

Reproduce:
```
sed -n '200,210p' "$A/review.md"
"$PY" -B -c "import json;print(len(json.load(open('$A/handoff_r4.json'))['self_inflicted_errors_recorded']))"   # 3
```

### F-REV-R4-04 — **INFO: three pre-existing tracked files were rewritten on disk after the r3 carrier pinned two of them**

`harness/run_i14d_oracle.py`, `harness/run_rule_table_i14d.py` and `harness/apply_i14d_narrow.py` all
carry mtime **2026-09-22 00:52:28**, i.e. 24 minutes after `handoff_r3.json` (mtime 00:28:52) pinned
the first two. Their **bytes still match the pins** (`f7c94c60…`, `01a3187e…`), so the pin's meaning
is intact. `git show HEAD:<file>` gives the pinned hashes; `git show HEAD~1:<file>` gives
`db3789ac…` / `70316a35…`, i.e. the r3 harness content entered git only in the round-72 commit
(01:02:22).

**I classify this as a predicate limitation, not a data defect.** mtime is not content; the check
"is this file at its pin" is a content check, and it passes. The most likely mechanism is this
project's own documented pre-commit hook contract (`stash → git checkout -- . → replay`,
`task_plan.md:119`), which rewrites tracked working-tree files and has already caused one recorded
production rollback. The consequence for the record is narrow but real: `handoff_r4.json.boundaries.
r3_harnesses_untouched: true` and `task_plan.md` Round 72's "r3 的 harness 与 r3 的载体均未触碰" are
true of the bytes and false of the files' write history, and no r4 artefact records the write. I did
**not** determine who or what wrote them (see UNVERIFIED §5).

Reproduce:
```
find "$A" -type f -newermt "2026-09-22 00:00" -printf '%TH:%TM:%TS  %10s  %p\n' | sort
cd <repo>; D=.planning/2026-09-19-three-project-history-audit/execution_runs/I-14-D/a20260919-01/harness
for f in run_i14d_oracle.py run_rule_table_i14d.py; do
  git show "HEAD:$D/$f" | sha256sum; git show "HEAD~1:$D/$f" | sha256sum; sha256sum "$D/$f"; done
```

### F-REV-R4-05 — **MEDIUM: an unregistered, `product_base`-regressive credential-persistence family remains on the auth path**

**Shape.** `Authorization: <W>\n<credential>`, where `<W>` is a **single pre-break token that is not
an RFC-7230 `tchar` token** — i.e. it contains at least one character outside
`!#$%&'*+-.^_\`|~` / DIGIT / ALPHA (but not a value delimiter, which splits the token instead), or it
is itself such a character. The `_AUTH_SCHEME_SPLIT` branch cannot fire (`<W>` is not a scheme
token), so `_AUTH_BARE_VALUE` consumes `<W>`, stops at the break, and the credential's line — having
no `key=` prefix — is invisible to the assignment scanner.

```
r4   redact_text('Authorization: Bo?t\nghp_ZQ7ReviewerFakeCredential0123456789')
       -> 'Authorization: <redacted>\nghp_ZQ7ReviewerFakeCredential0123456789'      # credential persists
base redact_text('Authorization: Bo?t\nghp_ZQ7ReviewerFakeCredential0123456789')
       -> 'Authorization: <redacted>'                                               # credential gone
```

**The card's own marker is affected.** `Authorization: Bo?t\nSYNTHETIC_AUDIT_TOKEN` → marker
persists on r4; redacted on `product_base`. Exit criterion 2 ("纯合成 marker 必须仍被脱敏") is
operationalised as `credential_leaks == []`, and that list is `[]` only because no row covers this
shape.

**Size, measured on a 47-probe sweep of the pre-break token** (one non-tchar char inserted into
`Bo…t`, plus single-token non-tchar words, plus controls):

| tree | probes leaking | leaking but **not** leaking on `product_base` |
|---|---|---|
| `product_narrow` (r2) | 47 | 38 |
| `product_narrow_r3` | 44 | 35 |
| **`product_narrow_r4`** | **38** | **32** |
| `product_base` | 9 | — |

Of r4's 32 base-regressions, **one is the registered `C10` shape** (`Authorization: Bearer abc\n…`,
my probe `pre-ctrl-two-token`); the other **31 are not registered anywhere**. r4 introduces none of
them (`r4 \ r3 = ∅`), and it strictly reduces the family (44 → 38), so **this is not a defect r4
introduced** — it is a residual of the r2 narrowing that the r3 review's differential fuzz did not
report (its census concluded the auth-path remainder was "1,764 inputs, all of them non-letter-initial
schemes", which this family is not).

**Why MEDIUM and not higher.** The record nowhere claims this family is closed: `oracle.md` C3.4 and
the source comment both scope the fail-closed claim to *"after a scheme token and one or more line
breaks"*, which is accurate; and the shape is a malformed Authorization header (a non-tchar "scheme"
is not a scheme). **Why not lower.** The card's established standard — set by the r2 BLOCKER
F-REV-R2-01 and reaffirmed by the r3 review — is that `credential_leaks == []` is sound evidence only
when what survives is *enumerated*; the registered `C10` row is the precedent for how this family
should be treated. 31 unregistered base-regressive shapes, one of which persists the card's own
marker, is not enumerated. Cheapest correct handling: register the shape on both instruments with
the non-marker credential (one oracle row, one rule-table row), exactly as `R3a`/`open-two-token-then-wrap`
register `C10` — or close it. Registering is sufficient; the owner already accepts a registered open
residual on this path.

Reproduce:
```
"$PY" -B "$S/rev_probe.py"    --src "$A/iso/product_narrow_r4/src" --label r4 --tree r4 --out "$S/probe_product_narrow_r4.json"
"$PY" -B "$S/rev_prebreak.py" --src "$A/iso/product_narrow_r4/src" --label r4 --tree r4 --out "$S/prebreak_product_narrow_r4.json"
"$PY" -B "$S/rev_prebreak.py" --src "$A/iso/product_base/src"      --label base --tree base --out "$S/prebreak_product_base.json"
"$PY" -B "$S/rev_prebreak_cmp.py"        # prints the regression sets
```

### F-REV-R4-06 — **MEDIUM: the r4 record states the residual as a universal, and the universal is false**

`oracle.md` CORRECTION 4 **C4.5**, the r4 generation's own correction carrier:

> "Both fixes measured separately: `fix_A_only` closes the `?` leak and leaves the non-letter family
> leaking; **`fix_A_and_B` leaves only the registered `C10` residual.**"

That is true of the **19 probes** `measure_r4.py` runs (`REVIEWER_MATRIX` C1–C12 plus the seven
`R3_FAMILIES` probes) and false of the code: F-REV-R4-05 measures 31 further base-regressive leaking
shapes that are not `C10`. The same unqualified universal is repeated downstream, where it is read as
the state of the world rather than as a measurement result:

* `REMEDIATION_REGISTER.md` REM-67②: "✅ **r4 内有落点**：`:317` 放宽为**完整 RFC 7230 tchar**；
  `fix_A_and_B` 下**仅剩登记的 `C10`**"
* `task_plan.md` Round 72 measurement table, row `fix_A_and_B`, column 仍泄漏: "**仅 `C10`**"

The measurement is honest — `r4_measurement.json` records `leaking: ["C10"]` as a field of a named
probe set, and `handoff_r4.json` repeats it only as a measurement field — but the prose derived from
it is not, and this is precisely the F-REV-R3-02 species (citing a measurement as if it were
general) recurring in the generation that was supposed to be answering F-REV-R3-02. Note the irony
worth recording: F-REV-R3-02 is listed in `handoff_r4.json.not_addressed_here` as deferred, yet its
mechanism reappears here in the r4 record.

Fix: state the probe set ("over the 19 probes in `measure_r4.py`") and register the residual family
per F-REV-R4-05, or drop the "only".

Reproduce:
```
sed -n '511,526p' "$A/oracle.md"
grep -n "仅剩登记的" <planning>/REMEDIATION_REGISTER.md
sed -n '1773,1781p' <planning>/task_plan.md
"$PY" -B "$S/rev_prebreak_cmp.py"
```

---

## 3. UNVERIFIED

1. **The copied pytest suites and the real worker/CLI exit were not run.**
   `harness/tests/test_i14c_real_exit_redaction.py`, `harness/tests/test_i14d_single_token.py`,
   `harness/run_exit_probe.py`, `harness/run_real_cli_exit.py` — not executed by me. Every leak
   reported here (including F-REV-R4-05) is measured at the `redact_text` helper, not end-to-end; I
   did **not** demonstrate the `Bo?t`-shaped credential reaching a persisted event log. The r3 review
   left the same gap.
2. **No mutation arm was exercised.** M1/M2/M3 were not re-run and M4 was not used; I substituted
   the r3 tree and `product_base` as the differential arms, which is sufficient for the leak
   direction of these fixes but is not the same instrument. The r2/r3 reviews' mutation results are
   carried, not re-measured.
3. **`boundaries.deletions: 0` cannot be independently verified.** There is no pre-r4 inventory of
   the attempt, so I can neither confirm nor refute that nothing was deleted. I confirmed only that
   the r4 tree differs from the r3 tree in exactly one file, that the production anchor is unchanged,
   and that the r3 harnesses and r3 carriers are at their pins.
4. **`boundaries.product_repo_written: 0` was checked only at the anchor.**
   `scripts/model_registry.py` = `9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f`
   / 26446 B, unchanged — confirmed. I did not sweep the rest of the `company-wiki` /
   `revenue-forecast` working trees for other modifications.
5. **The cause of the 00:52:28 rewrite (F-REV-R4-04) is not established.** I verified the mtimes, the
   pins, and the `HEAD`/`HEAD~1` hashes, and I noted the project's documented pre-commit stash/replay
   hook as the plausible mechanism; I did not determine who or what performed the write, and I did
   not inspect the git reflog or the hook.
6. **The historical intermediate states are not independently verifiable.** The claimed `CR 1794`
   product tree and the claimed "fix B changed nothing" first measurement are not on disk (as far as
   I looked); I verified the *arithmetic* of the former (897 × 2) and the *fix* for the latter, not
   the incidents themselves.
7. **ReDoS / timing was not re-timed.** The r4 change does not touch the quantifier structure
   (region 0+1 narrow the class; regions 2+3 delete two characters), so I did not expect a timing
   change and did not measure one.
8. **`scratch/` was not audited.** The r4 generation's ~30 scratch scripts were not read or run; I
   do not know whether any of them registers the F-REV-R4-05 shape or the `Bo?t` family.
9. **The r3 reviewer's differential-fuzz corpus was not reconstructed.** I assert only that the
   r3 review's published census ("all of them non-letter-initial schemes") does not include the
   pre-break non-tchar family, because that family starts with letters; I did not re-run its fuzz to
   find out whether the corpus could generate the shape.
10. **Downstream consequence of the over-redaction family** (whether any consumer depends on the
    deleted diagnostic key) was not investigated — same gap the r3 review recorded.

---

## 4. HOW TO REPRODUCE

```
A  = <attempt> = .../execution_runs/I-14-D/a20260919-01
S  = .../execution_runs/_review_i14d_r4_20260922        # reviewer scratch, outside the attempt
PY = "$A/iso/venv/Scripts/python.exe"                   # python 3.13.9, PyYAML 6.0.3
```
Every command below ran with `PYTHONDONTWRITEBYTECODE=1` and `-B`, so no `__pycache__` entry was
added to the attempt. The only file written into the attempt is `reviewer_report_r4.md`.

```bash
# 0. every pinned hash, recomputed from the bytes
"$PY" -B "$S/rev_carriers.py"          # product copy, 4 harnesses, 2 carriers, prefix hashes, anchor
sha256sum <repo>/scripts/model_registry.py

# 1. the byte diff and the inversion (claim 1)
"$PY" -B "$S/rev_claim1_bytes.py"
"$PY" -B "$S/rev_line_endings.py"      # whole-tree comparison + CR census
"$PY" -B "$S/rev_addendum.py"          # all-4-regions inversion + drop-one controls + class identity

# 2. the four harness runs (claims 4, 5, 6)
"$PY" -B "$A/harness/run_i14d_oracle_r4.py"     --src "$A/iso/product_narrow_r4/src" --label r4   --out "$S/oracle_r4_on_r4.json"
"$PY" -B "$A/harness/run_i14d_oracle_r4.py"     --src "$A/iso/product_narrow_r3/src" --label r3   --out "$S/oracle_r4_on_r3.json"
"$PY" -B "$A/harness/run_i14d_oracle_r4.py"     --src "$A/iso/product_base/src"      --label base --out "$S/oracle_r4_on_base.json"
"$PY" -B "$A/harness/run_rule_table_i14d_r4.py" --src "$A/iso/product_narrow_r4/src" --label r4   --out "$S/rule_r4_on_r4.json"
"$PY" -B "$A/harness/run_rule_table_i14d_r4.py" --src "$A/iso/product_narrow_r3/src" --label r3   --out "$S/rule_r4_on_r3.json"
# rcs: oracle 0 / 3 / 3 ; rule 3 / 3

# 3. the frozen r3 harnesses on both trees (claim 5)
"$PY" -B "$A/harness/run_i14d_oracle.py"        --src "$A/iso/product_narrow_r3/src" --label r3 --out "$S/r3oracle_on_r3.json"
"$PY" -B "$A/harness/run_i14d_oracle.py"        --src "$A/iso/product_narrow_r4/src" --label r4 --out "$S/r3oracle_on_r4.json"
"$PY" -B "$A/harness/run_rule_table_i14d.py"    --src "$A/iso/product_narrow_r3/src" --label r3 --out "$S/r3rule_on_r3.json"
"$PY" -B "$A/harness/run_rule_table_i14d.py"    --src "$A/iso/product_narrow_r4/src" --label r4 --out "$S/r3rule_on_r4.json"
"$PY" -B "$S/rev_rows.py"              # row-by-row: 0 differing rows in all four comparisons

# 4. the class-level leak probes (claims 2, 3; F-REV-R4-05)
for t in product_narrow_r4 product_narrow_r3 product_narrow product_base; do
  "$PY" -B "$S/rev_probe.py"    --src "$A/iso/$t/src" --label "$t" --tree "$t" --out "$S/probe_$t.json"
  "$PY" -B "$S/rev_prebreak.py" --src "$A/iso/$t/src" --label "$t" --tree "$t" --out "$S/prebreak_$t.json"
done
"$PY" -B "$S/rev_prebreak_cmp.py"

# 5. the measurement, re-run as a patched copy (claims 3, 8; F-REV-R4-02)
cp "$S/../../_r4_measure_20260922/measure_r4.py" "$S/measure_r4_rerun.py"   # HERE.parent must be execution_runs
"$PY" -B "$S/measure_r4_rerun.py"
cmp "$S/r4_measurement.json" "$S/../../_r4_measure_20260922/r4_measurement.json"   # identical

# 6. responsiveness (every predicate fed a mutated input)
"$PY" -B "$S/rev_responsive.py"

# 7. the r3 source delta has no registered diff artefact, so produce it
diff -u "$A/iso/product_narrow_r3/src/company_wiki/source_catalog/observability.py" \
        "$A/iso/product_narrow_r4/src/company_wiki/source_catalog/observability.py"   # 4 regions, 2 lines

# 8. provenance of the r3 harnesses (F-REV-R4-04)
find "$A" -type f -newermt "2026-09-22 00:00" -printf '%TH:%TM:%TS  %10s  %p\n' | sort
```

Reviewer artefacts written (all outside the attempt): `$S/{rev_claim1_bytes,rev_line_endings,rev_probe,
rev_prebreak,rev_prebreak_cmp,rev_rows,rev_carriers,rev_responsive,rev_addendum,rev_cr,measure_r4_rerun}.py`
and `$S/{probe_*,prebreak_*,oracle_*,rule_*,r3oracle_*,r3rule_*,r4_measurement}.json`.

---

## 5. RESPONSIVENESS OF MY OWN CHECKS

`rev_responsive.py` calls each predicate twice — once on the real data, once on a mutation held in
memory — and **11 of 12 go red on the mutation**:

| predicate | real | mutation that turned it red |
|---|---|---|
| `sha256(r4 product copy) == pin` | holds | one byte flipped at offset 100 |
| `diff regions(r3, r4) == 4` | holds | r3 fed against itself (0 regions) |
| `recorded r4 oracle run == my re-run` | holds | one row's `out` set to `"MUTATED"` |
| `28 r3 oracle rows identical on r3 vs r4 tree` | holds | **the base-tree run** |
| `over_redaction rows == 9 on the r4 tree` | holds | one row id deleted from the list |
| `Q_leaks(r4) == ['Q-scheme-with-q']` | holds | **the r3 probe** (17 leaks) |
| `CH_leaks(r4) == {0x0a, 0x0d}` | holds | **the r3 probe** (adds 0x3f) |
| `NL_leaks(r4) == []` | holds | **the r3 probe** (28 leaks) |
| `measure_r4 rerun == recorded r4_measurement.json` | holds | one byte flipped in my copy |
| `oracle.md prefix[:27119] == registered before_sha256` | holds | one byte flipped at offset 100 |
| `grep r4 row ids finds 0 in the r3 oracle harness` | holds | an `N5l…` comment appended to the string |

**The one that did not go red, and why — classified rather than believed.**
`invert(r3, r4) == r3 byte-for-byte` stayed true when I mutated byte 100 of r4, because the inversion
is *constructive*: it recomputes the differing regions and copies r3's bytes into them, so it repairs
any mutation inside a region and ignores any mutation outside one. That predicate is therefore
near-tautological as I first wrote it. I replaced it with the mutation that actually tests the claim
— **drop one of the four regions and re-invert** (`rev_addendum.py`):

```
invert(all 4 regions) == r3 : True
invert(drop region 0) == r3 : False
invert(drop region 1) == r3 : False
invert(drop region 2) == r3 : False
invert(drop region 3) == r3 : False
```

so the inversion claim is responsive once tested with the right control, and it also proves each of
the four regions is load-bearing. The general lesson matches the project's own: the failing
predicate was a *predicate* error, not a data defect — and the fix was to find the control the
predicate could actually fail on.

Two further responsiveness facts worth recording. (a) The two r3-harness greps are responsive in
both directions: the r4 row ids are absent from the r3 harnesses, and the *same* greps find them in
the r4 harnesses. (b) The `diff regions == 4` instrument is anchored by a second reading on a
different pair (r3 vs r3 → 0), so it is not just counting a constant.

---

## 6. ADJUDICATION

**Does r4 land what it claims? Yes, and the claims are unusually clean.** Every one of the eleven
claims is CONFIRMED; none is REFUTED; none is UNVERIFIABLE. Concretely, and re-derived by me from the
bytes rather than read from the record:

* r4 differs from r3 in **exactly four byte regions**, all on lines 317 and 320, and inverting them
  reproduces r3 **byte for byte** with CR 897 in both; `observability.py:319`'s `\r?\n` is
  deliberately and correctly left alone.
* The `?` leak is closed **at the class level**, not for two strings: the after-break quoted
  alternatives are now byte-identical to `_QUOTED_VALUE`, the character sweep leaves only `\n`/`\r`
  (which `_QUOTED_VALUE` also excludes), and `r4 \ r3 = ∅` on the leak sets.
* The non-letter-scheme regression is closed and r4 is **strictly better than `product_base`** on it
  (base leaks 3 of 30, r3 leaks 28, r4 leaks 0).
* The eight new rows are registered and **all eight are load-bearing**; the four oracle expectations
  are **derivable from the specification independently of the code**, by one-substitution derivation
  from the already-frozen and already-reviewed `N5c`/`N5k` rows — I settle the provenance question in
  the affirmative, while recording that the provenance itself is weaker than `oracle.md` §2 requires.
* **No pre-existing row moves** (0 field differences across 28 + 79 rows), the over-redaction family
  is unchanged at 9 rows, generation isolation is real, every registered hash reproduces, the three
  self-inflicted errors are recorded with verifiable fixes, the eight deferred findings are
  registered, and no verdict was pre-empted.

**Why not `accepted_scoped`.** Because two of the things r4 leaves standing are not documentation
noise. The auth path still persists a credential — including this card's own synthetic marker — for a
family of pre-break shapes that `product_base` redacts, is enumerated nowhere, and is 31 shapes wide
once the registered `C10` shape is removed (**F-REV-R4-05**). And the r4 generation's own record
states that residual as a universal ("leaves only the registered `C10` residual"), which is the
F-REV-R3-02 species recurring in the generation that was supposed to answer F-REV-R3-02
(**F-REV-R4-06**). The card's standard, set by F-REV-R2-01 and reaffirmed by the r3 review, is that
`credential_leaks == []` is sound evidence only when what survives is *enumerated*; it is not, and
accepting would again offer that field as an exit criterion for a class it cannot see. Neither
finding is a defect in the two fixes, and neither is introduced by r4 — but both are in r4's tree and
r4's record, and r4 is the revision on the table.

**Why not `cannot_adjudicate`.** Every claim was measurable with the attempt's own interpreter and
its own harnesses; nothing I needed was missing. The three documentation findings (F-REV-R4-01/-02)
and the provenance note (F-REV-R4-04) are likewise byte-verifiable.

**Cheapest path to green.** (1) Register the pre-break non-tchar family on both instruments with the
non-marker credential — one oracle row, one rule-table row, alongside `R3a`/`open-two-token-then-wrap`
— **or** close it; registering is sufficient and is the cheaper of the two. (2) Correct `oracle.md`
C4.5's "only the registered `C10` residual" to name the probe set, and correct the same phrase in
`REMEDIATION_REGISTER.md` REM-67② and `task_plan.md` Round 72. (3) Correct the source comment at
`observability.py:295-298` so it stops asserting the leading-letter ABNF and stops describing a class
the file does not contain. (4) Correct `measure_r4.py`'s docstring and the
`fix_b_measured_but_not_applied` key. (5) Add the third self-inflicted error to `review.md` §r4, or
re-head the section. (6) Re-run the oracle, the rule table and the two suites.

**What this review grants.** A byte-pinned, independently re-derived confirmation that both r4 fixes
are exactly what the carrier says, are class-level, are load-bearing and introduce no regression;
that the eight new rows are registered and go red on the pre-fix tree; that their expectations are
derivable from the specification; that no pre-existing row moved; that generation isolation is real;
that `handoff_r4.json` overstates nothing; that the three self-inflicted errors are recorded and
fixed; that the deferred findings are registered; and that the card was not pre-empted. **What it
does not grant:** acceptance, until the residual family is registered (or closed) and the "only
`C10`" statement is brought back to what the measurement supports.

---

*Reviewer's note on process: this review wrote exactly one file into the attempt
(`reviewer_report_r4.md`) and deleted, moved or cleaned up nothing. All instruments and outputs live
under `execution_runs/_review_i14d_r4_20260922/`. Every harness invocation used the attempt's own
interpreter with `-B` and `PYTHONDONTWRITEBYTECODE=1`; no `__pycache__` entry was added. The one
in-memory pattern substitution used to test responsiveness was applied to a loaded module object, not
to a file on disk.*
