# I-14-D r2 — FIX RECORD (answer to reviewer BLOCKER F-REV-D-01)

Attempt: `execution_runs/I-14-D/a20260919-01`
Reviewer report (byte-pinned): `reviewer_report.md`, sha256
`499d91acf06a67e2f7dd06d4a5af6569b5b92a6e4b3b77adda57b739eaa03d2b`, 37659 bytes —
**recomputed by this attempt before reading; both match the carrier's pin.**
Verdict received: **`changes_required`** (1 BLOCKER + 5 findings + 3 rulings).
Status after this record: `review_pending` — this attempt does **not** self-accept.

The reviewer's instructions were explicit about what to fix and what only to record.
This file is the fix record; every claim below has a file under `after/`,
`before/` or `mutations/`, and every rc is the raw process exit code.

---

## 1. The BLOCKER, restated (why the r1 attempt was unsound)

`"Authorization: Bearer\n<SECRET>\ndoc=17"`:

| tree | persisted `message_redacted` |
|---|---|
| `iso/product_base` (pre-I-14-D) | `"Authorization: <redacted>"` — secret gone, diagnostics gone |
| `iso/product_narrow` **as reviewed (r1)** | `"Authorization: <redacted>\n<SECRET>\ndoc=17"` — **full credential persisted** |
| `iso/product_narrow` **now (r2)** | `"Authorization: <redacted>\ndoc=17"` — secret gone **and** diagnostics kept |

Root cause (the reviewer's, reproduced here): the first key alternative
`authorization\s*[:=]\s*` consumes `Authorization: `, then the line-bounded
`_AUTH_BARE_VALUE` matches only the scheme word `Bearer` (because `\n ∉ [ \t]`), and
the secret's line has no `key=` prefix, so the assignment scanner cannot see it
either. The r1 rule table, the frozen oracle, the copied suite's auth rows and all
three mutations were structurally blind to `scheme␊secret`.

Reproduced in this attempt before fixing (helper level, 12 rows):
`harness/authsplit_probe.py` → `before/authsplit_probe_base.json` and the
pre-fix run recorded in `handoff.json`; **10 of 12 rows leaked** the credential
(the two same-line controls did not), matching the reviewer's D1–D10 table exactly.

## 2. The fix (reviewer RULING 2, applied verbatim)

Added ahead of `_AUTH_BARE_VALUE` and placed first in the value alternation:

```python
_AUTH_SCHEME_SPLIT = (r"(?:bearer|token|basic|digest|oauth|jwt|apikey|api_key|sso)"
                      r"[ \t]*\r?\n[ \t]*[^\s,;&\"'|]+")
# value group: _QUOTED_VALUE | _AUTH_SCHEME_SPLIT | _AUTH_BARE_VALUE
```

Semantics: after a **known** scheme word and exactly one line break, the first token
is redacted (fail closed). The break and any indentation stay **outside** the match,
which is what keeps the following diagnostic keys alive.

* The fix is one localized hunk:
  `changes_r2_authsplit.diff` (1786 bytes, 1 hunk, 1 file, POSIX paths); the
  deliverable diff `changes.diff` is 5101 bytes / 2 hunks.
* `iso/product_narrow/src/company_wiki/source_catalog/observability.py`:
  `sha256 2aa5ed1a219084a67f040388072aa94d7432c63414b6692060f1b4d6b4e12bde`,
  **41432 bytes**, CRLF preserved (was 40476 in r1; +956 B).
* Reproducible from scratch: `narrow` then `authsplit` in
  `harness/apply_i14d_narrow.py`; `reverse_authsplit` is its exact inverse and lands
  on the pre-r2 tree byte-for-byte (`e8abd522b2072add062be225d7ec1ca10621ffa5be7841f99ef9fb339015cbd0`).

## 3. Measured closure (r2)

| check | command | rc | result |
|---|---|---|---|
| helper probe, 12 rows incl. the reviewer's 39-char credential | `authsplit_probe.py --src product_narrow` | 0 | `credential_leaks []`, `fidelity_drift []` |
| same probe on the base tree | `authsplit_probe.py --src product_base` | 3 | 0 leaks, drift on the two C13 rows (the base tree deletes `doc=17`) |
| oracle, 20 cases | `run_i14d_oracle.py --src product_narrow` | 0 | `narrow_must_failed []`, `keep_must_failed []`, verdict `pass` |
| rule table, 55 rows | `run_rule_table_i14d.py --src product_narrow` | 0 | `credential_leaks []`, `credential_secret_leaks []`, `touched []`, `fidelity_ok true` |
| copied suite, rewritten per RULING 1 | pytest `I14C_PRODUCT_SRC=product_narrow/src` | 0 | **86 passed / 0 failed** |
| new suite | pytest `test_i14d_single_token.py` | 0 | **25 passed** |
| real exit, 10 scenarios | `run_exit_probe.py --src product_narrow` | 0 | `E6-auth-scheme-newline` persists `"Authorization: <redacted>\ndoc=17"`, 0 grep hits |
| real CLI E5a/E5b | `run_real_cli_exit.py` | 0 | E5a 0 hits, E5b 1 declared-residual hit, no catalogs (unchanged from r1) |

End-to-end, at `worker.py`'s own `redact_and_truncate` exit, the persisted event is
now `"Authorization: <redacted>\ndoc=17"` (32 chars): **both** halves of the card's
exit clause hold on the input family that violated it, and the credential — the
reviewer's synthetic 39-char one, which shares no substring with this attempt's
marker — is absent from every produced stdout/stderr/JSONL file
(`after/probe_results_narrow.json`, field `persisted_or_printed_hits`).

## 4. The new rows the reviewer required (RULING 1 + RULING 2)

* **Oracle**: N5c `Authorization: Bearer\n<M>\ndoc=17` → 32; N5d obs-fold
  `Authorization: Bearer\n  <M>` → 25; N5e `authorization: token\n<M>` → 25. All
  three FAIL on the base tree, on M4, and pass on the fixed tree.
* **Rule table** (`cred-auth-split-*`, 7 rows, all `kind: credential`): LF, CRLF,
  obs-fold, no-space `Authorization:Bearer\n`, `authorization: token\n`,
  `…\n<M>\ndoc=17\nstage=summarize`, and one carrying a **39-char non-marker
  credential** — the row that would have caught F-REV-D-01, because a marker-only
  table cannot distinguish "redacts the marker" from "redacts a credential".
  `credential_secret_leaks` is now reported as a separate fact.
* **Copied suite `FIDELITY_CASES`**: 4 new auth newline-split rows. Pair count
  **28 → 32**; `harness/report_i14d_counts.py` was re-run and `r5/counts.json`
  regenerated (rule table **48 → 55**, oracle **17 → 20**, total nodeids **103 → 111**).
* **N13 relabel**: the auth-path note is no longer "declared residual"; it is
  recorded as the **F-REV-D-01 credential-leak regression** (`oracle.md`
  CORRECTION 2 §C2.3). The assignment-path residual (`password: iron steel`) keeps
  its accepted-as-declared status (RULING 3).

## 5. Mutation plan, with the missing arm added

Specimens are single-site derivations of `iso/product_narrow` (r2). M1/M2/M3 were
rebuilt from the r2 tree because the r1 specimens were derived from the pre-fix tree
and their byte hashes therefore moved; `iso/product_mut_auth1` (r1) was removed and
replaced by `iso/product_mut_auth1_r2`. Every hash below is recomputed on disk.

| id | specimen | sha256 (observability.py) | rc | what fails |
|---|---|---|---|---|
| M1 `product_mut_greedy` | scanner loop restored to r1 multi-word | `bc857d41…` | oracle 3 / rule 3 / probe 0 | the 5 assignment-path C13 cases + 4 rule rows; the auth family stays GREEN |
| M2 `product_mut_authnl` | auth join `[ \t]+` → `\s+` | `a36e90b6…` | oracle 3 / rule 3 / probe 0 | exactly `N5-auth-multiline` + `cred-auth-multiline-swallow` |
| M3 `product_mut_auth1_r2` | auth value = strict single token | `ef450712…` | oracle 3 / rule 3 / probe 3 | `N5`, `N5b`, 8 auth rule rows leak, probe D8/D9 leak — a scheme-ignoring single token is WRONG |
| **M4 `product_mut_authsplit`** | **`_AUTH_SCHEME_SPLIT` removed from the value group** | **`e8abd522…`** (== the pre-r2 tree) | oracle 3 / rule 3 / probe 3 / exit probe: persisted secret | all 3 new oracle rows, all 7 `cred-auth-split-*` rows, 10/12 probe rows, and the REAL EXIT persists `"Authorization: <redacted>\nghp_…\ndoc=17"` |

M4 is the arm the r1 plan lacked: it is the r2 tree **as if the fix had never been
written** (its `observability.py` hash is byte-identical to the pre-r2 tree), so it
covers the leak direction, and the new suite's end-to-end case fails on it with
`AssertionError: the wrapped credential was persisted in plaintext`.

Full matrix (rcs + facts): `mutations/mutation_matrix.json`.

## 6. RULING 1 rewrite — landed, and explicitly attributed

The reviewer's nodeid rewrite is applied to `harness/tests/test_i14c_real_exit_redaction.py`:
one renamed nodeid (`test_f08_c13_multiline_diagnostics_survive`, loop inverted,
`len(out) 34 → 98`, plus `< 200` / `> 90` and marker-absent guards and both input
lengths kept), three changed `FIDELITY_CASES` expectations, four required new auth
rows, and the two stale comments rewritten.

**Disclosure — this is the one place where the r1 attempt's separation of duties
changed, and it must be visible to the reviewer:**

* The r1 pass (and `oracle.md` §3, and the r1 `handoff.json`) recorded card clause 5
  as "the 4 nodeids stay byte-identical; their rewrite is the REVIEWER's act".
* The re-review instruction for this fix directed the implementer to apply it. The
  reviewer's RULING 1 had already made it conditional on the BLOCKER being fixed,
  and its text is the reviewer's own, so the implementer **transcribed the reviewer's
  text and authored none of the expectations**.
* The file is therefore **no longer byte-identical to I-14-C's** copy
  (`672b88de…` is the r1 state). Every difference is attributable to RULING 1;
  the rewrite is revertible by restoring that copy, and `changes.diff` /
  `after/final_hashes.json` pin the current bytes.
* If the reviewer prefers to re-author it, nothing else in this attempt depends on
  the exact text: the count binding is mechanical (`r5/counts.json`), and the
  implementer's own oracle carries the same expectations in
  `harness/run_i14d_oracle.py`.

## 7. Recorded, deliberately NOT fixed (reviewer's instruction)

F-REV-D-02 (`_VALUE` dead code ⇒ the headline `_BARE_VALUE` narrowing has **no
runtime effect**; the assignment-path mechanism is the scanner-loop hunk alone, and
the same dead-constant pattern is where F-REV-D-01 hid), F-REV-D-03 (narrowing
unmasks the digit-suffixed atom-table gap: `token=<A> token2=<B>` leaves `<B>` in the
clear), F-REV-D-04 (value-less `Authorization:` + newline still takes the next
token), F-REV-D-06 (`residuals_confirmed` 3 vs `rule_kinds.residual` 4 — the key is
renamed here and both lists are now emitted, which is a reporting clarification, not
a fix to the rule), F-REV-D-07 (external `revenue-forecast` HEAD drift). F-REV-D-02
is flagged in `decision.md` as a **promotion hazard**: do not tidy `_VALUE` and
assume the narrowing is what protects the assignment path.
