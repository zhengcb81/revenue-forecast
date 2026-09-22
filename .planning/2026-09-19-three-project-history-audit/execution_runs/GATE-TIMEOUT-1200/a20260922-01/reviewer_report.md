# Independent Reviewer Report — GATE-TIMEOUT-1200

- Attempt: `execution_runs/GATE-TIMEOUT-1200/a20260922-01`
- Reviewer mode: byte-level evidence review only (no pytest, no gate run, no git writes; grep/partial reads only — no file >6 KB read whole)
- Review date: 2026-09-22
- **Verdict: `accepted_scoped`**

## Scope statement (REM-79, mandatory sentence)

The one-line gate timeout change (600→1200) is **proven at the measured load domains only**: RED arm and GREEN arm each ran with 8 card burners, GREEN2 ambient python-proc counts ≈ 2 (before) / 12 (mid, incl. 8 burners) / 2 (after), GREEN total gate wall = 1336.7 s. **Under extreme ambient load the real-data step finished in 1182.3 s wall against the 1200 s cap (~18 s margin) while a test inside it had already failed on its own internal 120 s timeout — extreme ambient can still exceed 1200 s, which is an owner call outside §16-B (OQ-01).** This acceptance grants no disclosure_adaptation (stays unmapped) and no accuracy (stays unproven) claim.

## Findings (all verified from bytes)

1. **[PASS] One-line change only.** `changes.diff` is a single hunk changing exactly one line: `timeout: int = 600` → `timeout: int = 1200` in `_run()`. `evidence/line_change.json` numstat = `1 1 tools/pre_push_gate.py`; only production file touched.
2. **[PASS] Hashes computed by reviewer.** `before/pre_push_gate.py.orig` = `0d290326200ebde819d3473589bd1aa0ed36da4806097d8a59dc8dc316fcc594`; current `tools/pre_push_gate.py` = `cf09ade8164e89d79237ff5a8409496ab1ae2a9c5f3ee2c253ccad20ef06df0b`. Both match `binding.json`, `oracle_freeze.json`, `line_change.json`, `final_deliverable_hashes.json`, and all driver logs. *(Brief-suffix note: the brief wrote before-hash suffix "f594"; the real suffix is "c594" — decision.md itself records `0d290326…c594`. Prefix and full hash match everywhere; brief suffix is a transcription typo, not an evidence defect.)*
3. **[PASS] Oracle frozen before the change.** `evidence/oracle_freeze.json`: `gate_untouched_at_freeze=true`, `oracle_frozen_utc=2026-09-22T07:26:09Z`, gate-hash-at-freeze = before hash, gate file mtime at freeze = 2026-09-20T15:23:51Z; change applied `2026-09-22T07:27:39Z` — freeze precedes application by ~90 s.
4. **[PASS] RED arm genuinely timed out at 600.** `after/gate_red_600.txt` ends in `subprocess.TimeoutExpired … timed out after 600 seconds`; argv = `-q --tb=short` + exactly the 7 `REAL_ROOTS_TESTS` files (verified against `tools/pre_push_gate.py` lines 141–148: zr803, zr1103, ca203_weekly_t3, fc1101, compatibility_manifest, fc1002, ca203_three_journeys); no skip/deselect flags; no GREEN line anywhere in the file. Failure exit evidence: `after/red_driver_log.txt` → `GATE_EXIT_CODE=1`, `HAS_TIMEOUTEXPIRED_600=True`, `HAS_GATE_GREEN=False`. `evidence/burners_red.json` → `requested: 8`, `alive_after_start: 8`.
5. **[PASS] RED count discipline held.** Dir-wide grep for `not observable (killed at 600 s)`: present only as the pre-registered I-3 caveat in oracle.md / decision.md / handoff.json / recovery README, each explicitly stating "never claimed as 55 passed, never read as a skip". No artifact claims 55 for the RED arm; `gate_red_600.txt` and `step_times_red_600.json` contain no 55-claim.
6. **[PASS] GREEN attempt #2 (same domain) is GREEN.** `after/gate_green_1200_attempt2_samedomain.txt`: all 10 steps `ok`, final line `pre-push gate GREEN — safe to push (then self-monitor CI).` `after/step_times_green_1200_attempt2.json`: GREEN banner at `elapsed_s 1336.699`, `run_end elapsed_s 1336.734`, `exit_code 0` — total ≈1336.7 s as claimed.
7. **[PASS] GREEN attempt #1 failed as disclosed (transparency check).** `after/gate_green_1200.txt`: failed at the real-data step with `1 failed, 63 passed, 1 xfailed, 2 warnings in 1159.84s`, `FAILED tests/test_fc1105_fault_injection.py::TestFaultInjection::test_f2_missing_samples_fails`, `GATE RED at: real-data suite`. Failure was recorded, not hidden.
8. **[PASS] f2 standalone characterization.** `evidence/f2_standalone_lightload.txt` = `1 passed in 44.00s` — the load-induced (not code-induced) nature of the OQ-02 failure is evidenced.
9. **[PASS] Count invariants + arithmetic.** `evidence/invariant_e2e_55_count_check.txt` = `55 passed in 185.96s`, no skipped line (0 skipped). `evidence/invariant_realdata_count_check.txt` = `64 passed, 1 xfailed, 2 warnings in 246.64s`, no skipped. Cross-check: attempt#1 1+63+1 = 65 = 64+1 ✓ (attempt#1's failing f2 test is the xfailed/pass delta reconciled by attempt#2 passing it — totals consistent).
10. **[PASS] GREEN2 load domain recorded.** `evidence/load_snapshot_green2_start/mid/end.json`: `ambient_python_procs 2` → `python_procs 12` with `this_cards_burners_alive 8` → `2`, timestamps 08:24:45 → 08:24:54 → 08:47:14, spanning the GREEN2 run (08:24:55–08:47:12). Burner count 8 matches the RED arm's 8 (`burners_red.json`) → RED-comparable induced load.
11. **[PASS] Handoff fields.** `handoff.json`: `status: review_pending`, `implementer_signed: false`, `gate_timeout_change: review_pending`, `disclosure_adaptation: "unmapped"`, `accuracy: "unproven"`, `not_granted: ["disclosure_adaptation (stays unmapped)", "accuracy (stays unproven)"]`; OQ-01 (real-data ~18-s margin at extreme ambient, owner ruling required, boundary "NOT covered by section 16-B … REM-79 rule"), OQ-02 (f2 helper internal `timeout=120` fragility, registered-not-fixed, passes standalone 44 s), OQ-03 (pre-existing GBK `UnicodeDecodeError` warnings in `test_install_sync_gate_detects_drift` reader threads, non-fatal) all present. Implementer has not self-signed ✓.
12. **[PASS] BONUS / live-push corroboration (rechecked by reviewer).** Repo HEAD = `6f74b056631e0cb50a28b57bdcf979514dadb8f9` and local `origin/main` = same commit; HEAD commit subject: "…gate timeout 600->1200 (live RED/GREEN pair)…". `git cat-file -p HEAD:tools/pre_push_gate.py` shows `timeout: int = 1200`, and `git diff --stat HEAD -- tools/pre_push_gate.py` is empty → HEAD blob == current after-image (`cf09ade8…df0b`). Verified-by-parent (not re-run by me): the literal push stdout `ab20cebe..6f74b056 HEAD -> main` and `pre-push gate GREEN` during that push.

## Unverified / not re-checked by this reviewer

- The literal live-push console line `ab20cebe..6f74b056 HEAD -> main` and the `pre-push gate GREEN` output emitted inside that push (parent-supplied; corroborated by HEAD == origin/main == 6f74b056 and HEAD blob == after-image).
- Full text of `oracle.md`, `decision.md`, `commands.json`, `git_status_*.txt` (each >6 KB / long): verified only via targeted greps as instructed.
- No RED-arm ambient python-proc snapshot exists (only `burners_red.json` = 8 alive); RED↔GREEN ambient-proc comparability rests on the equal burner count and the green2 snapshots, not on a red snapshot.
- `evidence/f2_standalone_lightload.txt` was not accompanied by its own load snapshot; its "light load" characterization relies on the surrounding run context.
- No pytest/gate execution was performed by this reviewer (per task bounds); all verdicts rest on recorded bytes plus live hash/git-object reads.

## Boundary compliance

Reviewer wrote only `reviewer_report.md` and `reviewer_report.md.sha256` inside this attempt dir. No production writes, no git writes, no pytest, no gate run, no self-signature of the card.
