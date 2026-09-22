"""Independent class-level sweep of the pre-break token class.

Loads each generation's observability.py standalone and asks, for every character
c at the scheme position, whether `Authorization: Bo{c}t` + break + credential
leaks.  Also sweeps the whole printable complement of the r5 class and of the
RFC-7230 tchar class.  Read-only: nothing under the attempt is written.
"""
from __future__ import annotations
import importlib.util, json, os, string, sys

ATT = r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\I-14-D\a20260919-01"
TREES = {
    "base": r"iso\product_base\src\company_wiki\source_catalog\observability.py",
    "r2":   r"iso\product_narrow\src\company_wiki\source_catalog\observability.py",
    "r3":   r"iso\product_narrow_r3\src\company_wiki\source_catalog\observability.py",
    "r4":   r"iso\product_narrow_r4\src\company_wiki\source_catalog\observability.py",
    "r5":   r"iso\product_narrow_r5\src\company_wiki\source_catalog\observability.py",
}
MARKER = "SYNTHETIC_AUDIT_TOKEN"
CRED39 = "ghp_ZQ7ReviewerFakeCredential0123456789"

def load(name, rel):
    path = os.path.join(ATT, rel)
    spec = importlib.util.spec_from_file_location("obs_" + name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = m          # dataclass() resolves cls.__module__ here
    spec.loader.exec_module(m)
    return m

MODS = {k: load(k, v) for k, v in TREES.items()}

def leaks(mod, text):
    out = mod.redact_text(text)
    return (MARKER in out) or (CRED39 in out), out

# ---------------------------------------------------------------- sweep 1
# every printable char in the pre-break token position, then a break, then a
# credential whose line has no key= prefix.
TCHAR = set(string.ascii_letters + string.digits + "!#$%&'*+-.^_`|~")
R5CLS = set(chr(c) for c in range(32, 127)) - set(" \t,;&\"'|")   # inside [^\s,;&"'|]

rows = []
for ch in string.printable:
    if ch in "\n\r\x0b\x0c":
        continue
    for form, text in (
        ("marker",   f"Authorization: Bo{ch}t\n{MARKER}"),
        ("cred+key", f"Authorization: Bo{ch}t\n{CRED39}\ndoc=17"),
    ):
        rec = {"char": ch, "cp": hex(ord(ch)), "form": form,
               "in_tchar": ch in TCHAR, "in_r5class": ch in R5CLS}
        for gen, mod in MODS.items():
            lk, out = leaks(mod, text)
            rec[gen] = "LEAK" if lk else "ok"
        rows.append(rec)

print("== SWEEP: `Authorization: Bo<c>t` + LF + credential ==")
print(f"{'char':>6} {'cp':>6} {'tchar':>5} {'r5cls':>5} | " + " ".join(f"{g:>4}" for g in MODS))
hdr = None
interesting = []
for rec in rows:
    if rec["form"] != "marker":
        continue
    line = f"{rec['char']!r:>6} {rec['cp']:>6} {str(rec['in_tchar']):>5} {str(rec['in_r5class']):>5} | " + \
           " ".join(f"{rec[g]:>4}" for g in MODS)
    print(line)
    if rec["r5"] == "LEAK":
        interesting.append(rec["char"])

print()
print("chars at the pre-break position that LEAK on r5 (marker form):")
print("  ", "".join(repr(c) for c in interesting))
print()
print("chars where r4 = ok but r5 = LEAK  (r5 regression vs its own pre-image):")
reg = [r["char"] for r in rows if r["form"] == "marker" and r["r4"] == "ok" and r["r5"] == "LEAK"]
print("  ", "".join(repr(c) for c in reg))
print("chars where base = ok but r5 = LEAK  (base-regressive on r5):")
basreg = [r["char"] for r in rows if r["form"] == "marker" and r["base"] == "ok" and r["r5"] == "LEAK"]
print("  ", "".join(repr(c) for c in basreg))
print("chars where base = ok but r4 = LEAK  (base-regressive on r4, the F-REV-R4-05 family):")
basreg4 = [r["char"] for r in rows if r["form"] == "marker" and r["base"] == "ok" and r["r4"] == "LEAK"]
print("  ", "".join(repr(c) for c in basreg4))

# ---------------------------------------------------------------- sweep 2
# the cred+key form, to see whether the diagnostic key survives
print()
print("== SWEEP: `Authorization: Bo<c>t` + LF + cred39 + LF + `doc=17` ==")
for rec in rows:
    if rec["form"] != "cred+key":
        continue
    if rec["r5"] == "ok" and rec["r4"] == "ok" and rec["base"] == "ok":
        continue
    print(f"{rec['char']!r:>6} {rec['cp']:>6} tchar={str(rec['in_tchar']):>5} r5cls={str(rec['in_r5class']):>5} | " +
          " ".join(f"{rec[g]:>4}" for g in MODS))

# ---------------------------------------------------------------- sweep 3
# the four registered shapes, explicit
print()
print("== THE FOUR REGISTERED SHAPES (C5.2) ==")
for label, text, exp in (
    ("N5p", f"Authorization: Bo?t\n{MARKER}", "Authorization: <redacted>"),
    ("N5q", f"Authorization: Bo/t\n{CRED39}\ndoc=17", "Authorization: <redacted>\ndoc=17"),
    ("N5r", f"Authorization: Bo:t\n{MARKER}", "Authorization: <redacted>"),
    ("N5s", f"Authorization: Bo=t\n{MARKER}", "Authorization: <redacted>"),
):
    out = MODS["r5"].redact_text(text)
    print(f"{label}: ok={out == exp} expected={exp!r} got={out!r}")

# ---------------------------------------------------------------- sweep 4
# whole-class membership test: is every char r5's class EXCLUDES also excluded by
# r4's class?  (i.e. is the r5 class a superset of the r4 class?)
r4cls = TCHAR
print()
print("r5 class = [^\\s,;&\"'|]  ; r4 class = RFC7230 tchar")
print("chars IN r4's class but NOT in r5's class:",
      sorted(c for c in r4cls if c not in R5CLS))
print("chars IN r5's class but NOT in r4's class:",
      sorted(c for c in R5CLS if c not in r4cls))
print("=> r5 class is a SUPERSET of r4 class:", set(r4cls) <= R5CLS)
