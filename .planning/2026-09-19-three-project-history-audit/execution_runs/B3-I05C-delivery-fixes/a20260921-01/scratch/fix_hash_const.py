"""One-shot: correct the FIXED_CWS_SHA256 constant in both B3 test carriers."""
from pathlib import Path

TESTS = Path(__file__).resolve().parents[1] / "iso" / "fixed" / "tests"
WRONG = "7D1BD8F9D9122DC4A99465A8F9201E855417A5D0756F5BFDDD6D404F7CA9E48CE"
RIGHT = "7D1BD8F9D9122DC4A99465A8F9201E855417A5D0756F5BFDD6D404F7CA9E48CE"

for name in ("test_fc904_artifact_selection.py",
             "test_w05b_verified_artifact_read.py"):
    path = TESTS / name
    text = path.read_text(encoding="utf-8")
    assert WRONG in text, f"{name}: wrong constant not found"
    path.write_text(text.replace(WRONG, RIGHT), encoding="utf-8")
    print(f"fixed {name}")

# sanity: no stray concatenations left behind
for name in ("test_fc904_artifact_selection.py",
             "test_w05b_verified_artifact_read.py",
             "test_w05c_minimal_production.py"):
    path = TESTS / name
    text = path.read_text(encoding="utf-8")
    compile(text, str(path), "exec")
    print(f"compiles OK: {name}")
