# P5-RF MAIN integration — 2026-10-06

Local source/default/forecast responsibility checks and fixed real-PDF CLI GREEN.
Publication complete: main ca67eab7, exact CI37391526925 attempt1 ALL steps GREEN.
One Ubuntu job32s; checkout1s, dependencies7s, siblings7s, shared checks11s.
Delivery a74b9ceb / code31fe65e6, published base8a153f33. Producer pins: FF758e8f4,
CWP2145661. Only the independent MAIN worktree was edited; delivery tree unchanged.

## Corrections made by MAIN

- Expand the MAIN worktree's historical sparse checkout; missing files were environment
  errors with zero collected tests, not product RED. Owner worktrees were untouched.
- Bind current published FF/CWP in compatibility/current.json. Preserve frozen baselines,
  registry hashes, wire and forecast calculations. CI tests its checked-out RF HEAD.
- Default public CLI E2E resolves sibling roots without opt-in environment variables.
  A missing dependency now fails visibly; it never becomes an automatic skip.
- Seed three REAL old files and artifact rows before the deletion journey; delete the
  actual .source_catalog/derived root. The earlier empty deletion could not prove this.
- Remove calls to deleted CWP evaluate_review from old message pins, retain active hash
  validation and SourceRef wrong-byte/hash/identity refusal tests.
- Replace daily full pytest + second coverage pass + Windows historical audit job with
  one Ubuntu3.12 job and the SAME tools/pre_push_gate.py curated offline set as local push.
  No install auto-sync, production-catalog tests, workflow byte-signature, complexity,
  mutation or manual planning receipts in this daily gate. Commit stays static only.
- Retire the obsolete ZR-901 historical workflow-signature test, whose Windows job and
  hash-pinning assumptions were deliberately removed. Original is available in Git
  at a74b9ceb:tests/test_zr901_pr_fanout.py. Current CI wiring is behavior-tested in
  test_ci_smoke_plan.py; this does not modify the historical UC reports or forge them GREEN.
- One pytest process, 300s command cap, temporary basetemp automatically removed;
  child Git hook context is stripped, scoped Git configuration retained, no pycache writes.

## Tests actually executed (not added together as distinct without deduplication)

- Default source and public CLI baseline:11 passed,1 stale-review failure,18.27s.
- Short-CI TDD:2 RED,1 skipped (old opt-in skip),3.72s; implementation5 passed,0.92s.
- Concentrated source+forecast package:107 passed,1 new fixture error,16.10s.
  The sole fixture error used nonexistent documents.source_id; corrected to the actual
  primary_source_id. That case plus gate/environment cases:5 passed,7.23s.
  All108 distinct node cases passed across these runs; not one108-case GREEN claim.
- Shared gate Ruff/public types/curated behavior GREEN; normal commit/push repeats only
  the existing relevant gate. No broad legacy or production-data suite was rerun.
- Fixed actual AMEC FY2025 PDF:9165875B, SHA
  d64c410832f22f5127277bad6dc357c664aede523561af99150c494857fd3aa5.
  Public DEFAULT RF CLI succeeds three times (before deletion, after deletion, restored
  after tamper), tampered raw refuses once. Three legacy files/rows were really deleted
  in the fixture; source/document/location facts unchanged; artifact_read empty,
  download_calls0, unknown parser count null, original SHA unchanged.
  Identity/publication metadata is a labelled fixture, not live provider verification.

## Manual actual-PDF node and boundary

    python -B e2e/run_p5_rf_real_source_acceptance.py --raw-file <original-pdf> --scratch-root <existing-empty-independent-root> --ff-root <FF-code> --cwp-root <CWP-code>

No network/download/model calls. rfmcurrent/rfmfastred/rfmfastgreen/rfmnode/rfmfix/rfmreal
roots restored absent. Parent gate temp roots are automatically removed. Original RF
weekly logs, rf-impl staged WIP, CWP user configuration and originals were not edited.
No production legacy deletion, span pruning or VACUUM occurred. Local owner deployment
and exact CI are now completed as recorded below; delivery signoff alone was not that evidence.

Normal commit first rejected the new fixed raw-sample SHA as unregistered by the existing
host guard. Registered that byte-only sample with its provenance; no hash assertion
was removed or changed to a computed host-dependent value.

## Checkout bottleneck found after publication

The first exact code run37391276302 remained in actions/checkout before executing tests.
Git tracked directory counts: .planning47079 files, assurance1392, actual scripts51,
tests151. Daily CI now sparsely checks out its actual source/test/config dependencies,
excluding historical execution archives; original tracked history is not deleted.
Supported checkout@v4 sparse-checkout semantics were verified against the action's
[official README](https://github.com/actions/checkout/tree/v4#fetch-only-part-of-the-repository).
This is a new configuration correction, not a blind rerun of the earlier SHA.

## Final publication and local deployment

- Semantic/source code b110502f and checkout correction ca67eab7 are published on main.
- [Exact code CI37391526925](https://github.com/zhengcb81/revenue-forecast/actions/runs/37391526925)
  completed/success, all steps GREEN. Normal pre-push107 passed/19.12s.
- GitHub returned one remote500; remote state was checked and the SAME commit retried
  successfully. No blind test rerun or force push. Main/remote was verified equal.
- Formal Projects/revenue-forecast checkout switched to main. Both weekly log SHA remain
  identical. Old rf-impl main was renamed codex/rf-preserved-main-wip-20261006 without
  altering its242 WIP entries or staged bytes; fcap is an ancestor of main.
- Wider read found7 stale installed code/reference files per unique install; only those
 14 files were synchronized to agents/codex (claude resolves to agents). All72 production
  files now match. Installed configuration/output were not changed.
- This final receipt is documentation only. No production derived/span deletion or
  VACUUM took place; that belongs to the ongoing CWP storage node.
