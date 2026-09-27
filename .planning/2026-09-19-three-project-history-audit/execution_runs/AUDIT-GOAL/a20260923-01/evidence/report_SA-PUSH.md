# SA-PUSH AUDIT REPORT

SA-PUSH AUDIT REPORT (read-only; nothing modified; all git checks re-run by me unless marked [parent-supplied]). Repo=C:\Users\郑曾波\Projects\revenue-forecast, PLAN=.planning\2026-09-19-three-project-history-audit.

## (1) BATCH TABLE (all endpoints confirmed `git cat-file -t`=commit + `git log -1`)

| # | push window | commits (re-counted rev-list --count) | subjects (abbrev) | gate record in plan docs | verdict |
|---|---|---|---|---|---|
| 1 | ab20cebe..6f74b056 | 21 | rounds 43–80 PWF+gate 600→1200 (6f74b056)… | findings.md:653-655 ("pre-push gate GREEN — safe to push"; 10 步全 ok; ab20cebe..6f74b056 HEAD->main, push_rc=0) + progress.md:930-932 | VERIFIED ("20+"=21 ✓) |
| 2 | 6f74b056..3861f08d | 1 | batch-2 four-systems closure | progress.md:1050-1052 ("pre-push gate GREEN（10/10 步含 real-roots + real-data）", 6f74b056..3861f08d, rc=0) | VERIFIED (see INC-4) |
| 3 | 3861f08d..4b1c690b | 3 | batch-3a 17565057 / 3b 60489e34 / 3c 4b1c690b (gitlink fix) | findings.md:680-682 ("pre-push gate GREEN（10/10）→ 3861f08d..4b1c690b", rc=0) | VERIFIED |
| 4 | 4b1c690b..865428f8 | 5 | 95df2661(GATE-OQ-FIX), ec307d20, 5fd82de7, 243d0cb6, 865428f8 | REMEDIATION_REGISTER.md:1095-1097 (§46 "push_rc=0、门 10/10 绿…gate=3df161a7（1800 版）") + progress.md:1114-1116 | VERIFIED |
| 5★GAP | 865428f8..b0d016a6 | 2 | 1fa090fe (batch-5), b0d016a6 (batch-5c) | REMEDIATION_REGISTER.md:1211-1213 (§54 "推送：865428f8..b0d016a6、push_rc=0、门 10/10 全绿") | VERIFIED as ONE window; "5a/5b/5c" labels inconsistent (INC-2) |
| 6 | b0d016a6..262659e4 | 1 | batch-6 E2E-EXPAND + I-07-B | progress.md:1148 ("批 6 门 10/10 绿") | VERIFIED (thin record) |
| 7 | 262659e4..a31fd7ed | 1 | batch-7 F-EE1-FIX | progress.md:1158 ("批 7 a31fd7ed 落地（门 10/10）") | VERIFIED (thin) |
| 8 | a31fd7ed..977fa1e8 | 1 | batch-8 I-07-C | register:1323 (intent "批 8 提交推送") + register:1331 (CI run #312(batch-8) ⇒ push happened). NO green-gate line found | UNVERIFIED gate record (INC-1) |
| 9 | 977fa1e8..b7a6a116 | 1 | batch-9 I-07-D + register 62-63 | register:1362 ("批 9 推送中" in-flight at write time); no green confirmation anywhere | UNVERIFIED gate record (INC-1) |

★ The "gap" between 865428f8 and b0d016a6 = batch 5 series, omitted from the claimed range list. Reconstructed: batch-5 first landed as sibling commit 0d10ae8f (parent=865428f8, `cat-file -t`=commit, dangling—amended away), push #1 rc=1 (ruff F401 etc., register:1187-1191) → amended to 1fa090fe (same parent 865428f8 — re-measured `git rev-parse 0d10ae8f^ 1fa090fe^`), push #2 rc=1 (real-roots E2E 4F/51P, register:1201) → batch-5c commit b0d016a6 (RF-E2E-ADAPT root fix) → ONE green push 865428f8..b0d016a6. Total commits in ab20cebe..b7a6a116 = 21+1+3+5+2+1+1+1+1 = 36 (sum of re-counted segment counts).

HEAD check (re-measured `git rev-parse HEAD origin/main`): both = b7a6a1167beeac6975fa9f8fe130bdd2136ecbcb ⇒ ahead=0, ZERO unpushed commits. Working tree dirty only with uncommitted PLAN artifacts (REMEDIATION_REGISTER.md modified + untracked execution_runs evidence dirs) — no unpushed history.

## (2) GATE-BLOCK ROOT-CAUSE DOSSIERS (4)

DOSSIER A — ruff F401 (batch-5 round 1)
(a) RED record: register:1187-1189 ("批 5…首推 push_rc=1 门红…ruff F401：tests/test_message_contract_pins.py:30 import json 未用") [parent-supplied prose; no raw capture preserved in git].
(b) Root cause: FIX-card's new test file had unused `import json` (single-file ruff never run on it).
(c) Fix file: tests/test_message_contract_pins.py ONLY — re-measured `git diff 0d10ae8f 1fa090fe --stat` = exactly 1 file; 1fa090fe adds it (266 lines). NOTE: the pre-fix red bytes are NOT in git (0d10ae8f does not contain the file — re-measured; it was fixed in the working tree before the amend), so the byte-level red→fix diff is UNVERIFIED (INC-5).
(d) No gate/baseline weakening: fix is a test-code deletion; `git log ab20cebe..b7a6a116 -- tools/pre_push_gate.py conftest.py pytest.ini pyproject.toml setup.cfg` = only 6f74b056 + 95df2661 (both pre-batch-5, timeout-only). No skip/deselect added (see bypass scan below).

DOSSIER B — host-assumption-guard ("宿主字面") + U+FEFF BOM (same round)
(a) RED: register:1190-1191 (amend hook 报守卫语法错/new=1；host-guard new=2 at the file's :44/:48 硬编码 `C:\Users\…`).
(b) Root cause: (i) author's own `Set-Content -Encoding UTF8` wrote a U+FEFF BOM (self-inflicted, logged as "第 9 例自纠", register:1190/1194); (ii) test file baked host-absolute paths as fallback (guard violation vs host_assumption_guard).
(c) Fix: same single file tests/test_message_contract_pins.py — re-measured at HEAD via grep: NO `C:\Users` literal, NO BOM-suspect line, paths now `ROOT = Path(__file__).resolve().parents[1]` + `GAPS_PIN_RF_SCRIPTS`/`GAPS_PIN_CW_DIR` env overrides (tests/test_message_contract_pins.py:38-49). "守卫 new=0 rc=0、ruff All checks passed、8 测全过" register:1191 [parent-supplied].
(d) The guard itself (tools/host-assumption-guard / gate) was NOT touched in the audited range (gate-file log, re-measured) — fix was in the offending test code. PASS.

DOSSIER C — E2E receipt-contract / fail-closed adaptation (batch-5 round 2 = RF-E2E-ADAPT)
(a) RED record: register:1201 ("real-roots E2E RED（4F/51P）") + raw captures COMMITTED in b0d016a6 (re-measured `git show --stat b0d016a6`): execution_runs/RF-E2E-ADAPT/a20260923-01/evidence/red_raw.txt (7090 B), red_prep_e2e_raw.txt, red_zr709_raw.txt, red_zr803_lock_raw.txt.
(b) Root cause: cross-repo contract drift — CW commit 5d72529 added a state_domain fail-closed gate (CW prompt_injection.py:449-452) while RF E2E fixtures still minted OLD-form receipts → envelope defaults not_reviewed (:1078) → RF source_preparation:150-156 blocks rc=3 (register:1201) [line refs parent-supplied].
(c) Fix files (re-measured from commit stat): tests/e2e_support/isolated_lake.py (43±), tests/test_preparation_e2e_success.py (29±), tests/test_zr709_zijin_journey.py (29±), tests/test_zr803_chaos_recovery.py (5±) + tests/test_fc905b_trusted_receipt.py (owed face, disclosed not smuggled, register:1206-1207). Fix = fixtures mint receipts via CW's real writer (new contract); zr803 = diagnostic fix (`.decode` under text=True), assertion-condition bytes untouched (register:1204).
(d) No gate/oracle/selection weakening (independent): b0d016a6 touches NO tools/ file (stat above) — gate "未动" (register:1204); the fix's changes.diff contains ZERO matches for skip|xfail|deselect|pytest.mark (re-measured grep of RF-E2E-ADAPT/a20260923-01/changes.diff); GREEN = gate's ORIGINAL 7-file literal selection set, 55 passed exit 0, and a mutation restore re-reproduced the 4F red (compliance proof) + business assertions 66=66 unchanged (register:1204, reviewer_report.md 294 lines in attempt) [counts parent-supplied, files re-measured present].

DOSSIER D — gate timeout block (the batch-1 unblock)
(a) RED: findings.md:398-412 (E2E 7 files all pass, 55 passed/0 failed, wall-clock ≈861.7s > gate's 600s subprocess cap; culprit test_ca203_weekly_t3.py 387.1s) + task_plan.md:1415 ("未绕过门"); live RED re-reproduced at 600 under 8 burners for the red/green pair (findings.md:592-596, commit msg 6f74b056).
(b) Root cause: the gate's timeout configuration, not tests (test suite GREEN given time).
(c) Fix = the owner-authorized ONE-LINE gate change (see §3) with live RED/GREEN pair; green arm#2 same-domain at 1200s (findings.md:618).
(d) No test was skipped/split/weakened; full suites ran and were judged (findings.md:594 "不绕门：绿臂须在 1200 下完整跑一遍留证").

## (3) GATE-CHANGE HISTORY VERDICT (tools/pre_push_gate.py — `git log --oneline --follow`, dates added)

6682ecf5 09-06 created gate | 51b9469e 09-07 "tmp neg test revenue" (+U+FEFF BOM header + `/nonexistent-neg` appended to ruff args — deliberate NEGATIVE test to prove push blocks) | 96c03298 09-07 reverts it ("push was BLOCKED as designed") | a33030d4 09-07 gate file must be UTF-8 w/o BOM (ratchet, +1/−1) | 81553f13 09-07 ADD UTF-8 BOM scan step (+27) | cbfc85c3/6f041f8b/add326a2 09-08 install-sync + real-roots blocking (strengthening) | 798d3afd 09-15 vendor host-assumption gate into commit+push (strengthening) | 6f74b056 09-22 timeout 600→1200 (exactly 1 line, hunk @@ -70,7 +70,7 — diff re-read by me) | 95df2661 09-22 real-data step +1 line timeout=1800 (per-step; _run default stays 1200) + tests/test_fc1105_fault_injection.py f2 helper 120→300.

VERDICT: In the audited window (post-2026-09-19) exactly TWO gate edits: (1) 6f74b056 — the expected, owner-authorized one-liner (OWNER_DECISIONS.md:365/371 §16 verbatim "A-2: 批准 B: a（提高门超时到 1200，立卡红绿）"); (2) 95df2661 — FLAGGED (INC-3): a SECOND gate product change beyond the stated "only expected" line. It is owner-authorized (OWNER_DECISIONS.md:418-426 §18 "B=全批…OQ-01/02 修复卡 GATE-OQ-FIX…real-data 步 1200→1800（仅该步）、f2 内部 timeout 120→300") and timeout-only (no test-selection/oracle change; OQ-01/02 closed at register:1099). Pre-window edits (09-06..09-15) all strengthen the gate except 51b9469e, a self-reverted one-commit negative test (net zero; made the gate stricter, not weaker). No historical gate edit found that weakens checks. The GATE-TIMEOUT-1200 card's red arm transiently restored the 600 version in the working tree (findings.md:592-596) as the RED fixture of the authorized red/green pair; final state verified at HEAD: `timeout: int = 1200` default + real-data call `timeout=1800` (Select-String on HEAD blob 9004104d). Hash labels `cf09ade8…`(1200版)/`3df161a7`(1800版) (findings.md:594, register:1097) = [parent-supplied]; content facts re-measured, hash values not recomputed (no-write constraint).

## (3b) BYPASS SCAN

`git log ab20cebe..b7a6a116 --grep` re-run per pattern: no-verify=0 hits, deselect=0 hits; "bypass"=1 hit (bdae6a22 body: "the gate has not been bypassed" — a DENIAL); "skip"=3 hits (batches 5c/6/7 bodies mention "skip/xfail 0→0" accounting / KEEP-RED; no skip introduced — corroborated by zero skip/xfail in RF-E2E-ADAPT changes.diff). Register hits: register:929 "B-6b 无目标 SKIP"=promotion-node with nothing to promote (not a test/gate skip); register:21 "去掉 xfail" (REM-10) = REMOVING an xfail (strengthening); register:903 §17 B-8 ruling = "永不设（可）绕过旗标…warn-only/降级/env bypass 都会换名重造 REM-01" (all bypass mechanisms forbidden). One earlier gate block (progress.md:497, pre-window commit 2028576) resolved by RE-RUNNING the same gate to green — explicitly "未绕过任何门（是重跑通过，不是跳过）". VERDICT: no gate bypass, no test-selection shrink found; the only "skip"-adjacent acts are fixture-isolation skips already pre-existing (register:1204: skip/xfail 0→0).

## (4) INCONSISTENCIES / UNVERIFIED

INC-1 [MEDIUM] Batches 8 and 9 have NO recorded pre-push gate GREEN anywhere in PLAN docs (searched findings.md/progress.md/REMEDIATION_REGISTER.md/task_plan.md). Batch 8: only intent (register:1323) + downstream CI run #312 mention (register:1331); batch 9: status frozen mid-flight at "批 9 推送中" (register:1362). Both ARE on origin/main (re-measured HEAD==origin/main==b7a6a116). Gate result at their push time = UNVERIFIED; a push without a recorded green gate cannot be excluded from docs alone. Mitigating (re-measured): the gate file and test-selection configs are unchanged across both batches (only 6f74b056/95df2661 in the whole range), and no bypass markers exist.

INC-2 [LOW] "批次 1/2/3/4/5a/5b/5c 全部推送绿" (register:1229, progress.md:1139) is loose: git shows batch 5 as ONE green push window (865428f8..b0d016a6, register:1213) over 2 commits + 1 superseded pre-amend commit (0d10ae8f) + 2 BLOCKED push attempts (register:1187/1201). "5a/5b/5c" do not map 1:1 to any git commits ("batch-5" and "batch-5c" exist as subjects; no batch-5a/5b anywhere, `git log --all --grep`).

INC-3 [LOW, premise flag] Parent's expectation "the ONLY gate change is 600→1200 in 6f74b056" is factually incomplete: 95df2661 also edits the gate (real-data step 1200→1800). Owner-authorized (OWNER_DECISIONS.md:418-426) and surgical (timeout only) — classify as authorized, but register it as the second gate edit.

INC-4 [LOW] Batch-2 was pushed with a quality defect: 2 mode-160000 embedded git repos committed (findings.md:671-673 "带病推送…属运气非护栏"); healed in batch-3c 4b1c690b. Gate was green — shows the gate does not cover gitlink hygiene.

INC-5 [UNVERIFIED, low] Byte-level red→fix evidence for Dossier A/B fixes is not recoverable from git: the red working-tree state of tests/test_message_contract_pins.py was never committed (0d10ae8f lacks the file — re-measured); red facts rest on register:1187-1191 prose. End state independently verified clean.

INC-6 [INFO] Gate content-hash labels (cf09ade8/3df161a7/0d290326) are [parent-supplied]; I verified the underlying content facts but did not recompute file hashes (read-only/no-write rule).

Also noted (not an inconsistency): register:1331 + §55 record CI RED after batches 5c–8 (14 pre-existing violations + pinned old fixtures) — honestly ledgered, never claimed green; distinct from the local pre-push gate.

## (5) COVERAGE STATS

Independently re-measured: 9/9 range endpoints (cat-file/log -1), 9/9 rev-list counts + subject lists, HEAD vs origin/main, gate-file full history + diffs of 6f74b056/51b9469e/96c03298 + stats of 81553f13/a33030d4/95df2661, b0d016a6 & 1fa090fe file stats, 0d10ae8f↔1fa090fe diff, bypass-term greps (commits + RF-E2E-ADAPT changes.diff), end-state grep of tests/test_message_contract_pins.py, HEAD gate content (timeout lines). Plan-doc quotes cited at file:line for every batch. NOT verified (out of scope/limits): raw gate capture file contents for batch-5 round-1 reds (glob of execution_runs timed out repeatedly; only file presence inside commit b0d016a6 confirmed via git), the CW sibling repo, CI/GitHub runs (no network), reviewer_report.md full text (presence + line count only), exact sha256 hash labels. Parent-supplied vs re-measured markers are inline above.

Written by SA-PUSH (independent reviewer) on 2026-09-23; parent-supplied vs re-measured markers as inline.
