"""I-14-C: the shared binding guard for the two subprocess drivers.

r5 (reviewer "unable to verify" item 1): the r4 guard required the run dir to live under
``execution_runs``, so an independent reviewer could only use ``%TEMP%`` and the 17
subprocess-backed cases were refused with 97 - the full 82-case suite was therefore NOT
independently runnable.  The guard is now split along the axis that matters:

* REFUSE anything that is a product path, always:
    - any path containing ``.source_catalog``;
    - any path inside the ``company-wiki`` / ``filing-fetch`` checkouts;
    - any path inside the ``revenue-forecast`` checkout that is NOT under ``.planning``;
* ALLOW a run dir when either it is under ``execution_runs`` (the attempt's own layout), or
  the caller declares a scratch root through ``I14C_RUN_ROOT`` and the run dir lives inside
  it.  The declared root is itself checked against the product rules.

So a reviewer can point ``I14C_RUN_ROOT`` at their own scratch directory and run everything,
while a typo that aims a run at a product tree is still refused.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

PRODUCT_REPOS = ("company-wiki", "filing-fetch", "revenue-forecast")
REFUSAL_EXIT = 97


def _product_violation(resolved: Path) -> str | None:
    parts = list(resolved.parts)
    lowered = [part.lower() for part in parts]
    if ".source_catalog" in lowered:
        return "path contains .source_catalog (a live catalog directory)"
    if "company-wiki" in lowered or "filing-fetch" in lowered:
        return "path is inside a product checkout"
    if "revenue-forecast" in lowered and ".planning" not in lowered:
        return "path is inside the revenue-forecast checkout but outside .planning"
    return None


def guard_run_dir(run_dir: str | Path) -> Path | None:
    """Return the resolved run dir, or print BINDING-REFUSED and return None."""
    resolved = Path(run_dir).resolve()
    violation = _product_violation(resolved)
    if violation is not None:
        print(f"BINDING-REFUSED ({violation}): {resolved}", file=sys.stderr)
        return None

    if "execution_runs" in [part.lower() for part in resolved.parts]:
        return resolved

    declared = os.environ.get("I14C_RUN_ROOT")
    if declared:
        root = Path(declared).resolve()
        if _product_violation(root) is None and (root == resolved or root in resolved.parents):
            return resolved
        print(f"BINDING-REFUSED (declared I14C_RUN_ROOT is unusable: {root})", file=sys.stderr)
        return None

    print(
        "BINDING-REFUSED (run dir is not under execution_runs and no scratch root was "
        f"declared through I14C_RUN_ROOT): {resolved}",
        file=sys.stderr,
    )
    return None
