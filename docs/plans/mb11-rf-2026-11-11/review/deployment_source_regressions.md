# Independent review: RF deployment and publication-source regressions

Reviewer: independent read-only reviewer.

## Scope

- `tests/test_report_catalog_deployment.py`
- `tests/b37_publication_sources/`
- Owner lock assertions for read-only catalog/deployment operations

## Findings

PASS. No actionable findings.

The deployment tests use isolated temporary owner roots and verify that read-only metadata and comparison operations leave catalog files unchanged. Assertions match RF's lock protocol: the lock file persists, while `OwnerFileLock.is_locked()` confirms that the OS lease is released.

The publication-source tests use synthetic data and isolated temporary roots. They cover omitted and duplicate sources, mismatched identities and hashes, changed response bytes, invalid paths, and lineage reads. No production data is modified.

## Validation evidence

- Focused deployment/compare/publication-source suite: 120 passed, 1 skipped.
- Combined MB-RF regression: 171 passed, 1 skipped in 71.41 seconds, using a short temp root to avoid Windows path-length failures.
- Final deployment-file regression after lint cleanup: 38 passed; Ruff passed.
- Tests correspond to the checked-in owner protocol; review does not cover the deferred scope/subject candidate or real StockWiki/CWP composition.
