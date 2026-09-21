# I-14-F decision — product-side short-basetemp convention

Authorization: OWNER_DECISIONS.md §13 T1-7 item ③ (from I-14-C r5 §19-③) — "深层 cwd 的
WinError 206 —— 授权在产品侧改为短路径 basetemp 约定". The owner decision (convention,
product-side, not cwd-shortening, not global pytest loosening) is already made; this file
records the implementation design that fulfils it.

## Chosen design

A root `conftest.py` in the product tree (company-wiki) owns the convention:

1. **Criterion (judgable, pure function).** Let `cwd` be the pytest process cwd and
   `basetemp` the explicit `--basetemp` option (absent ⇒ pytest's own default, which derives
   from `%TEMP%\pytest-of-<user>` and is short; nothing to do). Resolve
   `effective = basetemp` if absolute else `cwd\basetemp` — the cwd enters exactly through
   resolution, which is where a deep cwd makes a relative basetemp deadly. Relocate iff
   `len(effective) + GENERATION_RESERVE > WIN32_PATH_LIMIT`, i.e. `len > 116`.
   Constants (recalibrated on attempt evidence, oracle Addendum B):
   `WIN32_PATH_LIMIT = 240` — the longest generated artifact passed at ~200 total and failed
   at 253 total (literal WinError 206, basetemp 155) and 278 (dead launcher spawns, basetemp
   156); 240 sits conservatively below the failure band.
   `GENERATION_RESERVE = 124` — the longest suffix the suite builds under basetemp: the
   launcher's redirect log `\.source_catalog\worker_stdout-<32hex>-attempt-0001.log` (79)
   below `\fake-project` (13) below the pytest test dir (31) + separators.
   Superseded first guess (260 classic MAX_PATH / reserve 100 / threshold 160) was falsified:
   it let basetemp 155/156 through unrouted and both placements failed on path grounds.
2. **Fallback target.** `%TEMP%\cw-pytest-basetemp\<UTCstamp>-<8hex>`: fresh empty dir,
   created per relocating session, owned by that session. Never an attempt/evidence root,
   never reused — same discipline as START_HERE's `--basetemp` rule.
3. **Mechanism.** In `pytest_configure` (root conftest hookimpls run before the builtin
   `tmpdir` plugin reads `basetemp` — LIFO registration order), rewrite
   `config.option.basetemp` to the fallback and print a `CW-BASETEMP-DECISION {...}` JSON
   line (requested/effective lengths, relocated, reason) so every run carries its own
   machine-readable evidence.
4. **Cleanup.** `pytest_unconfigure` rmtree's the created fallback dir and prints
   `CW-BASETEMP-CLEANUP ...`. Only the dir this session created is removed; a failed session
   still cleans up (unconfigure always runs).
5. **Opt-out for A/B testing.** `CW_SHORT_BASETEMP_DISABLE=1` disables relocation (decision
   line still printed, `reason=disabled`) — used for the mutation proof.
6. **Associated tests.** `tests/contract/test_short_basetemp_convention.py` unit-tests the
   criterion table, the constant coherence (160 = 260−100), fresh-and-unique fallback dirs,
   and the disabled branch. The two real nodes are the integration cases.

## Rejected alternatives

1. **Shorten cwd instead** — the card forbids it; it bypasses the product defect.
2. **Loosen global pytest config** (e.g. delete `--strict-markers`, set `asyncio_mode`, or
   add `addopts` overrides in pytest.ini) — forbidden; the convention must not change what
   normal runs assert. The hook only rewrites the basetemp option when the criterion fires.
3. **Always relocate basetemp to %TEMP%** — would mask genuine deep-path defects at normal
   depth (card negative case: "正常深度的 cwd 不得被无谓地改道"). Rejected.
4. **Hardcode a cwd-length threshold (relocate when cwd > N)** — cwd length alone is not the
   failure variable: a deep cwd with a short absolute basetemp passes (proven by this card's
   GREEN-deep runs). Only resolved basetemp depth predicts the generated path depth.
5. **Set `长短路径` conversion via `GetShortPathName`/`\\?\` prefixes in the product launcher**
   — touches production runtime code for a test-infrastructure problem, far outside this
   card's allowlist; the launcher contract (quoted paths, logon wrapper) would need its own
   cross-consumer review.

## Compatibility impact

Additive only: two new files in the tree (`conftest.py`, `tests/contract/test_short_basetemp_convention.py`).
No existing file changes; no pytest.ini change; no product module change. Sessions that pass
a short basetemp (including every existing audit discipline command) are byte-for-byte
unaffected except for one extra `CW-BASETEMP-DECISION` stdout line.

## Recovery rule

Delete the two added files (inverse of `changes.diff`). Deep-cwd behaviour returns to the
frozen RED state; the RED evidence and the historical 166/167 vs 74/75 datapoints remain.
