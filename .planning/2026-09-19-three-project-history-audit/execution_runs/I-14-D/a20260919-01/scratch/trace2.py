"""Scratch: find which expansion the SPLIT template resolves to, and trace matching."""
import re
import sys
from pathlib import Path

A = Path(__file__).resolve().parents[1]
B = chr(92)
tmpl = (A / "scratch" / "r3_block_template.txt").read_text(encoding="utf-8")
resolved = tmpl.replace("_AUTH_SCHEME_DELIMS", "_DELIM")
resolved = resolved.replace("@T@", B + "t").replace("@N@", B + "r?" + B + "n")

print("=== resolved source lines ===")
for ln in resolved.split("\n")[-3:]:
    print(repr(ln))
print()

sys.path.insert(0, str(A / "iso" / "product_narrow" / "src"))
from company_wiki.source_catalog import observability as ob  # noqa: E402

for label, delim in (("_AUTH_BARE_VALUE", ob._AUTH_BARE_VALUE),
                     ("simple class", r"[^\s,;&\"'|]")):
    ns = {"_DELIM": delim}
    exec(resolved, ns)
    SPLIT = ns["_AUTH_SCHEME_SPLIT"]
    print(f"--- delim = {label}")
    print("    SPLIT =", SPLIT)
    p = re.compile(SPLIT)
    M = "SYNTHETIC_AUDIT_TOKEN"
    for t in ["Bearer " + M + "\ndoc=17\nstage=summarize",
              "Bearer\n" + M + "\ndoc=17",
              "Bearer abc\nghp_ZQ7ReviewerFakeCredential0123456789"]:
        m = p.match(t)
        print("    ", repr(t[:34]), "->", repr(m.group(0)) if m else None)
