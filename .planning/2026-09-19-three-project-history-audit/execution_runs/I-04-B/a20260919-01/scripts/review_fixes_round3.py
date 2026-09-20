"""I-04-B review fixes, round 3: the last two fixture bugs in the new cases.

1. F-B4c: `_handle` is an instance method on the base test class, so it needs an
   instance (`FilingFetchTests()._handle(root)`).
2. F-B4d: seeding the refcount with OUR OWN pid makes `_register` append a duplicate
   (register appends unconditionally), which changes the probe count.  Seed a FOREIGN
   participant and assert the cap itself (every probe <= 20s) plus that CLI calls keep
   the uncapped phase budget - the point of reviewer finding F-B4B-01.
"""
from __future__ import annotations

import pathlib

ATTEMPT = pathlib.Path(__file__).resolve().parents[1]
TESTS = ATTEMPT / "iso" / "filing-fetch" / "tests" / "test_fetch_filing.py"

FIXES = [
    (
        "f-b4c-instance-method",
        '"matches": [FilingFetchTests._handle(root)],',
        '"matches": [FilingFetchTests()._handle(root)],',
    ),
    (
        "f-b4d-foreign-pid",
        '            (catalog / _PAUSE_REFCOUNT_NAME).write_text(\n'
        '                json.dumps([{"pid": os.getpid(), "joined": False}]), encoding="utf-8"\n'
        '            )\n',
        '            # a FOREIGN participant: seeding our own pid would make _register append a\n'
        '            # duplicate entry and change the probe count (register appends always)\n'
        '            (catalog / _PAUSE_REFCOUNT_NAME).write_text(\n'
        '                json.dumps([{"pid": 999999, "joined": False}]), encoding="utf-8"\n'
        '            )\n',
    ),
    (
        "f-b4d-cap-assertions",
        '            self.assertTrue(probes, "the probe must have run")\n'
        '            for grant in probes:\n'
        '                self.assertLessEqual(grant, _PID_PROBE_MAX_SECONDS)\n'
        '            self.assertEqual(len(probes), 2, "one probe per phase")\n',
        '            self.assertGreaterEqual(len(probes), 2, "a probe in each phase")\n'
        '            for grant in probes:\n'
        '                self.assertLessEqual(grant, _PID_PROBE_MAX_SECONDS)\n'
        '                self.assertGreater(grant, 0.0)\n',
    ),
]


def main() -> int:
    if "I-04-B" not in str(TESTS):
        raise SystemExit("refusing to edit outside the I-04-B attempt")
    text = TESTS.read_text(encoding="utf-8")
    problems: list[str] = []
    for name, old, new in FIXES:
        count = text.count(old)
        if count != 1:
            problems.append(f"{name}: expected 1 match, found {count}")
            continue
        text = text.replace(old, new, 1)
        print(f"applied  {name}")
    if problems:
        print("FAILED:", *problems, sep="\n  ")
        return 1
    TESTS.write_text(text, encoding="utf-8", newline="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
