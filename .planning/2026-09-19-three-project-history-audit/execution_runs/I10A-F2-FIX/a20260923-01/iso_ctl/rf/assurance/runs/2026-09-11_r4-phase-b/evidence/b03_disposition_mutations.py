"""Are the B03 review dispositions load-bearing?  Three mutations, each
removing exactly one fix, must be killed by the case that claims to guard it.

Run from the worktree:  python %TEMP%\\b03_disposition_mutations.py
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

WT = Path(tempfile.gettempdir()) / "cw-b06-wt"
RESOLVER = WT / "src" / "company_wiki" / "source_catalog" / "resolver.py"
BACKUP = Path(tempfile.gettempdir()) / "b03-disposition-resolver.bak"

TAIL_GUARD = """    if budget is not None and budget.cancelled:
        # TAIL GUARD (B-VR03-04)"""

INLOOP = """                if budget is not None and budget.cancelled:
                    # Cancellation is sticky caller intent: never answer, even
                    # with bytes that are already in hand.
                    return None, B03_ERROR_UNAVAILABLE, "cancelled", str(read)
"""

PIN = """        if expected_content_sha256 and expected_content_sha256 != handle.content_sha256:
            return ByteReadResult("""

MUTATIONS = {
    "tail_guard_off": (
        TAIL_GUARD,
        "    if False:  # MUTANT: tail guard removed\n        # TAIL GUARD (B-VR03-04)",
        "tests/contract/test_r4b03_stable_bytes.py::test_r4b03_cancellation_inside_the_last_read_is_honoured",
    ),
    "inloop_cancel_off": (
        INLOOP,
        "",
        "tests/contract/test_r4b03_stable_bytes.py::test_r4b03_cancellation_stops_the_read_early",
    ),
    "version_pin_off": (
        PIN,
        "        if False:  # MUTANT: version pin removed\n            return ByteReadResult(",
        "tests/contract/test_r4b03_stable_bytes.py::test_r4b03_caller_supplied_version_is_pinned_to_the_handle",
    ),
}


def main() -> int:
    shutil.copy2(RESOLVER, BACKUP)
    original = RESOLVER.read_text(encoding="utf-8")
    failures = 0
    try:
        for name, (needle, replacement, test) in MUTATIONS.items():
            if needle not in original:
                print(f"{name}: PATTERN NOT FOUND (harness is stale)")
                failures += 1
                continue
            RESOLVER.write_text(
                original.replace(needle, replacement, 1), encoding="utf-8", newline=""
            )
            result = subprocess.run(
                [sys.executable, "-m", "pytest", test, "-q", "--no-header", "-x"],
                cwd=str(WT), capture_output=True, text=True,
                encoding="utf-8", errors="replace",
            )
            killed = result.returncode != 0
            print(f"{name}: {'KILLED' if killed else 'SURVIVED'}  ({test.rsplit('::', 1)[-1]})")
            if not killed:
                failures += 1
            RESOLVER.write_text(original, encoding="utf-8", newline="")
    finally:
        shutil.copy2(BACKUP, RESOLVER)
    check = RESOLVER.read_text(encoding="utf-8") == original
    print("restored byte-identically:", check)
    return 1 if failures or not check else 0


if __name__ == "__main__":
    raise SystemExit(main())
