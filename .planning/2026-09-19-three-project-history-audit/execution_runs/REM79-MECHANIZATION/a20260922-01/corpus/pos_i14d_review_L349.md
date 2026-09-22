<!-- REM79 corpus POSITIVE-1 (historical FALSE case): I-14-D review.md line 349, r6-era bytes; F-REV-R6-02 site 1; frozen expectation: FLAG line 4 -->
<!-- src: execution_runs/I-14-D/a20260919-01/review.md line 349 (1-based), extracted verbatim at corpus build; source file sha256 recorded in evidence/corpus_manifest.json -->

| `F-REV-R5-01` (MEDIUM) | **fixed**: the pre-break token is now `[^\s]+` — any non-whitespace run. The r5 class was a swap that re-opened `&`, `'` and `|`; `[^\s]+` closes every character r4 or r5 closed and every character either leaked, except the space (which is the registered OPEN shape) | `observability.py:329` |
