# Reviewer report — CW-TEST-DEBT / a20260922-01

Independent review of the 2 CW unit-test debt fixes (GUARD-MERGE review
condition-1, verdict ACCEPT sidecar `2a26aaae`), card state at arrival =
`review_pending` / unsigned.

**Verdict: ACCEPT** (scope = these 2 test-file edits plus the card's evidence and
boundary claims; findings F1–F5 are minor, none blocking (domain: §9 findings)). Reviewer: independent
review subagent of parent session `session-bfecd191-fbc3-4a66-8ed1-6562479bf102`.
Reviewed 2026-09-23 (host clock, UTC+1-style local stamps used below).

Method: read / grep / pwsh only (domain: my command log). My runs live in `%TEMP%\rvrev-cwtd-a20260922-01`
(domain: this review's runs — 1 mirror build, 3 pytest invocations, 4 python
analysis scripts). CW opened READ-ONLY (domain: this review's writes — 0 product
bytes; scratch confined to `%TEMP%`; git used read-only: `rev-parse` / `hash-object` /
`diff --name-only` / `ls-files` / `check-ignore`, zero state-changing verbs,
domain: my command log). Files I write in the plan tree = this report + its
`.sha256` sidecar (domain: my deliverable writes, 2 files).

## 1. Deliverables — live re-hash by me (not transcribed)

| artifact | live sha256 (mine) | matches |
|---|---|---|
| `oracle.md` | `9334302aa236da374e74f69d9cbfa95e40aaf5ae0d3e76afd0f246079e820a42` | `oracle_freeze.json` + card close ✓ |
| `handoff.json` | `9c2a5527da4de9441db118ce0be45584f8122332b56337f29fab149725b2c919` | card's `final_deliverable_hashes.json` ✓ |
| `changes.diff` | `030e9e038d4afe69b084add785bee36068ed1d8a1e10e6694d1e18a9472f957f` | card's close hash ✓ |
| `before/test_readiness_graph.py` | `71893f5d0db8ca675e05ebcda6d7feebefde7ee9a7a19350461efc0ece4708a7` | before-pin ✓ |
| `before/test_prompt_injection_guard.py` | `c05e25fb4f2e3e1c72143ee3a7c56eccf8a7bddf750efb0394984561484f9bae` | before-pin ✓ |
| live `tests/unit/test_readiness_graph.py` | `a5db0c9c6959d9c8cbd68d606eec0dc9368ab09f93168a2b892e3fd459f368c2` | after-pin, at my start AND my close ✓ |
| live `tests/unit/test_prompt_injection_guard.py` | `d3bde1a3d5ec2495474aae5b91595362b2caad4c8a0178c6927bf2d8023eec3f` | after-pin, at my start AND my close ✓ |
| live `src/…/prompt_injection_guard.py` | `f900a13d7c22fe3bd742485c6b603de11b92a56d2414a2a046216ccd3b0b9c08` | start-pin = close-pin = HEAD ✓ |
| live `src/…/prompt_injection.py` | `7b22f23918d5e6b083a3c5272de2ed26c8a0c420b007f1268c664c0c86139618` | start-pin = close-pin = HEAD ✓ |
| live `src/…/readiness_graph.py` | `3f4c43b0049eca71fde4f7d9152b02674a26679b4470f6607383eb1820685acc` | start-pin = close-pin = HEAD ✓ |
| GM `iso/prompt_injection_guard.py` | `d71254782c10cd6d58c768eeb50e220de5e3d8047709e26f0604b5c59e67df0d` | ACCEPT pin ✓ |
| GM `iso/prompt_injection.py` | `88154de4ab7630606c2545cdcdf9c3ac44faf32bcae0f83f33a1cebc6d490f33` | ACCEPT pin ✓ |
| GM `iso/readiness_graph.py` | `50c94de28f328d125bd4834b2cda8a46794cba5f5f3f01c5415b4060b2d8c97b` | ACCEPT pin ✓ |
| GM `reviewer_report.md` | `2a26aaae736c44035c953b7f8a5751201daeeab223b2778a1678cd000f64cba5` | its `.sha256` sidecar content ✓ |

Additionally, each of the **26** entries in `evidence/final_deliverable_hashes.json →
deliverable_sha256` matched my live re-hash (26 of 26, 0 mismatches; domain: my
python re-hash over that manifest).

## 2. Oracle — frozen-first and the three required sections

Freeze ordering by disk times (domain: CreationTime/LastWriteTime of the attempt
files): `oracle.md` created **00:59:32.911**, written 00:59:46 →
`oracle_freeze.json` 00:59:56.731 (`frozen_at_utc 2026-09-22T23:59:56.707Z`) →
mirror scaffold 00:59:58 → RED run 01:00:14–01:00:21 → **first edit to either
test file 01:01:01** → greens 01:01:32+. The freeze chain (domain: disk mtimes) predates every edit
AND every run (domain: disk mtimes above; the pre-freeze `before/` copy-out at 00:58:34 is a read-only copy,
same class as GUARD-MERGE F1). Re-hash at my close = freeze value ✓.

- **§R** present (oracle L189–208): parent's 「22/22」 ruled void with the
  arithmetic (22 = 26 − 4; 9 + 22 = 31 > 26 collected); frozen binding form
  **(b')** = 0 failed / collected == 17 / the 11 RED names map one-for-one ✓.
- **§4-E5** present (L130–150): E5a (valid `source_sha256` to unmask the
  `policy_hash` assertion) and E5b (SQL-plant replacement, required comment
  carrying the pre-C7-absent / `unproven[2]` disclosure) frozen verbatim before
  any run ✓.
- **§R2** present (L210–224): 11-RED attribution table ⇒ E2+E3+E4 leave exactly
  2 red, hence E5 in the edit set ✓.
- Dispatch-label note: the dispatch's 「22→27」 has no counterpart token in the
  oracle (no `27` anywhere; the reconciliation is 26/17 arithmetic) — a dispatch
  characterization slip, recorded as F4; the substance the dispatch describes is
  present and correct.

## 3. The 2 edited test files — my own difflib against `before/`

Method: python `difflib.unified_diff` in memory, before-copy vs LIVE CW file
(domain: my Part A/B output). Results:

| file | hunks (mine) | card claim | changed lines |
|---|---|---|---|
| `test_readiness_graph.py` | **1** | 1 | +1 / −0 |
| `test_prompt_injection_guard.py` | **8** | 8 | +73 / −19 (8 replace/insert blocks) |
| `changes.diff` `^@@` scan | **9** total | 9 (1+8) | 2 sections keyed to the 2 before-pins, difflib header, no git metadata ✓ |

**readiness**: the single hunk is exactly the seed line
`+                        "state_domain": "review",` after `"policy_hash": RULESET_HASH,`.
No assert line changed (domain: my line accounting — 0 `-`/`+` lines containing
`assert`), no comment added, seed-tag count in file = 1.

**prompt_injection_guard**: each of the 8 hunks maps to the frozen edit set and
nothing else (domain: my hunk listing):

1. `+import hashlib` → E2; 2. module `_EVIDENCE_PAYLOAD` + `_evidence_sha256()`
(+ its explanatory comment) → E2; 3. `_write_receipt` gains
`evidence_payload=_EVIDENCE_PAYLOAD` and bound `evidence_sha256=_evidence_sha256()` → E2;
4. rename `test_record_without_binding_keeps_legacy_shape` →
`test_record_without_binding_rejected` + forward-contract body → E4;
5. `test_record_bad_binding_hash_rejected`: payload pair both calls + P5-c
masking comment + `source_sha256="a" * 64` in the policy branch → E5a (+E2);
6. `state_domain="cache"` in `test_evaluate_hit` → E3; 7. same in
`test_evaluate_absent` → E3; 8. E5b SQL plant + disclosure comment.

Test-count invariants: 17 `def test_` before = 17 after; exactly 1 name removed
and 1 added (the authorized rename) (domain: my parser over both files). Every
direct `record_prompt_injection_review(...)` call site carries
`evidence_payload` (5 of 5 call sites checked; domain: my call-site scan), and
`_write_receipt` carries it too → E2 「every call」 holds as implemented.

Assertion-line audit (lines whose stripped text starts with `assert`): the
set of tests with differing assertion lines is exactly
`{test_evaluate_absent}` (E3, authorized re-construction; `test_evaluate_hit`'s
change sits in its continuation lines — also E3, shown in hunk 6). E5b's 2
assertion lines are byte-for-byte equal to the before-copy, its docstring is
byte-equal, and its evaluate/assert tail is byte-equal ✓.

E5b disclosure comment (verbatim in file): the writer can no longer produce the
row, and "a pre-C7 row WITHOUT the tag reads as `absent` instead (GUARD-MERGE
handoff unproven[2], not asserted here)" ✓. E4 lineage comment
「Replaces test_record_without_binding_keeps_legacy_shape: P5-c made dual
binding MANDATORY … invalid BY DESIGN」 + citation docstring 「P5-c / OPEN-6 C2」
both present ✓.

## 4. My own re-run in a fresh %TEMP% mirror + one mutation

Mirror (domain: my build log): robocopy live CW `src`/`tests`/`config` +
`conftest.py`/`pytest.ini` into `%TEMP%\rvrev-cwtd-a20260922-01\mirror`, overlay
the 3 merged iso faces — overlay re-hash = `d7125478…`/`88154de4…`/`50c94de2…`
✓, the 2 tests in the mirror = after-pins `a5db0c9c…`/`d3bde1a3…` ✓.

- **Run**: `PYTHONIOENCODING=utf-8 python -X utf8 -m pytest
  tests/unit/test_readiness_graph.py tests/unit/test_prompt_injection_guard.py
  -q --no-header -p no:cacheprovider`, cwd = mirror → **26 passed, 0 failed**
  (9 + 17), Python 3.13.9 / pytest 9.1.1 — matches oracle (a)+(b') and the
  card's GREEN row-for-row.
- **My mutation (M1 spot-run)**: removed the seed tag from the mirror copy alone
  (14187 → 14137 bytes, i.e. back to the before-copy length) → **4 failed /
  5 passed** with the same 4 names
  (`test_ready_source_all_stages`, `test_safety_guard_drives_graph`,
  `test_safety_tampered_blocks_with_action`,
  `test_safety_ignored_blocks_with_action`) → the seed line is load-bearing and
  non-vacuous. Restore from the live CW file: hash = `a5db0c9c…`, re-run →
  **26 passed** (restore-then-green in my own mirror).
- Card raw re-read (tail bytes, domain: evidence/raw files): RED
  `15 failed, 11 passed`; green_a `9 passed`; green_b `17 passed`; combined
  `26 passed`; mut1 `4 failed, 5 passed` (same 4 names); mut_restored
  `26 passed`. The M2 raw (`7 failed, 10 passed`, the 7 payload-dependent names)
  is raw-verified only (domain: evidence/raw/mut2_payload_removed.txt) — I did not re-run M2 (see Unverified).

## 5. RED reproduction — my own name-set diff

I extracted `FAILED <nodeid>` lines independently from
`evidence/raw/red_unedited_on_merged.txt` (UTF-16 encoded; handled) and from
GUARD-MERGE's two reference raws `informational_cw_readinessgraph_unadapted_seed.txt`
+ `informational_cw_unit_tests_on_merged.txt` (domain: my python set comparison):

- CW RED = **15** names (4 readiness + 11 prompt-injection); GM references =
  4 + 11 = **15**; `RED − GM = ∅`, `GM − RED = ∅`, sorted-joined strings equal
  → **byte-identical name sets, both directions** ✓. Summary tails agree with the
  card's claim (`15 failed, 11 passed`) and with the GM reviewer §6 decomposition
  (4F/5P + 11F/6P on Run 1).
- Caveat: the GUARD-MERGE reviewer's own Run-1 console output is not persisted
  in `%TEMP%\rvrev-gm` (only `c7_rerun.txt` survives; domain: that dir listing), so the comparison anchor
  is the pair of reference raws the reviewer certified its Run-1 names against —
  which is exactly what oracle §2 pins.

## 6. Replaced-test design vs P5-c / OPEN-6 C2 semantics

- **Literal match against the merged iso**: `iso/prompt_injection.py` L86
  `_require_sha256(value, field, *, optional: bool = False)` raising
  `PromptInjectionReviewError` (L82/L90) with message
  `f"{field} must be a lowercase SHA-256"` (L91), invoked unconditionally at
  L117 (`evidence_sha256`), L121 (`source_sha256`), L122 (`policy_hash`) — so the
  writer emits exactly `source_sha256 must be a lowercase SHA-256` then
  `policy_hash must be a lowercase SHA-256`, in that order. E4's two
  `pytest.raises(match=…)` literals and its two-stage sequence therefore match
  the production-of-the-merged-face messages one-for-one ✓ (and the independent
  GUARD-MERGE GREEN literal `source_sha256 must be a lowercase SHA-256` is the
  same string).
- **E4 forward contract**: unbound write → stage-1 refusal; same write with
  valid `source_sha256` → stage-2 `policy_hash` refusal; afterwards
  `read_prompt_injection_review(_Store(con), "d1") is None` (nothing written) ✓ —
  implemented as claimed; passes only where dual binding is mandatory (domain: merged
  faces), i.e. the honest post-P5-c contract.
- **E5a**: valid `source_sha256="a" * 64` + payload pair reach the intended
  `match="policy_hash"` assertion; the expectation line itself unchanged
  (domain: my hunk-5 diff) ✓.
- **E5b technique**: `UPDATE documents SET metadata_json=? WHERE document_id='d1'`
  at L320 — byte-same technique as the pre-existing
  `test_evaluate_malformed_receipt_fails_closed` plant at L296 (grep: exactly 2
  occurrences in the file) ✓; planted row carries `"state_domain": "review"` ✓;
  name / docstring / both assertions / evaluate-tail byte-equal to before ✓;
  required disclosure comment present ✓.

## 7. Boundaries

- **Source pins, my start and my close**: `f900a13d…` / `7b22f239…` /
  `3f4c43b0…` — unchanged at both ends (3 of 3; domain: my two re-hash passes) ✓.
  The 3 production blobs are also byte-equal to `HEAD` (sha1 of raw bytes ==
  `rev-parse HEAD:<path>`, no EOL caveat) ✓.
- **CW tree write sweep** (domain: my recursive mtime sweep, window 00:57 → my
  close): exactly **5** paths carry a write time in the window —
  (a) the 2 authorized test files (01:01:01 / 01:01:16, the card);
  (b) `.source_catalog/catalog.sqlite3-wal` 00:59:38 (in-card-window;
  `.source_catalog/` is gitignored per `.gitignore:50` — runtime artifact, no
  disclosed card command opens that database, attribution open → F3);
  (c) `.source_catalog/catalog.sqlite3-shm` 01:12:51 and
  (d) `.pytest_cache/v/cache/{nodeids,lastfailed}` 01:15:50 — both strictly
  AFTER card close (01:09:19), written by an unidentified third-party pytest run
  of the live tree during my review → F3. No other file in CW (tracked or
  untracked; domain: same sweep) was written in the window.
- **vs CW HEAD** (my read-only git, `rev-parse` + `hash-object` +
  `diff --name-only`): the differing tracked set = **5** files —
  `tests/unit/test_readiness_graph.py`, `tests/unit/test_prompt_injection_guard.py`,
  plus pre-existing dirt `CLAUDE.md`, `README.md`,
  `src/company_wiki/source_catalog/artifact_dag.py` (3 files, shared mtime
  2026-09-22 22:23:23, i.e. before GUARD-MERGE's 23:59 start and before this
  card; also disclosed by the GUARD-MERGE porcelain spot). So the dispatch's
  「only the 2 unit files differ from CW HEAD」 is true for card-attributable
  deltas but repo-wide the set is these 5 → F2. EOL note (bounded): the before
  copy of `test_prompt_injection_guard.py` equals its HEAD blob after LF
  normalization (autocrlf clean-filter delta alone, pre-existing; the CRLF style
  of that file was preserved by the edit), and `test_readiness_graph.py`'s
  before copy equals its HEAD blob byte-exactly.
- **Zero git verbs by the card**: no `git <verb>` text occurs anywhere in the
  attempt directory (domain: my grep over the attempt tree); `commands.json`
  C1–C12 contain no git invocation; no `.git` state file (`index`,
  `COMMIT_EDITMSG`, `HEAD`) has an mtime after 2026-09-22 22:23:24 (domain:
  `.git` file mtimes), so no staging/commit/checkout occurred across the card or
  my review. The `.git` directory entry mtime (01:13:51, post-close) is a
  transient lock/unlock by an unattributed read-only git user — no state file
  changed. My own review used read-only git throughout (disclosed in the header).
- **C11 / evidence chain** (domain: my mtime table): every raw run output has
  CreationTime ≈ LastWriteTime (created once, never regenerated); each predating
  the generator-derived files — raws ≤ 01:02:58; `changes.diff` /
  `oracle_checks.json` / `mutation_summary.json` / `live_pins_close.json` /
  `binding.json` created 01:04:29.91x, last written 01:05:18.9xx. That is
  consistent with the disclosed 「generator ran 3×, parser bugs in runs 1–2, raw
  never regenerated or edited」: ≥2 distinct generator writes are provable from
  C≠W; the run-1/2 outputs themselves are no longer on disk (overwritten by
  design) — disclosure-only. The five machine checks in `oracle_checks.json` are
  each true, and its RED name list (15) matches my independent extraction.
- **Handoff honesty statements**: parsed as JSON — `unmapped` = **5** items
  including 「the rest of CW's unit/contract/e2e suites were NOT run」 ✓;
  `unproven` = **5** items (the dispatch says 6 → F1) including
  「the edited tests have NOT been run against the current unmerged production
  sources — BY DESIGN」 ✓. Both statements the dispatch requires are present and
  accurate as descriptions of this pass's actions. `status = review_pending`,
  `signature.signed = false`, `signature.reviewer = null` — untouched by me (I
  do not sign the handoff; this report + sidecar are the review authority,
  per the FIX/TTL/GUARD-MERGE carrier pattern).
- Cross-checked honesty of the by-design non-run: live production
  `prompt_injection.py` really lacks the merged contract (grep: `_require_sha256(… optional=True)`
  at L64/L65, no `evidence_payload must be provided`) and GUARD-MERGE
  `red_green_status_quo.json` R3 shows the unbound write accepted on exactly
  these before-pins — so running the edited tests against unmerged production
  would indeed fail for the wrong reason; not running them there was correct.

## 8. `recommended_cw_commit` block

5 entries, `count = 5`, `sources_written_by_this_card = 0`,
`tests_written_by_this_card = 2` (domain: my JSON parse of `handoff.json`):

| path | before → after | verification |
|---|---|---|
| `src/…/prompt_injection_guard.py` | `f900a13d… → d7125478…` | exact match to GUARD-MERGE landed `recommended_cw_commit` ✓; live before == `f900a13d…` at my close ✓ |
| `src/…/prompt_injection.py` | `7b22f239… → 88154de4…` | exact match to GUARD-MERGE landed block ✓; live before == `7b22f239…` ✓ |
| `src/…/readiness_graph.py` | `3f4c43b0… → 50c94de2…` | exact match to GUARD-MERGE landed block ✓; live before == `3f4c43b0…` ✓ |
| `tests/unit/test_readiness_graph.py` | `71893f5d… → a5db0c9c…` | before == `before/` copy == pre-edit pin; after == my close re-hash ✓ |
| `tests/unit/test_prompt_injection_guard.py` | `c05e25fb… → d3bde1a3…` | before == `before/` copy == pre-edit pin; after == my close re-hash ✓ |

The 3 source pins are byte-identical between this card's block and GUARD-MERGE's
landed handoff (programmatic field-by-field compare: 3/3 match) ✓. The GUARD-MERGE
carrier (`2a26aaae…`) re-hashes live to its sidecar content ✓, and its condition-1
text (bundle 3 merged files with the 2 debt fixes via this separate pass) is the
authority this card executed.

## 9. Findings (minor — none blocking; domain: this review's finding list)

- **F1 (dispatch count)**: handoff `unproven` holds **5** entries, not the
  dispatch's 6; `unmapped` = 5 as dispatched. Content required by the dispatch
  (both honest non-run statements) is present; the "6" is a dispatch arithmetic
  slip of the same family as 22/22.
- **F2 (dispatch count)**: repo-wide, **5** tracked files differ from CW HEAD
  (the 2 tests + the 3 pre-existing dirt rows disclosed by GUARD-MERGE), not
  only the 2; card-attributable delta remains exactly the 2 tests, and the 3
  production sources are byte-equal to HEAD.
- **F3 (concurrent third-party runtime artifacts, attribution open)**: inside
  the card window, `.source_catalog/catalog.sqlite3-wal` was touched at 00:59:38
  (gitignored runtime; no disclosed card command opens that DB); after card
  close, an unidentified third party ran pytest against the LIVE CW tree
  (basetemp-dir touch 01:11:36; `.pytest_cache` nodeids+lastfailed written
  01:15:50; `.source_catalog-shm` 01:12:51; no python process remains at my
  close). Facts from that cache: nodeids collected **800** unit + **2113**
  contract ids including our 17+9; `lastfailed` holds **29** keys — ours absent
  (domain: my counts over both cache files — 0 of our 26 keys); every entry is a
  contract/config-doctor/source_lifecycle failure. Bounded inference from metadata alone: such
  a state is consistent with either a run that deselected our 2 files or a
  merged-pinned run (the `PYTHONPATH/GAPS_PIN_CW_DIR` pattern battery (ii) uses)
  — neither mechanism is verified by me, and the runner is unidentified. No
  tracked bytes changed (`git diff --name-only HEAD` identical before and after
  this episode). Parent should identify this runner before relying on
  「first live validation = post-commit」 as a global claim.
- **F4 (dispatch label)**: 「22→27」 appears nowhere in the oracle; the §R
  arithmetic is 26/17 (`22 = 26 − 4`, `9 + 22 = 31 > 26`). Substance matches the
  dispatch; the label alone is off.
- **F5 (doc-only edit-set wording)**: two comment groups exceed the frozen edit
  set's literal wording — E2's 5-line module comment above `_EVIDENCE_PAYLOAD`
  and E5a's 2-line P5-c masking comment (the oracle names E4's and E5b's
  comments explicitly, E1's comment explicitly excluded, E2/E5a's silent). Both
  are rationale documentation with zero assertion/behavior effect, and hunk
  accounting is unaffected (9 hunks, each inside E1–E5 regions); noted for the
  record rather than as a violation of scope.

## 10. Unverified / residual

- M2 (`evidence_payload` mutation) not re-executed by me — raw-verified alone
  (`7 failed, 10 passed`, the 7 payload-dependent names); I re-ran M1 myself.
- GUARD-MERGE reviewer's Run-1 console output is not on disk (§5 caveat).
- Generator runs 1–2 outputs overwritten by run 3 (C11; ≥2 writes proven from
  C≠W, run count itself disclosure-only).
- Attribution of the WAL / SHM / `.pytest_cache` writers (F3) — unattributed
  from file metadata alone.
- Edited tests vs unmerged production: never run by this card (by design;
  stands) — and my finding in §7 verifies the by-design premise against the
  live bytes; rest of the CW suite not run by this card (stands; see F3 for a
  third party's separate run).
- Single-platform, single-runner evidence only — domain: this host (Windows, CPython 3.13.9,
  pytest 9.1.1) — same residual as the card's `unproven[3]`.
- The CW commit itself is not run here (parent's action, condition-4); battery
  re-run condition (condition-2) and store UNRATIFIED (condition-3) are untouched
  by this card and stand as written.

---

**Verdict: ACCEPT.** The 2 edits are exactly the frozen E1–E5 set (1 + 8 hunks,
no expectation changed outside the two authorized E3 constructions and the E4
forward replacement), RED reproduces byte-identically, green is 26/26 in my own
fresh mirror, M1 is non-vacuous with the same 4 names, the replaced-test design
matches the merged iso's literal P5-c messages, and each boundary pin held at my
start and close. Scope if accepting: the parent performs the single CW commit
bundling **all 5 files** (hook runs); the unmerged-production non-run stands (this
card's first live in-tree validation = post-commit CW suite; caveat F3 for other
runners); store UNRATIFIED and GUARD-MERGE `unproven[2]` stand; handoff stays
`review_pending`/unsigned until the parent's landing — this report + sidecar are
the signature.

Signed: independent reviewer (CW-TEST-DEBT / a20260922-01), verdict **ACCEPT**,
findings F1–F5 (none blocking; domain: §9 above). Sidecar: `reviewer_report.md.sha256`.
