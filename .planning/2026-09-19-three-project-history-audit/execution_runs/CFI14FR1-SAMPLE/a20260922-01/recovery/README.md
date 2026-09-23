# recovery/README.md — CFI14FR1-SAMPLE (a20260922-01)

**Nothing to revert. This card made ZERO product writes.**

Checked and true at handoff:

1. **CW tree** — no command of this card wrote any CW path. Full mtime scan
   (`evidence/tree_scan_after.json`, window ≥ 2026-09-22 22:50) shows exactly 6 hits:
   - `.pytest_cache/v/cache/{lastfailed,nodeids}` — pytest's disclosed side effect
     (un-reverted on purpose: rewriting them back would itself be a CW write, and they are
     volatile test-state caches);
   - `.source_catalog/catalog.sqlite3-{wal,shm}` — volatile SQLite companions created/
     refreshed when TESTS opened the catalog (0-byte `-wal`; the 46.3 GB
     `catalog.sqlite3` itself has mtime 2026-09-19 07:31:35 — untouched). Left in place
     deliberately, same reason; they are transient, not product content;
   - `tests/unit/test_prompt_injection_guard.py`, `tests/unit/test_readiness_graph.py` —
     **external concurrent edit at 01:01 (not this card; see decision.md §5.3)**. Nothing
     to revert BY THIS CARD; reverting someone else's in-flight edit is explicitly NOT
     ours to do.
2. **%TEMP%** — own debris cleaned: `cf14fr1-with-hook` removed (incl. interrupted run's
   test dirs; pre-cleanup listing preserved at `evidence/01b_basetemp_leftovers.txt`);
   probe's over-budget dir never created; hook fallback `20260923-001135-9b6efb68`
   self-removed by the hook (`"removed": true` in `04_redirect_probe.decision.jsonl`);
   `cf14fr1-pycache` prefix never created. NOT touched: the three `20260921-*` fallback
   leftovers belonging to OTHER sessions.
3. **git** — none (no git read or write). **network** — none.
4. **Other cards/attempts** — read-only citations only; no oracle/card/register of anyone
   else edited; `commands.json`/`oracle.md` of THIS attempt are byte-frozen as pinned.
5. If a future session wants the volatile leftovers gone (`.source_catalog/*-wal/-shm`,
   `.pytest_cache` cache files): that is an explicit CW write and must be its own
   sanctioned action — not part of this card, and not required for correctness.
