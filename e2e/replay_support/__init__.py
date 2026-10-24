"""W14-RF-CLEAN-CHAIN replay support (E08 module split).

Small, single-purpose modules behind ``e2e/run_cross_repo_chain_e2e.py``:

- ``deploy``    — frozen-Git deployment of the three production repos and
                  provenance evidence (E02);
- ``netguard``  — offline child-environment construction: counter spy,
                  outbound-network block, credential scrubbing (E02/E03/E05);
- ``fixtures``  — the synthetic two-document lake built through public CWP
                  scan plus the fail-closed receipt writer (E03/E04);
- ``observe``   — judged subprocess execution, evidence writers, counters,
                  catalog/tree snapshots, semantic projection (E03/E07);
- ``cleanup``   — exclusive attempt directories and restore proofs; the
                  caller's existing directories are never deleted (E06).

No company names, personal directories, or historical SHA special cases live
in this package; every path and identity comes in as a parameter or from the
fixture manifest.
"""
