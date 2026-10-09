# Source clock implementation handoff

Status: **IMPLEMENTED_AND_LOCALLY_VERIFIED**; MAIN integration and actual fresh research/full71 are separate and NOT RUN here.

- Worktree: `C:/Users/郑曾波/Projects/_harness_worktrees/cmrf-20261008/rf-inputs`.
- Branch: `codex/source-clock-20261009`; base e688b0a2.
- Implementation commit: **a001995a26a6b9b1a294ae62bb4fe57eeac6ca51**. This final handoff/PWF update is a separate normal docs commit.
- Engine4.1.1/source-clock/1; schemas3.7/3.8 unchanged. See INTERFACE for exact defaults, opt-in2.2 and old emit/runtime matrix.

## Evidence

| Responsibility | Actual result / file |
| --- | --- |
| Initial 18 clock cases | true RED16FAIL/2PASS; `red.xml` |
| Clock + declared capability | 20PASS/0.43s; `green.xml` (additional capability2RED first) |
| Remaining caller deadline | true RED5FAIL/1PASS; `deadline_red.xml`; related closure79PASS/2SKIP/13.15s in `deadline_green.xml` |
| Concentrated source/capture/claim/legacy/version/backtest | first188PASS/5SKIP, 4 obsolete assertions +11 missing producer setup failures; targeted repaired79PASS/2SKIP/30.15s; original/repair XML retained |
| Required offline CI/pre-push | ruff scripts/tests/tools/e2e PASS; mypy8 modules PASS; curated126PASS/18.63s; `required_gate.log` |
| Real original-three late-read | `actual_late_read.json`: CN/HK/US each one actual public CLI open, exact original SHA, published before Oct8; actual read/captureOct9; US true raw-HTML inspection claim verifiedOct9; all source/capture qualificationPASS; download/FF/provider/model0 |
| Untouched numerical/frozen compatibility | `pinned_golden_validation.json`: all5 original4.1.0 full-result hashes reproduced using e688 runtime; current4.1.1 differs only engine/publication_receipt/result_sha256; other fields exact equal; original golden JSON SHA unchanged61a4040e |

Real source node is registered-source public read → RF source/capture/claim contract, not actual FF resolve or a forecast publication. Real known-pub dates are CN2026-03-31, HK2026-04-09, MSFT2025-07-30; original retrieval remains null. Source SHA/size/ref are reported in the compact JSON. No raw content dump, original modification, model, OCR or provider call occurred. The US excerpt is explicitly a clock-inspection target, not a completed research claim.

The first local validation fixture failed its too-long excerpt and Windows TEMP cleanup because sqlite context manager does not close its connection. Initial report retained as `actual_late_read_initial.json`. Explicit close and bounded excerpt fixed the tool; exact owned TEMP path was checked before cleanup. Final temp catalog/runtime/registries removed and environment restored. Production config SHA before/after3d159a4e unchanged. Temporary DB backup is only an isolated runtime fixture, not an architectural second catalog or registry.

## Integration responsibility for MAIN

1. Integrate implementation and this final docs commit normally; do not rewrite old input/output hashes. Existing production config/registries/installation copies were untouched.
2. CWP producer dependency is ea76998c with declared public2.2 flag. Default RF2.1 known-publication route works independently. Enable2.2 explicitly only where required; if real prior provenance is missing, keep the unknown gap. Do not replace it with fabricated publication/retrieval/mtime or force a new download.
3. Current narrative wire has no prior-availability proof DTO; unknown narrative publication remains refused. This implementation did not alter that producer protocol or shared CWP owner files.
4. Preserve future information, period, source/claim/raw/hash/host checks. The caller now owns the finite remaining deadline; an exhausted or actual transport timeout is a failure with no retry/paid batch reopen. Actual long selected-OCR replay performance is MAIN's current separate node.
5. Run MAIN's actual fixed71/fresh workflow after integration. Existing HK role issue and no-OCR fixture partial result are not repaired or relabeled by this package. Unknown proof fixtures are unit tests, not actual original-three source evidence.

## Commit / hooks / scope

Normal git commits, no `--no-verify`, merge, push or installation sync. `core.hooksPath=.githooks` is configured but the isolated checkout has no hook files; commit hooks therefore did not execute. The required gate was executed explicitly and passed. No CWP/FF/Dayu code, production/config/raw/registry or MAIN PWF write. Allowed RF code boundaries, necessary release docs, responsibility tests and this standalone package only; exact implementation file list is in `handoff.json`.
