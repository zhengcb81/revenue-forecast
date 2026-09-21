# I-14-D — INDEPENDENT REVIEWER REPORT

Card: **I-14-D** (narrow the redactor's greedy bare-value semantics to a single token — the C13 card)
Attempt: `execution_runs/I-14-D/a20260919-01`
Reviewer: **independent reviewer** (not the implementer; no implementer artifact was edited)
Date of review: 2026-09-21
Review posture: read-only against both production checkouts and against `iso/`; the only file this
review writes into the attempt dir is this report. All reviewer scratch output (probe scripts, run
dirs, prototype tree) lives **outside** the attempt, under `%TEMP%\i14d_review\`.

The byte-pin of this file (sha256 of raw bytes) is reported by the carrier in the handoff message,
not inside the file, so that the pin covers content that cannot change after hashing.

---

## 0. VERDICT

**CHANGES_REQUIRED — the attempt is NOT accepted.**

The card's exit clause is **met on the assignment path** (`token=`/`key=` values no longer cross
newlines; multi-line diagnostics survive) and the new E4b baseline is **independently re-derived and
confirmed**. Every implementer claim I was asked to check reproduces, in several cases exactly to the
byte.

However the review found a **credential-persistence regression on the authorization path that the
frozen oracle, the rule table and all three mutations fail to exercise**:

> `"Authorization: Bearer\n<SECRET>\ndoc=17"` — on the pre-fix tree the persisted event is
> `"Authorization: <redacted>"` (secret gone); on `iso/product_narrow` the persisted event is
> `"Authorization: <redacted>\n<SECRET>\ndoc=17"` — **the full credential is written to the
> append-only event log in plaintext.**

This was confirmed both at helper level and **end-to-end through the real worker exception exit**
(`SourceCatalogWorker.run_forever` → `worker.py:1066 message_redacted=redact_and_truncate(message)`).
It violates the card's own negative clause (纯合成 marker 必须仍被脱敏) for a measured input family, so
exit criterion 2 as evidenced by this attempt (`credential_leaks == []`) is **not sound for the auth
path**. See **F-REV-D-01**.

The implementer's engineering discipline is otherwise high: the oracle was genuinely frozen before
the edit, the correction is genuinely append-only, `changes.diff` round-trips in both directions, the
mutation specimens are genuine single-site derivations, and no production file was written. The
defect is one of **coverage of the negative clause**, not of process.

---

## 1. WHAT I VERIFIED (implementer claims 1–9)

### Claim 1 — only `observability.py` changed; hashes and CRLF — **VERIFIED**

I hashed all eight `iso/product*` trees myself (`Get-FileHash -Algorithm SHA256` on raw bytes):

| tree | `observability.py` sha256 | bytes | CRLF |
|---|---|---|---|
| `product` (T0 pristine) | `a73826aa…ffebe5a` | 30087 | yes |
| `product_base` (I-14-C r5 T4) | `c5608c4b45a55cce03df9988561e1a3ad1cab0970c51e8b3af630239fe9de35c` | 40060 | yes |
| `product_narrow` (deliverable) | `e8abd522b2072add062be225d7ec1ca10621ffa5be7841f99ef9fb339015cbd0` | 40476 | yes |
| `product_mut_greedy` (M1) | `6c093676907e5e9ca3be3f31cd62c0726ca1be10cda68cf0e38a8910b75c514f` | 40682 | yes |
| `product_mut_authnl` (M2) | `018bf169e00c265012fbe826a12621e25374418eec18c33788bd04ff519dbd24` | 40473 | yes |
| `product_mut_auth1` (M3) | `13470b010b1b7a25bd0c9f236850aab17c5afefc8ae9b5b76d6af0b6068fd371` | 40471 | yes |
| `product_swapped` (control) | `0286cd19…82f6b6a` | 34239 | yes |
| `product_fixed` (I-14-C T4, same as base) | `e8abd522…015cbd0`* | 40476 | yes |

\* `iso/product_fixed` in **this** attempt is the *narrow* tree; `product_base` is the r5 tree. Both
`product_fixed` and `product_narrow` are `e8abd522…` — the copy that is named `product_fixed` here is
the deliverable, not the I-14-C tree. Not a defect (the suite's default `TREE_FIXED` points at it and
the suite is run with `I14C_PRODUCT_SRC` overridden), but the naming is confusing for a future reader.

`+416 B` = 40476 − 40060 **confirmed**; CRLF preserved in every tree.

A full 152-file byte comparison of `product_base/src` vs `product_narrow/src` (excluding
`__pycache__`) returned **exactly one** differing path:

```
DIFFERS: company_wiki\source_catalog\observability.py
```

with no file present in only one tree. **Only `observability.py` changed.**

The three mutation trees are also genuine minimal derivations of `product_narrow` (only
`observability.py` differs in each, and the diff is one localized site):
M1 restores the r1 multi-word scanner loop verbatim; M2 changes the auth join `[ \t]+` → `\s+`;
M3 switches the auth value group from `_AUTH_BARE_VALUE` to `_BARE_VALUE`.

I also recomputed **all 46 entries** of `after/final_hashes.json` (sha256 **and** byte count) with the
attempt dir as cwd: **46/46 reproduce, 0 missing, 0 mismatched.**

### Claim 2 — `changes.diff` round-trip — **VERIFIED**

In a fresh scratch repo (`git init`, `core.autocrlf=false`), copied from `product_base`:

* structure: **4130 bytes, 2 hunks, 1 file, 0 non-POSIX `---`/`+++` lines** — confirmed;
* `git apply --check -p1` → **rc 0**; `git apply -p1` → **rc 0**;
* applied `observability.py` == `e8abd522…` == `product_narrow` → **IDENTICAL**;
* `git apply -R -p1` → **rc 0**, and a **full-tree byte comparison of all 152 files** against
  `product_base` gave **0 mismatches** → reverse-apply reproduces the base tree byte-for-byte.

The implementer's own `after/git_apply_verification.json` agrees (`GIT_APPLY_REPRODUCES_T4: true`,
all three files identical).

### Claim 3 — RED state on `product_base` — **VERIFIED**

* **Probe reproduces I-14-C's r5 row exactly.** My independent run:
  `E1 25 / E2a 65 / E2a-deep 74 / E2b 34 / E2b-residual 46 / E3 30 / E4a 20 / **E4b 193** / E1-no-cli 25`,
  rc 3 each, marker hits 0 except the declared `E2b-residual` (2 hits). Cross-checked against
  I-14-C's **own** r5 record (`I-14-C/.../review.md:264 | E4b | len 193 |`), not merely against this
  attempt's transcription.
* **Oracle on base**: rc 3, `narrow_must_failed` = exactly all 6
  (`N1-mine, N1-reviewer, N2-middle-line, N3-newline-then-key, N5-auth-multiline,
  N13-partial-multiword-residual`), `keep_must_failed` = `[]` → `RED-as-expected-pre-fix`.
* **Rule table on base**: rc 3 with **exactly the 5 documented C13-family fidelity failures**
  (`cred-line-middle-single-token`, `cred-multiline-swallow`, `cred-multiline-then-key`,
  `cred-auth-multiline-swallow`, `res-partial-multiword-secret`); 0 leaks, 0 touched.
* **Copied suite on base**: `82 passed`, **rc 0**.

### Claim 4 — GREEN state on `product_narrow` — **VERIFIED**

* **Oracle**: 17 cases, `narrow_must_failed []`, `keep_must_failed []`, `verdict pass`, **rc 0**.
* **Rule table**: 48 entries, `credential_leaks []`, `touched_but_should_not_be []`,
  `fidelity_ok true`, **rc 0**.
* **Copied suite** (byte-identical copy, sha256 `672b88de…` == I-14-C's): exactly
  **4 failed / 78 passed**, and the 4 are precisely the frozen greedy-semantics nodeids:
  1. `…::test_f08_c13_multiline_loss_is_frozen_not_hidden`
  2. `…::test_f08_output_fidelity_exact[a=1 token=SYNTHETIC_AUDIT_TOKEN b=2-a=1 token=<redacted>]`
  3. `…::test_f08_output_fidelity_exact[upload failed for token=SYNTHETIC_AUDIT_TOKEN doc=17\nstage=summarize code=llm_global_failure request_id=req-1-upload failed for token=<redacted>]`
  4. `…::test_f08_output_fidelity_exact[token=SYNTHETIC_AUDIT_TOKEN\nnext=1-token=<redacted>]`
  Nothing else failed. The neighbouring row `("failed for token=" + MARKER + "; see log\nstage=…")`
  is **GREEN on both trees** and needs **no** rewrite (verified: it is not among the 4).
* **New suite**: **21 passed, rc 0** on narrow; on base **9 failed / 12 passed, rc 1** — matching the
  documented B5 RED set exactly.
* **Probe on narrow**: identical to base on all 9 rows **except `E4b` 193 → 200**; marker hits 0
  except the declared `E2b-residual`.
* Counts cross-check: `after/counts.json` == `r5/counts.json` (48 / 17 / 6 / 11 / 28 / 103), and all
  of those numbers match what my own runs produced.

### Claim 5 — mutation proof — **VERIFIED**

* **M1** (`product_mut_greedy`): oracle rc 3, `narrow_must_failed` = the **5 scanner cases**
  (N1-mine, N1-reviewer, N2, N3, N13) with **`N5-auth-multiline` GREEN**; rule table rc 3 with
  **exactly the 4 scanner-family** fidelity failures and no auth row; probe **E4b back to 193** and
  all other rows equal to base. → the scanner loop is what fixes the assignment path and what moves E4b.
* **M2** (`product_mut_authnl`): oracle rc 3 with **ONLY `N5-auth-multiline`** failing; rule table
  rc 3 with only `cred-auth-multiline-swallow`. → the auth line-bound is load-bearing for the C13 half.
* **M3** (`product_mut_auth1`): rule table rc 3, `credential_leaks` = exactly
  `[cred-header-bearer, cred-header-scheme, cred-auth-multiline-swallow, cred-auth-sameline-tail-kept]`,
  and the marker is visibly present in the output, e.g.
  `'Authorization: <redacted> SYNTHETIC_AUDIT_TOKEN'`. → a scheme-ignoring strict single token **leaks**.

All three claims reproduce exactly. Note the logical limit of this proof: **M3 proves a *different*
auth rule leaks; it does not prove the *chosen* rule does not leak.** It does — see F-REV-D-01.

### Claim 7 — declared residual N13 — **VERIFIED**

`redact_text("password: iron steel")` → `"password: <redacted> steel"` (26 chars) on narrow;
`"password: iron steel"` (greedy, unchanged) on base. `redact_text("password: 'iron steel'")` →
`"password: <redacted>"` — quoting still gives full coverage. The residual is registered as rule-table
row `res-partial-multiword-secret` with kind `residual`. Declared, not hidden. **But** see Ruling 2:
the *auth-path analogue* of N13 was mis-classified as the same "residual" class when it is in fact a
full credential leak.

### Claim 8 — oracle CORRECTION 1 — **VERIFIED, and genuinely append-only**

* `before/oracle.md.pre-correction-1`: sha256 `d8deaee4e7f4a21c13722ffa58c18c2c093d789b9701d249880f95f7bd3fddb4`,
  11999 bytes — matches the claimed pre-correction hash.
* `oracle.md` (current): sha256 `6baad12cda54abda9bacebd255b9065aa6126dc96cbc581c88a1904a68336cd8`,
  12823 bytes — matches.
* I compared the raw bytes: the pre-correction file is a **byte-exact prefix** of the current file,
  with 824 bytes appended beginning `"\n\n---\n\n# CORRECTION 1 (2026-09-19, appended after the first A"`.
  **APPEND_ONLY_PREFIX_OK = true.**
* The correction itself is **right**, and I re-derived it independently:
  `S = "start-" + "x"*170 + " token=" + M + " " + "y"*120` → `len(S) == 325`;
  `redact_text(S) == 314`; `redact_and_truncate(S) == 200`;
  `redact_text(S)[:193] == "start-" + "x"*170 + " token=<redacted>"` → **true**;
  `redact_and_truncate(S)[193:] == " yyyyyy"` (**space + 6 y's**) → the off-by-one fix is correct;
  marker and `M[:8]` absent. The persisted probe tail is `"...cted> yyyyyy"`.

### Claim 9 — production untouched — **VERIFIED**

`C:\Users\郑曾波\Projects\company-wiki\src\company_wiki\source_catalog\observability.py`:

```
HEAD blob : d9ce30dfeb14d87e2a9a9a873e9b4972e3df3f85
worktree  : d9ce30dfeb14d87e2a9a9a873e9b4972e3df3f85   (git hash-object)
index     : d9ce30dfeb14d87e2a9a9a873e9b4972e3df3f85
git diff --quiet -- <path>  →  rc 0
```

Three independent plumbing checks agree: **the production redactor is byte-identical to its HEAD
blob; no production write occurred.** Raw-bytes hash of the production working file is
`a73826aa10c9c0bf09bb5dc73cb7466358497f9d9d8c66ba73bfe4b90ffebe5a` (30087 B, CRLF), **equal to
`iso/product`** — i.e. production is still the *pristine T0* tree, so I-14-C's r5 fix is likewise
unpromoted. That is consistent with both cards' scope statements ("promotion is a separate owner
decision"), but the carrier should be aware that **two** cards' fixes are now waiting on promotion.

`company-wiki` HEAD `f39bd5a6…` (branch `fcap`) equals the binding record; porcelain is
`M CLAUDE.md`, `M README.md`, `M src/company_wiki/source_catalog/artifact_dag.py`. The
`artifact_dag.py` edit has worktree mtime `2026-09-20T11:48:46Z`, i.e. **before** this attempt started
(2026-09-21), independently confirming the implementer's `after/external_edit_note.json`. I found no
evidence this attempt touched it.

---

## 2. INDEPENDENT RE-DERIVATION OF THE ORACLE NUMBERS

Every number below I computed from the frozen semantics text **before** running anything, then
confirmed against the trees. All agree.

| quantity | my hand computation | module result | agree |
|---|---|---|---|
| `len("upload failed for token=" + RM + tail)`, RM = `ZQ7_REVIEWER_MARKER_9f3c` (24) | 24 + 24 + 64 = **112** | 112 | ✅ |
| narrow output of N1 | 24 + 10 + 64 = **98** | 98 | ✅ |
| `len("a=1 token=" + M + " b=2")` | 10 + 21 + 4 = **35** → out **24** | 24 | ✅ |
| `len("token=" + M + "\nnext=1")` | 6 + 21 + 7 = **34** → out **23** | 23 | ✅ |
| `len(S)` N4 | 6 + 170 + 7 + 21 + 1 + 120 = **325** | 325 | ✅ |
| greedy `redact_text(S)` (base) | 6 + 170 + 7 + 10 = **193** | 193 (probe) | ✅ |
| narrow `redact_text(S)` | 325 − 21 + 10 = **314** | 314 | ✅ |
| narrow persisted (`[:200]`) | **200** | 200 | ✅ |
| N5 `"Authorization: Bearer " + M + "\ndoc=17\nstage=summarize"` | 22 + 21 + 7 + 16 = **66** → out 25 + 23 = **48** | 48 | ✅ |
| N13 `"password: iron steel"` | out 10 + 10 + 6 = **26** | 26 | ✅ |

`tail = " doc=17\nstage=summarize code=llm_global_failure request_id=req-1"` = 7+1+15+1+23+1+16 = **64** ✅

**The new E4b baseline (314 pre-truncation / 200 persisted) is CONFIRMED by independent re-derivation.**

---

## 3. FINDINGS

### F-REV-D-01 — **BLOCKER (high): the auth path now persists a credential in plaintext when a line break separates the scheme word from the secret**

Measured on `iso/product_narrow` with the synthetic secret
`ghp_ZQ7ReviewerFakeCredential0123456789` (39 chars, no whitespace):

| # | input | base `redact_text` | narrow `redact_text` | leak |
|---|---|---|---|---|
| D1 | `Authorization: Bearer\n<SECRET>\ndoc=17` | `Authorization: <redacted>` | `Authorization: <redacted>\n<SECRET>\ndoc=17` | **YES** |
| D2 | `Authorization: Bearer \n<SECRET>` | `Authorization: <redacted>` | `Authorization: <redacted> \n<SECRET>` | **YES** |
| D3 | `Authorization:Bearer\n<SECRET>` | `Authorization:<redacted>` | `Authorization:<redacted>\n<SECRET>` | **YES** |
| D4 | `authorization: token\n<SECRET>` | `authorization: <redacted>` | `authorization: <redacted>\n<SECRET>` | **YES** |
| D5 | `Authorization: Bearer\r\n<SECRET>` | `Authorization: <redacted>` | `Authorization: <redacted>\r\n<SECRET>` | **YES** |
| D6 | `Authorization: Bearer\n  <SECRET>` (HTTP obs-fold) | `Authorization: <redacted>` | `Authorization: <redacted>\n  <SECRET>` | **YES** |
| D7 | `stage=summarize Authorization: Bearer\n<SECRET>\nrequest_id=req-1` | `stage=summarize Authorization: <redacted>` | `stage=summarize Authorization: <redacted>\n<SECRET>\nrequest_id=req-1` | **YES** |
| D8 | `Authorization: Bearer\t<SECRET>` | `Authorization: <redacted>` | `Authorization: <redacted>` | no |
| D9 | `Authorization: Bearer <SECRET>` | `Authorization: <redacted>` | `Authorization: <redacted>` | no |

**End-to-end confirmation through the real worker exit** (my own driver in reviewer scratch, using the
product's own `CW/tests/contract/` doubles, reading the persisted `unhandled_exception` event):

```
product_narrow / bearer-newline
  raw_message                : "Authorization: Bearer\nghp_ZQ7…789\ndoc=17"
  persisted_message_redacted : "Authorization: <redacted>\nghp_ZQ7…789\ndoc=17"
  SECRET_ABSENT_FROM_PERSISTED: false      ← credential persisted in plaintext
  doc17_survives             : true        ← the card's goal is met
product_base   / bearer-newline
  persisted_message_redacted : "Authorization: <redacted>"
  SECRET_ABSENT_FROM_PERSISTED: true
```

So the fix trades "diagnostics deleted" for "**secret written to the append-only event log**" on this
input family. `worker.py:1066` is `message_redacted=redact_and_truncate(message)`, and
`redact_and_truncate` is `redact_text` then `[:200]` — the leaked line is well inside 200 chars.

**Root cause.** In `_AUTH_PATTERN` the first key alternative `authorization\s*[:=]\s*` matches and
consumes `Authorization: `; the value alternation is then tried at `Bearer`, where the line-bounded
`_AUTH_BARE_VALUE = [^\s,;&"'|]+(?:[ \t]+[^\s,;&"'|]+)*` matches **only the scheme word** (because
`\n ∉ [ \t]`). The secret on the next line has no `key=` prefix, so `_redact_assignments` cannot see it
either. On the base tree the greedy `_BARE_VALUE`'s `\s+` join crossed the newline and consumed
scheme + secret together.

**Why the attempt's own controls missed it.**
* The oracle's N13 *does* mention the phenomenon ("`Authorization: Bearer ab\ncd` →
  `Authorization: <redacted>\ncd`") but classifies it as **"the accepted cost … loses only its
  continuation"** and registers **no rule-table row** for it. With a real wrapped header the entire
  secret, not a continuation fragment, is what survives.
* `credential_leaks == []` on the 48-row table is therefore **not sound evidence** for exit criterion 2
  on the auth path: no row exercises `scheme␊secret`.
* The mutation plan tests the *other* direction (M2: does the line-bound carry the C13 fix?) and a
  *different* candidate rule (M3: does a scheme-ignoring single token leak?). Neither M2 nor M3 can
  detect that the chosen rule leaks.
* The copied suite's auth rows are all single-line (`Authorization: Bearer <marker>`), so 78 GREEN is
  consistent with the leak.

**Required remediation.** Either the scheme-aware fail-closed value (Ruling 2 / §5), or an equivalent
that cannot leave a token after a scheme word unredacted, **plus** rule-table and `FIDELITY_CASES`
rows for `Authorization: Bearer\n<marker>` (LF, CRLF, obs-fold, and `authorization: token\n`). Re-run
the oracle, rule table, both suites and the mutation plan afterwards.

### F-REV-D-02 — **MEDIUM: the headline regex edit has no runtime effect**

`_VALUE = r"(?P<value>" + _QUOTED_VALUE + r"|" + _BARE_VALUE + r")"` is **defined but never used** in
either tree — `_AUTH_PATTERN` inlines the pieces, and the assignment scanner is hand-written and does
not use `_VALUE` at all. I confirmed this by scanning every occurrence of `_VALUE` in both files.

Consequence: narrowing `_BARE_VALUE` from `X+(?:\s+X+)*` to `X+` is **intent documentation only**; the
assignment-path behaviour change comes **entirely** from the scanner-loop rewrite (`changes.diff`
hunk 2). This is not a defect — the mutation proof correctly shows the loop is load-bearing (M1) — but:
* the card's stated mechanism ("anchor: `_BARE_VALUE`") is not what fixes the assignment path;
* a future reader (or promoter) could "tidy" the dead constant and believe the fix is intact;
* the same dead-constant pattern in `_AUTH_PATTERN` is exactly where L1 (`F-REV-D-01`) hides: the
  scheme-word branch is chosen by alternation order, not by anything that recognises a scheme.

Recommendation (non-blocking): delete `_VALUE`, or use it, and add a comment saying the scanner loop
is the assignment-path mechanism.

### F-REV-D-03 — **MEDIUM: the narrowing exposes a pre-existing atom-table gap as a new observable leak**

```
narrow: redact_text("token=<A> token2=<B> b=2") -> "token=<redacted> token2=<B> b=2"   (2nd marker survives)
base  :                                          "token=<redacted>"                     (masked by the swallow)
key_is_credential("token2") == False,  key_is_credential("secret2") == False,
key_is_credential("password2") == False,  key_is_credential("api_key2") == False
key_is_credential("token_2") == True, key_is_credential("refresh_token") == True
```

Root cause is pre-existing (digit-suffixed names are not in the atom tables); the greedy swallow used
to delete them by accident. The narrowing makes the gap observable. Lower severity than F-REV-D-01
because realistic compound names (`refresh_token`, `access_token`, `my_token`) do work, but
`SECRET2=`/`PASSWORD2=` do occur in env dumps. Suggest a rule-table row plus a follow-up card.

### F-REV-D-04 — **LOW: one C13 sub-case remains unfixed on the auth path (pre-existing, not a regression)**

Both trees still swallow a following token when the header has **no value on its line**:

```
base  : "Authorization:\ndoc=17\nstage=summarize" -> "Authorization:\n<redacted>"                              (both keys lost)
narrow: "Authorization:\ndoc=17\nstage=summarize" -> "Authorization:\n<redacted>\nstage=summarize"            (doc=17 still lost)
narrow: "Authorization:\n\n doc=17"              -> "Authorization:\n\n<redacted>"   (blank-line variant, spurious <redacted>)
```

Cause: the **key-side** `\s*` in `authorization\s*[:=]\s*` crosses newlines, so the next token is taken
as the value. The narrowing improves this case (one of two keys now survives) but does not close it.
Not a regression and not a blocker for this card — but the card's exit clause ("裸值不再跨行吞掉后续诊断键")
is only **partially** met on the auth path and this should be carried as an open C13 sub-case.

### F-REV-D-05 — **LOW (documentation inconsistency)**

`binding.json → allowed_product_edits` states `harness/tests/conftest.py (one-line tree-pointing
change, recorded in changes.diff scope note)`. It is **byte-identical** to I-14-C's
(`783b1774ec2115eea0b2c3c92b6572842bb41eeda08054d69ec625fbcafbb7a9`, 275 B), as `handoff.json`
correctly says. Also, the copied `conftest.py` adds only `harness/` to `sys.path`; it does **not**
point at a tree — the tree comes from `I14C_PRODUCT_SRC`. Cosmetic, but it is an untrue statement in a
binding document.

### F-REV-D-06 — **LOW (reporting clarity)**

`run_rule_table_i14d.py` reports `residuals_confirmed` = 3 rows while `counts.json` reports
`rule_kinds.residual` = 4. This is **consistent** — `residuals_confirmed` filters on `marker_survives`,
and the 4th row (`res-partial-multiword-secret`, `"password: iron steel"`) contains no marker — but the
key name under-reports the residual inventory by one. Rename to `residuals_with_marker_surviving` or
emit both lists.

### F-REV-D-07 — **INFO (external drift, not caused by this attempt)**

* `revenue-forecast` HEAD is now `ab20cebea21fa2e540ad5bab15a00ad116d28e14`; `binding.json` records
  `2c5384bb0133c4e19c3d6049449b32469e14b09b`. The intervening commits are **other cards' planning
  carriers** (`I-14-H landed`, `I-10-B carrier landed`, `I-05-C carrier landed`) — the plan tree lives
  inside the `revenue-forecast` checkout. Not this attempt's doing; the plan tree is version-controlled,
  so the attempt's nested scratch repos (`scratch/apply-check`, `scratch/diff-repo`, both carrying their
  own `.git`) also show as modified gitlinks in `git status`.
* `company-wiki` HEAD still matches the binding (`f39bd5a6…`).

---

## 4. UNVERIFIED LIST

Stated plainly so the carrier can weigh the verdict:

1. **Real-CLI E5a/E5b numbers** (claim 4: "E5a 0 hits, E5b 1 declared-residual hit, no catalogs").
   I did not re-run `harness/run_real_cli_exit.py`. The CLI envelope path is partially covered by the
   copied suite's E5 nodes, which passed on narrow. The specific hit counts in
   `after/cli/E5a|E5b/result.json` are **taken on trust**.
2. **The 30-entry diagnostic corpus** (carry `C13-narrow-3`, `harness/run_diagnostic_table.py`) is not
   present in this attempt, so its C13-family rows (which will legitimately fail against the narrowed
   redactor) were **not** re-run or enumerated by me. The carrier must schedule that rewrite.
3. **The five kept failed attempts** (`B1-pass1/2/3`, `B4-pass1/2`, `P1-pass1`, `A5-pass1`) were read
   from `commands.json` and their evidence dirs exist, but I did not replay them; their failure
   narratives are taken on trust.
4. **Venv provenance** (packages copied from I-14-C's venv because the I-00-A template ships only pip)
   — I confirmed only that the interpreter works and reports Python 3.13.9 / pytest 9.1.1. I did not
   diff the venv against I-14-C's.
5. **Performance / ReDoS linearity** and the F07 deadline assertion were not re-timed beyond the
   suite's own passing assertion.
6. The product test doubles under `CW/tests/contract/` were executed (17 subprocess cases) but I did
   not audit them as evidence in their own right.
7. `after/cli/**` and `after/runs-narrow/**` contents were not byte-audited (they are outputs, not
   claims); the hashes listed for them in `final_hashes.json` do reproduce.

---

## 5. RULINGS (card clause 5 + decision.md D1)

### RULING 1 — the 4 frozen greedy-semantics nodeids: **rewrite ACCEPTED, with exact new expected values, conditional on F-REV-D-01**

I accept the principle: per card clause 5 the rewrite is the reviewer's act, and the new values follow
from the narrowed semantics I verified. I derived them by hand and then confirmed them against the
narrow tree. **Condition:** do not land the rewrite while F-REV-D-01 stands, because clause 5's purpose
is to move the criterion onto the *new* semantics — not to freeze an oracle that is silent about a
credential leak. Land the rewrite **together with** the F-REV-D-01 fix and its new auth rows.

**Nodeid 1** — `test_f08_c13_multiline_loss_is_frozen_not_hidden`.
The name asserts a behaviour that no longer exists; rename to
`test_f08_c13_multiline_diagnostics_survive` (renaming changes the nodeid, which is correct here — the
old name is a false statement about the current tree). New body, keeping the test's original intent
(the criterion must not be blind to multi-line inputs) and its "not a truncation artefact" guard:

```python
tail = " doc=17\nstage=summarize code=llm_global_failure request_id=req-1"
for marker in (MARKER, review_marker):
    text = "upload failed for token=" + marker + tail
    out = redact_and_truncate(text)
    assert out == "upload failed for token=<redacted>" + tail     # len(out) == 98 for both markers
    assert len(out) < 200, "well below the 200-char limit, so this is not truncation"
    assert len(out) > 90,  "the multi-line diagnostics must survive"
    assert marker not in out, "the marker must still be redacted"
    for kept in ("doc=17", "stage=summarize", "code=llm_global_failure", "request_id=req-1"):
        assert kept in out, f"C13 narrowing lost the diagnostic key {kept!r}"
# the reviewer's exact reproduction: 24-char marker -> 112 chars in, 98 out
assert len("upload failed for token=" + review_marker + tail) == 112
assert len("upload failed for token=" + MARKER + tail) == 109
```
Note the inversion: the old `assert lost not in out` loop becomes `assert kept in out`, and
`len(out) == 34` becomes `len(out) == 98`. Both must change inside this one nodeid.

**Nodeids 2–4** — the three `FIDELITY_CASES` parameters. **Only the expected strings change**; keep the
parametrization, the pair count (still **28**, so `counts["fidelity_cases"] == len(FIDELITY_CASES) ==
counts["exact_nodeids"] == 28` still holds and `r5/counts.json` need not be regenerated by *this* step):

| nodeid (unchanged) | new expected value |
|---|---|
| `…exact[a=1 token=SYNTHETIC_AUDIT_TOKEN b=2-a=1 token=<redacted>]` | `"a=1 token=<redacted> b=2"` |
| `…exact[upload failed for token=SYNTHETIC_AUDIT_TOKEN doc=17\nstage=summarize code=llm_global_failure request_id=req-1-upload failed for token=<redacted>]` | `"upload failed for token=<redacted> doc=17\nstage=summarize code=llm_global_failure request_id=req-1"` |
| `…exact[token=SYNTHETIC_AUDIT_TOKEN\nnext=1-token=<redacted>]` | `"token=<redacted>\nnext=1"` |

Two mandatory companion edits in the same file:
* the inline comments above the table (currently `# greedy value (r1 _BARE_VALUE semantics, kept - see
  carry C13):` and `# Frozen as CURRENT BEHAVIOUR so the criterion is not blind in this direction any
  more.`) now describe superseded behaviour and must be rewritten to the narrowed semantics;
* **no change** to `("failed for token=" + MARKER + "; see log\nstage=…")` — I verified it is GREEN on
  both trees.
* **Required addition** (this is my condition, not optional): add `FIDELITY_CASES`/rule-table rows for
  `Authorization: Bearer\n<marker>` (LF), CRLF, obs-fold (`\n  `), and `authorization: token\n<marker>`,
  each asserting the **marker is absent**. Adding rows changes the count, so
  `harness/report_i14d_counts.py` must then be re-run and `r5/counts.json` regenerated (the suite's
  count assertion will otherwise fail — which is the mechanism working as designed).

### RULING 2 — `decision.md` D1 (auth-path choice): **OVERTURNED — neither option 1 nor option 2 is acceptable as written; adopt a scheme-aware fail-closed value**

The implementer framed D1 as option 1 (line-bound token run) vs option 2 (scheme word moved into the
KEY). That framing is incomplete, and the verdict on it is:

* **Option 1 (chosen) is rejected as implemented**, because it fails the card's own negative clause:
  any line break between the scheme word and the secret leaves the secret in the clear and persists it
  (`F-REV-D-01`, measured helper-level and end-to-end).
* **Option 2 should NOT be preferred.** As described (`authorization\s*[:=]\s*(?:\S+\s+)?` as the KEY,
  strict single token as the value) it has the *same* hole — the optional scheme group is itself
  line-bounded in any safe reading — and it is *worse* if `\s+` is used inside that group, because then
  the greedy optional group can consume a line break and take the *next diagnostic key* as the value,
  re-introducing C13 on the key side. It also rewrites five frozen I-14-C envelopes and the E1 exact
  assertion, for no benefit over a third option.
* **Option 3 (leave the auth regex untouched) stays rejected** — the implementer is right that C13
  would then remain open on the auth path, and M2 is legitimate evidence that the line bound is
  load-bearing for that half.

**The right call is a third option: scheme-aware, fail-closed.** A token may follow a *known* scheme
word across **one** line break, and that token is then redacted; otherwise the value stays a
line-bounded token run. I built this prototype in reviewer scratch (never touching `iso/`) by adding a
scheme alternative ahead of `_AUTH_BARE_VALUE`:

```python
_AUTH_SCHEME_SPLIT = (r"(?:bearer|token|basic|digest|oauth|jwt|apikey|api_key|sso)"
                      r"[ \t]*\r?\n[ \t]*[^\s,;&\"'|]+")
# value group order: _QUOTED_VALUE | _AUTH_SCHEME_SPLIT | _AUTH_BARE_VALUE
```

Measured on the prototype:

* oracle **17/17, rc 0**; rule table **48 entries, 0 leaks, 0 touched, fidelity ok, rc 0**;
* all of D1–D10 **SECRET_LEAKS = False**;
* end-to-end: `Authorization: Bearer\n<SECRET>\ndoc=17` persists as **`"Authorization: <redacted>\ndoc=17"`**
  — **secret gone AND diagnostics kept**, i.e. both halves of the card's exit clause satisfied;
* same-line controls unchanged (`Authorization: Bearer <SECRET>` → `Authorization: <redacted>`);
* the copied suite on the prototype still yields **exactly the same 4 RED / 78 GREEN**, so Ruling 1's
  rewrite set is unchanged by this fix.

**Minimum acceptable alternative** if the owner wants a smaller diff: if the matched auth value is
*exactly* a known scheme word, also redact the first token after the following line break (fail closed).
Same closure, narrower change, but it will over-redact `Authorization: Bearer\ndoc=17` the way the base
tree did. I recommend the prototype form because it is already measured.

**Also required by this ruling:** re-label the auth-path note in `oracle.md` N13 from "declared
residual" to "credential-leak regression", give it a rule-table row, and add the auth rows listed in
Ruling 1. The current "loses only its continuation" wording materially understates the exposure — that
wording is precisely why the defect survived the oracle, the rule table and all three mutations.

### RULING 3 — residual N13 (assignment path): **accepted as declared**, with a scope limit

`"password: iron steel"` → `"password: <redacted> steel"` is a genuine, disclosed consequence of
"one token", it is measured on both trees, it is a `residual`-kind rule-table row, and quoting restores
full coverage. Accepted. It is **not** the same class as `F-REV-D-01` (there, a *whole* credential
survives where the pre-fix tree redacted it) — the two must not be merged in the record.

---

## 6. SCOPE / AUTHORIZATION NOTES

* **Promotion is untouched and is a separate owner decision.** Production `observability.py` is
  byte-identical to its HEAD blob (verified three ways). Nothing was promoted by this attempt, and
  nothing was promoted by I-14-C either.
* **I-14-C was not modified.** I confirmed byte-identity of everything this attempt copied from it:
  the frozen suite (`672b88de…`) and `conftest.py` (`783b1774…`).
* **Recovery rule holds.** Reverse-applying `changes.diff` to the narrow tree reproduces
  `product_base` byte-for-byte across all 152 files (rc 0). The redactor is a pure function, so
  crash-restart evidence is genuinely NA.
* **The `r5/counts.json` shim** in this attempt is explained by `r5/README.txt` and is consistent with
  the copied suite's count binding; nothing from I-14-C was copied into it. Disclosed, acceptable.
* **Absence of implementation of clause 5** (the implementer correctly left the 4 nodeids
  byte-identical) is a **positive** finding — the card's separation of duties was respected.
* **Reviewer side effect, disclosed.** Running the oracle/rule-table scripts with the iso venv
  interpreter refreshed `__pycache__/*.pyc` files under `iso/*/src/company_wiki/source_catalog/`.
  These caches **pre-existed** from the implementer's own runs (mtimes 18:57–19:05 UTC); the mutation
  trees' `observability.cpython-313.pyc` carry my later mtimes. `after/final_hashes.json` covers **no**
  `.pyc` path, so the 46-entry byte-pin is unaffected — and I re-ran the full 46-entry recomputation
  after all reviewer runs: **46/46 reproduce.** No source file, JSON evidence file or document in the
  attempt was modified by this review; the only file written into the attempt dir is this report.
* What this attempt **does** grant: a byte-pinned demonstration that the C13 narrowing works on the
  assignment path, a re-derivable new E4b baseline (314/200), an honest mutation proof, and a
  genuinely append-only oracle correction.
* What it does **not** grant: promotion, `disclosure_adaptation` (unmapped), accuracy (unproven), and —
  as of this review — **acceptance**, pending `F-REV-D-01`.

---

## 7. HOW TO REPRODUCE THIS REVIEW

Scratch root used: `%TEMP%\i14d_review\`. Interpreter:
`<ATT>\iso\venv\Scripts\python.exe` (Python 3.13.9, pytest 9.1.1).

```powershell
$A = "<attempt dir>"; $PY = "$A\iso\venv\Scripts\python.exe"

# oracle / rule table (base must be rc 3, narrow rc 0)
& $PY "$A\harness\run_i14d_oracle.py"      --src "$A\iso\product_base\src"   --label base   --out o_base.json
& $PY "$A\harness\run_i14d_oracle.py"      --src "$A\iso\product_narrow\src" --label narrow --out o_narrow.json
& $PY "$A\harness\run_rule_table_i14d.py"  --src "$A\iso\product_base\src"   --label base   --out rt_base.json
& $PY "$A\harness\run_rule_table_i14d.py"  --src "$A\iso\product_narrow\src" --label narrow --out rt_narrow.json

# copied suite (narrow: exactly 4 failed / 78 passed; base: 82 passed)
$env:I14C_PRODUCT_SRC = "$A\iso\product_narrow\src"
& $PY -X utf8 -B -m pytest "$A\harness\tests\test_i14c_real_exit_redaction.py" -q --tb=no -rf -p no:cacheprovider

# new suite (narrow 21 passed; base 9 failed / 12 passed)
$env:I14C_PRODUCT_SRC = "$A\iso\product_base\src"
& $PY -X utf8 -B -m pytest "$A\harness\tests\test_i14d_single_token.py" -q --tb=no -rf -p no:cacheprovider

# mutations: oracle + rule table against product_mut_greedy / _authnl / _auth1
# probe (real exit): base E4b 193, narrow E4b 200, mut_greedy E4b 193
& $PY "$A\harness\run_exit_probe.py" --label <l> --out <dir> --run-root <fresh dir> `
      --python $PY --src "$A\iso\<tree>\src" --tests-dir "C:\Users\郑曾波\Projects\company-wiki\tests\contract"

# diff round-trip: copy product_base to a scratch repo, git init, autocrlf=false,
#   git apply --check -p1 / -p1 / -R -p1 changes.diff, byte-compare.
```

Reviewer's own scripts (outside the attempt, for F-REV-D-01 and Ruling 2):
`adv_probe.py`, `adv_probe2.py`, `e2e_leak_check.py`, and the proto tree
`proto/src` (`build_proto` result) under `%TEMP%\i14d_review\`.

---

## 8. BOTTOM LINE FOR THE CARRIER

1. **Do not accept I-14-D as-is.** `F-REV-D-01` is a credential-persistence regression on the auth
   path, proven end-to-end, and it sits inside the card's own negative clause.
2. **The rest of the attempt is sound** — all nine implementer claims I was asked to verify reproduce,
   the E4b baseline re-derivation (314/200, tail = space + 6 y's) is confirmed, the diff round-trips
   both ways, the production tree is provably untouched, and the oracle correction is genuinely
   append-only. The implementer's honesty about scope is exemplary.
3. **Ruling 1** gives the exact 4 nodeid rewrites (conditional on the fix).
4. **Ruling 2** overturns D1 and hands the owner a measured, minimal, already-validated replacement
   (scheme-aware fail-closed auth value) that satisfies **both** halves of the exit clause.
5. Cheapest path to green: apply the Ruling-2 prototype regex, add the auth newline-split rows to the
   rule table and `FIDELITY_CASES`, re-run oracle + rule table + both suites + the mutation plan, then
   land the Ruling-1 rewrite.
