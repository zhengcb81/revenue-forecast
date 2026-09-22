# I-14-D — INDEPENDENT REVIEWER REPORT (r2 re-review)

Card: **I-14-D** (narrow the redactor's greedy bare-value semantics to a single token — the C13 card)
Attempt: `execution_runs/I-14-D/a20260919-01`
Revision under review: **r2** (the BLOCKER-fix revision of the r1 pass)
Reviewer: **independent reviewer** (not the implementer; no implementer artifact was edited)
Date of review: 2026-09-21
Review posture: read-only. Neither production checkout nor any file of the attempt was modified by
this review; the only file written into the attempt dir is this report. All reviewer scratch output
(probes, drivers, run dirs, round-trip repos) lives **outside** the attempt, under
`%TEMP%\i14d_review_r2\`. Every subprocess ran with `-B` / `PYTHONDONTWRITEBYTECODE=1`, so not even a
`__pycache__` file under `iso/` was refreshed by this pass.

Predecessor report (r1, byte-pinned by the carrier): `reviewer_report.md`, sha256
`499d91acf06a67e2f7dd06d4a5af6569b5b92a6e4b3b77adda57b739eaa03d2b`, 37659 bytes — **recomputed by me
before reading; both match the pin.**

---

## 0. VERDICT

**CHANGES_REQUIRED — the r2 revision is NOT accepted.**

The BLOCKER **F-REV-D-01 is closed for the family the predecessor measured**, and closed exactly as
prescribed: the RULING-2 `_AUTH_SCHEME_SPLIT` branch is applied verbatim, the real worker exit now
persists `"Authorization: <redacted>\ndoc=17"` for a wrapped `Bearer` header (I reproduced that string
with my own end-to-end driver), the helper probe is 12/12 closed with `fidelity_drift []`, the oracle,
the rule table and the copied suite are all rc 0 on the deliverable, the byte-pins and diffs round-trip,
M4 is the pre-r2 tree by construction, the RULING-1 rewrite is a faithful transcription, and production
is provably untouched.

**The finding is that the fix closes the measured *instance* but not the *class*.** F-REV-D-01's own
sentence — "the auth path now persists a credential in plaintext when a line break separates the scheme
word from the secret" — is still true on the r2 tree for every scheme word outside the 9-word
enumeration, and for two adjacent shapes:

> `"Authorization: Negotiate\nSYNTHETIC_AUDIT_TOKEN\ndoc=17"`
> → persisted `"Authorization: <redacted>\nSYNTHETIC_AUDIT_TOKEN\ndoc=17"` —
> **the card's own synthetic marker, in plaintext, in the append-only event log**, where the
> pre-I-14-D tree (`iso/product_base`) persisted `"Authorization: <redacted>"`.

This is the same defect shape, the same negative-clause violation (`纯合成 marker 必须仍被脱敏`) and the
same evidence standard the predecessor used to call F-REV-D-01 a BLOCKER; the only difference is which
scheme word appears before the line break. It is **not disclosed anywhere in the attempt's records**
(I searched every record for the family and for the words "unlisted", "other/unknown scheme" — the only
occurrence of "known scheme" is in `decision.md:45`, about a *rejected* alternative), and it is **not
registered in the oracle or the rule table**, so `credential_leaks == []` is once again — for this
family — not sound evidence for exit criterion 2. See **F-REV-R2-01**.

RULING 2's own remedy sentence asked for "an equivalent that **cannot leave a token after a scheme word
unredacted**". The applied branch can. The predecessor's snippet was too narrow, and the re-review's job
is to measure that, not to ratify it.

Two further findings are recorded but are **not** blockers: an over-redaction family that the fix
introduces and that *is* disclosed in `decision.md` but is not machine-registered (**F-REV-R2-02**), and
a false measured claim repeated in three records (**F-REV-R2-03**).

Everything else in the r2 revision is sound, and several r1 "unverified" items are now verified.

---

## 1. WHAT CHANGED IN r2 — CLAIM-BY-CLAIM VERIFICATION

### Claim 1 — the fix, its hashes and its invertibility — **VERIFIED, exactly**

| tree | `observability.py` sha256 (raw bytes) | bytes | line endings |
|---|---|---|---|
| `product` (T0 pristine) | `a73826aa10c9c0bf09bb5dc73cb7466358497f9d9d8c66ba73bfe4b90ffebe5a` | 30087 | all-CRLF (625/625) |
| `product_base` (I-14-C r5, card start) | `c5608c4b45a55cce03df9988561e1a3ad1cab0970c51e8b3af630239fe9de35c` | 40060 | all-CRLF |
| pre-r2 tree (= r1 deliverable) | `e8abd522b2072add062be225d7ec1ca10621ffa5be7841f99ef9fb339015cbd0` | 40476 | all-CRLF |
| **`product_narrow` (r2 deliverable)** | **`2aa5ed1a219084a67f040388072aa94d7432c63414b6692060f1b4d6b4e12bde`** | **41432** | **all-CRLF (878/878)** |
| `product_mut_greedy` (M1) | `bc857d411a5363674fff93366f8e6eb717edb670cf2d95178554f81c4984738b` | 41638 | all-CRLF |
| `product_mut_authnl` (M2) | `a36e90b62e2206f7017d448f8b051c56448fb24102a2c9def82f384ea39e5137` | 41429 | all-CRLF |
| `product_mut_auth1_r2` (M3) | `ef450712f13274af82da244b6cea0e3294892ae8d1232ff0c57f3137cc3ecf82` | 41427 | all-CRLF |
| `product_mut_authsplit` (M4) | `e8abd522b2072add062be225d7ec1ca10621ffa5be7841f99ef9fb339015cbd0` | 40476 | all-CRLF |

`+956 B` = 41432 − 40476 **confirmed**; CRLF preserved in every tree.

The applied text is the predecessor's RULING-2 snippet **character for character**
(`(?:bearer|token|basic|digest|oauth|jwt|apikey|api_key|sso)` + `[ \t]*\r?\n[ \t]*[^\s,;&\"'|]+`),
placed first in the value alternation after `_QUOTED_VALUE`:

```python
    + _LEFT_ANCHOR + r"bearer\s+)(?P<value>" + _QUOTED_VALUE + r"|" + _AUTH_SCHEME_SPLIT + r"|" + _AUTH_BARE_VALUE + r")"
```

* `changes_r2_authsplit.diff` — **1786 bytes, 1 hunk, 1 file, POSIX paths**, sha256
  `40a146d4745652e63d75e7eb17787daf4c255c5544d295219cd29b342c3f18bc` — confirmed.
* **Invertibility, tested by me on copies (never on the deliverable):**
  `apply_i14d_narrow.py --op reverse_authsplit` on a copy of the r2 file →
  `e8abd522…015cbd0`, 40476 B — **the pre-r2 tree, byte-for-byte**; and `--op authsplit` on a copy of
  the pre-r2 file → `2aa5ed1a…4e12bde`, 41432 B — **the deliverable**. The fix is exactly reversible and
  exactly reproducible from its own inverse.
* `changes.diff` (the full deliverable diff, 5101 B, 2 hunks): applied with `git apply -p1` to a scratch
  copy of `product_base` in a `core.autocrlf=false` repo → **rc 0**, and a **full 152-file byte
  comparison against `iso/product_narrow/src` gave 0 mismatches**; `git apply -R -p1` → rc 0 and returns
  `observability.py` to `c5608c4b…` exactly.
* The four mutation trees are genuine single-site derivations of the r2 tree (line-diff against the
  deliverable): M1 = one contiguous block (the r1 scanner loop + comment), M2 = **1 line**
  (`[ \t]+` → `\s+` in `_AUTH_BARE_VALUE`), M3 = **1 line** (`_AUTH_BARE_VALUE` → `_BARE_VALUE` in the
  auth value group), M4 = the r2 hunk reversed (comment block + `_AUTH_SCHEME_SPLIT` definition + the
  value-group line).

### Claim 2 — RULING 1 landed — **VERIFIED** (transcription check in §4)

Nodeid renamed `test_f08_c13_multiline_diagnostics_survive`; loop inverted; `len(out) == 98`; both input
lengths kept (`== 112` for the 24-char reviewer marker, `== 109` for the 21-char marker); marker-absent
guard kept; the three `FIDELITY_CASES` expectations replaced with the reviewer's values; the four
required auth newline-split rows added (LF, CRLF, obs-fold, `authorization: token\n`); the two stale
comments rewritten; the `("failed for token=" + MARKER + "; see log\n…")` row left unchanged. Counts
regenerated and consistent (§5).

### Claim 3 — new leak-direction coverage — **VERIFIED**

* Oracle N5c/N5d/N5e present and hand-computed (32 / 25 / 25 chars).
* Rule table `cred-auth-split-*` ×7, including `cred-auth-split-bearer-real-secret` carrying the
  predecessor's **39-char non-marker credential** — the row that makes a marker-only table insufficient.
* **M4 `iso/product_mut_authsplit` is byte-identical to the pre-r2 tree across all 152 files** (my
  full-tree comparison: `product_mut_authsplit/src` differs from `product_narrow/src` in **exactly one**
  file, `observability.py`, and that file's hash equals the pre-r2 hash; it also differs from
  `product_base` in exactly one file). So M4 is literally the tree the r1 review condemned — the
  regression "re-opened by construction", not merely a lookalike.
* **Detection matrix — I re-measured it myself at two levels** (oracle rows, and the real worker exit
  through my own driver, scenario `Authorization: Bearer\n<39-char secret>\ndoc=17`):

| specimen | oracle N5c/N5d/N5e | real exit persisted | detects the leak class? |
|---|---|---|---|
| M1 `mut_greedy` | **pass** | `Authorization: <redacted>\ndoc=17`, secret absent | **no** |
| M2 `mut_authnl` | **pass** | `Authorization: <redacted>\ndoc=17`, secret absent | **no** |
| M3 `mut_auth1_r2` | **pass** | `Authorization: <redacted>\ndoc=17`, secret absent | **no** |
| **M4 `mut_authsplit`** | **fails all three** | `Authorization: <redacted>\n<secret>\ndoc=17` — **leak** | **yes** |

  The claim "M1–M3 all PASS the new e2e check, only M4 detects it" is **confirmed**, independently, at
  both levels.

### Claim 4 — F-REV-D-05 — **VERIFIED**

`binding.json → allowed_product_edits` no longer states that `harness/tests/conftest.py` carries a
one-line tree-pointing change; it now says the opposite and records the correction. The file itself is
**byte-identical to I-14-C's**: `783b1774ec2115eea0b2c3c92b6572842bb41eeda08054d69ec625fbcafbb7a9`,
275 B. Only `binding.json` changed.

### Claim 5 — recorded-not-fixed — **VERIFIED**

F-REV-D-02 (`_VALUE` dead code; `decision.md` carries the promotion hazard), F-REV-D-03 (digit-suffixed
atom-table gap), F-REV-D-04 (value-less `Authorization:`), F-REV-D-06 (residual key renamed and both
lists emitted — I confirmed `residuals_with_marker_surviving` = 3 and `residual_rows` = 4 in my own rule
table run), F-REV-D-07 (external HEAD drift) are all recorded and none was silently "fixed".
**Caveat:** F-REV-D-04's family is *widened* by this fix — see F-REV-R2-02.

### Claim 6 — production untouched — **VERIFIED, four independent ways**

```
raw sha256 : a73826aa10c9c0bf09bb5dc73cb7466358497f9d9d8c66ba73bfe4b90ffebe5a   30087 B  (all-CRLF)
worktree   : d9ce30dfeb14d87e2a9a9a873e9b4972e3df3f85   (git hash-object)
HEAD blob  : d9ce30dfeb14d87e2a9a9a873e9b4972e3df3f85   (rev-parse HEAD:src/…/observability.py)
index blob : d9ce30dfeb14d87e2a9a9a873e9b4972e3df3f85   (ls-files -s)
git diff --quiet -- <path> → rc 0
HEAD f39bd5a64224cd0c7aa098f23f64bf3811fa8939, branch fcap
```

Production is still the pristine T0 tree (equal to `iso/product`), so **both** I-14-C's r5 fix and this
card's fix remain unpromoted — consistent with both cards' scope, and worth the carrier's attention.
Porcelain is the same three pre-existing entries as r1 (`M CLAUDE.md`, `M README.md`,
`M artifact_dag.py`); `artifact_dag.py`'s worktree mtime is `2026-09-20T11:48:46Z`, i.e. **before** this
attempt began. I found no evidence this attempt or this review wrote to production: since the r1 report,
`observability.py`'s bytes have not moved at all.

---

## 2. THE DECISIVE CHECK — LEAK CLOSURE, RE-RUN BY ME

### 2.1 The pre-fix leak reproduces on the r1 tree (my own instrument)

I wrote my own 49-case differential probe (`rev_probe.py`, from scratch — not derived from the attempt's
`authsplit_probe.py`), carrying the r1 report's D1–D9 predictions verbatim so the pre-fix reproduction is
checked against the **predecessor's printed numbers**, not against trust. On M4 (= the pre-r2 tree):

```
r1_prediction_mismatches: []          ← all 9 r1-predicted pre-fix outputs match byte-for-byte
secret_leaks: A01-D1..A07-D7, B01..B10, C01..C09, F01..F05, F07, F09   (33 rows)
```

So the r1 tree really did persist `"Authorization: <redacted>\n<SECRET>\ndoc=17"`, and my instrument
agrees with the predecessor's table exactly.

### 2.2 r2 closes the measured family — confirmed on three instruments, and at the real exit

```
attempt's 12-row probe   : M4 10/12 leak (rc 3)  →  r2: credential_leaks [] , fidelity_drift [] , rc 0
attempt's oracle         : r2 20 cases, narrow_must_failed [] , keep_must_failed [] , rc 0
attempt's rule table     : r2 55 rows, credential_leaks [] , credential_secret_leaks [] ,
                           touched_but_should_not_be [] , fidelity_ok true , rc 0
```

Closed on r2 (my probe): the whole `D1–D7` family; **all nine enumerated scheme words** (`bearer`,
`token`, `basic`, `digest`, `oauth`, `jwt`, `apikey`, `api_key`, `sso`), plus `BEARER` upper-case and
`proxy-authorization:` (the `_LEFT_ANCHOR` lookbehind admits the `-authorization` form); CRLF; obs-fold;
tab after the break; the `|`-delimited and ` doc=17`-same-line shapes.

**Real exit, my own driver** (`rev_e2e.py`, driven through `SourceCatalogWorker.run_forever` with the
product's own contract doubles, reading the persisted `unhandled_exception.message_redacted`):

| tree | message | persisted | secret in any file of the run dir |
|---|---|---|---|
| `product_base` | `Authorization: Bearer\n<39-char secret>\ndoc=17` | `"Authorization: <redacted>"` (diagnostics deleted) | no |
| pre-r2 / M4 | same | `"Authorization: <redacted>\n<39-char secret>\ndoc=17"` | **yes — 1 hit in `worker_process_events.jsonl`** |
| **r2** | same | **`"Authorization: <redacted>\ndoc=17"` — exactly 32 chars** | **no — 0 hits in every file** |

The claimed closure string is **confirmed verbatim, end-to-end**. Both halves of the card's exit clause
hold together on this input. The E4b baseline is likewise re-derived on both trees and is **unchanged by
the fix**: 325 in → 314 pre-truncation → 200 persisted, `redact_text(S)[:193]` correct,
`persisted[193:] == " yyyyyy"`, marker absent. That also confirms the fix did not disturb the
assignment path.

### 2.3 But the leak class is NOT closed — **F-REV-R2-01**

My independent matrix, helper level, with the 39-char credential, on the r2 tree (**still leaking**, all
verified also against `product_base` and M4):

| # | input (S = 39-char credential, M = the card's marker) | base tree | r2 tree |
|---|---|---|---|
| C1 | `Authorization: Negotiate\n` + S + `\ndoc=17` | `Authorization: <redacted>` | `Authorization: <redacted>\n`**S**`\ndoc=17` |
| C2 | `Authorization: AWS4-HMAC-SHA256\n` + S + `\ndoc=17` | `Authorization: <redacted>` | leak |
| C3 | `Authorization: SCRAM-SHA-256\n` + S + `\ndoc=17` | `Authorization: <redacted>` | leak |
| C4 | `Authorization: Hawk\n` + S + `\ndoc=17` | `Authorization: <redacted>` | leak |
| C5 | `Authorization: Bot\n` + S + `\ndoc=17` | `Authorization: <redacted>` | leak |
| C6 | `Authorization: Mutual\n` + S + `\ndoc=17` | `Authorization: <redacted>` | leak |
| C7 | `Authorization: vapid\n` + S + `\ndoc=17` | `Authorization: <redacted>` | leak |
| C8 | `Authorization: HOBA\n` + S + `\ndoc=17` | `Authorization: <redacted>` | leak |
| C9 | `Authorization: Zzz\n` + S + `\ndoc=17` (any unknown word) | `Authorization: <redacted>` | leak |
| C10 | `Authorization: Bearer abc\n` + S (two-token value, then wrap) | `Authorization: <redacted>` | leak |
| C11 | `Authorization: Bearer\n\n` + S (blank line between) | `Authorization: <redacted>` | leak |
| C12 | `Authorization: Bearer\n"` + S + `"` (quoted continuation) | leak (pre-existing) | leak |

The marker form is decisive because it is the instrument the card's own negative clause names:

```
r2 tree   : redact_text("Authorization: Negotiate\nSYNTHETIC_AUDIT_TOKEN") -> "Authorization: <redacted>\nSYNTHETIC_AUDIT_TOKEN"
base tree : redact_text("Authorization: Negotiate\nSYNTHETIC_AUDIT_TOKEN") -> "Authorization: <redacted>"
```

and end-to-end through the real worker exit on the r2 tree:

```
message                                     : "Authorization: Negotiate\nSYNTHETIC_AUDIT_TOKEN\ndoc=17"
persisted message_redacted                  : "Authorization: <redacted>\nSYNTHETIC_AUDIT_TOKEN\ndoc=17"
secret_anywhere_in_run_dir                  : {"worker_process_events.jsonl": 1}
```

**Why this is a BLOCKER and not a disclosure.** (a) The input family is at least as realistic as the
`Bearer` one: `Negotiate` (RFC 4559 SPNEGO) tokens are long and wrap; `AWS4-HMAC-SHA256` is SigV4; the
scheme word is not what causes a header to wrap. (b) The card's starting tree did **not** persist this
marker, so the deliverable is a persistence regression relative to `product_base`, exactly as with
F-REV-D-01. (c) The fix's own comment discloses the scope ("only behind a *known* scheme word"), but no
record discloses that the excluded words still leak — I searched every `.md`/`.json` in the attempt for
`Negotiate|AWS4|SCRAM|Hawk|unlisted|other scheme|unknown scheme` and found nothing. (d) There is **no
oracle row and no rule-table row** for a non-enumerated scheme, so the strengthened criterion is blind to
this family in exactly the way C2.1 admits the original criterion was blind to `scheme␊secret`. (e) The
predecessor's remediation asked for an equivalent that *cannot* leave a token after a scheme word
unredacted; this one can.

**Remedy (one localized site, same shape as the current branch).** Make the pre-break token a generic
RFC-7235 scheme token rather than a 9-word alternation, e.g. replace the enumerated group with
`[A-Za-z][A-Za-z0-9!#$%&'*+.^_\`|~-]*` (an HTTP `token`), keeping the rest of `_AUTH_SCHEME_SPLIT`
identical. That closes C1–C11 in one line, and the over-redaction it implies (F-REV-R2-02) is *already*
disclosed and accepted for the nine listed words, so globalizing the branch adds no new class of cost.
C12 (quoted continuation) additionally needs `_QUOTED_VALUE` tried after the break. Whatever the owner
chooses, the residual must be **registered** — oracle + rule-table rows using both the marker and a
non-marker credential — before `credential_leaks == []` can be offered as exit-criterion evidence again.

---

## 3. FINDINGS

### F-REV-R2-01 — **BLOCKER (residual of F-REV-D-01): the auth newline-split leak is closed only for the nine enumerated scheme words**

Full evidence in §2.3. Resident risk: a real wrapped `Authorization:` header using any other scheme
persists its credential in the append-only event log, and the deliverable's own criterion reports zero
leaks. Not disclosed; not registered; a regression relative to the card's starting tree.

### F-REV-R2-02 — **MEDIUM: the fix over-redacts the first token after a known scheme word, and the "no over-redaction" evidence does not cover it**

The `_AUTH_SCHEME_SPLIT` branch cannot tell a wrapped credential from a diagnostic key. Measured, r2 vs
the pre-r2 tree (identical input, both trees, my probe):

| input | pre-r2 tree | r2 tree |
|---|---|---|
| `Authorization: Bearer\ndoc=17` | `<redacted>\ndoc=17` | `<redacted>` — **`doc=17` deleted** |
| `Authorization: Bearer\nrequest_id=req-1` | keeps the key | `<redacted>` — **key deleted** |
| `Authorization: Bearer\nstage=summarize` | keeps the key | `<redacted>` — **key deleted** |
| `Authorization: token\ndoc=17\nstage=summarize` | keeps both keys | loses `doc=17` |
| `proxy-authorization: Bearer\ndoc=17` | keeps the key | loses the key |
| CRLF / obs-fold-indented variants (4 more) | keeps the key | loses the key |

Nine measured shapes. This is the card's **own** defect class (a value crossing a newline and eating the
next diagnostic key) re-introduced on the auth path, and it **widens F-REV-D-04**, whose family was
"no value on the header's line".

**It is disclosed**: `decision.md` D1-r2 "Cost" says the branch "now always redacts the next token, i.e.
`Authorization: Bearer\ndoc=17` would over-redact `doc=17` the way the base tree did", and explains it as
the fail-closed direction. I accept the *direction* (never leak rather than never over-redact) and I do
**not** treat this as a blocker. What is missing is registration and honest scope on the evidence:
`authsplit_probe.py`'s `fidelity_drift []` is computed over a matrix in which **every** row puts a
credential after the scheme word, so it cannot see this family; and no oracle or rule-table row records
the cost. Note also that the r1 report's RULING 2 attributed this over-redaction only to the *rejected*
"minimum acceptable alternative" and implied the prototype avoided it; the prototype, applied verbatim,
does not.

**Recommendation:** add rule-table rows (kind `residual`, or a new `over_redaction` kind) for
`Authorization: Bearer\ndoc=17` and one CRLF/obs-fold variant, and state in `oracle.md` C2.2 that the
branch is fail-closed in both directions.

### F-REV-R2-03 — **LOW: a false measured claim about the base tree, repeated in three records**

`oracle.md:272` — "On the pre-fix base tree **all three FAIL**"; `fix_record.md:86` — "All three FAIL on
the base tree, on M4, and pass on the fixed tree"; `after/r2_summary.json → oracle.narrow_must_failed_base`
— lists `N5c` **and `N5e`** as failing on base.

Measured by me on `iso/product_base` (`harness/run_i14d_oracle.py`):

```
narrow_must_failed = N1-mine, N1-reviewer, N2-middle-line, N3-newline-then-key,
                     N5-auth-multiline, N5c-auth-scheme-lf-secret, N13-partial-multiword-residual
N5d-auth-scheme-obsfold      pass=True   (base -> "Authorization: <redacted>"  == expected)
N5e-auth-token-key-lf-secret pass=True   (base -> "authorization: <redacted>"  == expected)
```

Only **N5c** fails on base, and it fails in the *over-redaction* direction, not the leak direction;
N5d/N5e pass there because the greedy swallow happens to produce the expected string. All three fail
**only on M4**, which is the arm that matters and where the claim is true. `r2_summary.json` is also
internally inconsistent with the other two (it omits N5d but adds N5e). The attempt's **own new suite
corroborates my measurement**: run against `product_base` it fails 11 rows, and `N5d`/`N5e` are *not*
among them, while against M4 its 4 failures are exactly `N5c`, `N5d`, `N5e` and the auth real-exit test
(§5). So the sentence is contradicted by the attempt's own machine output, not only by my re-run. This is
a hand-assembled prediction contradicting the machine record — the same failure mode as the `112`
hand-typed number the r5 suite was rewritten to avoid. Low impact on the verdict; worth fixing because it
is exactly the class of error this card exists to eliminate.

### F-REV-R2-04 — **INFO: `binding.json`'s M3 description is imprecise**

`binding.json → isolation_rule.product_code_copies` describes M3 as "the auth value reduced to a strict
single token (**scheme branch left defined but unreferenced**)". In the tree, `_AUTH_SCHEME_SPLIT` is
**still referenced** in the value group; M3's one-line edit is `_AUTH_BARE_VALUE` → `_BARE_VALUE`. The
described intent (a naive single-token narrowing) is what the tree does — M3 leaks 4 auth rule rows and
both same-line controls — so only the parenthetical is wrong.

### Carried from r1 (recorded, not fixed — as instructed)

F-REV-D-02 (dead `_VALUE`; promotion hazard), F-REV-D-03 (digit-suffixed key gap), F-REV-D-04
(value-less header — family now **widened**, see F-REV-R2-02), F-REV-D-06 (residual key naming — fixed as
a reporting change), F-REV-D-07 (external `revenue-forecast` HEAD drift; the attempt leaves the r1
binding value in place and discloses the drift, which is the right call). Note the F-REV-D-02 promotion
hazard is now sharper: a promoter who "tidies" `_VALUE` gains nothing, and the branch that
F-REV-R2-01 exploits is chosen by **alternation order**, not by anything that recognizes a scheme.

---

## 4. RULING 1 TRANSCRIPTION CHECK (per the parent's ruling — verification only)

The parent ruled the rewrite stands. I therefore checked **transcription fidelity only**, against the
predecessor's exact text at `reviewer_report.md:406–444`.

| predecessor's requirement | r2 file | verdict |
|---|---|---|
| rename to `test_f08_c13_multiline_diagnostics_survive` | line 311 | **exact** |
| `tail = " doc=17\nstage=summarize code=llm_global_failure request_id=req-1"` | line 326 | **exact** |
| `review_marker = "ZQ7_REVIEWER_MARKER_9f3c"` | line 325 | **exact** |
| `for marker in (MARKER, review_marker):` | line 327 | **exact** |
| `assert out == "upload failed for token=<redacted>" + tail` | line 330 | **exact** |
| loop inverted: `for kept in ("doc=17", "stage=summarize", "code=llm_global_failure", "request_id=req-1"): assert kept in out` | lines 334–336 | **exact** |
| `assert len(out) > 90, "the multi-line diagnostics must survive"` | line 332 | **exact** |
| `len(out) == 34` → `== 98` | line 331 | **exact** |
| `assert marker not in out, …` | line 333 | **exact** |
| `assert len("upload failed for token=" + review_marker + tail) == 112` | line 338 | **exact** |
| `assert len("upload failed for token=" + MARKER + tail) == 109` | line 339 | **exact** |
| `assert len(out) < 200, "well below the 200-char limit, so this is not truncation"` | line 331 | **folded, not literal** |
| `FIDELITY_CASES`: `("a=1 token="+MARKER+" b=2", "a=1 token=<redacted> b=2")` | line 256 | **exact** |
| `FIDELITY_CASES`: multiline row → keeps ` doc=17\nstage=…request_id=req-1` | lines 260–263 | **exact** |
| `FIDELITY_CASES`: `("token="+MARKER+"\nnext=1", "token=<redacted>\nnext=1")` | line 267 | **exact** |
| **no change** to `("failed for token=" + MARKER + "; see log\nstage=…")` | lines 265–266 | **unchanged** |
| four new auth rows (LF, CRLF, obs-fold, `authorization: token\n`) | lines 274–277 | **exact** |
| the two stale comments rewritten | lines 235–238, 254–255, 258–259, 270–273 | **done** |

**The one deviation:** the predecessor wrote the `< 200` guard as a **separate assertion**;
the r2 file folds it into the message of `assert len(out) == 98, "well below the 200-char limit, so this
is not truncation"`. The predicate `len(out) < 200` is still **entailed** (line 330 pins
`out == expected + tail` and line 331 pins the length at 98), so no protection was lost — but the
transcription is not literally verbatim, and the assertion message now sits on an assertion that does not
test it. I record this as a transcription nit, not a defect; the parent's ruling that the rewrite stands
is unaffected and I do not re-litigate it.

Every other requirement is transcribed character-for-character, and no expectation in the file was
authored by the implementer.

---

## 5. COUNTS, SUITES, AND THE BYTE-PIN

**Counts** (`r5/counts.json` == `after/counts.json`, sha256 `53dd855318ea16aa7655…`, 486 B):

| quantity | r1 | r2 claimed | my verification |
|---|---|---|---|
| rule table rows | 48 | **55** | 55 by my own rule-table run; 42 credential + 9 untouched + 4 residual = 55 ✅ |
| oracle cases | 17 | **20** | 20 (9 `narrow_must` + 11 `keep_must`) ✅ |
| `FIDELITY_CASES` pairs | 28 | **32** | **32, counted by hand from the table source** ✅ (32 exact nodeids too) |
| total nodeids | 103 | **111** | see the suite table below |

**Suites** (iso venv, Python 3.13.9, pytest 9.1.1, `--basetemp` in my own scratch):

| suite / tree | result | rc |
|---|---|---|
| copied `test_i14c_real_exit_redaction.py` on **r2** | **86 passed, 0 failed** (529.85 s) | **0** |
| new `test_i14d_single_token.py` on **r2** | **25 passed** (327.49 s) | **0** |
| new `test_i14d_single_token.py` on `product_base` | **11 failed, 14 passed** (274.77 s) | 1 |
| new `test_i14d_single_token.py` on **M4** | **4 failed, 21 passed** (336.99 s) | 1 |
| oracle on r2 / base / M4 / M1 / M2 / M3 | 0 / 3 / 3 / 3 / 3 / 3 | as claimed |
| rule table on r2 / base / M4 / M1 / M2 / M3 | 0 / 3 / 3 / 3 / 3 / 3 | as claimed |

Every one of the four suite numbers matches the claim exactly. The two RED signatures are also exactly
right, and they independently corroborate **F-REV-R2-03**: on `product_base` the 11 failures are the
7 `narrow_must` rows (`N1-mine`, `N1-reviewer`, `N2`, `N3`, `N5`, **`N5c`**, `N13`) plus the four
E4b/C13/auth-real-exit rows — **`N5d` and `N5e` are absent from that list because they PASS on base**
while failing on M4; and M4's 4 failures are precisely `N5c`, `N5d`, `N5e` and
`test_i14d_auth_scheme_newline_real_exit_…`, the last with
`AssertionError: the wrapped credential was persisted in plaintext`. So the "all three FAIL on the base
tree" sentence in `oracle.md`/`fix_record.md` is contradicted by the suite as well as by the oracle.

Base-tree signatures reproduce the documented RED states: the rule table's base failures are
`cred-line-middle-single-token`, `cred-multiline-swallow`, `cred-multiline-then-key`,
`cred-auth-multiline-swallow`, `cred-auth-split-keeps-diagnostics`,
`res-partial-multiword-secret`; M4's are exactly the seven `cred-auth-split-*` rows with
`credential_secret_leaks = ["cred-auth-split-bearer-real-secret"]`; M1's are the four
assignment-path rows; M2's is `cred-auth-multiline-swallow` alone; M3's are the four auth rows with
`credential_secret_leaks []`.

**Recovery evidence is real.** Independently hashed: `scratch/pre-r2-narrow/src/…/observability.py` =
`e8abd522…` (40476 B) — the pre-r2 state restorable on demand — and `scratch/apply-check/…` =
`2aa5ed1a…` (41432 B) — the deliverable reproduced by the op script; `recovery/recovery-tree{,-r2}/…` =
`c5608c4b…` (40060 B) — the base tree, consistent with `round_trips.recovery_byte_identical`.

**Byte-pin:** `after/final_hashes.json` (74 entries, up from r1's 46) — I recomputed **every**
sha256 and byte count against the attempt dir: **74/74 reproduce, 0 missing, 0 mismatched.**

**Other artifacts:** `reviewer_report.md` `499d91ac…`/37659 B ✅; `changes.diff` `4c0160b8…`/5101 B ✅;
`changes_r2_authsplit.diff` `40a146d4…`/1786 B ✅; copied suite now `eb3fc44e…`/26425 B (correctly no
longer `672b88de…`); `harness/tests/conftest.py` `783b1774…`/275 B (untouched) ✅.

**Real CLI (E5a/E5b/E5c), which r1 left unverified — I ran it and it reproduces:**

```
E5a (credential-shaped config name): rc 1, marker hits stdout 0 / stderr 0,
     bare_traceback false, structured_envelope true, catalogs_created []      ✅ as recorded
E5b (bare-marker config name)      : rc 1, marker hits stdout 0 / stderr 1,
     bare_traceback false, structured_envelope true, catalogs_created []      ✅ the 1 hit is the
                                                                                declared residual
E5c (argparse failure)             : rc 2, bare_traceback false, no envelope, no catalogs
```

---

## 6. UNVERIFIED LIST

1. **The copied suite was run on the deliverable only** (86 passed / 0 failed). I did not run it against
   base or the four mutants: the decisive claim concerns the deliverable, each mutant's detection
   behaviour is covered by the oracle, the rule table, the new suite and my own e2e driver (all run
   across all six trees), and a six-tree sweep of that file costs ~9 minutes per tree. The new suite's
   rows for the rewritten `FIDELITY_CASES` are the same expectations as the copied suite's, so mutant
   detection is not left unchecked — only unreplicated in the second file.
2. **The new suite was run on r2 (`25 passed`), `product_base` (`11 failed / 14 passed`) and M4
   (`4 failed / 21 passed`), but not on M1/M2/M3.** Their rows are nevertheless covered: the oracle was
   run on all six trees and M1/M2/M3 pass `N5c`/`N5d`/`N5e` there, and my own end-to-end driver shows
   the wrapped credential absent from the persisted event on all three. So the "only M4 detects it"
   claim is verified by my instruments for M1–M3 and by the file itself for M4.
3. **`residuals_confirmed` → `residuals_with_marker_surviving`** (F-REV-D-06) is a reporting rename; I
   verified both emitted lists but not that every downstream consumer was updated.
4. **`harness/run_mutations_i14d.py`** as an orchestrator was not re-run end-to-end; I re-ran its
   constituent measurements (oracle, rule table, probe) individually on all four mutants and compared
   them to `mutations/mutation_matrix.json`, which agrees.
5. **Venv provenance** (unchanged from r1): the interpreter works and reports Python 3.13.9 / pytest
   9.1.1; I did not diff it against I-00-A's or I-14-C's.
6. **Outputs, not claims:** `after/cli/**`, `after/cli-r2/**`, `after/runs-narrow-r2/**`,
   `mutations/runs-*/**` were not byte-audited beyond their `final_hashes.json` entries (which
   reproduce); the five kept failed attempts in `commands.json` were not replayed.
7. **Performance / ReDoS linearity** and the F07 deadline assertion were not re-timed.
8. **F-REV-D-03's atom-table gap** (`token2=`, `secret2=`) was not re-measured by me this round; it is
   carried as recorded.
9. **The remedy for F-REV-R2-01 is a recommendation, not a measurement.** I did not build or measure the
   generic-scheme-token variant; the "one line" claim is a reading of the current branch's structure.

---

## 7. ADJUDICATION

**Does r2 close F-REV-D-01 completely? No — it closes the measured family and leaves the class open.**

* **Closed, and verified by me at the real exit:** the predecessor's `D1–D7` family, all nine enumerated
  scheme words, CRLF, obs-fold, the no-space and embedded forms, `proxy-authorization`, and the
  `Bearer\n<secret>\ndoc=17` exit state `"Authorization: <redacted>\ndoc=17"` (32 chars), with the
  secret absent from every produced file. Helper probe 12/12 closed, `fidelity_drift []`, oracle 20/20
  rc 0, rule table 55 rows rc 0 with both leak lists empty, copied suite 86/0, new suite 25/0.
* **Open (F-REV-R2-01, BLOCKER-class):** any `Authorization:` scheme word outside the nine —
  `Negotiate`, `AWS4-HMAC-SHA256`, `SCRAM-SHA-256`, `Hawk`, `Bot`, `Mutual`, `vapid`, `HOBA`, or an
  arbitrary word — followed by one line break still leaves the credential, **including the card's own
  marker**, in the append-only event log, where the card's starting tree redacted it. Two adjacent
  shapes (a two-token value then a wrap; a blank line between) behave the same way; a quoted
  continuation leaked on base too.
* **Root cause of the gap:** the remedy was implemented as an **enumeration** of scheme words, so the
  fix's coverage is exactly as wide as the list. RULING 2 asked for something that "cannot leave a token
  after a scheme word unredacted"; the applied branch can. The predecessor's snippet was too narrow, and
  the honest re-review result is that the snippet needs generalizing — not that the clause is satisfied.
* **Why not `accepted_scoped`:** the residual persists *the card's own marker*, end-to-end, in a
  permanent log; the card's starting tree did not; no record discloses it; and no oracle or rule-table
  row registers it, so the strengthened exit criterion is blind to it in precisely the way C2.1 says the
  original criterion was blind to `scheme␊secret`. Accepting it would let a promoter ship a redactor that
  writes live credentials to the event log while the record certifies `credential_leaks == []`. If the
  owner prefers to accept the narrower scope deliberately, that is a legitimate owner decision — but it
  should be recorded as an **open, measured, registered** sub-case (with rows), not left as an
  undocumented consequence of a word list.

**Verdict: `changes_required`** — one BLOCKER-class residual (F-REV-R2-01), two non-blocking findings
(F-REV-R2-02, F-REV-R2-03), one informational (F-REV-R2-04). Nothing in this verdict touches the
RULING-1 rewrite, which I verified as a faithful transcription and did not re-litigate.

**Cheapest path to green:** (1) generalize the pre-break token in `_AUTH_SCHEME_SPLIT` from the nine-word
alternation to an RFC-7235 scheme token (and try `_QUOTED_VALUE` after the break) so C1–C12 close;
(2) add oracle + rule-table rows for a **non-enumerated** scheme carrying both the marker and a 39-char
non-marker credential, and for the over-redaction family of F-REV-R2-02; (3) correct the three "all three
FAIL on the base tree" statements; (4) re-run the probe, oracle, rule table, both suites and the M4 arm;
(5) re-run `report_i14d_counts.py` and regenerate `r5/counts.json` if rows are added.

**What this review does grant:** a byte-pinned demonstration that the RULING-2 fix closes the measured
F-REV-D-01 family and satisfies both halves of the exit clause on it, at the real exit; that the fix is
exactly invertible and exactly reproducible; that M4 is the pre-r2 tree by construction and is the only
arm of the four that detects the class; that the RULING-1 rewrite is the predecessor's text; that the
counts, the diffs, the suites and the 74-entry byte-pin all reproduce; and that production is provably
untouched. **What it does not grant:** acceptance, `disclosure_adaptation` (unmapped), accuracy
(unproven), promotion, or the soundness of `credential_leaks == []` as evidence for the *class*.

---

## 8. HOW TO REPRODUCE THIS REVIEW

Scratch root: `%TEMP%\i14d_review_r2\`. Interpreter:
`<ATT>\iso\venv\Scripts\python.exe` (Python 3.13.9, pytest 9.1.1). Every run used
`-B` + `PYTHONDONTWRITEBYTECODE=1`, with `--basetemp` and `I14C_RUN_ROOT` pointing into the scratch root,
so nothing was written into the attempt or into `iso/`.

Reviewer's own instruments (written from scratch, **not** derived from the attempt's harness):

```powershell
$A = "<attempt dir>"; $S = "$env:TEMP\i14d_review_r2"; $PY = "$A\iso\venv\Scripts\python.exe"

# 49-case differential leak/fidelity probe (carries the r1 report's D1-D9 predictions verbatim)
& $PY -B "$S\rev_probe.py"  --src "$A\iso\product_mut_authsplit\src" --label M4     --out "$S\m4.json"
& $PY -B "$S\rev_probe.py"  --src "$A\iso\product_narrow\src"        --label r2     --out "$S\r2.json"
& $PY -B "$S\rev_probe.py"  --src "$A\iso\product_base\src"          --label base   --out "$S\base.json"
# adjacent shapes (over-redaction + F-REV-D-04) and the E4b re-derivation
& $PY -B "$S\rev_probe2.py" --src "<tree>\src" --label <l> --out "<out>.json"

# own end-to-end driver: real worker exit + CLI handler, arbitrary message via --message-file
$env:I14C_RUN_ROOT = "$S\e2e"
& $PY -B "$S\rev_e2e.py" --message-file <msg.txt> --run-dir <fresh dir> `
      --src "$A\iso\<tree>\src" --tests-dir "$env:USERPROFILE\Projects\company-wiki\tests\contract" `
      --secret <secret> --cli-exit        # prints RESULT {...persisted_message_redacted...}

# attempt's own instruments, re-run by me (outputs into the scratch root, never the attempt)
& $PY -B "$A\harness\authsplit_probe.py"     --src "<tree>\src" --label <l> --out <json>
& $PY -B "$A\harness\run_i14d_oracle.py"     --src "<tree>\src" --label <l> --out <json>
& $PY -B "$A\harness\run_rule_table_i14d.py" --src "<tree>\src" --label <l> --out <json>
& $PY -B "$A\harness\run_real_cli_exit.py"   --shape E5a|E5b|E5c --run-dir <fresh> --src "<tree>\src" --python $PY
$env:I14C_PRODUCT_SRC = "$A\iso\product_narrow\src"
& $PY -X utf8 -B -m pytest "$A\harness\tests\test_i14c_real_exit_redaction.py" -q --tb=no -rf `
      -p no:cacheprovider --basetemp "$S\pt_narrow"
& $PY -X utf8 -B -m pytest "$A\harness\tests\test_i14d_single_token.py" -q --tb=no -rf `
      -p no:cacheprovider --basetemp "$S\nt_narrow"

# fix invertibility, on COPIES (never on the deliverable)
& $PY -B "$A\harness\apply_i14d_narrow.py" --op reverse_authsplit --tree "<copy of r2 tree>"
& $PY -B "$A\harness\apply_i14d_narrow.py" --op authsplit        --tree "<copy of pre-r2 tree>"
```

Round-trip: copy `iso/product_base/src` into a scratch `git init` repo with `core.autocrlf=false`,
then `git apply --check -p1` / `git apply -p1` / `git apply -R -p1` with `changes.diff`, comparing all
152 files against `iso/product_narrow/src` (0 mismatches) and the reverse against `product_base`.

The byte-pin of this file (sha256 of its raw bytes) is reported by the carrier in the handoff message,
not inside the file, so that the pin covers content that cannot change after hashing.
