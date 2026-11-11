# Independent review: RF compare adapter

Reviewer: independent read-only reviewer. Scope: `scripts/report_catalog_compare.py`, `scripts/report_catalog_compare_cli.py`, `tests/test_report_catalog_compare.py`.

## Findings and disposition

- Main compare path reads exact report and run through `ReportCatalog.get_report/get_run`; it does not open CWP private storage or scan artifact directories.
- Entity, listing, analysis subject, exact run/report identity, period, unit, currency, scale, basis, scenario and actual/forecast are aligned before a delta is emitted. Missing values remain explicit; legacy reports do not generate deltas; Decimal arithmetic avoids float rounding.
- The candidate's fixed `MAX_COMPARED_ROWS=512` and `MAX_OUTPUT_BYTES=1MiB` had no configured-work-budget basis and rejected valid complete owner results. Both were removed. New synthetic tests return every one of 600 periods and a complete CLI response larger than 1MiB; each row retains both source locators.
- `MAX_METRICS=32` was redundant because only revenue is currently supported and duplicate IDs are rejected; removed. The 64KiB request bound remains a resource guard; valid request fields and values are bounded to far less than that size.
- Reviewer suggested asserting the complete period sequence and both locators on every row. Those assertions were added and the focused suite rerun.

## Result

PASS for the three-file compare slice, after correction. Final focused result: 52 passed, 1 environment-dependent skip. Ruff and mypy passed. Earlier combined regression, before the large-result change, was 102 passed, 1 skip; it is recorded as supporting evidence, not as the final post-change result. The remaining skip depends on a Dashboard contract checkout not present in this environment.

The long locators are synthetic public DTO serialization fixtures; current native ReportCatalog metric projection may expose a null locator. This test proves the transport does not discard long evidence fields, not that a production report currently contains such locators.

Scope remains partial: B37 scope binding, subject resolution, verified comparison and publication-source contracts are not part of this commit. Do not mark the complete MB-RF card done.
