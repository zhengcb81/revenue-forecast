"""Negative controls: every predicate I used must go RED on a mutated input.

1. hash predicate          -> flip one byte, the recomputation must differ
2. class sweep predicate   -> swap r5's class back to r4's, the leak set must change
3. row-by-row predicate    -> perturb one row, the comparison must report a diff
4. CRLF predicate          -> write LF, the uniformity check must fail
5. harness predicate       -> the r5 oracle must be sensitive to the class (via a
                              mutation tree built in memory, no file written)
"""
from __future__ import annotations
import hashlib, importlib.util, json, os, re, sys

ATT = r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\I-14-D\a20260919-01"
R5 = os.path.join(ATT, r"iso\product_narrow_r5\src\company_wiki\source_catalog\observability.py")
R4 = os.path.join(ATT, r"iso\product_narrow_r4\src\company_wiki\source_catalog\observability.py")
M = "SYNTHETIC_AUDIT_TOKEN"
S39 = "ghp_ZQ7ReviewerFakeCredential0123456789"
ok = lambda b: "RED (good)" if b else "GREEN (BAD: predicate cannot fail)"

print("== 1. hash predicate ==")
b = open(R5, "rb").read()
h0 = hashlib.sha256(b).hexdigest()
mut = bytearray(b); mut[b.find(b"_AUTH_PREBREAK_TOKEN")] = ord("X")
h1 = hashlib.sha256(bytes(mut)).hexdigest()
print(f"   clean  {h0}")
print(f"   mutated {h1}  differs={h0 != h1}  -> {ok(h0 != h1)}")

print("\n== 2. class sweep predicate ==")
def load(name, path, cls=None):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); sys.modules[name] = m
    spec.loader.exec_module(m)
    if cls is not None:
        m._AUTH_PREBREAK_TOKEN = cls
        m._AUTH_SCHEME_SPLIT = (r"(?:" + cls + r")[ \t]*"
                                r"(?:(?:\r?\n)[ \t]*)+"
                                r"(?:" + m._AUTH_BARE_VALUE + r"+|\"[^\"\r\n]*\"|'[^'\r\n]*')")
        m._AUTH_PATTERN = re.compile(
            r"(?i)(?P<key>" + m._LEFT_ANCHOR + r"authorization\s*[:=]\s*|"
            + m._LEFT_ANCHOR + r"bearer\s+)(?P<value>" + m._QUOTED_VALUE + r"|"
            + m._AUTH_SCHEME_SPLIT + r"|" + m._AUTH_BARE_VALUE + r")")
    return m

R4CLS = r"[A-Za-z0-9!#$%&'*+.^_`|~-]+"
clean = load("sweep_clean", R5)
mutd  = load("sweep_mut",   R5, R4CLS)

def leakset(mod, chars):
    return {c for c in chars if M in mod.redact_text(f"Authorization: Bo{c}t\n{M}")}

PROBE = "()/:<=>?@[\\]{}" + "&'|" + '",;'
lc = leakset(clean, PROBE); lm = leakset(mutd, PROBE)
print(f"   clean r5 class leak set : {''.join(sorted(lc))!r}")
print(f"   mutated (r4 class) set  : {''.join(sorted(lm))!r}")
print(f"   the sweep is sensitive to the class: {lc != lm}  -> {ok(lc != lm)}")
print(f"   (r4 class leaks {len(lm)} chars, r5 class leaks {len(lc)}; "
      f"r5\\r4={''.join(sorted(lc-lm))!r}  r4\\r5={''.join(sorted(lm-lc))!r})")

print("\n== 3. row-by-row predicate ==")
S = r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\_review_i14d_r5_20260922\scratch"
a = json.load(open(os.path.join(S, "r4oracle_on_product_narrow_r4.json"), encoding="utf-8"))
bb = json.load(open(os.path.join(S, "r4oracle_on_product_narrow_r5.json"), encoding="utf-8"))
ra = {r["id"]: r for r in a["rows"]}; rb = {r["id"]: r for r in bb["rows"]}
diff0 = [i for i in ra if ra[i] != rb[i]]
print(f"   as measured, differing rows = {len(diff0)} -> {ok(len(diff0) == 0)}")
ra2 = dict(ra); k = next(iter(ra2)); ra2[k] = dict(ra2[k]); ra2[k]["out"] = "PERTURBED"
diff1 = [i for i in ra2 if ra2[i] != rb[i]]
print(f"   after perturbing one row, differing rows = {len(diff1)} ({diff1[:1]}) -> {ok(len(diff1) == 1)}")

print("\n== 4. CRLF predicate ==")
crlf = b.count(bytes([13])) == b.count(bytes([10])) == b.count(bytes([13, 10]))
lfonly = b.replace(bytes([13, 10]), bytes([10]))
crlf2 = lfonly.count(bytes([13])) == lfonly.count(bytes([10])) == lfonly.count(bytes([13, 10]))
print(f"   r5 bytes uniformly CRLF = {crlf}  (CR {b.count(bytes([13]))} LF {b.count(bytes([10]))})")
print(f"   LF-rewritten: uniformly CRLF = {crlf2}  -> {ok(crlf and not crlf2)}")

print("\n== 5. the four registered shapes are sensitive to the class (in-memory mutation) ==")
ROWS = [("N5p", f"Authorization: Bo?t\n{M}", "Authorization: <redacted>"),
        ("N5q", f"Authorization: Bo/t\n{S39}\ndoc=17", "Authorization: <redacted>\ndoc=17"),
        ("N5r", f"Authorization: Bo:t\n{M}", "Authorization: <redacted>"),
        ("N5s", f"Authorization: Bo=t\n{M}", "Authorization: <redacted>")]
for rid, txt, exp in ROWS:
    c = clean.redact_text(txt) == exp
    m = mutd.redact_text(txt) == exp
    print(f"   {rid}: r5-class ok={c}  r4-class ok={m}  -> {ok(c and not m)}")
