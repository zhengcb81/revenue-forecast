# Recovery — PROMOTION-EXEC a20260922-01 (exact revert instructions per row)

Every modified production target has its byte-exact pre-promotion image under
`before_images/<row>/` inside this directory. All commands are plain copies —
no git required (and no git may be run: parent owns commits).

Run from PowerShell. `<AT>` = this attempt directory
(`...\.planning\2026-09-19-three-project-history-audit\execution_runs\PROMOTION-EXEC\a20260922-01`).

## B-1 — revert RF revenue 安全三项
```powershell
$rf = 'C:\Users\郑曾波\Projects\revenue-forecast'
Copy-Item "<AT>\recovery\before_images\B-1\revenue_core.py"         "$rf\scripts\revenue_core.py" -Force
Copy-Item "<AT>\recovery\before_images\B-1\revenue_publication.py"  "$rf\scripts\revenue_publication.py" -Force
Copy-Item "<AT>\recovery\before_images\B-1\revenue_report.py"       "$rf\scripts\revenue_report.py" -Force
```
Verify: `revenue_core.py=1821fd2a…, revenue_publication.py=183803bb…, revenue_report.py=a85fb484…`
Consequence: I-08-C 13-node suite returns to pre-promotion behaviour (RUN-B: exactly {e11,e13} red, rc 1).

## B-2 — revert RF company_wiki_source + source_preparation (revert BOTH together)
```powershell
Copy-Item "<AT>\recovery\before_images\B-2\company_wiki_source.py" "$rf\scripts\company_wiki_source.py" -Force
Copy-Item "<AT>\recovery\before_images\B-2\source_preparation.py"  "$rf\scripts\source_preparation.py" -Force
```
Verify: `company_wiki_source.py=225fecdd…, source_preparation.py=37a3eeae…`
(REM-49 comment fix leaves production again with this revert — REM-49 rides this batch by manifest constraint, so never revert only one of the two.)

## B-3 — revert CW observability.py
```powershell
$cw = 'C:\Users\郑曾波\Projects\company-wiki'
Copy-Item "<AT>\recovery\before_images\B-3\observability.py" "$cw\src\company_wiki\source_catalog\observability.py" -Force
```
Verify: `a73826aa…` (30087 B — the pre-r6 production image).

## B-4 — revert CW new files = DELETE the two created files
```powershell
Remove-Item "$cw\conftest.py" -Force
Remove-Item "$cw\tests\contract\test_short_basetemp_convention.py" -Force
```
(Both were ABSENT before this card — live-confirmed; no before-image exists because none is needed.
Do NOT delete the `tests/contract/` directory itself: it already existed.)

## B-5 — revert CW prune/archive (CODE ONLY revert; no execution ever authorized)
```powershell
Copy-Item "<AT>\recovery\before_images\B-5\prune_retired_evidence.py" "$cw\src\company_wiki\source_catalog\prune_retired_evidence.py" -Force
Copy-Item "<AT>\recovery\before_images\B-5\archive_retired_evidence.py" "$cw\src\company_wiki\source_catalog\archive_retired_evidence.py" -Force
```
Verify: `prune=2358c73b…, archive=143fef01…`

## B-6b — nothing to revert
No file was created: I-14-B's card declares no production target (BLOCKED-unresolved),
I-14-I skipped. `natural_window.py` stays ABSENT in `revenue-forecast\scripts\` and
`company-wiki\src\company_wiki\source_catalog\`.

## B-6c — ALREADY REVERTED during this run (no action needed)
The row was STOPPED: promoting `model_registry.py` turned the production focused
battery from 59-passed (pre-check control) to 31-failed. The before-image was copied
back within the same run and re-verified (59 passed rc 0).
Current production `scripts/model_registry.py = 9ec65295…` (= before-image, byte-exact).
If a future re-attempt happens, its before-image is
`before_images/B-6c/model_registry.py` and the current file already equals it.

## B-7a — not touched by this card
`tools/pre_push_gate.py` is owned by the concurrent GATE-OQ-FIX card
(before = after = `3df161a7…`, this card never wrote it). Do not revert it here.

## Protected files (must never change)
CW dirty-3 before == after: CLAUDE.md `963869fa…`, README.md `302bd10b…`,
src/company_wiki/source_catalog/artifact_dag.py `0c8b1d6d…`.
