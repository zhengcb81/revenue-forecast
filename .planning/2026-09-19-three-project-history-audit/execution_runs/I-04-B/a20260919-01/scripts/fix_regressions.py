"""I-04-B: fix the two consequences the first GREEN run exposed.

(a) PRODUCT-side (author bug in the iso patch): `_stamp_request_timing` was called at
    the top of the `except FilingFetchError` handler, but a request_error is raised
    BEFORE `stats`/`started_monotonic` exist -> UnboundLocalError.  Three existing
    request_error tests caught it.  Guarded instead.
(b) TEST-side clock scripts: the fix re-reads the budget after each subcall, so the
    scripted `time.monotonic` side_effect lists need one extra value per retry.  The
    observable expectations (2 calls, sleeps [5, 3], attempts=2) are UNCHANGED - only
    the fixture's clock script is corrected, never the assertion.
"""
from __future__ import annotations

import pathlib

ATTEMPT = pathlib.Path(__file__).resolve().parents[1]
ISO = ATTEMPT / "iso" / "filing-fetch"
TARGET = ISO / "scripts" / "fetch_filing.py"
TESTS = ISO / "tests" / "test_fetch_filing.py"

PRODUCT_FIXES = [
    (
        """    except FilingFetchError as exc:
        _stamp_request_timing(stats, started_monotonic, args.timeout_seconds)
        error_response: dict[str, Any] = {
""",
        """    except FilingFetchError as exc:
        # The request window only exists once the request itself started: a
        # request_error raised while parsing the input has neither `stats` nor a
        # start instant, so stamping is conditional (three existing request_error
        # tests caught the unconditional version with an UnboundLocalError).
        if "stats" in locals() and "started_monotonic" in locals():
            _stamp_request_timing(stats, started_monotonic, args.timeout_seconds)
        error_response: dict[str, Any] = {
""",
        "P-j5b guard-request-error-path",
    ),
]

TEST_FIXES = [
    (
        '                            "fetch_filing.time.monotonic",\n'
        '                            side_effect=[100.0, 100.0, 105.0, 108.0],\n',
        '                            "fetch_filing.time.monotonic",\n'
        '                            # I-04-B: one extra reading per retry - the budget is\n'
        '                            # re-read after each subcall (same expectations below).\n'
        '                            side_effect=[100.0, 100.0, 100.0, 105.0, 105.0, 108.0],\n',
        "test_failure_envelope clock script",
    ),
    (
        '                            "fetch_filing.time.monotonic", side_effect=[100.0, 100.0, 105.0, 108.0]\n',
        '                            # I-04-B: one extra reading per retry - the budget is re-read\n'
        '                            # after each subcall; the assertions below are unchanged.\n'
        '                            "fetch_filing.time.monotonic",\n'
        '                            side_effect=[100.0, 100.0, 100.0, 105.0, 105.0, 108.0],\n',
        "test_catalog_locked clock script",
    ),
]


def apply(path: pathlib.Path, fixes, label: str) -> list[str]:
    if "I-04-B" not in str(path):
        raise SystemExit(f"refusing to edit outside the I-04-B attempt: {path}")
    text = path.read_text(encoding="utf-8")
    problems: list[str] = []
    for old, new, name in fixes:
        count = text.count(old)
        if count != 1:
            problems.append(f"{label}/{name}: expected 1 match, found {count}")
            continue
        text = text.replace(old, new, 1)
        print(f"applied  {label}/{name}")
    if not problems:
        path.write_text(text, encoding="utf-8", newline="")
    return problems


def main() -> int:
    problems = apply(TARGET, PRODUCT_FIXES, "product")
    problems += apply(TESTS, TEST_FIXES, "tests")
    if problems:
        print("FAILED:", *problems, sep="\n  ")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
