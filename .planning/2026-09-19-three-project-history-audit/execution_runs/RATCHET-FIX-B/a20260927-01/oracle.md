# Oracle - RATCHET-FIX-B (FC-1204 complexity ratchet)

- role: implementer_ratchet_b
- authorized_by: owner `§四十二 裁定一` (FC-1204 complexity ratchet, 2026-09-27)
- scope: company-wiki/src/company_wiki/source_catalog/ 3 files (B group)
  - producer_events.py  actual 3 -> frozen <= 1 (must be zero-branch top-level)
  - identity_cli.py     actual 9 -> frozen <= 6
  - artifact_read_model.py actual 11 -> new-file rule <= 10
- method: split only; behaviour unchanged. Frozen table NOT touched.
- note carried into each file: `Complexity ratchet (FC-1204, owner §四十二 裁定一, 2026-09-27): split only; behaviour unchanged.`
- metric authority: tests/contract/test_fc1204_complexity_ratchet.py::_max_complexity (top-level functions only)
- fail-closed: a file that cannot meet target or turns tests red is rolled back to its pre-image and reported blocked.
- dayu-agent: zero contact. No network. No git writes. No `git status`.
- write surface: the 3 target files + this output directory only.
