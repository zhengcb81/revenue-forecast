"""I11A-OPEN12-VALIDATOR-COMPLETENESS — the proposed patch (changes.diff source).

Design rule: the ORIGINAL predicates are left in place untouched; every OPEN12 guard is an
ADDITIONAL, marker-delimited block (# <OPEN12-Gn> ... # </OPEN12-Gn>) so that deleting the
block is an exact "weaken the validator" mutation (oracle §4, M1..M10).

Writes: <attempt>/tools/validate_hypotheses.py  (in the patched iso copy only; never the repo).
"""

from __future__ import annotations

import io
import os
import sys

REPLACEMENTS = []


def rep(old, new):
    REPLACEMENTS.append((old, new))


# ---------------------------------------------------------------- G1 threshold honesty
rep(
    """        if tb == "arithmetic_identity":
            # an arithmetic-identity threshold must be a decidable equality statement
            thr = str(fz.get("threshold", ""))
            if not re.search(r"0|差|等于|=|≤", thr):
                err("E_THRESHOLD_BASIS_INCONSISTENT",
                    "threshold_basis=arithmetic_identity but the threshold text is not an equality: %r" % thr)
""",
    """        if tb == "arithmetic_identity":
            # an arithmetic-identity threshold must be a decidable equality statement
            thr = str(fz.get("threshold", ""))
            if not re.search(r"0|差|等于|=|≤", thr):
                err("E_THRESHOLD_BASIS_INCONSISTENT",
                    "threshold_basis=arithmetic_identity but the threshold text is not an equality: %r" % thr)
            # <OPEN12-G1>
            # OPEN12: the frozen rule (oracle R2-1) says the threshold text must BE an
            # equality. The original predicate also matches the digit 0, so a bare
            # magnitude band such as "+/-10%" was accepted as an arithmetic identity.
            if (not re.search(r"=|≤|≥|等于|恒等式|0（", thr)) or (
                    re.search(r"±?\\s*\\d+(?:\\.\\d+)?\\s*%", thr)
                    and not re.search(r"=|≤|≥|等于", thr)):
                err("E_THRESHOLD_BASIS_INCONSISTENT",
                    "OPEN12-G1: arithmetic_identity threshold is not a decidable equality: %r" % thr)
            # </OPEN12-G1>
""",
)

# ---------------------------------------------------------------- G5 top-level page basis
rep(
    """        if src.get("page_index_basis") not in LOCATION_BASES:
            err("E_BAD_PAGE_BASIS", "page_index_basis=%r not in %s"
                % (src.get("page_index_basis"), sorted(LOCATION_BASES)))
""",
    """        if src.get("page_index_basis") not in LOCATION_BASES:
            err("E_BAD_PAGE_BASIS", "page_index_basis=%r not in %s"
                % (src.get("page_index_basis"), sorted(LOCATION_BASES)))
        # <OPEN12-G5>
        # OPEN12: the top-level page_index_basis declared by the template was only ever
        # checked for presence, so "printed_page_1based" at the top level passed while
        # the same value under source.* was rejected (oracle §7 E_BAD_PAGE_BASIS / O-4).
        if h.get("page_index_basis") not in LOCATION_BASES:
            err("E_BAD_PAGE_BASIS",
                "OPEN12-G5: top-level page_index_basis=%r not in %s"
                % (h.get("page_index_basis"), sorted(LOCATION_BASES)))
        # </OPEN12-G5>
""",
)

# ---------------------------------------------------------------- G4 falsifier blank
rep(
    """        fz = h.get("falsifier", {})
        for k in FALSIFIER_KEYS:
            if not fz.get(k):
                err("E_MISSING_FALSIFIER", "falsifier.%s empty" % k)
""",
    """        fz = h.get("falsifier", {})
        for k in FALSIFIER_KEYS:
            if not fz.get(k):
                err("E_MISSING_FALSIFIER", "falsifier.%s empty" % k)
        # <OPEN12-G4>
        # OPEN12: the original test is a bare truthiness check, so whitespace-only
        # values ("   ") satisfied all five falsifier elements (oracle §7
        # E_MISSING_FALSIFIER / §3.4). refuted_by already strips; falsifier did not.
        for k in FALSIFIER_KEYS:
            v = fz.get(k)
            if v is not None and str(v).strip() == "":
                err("E_MISSING_FALSIFIER",
                    "OPEN12-G4: falsifier.%s is blank/whitespace-only" % k)
        # </OPEN12-G4>
""",
)

# ---------------------------------------------------------------- G9 observable concrete
rep(
    """        od = str(fz.get("observation_date", "")).strip().lower()
""",
    """        # <OPEN12-G9>
        # OPEN12: oracle §3.4(1) requires observable to be a concrete measurable
        # quantity, explicitly NOT a phrase like "risk rises". Nothing checked it.
        # A blank observable is G4's business (E_MISSING_FALSIFIER); this guard only
        # judges a filled-in-but-vague observable, so M4/M9 stay independent.
        _obs_txt = str(fz.get("observable") or "")
        if _obs_txt.strip():
            _vague = ("风险上升", "风险加大", "不确定性上升", "景气", "情绪", "信心",
                      "趋势向好", "向好", "恶化", "不确定")
            _grounded = re.search(
                r"\\d|收入|生产量|销售量|库存量|产量|分部|披露|增速|抵销|席位|ARPU|合计|计划|单价|价格|占比",
                _obs_txt)
            if any(t in _obs_txt for t in _vague) or not _grounded:
                err("E_FALSIFIER_OBSERVABLE_VAGUE",
                    "OPEN12-G9: falsifier.observable is not a concrete measurable quantity: %r"
                    % _obs_txt)
        # </OPEN12-G9>
        od = str(fz.get("observation_date", "")).strip().lower()
""",
)

# ---------------------------------------------------------------- G7 observation date month
rep(
    """        od = str(fz.get("observation_date", "")).strip().lower()
        if od in OBSERVATION_DATE_BAD or not OBSERVATION_DATE_OK.search(od):
            err("E_OBSERVATION_DATE_UNRESOLVED",
                "observation_date carries no resolvable date anchor: %r" % fz.get("observation_date"))
""",
    """        od = str(fz.get("observation_date", "")).strip().lower()
        if od in OBSERVATION_DATE_BAD or not OBSERVATION_DATE_OK.search(od):
            err("E_OBSERVATION_DATE_UNRESOLVED",
                "observation_date carries no resolvable date anchor: %r" % fz.get("observation_date"))
        # <OPEN12-G7>
        # OPEN12: the shape-only regex accepts any MM, including "2026-13"; an anchor
        # that cannot be resolved to a month is not a resolvable observation date
        # (oracle R2-1 / review.md §5.1 "观察日可解析").
        for _y, _m in re.findall(r"(\\d{4})\\s*[-/年]\\s*(\\d{1,2})",
                                 str(fz.get("observation_date", ""))):
            if not (1 <= int(_m) <= 12):
                err("E_OBSERVATION_DATE_UNRESOLVED",
                    "OPEN12-G7: observation_date carries an unresolvable date anchor %s-%s"
                    % (_y, _m))
                break
        # </OPEN12-G7>
""",
)

# ---------------------------------------------------------------- G6 top-level anchor
rep(
    """        # anchor text must occur in the extraction output
        corpus = doc_texts.get(src.get("doc_id"), "")
        if src.get("anchor_text") and _norm(src["anchor_text"]) not in _norm(corpus):
            err("E_ANCHOR_NOT_FOUND", "anchor_text not found in extraction output")
""",
    """        # anchor text must occur in the extraction output
        corpus = doc_texts.get(src.get("doc_id"), "")
        if src.get("anchor_text") and _norm(src["anchor_text"]) not in _norm(corpus):
            err("E_ANCHOR_NOT_FOUND", "anchor_text not found in extraction output")
        # <OPEN12-G6>
        # OPEN12: only source.anchor_text was checked; the top-level anchor_text field
        # required by the template was never compared with the corpus (oracle §7
        # E_ANCHOR_NOT_FOUND / O-4).
        if h.get("anchor_text") and _norm(str(h.get("anchor_text"))) not in _norm(corpus):
            err("E_ANCHOR_NOT_FOUND",
                "OPEN12-G6: top-level anchor_text not found in extraction output")
        # </OPEN12-G6>
        # <OPEN12-G10>
        # OPEN12: evidence_path must point at an extraction output that was actually
        # archived in this attempt (oracle §2 O-3 / §3 mandatory field).
        _archived = set()
        for _d in source_map["documents"]:
            if _d.get("extraction_output_path"):
                _archived.add(_d["extraction_output_path"])
            if _d.get("narrative_text_path"):
                _archived.add(_d["narrative_text_path"])
        if h.get("evidence_path") not in _archived:
            err("E_EVIDENCE_PATH_NOT_ARCHIVED",
                "OPEN12-G10: evidence_path %r is not one of the archived extraction outputs"
                % h.get("evidence_path"))
        # </OPEN12-G10>
""",
)

# ---------------------------------------------------------------- G8 approved seal
rep(
    """            if not h.get("decision", {}).get("decision_sha256"):
                err("E_STATE_APPROVED_BY_IMPLEMENTER",
                    "approved_frozen requires decision.decision_sha256 to seal the review record")
""",
    """            if not h.get("decision", {}).get("decision_sha256"):
                err("E_STATE_APPROVED_BY_IMPLEMENTER",
                    "approved_frozen requires decision.decision_sha256 to seal the review record")
            # <OPEN12-G8>
            # OPEN12: "any non-empty string" is not a seal. §7 requires an independent
            # reviewer signature; a well-formed 64-hex sha256 is the minimum that makes
            # decision_sha256 falsifiable at all.
            _sha = str(h.get("decision", {}).get("decision_sha256") or "").strip().lower()
            if not re.fullmatch(r"[0-9a-f]{64}", _sha):
                err("E_STATE_APPROVED_BY_IMPLEMENTER",
                    "OPEN12-G8: decision.decision_sha256 is not a well-formed sha256 seal: %r"
                    % _sha)
            # </OPEN12-G8>
""",
)

# ---------------------------------------------------------------- G3 chain end semantics
rep(
    """            last = str(chain[-1])
            if len(last.strip()) < 8 or not any(m in last for m in CHAIN_END_MARKERS):
                err("E_CHAIN_END_SEMANTICS",
                    "mechanism_chain must end in revenue-recognition/period semantics, got %r" % last)
""",
    """            last = str(chain[-1])
            if len(last.strip()) < 8 or not any(m in last for m in CHAIN_END_MARKERS):
                err("E_CHAIN_END_SEMANTICS",
                    "mechanism_chain must end in revenue-recognition/period semantics, got %r" % last)
            # <OPEN12-G3>
            # OPEN12: CHAIN_END_MARKERS contains bare 确认/交付/control, so a link like
            # "项目档案信息确认流程闭环交付" satisfied the check while carrying no revenue
            # semantics at all (oracle §3.3 / R2-1 E_CHAIN_END_SEMANTICS).
            if not (re.search(r"收入|营收|营业", last)
                    and re.search(r"确认|归属|期间|时点", last)):
                err("E_CHAIN_END_SEMANTICS",
                    "OPEN12-G3: mechanism_chain last link lacks revenue-recognition/period "
                    "semantics: %r" % last)
            # </OPEN12-G3>
""",
)

# ---------------------------------------------------------------- G2 duplicates / O-11
# handled separately: the whole block is inserted immediately before the function's
# `return errors` (see PATCH_ANCHOR / G2_BLOCK below)

G2_BLOCK = '''    # <OPEN12-G2>
    # OPEN12-G2a: "one proposition corresponds to ONE parameter_id" (oracle §3.3). The
    # existing check only fires when claim/observation DIFFER, so appending the very
    # same proposition twice (the case the independent reviewer pre-registered as
    # "expected to be rejected", REPORT.md L233) was still accepted.
    _seen_prop = {}
    for h in hypotheses:
        _key = (json.dumps(h.get("claim"), ensure_ascii=False),
                json.dumps(h.get("observation"), sort_keys=True, ensure_ascii=False))
        if _key in _seen_prop:
            errors.append({"hypothesis_id": h.get("hypothesis_id"),
                           "code": "E_DUPLICATE_PARAMETER",
                           "detail": "OPEN12-G2a: duplicate proposition (identical claim and "
                                     "observation) first registered as %s" % _seen_prop[_key]})
        else:
            _seen_prop[_key] = h.get("hypothesis_id")
    # OPEN12-G2b: oracle O-11 forward direction — same model_id + driver_name +
    # effective_period MUST share one parameter_id. The old check indexed only by
    # parameter_id, so a second parameter_id for the same driver was never seen.
    _seen_drv = {}
    for h in hypotheses:
        _pmx = h.get("parameter_mapping", {})
        _k = (_pmx.get("model_id"), _pmx.get("driver_name"), _pmx.get("effective_period"))
        _pid = _pmx.get("parameter_id")
        if _k in _seen_drv and _seen_drv[_k] != _pid:
            errors.append({"hypothesis_id": h.get("hypothesis_id"),
                           "code": "E_DUPLICATE_PARAMETER",
                           "detail": "OPEN12-G2b: same model/driver/period registered with two "
                                     "different parameter_ids (%s vs %s) — oracle O-11"
                                     % (_seen_drv[_k], _pid)})
        else:
            _seen_drv[_k] = _pid
    # </OPEN12-G2>
    return errors
'''

PATCH_ANCHOR = "    return errors\n"


def build(src_text):
    text = src_text
    for old, new in REPLACEMENTS:
        if old == new:
            # marker for the G2 block: handled separately below
            continue
        n = text.count(old)
        if n != 1:
            raise SystemExit("anchor not unique (count=%d):\n%s" % (n, old[:160]))
        text = text.replace(old, new)
    if text.count(PATCH_ANCHOR) != 1:
        raise SystemExit("return-anchor count=%d" % text.count(PATCH_ANCHOR))
    text = text.replace(PATCH_ANCHOR, G2_BLOCK)
    return text


def main():
    src, dst = sys.argv[1], sys.argv[2]
    original = io.open(src, encoding="utf-8", newline="").read()
    patched = build(original)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with io.open(dst, "w", encoding="utf-8", newline="") as fh:
        fh.write(patched)
    print("patched %s -> %s (%d -> %d bytes)" % (src, dst, len(original.encode('utf-8')),
                                                 len(patched.encode('utf-8'))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
