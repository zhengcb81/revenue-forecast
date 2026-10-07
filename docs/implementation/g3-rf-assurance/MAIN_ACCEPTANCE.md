# MAIN acceptance — 2026-10-07

Worker delivery: `4a936395be692c6dbf23685b89d2e4894ac73984` (implementation `e9f9405936c8b123b17592538d1bf70f76d8a6a5`). MAIN receives the branch with its complete history.

## Wiring completed

- Runtime `--version` uses the same file-name set as the distribution (tests are repository-only). This identifier describes file membership, not verification of file content; packaging still uses full SHA-256 for content checks.
- ZR-804 installed-copy tests run the real sync CLI against three `tmp_path` destinations. No home installation is read/written and no missing-installation skip is used.
- README documents default hash+size with diagnostic mtime, optional explicit strict time checks. Four runtime references identify engineering tests as repository contributor instructions.
- Existing `FF_V2_CODE_ROOT` / `CWP_V2_CODE_ROOT` provide explicit sibling code inputs for normal pre-push. No dependency check was removed or hook bypassed. Missing siblings in the worker layout were not forecast defects.

## Evidence

RED: runtime file-set comparison failed (`76b37ec851b558eb` expected vs `c58de2c159dcfcf5`).
GREEN: worker eight responsible suites + runtime file-set regression + three isolated installed-copy cases: **78 passed / 26.27s / exit 0**. Changed Python files pass Ruff.

Real user installation synchronization is not performed in this acceptance. Root RF owner assurance logs are preserved; no paid/model/download/production data calls. Scratch test paths are removed after all readers/subprocesses exit. Historical full UC baseline failures are not converted into a routine long gate.

Publishing and exact CI results are recorded by MAIN in company-wiki's selected PWF acceptance receipt, outside historical frozen inputs.
