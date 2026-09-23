# ORACLE — RF-STEP9-TRIAGE (frozen BEFORE execution)

Card: RF-STEP9-TRIAGE — attribution + scope classification of the 12 residual CI step9 failures
(post sibling-pin-fix residual; register §55 "余12待归因").
Frozen at: a20260923-01, before any reproduction/fix work.
Human confirmation: **UNAVAILABLE this session** (subagent of session-bfecd191-fbc3-4a66-8ed1-6562479bf102;
ask_user_question rejected with "human interaction is unavailable while the calling agent is owned by
another live agent"). Oracle frozen from the card text itself; the pending confirmation question is
carried in the final report to the parent.

## 1. SCOPE (in)
Exactly these 12 CI step9 failures (WSL arm2, wiki@5d72529 NEW ⇒ sibling NOT the cause):

1. tests/adversarial/test_receipt_attacks.py::test_context_fabrication_is_rejected_by_final_validation
2. tests/test_attestation.py::test_configured_provider_means_host_signed_publication
3. tests/test_fc1102_t2_runner.py::test_healthy_lake_passes
4. tests/test_fc1102_t2_runner.py::test_report_isolated_and_json
5. tests/test_fc1102_t2_runner.py::test_trend_delta_detects_regression
6. tests/test_fc1302_scan_health.py::test_recurring_unchanged_errors_do_not_fail
7. tests/test_fc1302_scan_health.py::test_interrupted_delta_beyond_budget_fails
8. tests/test_single_owner_guard.py::test_only_canonical_client_may_use_subprocess_download_adapters
9. tests/test_zr1102_adversarial_audit.py::test_c4_mutation_patrol_capabilities
10. tests/test_zr601_asset_facts.py::test_c1_negative_asset_drivers_rejected
11. tests/test_zr601_asset_facts.py::test_c1_recovery_rate_out_of_range_rejected
12. tests/test_zr708_backtest_reverify.py::test_c2_accuracy_record_consumed_by_confidence

## 2. SCOPE (out)
- The 13th/14th complexity-ratchet failures (scripts/model_extensions.py ×2, scripts/analysis/confidence.py
  ×1 ratchet face) → separate card RF-RATCHET-FIX. EXCLUDED. (Note: zr708 #12 exercises confidence.py as a
  *product dependency* — testing that link is in scope; ratchet-count failures are not.)
- Blind mass fixes; any fix that is not small-and-clearly-safe.

## 3. PER-FAILURE ATTRIBUTION SUB-PROTOCOL (evidence-backed; all five legs required)
a. REPRODUCE in WSL: exact CI step9 command scoped to the failing file; raw output (failure message +
   traceback tail) saved under evidence/; wiki sha + RF sha recorded per run.
b. FIRST-RED evidence: last-green anchor `46bd8b16` (#287, 9-20 07:47Z) in a THROWAWAY clone/worktree
   (TEMP/WSL-home only; no RF writes; no git mutations in RF). Failure present there too ⇒ "pre-existing
   before the red streak"; else bisect-lite across commits 46bd8b16..current to find introducing commit.
c. HOST-DEPENDENCE: each file also run on WINDOWS locally ⇒ yes/no recorded.
d. ROOT-CAUSE CLASS ∈ { i RF product-code defect, ii RF test-expectation drift vs product change,
   iii platform/Linux-only, iv environment/dep, v sibling/manifest interplay (expect NONE @wiki-new —
   must confirm), vi order/fixture-state dependence }.
e. FAMILY grouping (hypothesis to verify): fc1102×3 → t2_runner; fc1302×2 → scan_health;
   zr601×2 → asset_facts; singles = receipt_attacks, attestation, single_owner, zr1102, zr708.
   Prime suspects to test explicitly: 70dd9f6e (fcap→main checkout), 5db4734a, ec307d20 (B1 promotion),
   5fd82de7 (MODEL); zr708 ↔ confidence.py fcap-checkout link tested explicitly.

## 4. WHAT COUNTS AS ATTRIBUTION-COMPLETE (per failure)
All of: raw reproducer on BOTH platforms saved with shas bound; first-red verdict with git evidence
(anchor run output or bisect-lite introducing-commit proof, git log -L / blame on BOTH failing test and
product code exercised); root-cause class assigned with reasoning; family assigned; scope class assigned ∈
{small-safe-fix-now, family-card-needed, owner-ruling-needed} with a fix plan (or STOP-evidence for
owner-ruling). Attribution completeness > fixing speed.

## 5. SCOPE CLASS + FIX RULES
- small-safe-fix NOW in-card only if clearly safe: owner-authorized test-expectation update matching an
  owner-authorized product change, missing import, trivially-safe product bug with clear intent. Applied in
  an ISO copy only, red/green proven, recorded in changes.diff. RF production tree stays byte-clean.
- family-card-needed ⇒ prompt-sized card spec delivered in decision.md; NOT executed here.
- owner-ruling-needed ⇒ item STOPPED with evidence (e.g., expectation conflicts with frozen contract).
- NO blind mass fixes.

## 6. RULES / BINDING
- RF production READ-ONLY: writes only inside this attempt dir; small fixes live only in changes.diff;
  RF porcelain must be identical to baseline at close (disclosed pre-existing dirt listed).
- No network. WSL (`wsl -d Ubuntu`) + %TEMP% allowed. Git mutations in RF forbidden; throwaway
  clones/worktrees in TEMP/WSL-home allowed and disclosed.
- Strictly incremental: oracle → binding → commands → raws → attribution → decision.md → handoff.

## 7. DELIVERABLES (nine-step)
oracle.md (this) · binding.md · commands.md · decision.md (12-row attribution table) · changes.diff
(may be empty — honest) · handoff.md · evidence/ · recovery.md · final report to parent incl. the
unresolved oracle-confirmation question.
