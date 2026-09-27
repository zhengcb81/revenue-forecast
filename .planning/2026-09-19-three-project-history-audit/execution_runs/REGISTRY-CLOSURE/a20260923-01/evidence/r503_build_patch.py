# R5-03 patch: disambiguate the F-REV-R4-01 correction sentence (comment-only, both targets).
# Old (ambiguous; reading "indentation of the redacted line is not consumed" is false):
#   "# breaks are consumed by the match; the indentation and the keys on the lines AFTER"
#   "# the redacted one are not."
# New (reviewer's demanded single reading — the indentation that FOLLOWS the breaks is
# consumed; the keys on the lines AFTER the redacted one are not):
#   "# breaks and the indentation that FOLLOWS them are consumed by the match; the keys"
#   "# on the lines AFTER the redacted one are not."
import difflib
import py_compile
from pathlib import Path

ATTEMPT = Path(r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\REGISTRY-CLOSURE\a20260923-01")
ORIG = Path(r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\I-14-D\a20260919-01\iso\product_narrow_r6\src\company_wiki\source_catalog\observability.py")
PROD = Path(r"C:\Users\郑曾波\Projects\company-wiki\src\company_wiki\source_catalog\observability.py")

L1_OLD = b"# breaks are consumed by the match; the indentation and the keys on the lines AFTER"
L1_NEW = b"# breaks and the indentation that FOLLOWS them are consumed by the match; the keys"
L2_OLD = b"# the redacted one are not."
L2_NEW = b"# on the lines AFTER the redacted one are not."

for name, src, out, tgt in (
    ("r6tree", ORIG, ATTEMPT / "fix_r503" / "observability_r6tree_r503.py",
     ("a/iso/product_narrow_r6/src/company_wiki/source_catalog/observability.py",
      "b/iso/product_narrow_r6/src/company_wiki/source_catalog/observability.py")),
    ("production", PROD, ATTEMPT / "fix_r503" / "observability_production_r503.py",
     ("a/src/company_wiki/source_catalog/observability.py",
      "b/src/company_wiki/source_catalog/observability.py")),
):
    data = src.read_bytes()
    print(name, "anchor_counts:", data.count(L1_OLD), data.count(L2_OLD))
    if data.count(L1_OLD) != 1 or data.count(L2_OLD) != 1:
        continue
    new = data.replace(L1_OLD, L1_NEW).replace(L2_OLD, L2_NEW)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(new)
    diff = "".join(difflib.unified_diff(
        data.decode("utf-8").splitlines(keepends=True),
        new.decode("utf-8").splitlines(keepends=True),
        fromfile=tgt[0], tofile=tgt[1], n=3))
    (ATTEMPT / "evidence" / f"r503_patch_{name}.diff").write_text(diff, encoding="utf-8", newline="")
    ops = [op for op in difflib.SequenceMatcher(None, data, new).get_opcodes() if op[0] != "equal"]
    print(name, "opcodes:", ops)
    try:
        py_compile.compile(str(out), doraise=True, cfile=str(ATTEMPT / "fix_r503" / f"_{name}.pyc"))
        print(name, "compile: OK")
    except Exception as e:  # noqa: BLE001
        print(name, "compile:", repr(e))
