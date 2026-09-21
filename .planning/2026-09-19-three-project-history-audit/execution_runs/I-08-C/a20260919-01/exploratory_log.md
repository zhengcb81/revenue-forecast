# I-08-C — exploratory-phase log preservation

- Card: `I-08-C` · attempt `a20260919-01` · written in revision **r3**
  (deliverable remediation after an independent `changes_required` verdict)
- Reviewer item addressed: `review.md` "what would close this card" item **(4)**
  — "Re-freeze the oracle with E4 either implemented or explicitly withdrawn,
  **and preserve the exploratory run log**"; reviewer unverified-list item **3**.
- This file is **not** a reconstruction and **not** a substitute log. It is an
  inventory of what actually survives, with hashes, plus an explicit list of what
  does not. No log was fabricated for the exploratory run.

## 1. What the exploratory phase was

`oracle.md` "Revision r2 (pre-verdict freeze)" records one exploratory run of an
early 12-test revision: **8 passed, 4 failed**. Its purpose was to validate
fixture mechanics. It found that the originally chosen E6 forgery vector
(`segments[0].base_revenue`) is not bound by any output gate; that vector was
moved to its own case **E13**, and E6 was re-pointed at the top-level
`base_revenue`, which is bound. The expectations were then frozen again (r2)
**before** the verdict run.

Independent reviewer adjudication of the freeze order (`review.md`):
`ADJUDICATED: no pre-registration violation` — the r2 freeze at 18:58:33 UTC
precedes the verdict stdout at 18:58:47 UTC, and the exploratory iteration is
disclosed in the oracle.

**Known, disclosed weakness (not repaired):** E13's expected outcome
("`validate_forecast_output` ACCEPTS") was pinned by *observing* the exploratory
run rather than derived from code reading. E11's gap *was* derived from code
reading (`revenue_publication.py:222-226`). E13 remains labelled as empirical in
`oracle.md` (r1 line 63) and in `handoff.json`.

## 2. What survives — archived in `exploratory/`

Archived **before** the r3 run by `scratch/archive_exploratory.py`
(raw rc 0, stdout kept), because that run rewrote `.pytest_cache/v/cache/*`.
Byte-identical copies; sizes, source mtimes and sha256 are in
`exploratory_manifest.json`.

| Artefact | Bytes | sha256 | What it is |
|---|---|---|---|
| `exploratory/pytest_cache_v_cache_lastfailed/lastfailed` | 2 | `44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a` | `{}` — **already overwritten by the r2 verdict run before this round**; the exploratory failure set was lost earlier, not by the remediation |
| `exploratory/pytest_cache_v_cache_nodeids/nodeids` | 1097 | `87341184954349530a11da5a7b062ecf7ec9a73b1f39fec34144ae502ecc1f69` | the **r2 verdict-run** node list, 12 node ids (the file the reviewer read) |
| `exploratory/pytest_cache_CACHEDIR.TAG/CACHEDIR.TAG` | 191 | `37dc88ef9a0abeddbe81053a6dd8fdfb13afb613045ea1eb4a5c815a74a3bde4` | cache marker, created 18:53:35 UTC = first (exploratory) pytest run |
| `exploratory/pytest_cache_README.md/README.md` | 302 | `73fd6fccdd802c419a6b2d983d6c3173b7da97558ac4b589edec2dfe443db9ad` | cache readme, same run |
| `exploratory/pycache_pytest_pyc/test_i08c_consumer_rejection.cpython-313-pytest-9.1.1.pyc` | 15616 | `f0dbe540404b8045f393a9f93695cc835a6bcf5323d3699dfe2afd1262941431` | r2 verdict-run bytecode; header `flags=0, field1=1790017267, field2=8542` = source mtime 2026-09-21T19:01:07Z / size 8542 = the **r2** test file |
| `exploratory/pycache_plain_pyc/test_i08c_consumer_rejection.cpython-313.pyc` | 13128 | `572318749a6b5685677de16f21e6b8a20db285990775501b97e9ace2a72e4bd5` | same source revision, compiled without the pytest assertion-rewrite tag (20:13:12Z = the reviewer's rerun window) |

Both `.pyc` files carry the timestamp-based source id
(`field1` = source mtime `1790017267` = 2026-09-21T19:01:07Z, `field2` = source
size `8542`), both equal to the **r2** test file. So **neither surviving `.pyc`
is an exploratory artefact** — the exploratory bytecode was replaced in place
before the r2 run. Claiming either as exploratory evidence would be wrong.

## 3. What does NOT survive (honest gaps)

1. **The exploratory run's stdout.** It was never written to a file by the
   implementer of record. No preserved stdout exists anywhere under this attempt
   — before this remediation or after it.
2. **Per-test pass/fail detail.** Only the prose count "12 tests, 8 passed"
   (`oracle.md` revision r2) and the echoed note in the original `handoff.json`
   `oracle.provenance` survive. *Which* four failed is not recorded; the oracle
   names only the E6/E13 vector change as the reason.
3. **The exploratory source revision of the test file.** It was edited in place;
   the r2 revision (8542 B / `5dd5a96c…`) replaced it, and the r3 revision
   (10902 B / `0072b160…`) replaced that.
4. **The exploratory node-id list.** `nodeids` was overwritten by the r2 verdict
   run before this round, so the pre-r2 node set cannot be recovered; if the
   exploratory revision had 12 nodes with different ids, they are gone.
5. **The exploratory `lastfailed` set.** Overwritten to `{}` by the r2 run;
   pre-dates this remediation.

Corroboration of the exploratory run is therefore limited to: the disclosed
prose in `oracle.md`, the `.pytest_cache` creation time 18:53:35 UTC, the
`lastfailed` write time 18:56:19 UTC, and the fact that the r2 freeze at
18:58:33 UTC precedes the verdict stdout at 18:58:47 UTC. The independent
reviewer reached the same position and did not treat the missing stdout as a
freeze-order violation.

## 4. r3 run artefacts (for contrast — these ARE complete)

The r3 evidence run **was** logged in full, so the same gap is not repeated:

- `pytest_r3_verdict.stdout.txt` — full `-v` stdout, 13 collected / 13 passed in
  2.37s, raw rc 0 (also `runner/.rc.txt`)
- `test_i08c_consumer_rejection.py` — 10902 B / `0072b160…`, frozen before the run
- `.pytest_cache/v/cache/nodeids` — now the 13-node r3 list (the 12-node r2 list
  is preserved in `exploratory/`)
- `commands.json` entry `I08C-c4-verdict-pytest` — argv, cwd, env, timeout, raw
  and expected rc

## 5. Residual risk this file does not remove

The exploratory phase remains **weakly evidenced** (prose + cache timestamps
only). That is a property of what was preserved at the time, and it cannot be
fixed retroactively without fabricating a log. If a future reviewer requires
per-run stdout as a hard precondition, the correct disposition is a process
finding against the r1/r2 attempt, recorded here rather than papered over.
