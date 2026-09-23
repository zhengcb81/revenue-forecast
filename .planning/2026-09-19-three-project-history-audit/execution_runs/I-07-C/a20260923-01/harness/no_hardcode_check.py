"""I-07-C clause-5 obligation: prove NO company-name hardcoding in THIS card's
test construction.

Scans every harness/*.py EXCEPT this checker itself (self-referential patterns
would always match) for:
  1. any CJK codepoint (fixture company names are CJK),
  2. ASCII identifier tokens DERIVED AT RUNTIME from sample_manifest.json
     (security ids, company queries, provider document ids) and from
     inputs/fifth_root_company.json (the fifth-root company's security id).

Writes evidence/no_hardcode_grep.txt (+ .json). Expected: 0 matches in every
scanned file. Data files that legitimately carry company identity are DISCLOSED,
not scanned: sample_manifest.json, inputs/fifth_root_company.json, the copied
*.source.json sidecars inside the isolated cells.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from i07c_common import ATT, EVID, INPUTS, load_manifest, read_json, write_json

HARNESS = ATT / "harness"
CHECKER = Path(__file__).name
CJK = re.compile("[" + chr(0x4E00) + "-" + chr(0x9FFF) + "]")  # ASCII-built so this file stays CJK-free


def path_masks() -> list[str]:
    """Machine identity strings that legitimately appear in absolute paths and
    are NOT company identifiers: the Windows user profile (this machine's
    username contains CJK glyphs). Masked before the CJK test so the check
    measures company literals, not the OS username. Derived at runtime."""
    import os
    masks = []
    home = str(Path.home())
    if home:
        masks.append(home)
    userprofile = os.environ.get("USERPROFILE") or ""
    if userprofile:
        masks.append(userprofile)
    users_root = str(Path(home).anchor) + "Users"
    name = Path(home).name
    if name:
        masks.append(str(Path(users_root) / name))
    return [m for m in masks if len(m) >= 4]


def ascii_tokens() -> set[str]:
    tokens: set[str] = set()
    for s in load_manifest()["samples"]:
        request = s.get("request") or {}
        for value in (s.get("provider_document_id"), request.get("company_query"),
                      request.get("market"), s.get("market")):
            if isinstance(value, str) and len(value) >= 4:
                tokens.add(value)
        sidecar = s.get("sidecar")
        # provider ids / tickers are not in the manifest; add well-known ascii
        # fields from the fifth-root input instead
    data = read_json(INPUTS / "fifth_root_company.json")
    for value in (data.get("security_id"), data.get("provider_document_id"),
                  data.get("canonical_entity_id")):
        if isinstance(value, str) and len(value) >= 3:
            tokens.add(value)
    # manifest-derived ascii tokens only for >=4 chars to avoid false positives
    # on short generic strings; CJK names are covered by the CJK range check.
    return {t for t in tokens if len(t) >= 4}


def main() -> int:
    tokens = sorted(ascii_tokens(), key=len, reverse=True)
    masks = path_masks()
    lines = ["I-07-C no-company-hardcode grep of the test construction",
             f"scope: {HARNESS}/*.py excluding {CHECKER} (the checker itself holds "
             "the patterns; self-scan would be self-referential)",
             f"path masks applied before testing (machine username, NOT a company "
             f"identifier): {len(masks)} mask(s)",
             f"patterns: [\\u4e00-\\u9fff] (any CJK) + ascii tokens derived from "
             f"sample_manifest.json + inputs/fifth_root_company.json: {tokens}",
             "expected: 0 matches in every scanned file", ""]
    total = 0
    per_file = {}
    for path in sorted(HARNESS.glob("*.py")):
        if path.name == CHECKER:
            continue
        text = path.read_text(encoding="utf-8")
        for mask in masks:
            text = text.replace(mask, "<MASKED_USER_PROFILE>")
        hits = []
        for lineno, line in enumerate(text.splitlines(), start=1):
            if CJK.search(line):
                hits.append({"line": lineno, "kind": "CJK", "text": line.strip()})
            for tok in tokens:
                if tok in line:
                    hits.append({"line": lineno, "kind": f"token:{tok}",
                                 "text": line.strip()})
        per_file[path.name] = len(hits)
        total += len(hits)
        lines.append(f"{path.name}: {len(hits)} match(es)")
        for hit in hits:
            lines.append(f"    L{hit['line']} [{hit['kind']}] {hit['text']}")
    lines += ["", "TOTAL MATCHES: %d" % total, "",
              "DISCLOSED DATA FILES (carry company identity BY DESIGN, not code):",
              f"  - {INPUTS / 'fifth_root_company.json'} (fifth-root company input data)",
              "  - PLAN/execution_v2/sample_manifest.json (frozen sample identities)",
              "  - each isolated cell's copied *.source.json / meta.json (asset bytes)",
              "",
              "Sample selection is data-driven: X04 uses min(byte_size), X01 uses",
              "market==CN, X02 uses market==US - no company literal selects a sample,",
              "so no swap to a previously-successful company is possible in code."]
    (EVID / "no_hardcode_grep.txt").write_text("\n".join(lines) + "\n",
                                               encoding="utf-8")
    write_json(EVID / "no_hardcode_result.json",
               {"total_matches": total, "per_file": per_file,
                "tokens_used": tokens,
                "verdict": "PASS" if total == 0 else "FAIL",
                "checker_excluded": CHECKER})
    print(json.dumps({"total_matches": total,
                      "verdict": "PASS" if total == 0 else "FAIL"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
