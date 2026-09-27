# Rebuild REM-05 patch byte-safely (CRLF-consistent insertion) + emit unified diff.
import difflib
from pathlib import Path

ATTEMPT = Path(r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\REGISTRY-CLOSURE\a20260923-01")
ORIG = Path(r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\I-14-D\a20260919-01\iso\product_narrow_r6\src\company_wiki\source_catalog\observability.py")
PROD = Path(r"C:\Users\郑曾波\Projects\company-wiki\src\company_wiki\source_catalog\observability.py")

ANCHOR = b'_VALUE = r"(?P<value>"'
COMMENT_LINES = [
    b"# _VALUE IS DEAD CODE (REM-05 / F-REV-D-02; annotated 2026-09-23 by REGISTRY-CLOSURE",
    b"# a20260923-01). This constant is referenced NOWHERE at runtime: _AUTH_PATTERN",
    b"# inlines `(?P<value>...|_AUTH_SCHEME_SPLIT|_AUTH_BARE_VALUE)` below and the",
    b"# assignment path is the hand-written scanner that uses _VALUE_STOP_CHARS.",
    b"# The load-bearing C13 narrowing is that scanner loop, NOT this constant.",
    b"# Deleting this constant outright is behaviour-neutral (probe evidence:",
    b"# execution_runs/REGISTRY-CLOSURE/a20260923-01/evidence/rem05_behavior_identity.txt).",
    b"# Do NOT \x22clean up\x22 _BARE_VALUE/_AUTH_BARE_VALUE/the scanner assuming this",
    b"# constant keeps the fix alive: it never had runtime effect (that is F-REV-D-02).",
]

def patched_bytes(src: Path):
    data = src.read_bytes()
    assert data.count(ANCHOR) == 1, f"anchor count != 1 in {src}"
    eol = b"\r\n" if b"\r\n" in data else b"\n"
    comment = eol.join(COMMENT_LINES) + eol
    return data.replace(ANCHOR, comment + ANCHOR), data, eol

for name, src, out in (
    ("r6tree", ORIG, ATTEMPT / "fix_rem05" / "observability_r6tree_annotated_full.py"),
    ("production", PROD, ATTEMPT / "fix_rem05" / "observability_production_annotated.py"),
):
    new, old, eol = patched_bytes(src)
    out.write_bytes(new)
    # unified diff with stable target paths
    old_txt = old.decode("utf-8").splitlines(keepends=True)
    new_txt = new.decode("utf-8").splitlines(keepends=True)
    tgt = ("a/iso/product_narrow_r6/src/company_wiki/source_catalog/observability.py",
           "b/iso/product_narrow_r6/src/company_wiki/source_catalog/observability.py") if name == "r6tree" else (
           "a/src/company_wiki/source_catalog/observability.py",
           "b/src/company_wiki/source_catalog/observability.py")
    diff = "".join(difflib.unified_diff(old_txt, new_txt, fromfile=tgt[0], tofile=tgt[1], n=3))
    (ATTEMPT / "evidence" / f"rem05_patch_{name}.diff").write_text(diff, encoding="utf-8", newline="")
    # sanity: only insertion
    sm = difflib.SequenceMatcher(None, old, new)
    ops = [op for op in sm.get_opcodes() if op[0] != "equal"]
    print(name, "opcodes:", ops, "eol:", "CRLF" if eol == b"\r\n" else "LF", "diff_lines:", diff.count("\n"))
