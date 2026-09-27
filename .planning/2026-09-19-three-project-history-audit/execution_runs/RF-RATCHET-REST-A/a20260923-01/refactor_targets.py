"""RF-RATCHET-REST-A: mechanical extract-function surgery on research/targets.py.

Operates ONLY on the iso copy. Verbatim line-range extraction with anchor
assertions (abort if the source does not look exactly as expected), so the
moved code is byte-identical modulo a uniform 4-space dedent for loop bodies
that moved from nested-loop level into function level.

Surgery:
  H1  _normalize_communication_coverage   <- lines 40..170 (coverage loop; stays at same depth, NO dedent)
  H2  _validate_management_target         <- lines 183..498 (targets loop body; DEDENT 4)
  main keeps orchestration: coverage get -> H1 -> targets/roles/segment_names ->
        for-loop calling H2 -> post-loop require + result assembly (lines 499..end).
"""
from __future__ import annotations

import sys
from pathlib import Path

path = Path(sys.argv[1])
lines = path.read_text(encoding="utf-8").split("\n")  # keep exact text lines


def L(n: int) -> str:
    """1-indexed line."""
    return lines[n - 1]


# ---- anchor assertions -----------------------------------------------------
assert L(31).startswith("def validate_management_target_coverage("), L(31)
assert L(38).strip().startswith('"""Validate official communication coverage'), L(38)
assert 'coverage = data.get("management_communication_coverage")' in L(39), L(39)
assert "isinstance(coverage, list)" in L(41), L(41)
assert L(47).strip() == "normalized_coverage: dict[str, dict[str, Any]] = {}", L(47)
assert L(48).strip() == "referenced_target_ids: set[str] = set()", L(48)
assert L(49).strip().startswith("for position, record in enumerate(coverage):"), L(49)
assert L(170).strip() == "normalized_coverage[category] = normalized", L(170)
assert L(171).strip() == "", repr(L(171))
assert 'targets = data.get("management_targets")' in L(172), L(172)
assert L(182).strip().startswith("for position, target in enumerate(targets):"), L(182)
assert L(183).strip().startswith('prefix = f"management_targets[{position}]"'), L(183)
assert "gap_messages.append(" in L(471), L(471)
assert "gap_messages.append(" in L(479), L(479)
assert L(498).strip() == "normalized_targets[target_id] = normalized", L(498)
assert L(499).strip() == "", repr(L(499))
assert "referenced_target_ids == set(normalized_targets)" in L(501), L(501)


def dedent4(block: list[str]) -> list[str]:
    out = []
    for ln in block:
        if ln.strip() == "":
            out.append(ln)
        else:
            assert ln.startswith("    "), f"cannot dedent: {ln!r}"
            out.append(ln[4:])
    return out


# ---- H1: coverage normalizer (same nesting depth -> verbatim) --------------
h1_body = lines[39:170]  # lines 40..170 inclusive
h1 = (
    ["def _normalize_communication_coverage(",
     "    coverage: Any,",
     "    source_index: dict[str, dict[str, Any]],",
     "    as_of: date,",
     ") -> tuple[dict[str, dict[str, Any]], set[str]]:",
     '    """Validate and normalize management communication coverage records.',
     "",
     "    Extracted verbatim from validate_management_target_coverage (the",
     "    coverage loop); runs at the same point in the same order, so every",
     "    require() still fires in the original sequence.",
     '    """']
    + h1_body
    + ["", "    return normalized_coverage, referenced_target_ids", "", ""]
)

# ---- H2: per-target validator (dedent 4) -----------------------------------
h2_body = dedent4(lines[182:498])  # lines 183..498 inclusive
# gap_messages (orchestrator accumulator) -> gaps (local, returned)
n_before = sum("gap_messages" in ln for ln in h2_body)
h2_body = [ln.replace("gap_messages", "gaps") for ln in h2_body]
n_after = sum("gap_messages" in ln for ln in h2_body)
assert n_after == 0, "stray gap_messages left in helper body"
# drop the orchestrator's bookkeeping line, return instead
assert h2_body[-1].strip() == "normalized_targets[target_id] = normalized", h2_body[-1]
h2_body = h2_body[:-1]
h2 = (
    ["def _validate_management_target(",
     "    target: dict[str, Any],",
     "    position: int,",
     "    data: dict[str, Any],",
     "    parameter_index: dict[str, dict[str, Any]],",
     "    claim_index: dict[str, dict[str, Any]],",
     "    roles: dict[str, set[str]],",
     "    segment_names: set[Any],",
     "    normalized_targets: dict[str, dict[str, Any]],",
     ") -> tuple[dict[str, Any], list[str]]:",
     '    """Validate one management target; return (normalized record, gap messages).',
     "",
     "    Extracted verbatim from the management_targets loop body of",
     "    validate_management_target_coverage. normalized_targets is read-only",
     "    here (duplicate check against previously accepted targets); the",
     "    orchestrator stores the returned record after this call.",
     '    """',
     "    gaps: list[str] = []"]
    + h2_body
    + ["", "    return normalized, gaps", "", ""]
)

# ---- reassemble -------------------------------------------------------------
head = lines[0:30]          # lines 1..30 (imports, blanks)
main_start = lines[30:39]   # lines 31..39 (def + docstring + coverage get)
mid = lines[170:181]        # lines 171..181 (blank, targets get, require, roles,
                            #   segment_names, normalized_targets, gap_messages)
tail = lines[498:]          # lines 499..end (blank, final require, assembly)

loop = [
    "    for position, target in enumerate(targets):",
    "        normalized, target_gaps = _validate_management_target(",
    "            target,",
    "            position,",
    "            data,",
    "            parameter_index,",
    "            claim_index,",
    "            roles,",
    "            segment_names,",
    "            normalized_targets,",
    "        )",
    "        gap_messages.extend(target_gaps)",
    "        normalized_targets[normalized[\"target_id\"]] = normalized",
]

coverage_call = [
    "    normalized_coverage, referenced_target_ids = _normalize_communication_coverage(",
    "        coverage, source_index, as_of",
    "    )",
]

result = (
    head
    + h1
    + h2
    + main_start
    + coverage_call
    + mid
    + loop
    + tail
)

path.write_text("\n".join(result), encoding="utf-8")
print(f"rewrote {path}: {len(lines)} -> {len(result)} lines; "
      f"gap_messages->gaps replacements in H2: {n_before}")
