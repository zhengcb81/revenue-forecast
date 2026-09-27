"""Mutation builder — RF-RATCHET-FIX-2 (non-vacuity proofs, both directions).

MUT1 (confidence): merge TWO extracted helpers (`_evidence_quality`, `_limitations`)
back into `calculate_confidence` -> expect calculate_confidence CC=24 > frozen 23
(barely-over merge, matching the predecessor's mut1 shape), while the unused helper
defs stay in the file (their own CC stays <= 23 so FILE_MAX = 24 comes from
calculate_confidence only). Frozen test must flip back to
`analysis/confidence.py max 24 > 23`; restore flips it to the F2 row.

MUT2 (model_extensions): merge `_check_driver_bounds`'s gate back into
`_validate_driver_paths` (replacing the helper call with its inlined body)
-> expect _validate_driver_paths CC=11 > 10. New-file test must flip to
`model_extensions.py max 11 > 10`; restore flips back to full green.

Bodies are extracted from the refactored source itself (ast), so the mutation is a
true textual re-merge of the refactor's own hunks — no hand-retyped logic.
"""
from __future__ import annotations

import ast
import textwrap
from pathlib import Path

WORK = Path(__import__("os").environ["TEMP"]) / "rf2-iso-work"
OUT = Path(__file__).resolve().parent


def helper_body(text: str, name: str) -> str:
    """Body of a top-level def, minus its docstring and trailing return."""
    tree = ast.parse(text)
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
    lines = text.splitlines(keepends=True)
    body = node.body
    if isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
        body = body[1:]
    assert isinstance(body[-1], ast.Return), f"{name}: last stmt must be return"
    start = body[0].lineno
    end = body[-1].lineno - 1  # drop the return line
    return textwrap.indent("".join(lines[start - 1:end]), "")


# ---- MUT1: confidence.py -------------------------------------------------
conf_path = WORK / "scripts" / "analysis" / "confidence.py"
conf = conf_path.read_text(encoding="utf-8")

call1 = (
    "    source_quality, freshness = _evidence_quality(\n"
    "        validated, weights, parameters, claims, covered_weight\n"
    "    )\n"
)
call2 = (
    "    limitations = _limitations(\n"
    "        data,\n"
    "        validated,\n"
    "        result,\n"
    "        covered_weight,\n"
    "        historical_wape,\n"
    "        historical_observations,\n"
    "        usable_origins,\n"
    "        sensitivities,\n"
    "        explicit_model_share,\n"
    "    )\n"
)
assert conf.count(call1) == 1 and conf.count(call2) == 1
mut1 = conf.replace(call1, helper_body(conf, "_evidence_quality")).replace(
    call2, "    " + helper_body(conf, "_limitations").lstrip()
)
(OUT / "confidence_mut1.py").write_text(mut1, encoding="utf-8")

# ---- MUT2: model_extensions.py -------------------------------------------
me_path = WORK / "scripts" / "model_extensions.py"
me = me_path.read_text(encoding="utf-8")
call = "            _check_driver_bounds(model_id, name, value, lower, upper, error)\n"
inline = (
    "            if (lower is not None and value < lower) or (upper is not None and value > upper):\n"
    '                raise error(f"driver out of bounds: {model_id}/{name}")\n'
)
assert me.count(call) == 1
mut2 = me.replace(call, inline)
(OUT / "model_extensions_mut2.py").write_text(mut2, encoding="utf-8")

print("mutants written:", OUT / "confidence_mut1.py", OUT / "model_extensions_mut2.py")
