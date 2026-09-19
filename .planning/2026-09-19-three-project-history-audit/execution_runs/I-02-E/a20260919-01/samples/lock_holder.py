"""lock_holder: scratch subprocess for the N2a DB-lock injection.

argv:
  python lock_holder.py <catalog_dir> <hold_seconds> <release_file>

Acquires the shared CatalogOperationLock(operation.lock) the same way the
normal import path does, holds it while <release_file> is absent, then
releases.  Records its PID to the given pid_file.  This child is spawned and
recorded by the w02e driver; only it is ever terminated.
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import w02e_bootstrap  # noqa: E402

w02e_bootstrap.setup("override")

from company_wiki.source_catalog.lock import CatalogOperationLock  # noqa: E402


def main() -> int:
    catalog_dir = Path(sys.argv[1])
    hold_file = Path(sys.argv[2])
    token_path = Path(sys.argv[3])
    with CatalogOperationLock(catalog_dir, operation="canonical_import"):
        token_path.write_text(str(os.getpid()), encoding="utf-8")
        deadline = time.monotonic() + 60.0
        while time.monotonic() < deadline:
            if hold_file.is_file():
                break
            time.sleep(0.05)
    return 0


if __name__ == "__main__":
    sys.exit(main())
