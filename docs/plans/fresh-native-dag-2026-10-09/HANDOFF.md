# W10/W14 engineering handoff

- Implementation commit: `3cecdecf9341c5cfaf2d687585e60168fd8c665f`; branch `codex/fresh-rf-dag-20261009`; base `79139534375f7eb523a768202f34aedf58538051`.
- Exclusive worktree: `C:\Users\郑曾波\AppData\Local\Temp\rf-fresh-dag-20261009`.
- Production writes: sensitivity.py, forecast/calc.py, contracts/document.py, forecast/segments.py, revenue_report.py. Focused tests: test_sensitivity_dependency_dag.py and test_published_foundation_roundtrip.py.
- Evidence: initial 16 RED failures; final 202 passed + 202 subtests, 1 historical-version skip; normal hooks all passed. Pinned full-result comparison covers the skipped lock's five model families without changing old hashes.
- Retained HK/US equivalent reconstructions fail on pinned base and pass repaired source with 12/24/24 shocks. Only explicit domain metadata was added in memory. No company special case exists in production code. Original source byte hashes are preserved.
- Opening definition: residual = segment bases + signed base adjustments - reported opening total. Adjustment increment = terminal forecast adjustments - opening adjustments + residual. Annual forecast revenue is unchanged; input tolerance and strong independent contribution checks remain enforced.
- Authoring domain: optional `sensitivity_domain` object with exact `lower`, `upper`, `basis`; null endpoint means no bound. An ancestor ratio needs explicit domain semantics. Signed growth changes can be negative; downstream driver bounds remain binding. Numeric magnitude support is a separate research contract.
- Conditional sensitivity may exceed the original scenario bracket as before; formally authored Base/Low/High ordering is still checked.
- Required selected installation: the five source files in installation-delta.json, after independent review/integration. This lane did not install, push, merge, call providers/models, acquire sources or change old originals/outputs/snapshots.
- Engineering PASS does not clear missing future-magnitude evidence, joint stress research, lost first-authoring bytes, or all fresh audit findings. MAIN must score those separately at M3.

## Cleanup

Every disposable pytest/publication/baseline root was context-managed and removed; old source bytes remained unchanged. Only verified caches under this worktree were deleted. No successful XML or duplicate forecast output is retained. This worktree and the compact plan/evidence package remain available for independent review.
