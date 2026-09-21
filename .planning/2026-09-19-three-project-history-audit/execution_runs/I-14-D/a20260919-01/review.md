# I-14-D — INDEPENDENT REVIEW: PENDING

Status: **review_pending**. The implementer does not write an acceptance verdict.

This file is reserved for the independent reviewer. Nothing below may be read as a
pass/fail conclusion; the implementer's claims live in `oracle.md` (frozen), `decision.md`,
`commands.json` (raw rcs) and `handoff.json`.

## What to review (suggested order)

1. `oracle.md` — the frozen new oracle, including hand-computed expectations (§2),
   the RED→GREEN definition (§3, incl. the only-4-allowed-RED rule for the copied
   I-14-C suite), the mutation plan (§4) and CORRECTION 1 (appended, append-only;
   pre-correction snapshot `before/oracle.md.pre-correction-1`,
   sha256 `d8deaee4e7f4a21c13722ffa58c18c2c093d789b9701d249880f95f7bd3fddb4`).
2. Re-derive the numbers: N1 (112 in → 98 out with your own 24-char marker), N4
   (325 → 314 pre-truncation → 200 persisted; prefix 193; tail = space + 6 y's),
   N5 (66 → 48), N13 residual.
3. Re-run anything: `iso/venv` is self-contained;
   `harness/run_i14d_oracle.py --src iso/<tree>/src --label <label> --out <your file>`
   and `harness/run_rule_table_i14d.py` work from any cwd; the copied suite runs
   with `I14C_PRODUCT_SRC` pointed at any tree (17 subprocess-backed cases included;
   guard accepts a declared non-product scratch root, refuses product paths).
4. Mutations: `iso/product_mut_greedy` / `_authnl` / `_auth1` are standing specimens;
   rebuild with `harness/apply_i14d_narrow.py --op <narrow|reverse|mut_greedy|mut_authnl|mut_auth1>`.
5. The copied I-14-C suite's 4 expected-RED nodeids are yours to rewrite against
   this oracle (card clause 5): `test_f08_c13_multiline_loss_is_frozen_not_hidden`
   plus the three greedy-semantics `FIDELITY_CASES` parameters. The implementer did
   not touch them (byte-identical copy, sha256
   `672b88de585046759f4ef29ce008fdbff9fa76404446ff7ae7317ddf539cce15`).
6. Scope/authorization notes: `decision.md` D1 (auth-path line-bound vs strict
   single token; option 2 available if you prefer scheme-visible envelopes), the
   declared residual N13, and `r5/README.txt` explaining the counts-shim directory.
