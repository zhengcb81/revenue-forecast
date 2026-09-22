# I-14-D r5 — INDEPENDENT REVIEW

Reviewer: an independent subagent, not the author of any of this, working from
`_review_i14d_r5_20260922/DISPATCH.md` and nothing else. The verdict below is mine; nothing
in the dispatch asked me to agree with anything.

Date: 2026-09-22 (UTC). Interpreter used for every number below:
`<attempt>/iso/venv/Scripts/python.exe` (CPython 3.13.9, PyYAML 6.0.3).

---

## 1. VERDICT

**VERDICT: `changes_required`**

**Scope this verdict covers**

* the r5 product copy `iso/product_narrow_r5/src/company_wiki/source_catalog/observability.py`
  (43362 B, sha256 `ca13fb81aa2a1234ba760f49576a6409bbd3b1397f921f2e73311f90a263fc45`) and its
  byte-level relationship to the r4 pre-image;
* the pre-break token class as a *class* — swept over the whole printable complement at the
  scheme position, on all five generations;
* `harness/run_i14d_oracle_r5.py`, `harness/run_rule_table_i14d_r5.py` and the rows they carry;
* the r3/r4 harness byte-pins and the r5 rows' generation isolation;
* the r5 carriers `handoff_r5.json`, `oracle.md` CORRECTION 5, `review.md` `## r5`, and the
  three copies of the corrected sentence;
* the repository-level finding about `iso/` and its remedy;
* the card's status.

**What this verdict does NOT cover**

* the copied pytest suites (`harness/tests/*`) and the real worker/CLI exit — I did not run
  them; every leak reported here is measured at the `redact_text` helper, not end-to-end. I did
  not demonstrate a credential reaching a persisted event log.
* the mutation trees M1–M4 beyond the single in-memory class swap used as a negative control;
* promotion, `disclosure_adaptation`, accuracy, mapping, or any downstream consumer of the
  deleted diagnostic key;
* the correctness of the r2/r3/r4 generations beyond the differential arms I re-ran;
* anything in the product repositories, which I did not write to.

**Shape of this verdict, stated plainly, because it is the fourth of its kind**

The *fix direction* is right and I confirmed most of what the dispatch asked me to test: the
base-regressive family F-REV-R4-05 really is closed **at class level** (I swept it, not four
shapes), no registered row moved, every registered hash reproduces from the bytes, the comment
block is materially true, and the overstated sentence is corrected in all three carriers with
its domain attached. The verdict is nevertheless `changes_required`, for two reasons:

1. **the class swap was also a narrowing, and it re-opened three characters** that r3 and r4
   redacted (`&`, `'`, `|`) — six unregistered credential-persistence shapes, measured
   (`F-REV-R5-01`, MEDIUM). r5 is the first revision since r2 to leak a shape its own pre-image
   redacted: measured over the same 96-character sweep, `r3 \ r2 = []` and `r4 \ r3 = []`, while
   `r5 \ r4 = ['&', "'", '|']`.
2. **the record asserts the family is closed on a measurement set that does not contain the
   family** (`oracle.md` C5.1: "closes the whole family at zero cost", priced by
   `measure_r5.py`, whose non-tchar probe list has 4 entries out of a family the r4 reviewer
   sized at 31). This is `F-REV-R4-06` recurring in the generation that corrected
   `F-REV-R4-06`, resting on literally the same 19-probe set that C5.3 identifies as
   insufficient (`F-REV-R5-02`, MEDIUM).

Either one alone is a MEDIUM by this card's own calibration (`F-REV-R4-05` was MEDIUM and drove
`changes_required`). Neither is a base regression: `product_base` leaks the `F-REV-R5-01` shapes
too. I say so explicitly so that the owner can price this correctly — the cost of fixing is one
character class, not a redesign.

---

## 2. THE THIRTEEN CLAIMS

### Claim 1 — the widening is real and byte-correct — **CONFIRMED** *(with the word "widening" reserved to Claim 3)*

Measurement. `diff45.py` + `linediff45.py`. r4 (42829 B, `15446f4d…`) vs r5 (43362 B,
`ca13fb81…`):

* `difflib.SequenceMatcher` over CRLF-split lines yields **exactly one non-equal opcode**:
  `replace r4[290..318] -> r5[290..325]`. In r4 that span is 27 comment lines (290–316) plus
  **two code lines** (317 `_AUTH_SCHEME_TOKEN = …`, 318 `_AUTH_SCHEME_SPLIT = (r"(?:" + _AUTH_SCHEME_TOKEN …`);
  in r5 it is 34 comment lines (290–323) plus two code lines (324 `_AUTH_PREBREAK_TOKEN = …`,
  325 the split's first line).
* Nothing else moved: `r4 lines 1..289 == r5 lines 1..289` (True) and
  `r4 lines 319..897 == r5 lines 326..904` (True). Shift = +7 lines.
* **Inversion**: splicing r4's middle into r5's frame yields sha256
  `15446f4da6ba256f039e684eaa4bd0c6f45889dc86a624717c6a0ec836e3f2a1` — byte-for-byte r4.
* **Line endings**: r5 CR = LF = CRLF = 904, lone CR = 0, lone LF = 0. r4 the same at 897.
* **Rename**: `_AUTH_SCHEME_TOKEN` present in r4 / absent in r5; `_AUTH_PREBREAK_TOKEN` absent in
  r4 / present in r5.
* The bookkeeping copies `i14d_r4_observability.py` and `i14d_r5_observability.py` are byte-equal
  to the two trees (True/True).

### Claim 2 — the F-REV-R4-05 family is closed — **CONFIRMED** *(at class level; the sweep is the evidence, not the four rows)*

Measurement. `sweep.py`. I did not accept four shapes. I inserted **every printable character**
at the pre-break position of `Authorization: Bo<c>t` + LF + credential, on all five generations.

The complement of the new class `[^\s,;&"'|]` is exactly `\s , ; & " ' |`. Results at the
pre-break position (marker form):

| `<c>` | base | r2 | r3 | r4 | **r5** |
|---|---|---|---|---|---|
| `( ) / : < = > ? @ [ \ ] { }` (14 chars) | ok | LEAK | LEAK | LEAK | **ok** |
| `,` `;` `"` | LEAK | LEAK | LEAK | LEAK | LEAK |
| `&` `'` `\|` | LEAK | LEAK | ok | ok | **LEAK** |
| space, TAB | ok | LEAK | LEAK | LEAK | LEAK |

So the **base-regressive** part of the family — the part the r4 reviewer defined and sized at 31
shapes, i.e. a non-tchar pre-break token that contains no value delimiter — is **closed on r5**:
all 14 non-tchar, non-delimiter characters are redacted, against 14 leaks on r4. The rows
`N5p`–`N5s` are load-bearing, not decorative: they go RED on the r4 tree and on the r3 tree
(`r5oracle_on_product_narrow_r4.json`, `r5oracle_on_product_narrow_r3.json`).

Two qualifications, both measured, both load-bearing for other claims:

* `,` `;` `"` still leak on **every** generation including `product_base`. They are value
  delimiters, so the r4 reviewer's definition excludes them ("but not a value delimiter, which
  splits the token instead"), and they are not base-regressive. Not new, not a r5 defect — but
  they are *also* not closed, and `credential_leaks == []` does not see them.
* space/TAB still leak, which is the registered two-token-then-wrap residual (`R3a`), and is
  correct by design — with one gap: the *registered* rows declare the **secret** surviving, so the
  **marker** form of the same shape (`Authorization: Bearer abc\nSYNTHETIC_AUDIT_TOKEN` →
  `Authorization: <redacted>\nSYNTHETIC_AUDIT_TOKEN`) is invisible to `credential_leaks`, which is
  `[]`. See F-REV-R5-08.

Whole-sweep leak-set sizes at this position, for the record: `product_base` 6 characters,
r2 96, r3 19, r4 19, **r5 8**. Set differences: `r3 \ r2 = []`, `r4 \ r3 = []`,
**`r5 \ r4 = ['&', "'", '|']`**.

### Claim 3 — the widening introduced no new leak family of its own — **REFUTED**

Measurement. `sweep.py`, `negative_controls.py`, `claims467.py`.

The new class is **not a superset of the class it replaced**. Measured set difference:

```
chars in r4's class but NOT in r5's class : ['&', "'", '|']
chars in r5's class but NOT in r4's class : ['(', ')', '/', ':', '<', '=', '>', '?', '@', '[', '\\', ']', '{', '}']
=> r5 class is a SUPERSET of r4 class: False
```

`&`, `'` and `|` are all RFC-7230 `tchar`s, all three were matched by r4's class, and none is in
r5's. The consequence, measured:

```
Authorization: Bo&t\nSYNTHETIC_AUDIT_TOKEN
  r3 -> 'Authorization: <redacted>'                      # credential gone
  r4 -> 'Authorization: <redacted>'                      # credential gone
  r5 -> 'Authorization: <redacted>&t\nSYNTHETIC_AUDIT_TOKEN'   # credential PERSISTS
```

Identical results for `Bo't` and `Bo|t`, and for the 39-char non-marker credential followed by
`doc=17`. So **six unregistered credential-persistence shapes** (3 characters × 2 credential
forms) exist on r5 and did not exist on its own pre-image. `product_base` leaks them too, so they
are **not** base-regressive — but r5 is the first revision in this card's history to *introduce*
a leak shape, and the record does not mention them anywhere. On a class-level reading, the
honest description of r4→r5 is **a swap, not a widening**: +14 characters, −3 characters.

Reproduced independently outside my scratch scripts:

```
cd <repo>/.planning/2026-09-19-three-project-history-audit/execution_runs/I-14-D/a20260919-01
./iso/venv/Scripts/python.exe -c "
import importlib.util,sys
def L(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s)
    sys.modules[n]=m;s.loader.exec_module(m);return m
r4=L('a',r'iso/product_narrow_r4/src/company_wiki/source_catalog/observability.py')
r5=L('b',r'iso/product_narrow_r5/src/company_wiki/source_catalog/observability.py')
t='Authorization: Bo&t\nSYNTHETIC_AUDIT_TOKEN'
print('r4:',repr(r4.redact_text(t)));print('r5:',repr(r5.redact_text(t)))"
```

### Claim 4 — the four new rows are registered and their expectations derivable — **CONFIRMED**

Measurement. `claims467.py`; harness row dumps.

* Registered: `N5p-auth-nontchar-question-marker`, `N5q-auth-nontchar-slash-secret`,
  `N5r-auth-nontchar-colon-marker`, `N5s-auth-nontchar-equals-marker` in
  `run_i14d_oracle_r5.py`; `cred-auth-nontchar-{question,slash,colon,equals}` in
  `run_rule_table_i14d_r5.py`. The r5 oracle harness holds 36 cases and the rule table 87 rows,
  i.e. the r4 sets (32 / 83) plus exactly these four and four.
* Derivable independently of the code: I re-derived the expected lengths from the stated
  semantics before running anything — `"Authorization: "` = 15, `"<redacted>"` = 10, so the
  single-line form is **25**; adding `"\n"` + `"doc=17"` gives **32**. The tree agrees on all
  four: 25 / 32 / 25 / 25. The mechanism in C5.2 (key group consumes `Authorization: `, the split
  consumes the token plus the break run, the tail consumes the credential, and the break before a
  following `doc=17` line is not consumed) is what produces them, and I verified each step.
* Load-bearing: all four are RED on the r4 tree (oracle) and produce `fidelity_ok: false` on the
  r4 tree (rule table). So they are not green-washing.

**Disclosure acted on.** The dispatch says their expected strings were observed from the tree and
then frozen. I cannot determine from the artefacts alone whether observation or derivation came
first — neither `measure_r5.py` nor the harness carries an ordering proof. What I *can* report is
that the strings are derivable from the stated semantics and correct; and that the derivation in
C5.2 is expressed in the vocabulary of the regex's own parts, so it is a derivation from the
mechanism restated as specification rather than an independent one. That is a real but small gap,
and it is the same shape as the r4 disclosure. Noted, not blocking.

### Claim 5 — no regression — **CONFIRMED**

Measurement. `rowbyrow.py`, comparing the *recorded rows themselves* field by field, not just the
verdicts.

| instrument | rows | on r4 tree | on r5 tree | differing | order preserved |
|---|---|---|---|---|---|
| r4 oracle (r3+r4 rows) | 32 | 32 | 32 | **0** | True |
| r4 rule table (r3+r4 rows) | 83 | 83 | 83 | **0** | True |
| r3 oracle (r3 rows) | 28 | 28 | 28 | **0** | True |
| r3 rule table (r3 rows) | 79 | 79 | 79 | **0** | True |
| r5 oracle (all 36) | 36 | 36 | 36 | **4** | True |
| r5 rule table (all 87) | 87 | 87 | 87 | **4** | True |

The only four differing rows in the r5 instruments are the four new ones, and they differ in
exactly the intended direction (fail on r4, pass on r5). No pre-existing row moved anywhere.

### Claim 6 — the over-redaction family is unchanged, `C10` residual by design — **CONFIRMED** *(for the registered family; see the class-level qualification in F-REV-R5-02)*

Measurement. `claims467.py`.

* The nine `over_redaction` rows (`over-auth-scheme-then-key`, `-reqid`, `-stage`,
  `over-auth-token-then-keys`, `-crlf-then-key`, `-obsfold-then-key`, `over-proxy-auth-then-key`,
  `-scheme-then-marker`, `over-auth-generic-then-key`) produce byte-identical outputs on r4 and
  r5, and `over_redaction_touched` is the same nine-element set in both harness runs.
* The registered residual survives by design: `Authorization: Bearer abc\n<39-char credential>`
  → `Authorization: <redacted>\n<39-char credential>` on r4 and on r5; the rule table reports it
  as `open-two-token-then-wrap` in `registered_open_leaking`, and `credential_leaks` stays `[]`.
* Qualification, measured: relative to r4 the *class-level* over-redaction set grew by exactly
  the 14 non-tchar non-delimiter characters — `Authorization: Bo?t\ndoc=17` keeps `doc=17` on r4
  and deletes it on r5. `product_base` deletes it too, so this is not a new cost; it is the other
  face of closing the leak. The word "unchanged" is true of the registered family and of base,
  and false of the r4→r5 delta. Recorded under F-REV-R5-02.

### Claim 7 — the comment block now says what the code does — **CONFIRMED**, with two exceptions recorded as F-REV-R5-03

Measurement. `claims467.py` (each sentence tested), plus an in-memory reconstruction of the
alternative candidate the block names.

True, verified:

* "The breaks are consumed by the match" — `Authorization: Bearer\n<marker>` → `Authorization: <redacted>` (25). No break survives. ✔
* "Fail CLOSED: after that token and one or more line breaks (a blank line included), the next token - or a quoted string reached through the same break run - is redacted" — blank-line variant `Authorization: Hawk\n\n<39-char credential>` → `Authorization: <redacted>` (25). ✔
* "`Authorization: Bearer` + newline DELETES `doc=17`" — ✔ (25 chars, key gone).
* "No RFC scheme production is claimed any more"; "the token is now whatever the value grammar calls a token" — `_AUTH_PREBREAK_TOKEN == _BARE_VALUE` is `True` (`'[^\\s,;&\\"\'|]+'`), and `_AUTH_BARE_VALUE` is that class plus `(?:[ \t]+…)*`. The ABNF sentence is gone. ✔
* "nothing can gain a delimiter by this widening" — true: none of the 14 added characters is in `_VALUE_STOP_CHARS = ",;&\"'|"`. ✔
* "One shape stays OPEN and is registered rather than hidden: a TWO-token value that then wraps" — R3a/R3b, registered on both instruments. ✔
* "Closing it needs the whole first line consumed as a token run, which deletes `doc=17` from `Authorization: Bearer <marker>` + newline + `doc=17` + newline + `stage=`" — **independently reproduced in memory**: with the pre-break token widened to `_AUTH_BARE_VALUE`, that exact input yields `Authorization: <redacted>\nstage=` (doc=17 deleted) where r5 yields `Authorization: <redacted>\ndoc=17\nstage=`. ✔ And the cited directory `_r3_design_reprobe_20260922/` exists and **is committed** (2 files). ✔
* "`r3_fix_record.md` … was never written and is deliberately NOT substituted for" — confirmed against `handoff_r3.json.not_written`. ✔

Not true / not cleanly true:

* "**the indentation** and the keys on the lines AFTER the redacted one are not [consumed]" — true only under the reading "the indentation *on the lines after the redacted one*". Under the reading "the indentation of the redacted line is not consumed" it is **false**: `Authorization: Bearer\n  <marker>` → `Authorization: <redacted>` (25 chars — the two spaces are consumed; this is also the frozen N5d expectation). Since this sentence *is* the correction for `F-REV-R4-01`, and the defect it corrects was exactly a wrong claim about this mechanism, the ambiguity should be removed rather than argued. → F-REV-R5-03 (LOW).
* "That token has been **widened** three times" — the third change is not a widening; it removes three characters (Claim 3). → F-REV-R5-02.
* "`|` is not in the class because the value delimiter class used everywhere else already stops at `|`, so nothing can gain a delimiter by this widening" — both clauses true, but the justification is silent about the coverage *lost* by excluding `|` (and `&`, `'`), which is precisely F-REV-R5-01. A comment that justifies a choice by the argument for its safe direction, in the sentence that introduces the defect, is the same species as the r4 comment it replaces.
* The pointer `_r3_design_reprobe_20260922/` is a bare directory name inside product source. It resolves (it exists, committed, one level up from the attempt) but not from the file's own location; the previous dangling reference at least named a file. INFO only.

### Claim 8 — the correction of the overstated sentence is adequate — **CONFIRMED**

Measurement. `git grep` over the planning tree for the sentence in both languages, plus reading
each correction.

The original appears as an **assertion** in exactly three places, as the dispatch says:

| carrier | original | correction | domain carried? |
|---|---|---|---|
| `oracle.md` C4.5 (line 524) | "`fix_A_and_B` leaves only the registered `C10` residual" | C5.3 (lines 566–583): "**That is false as written.** … The corrected form, with its domain attached: > On the 19 probes reported in C4.5, `fix_A_and_B` leaves only the registered `C10` residual. It is **not** a statement about the family in general" | **yes** |
| `REMEDIATION_REGISTER.md` §16 REM-67② (line 262) | "`fix_A_and_B` 下**仅剩登记的 `C10`**" | §18.1 (lines 299–303): "该句作为普遍断言是假的 … **带域的更正写法**：**在那 19 个探针上**，`fix_A_and_B` 仅剩登记的 `C10` 残留" | **yes** |
| `task_plan.md` Round 72 (line 1778) | "**仅 `C10`**" | Round 74 (lines 1866–1874): "**在 Round 72 报告的那 19 个探针上**，`fix_A_and_B` 仅剩登记的 `C10` 残留——**这不是关于该族的普遍陈述**" | **yes** |

Originals retained (append-only), each correction names the other two copies consistently, and
each records that this is `F-REV-R3-02` recurring. Corrections also propagated to `findings.md`
(line 501) and `progress.md` (line 808), which is beyond the requirement. No fourth assertion copy
exists. Adequate.

### Claim 9 — **does r5's own record overstate anywhere?** — **REFUTED (yes, in one place, and it is the same species)**

This is the claim I was told to try hardest on, and it is the one that fails.

**The sentence.** `oracle.md` C5.1 (lines 547–550), r5's own correction carrier:

> "**Priced before it was taken** (`_r5_measure_20260922/measure_r5.py`): widening to the value
> token **closes the whole family** at **zero cost** — oracle 0 failures, rule table 0 failures,
> and the over-redaction family **unchanged**"

**Why it overstates.** The sentence names a measurement set, and the set does not contain its
subject. `measure_r5.py`'s `FAMILIES` list has seven probes, of which the ones in the
F-REV-R4-05 family are four (`non-tchar-question`, `-question-secret`, `-slash`, `-equals`,
`-colon` — five entries, four distinct characters), plus the twelve-probe `MATRIX` and four
`OVER` probes: **19 probes total**, of which four are family members. The family the r4 reviewer
measured is **31 base-regressive shapes**, and at the class level it has ≥14 members. So
"closes the whole family" is a universal conclusion carried on 4 of ≥14. That is structurally
identical to C4.5's "leaves only the registered `C10` residual", which is what C5.3 — nine
paragraphs above it in the same file — declares false. And it rests on literally the same
19-probe set that C5.3 identifies as insufficient.

Note what this is *not*: the conclusion happens to be **true**. I closed the family at class level
myself (Claim 2). The defect is that r5's record offers four shapes as the evidence for a family
— the exact move the dispatch warns against and the exact move that failed r3 and r4.

**Corroboration.**

* `_bookkeeping_20260922_round74/handoff.json` carries the key
  `"the_F_REV_R4_05_family_is_closed_on": "the four shapes registered in oracle.md C5.2"`. The
  **key name** asserts the family is closed; the value restricts it to four shapes. `F-REV-D-06`
  in the r1 review already established this project's rule that a key name which misreports an
  inventory is the same failure mode this card exists to avoid; this key name over-reports one.
* `review.md` `## r5` and `handoff_r5.json.responses.F-REV-R4-05.change` call the change a
  "**widening**". It is not (Claim 3). The mischaracterisation is load-bearing: "widening" is what
  makes "closes the whole family at zero cost" sound, and it is what hides the three-character
  regression.
* The register's `零代价` (§18.2 REM-71) and `task_plan.md` Round 74's "放宽到值 token 类是零代价的"
  repeat the same unqualified "zero cost" without noting the `&`/`'`/`|` loss.
* `oracle.md` C5.6 does scope it — "closed **on the four shapes registered in C5.2**" — which is
  honest but self-defeating: it says a family is closed on four of its members. It is also not
  the sentence a reader carries away, since C5.1 states the unscoped version first.

**What is clean.** `handoff_r5.json.measurement.domain` is exemplary: "the 36 frozen oracle cases
and the 87 rule-table rows in the r5 harnesses. NOT a claim about all inputs." C5.3's corrected
form carries its domain. `boundaries.r4_carrier_untouched: true` is checkable and correct
(handoff_r4.json sha256 `ea6ad25bbaed63b6a29079a31ab62d96980e30024f42914cc1db470083595cef` is
pinned in `_bookkeeping_20260922_round72/handoff.json`), as is
`boundaries.production_anchor` (`scripts/model_registry.py` =
`9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f` / 26446 B, recomputed). So the
failure is not systemic — it is one sentence, in the newest artefact, exactly where the dispatch
said it would be.

### Claim 10 — the finding about this repository is correct — **CONFIRMED**

Measurement. `git check-ignore`, `git ls-files`, `git grep`, `hashes.py`.

* `iso/` really is ignored by policy: `execution_runs/.gitignore:17` is `*/a*/iso/`, and
  `git check-ignore -v` reports that rule for the r5 tree, the r4 tree and `product_base`.
  `git ls-files <attempt>/iso/` returns **0** files.
* The hashes really are registered in committed carriers: r3 in `handoff_r3.json`, r4 in
  `handoff_r4.json`, r5 in `handoff_r5.json`, base in `oracle.md` §0 (and I-14-C's carriers) — all
  of which are tracked. So a registered hash pointed at an unversioned file. **True.**
* "Including for r2 and r3, which nobody had noticed": the r2 tree's hash (`2aa5ed1a…`) *is*
  registered in committed files — `handoff.json` (the r2 carrier), `after/final_hashes.json`,
  `fix_record.md`, `commands.json`, `reviewer_report_r2.md` — so r2 is in the same position, and
  the bookkeeping finding names only `handoff_r3/r4/r5`. That is an understatement of the
  finding's reach, not an error in it. r3 likewise. So the finding holds for **all five**
  generations.
* "the rescued copies match the carriers one for one": recomputed from bytes —
  base `c5608c4b…`/40060, r2 `2aa5ed1a…`/41432, r3 `a551cc45…`/42839, r4 `15446f4d…`/42829,
  r5 `ca13fb81…`/43362 — each equal to its carrier pin, and each bookkeeping copy byte-equal to
  its tree (True/True for r4 and r5, and equal for base/r2/r3).
* "whether the remedy is adequate": the remedy directory **is** versioned — all 13 files in
  `_bookkeeping_20260922_round74/` are tracked and `git check-ignore` says NOT ignored for the
  rescued copies. That is the right shape of remedy, and it is adequate **for the artefact whose
  hash was registered** (the redactor source). It is *not* adequate for whole-tree reproduction:
  the rest of each product tree is still only rebuildable from HEAD + `changes.diff`, and the
  committed r3→r4 / r4→r5 diffs are explicitly **not** applicable (CRLF; `patch(1)` fails), so the
  byte copies are the only working route — which the round-74 handoff states honestly.
* One level out, the same failure survives: `_review_i14d_r5_20260922/` — which carries
  `DISPATCH.md`, the document this review was dispatched from — is **not** tracked (`git ls-files`
  returns 0), while `_review_i14d_r3_20260922/` (42 files) and `_review_i14d_r4_20260922/`
  (30 files) are. → F-REV-R5-06 (INFO).

### Claim 11 — generation isolation still holds — **CONFIRMED**

Measurement. `hashes.py`; `git grep` for the new row IDs.

* r3 pins reproduce from bytes: `run_i14d_oracle.py` `f7c94c60…`/11043,
  `run_rule_table_i14d.py` `01a3187e…`/19378. r4 pins: `run_i14d_oracle_r4.py`
  `240d181c…`/12316, `run_rule_table_i14d_r4.py` `610ce4b8…`/20006.
* The four r3/r4 harness files contain **0** mentions of `N5p|N5q|N5r|N5s|nontchar`; the two r5
  files contain 4 each. So the r5 rows live only in the new files.
* The r5 harnesses reproduce their pins: `38a22101…`/13293 and `1e51373a…`/20600.

### Claim 12 — what r5 did NOT do is honestly scoped — **CONFIRMED**

Measurement. `handoff_r5.json`, `REMEDIATION_REGISTER.md` §16–§18.

* `handoff_r5.json.not_addressed_here` lists exactly `F-REV-R3-02`, `-03`, `-05`, `-06`, `-07`,
  `-08`, `-09`, `-10` — the eight the dispatch names.
* The register marks them unaddressed: REM-66 (`F-REV-R3-02`), REM-68 (five INFO items, ①–⑤),
  REM-67①/③ (`F-REV-R3-03`, `F-REV-R3-05`) — all `未处理`, unchanged by §18.
* `F-REV-R4-02` is registered and deliberately not edited (REM-74, "🟡 已登记，未改", with the
  reason that the r4 measurement record's hashes are pinned by the r4 carrier). `oracle.md` C5.5
  says the same. I confirmed the r4 measurement directory's hashes are indeed pinned by
  `handoff_r4.json.measurement.evidence`, so the reason is sound rather than convenient.
* Caveat (INFO): the register registers the five INFO items as a group with a ①–⑤ substance
  enumeration (REM-68) and never by their `F-REV-R3-06`…`-10` IDs. The IDs are in
  `handoff_r5.json` and in the committed `reviewer_report_r3.md`, so they are traceable; the
  register just is not the place that carries them. → F-REV-R5-07 (INFO).

### Claim 13 — no verdict was pre-empted — **CONFIRMED**

Measurement. Read the carriers; `grep` for acceptance language.

* `handoff_r5.json`: `status: "review_pending"`, `boundaries.verdict_expressed: false`,
  `boundaries.status_transitions: 0`, `who_wrote_it_on_what_basis.it_states_no_verdict: true`.
* `review.md` `## r5`: "The implementer writes no verdict here"; `REMEDIATION_REGISTER.md` REM-75:
  "**待复核**".
* `binding.json` carries no `status` or `verdict` key at all (its 22 top-level keys are all
  binding/isolation fields), so there is no place a verdict could have been pre-empted in the
  binding record either.
* No acceptance, approval or closure language found in any r5 artefact.

---

## 3. FINDINGS

Severity follows this card's own calibration (MEDIUM = an unregistered credential-persistence
family, or a record that claims more than its measurement; LOW = a record/comment inaccuracy;
INFO = note).

### F-REV-R5-01 — **MEDIUM — r5's class change is a swap, not a widening: it re-opens `&`, `'` and `|`, and six credential-persistence shapes exist on r5 that its own pre-image redacted**

`_AUTH_PREBREAK_TOKEN` is `[^\s,;&\"'|]+`. The class it replaced was
`[A-Za-z0-9!#$%&'*+.^_\`|~-]+`, which matched `&`, `'` and `|`; the new one does not. `&`, `'` and
`|` are all RFC-7230 `tchar`s, so these are pre-break tokens by the *old* class's own definition,
and r3 and r4 redacted the credential behind them. r5 does not:

```
Authorization: Bo&t\nSYNTHETIC_AUDIT_TOKEN   ->  r4 'Authorization: <redacted>'
                                                 r5 'Authorization: <redacted>&t\nSYNTHETIC_AUDIT_TOKEN'
Authorization: Bo&t\n<39-char credential>\ndoc=17
                                             ->  r4 'Authorization: <redacted>'
                                                 r5 'Authorization: <redacted>&t\n<39-char credential>\ndoc=17'
```

Identical for `Bo't` and `Bo|t`. Not registered in either instrument, and mentioned in no carrier.

**Not base-regressive**: `product_base` leaks these shapes too, so the card's own negative clause
("纯合成 marker 必须仍被脱敏") is not violated and the card-level baseline is not regressed. That is
what bounds this at MEDIUM rather than BLOCKER. But it is the first time **since r2** that a
revision has leaked a shape its pre-image redacted: measured over the same 96-character sweep,
`r3 \ r2 = []` and `r4 \ r3 = []` (r3 and r4 each introduced nothing), while
`r5 \ r4 = ['&', "'", '|']`. `F-REV-R4-05`'s reviewer was able to write "r4 introduces none of
them (`r4 \ r3 = ∅`)" and "it strictly reduces the family"; r5 can write neither. Leak-set sizes at
this position: base 6, r2 96, r3 19, r4 19, r5 8.

**Cheapest correct handling**: one of two, both cheap. (a) add `&`, `'`, `|` back —
e.g. `[^\s,;"|]+` keeps the value-delimiter semantics of `,` `;` `"` while restoring the three
tchar specials — and re-measure the four rows plus the 14 characters; or (b) register the three
shapes on both instruments, as `R3a`/`open-two-token-then-wrap` register `C10`, and say so in the
comment block. Registering is sufficient by this card's precedent; the owner already accepts a
registered open residual on this path.

Reproduce: `sweep.py` (or the inline one-liner in Claim 3), and
`negative_controls.py` step 2, which shows the sweep is sensitive to the class
(`r5\r4 = "&'|"`, `r4\r5 = '()/:<=>?@[\\]{}'`).

### F-REV-R5-02 — **MEDIUM — r5's record asserts the family is closed on a measurement set that does not contain the family (the `F-REV-R4-06` species, in the generation that corrected `F-REV-R4-06`)**

`oracle.md` C5.1: "widening to the value token **closes the whole family** at **zero cost** —
oracle 0 failures, rule table 0 failures, and the over-redaction family unchanged". The measurement
named in the same sentence, `_r5_measure_20260922/measure_r5.py`, carries 19 probes, of which four
are members of the F-REV-R4-05 family; the r4 reviewer sized that family at 31 base-regressive
shapes and at class level it has ≥14 members. The conclusion is a universal; the evidence covers
4/≥14. This is structurally the sentence C5.3 declares false nine paragraphs earlier, resting on
the same 19-probe set C5.3 identifies as insufficient.

Repeated, unscoped, downstream: `review.md` `## r5` and `handoff_r5.json` call the change a
"widening" (it is not — Claim 3); `REMEDIATION_REGISTER.md` §18.2 says `零代价`;
`task_plan.md` Round 74 says "放宽到值 token 类是零代价的". The bookkeeping handoff's key
`the_F_REV_R4_05_family_is_closed_on` asserts closure in its name and restricts it to four shapes
in its value.

Also: "the over-redaction family **unchanged**" is true of the nine registered rows and of
`product_base`, and false of the r4→r5 delta, where r5 deletes `doc=17` in 14 shapes r4 kept
(`Authorization: Bo?t\ndoc=17`). Same species: a conclusion whose named measurement set does not
cover the change it is describing.

**Fix**: state the set. "Over the 19 probes in `measure_r5.py`, four of which are family members,
the widening leaves only `C10`; the family itself is closed over all 14 non-tchar, non-delimiter
characters, swept in `<path>`, and it re-opens `&`, `'`, `|` against r4 (F-REV-R5-01)." One
sentence, and it is then true.

Reproduce: `sed -n '547,550p' "$A/oracle.md"`; `sed -n '52,68p' "$ER/_r5_measure_20260922/measure_r5.py"`;
`sweep.py`.

### F-REV-R5-03 — **LOW — the sentence that corrects `F-REV-R4-01` is ambiguous, and one reading of it is still false**

`observability.py:315-316`: "The breaks are consumed by the match; the indentation and the keys on
the lines AFTER the redacted one are not." True under the coordination reading ("the indentation
*on the lines after the redacted one*"). False under the reading "the indentation of the redacted
line is not consumed": measured, `Authorization: Bearer\n  <marker>` → `Authorization: <redacted>`
(25 chars — both spaces consumed; this is also the frozen N5d expectation, so the code and the
oracle agree with each other and against that reading). Since this sentence *is* the correction
for a defect that was itself a wrong claim about this exact mechanism, it should be written so
that only one reading is available: e.g. "the breaks and the indentation that follows them are
consumed; the keys on the lines AFTER the redacted one are not."

Reproduce: `claims467.py` section (b); or
`redact_text("Authorization: Bearer\n  SYNTHETIC_AUDIT_TOKEN")` → `'Authorization: <redacted>'`,
`len == 25`.

### F-REV-R5-04 — **LOW — the same false sentence that r5 corrected in the source comment is left standing, uncorrected and unnamed, in `oracle.md` C2.2**

`oracle.md:260-262` (appended in the r2 generation) still reads: "**after a *known* scheme word**
(`bearer`, `token`, `basic`, `digest`, `oauth`, `jwt`, `apikey`, `api_key`, `sso`) **and exactly
one line break, the first token is redacted (fail closed)**, and **the line break plus any
indentation stay OUTSIDE the match**." Every clause of that is contradicted by the code and by
C2.2's own table: the scheme enumeration was removed in r3 (`C3.1`); the break is a *run*, not
"exactly one"; and the break plus the indentation are *inside* the match (N5d → 25 chars).

C5.4 corrects the identical claim **in the source comment** and does not name C2.2 as superseded.
This project's own convention is to name a superseded section explicitly — `C3.5` does exactly
that for line 272 ("Line 272 above is SUPERSEDED"), and `C5.3` for C4.5. So the omission is a real
gap by the project's standard, not a stylistic quibble: a reader of `oracle.md` now finds C2.2 and
C5.4 asserting opposite things about the same mechanism, in the document that defines the
expectations the new rows are derived from.

Reproduce: `sed -n '255,275p' "$A/oracle.md"`; `grep -n "SUPERSEDED\|已过时" "$A/oracle.md"`;
then `claims467.py` section (a)/(b).

### F-REV-R5-05 — **LOW — the carrier's registered `site` values are stale r4 line numbers**

`handoff_r5.json` `responses.F-REV-R4-05.site` = `"observability.py:317"`, but in r5 the renamed
constant `_AUTH_PREBREAK_TOKEN` is at **line 324** (line 317 is now a comment line).
`responses.F-REV-R4-01.site` = `"observability.py:290-325"`, but r5's comment block is
**290–323** (324–325 are code). The same values are repeated in `review.md` `## r5`,
`REMEDIATION_REGISTER.md` §18.2 and `task_plan.md` Round 74. A reviewer who follows the pointer
reads the wrong line. Trivial to fix; worth fixing because the whole discipline of this card is
that a registered pointer and the bytes must agree.

Reproduce: `grep -n "_AUTH_PREBREAK_TOKEN =" "$A/iso/product_narrow_r5/src/company_wiki/source_catalog/observability.py"` → 324;
`grep -n '"site"' "$A/handoff_r5.json"`.

### F-REV-R5-06 — **INFO — the review directory that carried this dispatch is itself unversioned**

`_review_i14d_r5_20260922/` is untracked (`git ls-files` → 0), while
`_review_i14d_r3_20260922/` (42 files) and `_review_i14d_r4_20260922/` (30 files) are tracked. So
the newest review round's inputs — including `DISPATCH.md` — are the one set of round artefacts
that will not survive a clone. This is the same failure Claim 10's finding is about, one level
out. My own report goes into the attempt (tracked), so it is not affected.

### F-REV-R5-07 — **INFO — the five INFO items are registered by substance, not by their finding IDs**

`REMEDIATION_REGISTER.md` REM-68 registers `F-REV-R3-06`…`-10` as "五项 INFO" with a ①–⑤
substance enumeration and never uses the IDs. The IDs are carried by `handoff_r5.json` and by the
committed `reviewer_report_r3.md`, so they are traceable; the register is just not a place where a
reader can join ID to disposition. Same class as F-REV-D-06.

### F-REV-R5-08 — **INFO — `credential_leaks == []` does not see the marker form of the registered two-token shape**

The two `registered_open` rows declare the **secret** surviving
(`Authorization: Bearer abc\n<39-char credential>` → `Authorization: <redacted>\n<39-char credential>`),
and the marker-based `credential_leaks` list is `[]` on the r5 tree. But the **marker** form of the
same shape leaks and is in neither list:

```
Authorization: Bearer abc\nSYNTHETIC_AUDIT_TOKEN
  r5 -> 'Authorization: <redacted>\nSYNTHETIC_AUDIT_TOKEN'      # marker persists
Authorization: Bo t\nSYNTHETIC_AUDIT_TOKEN
  r5 -> 'Authorization: <redacted>\nSYNTHETIC_AUDIT_TOKEN'      # same shape, no known scheme word
r5 rule table: credential_leaks = []
```

This is pre-existing (it comes from the r3 registration) and it is *registered by example* rather
than hidden — the shape is declared, just with the other credential. But the card's exit criterion
2 ("纯合成 marker 必须仍被脱敏") is operationalised as `credential_leaks == []`, and that list is
empty here only because the marker variant of the declared shape is not a row. Worth one row on
each instrument; not a r5 regression. Reproduce: `claims467.py` section (g); or the two probes
above.

---

## 4. UNVERIFIED

I list these as unverified rather than confirming them. Nothing below is a finding.

1. **End-to-end persistence.** I did not run `harness/run_exit_probe.py`, `harness/drive_real_exit.py`,
   `harness/run_real_cli_exit.py` or the copied pytest suites. Every leak in this report is
   measured at the `redact_text` helper. I did not demonstrate that a `Bo&t`-shaped credential, or
   any other shape, reaches a persisted event log through `worker.py` → `redact_and_truncate`.
   The r3 and r4 reviews left the same gap.
2. **Whether the four new rows' expected strings were observed from the tree before being frozen.**
   The dispatch discloses that they were. I could not verify or refute the ordering from the
   artefacts: `measure_r5.py` measures candidates in memory and does not record row strings, and
   neither harness carries an ordering proof. I verified only that the strings are derivable and
   correct (Claim 4).
3. **The mutation arms M1–M4.** Not re-run. My differential arms are the r3 and r4 trees plus
   `product_base`, and one in-memory class swap as a negative control. That is sufficient for the
   leak direction of these fixes but is not the same instrument.
4. **`harness/tests/*` and the copied-suite counts** (86 passed / 0 failed; `fidelity_cases` 32).
   Not re-run.
5. **`F-REV-R3-02`, `-03`, `-05`, `-06`…`-10` and `F-REV-R4-02` themselves.** I verified they are
   registered and unaddressed (Claim 12); I did not verify their substance, and `F-REV-R4-02`'s
   self-contradiction in `_r4_measure_20260922/` is deliberately not edited, so it is still there.
6. **Whether `_r3_design_reprobe_20260922/`'s four reconstructed candidate patterns are faithful.**
   The reprobe itself says only `r3-chosen` uses the product's own split verbatim and the other
   four are re-expressed from scratch scripts. I independently reproduced the *design claim* the
   comment makes (Claim 7) with my own reconstruction, which is stronger for that claim, but I did
   not audit the reprobe's other candidates.
7. **The r2 generation's historical reproduction basis.** `REMEDIATION_REGISTER.md` REM-70 records
   that the r2 harness was extended in place, so the r2 generation's reproduction basis is gone. I
   did not attempt to reconstruct it.
8. **`disclosure_adaptation`, promotion, accuracy, mapping**, and any downstream consumer of the
   diagnostic key the auth branch deletes.
9. **Non-printable and non-ASCII characters at the pre-break position.** My sweep covered
   `string.printable` minus the four whitespace controls. Control characters other than TAB/LF/CR
   and non-ASCII code points were not swept; the r4 reviewer's sweep included controls and found
   them in the family. Not swept here.

---

## 5. HOW TO REPRODUCE

Paths. `A` = `<attempt>` =
`<repo>/.planning/2026-09-19-three-project-history-audit/execution_runs/I-14-D/a20260919-01`;
`ER` = its parent `execution_runs`; `S` = `<ER>/_review_i14d_r5_20260922/scratch` (my scratch,
outside the attempt, per the dispatch); `PY` = `"$A/iso/venv/Scripts/python.exe"`.

My scratch scripts are in `$S`: `hashes.py`, `diff45.py`, `linediff45.py`, `sweep.py`,
`claims467.py`, `rowbyrow.py`, `negative_controls.py`. Every finding is also reproducible from the
inline one-liners below, without them.

```bash
cd "$A"
PY="./iso/venv/Scripts/python.exe"
S="../_review_i14d_r5_20260922/scratch"

# --- every registered hash, recomputed from the bytes (Claims 1, 10, 11) ---
"$PY" "$S/hashes.py"

# --- the r4->r5 byte relationship and the inversion (Claim 1) ---
"$PY" "$S/diff45.py"        # CR/LF counts, region count, inversion, rename
"$PY" "$S/linediff45.py"    # the single replace opcode r4[290..318] -> r5[290..325]

# --- the class-level sweeps (Claims 2, 3, 6, 7) ---
"$PY" "$S/sweep.py"         # every printable char at the pre-break position, all 5 generations
"$PY" "$S/claims467.py"     # the comment's sentences, the over-redaction family, the four rows

# --- no regression, row by row (Claim 5) ---
for t in product_narrow_r5 product_narrow_r4 product_narrow_r3; do
  "$PY" harness/run_i14d_oracle_r4.py      --src "iso/$t/src" --label "$t" --out "$S/r4oracle_on_$t.json"
  "$PY" harness/run_rule_table_i14d_r4.py  --src "iso/$t/src" --label "$t" --out "$S/r4rule_on_$t.json"
  "$PY" harness/run_i14d_oracle.py         --src "iso/$t/src" --label "$t" --out "$S/r3oracle_on_$t.json"
  "$PY" harness/run_rule_table_i14d.py     --src "iso/$t/src" --label "$t" --out "$S/r3rule_on_$t.json"
  "$PY" harness/run_i14d_oracle_r5.py      --src "iso/$t/src" --label "$t" --out "$S/r5oracle_on_$t.json"
  "$PY" harness/run_rule_table_i14d_r5.py  --src "iso/$t/src" --label "$t" --out "$S/r5rule_on_$t.json"
done
"$PY" "$S/rowbyrow.py"      # 32/83/28/79 identical; 36/87 differ in exactly the 4 new rows

# --- negative controls: every predicate must go RED on a mutated input (section 6) ---
"$PY" "$S/negative_controls.py"

# --- the one-liner for the blocking finding, no scratch script needed ---
"$PY" -c "
import importlib.util,sys
def L(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s)
    sys.modules[n]=m;s.loader.exec_module(m);return m
r3=L('a',r'iso/product_narrow_r3/src/company_wiki/source_catalog/observability.py')
r4=L('b',r'iso/product_narrow_r4/src/company_wiki/source_catalog/observability.py')
r5=L('c',r'iso/product_narrow_r5/src/company_wiki/source_catalog/observability.py')
t='Authorization: Bo&t\nSYNTHETIC_AUDIT_TOKEN'
for n,m in (('r3',r3),('r4',r4),('r5',r5)): print(n,repr(m.redact_text(t)))"

# --- the record (Claim 9) ---
sed -n '547,550p' "$A/oracle.md"                      # C5.1 "closes the whole family"
sed -n '566,583p' "$A/oracle.md"                      # C5.3 the correction of C4.5
sed -n '52,68p'   "$ER/_r5_measure_20260922/measure_r5.py"   # the FAMILIES probe list
sed -n '255,275p' "$A/oracle.md"                      # C2.2, still uncorrected (F-REV-R5-04)

# --- the three copies of the corrected sentence (Claim 8) ---
grep -n "仅剩登记的" "$ER/../REMEDIATION_REGISTER.md"        # §16 original, §18.1 correction
sed -n '1770,1780p;1866,1874p' "$ER/../task_plan.md"         # Round 72 original, Round 74 correction

# --- the repository finding and the remedy (Claim 10) ---
git check-ignore -v "$A/iso/product_narrow_r5/src/company_wiki/source_catalog/observability.py"
git ls-files "$A/iso/" | wc -l                              # 0
git ls-files "$ER/_bookkeeping_20260922_round74/" | wc -l    # 13, all tracked
git ls-files "$ER/_review_i14d_r5_20260922/" | wc -l         # 0  (F-REV-R5-06)
git grep -l "2aa5ed1a219084a67f040388072aa94d7432c63414b6692060f1b4d6b4e12bde" -- .   # r2 pinned

# --- generation isolation and status (Claims 11, 13) ---
grep -c "N5p\|N5q\|N5r\|N5s\|nontchar" "$A/harness/run_i14d_oracle.py"      # 0
grep -c "nontchar" "$A/harness/run_i14d_oracle_r5.py"                       # 4
grep -n '"status"' "$A/handoff_r5.json"                                     # review_pending
```

Environment note: the global interpreter lacks PyYAML and the harnesses correctly return
`rc=2 cannot_adjudicate` with it. Use `$PY`. All runs above used `$PY` (CPython 3.13.9,
PyYAML 6.0.3) and wrote only into `$S`.

Nothing under the attempt was written except this report. Nothing was deleted, moved or cleaned
up. The `iso/` trees, the r3/r4 harnesses, `handoff_r3.json`, `handoff_r4.json` and the r4
measurement directory were read only.

---

## 6. WHICH OF MY OWN CHECKS I CONFIRMED ARE RESPONSIVE

The dispatch requires that a predicate which cannot fail is not a predicate. Every check I used
was fed a mutated input in memory and had to go RED. All five did
(`negative_controls.py`):

| # | my check | mutated input | result |
|---|---|---|---|
| 1 | recompute sha256 from bytes | flip the first byte of `_AUTH_PREBREAK_TOKEN` in memory | `ca13fb81…` → `5fa9856e…`, differs ✔ RED |
| 2 | class sweep leak set | rebuild the r5 pattern with **r4's** class | leak set changes from `"&',;|` to `'()/:<=>?@[\\]{}'` ✔ RED |
| 3 | row-by-row equality | perturb one field of one row | 0 differing → 1 differing (`N1-mine`) ✔ RED |
| 4 | CRLF uniformity | rewrite the file's CRLF to LF | uniform → not uniform ✔ RED |
| 5 | the four registered shapes' sensitivity | run them against r4's class | all four ok → all four fail ✔ RED |

Responsiveness, check by check, to the claims:

* **responsive and decisive for Claim 2**: the class sweep is the check that separates "four
  shapes" from "the family". It is the reason I can say the base-regressive family really is
  closed — and it is also the check that produced Claim 3's refutation. Same instrument, both
  directions; if it had been insensitive to the class (control 2) neither result would mean
  anything.
* **responsive and decisive for Claim 3 and F-REV-R5-01**: control 2 shows the sweep moves when
  the class moves, and the `r5 \ r4 = "&'|"` line is the finding itself.
* **responsive for Claim 1**: control 1 shows the hash predicate tracks the bytes; the inversion
  test is responsive because it reproduces a *pinned* hash (`15446f4d…`) rather than merely
  "not equal to r5".
* **responsive for Claim 5**: control 3 shows the row comparison would have caught a moved row.
  This matters because the alternative instrument (the harness verdict) is coarser — the rule
  table returns `rc=3` on *every* tree, so the verdict alone would have told me nothing.
* **responsive for Claim 7**: control 4 is a proxy (line endings), not a test of the comment. The
  comment's sentences were tested by direct execution, and the two that fail do so on inputs the
  oracle already freezes (N5d), so they are not artefacts of my choice of probe.
* **responsive for Claim 4**: control 5. Without it, "the four rows pass on r5" would be
  uninformative; with it, I know they are class-sensitive and therefore load-bearing.
* **NOT independently responsive, and I say so**: my check of Claim 9 is a *reading* of the record
  against a *count* of the measurement's probes. It has no mutated-input control because it is not
  a predicate over code — its force comes from the arithmetic (4 family members in a 19-probe set
  vs a family sized at 31 by the r4 reviewer and ≥14 at class level) and from the fact that C5.3,
  nine paragraphs above, declares the identical construction false. A reader who disagrees with my
  reading of "the whole family" would have to explain what measurement in the r5 carriers covers
  the other ≥10 family members; I could not find one.
* **Also not independently responsive**: my Claim 10 checks are `git` queries, which are their own
  instrument and cannot be mutated in memory. I substituted two independent routes — `git
  check-ignore -v` (which prints the matching rule) and `git ls-files` (which counts) — and both
  agree, plus a third (`git grep` for the r2 hash) that produced a *positive* result I did not
  expect and which therefore corrects the finding's reach rather than confirming it.

---

*End of report. Verdict: `changes_required` — `F-REV-R5-01` (MEDIUM) and `F-REV-R5-02` (MEDIUM),
with `F-REV-R5-03`/`-04`/`-05` (LOW) and `F-REV-R5-06`/`-07`/`-08` (INFO).*

*Tally of the thirteen: **11 CONFIRMED** (1, 2, 4, 5, 6, 7, 8, 10, 11, 12, 13), **2 REFUTED**
(3, and 9 — which is refuted in the sense the claim asks about: r5's own record does overstate),
**0 UNVERIFIABLE**. Two of the CONFIRMED carry recorded qualifications rather than being clean:
Claim 6 (the over-redaction family is unchanged *of the registered family and of `product_base`*,
not of the r4→r5 delta) and Claim 7 (the comment block is true except for one ambiguous sentence
and one load-bearing mischaracterisation).*
