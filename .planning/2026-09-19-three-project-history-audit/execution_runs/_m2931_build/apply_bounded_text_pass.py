import argparse
import datetime
import hashlib
import json
import os
import shutil

# NOTE (2026-09-20): this first-pass file was mangled twice by the authoring tool while it was being
# written and is NOT the tool of record.  The bounded-text pass that actually ran for M29/M30/M31 is
# _m2931_build/apply_bounded_pass.py (its sha256 is recorded in each attempt's
# recovery/bounded_text_pass.json), and its per-attempt results are in recovery/bounded_text_pass.json
# plus evidence/<CARD>/verdict_confirmation_check.txt.  Nothing imports this file; it is kept only so
# that the failed authoring attempt stays auditable.
TOOL_OF_RECORD = "apply_bounded_pass.py"
STATUS = "superseded: never executed successfully; superseded by " + TOOL_OF_RECORD


def main():
    print("this file is superseded and must not be used; use", TOOL_OF_RECORD)
    print(STATUS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
