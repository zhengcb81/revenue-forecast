# I-14-D-R2 oracle — FROZEN before the fix (fix round of `I-14-D/a20260919-01`)

Attempt: `execution_runs/I-14-D-R2/a20260926-01`
Card: `execution_v2/card_I-14-D.md` (C13 narrowing; exit = 裸值不再跨行吞掉后续诊断键 + E4b 新基线经独立复算)
Round opened by: orchestrator dispatch `I-14-D-R2` (修复轮), on the independent re-review
`I-14-D/a20260919-01/reviewer_report.md` **L18 `CHANGES_REQUIRED`** + **L25-L30**.
Owner authorization: `OWNER_DECISIONS.md §三十七` (L852-L871, 全沙箱常设授权; 边界: 前像留痕 +
写后验证 + fail-closed 回滚; `git add/commit/push` 不在授权内).

**This file is frozen before any edit is made to any tree owned by this round.** Every expected
value below was derived by hand from the pattern semantics (§3.1) and cross-checked against the
reviewer's own measured columns (reviewer_report.md L233-L243 base column, and L475-L483 the
reviewer's measured RULING-2 prototype). Nothing here was produced by calling the function under
test on a post-fix tree, because no post-fix tree existed when this file was frozen.

---

## 0. Scope, inputs, and what this round may touch

| item | value |
|---|---|
| write surface | `execution_runs/I-14-D-R2/a20260926-01/**` only (inside `.planning`) |
| product repo (`company-wiki`, `dayu-agent`) | **read-only — zero writes; a required product write = stop and report `blocked`** |
| old attempt `execution_runs/I-14-D/a20260919-01/**` | **read-only** (封盘) — copied FROM, never written to |
| five plan files / `.planning` outside this attempt | not written |
| git | no `add`/`commit`/`push`, **no `git status`**; only read-only `git diff HEAD --name-only` at handoff time |
| network | none |

**Pre-image (the defective tree this round fixes)** — copied from the read-only old attempt:

| field | value |
|---|---|
| source | `execution_runs/I-14-D/a20260919-01/iso/product_mut_authsplit/src` |
| target | `execution_runs/I-14-D-R2/a20260926-01/iso/product_pre/src` |
| `company_wiki/source_catalog/observability.py` sha256 | `e8abd522b2072add062be225d7ec1ca10621ffa5be7841f99ef9fb339015cbd0` |
| bytes | 40476 |
| line endings | CRLF preserved |
| why this tree | it is **byte-identical** to the `iso/product_narrow` tree the reviewer measured:
`reviewer_report.md` L56 (`product_narrow (deliverable) | e8abd522… | 40476 | yes`). That is the
tree in which the review found the credential-persistence regression, i.e. the r1 narrowing as
delivered. |

Disclosed: the read-only old attempt has since grown later revisions (its current
`iso/product_narrow` = `2aa5ed1a…/41432` already carries an auth-path branch, and
`iso/product_narrow_r3..r6` exist). **This round deliberately starts from the exact bytes the
dispatched review measured**, so the red arm reproduces the dispatched defect rather than a later,
already-worked-on state. Nothing in the old attempt is modified by this choice.

---

## 1. The defect, verbatim (复审逐字)

`execution_runs/I-14-D/a20260919-01/reviewer_report.md` (583 lines, sha256 recorded in
`handoff.json.input_hashes`) —

**L18 (verdict):**
> `**CHANGES_REQUIRED — the attempt is NOT accepted.**`

**L25-L30 (the defect):**
> ```
> However the review found a **credential-persistence regression on the authorization path that the
> frozen oracle, the rule table and all three mutations fail to exercise**:
>
>     "Authorization: Bearer\n<SECRET>\ndoc=17" — on the pre-fix tree the persisted event is
>     "Authorization: <redacted>" (secret gone); on iso/product_narrow the persisted event is
>     "Authorization: <redacted>\n<SECRET>\ndoc=17" — the full credential is written to the
>     append-only event log in plaintext.
> ```

Supporting verbatim, same file: L33-L34 (confirmed helper-level **and end-to-end** through
`SourceCatalogWorker.run_forever` → `worker.py:1066 message_redacted=redact_and_truncate(message)`),
L35-L37 (violates the card's own negative clause; `credential_leaks == []` is **not sound** for the
auth path), L228-L243 (the D1-D9 measurement table, reproduced as cases `P1..P10` in §3),
L263-L268 (root cause: `_AUTH_BARE_VALUE`'s join is `[ \t]+`, and `\n ∉ [ \t]`, so only the scheme
word is consumed and the secret's line carries no `key=` prefix for the assignment scanner),
L270-L281 (why the frozen oracle, the rule table and M1..M3 all missed it).

**Fix criterion from the review itself (L283-L286):**
> `Required remediation. Either the scheme-aware fail-closed value (Ruling 2 / §5), or an equivalent
> that cannot leave a token after a scheme word unredacted, plus rule-table and FIDELITY_CASES rows
> for Authorization: Bearer\n<marker> (LF, CRLF, obs-fold, and authorization: token\n). Re-run the
> oracle, rule table, both suites and the mutation plan afterwards.`

and **RULING 2 (L464-L483)**, whose measured prototype gives the target persisted value
(L479): `end-to-end: Authorization: Bearer\n<SECRET>\ndoc=17 persists as "Authorization:
<redacted>\ndoc=17" — secret gone AND diagnostics kept`.

---

## 2. GATE 0 — 自探留档 (run before this oracle was frozen, disclosed)

### 2.1 write / readback / delete probe (zero privilege, this attempt's own directory)

Raw output, verbatim, also saved at `evidence/gate0_raw.txt`:

```
=== GATE0 BEGIN (I-14-D-R2/a20260926-01) ===
cwd=C:\Users\郑曾波\Projects\revenue-forecast
--- step1 write ---
write_ok=True
--- step2 readback ---
gate0 probe I-14-D-R2 a20260926-01 write-readback-delete
--- step3 delete ---
deleted_gone=True
=== GATE0 END ===
```

`gate0_passed = true`: the three steps (write → readback → delete) all behaved; the probe file is
gone; no privilege beyond workspace-write was used or needed.

### 2.2 defect self-probe (read-only, against the pre-image and the read-only old trees)

`harness/probe_dfamily.py --src <tree>/src` exercises the review's own D1-D9 table plus the
dispatched core case. Raw JSON is kept in `evidence/`.

| tree | result |
|---|---|
| `I-14-D/a20260919-01/iso/product_base` (pre-narrowing) | `Authorization: <redacted>` — secret gone, diagnostics lost (review L235-L241 base column) |
| `I-14-D/…/iso/product_mut_authsplit` = **this round's pre-image** `e8abd522…` | **DEFECT PRESENT** — `D1..D7` + core all leak; rc 3 |
| `I-14-D/…/iso/product_narrow` (later revision `2aa5ed1a…`, read-only) | no leak in this family — see the disclosure in §0 |

This is the only information taken from running the code before freeze: **which tree carries the
defect** (already stated by the review) and the fact that the D-table reproduces. No expected value
in §3 was taken from these runs — every one is hand-derived in §3.1 and matches an already-published
reviewer column.

---

## 3. NEW criteria — the authorization path (added by this round; §4 is untouched)

Symbol: `R = "<redacted>"`, `M = "SYNTHETIC_AUDIT_TOKEN"` (21 chars),
`S = "ghp_ZQ7ReviewerFakeCredential0123456789"` (39 chars, the reviewer's synthetic credential).

### 3.1 Hand derivation (frozen before the fix)

The fix adds one alternative to the *value* group of `_AUTH_PATTERN` (key group unchanged):

```python
_AUTH_SCHEME_SPLIT = (r"(?:bearer|token|basic|digest|oauth|jwt|apikey|api_key|sso)"
                      r"[ \t]*\r?\n[ \t]*[^\s,;&\"'|]+")
# value group order: _QUOTED_VALUE | _AUTH_SCHEME_SPLIT | _AUTH_BARE_VALUE
```

and `redact_text` substitutes `m.group("key") + REDACT` for the whole match
(`observability.py` L315), then runs the assignment scanner. Consequences, by hand:

* after a **known scheme word**, exactly **one** line break (LF or CRLF) plus optional indentation
  is consumed *inside* the match together with the **first following token** — that token is the
  credential and it is redacted;
* the line break **after** that token stays **outside** the match, so `doc=17` / `request_id=…`
  survive — the C13 half of the card's exit clause;
* the key group already swallowed `Authorization:` + following inline whitespace, so nothing
  changes for the same-line forms (P9/P10);
* when no line break follows the scheme word, the alternative cannot match and the pre-existing
  `_AUTH_BARE_VALUE` (inline run) is used — identical to the pre-image.

### 3.2 The cases (hand-computed `out` / `len`)

| id | kind | input | expected `redact_text` | `len` |
|---|---|---|---|---|
| P1-bearer-lf-secret-doc17 | auth_must | `Authorization: Bearer\nM\ndoc=17` | `Authorization: <redacted>\ndoc=17` | 32 |
| P2-s39-lf-secret-doc17 | auth_must | `Authorization: Bearer\nS\ndoc=17` | `Authorization: <redacted>\ndoc=17` | 32 |
| P3-bearer-space-lf | auth_must | `Authorization: Bearer \nS` | `Authorization: <redacted>` | 25 |
| P4-nospace-colon | auth_must | `Authorization:Bearer\nS` | `Authorization:<redacted>` | 24 |
| P5-lowercase-token-key | auth_must | `authorization: token\nS` | `authorization: <redacted>` | 25 |
| P6-crlf | auth_must | `Authorization: Bearer\r\nS` | `Authorization: <redacted>` | 25 |
| P7-obsfold | auth_must | `Authorization: Bearer\n  S` | `Authorization: <redacted>` | 25 |
| P8-midline | auth_must | `stage=summarize Authorization: Bearer\nS\nrequest_id=req-1` | `stage=summarize Authorization: <redacted>\nrequest_id=req-1` | 58 |
| P9-tab-sep | auth_keep | `Authorization: Bearer\tS` | `Authorization: <redacted>` | 25 |
| P10-sameline | auth_keep | `Authorization: Bearer S` | `Authorization: <redacted>` | 25 |

`M` in the table is the literal marker string `SYNTHETIC_AUDIT_TOKEN`, `S` the literal credential
(not the single letters). Length checks: `P1` = 15 (`Authorization: `) + 10 + 7 (`\ndoc=17`) = **32**;
`P8` = 16 (`stage=summarize `) + 15 + 10 + 17 (`\nrequest_id=req-1`) = **58**; `P4` = 14 + 10 = **24**;
the 25-length rows are 15 (`authorization: `/`Authorization: `) + 10 or 14 + 10 for `P4`.

**P11-persisted-event (the "落盘" criterion):** for input `P1` and `P2`, the value that
`worker.py:1066` assigns — `message_redacted = redact_and_truncate(message)` — must be
**written to the append-only event log with no secret in it**:

* `redact_and_truncate(P1.in)` contains `"<redacted>"` and `"doc=17"`;
* it contains neither `SYNTHETIC_AUDIT_TOKEN` nor `ghp_ZQ7…789`;
* `len(...) <= 200` (the truncation limit), and the event JSON round-trips from disk with the same
  three properties.

**Universal auth guard (applies to every `auth_must` row):** `secret_absent` = the 39-char
credential and the marker must not appear anywhere in the output. A leak in any row = RED.

---

## 4. INHERITED criteria — unchanged (既有判据, 一字不改; this round only ADDS §3)

Transcribed from the r1-frozen oracle of `I-14-D/a20260919-01` (`oracle.md` §2, the 17 cases the
review re-derived independently in reviewer_report.md §2 and L117: "Oracle: 17 cases,
`narrow_must_failed []`, `keep_must_failed []`, `verdict pass`, rc 0"). Provenance of every number
is that review; this round neither edits nor re-derives them.

### A0 — E4b truncation baseline (N4, real-exit number, pure-function form)

`S4 = "start-" + "x"*170 + " token=" + M + " " + "y"*120`, `len(S4) = 6+170+7+21+1+120 = 325`
* `redact_text(S4)` length **314**
* `redact_and_truncate(S4)` length **200**, and its tail after byte 193 is `" yyyyyy"` (space + 6 y)
* neither `M` nor `M[:8]` appears in the truncated output

### A1..A17 — the frozen case table

| # | id | kind | input | expected | `len` |
|---|---|---|---|---|---|
| 1 | N1-mine | narrow_must | `upload failed for token=` + M + ` doc=17\nstage=summarize code=llm_global_failure request_id=req-1` | `upload failed for token=<redacted>` + same tail | 98 |
| 2 | N1-reviewer | narrow_must | same with `ZQ7_REVIEWER_MARKER_9f3c` | `upload failed for token=<redacted>` + same tail | 98 |
| 3 | N2-middle-line | narrow_must | `a=1 token=` + M + ` b=2` | `a=1 token=<redacted> b=2` | 24 |
| 4 | N3-newline-then-key | narrow_must | `token=` + M + `\nnext=1` | `token=<redacted>\nnext=1` | 23 |
| 5 | N5-auth-multiline | narrow_must | `Authorization: Bearer ` + M + `\ndoc=17\nstage=summarize` | `Authorization: <redacted>\ndoc=17\nstage=summarize` | 48 |
| 6 | N13-partial-multiword-residual | narrow_must | `password: iron steel` | `password: <redacted> steel` (declared residual) | 26 |
| 7 | N5b-auth-sameline-kept | keep_must | `Authorization: Bearer ` + M + ` rejected by provider` | `Authorization: <redacted>` | 25 |
| 8 | N6-quoted | keep_must | `password: '` + M + `'` | `password: <redacted>` | 20 |
| 9 | N7a-untouched-monkey | keep_must | `monkey=banana doc=1\nstage=x` | unchanged | — |
| 10 | N7b-untouched-diagnostics | keep_must | `stage=summarize code=llm_global_failure request_id=req-SYNTH-0001` | unchanged | — |
| 11 | N7c-untouched-url | keep_must | `url=https://example/x?page=2` | unchanged | — |
| 12 | N8-residual-digest | keep_must | `upload failed for digest=` + M | unchanged | — |
| 13 | N9-residual-flag | keep_must | `--api-key ` + M | unchanged | — |
| 14 | N10-semicolon-bounded | keep_must | `a=1 token=` + M + `; b=2` | `a=1 token=<redacted>; b=2` | — |
| 15 | N11-ampersand-bounded | keep_must | `GET /x?token=` + M + `&page=2` | `GET /x?token=<redacted>&page=2` | — |
| 16 | N12-no-tail-event | keep_must | `upload failed for token=` + M | `upload failed for token=<redacted>` | 34 |
| 17 | N13b-quoted-multiword-full | keep_must | `password: '` + M + `'` | `password: <redacted>` | — |

(Cases 6 and 17 are the two sides of the same rule: bare multi-word = partial (declared), quoted =
full. Case 6 must keep producing exactly `password: <redacted> steel`.)

**Not in this round's criteria (registered as out-of-scope, not silently green):** the later-revision
rows `N5f..N5k` / `R3a` / `R3b` of the old attempt's evolved oracle (generic scheme words
(`Negotiate`, `AWS4-HMAC-SHA256`, `Zzz`), blank-line runs, quoted continuation, two-token-then-wrap).
The dispatched defect (§1) is the `Bearer`/`token` family measured in the review's D1-D9 table, and
RULING 2's required remediation is exactly that family. This round does not claim those rows.

---

## 5. RED → GREEN definition

| arm | tree | required result |
|---|---|---|
| **RED (原缺陷复现)** | `iso/product_pre` (`e8abd522…`) | §4 (A0-A17) **all green**; §3 **red** — `P1..P8` leak the credential, `P11` persists it; rc **3** |
| **GREEN** | `iso/product_post` (pre + §6 fix) | §4 **and** §3 all green; rc **0** |
| mutations | `_mut/M1..M4` | each rc **3**, failing the specific row(s) named in §7 |

Exit codes (harness convention, inherited): `0` = all criteria pass, `2` = cannot adjudicate
(import failed), `3` = at least one criterion failed.

---

## 6. The fix (frozen description; the code is written only after this file)

One site, `company_wiki/source_catalog/observability.py`, immediately after `_AUTH_BARE_VALUE`:
add `_AUTH_SCHEME_SPLIT` (§3.1) and insert it into `_AUTH_PATTERN`'s value group **between**
`_QUOTED_VALUE` and `_AUTH_BARE_VALUE`. No other line of the file changes; no other file changes.

Fail-closed properties the fix must have (from RULING 2):
1. a token following a known scheme word across **one** line break is redacted (secret gone);
2. the break *after* that token is outside the match (diagnostics kept);
3. same-line forms behave exactly as before (P9/P10, A7 unchanged);
4. redaction completes **before persistence** — `redact_and_truncate` is the only writer of
   `message_redacted`, so a redacted value is what reaches the append-only log.

---

## 7. Mutation plan (≥3, all covering the authorization path; each is a tree copy)

Every mutation is a **single-site** edit applied to a **copy** of `iso/product_post`; the post tree
itself is never mutated (its sha256 is recorded before and after the mutation runs and must not
move).

| id | single-site edit | must fail (predicted) | why it is a different hole |
|---|---|---|---|
| **M1** | **remove the `_AUTH_SCHEME_SPLIT` branch from `_AUTH_PATTERN`** → the auth path is left exactly as the pre-image while the C13/narrow half stays fixed ("只修 iso/narrow 不修授权路径") | `P1..P8` leak (`secret_absent=false`), `P11` persists the credential; §4 stays green | the defect as dispatched — proves §3 is what catches it, not §4 |
| **M2** | scheme-word list loses `bearer` and `token` → `(?:basic\|digest\|oauth\|jwt\|apikey\|api_key\|sso)` | `P1,P2,P3,P4,P5,P6,P7,P8` leak; `P11` persists | the *scheme recognition* half: a fix that is present but does not recognise the dispatched scheme words still leaks |
| **M3** | split's token becomes a **multi-line run** → `scheme(?:[ \t]*\r?\n[ \t]*[^\s,;&"'\|]+)+` | `P1`, `P2`, `P8` lose `doc=17` / `request_id=req-1` (exact + `contains` fail), `P11` loses `doc=17`; **no leak** | the *diagnostics* half: a fix that over-redacts fails the card's own positive clause, not the leak guard |
| **M4** | `\r?\n` → `\n` (CRLF no longer recognised) | `P6` leaks | the *encoding* half: LF-only recognition leaves the CRLF header form in the clear |

Expected rc: GREEN `0`; M1-M4 all `3`. A mutation that passes is a hole in this oracle — it must be
reported as a finding, never absorbed.

---

## 8. Exit criteria / boundaries (this round)

1. `iso/product_post` green on §4 + §3 (rc 0); `iso/product_pre` red on §3 only (rc 3).
2. M1-M4 all red (rc 3), each with the named failing row recorded.
3. `changes.diff` covers **only** `src/company_wiki/source_catalog/observability.py` and round-trips
   (apply → byte-identical to `iso/product_post`; reverse-apply → byte-identical to
   `iso/product_pre`), with pre-image sha256+bytes+copy recorded.
4. Fail-closed rollback: any mismatch between the recorded pre-image and the tree that is actually
   edited ⇒ abort before writing, restore from the recorded copy, report `blocked`.
5. Zero writes to the product repo, to the old attempt, to the five plan files; zero git writes;
   `git status` never run; no network; no release of any parameter; `implementer_signed=false`;
   `releases_nothing=true`; the independent reviewer is dispatched separately by the parent.

---

# APPENDIX (appended AFTER the red / green / mutation runs — §3 and §4 criteria are byte-unchanged)

**Append-only proof.** The frozen oracle is bytes 1-18054 of this file, sha256
`71cbff493122d1f0905fd0eb5b6bfed0b0d7d0128bcdf475748bf32750ab1383` (sidecar `oracle.sha256`).
The appendix adds no criterion, changes no expected value, and only records what the frozen
criteria produced. The final file hash is recomputed at handoff and recorded in `handoff.json`.

## A.1 Measured results (evidence files under `evidence/`)

| arm | tree | oracle rc | inherited §4 failed | auth §3 failed | persistence probe rc |
|---|---|---|---|---|---|
| RED | `iso/product_pre` `e8abd522…/40476` | **3** | `[]` | P1-P8 (8, all leak) | **3** (`SECRET_PERSISTED`) |
| GREEN | `iso/product_post` `8dab63d9…/41304` | **0** | `[]` | `[]` | **0** (`PERSISTED_CLEAN`) |
| M1 auth path unfixed | `_mut/M1_…` | **3** | `[]` | P1-P8 (leak) | **3** |
| M2 no `bearer`/`token` in scheme list | `_mut/M2_…` | **3** | `[]` | P1-P8 (leak) | **3** |
| M3 multi-line run after break | `_mut/M3_…` | **3** | `[]` | P1, P2, P8 (diagnostics swallowed) | **3** (loses `doc=17`) |
| M4 LF-only break | `_mut/M4_…` | **3** | `[]` | P6 (CRLF leaks) | 0 (the persist case is LF) |

D-family probe (reviewer's D1-D9 + the dispatched core), `evidence/dfamily_product_pre.json` vs
`dfamily_product_post.json`: **DEFECT_PRESENT (9 leak rows) → NO_LEAK (0 leak rows)**.
The persisted event went from
`"Authorization: <redacted>\nghp_ZQ7…789\ndoc=17"` to `"Authorization: <redacted>\ndoc=17"` —
secret gone, `doc=17` kept, i.e. both halves of RULING 2 (L479).

## A.2 Supplementary cross-check: the read-only old attempt's rule table

`I-14-D/a20260919-01/harness/run_rule_table_i14d.py` (that attempt's current, evolved 79-row table)
was run read-only against both trees (`evidence/ruletable_product_pre.json`,
`ruletable_product_post.json`):

* `product_pre`: **8 credential leaks** + 29 fidelity failures;
* `product_post`: **2 credential leaks**, and every `cred-auth-split-*` row of the dispatched
  family (bearer-lf / crlf / obsfold / nospace / token-scheme / real-secret / keeps-diagnostics)
  **passes**; the 8 `over-auth-*` non-generic rows also pass, i.e. this fix produces exactly the
  over-redaction those rows register.

This table is **not** a criterion of this round (it belongs to later revisions of the read-only
attempt); it is recorded as an independent cross-check and as the source of A.3/A.4.

## A.3 Declared cost of the fix (recorded, not hidden)

When a bare scheme word is followed by a line that carries **no** credential, the fail-closed rule
redacts that line's first token anyway: `Authorization: Bearer\ndoc=17` →
`Authorization: <redacted>` (and `Authorization: Bearer\nstage=summarize` →
`Authorization: <redacted>`). The review names this cost at L485-L488 and the old attempt
registers it as the `over-auth-*` rule-table rows. No criterion of §3/§4 exercises it, so this
round neither claims nor hides it; it is disclosed here and in `handoff.json.open_questions`.

## A.4 Out-of-scope residual (measured, not claimed)

Scheme words **outside** the review's nine-word enumeration (`Negotiate`, `AWS4-HMAC-SHA256`,
`SCRAM-SHA-256`, `Hawk`, `Bot`, `Zzz`, …) still leave the following token in the clear:
`Authorization: Negotiate\n<marker>` → `Authorization: <redacted>\n<marker>`. These are the 2
remaining rule-table leaks (plus 12 fidelity rows) on `product_post`; they belong to the old
attempt's later findings (`F-REV-R2-01`), **not** to the dispatched `F-REV-D-01` D1-D9 family,
which the review's own required remediation (L283-L286) enumerates as LF / CRLF / obs-fold /
`authorization: token\n`. Registered here as open, carried, unclaimed.

## A.5 Not run (unverified)

The read-only attempt's copied pytest suite (`harness/tests/test_i14c_real_exit_redaction.py`)
was executed against `iso/product_post` with `PYTHONDONTWRITEBYTECODE=1`, `-p no:cacheprovider`
and `PYTEST_DEBUG_TEMPROOT` pointed inside this attempt: **68 passed, 18 errors**, where every
error is `PermissionError/WinError 5` at `tmp_path` **setup** (pytest cannot create its numbered
temp directory in this sandbox; raw output `evidence/pytest_copied_suite_post.txt`). The result is
therefore **not used as evidence** and the suite is listed as unverified in `handoff.json`; the
inherited criteria are carried by §4 (A0-A17) and by A.2 instead. No write reached the read-only
attempt (0 files with an mtime inside this session's window).

## A.6 Leftovers in this attempt directory

`pytest-of-郑曾波/` — empty pytest numbered-dir root created by the run above; the OS denies
deletion from this session (`rmdir` rc 5). It holds no source, no evidence and no product bytes.
`_pytest/post3/` — same origin, also access-denied for deletion. Neither affects any claim.
