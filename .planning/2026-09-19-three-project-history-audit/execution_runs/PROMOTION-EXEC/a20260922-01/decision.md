# decision.md — PROMOTION-EXEC a20260922-01

Authority: `OWNER_DECISIONS.md` §十八 verbatim「B: 全批」(2026-09-22) — ALL promotion rows of
the approved manifest executed by this card, per-item verification, lifting 生产零合并 for the
listed items ONLY. Contract `PROMOTION-PREP/a20260922-01/promotion_batch_manifest.md` verified
first (19190 B, sha256 `6759d1eb…3aac` — matched). `oracle.md` frozen BEFORE the first
production write; `binding.json` pins every before-hash measured live.

No git writes (parent commits after evidence). Write boundary held: only listed target paths
were written (one exception disclosed below under "boundary incidents").

## Per-row outcome

| row | source → target | src sha | target before → after | verification rc | outcome |
|---|---|---|---|---|---|
| B-1 | B1 iso fixed3 → RF `scripts/{revenue_core,revenue_publication,revenue_report}.py` | `8a761498…`/`bc2bb4a3…`/`212f0059…` | `1821fd2a…`/`183803bb…`/`a85fb484…` → **= src** | hash 0, py_compile 0, **13-node 0 (13/13)** | **PROMOTED + VERIFIED** |
| B-2 | B3 iso → RF `scripts/company_wiki_source.py` + B3-PREREQ fixed2 → RF `scripts/source_preparation.py` (**same batch**) | `7d1bd8f9…` / `91a6dc32…` | `225fecdd…`/`37a3eeae…` → **= src** | hash 0, py_compile 0, REM-49 parity 0, FC-904 **11 passed** 0, rem49 test **5 passed** 0 | **PROMOTED + VERIFIED** |
| B-3 | I-14-D r6 → CW `source_catalog/observability.py` | `2f644994…` | `a73826aa…` → **= src** | hash 0, py_compile 0, import 0 | **PROMOTED + VERIFIED** |
| B-4 | I-14-F-R1 → CW `conftest.py` + `tests/contract/test_short_basetemp_convention.py` | `a908c9da…` / `1fd4e0d8…` | ABSENT ×2 → **created = src** | pre-condition 0, hash 0, py_compile 0 | **CREATED + VERIFIED** |
| B-5 | DW15 fixed → CW `source_catalog/{prune,archive}_retired_evidence.py` | `0c99bbe0…` / `bbe855e4…` | `2358c73b…`/`143fef01…` → **= src** | byte-exact 0, py_compile 0 (retry), import 0; 15-test harness not run (guard) | **PROMOTED + VERIFIED (CODE ONLY — E-4: execution stays UNAUTHORIZED)** |
| B-6a | I-14-F originals | — | — | hashes != `c22be9f3…`/`b0402b56…` | **NOT PROMOTED (superseded by R1) — verified nothing landed** |
| B-6b | I-14-B → natural_window.py | — | UNRESOLVED | card/carriers read | **BLOCKED-unresolved: card declares NO production target ⇒ I-14-I SKIPPED (no path guessing); natural_window.py absent in both repos** |
| B-6c | I-10-B → RF `scripts/model_registry.py` | `62f864b9…` | `9ec65295…` → copied `62f864b9…` → **REVERTED `9ec65295…`** | hash 0, py_compile 0, focused battery **1 FAILED** | **STOPPED + REVERTED (see below)** |
| B-7a | `tools/pre_push_gate.py` | — | `3df161a7…` | before==after | **NOT TOUCHED (concurrent GATE-OQ-FIX card owns it)** |

## The 13-node suite (I-08-C, frozen test file 13152 B / `3f83fdf2…`)

- **Pre-promotion fact (card-recorded, both recorded here as frozen):** RUN-B against then-unfixed
  production = exactly **{e11, e13} red, 11 passed, rc 1** (anti-vacuity; RUN-A on B1's fixed
  tree = 13/13 rc 0).
- **Post-B-1 (RF_IMPORT_ROOT pointed at the NOW-PROMOTED production tree): 13 collected /
  13 passed / rc 0** (9.21 s).
- **Run-wide final (fully-promoted final tree, incl. B-2 landed, B-6c reverted): 13/13 rc 0**
  (3.56 s) — `evidence/B-1_i08c13_post_promotion.txt`, `evidence/RUNWIDE_i08c13_final.txt`.

## B-6c STOP detail (the one failed row)

Copying `62f864b9…` over production was byte-exact (manifest hash check passed) and py_compile
was green, but the card-demanded focused RF model battery went **31 failed / 53 passed** —
every traceback at the promoted `scripts/model_registry.py:410` (defect-1 省缺即抛: production
registry specs declare optional drivers like `other_revenue`/`usage_revenue` WITHOUT explicit
defaults, while `tests/test_model_economic_guardrails.py` encodes the old silent-0.0-fill
oracle; one more node flips on defect-2 sign-role rules).

Frozen failure rule executed:
1. **Control pre-check** (isolated copy of RF scripts+tests+config with ONLY model_registry
   restored to its before-image; B-1/B-2 promoted files kept): **59 passed rc 0** → proves
   green pre-promotion and excludes B-1/B-2 as the cause.
2. **STOP + REVERT** production `model_registry.py` from `recovery/before_images/B-6c/` —
   restored byte-exact to `9ec65295…`.
3. **Post-revert rerun:** **59 passed rc 0** — no half-promoted file left.
4. Continue other rows → all remaining checks green.

**Consequence note (recorded, not acted on):** because B-6c did NOT land, the four M-card oracle
forward-disclosures (M05/M14/M20/M24 defaults-phase flips + M14 E-5/E-6/E-7) remain **INACTIVE**.
The E1E7-ERRATA-LANDING carriers already carry their non-promotion statements and stay accurate.
**No oracle was touched by this card.**

**Follow-up for parent/owner:** before B-6c can be re-attempted, RF's
`tests/test_model_economic_guardrails.py` needs an alignment/replacement decision (same shape as
DW15's "product contract tests encode the wrong oracle" finding, I-15-A): either the test battery
is updated to the I-10-B semantics, or explicit defaults are added to the registry specs. This is
an owner/parent orchestration call — NOT decided here.

## SP repo-by-hash resolution (manifest constraint for B-2)

Live probe: manifest pin `37a3eeae…` = `revenue-forecast/scripts/source_preparation.py`;
`company-wiki/src/company_wiki/source_catalog/source_preparation.py` = **ABSENT** ⇒ target is the
RF path. Both B-2 files were promoted in the same copy operation (same-batch constraint honored).

## Boundary incidents (disclosed)

1. **`tests/test_fc1105_fault_injection.py` shows ` M` in RF porcelain but was NOT written by
   this card.** It was absent from this card's before-snapshot; `git --no-optional-locks diff`
   shows exactly one hunk `timeout=120 → timeout=300` in `_t2(...)`, which is verbatim the
   concurrent **GATE-OQ-FIX** card's OQ-02 mandate (§十八 row B ②); mtime 19:38:37+01:00 falls in
   the shared window because both cards run concurrently.
   Evidence: `evidence/ATTRIBUTION_fc1105_not_this_card.txt`.
2. **First `py_compile` attempt for B-5 (with PYTHONPYCACHEPREFIX) returned rc 1** (Errno 2 on a
   temp .pyc under the redirected prefix). Production was never written (recent-write scan of RF
   and CW `__pycache__` = empty); superseded by an explicit-`cfile` retry, rc 0. Both recorded.
3. Zero writes leaked into the B3-PREREQ or I-08-C attempt directories (10-min mtime scan for
   B3-PREREQ = none; I-08-C `.pytest_cache` pre-existed and was protected by
   `-p no:cacheprovider`).

## Boundaries honored

- CW dirty-3 byte-unchanged: CLAUDE.md `963869fa…`, README.md `302bd10b…`, artifact_dag.py `0c8b1d6d…`.
- `tools/pre_push_gate.py` byte-unchanged by this card (`3df161a7…` before == after).
- No git add/commit/restore/stash anywhere; git only read-only (`status`, `--no-optional-locks diff`).
- No self-sign; handoff stays `review_pending` / unsigned.
- No file written outside the listed targets **by this card** (incident 1 is the concurrent card's).

## Files touched per repo (this card, net)

- **revenue-forecast (5, all `scripts/`)**: `revenue_core.py`, `revenue_publication.py`,
  `revenue_report.py` (B-1); `company_wiki_source.py`, `source_preparation.py` (B-2).
  `model_registry.py` net UNCHANGED (B-6c promoted then reverted).
- **company-wiki (5)**: `src/company_wiki/source_catalog/{observability,prune_retired_evidence,
  archive_retired_evidence}.py` (M); `conftest.py`, `tests/contract/
  test_short_basetemp_convention.py` (new, untracked).
