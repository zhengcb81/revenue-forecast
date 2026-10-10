# P7-RF MAIN scope fix — source stable

Status: **implementation_complete_source_stable**, 2026-10-11. Actual HEAD: `9e29b1f8491ed9d0799a79084c4474d789d4fdaf`; no commit/merge/push/install by this agent. RF working directory: `C:/Users/郑曾波/.codex/worktrees/m3-acceptance-20261010/revenue-forecast`.

## Root cause and exact responsibility

The public diagnostics flattened referenced calibrations into one global PID→singlecalID map. A legal sharednative root consumed by SegmentA and SegmentB therefore inherited scopeA support in B; with two real scopedcalibrations it also selected whichever appeared first and borrowed that calibration's claims.

Only `scripts/research_support_diagnostics.py` production code changes. Its private `_covering_calibrations_for_cell` builds a peractual segment×scenario×year relationship: calibration scope must be that actual segment or explicit company scope, the same scenario's actual output must be a root in this cell, and the validated native output period must match its FYyear. A PID may have multiple matching calibration IDs; the cell's calibration/claim lists retain all and only these matching IDs. The validated strictFYyyyy contract is reused, not changed.

Shared roots remain fully legal. A calibration scopedA supports A; B needs its own applicable calibration or a real companyscope relation. Source numerical facts/parametervalues, DAG, confidence, arithmetic, period contracts, identity, authorization and nativeforecast runtime are unchanged. Diagnostics still use `economic-support-diagnostics/1`, remain optional/read only, and report `economic_truth_inferred=false`; no small-step permission or reject gate was added.

## TDD and acceptance

| Check | Actual result |
|---|---|
| Responsibility RED | **3 failed / 7 passed**,2.13s; sharedroot scope borrowing and both list-order claim borrowing reproduced |
| Concentrated responsibility | **35 passed**,6.63s: diagnostics10 + scopedcalibration14 + evidence-role11 |
| Ruff |2files,exit0 |
| mypy |1sourcefile,exit0 |
| Saved minimal-input real publicCLI |1invocation,**accepted**,0.286s; three A cells supported and three B cells unsupported |

Newtests preserve companyscope support and distinct A/B calibrations on the samePID with different claimIDs, in either list order. Original source period/disclosure/measurement and nativebridge tests remain green in the concentrated pack. There was no repeat of the119-test full compatibility run or the four pipeline suite.

The publicCLI actually invoked `scripts/research_support_diagnostics.py --input OWNED/input.json --output OWNED/diagnostics.json`, copying only the independent review's saved input into ownedTEMP. InputSHA `3353ccb20511e42a86ca3a8bc1e4e3bce6dad483c4c481e32e6276bedb506ef7`. DiagnosticsSHA `ee796335f7c65264934cfa9b48a84477422a3fe52c180b505d89a06f3c871805`. Exit0; actualnative validation legal; A correctly returns `reference_bridge` and its real referenceclaimIDs, B returns no borrowedcalibration/claimIDs and concrete `calibration_scope_not_covering:reference_bridge:Segment B` plus actualPID reasons. The input, original failedreview and facts remain intact.

## Isolation and preserved evidence

All37 protected original RF config/fixtures/oldhandoff/PWF/logs and prior MAIN reception evidence match their beforeSHA. All5 original failedreview files match; the original failure receipt/report/JSON was not rewritten. All10 prior periodrepair source/test/reference files match their acceptedSHA. HEADunchanged. ROOT-owned `.gitattributes` and `main_reception_fix.md` were alreadydirty at start and retained.

RED, concentratedGREEN and publicCLI all used ownedTEMP with explicit registrylocation, no pytestcache/bytecode; all test products removed. PublicCLI created no publicationregistry; processenvironment unchanged; inputbytes unchanged. Providercalls0, modelcalls0, newcostUSD0. Canonicalcustomer directories are not dependencies or write targets.

Exactcommands are in red/green receipts and the reproducible `run_checks.py`/`public_cli.py` drivers. Pythonstdout/stderr were captured into the recorded logartifact bytes; hashes below bind those exact artifacts. No test was skipped or loosened. Sources stable; this agent now stops writes.

## Changedfile SHA256

| File | WorkingbyteSHA256 |
|---|---|
| `scripts/research_support_diagnostics.py` | `dd09b7088c691205950413adafaf9604e303966c6aada7c344d63486dec12902` |
| `tests/test_research_support_diagnostics.py` | `af2a5c81895b1ec1b450a553331852261eba9d2f908ec99959bc3d31b801e12f` |

## Evidence index

| File | SHA256 |
|---|---|
| `before.json` | `aa3a74ed2e13ee97f027a191a1f41ed2b35825363dc594c5a28292026b847a45` |
| `red.json` | `edbf5b7c91d866413d0249a94d10fc8e76293ec64cb6d0c5747f651a0293b462` |
| `red.log` | `4d37815a340a0d9a42948e6d6e82d7ce895cb5c4777998c9233d80abd051e273` |
| `green.json` | `022c44c1d26d3bd4a0cb96f7556933441b46db9c0ddf5181bdb94ffbd31672e6` |
| `responsibility.log` | `3fbab63c58bd88107d1ee8d9fa2594a517cc425ec094b59b66658c7be1a016b1` |
| `ruff.log` | `82b3e6a6c090a57601d22943bd23fca9218d1031dbe5a7b754092f9a156b4f18` |
| `mypy.log` | `5d4b6d285b77932e3d08212c3b4974d0a803f98ec60408ac6ccf6a063fa6c19e` |
| `public_cli.py` | `347ead181ac835965914f01f4578fe227d0a2527ed5603b026c5dc9bdc7fc7ce` |
| `public-cli.log` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `public-cli-receipt.json` | `fc56a750e567847523fbe74b5e8ee87664a42402021f84eb20f9edc86da194a9` |
| `protected-after.json` | `13ec68e75a273068dcc6ee5be5385f61b4948e1199803d99563727073da09d4f` |
| `implementation.diff` | `1511f8b2855eb8eb8ec9dd4bdbb7de54887b76a5ff696bfa28e83c0cccf31ea0` |
| `run_checks.py` | `07648a4001deab5dcdbfc186536e0307d894be6a77d90ee6dc41a7bb82461fac` |

## MAIN continuation

ROOT performs independent focused replay of the original saved sharedroot counterexample, then normalcommit/ff/push and scopedinstallation. No new broad test/approval gate is required. R16/R17/R18/W09 remainopen; a structurally supported cell is not a completed economicresearch or accuratebuy-side forecast. Machine-readable handoff: `handoff.json`.
