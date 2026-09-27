# WC-6 evidence index

All files under `evidence/` were produced by the harness in `harness/` with the interpreter
pinned in `binding.json`. Raw product stdout/stderr/rc are kept next to every judged run;
nothing here is a summary written by hand unless it says so.

## Pins / isolation

| File | What it proves |
|---|---|
| `source_pins_before.json` | live CW `src/+tests/+config` = 503 files, manifest `41c2271d…`, `iso_equals_live: true` **before any edit**; hashes of the 7 key sources; sha256 of the I-07-C carriers + REMEDIATION_REGISTER |
| `source_pins_after.json` | the same live manifest **unchanged after the attempt** (`live_key_sources_drifted_vs_before: []`, manifest `41c2271d…`); `iso_equals_live: false` is *expected* and lists exactly the two fixed files |
| `complexity_before_after.json` | ratchet's own algorithm on both files, live vs fixed: per-function values **identical**, file max `adapter_dispatch 4 (=frozen 4)`, `scanner 140 (=frozen 140)` |

## The four arms (probe cell, one root, four I-07-C-shaped probes)

| Label | Code state | Notes |
|---|---|---|
| `red_run1/` | pre-fix (iso == live) | first RED observation (NULL ×4); superseded as comparison base by `red_prefix` (stage order + normalization fixed afterwards) — kept, never overwritten |
| `green_run1/` | fix applied | first GREEN run, same supersession |
| `red_prefix/` | **live pre-image copied back in, both hashes verified equal the pins** | the RED comparison base |
| `green/` | fix applied | the GREEN comparison base |
| `repeat_postfix/` | fix applied (independent rebuild) | determinism control |
| `mutation/` | fix present, pass-through removed (`error=None,  # MUTATION …`) | non-vacuity arm |
| `mutation_attempt1_mutation_not_applied/` | fix present (mutation silently failed to apply) | preserved disclosure of a harness mistake |
| `chain/` | fix applied | cell used for the end-to-end reason chain |

Each `<label>/` holds `fixture_manifest.json` (tree sha `37be0c5a…` in every arm = identical
input), `prepare.json`, and per stage (`scan`, `rescan`, `resolve`, `cfg01`):
`argv.json`, `stdout.txt`, `stderr.txt`, `product_rc.json`, `catalog_dump.json` (raw read-only
dump), `normalized.json` (outcome allowlist + `diagnostic` = `locations.error` per probe).

## Comparisons (the byte-proofs)

| File | Verdict |
|---|---|
| `compare_red_prefix_vs_green.json` | **rc 0** — outcome bytes identical in all 4 stages; diagnostics change on exactly the 3 remediated probes; fixture identical |
| `compare_green_vs_mutation.json` | **rc 0** — outcome bytes identical; diagnostics revert to NULL on the same 3 paths (non-vacuous) |
| `compare_green_vs_repeat_postfix.json` | **rc 0** — two independent post-fix runs identical everywhere (harness determinism) |
| `reason_chain.json` | **rc 0** — 4 probes × 4 hops (adapter evidence → `_Candidate.error` → `locations.error` → `SourceCatalog.query().locations[].error`) all equal the oracle literals; records which query view surfaced each row |
| `family_files.json` + `family_grep.txt` | mechanical family selection (60 files, patterns frozen in oracle §6) |
| `fam_before_family.txt` / `_outcomes.json` / `.xml` | pre-fix family run (raw rc, per-test outcomes) |
| `fam_after_family.txt` / `_outcomes.json` / `.xml` | post-fix family run |
| `compare_family_fam_before_vs_fam_after.json` | per-test outcome equality before vs after |
| `changes_diff_manifest.json` | exactly the 2 allowed product files differ between iso and live; no iso-only / missing files |

## Disclosures kept as evidence (not hidden)

- `mutation_attempt1_mutation_not_applied/` — the first mutation attempt never changed the bytes
  (`Set-Content -Encoding utf8NoBOM` unsupported on this host); the arm ran fixed code and was
  detected by the unchanged hash, then re-done properly.
- `red_run1/`, `green_run1/` — first-pass arms with the original (asymmetric) stage order.
- `fam_before_family.txt` — 23 pre-existing failures / 8 pre-existing skips with their raw
  assertion texts (18 are the iso copy scope not including `scripts/`; 5 pre-existing,
  including the live `archive_retired_evidence.py 19 > 7` ratchet failure).
