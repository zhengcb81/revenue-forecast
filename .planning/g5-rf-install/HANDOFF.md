# HANDOFF — G5-RF-INSTALL

**Package:** `G5-RF-INSTALL` · **Branch:** `codex/g5-rf-install` ·
**Base:** `ab7a7a4434bbb4c52a5bd2a6cd6ed710d7151eee` ·
**Implementation:** `a2116ca6d5280c140b42a0d8bd2d94521ee80ccd` ·
**Delivery status:** `ready_for_main`

G3 already delivered the runtime closure, the JSON contracts and the isolated
install acceptance. This lane adds the piece G3 did not have: an **explicit,
repeatable file scope** plus a zero-write plan and an accurate partial-failure
result, so a point update can touch only the files that were actually
investigated. It does not re-do G3, does not change the closure, the forecast
or the source-evidence rules, and did not write any real installation.

## 1. What changed (write set)

| path | change |
|---|---|
| `tools/sync_installations.py` | `+588 / -44` — selective scope, plan, result, selective writer |
| `tools/tests/test_g5_selective_install.py` | new, 17 tests |
| `.planning/g5-rf-install/**` | this PWF + handoff package |

Everything else — `scripts/**`, `config/**`, `references/**`, `agents/**`,
`SKILL.md`, `CHANGELOG.md`, `.gitignore`, `tools/tests/test_sync_installations.py`,
`tools/tests/test_g3_skill_package.py`, RF hooks, CI, pre-push, owner logs,
`audit_review/**`, other repositories — is byte-identical to the base commit.

## 2. The interface

```text
--file <relative>     repeatable; restrict check / --plan / --apply to that subset
--plan                print one zero-write rf-install-plan/1 JSON value, exit 0
--json                print exactly one rf-install-result/1 JSON value on stdout
```

- `--plan` joins the existing mutually-exclusive mode group, so combining it
  with `--apply` / `--import-from` / `--print-manifest` is a usage error
  (exit 2) raised **before** anything is written.
- `--file` and `--json` are additionally rejected with `--import-from` and
  `--print-manifest`, also before any write.
- Default check, `--print-manifest`, `--apply`, `--import-from` and every
  existing public function keep their old behaviour and old positional
  signatures (locked by `test_old_public_callers_keep_their_signatures`).
- JSON modes emit exactly one value on stdout; every diagnostic and every
  usage error goes to stderr. The plan itself is always JSON.

### Exit codes

| situation | code |
|---|---|
| usage / validation error (bad `--file`, bad flag combination, escaping link) | 2 |
| check or apply with `remaining_selected_drift == 0` | 0 |
| check or apply with `remaining_selected_drift > 0` | 1 |
| `--plan` produced successfully | 0 (the JSON carries the operations; a plan is machine fact, not a gate) |

Unselected drift is reported as a `NOTE` line / `remaining_unselected_drift`
and **can never fail** a completed selected sync. A clean subset prints
`MATCH <dest>: N selected files` — never the whole-runtime `MATCH`.

## 3. Scope rules

`--file` values are validated against `installable_files(canonical)` as a whole
set, before any destination is opened:

- normalized (`\` → `/`, leading `./` stripped), de-duplicated, sorted;
- absolute paths, `..`, directory names and anything outside the runtime
  closure are rejected with exit 2 and **zero writes at every destination**;
- a symlink / reparse point on any component that leaves the installation
  target is rejected the same way (`_target_file` resolves each component with
  `os.path.realpath` and checks containment).

## 4. Apply semantics

- Only files whose bytes differ are staged and replaced. Identical bytes keep
  mtime, size and content — no staging copy, no `os.replace` (asserted with an
  `os.replace` spy *and* an mtime snapshot, never a sleep).
- Each replacement is one atomic `os.replace` of a
  `<name>.<pid>.syncing` sibling, inside this invocation's own
  `.<skill>-stage-<random>/` directory under `destination`.
- Immediately before every swap the canonical source **and** the installed
  target are re-hashed; a difference on either side is reported as
  `reason="conflict"` and the file is left alone. A stale plan never
  overwrites a newer user edit.
- Failure is per-file: the run continues, returns exit 1, and reports
  `written` / `unchanged` / `failed` (with `reason` and `detail`) /
  `conflicts` / `remaining_selected_drift` / `remaining_unselected_drift` /
  `status = completed | partial | failed`. No whole-batch rollback is claimed,
  no backup set and no second transaction store exist.
- Only this invocation's own stage directory and `.syncing` files are removed;
  no glob ever deletes another process's temporary files.
- Re-running the same command against the current differences converges on the
  remainder: files already written are not touched again.

## 5. Live installation facts (read-only)

Measured with zero writes; `install_delta.json` holds the per-file evidence for
the card's 8 files × 3 targets = 24 candidates.

- `~/.claude/skills/revenue-forecast` is a symlink to
  `~/.agents/skills/revenue-forecast`; three configured roots = two physical trees.
- The card's **8** reproduces exactly when `--canonical` is the original
  repository working tree (`unselected_drift = 0`). From this G5 worktree the
  same read-only check reports **12**; against the raw git blob, **13**.
  The extra entries are identical content with a different line-ending byte
  state. Real content drift is **6** files under every canonical.
- **The live update list was not widened.** `install_delta.json` still carries
  exactly the card's 8 files, and the 8/12/13 counts are recorded as facts.

## 6. Tests

RED (production code restored from `git show HEAD:tools/sync_installations.py`,
behavioural probe, 0.50 s, exit 0):

```text
FAIL | RED1 cli --file two-file selection        | returncode=2 ... unrecognized arguments: --file ...
FAIL | RED2 repeat sync leaves identical bytes   | SKILL.md mtime_ns 1791401759673495700 -> 1791406759673495800
FAIL | RED3 rf-install-result/1 on failure       | returncode=2 stdout='' payload=<JSONDecodeError>
PASS | GREEN temp hygiene already correct        | raised=True residue=[]
SUMMARY 1 / 4
```

The temp-hygiene item was already correct in the previous tool (its
`finally: temporary.unlink(missing_ok=True)` plus `TemporaryDirectory`); it is
recorded as **existing GREEN**, not re-faked as RED. An earlier direct pytest
RED run of the same three behaviours, before any production line changed,
reported `3 failed, 1 passed in 1.89s`.

GREEN — one centralized node (scratch root `.planning/test-tmp/g5-install`,
absent beforehand, restored to absent afterwards):

```bash
python -B -m pytest -q -p no:cacheprovider --basetemp=.planning/test-tmp/g5-install \
  tools/tests/test_sync_installations.py tools/tests/test_g3_skill_package.py \
  tools/tests/test_g5_selective_install.py
```
→ **33 passed / exit 0 / 17.13 s / 0 skipped**

Related counter-examples and static checks:

| node | exit | elapsed | result |
|---|---|---|---|
| `pytest -q tests/test_zr804_platform_shape.py::test_installed_copy_executes_with_canonical_identity` | 0 | 10.99 s | 3 passed (pre-existing GBK warnings) |
| `pytest -q tests/test_fc1004_platform.py::test_install_sync_gate_detects_drift` | 0 | 7.13 s | 1 passed (pre-existing GBK warnings) |
| `ruff check` (the four owned/adjacent files) | 0 | 0.05 s | All checks passed |
| `python tools/host_assumption_guard.py --roots tests tools scripts e2e` | 0 | 1.33 s | 39 violations, **0 new** |
| pre-commit hook (ruff, mypy-contract, host-assumption-guard) | 0 | — | Passed / Skipped / Passed |

Replacement boundaries (what the tests substitute rather than prove):

- the controlled failure is a **directory occupying an installed package path**
  (`os.replace(file → directory)` fails on Windows and on POSIX); a read-only
  file would only fail on Windows and would be a host assumption;
- the identical-bytes assertion combines a forced stale mtime with an
  `os.replace` spy, never a sleep;
- the escaping-link rejection creates a real link (`os.symlink`, falling back
  to an unprivileged `mklink /J`) and **skips with an explicit `pytest.skip`**
  if the host forbids links;
- E2E roots are three `tmp_path` installations built from a **`git archive`
  export of HEAD**, then given a **synthetic** marker on the card's 8 files plus
  one deliberately unselected file. This is synthetic drift — it does **not**
  mean any real installation has been updated.

No external network request was made by any node (`external_network_requests:
0`). No paid, live or production path was touched.

## 7. Protection

Owner-log SHA-256, identical before and after:

```text
c3f88f63e12c143d6d722904fef7f29cd5d6c5751782d9b0fbd54ea9db11687d  assurance/runs/daily_alert.jsonl
108d0b14387dc50a7c0437cbe8f029d2e442dd6ed9c7bde7aea19e2113ae8ce0  assurance/runs/weekly_alert.jsonl
6562b768adf760fde2e0918344f9d15ccc51978dfe3ff4817c7eecd66d86d7ef  assurance/runs/weekly_manifest.json
```

- `production_writes: 0`, `raw_deletions: 0`, `paid_calls: 0`.
- Real home installations were only read (stat / SHA-256 / file names); they
  were never used as a pytest fixture.
- No authorization, binding, approval or expiry file was introduced anywhere.

## 8. Cleanup

`.planning/test-tmp/g5-install` and its parent `.planning/test-tmp` were absent
before this lane and are absent again — pytest's `--basetemp` scratch is owned
and removed; nothing else under `.planning/` was touched. The RED probe and its
backup of the base tool lived outside the repository in the system temp
directory and are removed at handoff. No backup, archive or engineering package
was copied to a user skill installation.

## 9. Remaining for MAIN

See `main_wiring.md` for the exact commands. Summary:

1. Merge into RF main, then run the read-only pre-flight **from the original
   repository** (`--canonical` there gives the card's 8-file reality).
2. `--plan` (expect `selected_drift=8`, `unselected_drift=0`), then `--apply
   --json` for exactly the 24 candidates, then confirm `MATCH …: 75 files`.
3. Re-read the installed `scripts/revenue_forecast.py --help/--version` from
   each physical root with `PYTHONPATH` unset.
4. Update the total PWF. This apply does not need a new review receipt; if a
   local tool approval appears, state the accurate 24-file fact and the existing
   authorization and let MAIN handle it.
5. Pre-push needs sibling repositories: use the existing `FF_V2_CODE_ROOT` /
   `CWP_V2_CODE_ROOT` explicit committed read-only entry rather than removing a
   check to go green. **Done here**: with
   `FF_V2_CODE_ROOT=C:/Users/郑曾波/Projects/filing-fetch` and
   `CWP_V2_CODE_ROOT=C:/Users/郑曾波/Projects/company-wiki` the gate is
   **GREEN** (`pre-push/CI checks GREEN`, ruff clean, public-contract types
   clean, 107 passed) and `git push -u origin codex/g5-rf-install` succeeded.

Nothing in this lane claims that a production forecast has been run, and the
other two lanes are unaffected.

## 10. Delivery record

| item | value |
|---|---|
| implementation commit | `a2116ca6d5280c140b42a0d8bd2d94521ee80ccd` — pre-commit: ruff Passed, mypy-contract Skipped, host-assumption-guard Passed |
| handoff commit | this `.planning/g5-rf-install/**` package; `handoff.json` validated against the read-only `g5_handoff.schema.json` |
| pre-push gate | exit 0, `pre-push/CI checks GREEN`, 107 passed in 18.11 s (ruff + public-contract types clean), sibling entry supplied through `FF_V2_CODE_ROOT` / `CWP_V2_CODE_ROOT` |
| push | `git push -u origin codex/g5-rf-install` exit 0; new remote branch, upstream set |
| not done | no merge into RF main, no real home installation synchronized — both are MAIN's steps (card §6) |
