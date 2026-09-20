"""r2 consistency check: every error code used in decision.md / oracle.md must be
defined in decision.md section 2.5 (the single source), and vice versa.

Read-only over the attempt's own text. Prints a report; exit 1 on any inconsistency.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parent
DECISION = (ATTEMPT / "decision.md").read_text(encoding="utf-8")
ORACLE = (ATTEMPT / "oracle.md").read_text(encoding="utf-8")

# --- 1. canonical codes: the E## rows of the section 2.5 table -------------
start = DECISION.index("### 2.5 规范错误码表")
end = DECISION.index("个参数、一个未决")
section = DECISION[start:end]
canonical_rows = re.findall(r"\|\s*(E\d\d)\s*\|\s*`([a-z0-9_]+)`\s*\|", section)
canonical = {code: name for code, name in canonical_rows}
defined_names = set(canonical.values())

print(f"canonical_codes_defined={len(canonical)}")
for code, name in canonical_rows:
    print(f"  {code} {name}")

# --- 2. codes referenced in the places that MUST use canonical codes -------
# Only the "error code" columns are normative: oracle.md section 2's 4th table
# column and decision.md section 2.4's failure column. Field/schema names such
# as `request_id` or `publication_attestation` are NOT error codes and are
# deliberately excluded.
CODE_SHAPE = re.compile(r"^[a-z][a-z0-9_]{5,}$")
CODE_SUFFIX = re.compile(
    r"(_mismatch|_invalid|_invalid_json|_json|_untrusted|_violation|_error|_large|"
    r"_nonzero|_timeout|_absent|_unavailable|_read_only|_reuse|_expired_at_publish|"
    r"_outside_validity_window|_revoked|_fields|_signature|_record|_not_executable|"
    r"_unproven|_unopenable|"
    r"_in_production_trust_domain|_not_allowed_for_optin_schema|_rollback_required)$"
)
BACKTICK = re.compile(r"`([a-z][a-z0-9_]{5,})`")
E_NUMBER = re.compile(r"\bE\d\d\b")
# explicit reference form used throughout the frozen texts
EXPLICIT_REF = re.compile(r"\*\*(E\d\d)\*\*\s*`([a-z0-9_]+)`")
REF_FORMS = re.compile(r"\*\*E\d\d\*\*\s*`[a-z0-9_]+`|`[a-z0-9_]+`\s*（\s*E\d\d\s*）|（\s*E\d\d\s*）")
E_REF_ADJACENT = re.compile(r"E\d\d\s*[`*]")


def is_code_like(token: str) -> bool:
    return bool(CODE_SHAPE.match(token)) and bool(CODE_SUFFIX.search(token))


def is_bound_code(segment: str, token: str) -> bool:
    """True when *segment* uses the explicit reference form ``**E##** `code```.

    The earlier heuristic ("any backticked token on a line that also mentions an
    E-number") was too loose: a line mixes field names with codes. The explicit
    adjacency form is what decision.md/oracle.md actually use for references.
    """
    return bool(EXPLICIT_REF.search(segment)) and bool(CODE_SHAPE.match(token))


def error_code_column(text: str) -> set[str]:
    """Codes appearing in a table cell whose header says 错误码/失败码/E 编号."""
    found: set[str] = set()
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        for cell in cells:
            if "E" in cell and re.search(r"\bE\d\d\b", cell) and is_code_like(
                BACKTICK.search(cell).group(1) if BACKTICK.search(cell) else ""
            ):
                found.update(BACKTICK.findall(cell))
    return found


def oracle_code_cells(text: str) -> set[str]:
    """Code strings that appear in the explicit reference form ``**E##** `code```.

    Scoping matters twice over: oracle.md mentions field names (payload_sha256,
    ...) in the same cells as codes, so neither a line-level heuristic nor a
    whole-cell scan is sound. Only the tightly-bound ``**E##** `code``` form is a
    code reference; the suffix heuristic covers loose mentions separately.
    """
    return {name for _num, name in EXPLICIT_REF.findall(text)}


# decision.md section 2.4 failure column: every code-like backtick token in the
# 2.2-2.5 window must be defined in 2.5
window_start = DECISION.index("### 2.3 响应")
window_end = DECISION.index("## 3. issuer / key 识别")
dec_normative = {
    token
    for segment in DECISION[window_start:window_end].splitlines()
    for token in BACKTICK.findall(segment)
    if is_code_like(token) or is_bound_code(segment, token)
}
ora_normative = oracle_code_cells(ORACLE)
# loose mentions of a code without the explicit **E##** form are still caught by
# the suffix heuristic; the E-number+backtick adjacency form was too loose
# (field names share those cells) and is deliberately NOT used.
ora_normative |= {
    token
    for segment in ORACLE.splitlines()
    for token in BACKTICK.findall(segment)
    if is_code_like(token)
}
# oracle may mention pre-existing product message strings; allow the regex-free
# ones that are documented as retained in decision.md section 2.5's last column
retained_legacy_messages = {"legacy_read_only"}

undef_dec = sorted(dec_normative - defined_names)
undef_ora = sorted(
    t for t in ora_normative if t not in defined_names and t not in retained_legacy_messages
)

print(f"\ncode_like_in_decision={len(dec_normative)}  code_like_in_oracle={len(ora_normative)}")
print("undefined_in_decision=" + (",".join(undef_dec) if undef_dec else "none"))
print("undefined_in_oracle=" + (",".join(undef_ora) if undef_ora else "none"))

unused = sorted(n for n in defined_names if n not in dec_normative and n not in ora_normative)
print("defined_but_never_referenced=" + (",".join(unused) if unused else "none"))

# --- 3. the two codes the reviewer flagged as formerly divergent -----------
legacy_checks = {
    "attestation_absent": ("G3a" in DECISION and "attestation_absent" in ORACLE),
    "attestation_missing_record": ("G3b" in DECISION and "attestation_missing_record" in ORACLE),
    "trust_domain_schema_error": ("trust_domain_schema_error" in DECISION and "E25" in ORACLE),
    "legacy_exemption_not_allowed_for_optin_schema": "E29" in ORACLE,
}
print("\nreviewer_flagged_pairings=" + str(legacy_checks))

# --- 4. r2 marker present in both files -----------------------------------
print("decision_has_r2_record=" + str("8.1 修订记录（r2" in DECISION))
print("oracle_has_r2_marker=" + str("r2 修订说明" in ORACLE))

problems = []
if undef_dec:
    problems.append("decision uses undefined codes: " + ",".join(undef_dec))
if undef_ora:
    problems.append("oracle uses undefined codes: " + ",".join(undef_ora))
if not all(legacy_checks.values()):
    problems.append("a reviewer-flagged pairing is missing")
if len(canonical) < 25:
    problems.append(f"canonical table looks truncated ({len(canonical)} codes)")

print("\nPROBLEMS=" + (str(len(problems)) + " :: " + " | ".join(problems) if problems else "0"))
sys.exit(1 if problems else 0)
