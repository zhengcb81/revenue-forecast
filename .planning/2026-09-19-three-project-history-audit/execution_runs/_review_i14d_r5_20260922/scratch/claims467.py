"""Claims 4, 6, 7: comment-block facts, over-redaction family, and the four new rows.

Also the break/indentation question the r5 comment makes a factual claim about.
"""
from __future__ import annotations
import importlib.util, json, os, re, sys

ATT = r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\I-14-D\a20260919-01"
TREES = {
    "base": r"iso\product_base\src\company_wiki\source_catalog\observability.py",
    "r2":   r"iso\product_narrow\src\company_wiki\source_catalog\observability.py",
    "r3":   r"iso\product_narrow_r3\src\company_wiki\source_catalog\observability.py",
    "r4":   r"iso\product_narrow_r4\src\company_wiki\source_catalog\observability.py",
    "r5":   r"iso\product_narrow_r5\src\company_wiki\source_catalog\observability.py",
}
M = "SYNTHETIC_AUDIT_TOKEN"
S39 = "ghp_ZQ7ReviewerFakeCredential0123456789"

def load(name, rel):
    p = os.path.join(ATT, rel)
    spec = importlib.util.spec_from_file_location("obs_" + name, p)
    m = importlib.util.module_from_spec(spec); sys.modules[spec.name] = m
    spec.loader.exec_module(m); return m

MODS = {k: load(k, v) for k, v in TREES.items()}

def show(label, text, gens=("base", "r2", "r3", "r4", "r5")):
    print(f"\n-- {label}")
    print(f"   in : {text!r}")
    for g in gens:
        out = MODS[g].redact_text(text)
        print(f"   {g:>4}: {out!r}  (len {len(out)})  marker_leaks={M in out} cred_leaks={S39 in out}")

print("=" * 78)
print("CLAIM 7 — the r5 comment block's factual claims, tested")
print("=" * 78)
# (a) "The breaks are consumed by the match"
show("(a) break consumed?  Authorization: Bearer<LF><marker>",
     f"Authorization: Bearer\n{M}")
# (b) "the indentation ... [is] not [consumed]"
show("(b) indentation consumed?  Authorization: Bearer<LF>  <marker>  (N5d)",
     f"Authorization: Bearer\n  {M}")
show("(b2) indentation before a FOLLOWING line",
     f"Authorization: Bearer\n{M}\n  doc=17")
# (c) "Fail CLOSED: after that token and one or more line breaks (a blank line included)"
show("(c) blank line included?  Authorization: Hawk<LF><LF><cred>  (N5j)",
     f"Authorization: Hawk\n\n{S39}")
# (d) "`Authorization: Bearer` + newline DELETES `doc=17`"
show("(d) over-redaction cost", "Authorization: Bearer\ndoc=17")
# (e) "no RFC scheme production is claimed any more" / "the token is now whatever the
#      value grammar calls a token" — the class is the value-token class
print("\n-- (e) is _AUTH_PREBREAK_TOKEN byte-identical to the token inside _AUTH_BARE_VALUE?")
r5 = MODS["r5"]
print("   _AUTH_PREBREAK_TOKEN =", repr(r5._AUTH_PREBREAK_TOKEN))
print("   _AUTH_BARE_VALUE     =", repr(r5._AUTH_BARE_VALUE))
print("   _BARE_VALUE          =", repr(r5._BARE_VALUE))
print("   equal:", r5._AUTH_PREBREAK_TOKEN == r5._BARE_VALUE)

# (f) "One shape stays OPEN and is registered rather than hidden: a TWO-token value that then wraps"
show("(f) the registered open shape (R3a)", f"Authorization: Bearer abc\n{S39}")
show("(f2) the 'two-token' shape in the comment's own terms",
     f"Authorization: Bearer abc\n{S39}\ndoc=17")

# (g) is the sentence 'One shape stays OPEN' an exhaustive count?
print("\n-- (g) shapes that stay OPEN and are NOT in the registered set:")
for probe, txt in (
    ("comma-in-token",   f"Authorization: Bo,t\n{M}"),
    ("semi-in-token",    f"Authorization: Bo;t\n{M}"),
    ("dquote-in-token",  f'Authorization: Bo"t\n{M}'),
    ("amp-in-token",     f"Authorization: Bo&t\n{M}"),
    ("squote-in-token",  f"Authorization: Bo't\n{M}"),
    ("pipe-in-token",    f"Authorization: Bo|t\n{M}"),
    ("space-in-token",   f"Authorization: Bo t\n{M}"),
):
    out = r5.redact_text(txt)
    print(f"   {probe:>18}: leaks={M in out}  out={out!r}")

print()
print("=" * 78)
print("CLAIM 6 — over-redaction family, r4 vs r5")
print("=" * 78)
OVER = [
    ("over-auth-scheme-then-key",   "Authorization: Bearer\ndoc=17"),
    ("over-auth-scheme-then-reqid", "Authorization: Bearer\nrequest_id=req-1"),
    ("over-auth-scheme-then-stage", "Authorization: Bearer\nstage=summarize"),
    ("over-auth-token-then-keys",   "authorization: token\nstage=x code=y"),
    ("over-auth-crlf-then-key",     "Authorization: Bearer\r\ndoc=17"),
    ("over-auth-obsfold-then-key",  "Authorization: Bearer\n  doc=17"),
    ("over-proxy-auth-then-key",    "X-Authorization: Bearer\ndoc=17"),
    ("over-auth-scheme-then-marker",f"Authorization: Bearer\n{M}"),
    ("over-auth-generic-then-key",  "Authorization: Negotiate\ndoc=17"),
]
print(f"{'id':>30} | {'base':>22} | {'r4':>22} | {'r5':>22} | r4==r5")
for pid, txt in OVER:
    o = {g: MODS[g].redact_text(txt) for g in ("base", "r4", "r5")}
    print(f"{pid:>30} | {o['base']!r:>22} | {o['r4']!r:>22} | {o['r5']!r:>22} | {o['r4']==o['r5']}")

print("\n-- over-redaction NEW on r5 relative to r4 (non-tchar non-delimiter pre-break token):")
for ch in "()/:<=>?@[\\]{}\" ,;&'|":
    txt = f"Authorization: Bo{ch}t\ndoc=17"
    o4 = MODS["r4"].redact_text(txt); o5 = MODS["r5"].redact_text(txt); ob = MODS["base"].redact_text(txt)
    if o4 != o5:
        print(f"   {ch!r:>6}: base={ob!r}  r4={o4!r}  r5={o5!r}")

print()
print("=" * 78)
print("CLAIM 4 — the four new rows, derived by hand from the spec")
print("=" * 78)
ROWS = [
    ("N5p", f"Authorization: Bo?t\n{M}",                    "Authorization: <redacted>"),
    ("N5q", f"Authorization: Bo/t\n{S39}\ndoc=17",          "Authorization: <redacted>\ndoc=17"),
    ("N5r", f"Authorization: Bo:t\n{M}",                    "Authorization: <redacted>"),
    ("N5s", f"Authorization: Bo=t\n{M}",                    "Authorization: <redacted>"),
]
# independent hand derivation of the expected LENGTHS, from the spec:
#   "Authorization: " = 15 ; "<redacted>" = 10 ; "\n" = 1 ; "doc=17" = 6
print("hand-derived lengths: 'Authorization: '+<redacted> = 15+10 = 25;  +'\\n'+'doc=17' = 25+1+6 = 32")
for rid, txt, exp in ROWS:
    out = MODS["r5"].redact_text(txt)
    print(f"   {rid}: tree={out!r} (len {len(out)})  hand-derived={exp!r} (len {len(exp)})  match={out==exp}")

print("\n-- and on the r4 tree (the new rows must be load-bearing):")
for rid, txt, exp in ROWS:
    out = MODS["r4"].redact_text(txt)
    print(f"   {rid}: r4={out!r}  r4==expected: {out==exp}")
