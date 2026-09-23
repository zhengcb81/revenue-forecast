# BINDING — pins, extracted step commands, environment (post-oracle, pre-execution)

## Repo pins (read-only git allowed; no mutations)

| item | value |
|---|---|
| CW root | `C:\Users\郑曾波\Projects\company-wiki` |
| HEAD | `bf0c8b27e83c3ee7e533c6031fefad8e27e5e121` (bf0c8b2) |
| origin/master | `f39bd5a64224cd0c7aa098f23f64bf3811fa8939` (f39bd5a) |
| ahead/behind | `0 3` — fcap ahead 3 (ac4ebd0, 5d72529, bf0c8b2), 0 behind |
| branch | `fcap` (parent pushes `git push origin fcap:master`) |
| dirty worktree (pre-existing, NOT mine, NOT in changes.diff) | ` M CLAUDE.md`, ` M README.md`, ` M src/company_wiki/source_catalog/artifact_dag.py` |

## File pins BEFORE (sha256 / bytes)

| file | sha256 | bytes |
|---|---|---|
| `tools/pre_push_gate.py` | `28338622cc3bfbd0dd3d98547844dc3500c2ec9a5fe656faed641c7b8743edc3` | 4434 |
| `src/company_wiki/source_catalog/archive_retired_evidence.py` | `bbe855e4495e82d2a40b0185c9db8efa2639449fdd5f768120538abb992b28ac` | 9894 |
| `tests/contract/test_fc1204_complexity_ratchet.py` (frozen table `"archive_retired_evidence.py": 7`) | `bcd01361e3025f99a78d8db8452116d05d81de685a4895d7b6ff34d7e93bb3f2` | 4866 |
| `tests/contract/test_fc1204_coverage_ratchet.py` (coverage floor 95 for the archive file) | `fa0001209bb43bf49e63ca9b9d9463485e6f35b1b8accb69d0e7f78defe31c85` | 5786 |

## Complexity BEFORE (measured with the ratchet test's OWN `_mccabe`/`_max_complexity` AST logic, on the pinned CW file)

| function | CC before | frozen bound |
|---|---|---|
| `_row_digest` | 1 | 7 |
| `_sha256_file` | 3 | 7 |
| `_atomic_write_text` | 2 | 7 |
| `_publish` | 4 | 7 |
| `_fsync_file` | 2 | 7 |
| `_verify_snapshot` | 5 | 7 |
| **`archive_retired_evidence`** | **19** | **7 → RED 19>7 (RC-2)** |
| file max | **19** | 7 |

## Gate step list EXTRACTED from `tools/pre_push_gate.py` (full, default invocation — no `--skip-contract`)

Cwd = project root (iso harness), `PYTHONPATH=<root>/src`, child interpreter = the
interpreter running the gate (`sys.executable`), label printed as `=== <label> ===`:

1. `ruff check src tests/unit tests/contract scripts` — label `ruff (CI WU-1.2 full scope)`
2. `<py> -m compileall -q src scripts tests` — label `compileall`
3. `<py> scripts/config_doctor.py` — label `config_doctor (CI WU-7.1)`
4. `<py> -m pytest tests/contract/test_fc1204_complexity_ratchet.py -q` — label `FC-1204 complexity ratchet (CI meta-gate)`
5. `<py> scripts/host_assumption_guard.py` — label `host assumption guard (FC-1307-a; the class that broke CI in F-B01-9)`
6. `<py> -m pytest -q --timeout=180 tests/contract/test_source_catalog_section_extractor.py tests/contract/test_fc906a_producer_binding_metadata.py tests/contract/test_legacy_observation.py tests/contract/test_zr506_section_chunk_fact.py tests/unit/test_writer_freeze.py tests/contract/test_fc1307_host_assumption_gate.py` — label `contract tests (extractor + binding + observation + chunk) + meta gates`

Gate semantics: runs steps in order, STOPS at first rc≠0, exits with that rc
(`_run` returns `proc.returncode` unchanged — must stay that way after the RC-1 fix).
`main(--skip-contract)` drops step 6 only (NOT used for full discovery).

## Environment (iso harness runs)

| item | value |
|---|---|
| `python` (PATH) | `C:\Miniconda\python.exe` — 3.13.9 (Anaconda MSC v.1929 64-bit) — **primary**, matches push protocol `python tools/pre_push_gate.py` |
| alt interpreter | `<CW>\.venv\Scripts\python.exe` — 3.14.2, pytest 9.1.1, pytest-timeout OK, NO ruff module (step 1 uses PATH `ruff` anyway) — fallback if a step proves interpreter-sensitive |
| `ruff` (PATH) | `C:\Miniconda\Scripts\ruff.exe` — 0.15.18 |
| pytest | 9.1.1; plugins: pytest-timeout OK, pytest-asyncio 1.3.0 (`asyncio_mode=auto` in pytest.ini) |
| pyyaml / fitz (pymupdf) | import OK |
| CW `.venv` | present (3.14.2) — pycache shows both 3.13 and 3.14 have run this suite |

## Iso harness layout (scratch, %TEMP%, short path for Win32 path budget)

- `ISO = %TEMP%\cwgu1\repo` — targeted copy: `src` (6.2 MB/438 f), `tests` (28.9 MB/1445 f),
  `scripts` (4.5 MB/320 f), `config` (0.5 MB/30 f), `tools` (45 KB/8 f),
  `.source_catalog/security_master/*` (existence/glob dependency of step 3 — full
  `.source_catalog` is 102 GB and NOT copied; the doctor only checks
  `catalog_dir.is_dir()` + `security_master/*.json` non-empty + config shape), root
  `conftest.py`, `pytest.ini`, `pyproject.toml`. Caches (`__pycache__`, `.pytest_cache`,
  `.ruff_cache`, `.mypy_cache`) excluded. `.git` NOT copied (1.1 GB; no gate step or the
  6 contract tests invokes git — verified by grep; `git init` in scratch is the documented
  fallback if a step unexpectedly needs a repo).
- CW working tree = 133.4 GB / 58 064 files — full copy impossible; targeted copy is the
  only viable iso strategy; iso copies are sha-verified against the pins above before RED.
- `DIFF = <attempt>\changes.diff`; `VERIFY = %TEMP%\cwgu1\verify` (fresh copy of the two
  original files + `git init` scratch repo used ONLY for `git apply --check` +
  byte-identity proof of the diff — no CW/RF/FF git mutation).

## Iso-fidelity risks recorded

1. Step 3 sees a stubbed-but-present `.source_catalog/security_master` (content not
   validated beyond glob non-empty). CW real state: 3 files present → parent's live run
   already passed step 3 (gate reached step 4) — iso/verdict expected identical OK.
2. Contract tests build tmp catalogs under pytest basetemp only (grep-verified: every
   fixture uses `tmp_path`/`project`); no production-dir reads.
3. Interpreter: primary = Miniconda 3.13.9; if a step fails, re-run under `.venv` 3.14.2
   before declaring a blocker (interpreter-sensitivity check).

## Test-family pins for RC-2 GREEN (every test naming `archive_retired_evidence`)

- `tests/contract/test_source_catalog_archive_retired.py` (functional: 2 direct calls) — the file's OWN tests
- `tests/contract/test_fc1204_complexity_ratchet.py` (frozen table entry)
- `tests/contract/test_fc1204_coverage_ratchet.py` (coverage floor 95; in-suite it
  SKIPS unless `FC1204_COVERAGE_GATE=1` + `coverage.json` present — expected skip)
- gate references: none (`pre_push_gate` referenced by no test — grep = only self) →
  RC-1 fix has no direct test consumer; writer-freeze meta gate only cares about
  `scripts/*.py` CLIs (tools/ unaffected; no new script added).
