"""Deterministic fix applicator for WC-4 = F12-RC120 (iso tree only).

Modes
  apply    : install the flush-failure normalization into iso's CLI
  revert   : restore the pristine CLI bytes (MUTATION-1: whole normalization gone)
  mutate2  : keep the in-domain catch but drop the stream neutralization
             (MUTATION-2: predicted to still exit 120, oracle M-2)
  status   : report which state the iso CLI is in

The pristine bytes are snapshotted once at evidence/rgm/cli_original.py so every
transition is byte-reproducible.  Production is never touched.
"""
from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
CLI = ATTEMPT / "iso" / "rf" / "scripts" / "revenue_forecast.py"
ORIGINAL = ATTEMPT / "evidence" / "rgm" / "cli_original.py"

TAIL = '''    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''

FIXED_TAIL = '''    return 0


def _neutralize_broken_stream(name: str) -> None:
    """WC-4 (F12): detach a std stream whose flush just failed so the CPython
    interpreter-shutdown flush cannot rewrite the process exit status (a failing
    shutdown flush makes CPython self-report 120; measured - see the card oracle
    mechanism erratum)."""
    try:
        setattr(sys, name, open(os.devnull, "w", encoding="utf-8"))
        return
    except OSError:
        pass

    class _NullStream:
        def write(self, text: str) -> int:
            return len(text)

        def flush(self) -> None:
            return None

    setattr(sys, name, _NullStream())


def _finalize_exit_status(rc: int) -> int:
    """WC-4 (F12, owner ruling "to be repaired"): a stdout delivery failure at
    process exit must stay inside the frozen rc domain {0, 2} instead of being
    overridden by CPython's shutdown-flush status (measured rc=120).

    Behavior changes ONLY when flushing stdout here raises: the CLI reports
    rc=2 (the existing error class), keeps the flush error on stderr, and
    neutralizes the broken stream so finalization cannot override the status.
    When the flush succeeds the incoming rc is returned untouched.
    """
    try:
        sys.stdout.flush()
    except (OSError, ValueError) as exc:
        try:
            print(f"error: stdout flush failed: {exc}", file=sys.stderr)
            sys.stderr.flush()
        except (OSError, ValueError):
            _neutralize_broken_stream("stderr")
        _neutralize_broken_stream("stdout")
        return 2
    return rc


if __name__ == "__main__":
    raise SystemExit(_finalize_exit_status(main()))
'''

MUTATE2_FIXED_TAIL = FIXED_TAIL.replace(
    '        _neutralize_broken_stream("stdout")\n        return 2',
    '        return 2',
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def state(text: str) -> str:
    if "def _finalize_exit_status" not in text:
        return "pristine"
    if '        _neutralize_broken_stream("stdout")\n        return 2' in text:
        return "fixed"
    return "mutate2"


def write(new_text: str, label: str) -> None:
    CLI.write_text(new_text, encoding="utf-8", newline="\n")
    print(f"{label}: cli_sha256={sha(CLI)} state={state(new_text)}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["apply", "revert", "mutate2", "status"])
    args = parser.parse_args()

    if args.mode == "status":
        print(f"cli_sha256={sha(CLI)} state={state(CLI.read_text(encoding='utf-8'))}")
        return 0

    if args.mode == "revert":
        if not ORIGINAL.exists():
            raise SystemExit("pristine snapshot missing")
        text = ORIGINAL.read_text(encoding="utf-8")
        if state(text) != "pristine":
            raise SystemExit("snapshot is not pristine")
        write(text, "revert->pristine")
        return 0

    if not ORIGINAL.exists():
        current = CLI.read_text(encoding="utf-8")
        if state(current) != "pristine":
            raise SystemExit("refusing: iso CLI not pristine and no snapshot yet")
        shutil.copyfile(CLI, ORIGINAL)
        print(f"snapshot pristine cli -> {ORIGINAL} sha256={sha(ORIGINAL)}")

    text = CLI.read_text(encoding="utf-8")
    current = state(text)
    if args.mode == "apply":
        if current == "fixed":
            print(f"already fixed: cli_sha256={sha(CLI)}")
            return 0
        if current == "mutate2":
            # Rebuild from the pristine snapshot instead of string surgery on a
            # half-reverted body (first attempt at that surgery failed - see
            # commands.md P1, attempt recorded as a failed non-evidence try).
            base = ORIGINAL.read_text(encoding="utf-8")
            if state(base) != "pristine" or TAIL not in base:
                raise SystemExit("pristine snapshot unusable")
            new_text = base.replace(TAIL, FIXED_TAIL, 1)
            if state(new_text) != "fixed":
                raise SystemExit("mutate2 -> fixed rebuild did not reach fixed state")
            write(new_text, "mutate2->fixed")
            return 0
        if TAIL not in text:
            raise SystemExit("apply anchor (module tail) not found")
        new_text = text.replace(TAIL, FIXED_TAIL, 1)
        if new_text == text:
            raise SystemExit("apply made no change")
        write(new_text, "apply->fixed")
        return 0

    if args.mode == "mutate2":
        if state(text) != "fixed":
            raise SystemExit(f"mutate2 requires fixed state, found {state(text)}")
        new_text = text.replace(
            '        _neutralize_broken_stream("stdout")\n        return 2\n    return rc',
            '        return 2\n    return rc',
            1,
        )
        if new_text == text:
            raise SystemExit("mutate2 anchor not found")
        write(new_text, "fixed->mutate2")
        return 0

    raise SystemExit(f"unhandled mode {args.mode}")


if __name__ == "__main__":
    raise SystemExit(main())
