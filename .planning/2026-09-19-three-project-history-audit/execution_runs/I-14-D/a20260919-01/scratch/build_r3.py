"""Scratch: build iso/product_narrow_r3 from the r2 deliverable and verify the delta."""
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

A = Path(__file__).resolve().parents[1]
PY = A / "iso" / "venv" / "Scripts" / "python.exe"
REL = Path("src") / "company_wiki" / "source_catalog" / "observability.py"

R2_TREE = A / "iso" / "product_narrow"
R3_TREE = A / "iso" / "product_narrow_r3"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


print("r2 deliverable:", sha(R2_TREE / REL), (R2_TREE / REL).stat().st_size)

if R3_TREE.exists():
    shutil.rmtree(R3_TREE)
shutil.copytree(R2_TREE, R3_TREE, symlinks=True)
print("copied ->", R3_TREE)

proc = subprocess.run([str(PY), "-B", str(A / "harness" / "apply_i14d_narrow.py"),
                       "--op", "genericscheme", "--tree", str(R3_TREE)],
                      capture_output=True, text=True, encoding="utf-8",
                      errors="replace")
print("op rc:", proc.returncode)
print(proc.stdout, proc.stderr)

print("r3 deliverable:", sha(R3_TREE / REL), (R3_TREE / REL).stat().st_size)

# the delta must be exactly one file
import filecmp
diffs = []
for base, _dirs, files in __import__("os").walk(R3_TREE):
    for f in files:
        p = Path(base) / f
        q = R2_TREE / p.relative_to(R3_TREE)
        if not q.is_file() or not filecmp.cmp(p, q, shallow=False):
            diffs.append(str(p.relative_to(R3_TREE)))
print("files differing from r2:", len(diffs), diffs)

# and the definition in the tree must equal the assembled one
spec_src = (R3_TREE / REL).read_text(encoding="utf-8")
import re
m = re.search(r"^_AUTH_SCHEME_SPLIT = .*?\n(?: .*\n)*", spec_src, re.M)
print()
print("=== tree definition ===")
print(m.group(0).rstrip())

sys.path.insert(0, str(R3_TREE / "src"))
from company_wiki.source_catalog.observability import redact_text
SEC = "ghp_ZQ7ReviewerFakeCredential0123456789"
M = "SYNTHETIC_AUDIT_TOKEN"
CASES = [
    ("C1", "Authorization: Negotiate\n" + SEC + "\ndoc=17", "Authorization: <redacted>\ndoc=17"),
    ("C2", "Authorization: AWS4-HMAC-SHA256\n" + SEC + "\ndoc=17", "Authorization: <redacted>\ndoc=17"),
    ("C3", "Authorization: SCRAM-SHA-256\n" + SEC + "\ndoc=17", "Authorization: <redacted>\ndoc=17"),
    ("C4", "Authorization: Hawk\n" + SEC + "\ndoc=17", "Authorization: <redacted>\ndoc=17"),
    ("C5", "Authorization: Bot\n" + SEC + "\ndoc=17", "Authorization: <redacted>\ndoc=17"),
    ("C6", "Authorization: Mutual\n" + SEC + "\ndoc=17", "Authorization: <redacted>\ndoc=17"),
    ("C7", "Authorization: vapid\n" + SEC + "\ndoc=17", "Authorization: <redacted>\ndoc=17"),
    ("C8", "Authorization: HOBA\n" + SEC + "\ndoc=17", "Authorization: <redacted>\ndoc=17"),
    ("C9", "Authorization: Zzz\n" + SEC + "\ndoc=17", "Authorization: <redacted>\ndoc=17"),
    ("C10", "Authorization: Bearer abc\n" + SEC, "Authorization: <redacted>"),
    ("C11", "Authorization: Bearer\n\n" + SEC, "Authorization: <redacted>"),
    ("C12", 'Authorization: Bearer\n"' + SEC + '"', "Authorization: <redacted>"),
    ("NEG", "Authorization: Negotiate\n" + M + "\ndoc=17", "Authorization: <redacted>\ndoc=17"),
]
print()
fails = 0
for cid, text, want in CASES:
    got = redact_text(text)
    ok = got == want
    fails += 0 if ok else 1
    print(f"{cid:5s} {'ok  ' if ok else 'FAIL'} {got!r}")
print("residual-variant failures:", fails)
