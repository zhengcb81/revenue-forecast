# Mainline reconciliation note — RF job facade

The original delivery was frozen on `codex/rf-job-facade-01` at `e4b38459f54db16e0de8e436690c2eb8c7cd13a1`, based on the B37 release line. Its package plan, handoff, design, findings, tests and review receipts are copied into this mainline PWF directory for discoverability; the receipt remains bound to its original branch code and does not attest the current implementation.

RF main already re-landed the public job facade in `ff1c69e082c7e0b1b03bac66a1117f6d8090233f` and added cross-process recovery in `cd24976a958bc2abee841a592691268b45b117ee`. The current main implementation differs materially from the original branch (`main...codex/rf-job-facade-01` = 73/70 commits; 706 paths in direct tree comparison), so the stale branch code is deliberately not merged over newer main code. The original branch ref is retained as a traceable archive. Current mainline tests must be run against the re-landed implementation.
