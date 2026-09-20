"""Close the release-path R5 hole the decision.md author found by reading the code.

``_release_common_locked``'s R5 cell only covered "no owner evidence".  The bare
``else: reason = why`` fallback also accepted `owner_probe:alive`,
`owner_probe_timeout` and `owner_probe_error:*` — i.e. a LIVE third-party owner whose
lease is no longer in the ledger would be resumed.  R5's literal text forbids that:
only positive, attributable death evidence authorises a takeover.
"""

from __future__ import annotations

import pathlib
import sys

PATCHER = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\scratch\patch_i04d.py"
)

OLD = '''            else:
                reason = why
'''
NEW = '''            else:
                # R5, second cell: a LIVE (or unverifiable) third-party owner whose lease
                # is no longer in the ledger.  Resuming would undo a pause this tool never
                # created, and the owner cannot be proven dead, so this stays fail closed
                # exactly like the missing-evidence cell above.
                state.entries = []
                self._persist_locked(state, resume_required=False)
                self._release_done = True
                self.action = "released_owner_changed"
                self._cleanup_failure = f"failed:owner_evidence_changed:{why}:not_provably_dead"
                _lease_journal(
                    self.root,
                    "released_owner_changed",
                    lease_id=self.lease_id,
                    why=why,
                    owner=state.owner,
                )
                return
'''
text = PATCHER.read_text(encoding="utf-8")
if OLD not in text:
    print("PATTERN NOT FOUND")
    sys.exit(1)
PATCHER.write_text(text.replace(OLD, NEW, 1), encoding="utf-8")
print("release-path R5 hole closed")
