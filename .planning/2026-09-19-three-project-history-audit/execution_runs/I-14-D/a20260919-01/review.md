# I-14-D — INDEPENDENT REVIEW

Status: **revision r2 submitted, RE-REVIEW REQUIRED.** The implementer does not write an
acceptance verdict, and the r1 verdict (`changes_required`) is not inherited.

## Verdict history

| round | reviewer verdict | artifact |
|---|---|---|
| r1 | **`changes_required`** — BLOCKER F-REV-D-01 (credential-persistence regression on the auth path), 5 further findings, 3 rulings | `reviewer_report.md`, sha256 `499d91acf06a67e2f7dd06d4a5af6569b5b92a6e4b3b77adda57b739eaa03d2b`, 37659 B (recomputed by this attempt; matches the carrier's pin) |
| r2 | *pending* | this attempt after the fix |

The implementer's claims live in `oracle.md` (frozen, with CORRECTION 1 and
CORRECTION 2 appended), `decision.md` (D1-r2), `fix_record.md` (the point-by-point
answer to the BLOCKER), `commands.json` (raw rcs) and `handoff.json`.

## What changed since the r1 review (round 2)

1. **F-REV-D-01 fixed** with the reviewer's own RULING 2 mechanism
   (`_AUTH_SCHEME_SPLIT`, scheme-aware, fail closed). Both halves of the card's exit
   clause now hold on the same input at the real worker exit:
   `"Authorization: Bearer\n<secret>\ndoc=17"` persists as
   `"Authorization: <redacted>\ndoc=17"`. See `fix_record.md` §2–§3.
2. **New coverage in the leak direction**, which is what the r1 criterion was blind to:
   oracle N5c/N5d/N5e; rule table `cred-auth-split-*` ×7 (including a row carrying a
   39-char **non-marker** credential); copied-suite `FIDELITY_CASES` +4 auth
   newline-split rows; a new end-to-end case in the implementer's suite; and a fourth
   mutation **M4** whose `observability.py` hash is byte-identical to the pre-fix tree,
   i.e. the leak re-opened by construction — detected by all four instruments.
3. **RULING 1 rewrite landed** — 1 renamed nodeid (loop inverted, `34 → 98`), 3 changed
   `FIDELITY_CASES` expectations, 4 required new auth rows, 2 stale comments rewritten.
   The copied suite is therefore **no longer byte-identical to I-14-C's**
   (`672b88de…` is the restore point). This is the one separation-of-duties change in
   the attempt: see the disclosure in `fix_record.md` §6 and `binding.json`.
4. **Counts moved and were regenerated mechanically**: rule table 48 → **55**, oracle
   17 → **20**, `FIDELITY_CASES` 28 → **32**, total nodeids 103 → **111**
   (`r5/counts.json`, `after/counts.json`).
5. **N13's auth-path note re-labelled** from "declared residual" to the
   F-REV-D-01 credential-leak regression (`oracle.md` CORRECTION 2 §C2.3). The
   assignment-path residual keeps its accepted-as-declared status (RULING 3).
6. **Recorded, deliberately NOT fixed**: F-REV-D-02 (`_VALUE` dead code ⇒ promotion
   hazard; the assignment-path mechanism is the scanner loop alone), F-REV-D-03
   (`token2`/`secret2` atom-table gap now observable), F-REV-D-04 (value-less
   `Authorization:` + newline), F-REV-D-06 (residual-key reporting — clarified),
   F-REV-D-07 (external HEAD drift). F-REV-D-05's untrue binding sentence was removed.

## What to review (suggested order)

1. `reviewer_report.md` → `fix_record.md`: confirm each finding is answered and that
   nothing in the report was silently reinterpreted.
2. Re-derive the three new numbers by hand (N5c 32, N5d 25, N5e 25) and check they
   FAIL on `iso/product_base` **and** on `iso/product_mut_authsplit`.
3. Re-run: `harness/run_i14d_oracle.py` (20 cases, narrow rc 0 / base rc 3),
   `harness/run_rule_table_i14d.py` (55 rows, `credential_leaks` and
   `credential_secret_leaks` both empty on narrow, rc 0), the copied suite with
   `I14C_PRODUCT_SRC=iso/product_narrow/src` (expect **86 passed**), the new suite
   (`25 passed`), and `harness/run_exit_probe.py` (E6 must persist
   `"Authorization: <redacted>\ndoc=17"` with zero persisted-or-printed hits).
   `iso/venv` is self-contained and the guard accepts a declared non-product scratch
   root through `I14C_RUN_ROOT`, so all of it runs from any directory.
4. Mutations: `mutations/mutation_matrix.json` plus the four standing trees
   (`product_mut_greedy`, `_mut_authnl`, `_mut_auth1_r2`, `_mut_authsplit`); rebuild any
   of them with `harness/apply_i14d_narrow.py --op <narrow|authsplit|mut_greedy|
   mut_authnl|mut_auth1_r2|mut_authsplit|reverse_authsplit>`.
5. Round-trips: `changes.diff` (base → r2 narrow, 5101 B) and
   `changes_r2_authsplit.diff` (pre-r2 → r2, 1786 B, the whole fix);
   `after/git_apply_verification.json` (GIT_APPLY_REPRODUCES true) and
   `recovery/recovery_verification_r2.json` (reverse-apply reproduces
   `iso/product_base` across all 152 non-`__pycache__` source files).
6. Judge the disclosed clause-5 transcription (item 3 above) and the disposition of
   F-REV-D-02/03/04 — whether they belong on a follow-up card or must block this one.
7. Scope/authorization notes: `decision.md` D1-r2, the declared residual N13, and
   `r5/README.txt` explaining the counts-shim directory.
