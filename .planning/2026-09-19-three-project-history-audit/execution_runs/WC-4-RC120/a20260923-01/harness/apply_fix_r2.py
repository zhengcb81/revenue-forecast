"""WC-4 r2 fix applicator / mutation switch for the ISO tree ONLY.

States
  r2          : delivered r2 bytes (r1 finalization wrapper + the F-01 wrapper
                that also covers SystemExit raised inside main())
  r1          : r1 delivery bytes (wrapper only around main()'s return value)
  mut2_nocatch: r2 wrapper + _finalize_exit_status keeps the catch but loses the
                stream neutralization (r1 oracle M-2, re-run with the r2 wrapper)
  mut3_neutralonly: r2 wrapper + _finalize_exit_status neutralizes the broken
                stream but never turns the failure into rc=2 / product text
                (supplementary arm added in r2 for reviewer finding F-08)

Every transition is byte-reproducible from the snapshots
evidence/rgm2/cli_r1_state.py and evidence/rgm2/cli_r2_state.py.
Production is never touched; nothing outside the attempt directory is written.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
CLI = ATTEMPT / "iso" / "rf" / "scripts" / "revenue_forecast.py"
R1_SNAP = ATTEMPT / "evidence" / "rgm2" / "cli_r1_state.py"
R2_SNAP = ATTEMPT / "evidence" / "rgm2" / "cli_r2_state.py"

MAIN_GUARD = 'if __name__ == "__main__":'
R1_ENTRY = "    raise SystemExit(_finalize_exit_status(main()))\n"
R2_MARKER = "    except SystemExit as _system_exit:\n"

MUT2_ANCHOR = '        _neutralize_broken_stream("stdout")\n        return 2'
MUT2_REPLACEMENT = "        return 2"

MUT3_OLD = '''    except (OSError, ValueError) as exc:
        try:
            print(f"error: stdout flush failed: {exc}", file=sys.stderr)
            sys.stderr.flush()
        except (OSError, ValueError):
            _neutralize_broken_stream("stderr")
        _neutralize_broken_stream("stdout")
        return 2
'''
MUT3_NEW = '''    except (OSError, ValueError):
        _neutralize_broken_stream("stdout")
'''


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def state(text: str) -> str:
    if "def _finalize_exit_status" not in text:
        return "pristine"
    if R2_MARKER not in text:
        return "r1"
    if MUT3_NEW in text:
        return "mut3_neutralonly"
    if MUT2_ANCHOR not in text:
        return "mut2_nocatch"
    return "r2"


def write(text: str, label: str) -> None:
    CLI.write_text(text, encoding="utf-8", newline="\n")
    print(f"{label}: cli_sha256={sha(CLI)} state={state(text)}")


def to_r1(text: str) -> str:
    index = text.index(MAIN_GUARD)
    return text[:index] + MAIN_GUARD + "\n" + R1_ENTRY


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "mode",
        choices=["status", "restore", "revert_wrap", "mut2", "mut3"],
    )
    args = parser.parse_args()
    text = CLI.read_text(encoding="utf-8")

    if args.mode == "status":
        print(f"cli_sha256={sha(CLI)} state={state(text)}")
        return 0

    if args.mode == "restore":
        write(R2_SNAP.read_text(encoding="utf-8"), "restore->r2")
        return 0

    if state(text) != "r2":
        raise SystemExit(f"mode {args.mode} requires state=r2, found {state(text)}")

    if args.mode == "revert_wrap":
        # reviewer mutation 1: put the wrapper back around main()'s return
        # value only, i.e. re-create the r1 delivery bytes exactly
        new_text = to_r1(text)
        if state(new_text) != "r1":
            raise SystemExit("revert_wrap did not reach r1 state")
        if new_text != R1_SNAP.read_text(encoding="utf-8"):
            raise SystemExit("revert_wrap is not byte-identical to the r1 snapshot")
        write(new_text, "r2->r1 (mutation 1: wrapper reverted)")
        return 0

    if args.mode == "mut2":
        if MUT2_ANCHOR not in text:
            raise SystemExit("mut2 anchor not found")
        new_text = text.replace(MUT2_ANCHOR, MUT2_REPLACEMENT, 1)
        if state(new_text) != "mut2_nocatch":
            raise SystemExit("mut2 did not reach mut2_nocatch state")
        write(new_text, "r2->mut2_nocatch (mutation 2: catch without neutralize)")
        return 0

    if MUT3_OLD not in text:
        raise SystemExit("mut3 anchor not found")
    new_text = text.replace(MUT3_OLD, MUT3_NEW, 1)
    if state(new_text) != "mut3_neutralonly":
        raise SystemExit("mut3 did not reach mut3_neutralonly state")
    write(new_text, "r2->mut3_neutralonly (mutation 3: neutralize without catch)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
