# BINDING — I-08-B-14FILE / a20260923-01

## 0. Identity & lineage

| field | value |
|---|---|
| card | I-08-B-14FILE (authorization-execution card, 14-file face) |
| attempt | a20260923-01 · plan `2026-09-19-three-project-history-audit` |
| parent | session-bfecd191-fbc3-4a66-8ed1-6562479bf102 |
| executes | I-08-B `a20260919-01` handoff.next_action ("Apply the SAME 14 files … from a card authorised to write it"), routed by RF-STEP9-TRIAGE finding #2 / handoff receipt ① |
| carrier status | `accepted_scoped` (round-4 independent verdict, technical + delivery surface) — this card CARRIES that state; it grants nothing further and closes nothing |
| oracle | `oracle.md` frozen 2026-09-23 before any run of this card |
| product tree | `C:\Users\郑曾波\Projects\revenue-forecast` = **READ-ONLY**; delivery = `changes.diff` only |
| write roots | this attempt dir + `%TEMP%\i08b14file\a20260923-01\**` (scratch trees) |
| forbidden | any RF write; any git command; network; test key into `config/` or any schema-validated document; hand-edited golden values |

## 1. Interpreter / environment (every run)

- `C:\Miniconda\python.exe` = **3.13.9 (Anaconda, MSC v.1929 64 bit)**, pytest **9.1.1**, cryptography **50.0.1** — same stack the carrier bound.
- `PYTHONDONTWRITEBYTECODE=1`, `PYTHONIOENCODING=utf-8`; `REVENUE_ATTESTATION_PROVIDER`/`REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS`/`REVENUE_ATTESTATION_PROVIDER_ARGV` cleared before every suite; `tests/conftest.py` redirects `REVENUE_PUBLICATION_REGISTRY` to `--basetemp` (all basetemps under the attempt's `%TEMP%` root) → **zero registry/artifact writes into RF**.
- Scratch trees (all under `%TEMP%\i08b14file\a20260923-01\`): `before_tree` (robocopy of RF, excl. `.git .planning` caches), `after_tree` (= before + the authorized 14), `mut_test` `mut_prod` `mut_guard` `mut_golden` (after_tree + one mutation each), `compat_tree` (after_tree + TRIAGE diff).

## 2. The 14 files — before/after pins (all measured this session)

| # | file | before (live RF, close-verified) | after (authorized = carrier iso bytes) | note |
|---|---|---|---|---|
| 1 | scripts/contracts/constants.py | 278e3e02df15e556f4851b46711a2f36aac5b7e6a9820c27e0ca31b02858d0ae | a299e95055f22f3d79967e2fdab0522120a9011d6bd9fda213b000904a7f2564 | = carrier patch base |
| 2 | scripts/contracts/evidence.py | 054e364a7a5c428f43c6378f795429751b26f24af8de07e22da4b3d0ac8a4561 | 4b422cd431c117047b7452cce9c756e9f8719c99c65b2b395c021f3da54af807 | = carrier patch base (carrier `source_hashes` older value bc5e4c53 noted in oracle §1) |
| 3 | scripts/publication_registry.py | 29aaae4f9864d9c4dbb92720744daa49315a2980dfa158b0e3666cb86d886344 | 172092e067f0e830e2e9c887b274b4560c7c4b300c5ac5088e7ff98920cda003 | = carrier patch base |
| 4 | scripts/revenue_core.py | **8a761498f5eb729e4f4227f2a315d709253f8b96acf7baa7253ab425e73ac883 (DRIFT vs carrier base 1821fd2a… = B1 ec307d20)** | aec1cf69a386b779a5b339e56a106062ceffa401152839d00153d99ba3e9d12f | supersession face — decision §3 |
| 5 | scripts/revenue_publication.py | **bc2bb4a33e36ed9ad82bc4ffe33e57de8999002c2c7910b9c8b9d1565678fcd0 (DRIFT vs carrier base 183803bb… = B1 ec307d20)** | e311b2bb5079e1a211c8ae7e35ad716fce0b0c8c6208f5e0a24cdfdf3da50aba | supersession face — decision §3 |
| 6 | scripts/trust_anchor.py | 9abdcec55a524574b55e0111f513338f79a486f536985d036b94b4a71ba1310c | a6049b580182ee99b6e02cb501562af2239c89ffa115a0aca6b1cd332bf9151f | = carrier patch base |
| 7 | tests/test_attestation.py | d1b7cf036b22867d62e235002e1d1736586ec45a2f888e84896504b7b7915404 | 17934e28a894ff1d3d95cb14d1665fb3ba27f7e6c587d916f2cdd4d2f547f5c4 | **the false-green rewrite (finding #2)** |
| 8 | tests/test_single_owner_guard.py | ae6f158c8a4b421e0393a5c7fcf3cab2ebce40b3d50a20e852cc73b2c5e26c2d | b5969ba6397fbe2d37f3000bf0ca301f505bfd056ee7cbbe9ba9b8f691774a65 | CONFLICT-1 hardening; **TRIAGE-overlap file** — decision §4 |
| 9 | tests/golden_behavior_hashes.json | 4e68b98cc16027bc370900e346f8554245e2e2155d0e22edc4beadba5f2933b5 | c6b13adabefac751e3f494cb229041f828f92ef59d782744b3b555ef8fda0c54 | carrier refresh passed as-is (R8) — no re-refresh needed |
| 10 | scripts/attestation_protocol.py | ABSENT | 6e58cde211bbf53557c89bcb1db31bcb77bdad5f678a1725520ebc1565b28db4 | added |
| 11 | tests/test_attestation_provider_protocol.py | ABSENT | 8e535d805cd1d09b75bfd31954e2c98ef56c0fbfdfc737d83df4619f40be6ddb | added |
| 12 | tests/test_attestation_legacy.py | ABSENT | 729d49cbf4bfb72fcb00b948c16fa699a48069efe96104282444836a243797ae | added |
| 13 | tests/test_publication_attestation_contract.py | ABSENT | 306407ec2f2b0ffa2220ab7518624051e6a31b7559b56541d1a46e97c51306a2 | added |
| 14 | tests/e2e_support/i08b_fake_provider.py | ABSENT | e715ca8a34c3fc817a1a06cf9f961118a6f515afe35bdaaff94ea0548bd6d92a | added |

- After-shas = **carrier** `binding.json.post_run_measurements.artifact_hashes`, independently re-measured from `iso/rf` before execution (14/14 matched) and re-verified in `after_tree` (hash table printed during build + `c1_gen_diff.txt`).
- Before-shas re-measured at CLOSE on the live RF tree: `evidence/c4_rf_close_hashes.txt` — identical to open → **RF write count = 0** (the 5 added paths ABSENT in RF, 9 edited unchanged). RF `.pytest_cache\v\cache\nodeids` mtime `20:37:58` (before this card's window 23:12–24:0x) → no test ever ran inside RF.

## 3. changes.diff (delivery artifact)

| field | value |
|---|---|
| path | `changes.diff` (this attempt) |
| generator | `scratch/gen_diff.py` (no git): walk before_tree/after_tree (excl. caches/pyc) + unified diff per file |
| files | **14** (9 edited + 5 added); `extras=[]`, `missing=[]` — generator exits 2 on any path outside the authorized 14 |
| bytes | 321042 |
| sha256 | `9721711a214c4dc7745dc960bf0be6280d86f25c8fe750376c9c9daf4a50bb66` |
| regeneration | re-run AFTER every test/mutation/compat run (`c5_gen_diff_rerun.txt`): **byte-identical** → no run mutated the after-state |
| round-trip | `scratch/apply_diff.py verify` → **14/14 `roundtrip_equal=true`** (`c2_changes_diff_roundtrip.txt`): applying the diff to before_tree reproduces after_tree **byte-for-byte**, i.e. exactly the carrier after-shas (stronger than the carrier's own diff, whose byte-level reproduction failed on CRLF/LF — carrier oracle §8.7) |
| line endings | hunks carry the trees' own EOLs (RF worktree files measured LF for tests/, mixed elsewhere); the diff is byte-faithful, no EOL normalization is performed by the generator |

## 4. Cross-card pins (volatile during this window — re-pin at merge)

| artifact | observed pins |
|---|---|
| RF-STEP9-TRIAGE `changes.diff` | **5423 B** (first listing ≈23:05) → **11184 B mtime 23:46:39** (grew: appended an 8th section `tests/test_single_owner_guard.py` = owner-ruled #8) → **11212 B mtime 23:54:56 sha256 `d476c40899d1f2090849af912ccbeea5fe1e2a808587e1174e6ab9606848be45`** (mutation_patrol section edited between 23:49 and 23:56; guard section edited again before 24:05) |
| sections used by compat arm | receipt_attacks/fc1102/fc1302 applied ≈23:49; zr601/zr708/daily_t2/mutation_patrol applied ≈23:57 = **current** patrol (`R10b` re-run green against it); guard excluded (conflict, both observed versions context-miss) |
| sections equality check | `receipt_attacks, fc1102, fc1302, zr601, zr708, daily_t2` byte-identical across observed versions; `mutation_patrol` and `single_owner_guard` changed during the window (printed table in session log; guard/patrol claims pinned explicitly above) |
| B1 promotion commit | `ec307d20` (source of the only 2-file base drift, decision §3) |
| REST-B a20260923-01 | helper-split of revenue_core.py (CC 23→6) / revenue_publication.py (16→5) against **8a761498/bc2bb4a3** — diff base conflict pre-registered in decision §5 (parent ruling, delivered mid-run) |

## 5. Results summary (raw under evidence/)

| leg | run | rc | result |
|---|---|---|---|
| R1 RED F1 | before, `tests/test_attestation.py` | 1 | **1 failed / 6 passed** — exactly `test_configured_provider_means_host_signed_publication`, `AssertionError: False is not true` |
| R4 RED F2 | before, `tests/test_single_owner_guard.py` | 1 | **1 failed / 2 passed** — `revenue_core.py imports subprocess (second download owner)` |
| R7 RED F3 | after-13-files, golden lock | 1 | **1 failed** — `volume output hash changed` |
| R0 sanity | before, golden lock | 0 | 1 passed (golden was green pre-landing) |
| R2 GREEN F1 | after, 4 attestation test files | 0 | **118 passed + 34 subtests, 0 failed** (296 s, loaded box) |
| R5 GREEN F2 | after, guard | 0 | **5 passed** (3 original + 2 carrier AST hardening nodes) |
| R8 GREEN F3 | after (14/14) | 0 | **1 passed in 21.40 s** — carrier golden values valid as-is |
| R3 MUTATION F1a | mut_test (original test restored) | 1 | **4 failed / 3 passed** — includes the false-green node (RED returns) + 3 enumerated L2 schema-drift nodes |
| R3b MUTATION F1b | mut_prod (files 4+5 reverted to live bytes) | 1 | **9 failed / 9 passed** — includes `test_provider_handshake_means_host_signed_publication` + all 8 reverse cases (rewrite is load-bearing on the landing) |
| R6 MUTATION F2 | mut_guard (original guard) | 1 | **1 failed / 2 passed** — guard fires on `attestation_protocol.py` subprocess (RED returns) |
| R9 MUTATION F3 | mut_golden (original golden) | 1 | **1 failed** (refresh load-bearing) |
| R11 census before | curated 15 files | 1 | **8 failed / 122 passed** |
| R11 census after | same 15 files | 1 | **4 failed / 139 passed** — after ⊂ before, **0 new failures**; removed: F1 node, F2 node, receipt_attacks #1, zr1102 c4 |
| R10 compat | after14 + TRIAGE7 | 1 | **33 passed / 1 failed** — only `zr1102::test_c1_no_orphaned_script_without_main` (pre-existing both arms; its `git grep` needs `.git`, absent in scratch = symmetric env artifact) |
| R10b compat re-run | current TRIAGE patrol section | 1 | **8 passed / 1 failed** (same pre-existing c1) — H2 green vs final TRIAGE pin |
| R12 ratchet c3 | before / after | 1 / 1 | RED in both arms — pre-existing (REST-B domain) AND carrier content over ≤6/≤10 → **交合并批步骤2** (parent ruling), no in-card change |

Counts: **RED 3/3 matched frozen expectations · GREEN 3/3 · MUTATION 4/4** (F1 has two legs) · census 0 new failures · compat 2 green targets (H1, H2) + H3/H4 green.

## 6. Process incidents (disclosed, all recovered)

1. First pytest attempt errored (basetemp parent missing) → re-ran after `New-Item`; raws overwritten by the valid run.
2. Tracebacks initially displayed RF paths while running in before_tree → cause: **copied stale `.pyc`** carrying RF `co_filename`; purged all `__pycache__` from scratch trees; before/after trees byte-verified by hash anyway.
3. One foreground call (R8+R2+R5) hit the 120 s tool timeout: R8 completed (rc0, raw kept), R2 was killed mid-run (0-byte file) → R2 re-run in background job pwsh-203 → 118 passed; stray-process check found no orphans of this card (surviving pythons belonged to concurrent sessions).
4. Evidence written by `*>` came out UTF-16 → re-encoded to UTF-8; subsequent runs use `| Out-File -Encoding utf8`.
5. `apply_diff.verify` first failed on universal-newline reading of the diff → fixed (`newline=""`), re-run 14/14 green.
6. First compat apply aborted at the forbidden guard path **after** writing sections 1–3 (partial-write bug: forbid checked per-section inside the loop) → detected, sections 4–8 applied individually; final compat state fully accounted (c3/c3b/c3e recorded as superseded steps, c3d/c3f/c3h = authoritative).
