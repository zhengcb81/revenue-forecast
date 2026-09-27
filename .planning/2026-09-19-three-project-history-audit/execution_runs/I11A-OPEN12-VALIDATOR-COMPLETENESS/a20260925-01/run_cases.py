"""I11A-OPEN12-VALIDATOR-COMPLETENESS — frozen case runner (oracle §3/§3.1/§4).

Runs, against ONE validator module:
  * the positive case (8 hypotheses)
  * the validator's own frozen 21-case counterexample suite
  * REPRO-1..8  (the independent reviewer's own 8 mutations, REPORT.md §2 P2-5 table)
  * CE-01..11   (this card's pre-registered counterexamples, oracle §3)

Usage:
  python -X utf8 -B run_cases.py <validator.py> <attempt_root> <out.json> <phase> [target ...]

phases:
  red      -> expects: positive pass, 21/21, ALL CE accepted, REPRO-8 accepted (others rejected)
  green    -> expects: positive pass, 21/21, ALL CE rejected with their expected code,
                        ALL REPRO rejected
  mut      -> expects: positive pass, 21/21, the named target CE(s) ACCEPTED,
                        every other CE rejected with its expected code
rc = 0 iff the phase expectation holds (hand-written in oracle.md §2/§4).
"""

from __future__ import annotations

import copy
import importlib.util
import io
import json
import os
import sys

BASE_ID = "H-CN-ZIJIN-SEG-01"


def load_module(path):
    spec = importlib.util.spec_from_file_location("validator_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_inputs(attempt):
    ev = os.path.join(attempt, "evidence", "I-11-A")
    hypotheses = json.load(io.open(os.path.join(ev, "hypotheses.json"), encoding="utf-8"))
    source_map = json.load(io.open(os.path.join(ev, "source_map.json"), encoding="utf-8"))
    doc_texts = {}
    for d in source_map["documents"]:
        p = os.path.join(attempt, d["extraction_output_path"])
        doc_texts[d["doc_id"]] = io.open(p, encoding="utf-8").read()
        npath = d.get("narrative_text_path")
        if npath:
            doc_texts[d["doc_id"] + "::narrative"] = io.open(
                os.path.join(attempt, npath), encoding="utf-8").read()
    return hypotheses, source_map, doc_texts


def base_of(hypotheses):
    return next(h for h in hypotheses if h["hypothesis_id"] == BASE_ID)


# ---------------------------------------------------------------- REPRO (8)
def repro_cases(base):
    """The independent reviewer's 8 pre-registered mutations, REPORT.md L224-233."""
    cases = []

    def one(tag, note, mutate):
        h = copy.deepcopy(base)
        mutate(h)
        cases.append({"id": tag, "note": note, "hypotheses": [h]})

    one("REPRO-1", "page_index_basis trailing space (REPORT R1)",
        lambda h: h["source"].update({"page_index_basis": "pdf_leaf_1based "}))
    one("REPRO-2", "doc_id swapped to Xiaomi, Zijin sha kept (REPORT R5)",
        lambda h: h["source"].update({"doc_id": "HK-XIAOMI-AR2025"}))
    one("REPRO-3", "approved_frozen + invented reviewer name, no decision (REPORT R3)",
        lambda h: h.update({"state": "approved_frozen",
                            "reviewer": "Independent Reviewer (external)"}))
    one("REPRO-4", "threshold_basis pretends arithmetic_identity for +/-7% (REPORT R4)",
        lambda h: h["falsifier"].update({"threshold_basis": "arithmetic_identity",
                                         "threshold": "±7% 无恒等式"}))
    one("REPRO-5", "refuted_by blank entries (REPORT R6)",
        lambda h: h.update({"refuted_by": ["", "   "]}))
    one("REPRO-6", "mechanism_chain placeholder letters (REPORT 追加)",
        lambda h: h.update({"mechanism_chain": ["a", "b", "c"]}))
    one("REPRO-7", "observation_date = TBD (REPORT 追加)",
        lambda h: h["falsifier"].update({"observation_date": "TBD"}))
    # REPORT L233: "两条同 parameter_id 的相同命题"
    a = copy.deepcopy(base)
    b = copy.deepcopy(base)
    b["hypothesis_id"] = BASE_ID + "-DUP-COPY"
    cases.append({"id": "REPRO-8", "note": "two propositions sharing parameter_id, identical otherwise (REPORT L233)",
                  "hypotheses": [a, b]})
    return cases


# ---------------------------------------------------------------- CE (11)
CE_SPEC = [
    ("CE-01", "E_THRESHOLD_BASIS_INCONSISTENT", "arithmetic_identity threshold is a bare +/-10% band"),
    ("CE-02", "E_DUPLICATE_PARAMETER", "identical proposition appended (same parameter_id)"),
    ("CE-03", "E_DUPLICATE_PARAMETER", "same model+driver+period but a different parameter_id (O-11)"),
    ("CE-04", "E_CHAIN_END_SEMANTICS", "chain last link has 确认 but no revenue semantics"),
    ("CE-05", "E_MISSING_FALSIFIER", "observable / source_route whitespace-only"),
    ("CE-06", "E_BAD_PAGE_BASIS", "TOP-LEVEL page_index_basis = printed_page_1based"),
    ("CE-07", "E_ANCHOR_NOT_FOUND", "TOP-LEVEL anchor_text absent from the filing"),
    ("CE-08", "E_OBSERVATION_DATE_UNRESOLVED", "observation_date = 2026-13 (no such month)"),
    ("CE-09", "E_STATE_APPROVED_BY_IMPLEMENTER", "approved_frozen + 30-char invented reviewer + sha 'x'"),
    ("CE-10", "E_FALSIFIER_OBSERVABLE_VAGUE", "observable = 'market risk rising'"),
    ("CE-11", "E_EVIDENCE_PATH_NOT_ARCHIVED", "evidence_path points at a file that was never archived"),
]


def ce_cases(base):
    out = []

    def single(tag, mutate):
        h = copy.deepcopy(base)
        mutate(h)
        out.append({"id": tag, "hypotheses": [h]})

    single("CE-01", lambda h: h["falsifier"].update(
        {"threshold": "相对偏离不超过 ±10%（纯幅度阈值）"}))

    a = copy.deepcopy(base)
    b = copy.deepcopy(base)
    b["hypothesis_id"] = BASE_ID + "-IDENTICAL-COPY"
    out.append({"id": "CE-02", "hypotheses": [a, b]})

    a = copy.deepcopy(base)
    b = copy.deepcopy(base)
    b["hypothesis_id"] = BASE_ID + "-SAMEDRIVER-OTHERPID"
    b["parameter_mapping"]["parameter_id"] = base["parameter_mapping"]["parameter_id"] + "_V2"
    # erratum-1: clear additional_parameters, otherwise the three inherited additional
    # parameter_ids collide with proposition A and the unrelated E_DUPLICATE_PARAMETER
    # path (claim mismatch) masks the O-11 forward direction being tested here
    b["additional_parameters"] = []
    b["claim"] = base["claim"] + "（同 driver 的第二条命题）"
    out.append({"id": "CE-03", "hypotheses": [a, b]})

    single("CE-04", lambda h: h.update({"mechanism_chain": [
        "上游产能与价格因素作用于销量",
        "销量变化通过价格传导影响分部收入",
        "项目档案信息确认流程闭环交付",
    ]}))
    single("CE-05", lambda h: h["falsifier"].update(
        {"observable": "   ", "source_route": "   "}))
    single("CE-06", lambda h: h.update({"page_index_basis": "printed_page_1based"}))
    single("CE-07", lambda h: h.update({"anchor_text": "这段文字不在原文中"}))
    single("CE-08", lambda h: h["falsifier"].update({"observation_date": "2026-13"}))
    single("CE-09", lambda h: h.update({
        "state": "approved_frozen",
        "reviewer": "Independent Reviewer (external)",
        "decision": {"professional_reviewer": "Independent Reviewer (external)",
                     "decision": "approved",
                     "reason": "sealed-looking record",
                     "decision_sha256": "x"},
    }))
    single("CE-10", lambda h: h["falsifier"].update(
        {"observable": "市场风险上升（若风险加大则命题失效）"}))
    single("CE-11", lambda h: h.update(
        {"evidence_path": "evidence/I-11-A/extract/NOT_ARCHIVED.json"}))
    return out


def suite_results(mod, hypotheses, source_map, doc_texts, attempt):
    """Re-run the validator's own frozen suite through the same code path as main().

    Mirrors main()'s special case: the E_LISTED_VALUE_NOT_IN_EVIDENCE case is fed a
    deep copy of source_map with the fabricated CE-DOC entry appended.
    """
    import copy as _copy
    results = []
    for code, note, patched in mod.make_counterexamples(hypotheses):
        if code == "E_LISTED_VALUE_NOT_IN_EVIDENCE":
            sm = _copy.deepcopy(source_map)
            sm["documents"].append({
                "doc_id": "CE-DOC", "doc_sha256": "f" * 64,
                "extraction_output_path": "evidence/I-11-A/hypotheses.json",
                "cited_values": [{"key": "ce", "raw": "999,999,999", "page": 1,
                                  "raw_label": "counterexample value"}],
                "narrative_facts": [],
            })
        else:
            sm = source_map
        errs = mod.validate(patched, sm, attempt, doc_texts)
        got = sorted({e["code"] for e in errs})
        results.append({"expected_code": code, "note": note,
                        "observed_codes": got, "rejected": code in got})
    return results


def main():
    vpath, attempt, out_json, phase = sys.argv[1:5]
    targets = set(sys.argv[5:])
    mod = load_module(vpath)
    hypotheses, source_map, doc_texts = load_inputs(attempt)
    base = base_of(hypotheses)

    positive = mod.validate(hypotheses, source_map, attempt, doc_texts)
    suite = suite_results(mod, hypotheses, source_map, doc_texts, attempt)

    def run(cases, expected_map=None):
        rows = []
        for c in cases:
            errs = mod.validate(c["hypotheses"], source_map, attempt, doc_texts)
            codes = sorted({e["code"] for e in errs})
            exp = (expected_map or {}).get(c["id"])
            rows.append({"id": c["id"], "rejected": len(errs) > 0,
                         "expected_code": exp,
                         "expected_code_seen": (exp in codes) if exp else None,
                         "observed_codes": codes,
                         "errors": errs[:6]})
        return rows

    repro_expected = {
        "REPRO-1": "E_BAD_PAGE_BASIS",
        "REPRO-2": "E_SOURCE_HASH_MISMATCH",
        "REPRO-3": "E_STATE_APPROVED_BY_IMPLEMENTER",
        "REPRO-4": "E_THRESHOLD_BASIS_INCONSISTENT",
        "REPRO-5": "E_EMPTY_FIELD",
        "REPRO-6": "E_CHAIN_END_SEMANTICS",
        "REPRO-7": "E_OBSERVATION_DATE_UNRESOLVED",
        "REPRO-8": None,
    }
    repro = run(repro_cases(base), repro_expected)
    ce = run(ce_cases(base), {c[0]: c[1] for c in CE_SPEC})

    ok_positive = (positive == [])
    ok_suite = (len(suite) == 21 and all(r["rejected"] for r in suite))

    if phase == "red":
        ok_cases = all(not r["rejected"] for r in ce)
        r8 = next(r for r in repro if r["id"] == "REPRO-8")
        ok_repro = all(r["rejected"] for r in repro if r["id"] != "REPRO-8") and \
            (not r8["rejected"])
        detail = "all 11 CE accepted (leak) + REPRO-1..7 rejected + REPRO-8 accepted"
    elif phase == "green":
        ok_cases = all(r["rejected"] and r["expected_code_seen"] for r in ce)
        ok_repro = all(r["rejected"] for r in repro)
        detail = "all 11 CE rejected with expected code + all 8 REPRO rejected"
    elif phase == "mut":
        # explicit, readable form: every named target (CE *or* REPRO id) must flip to
        # ACCEPTED, every other case must stay rejected with its expected code
        ok_cases = all(
            (not r["rejected"]) if r["id"] in targets
            else (r["rejected"] and r["expected_code_seen"])
            for r in ce)
        ok_repro = all(
            (not r["rejected"]) if r["id"] in targets else r["rejected"]
            for r in repro)
        detail = "targets %s flipped to ACCEPTED, the rest stay rejected" % sorted(targets)
    else:
        raise SystemExit("unknown phase %r" % phase)

    ok = ok_positive and ok_suite and ok_cases and ok_repro
    report = {
        "validator": os.path.abspath(vpath),
        "attempt_root": os.path.abspath(attempt),
        "phase": phase,
        "targets": sorted(targets),
        "phase_expectation": detail,
        "phase_expectation_met": ok,
        "positive": {"errors": positive, "verdict": "pass" if ok_positive else "fail"},
        "own_suite": {"cases": len(suite),
                      "rejected_as_expected": sum(1 for r in suite if r["rejected"]),
                      "accepted_by_mistake": sum(1 for r in suite if not r["rejected"]),
                      "ok": ok_suite},
        "repro": repro,
        "ce": ce,
        "checks": {"positive": ok_positive, "own_suite": ok_suite,
                   "ce": ok_cases, "repro": ok_repro},
    }
    with io.open(out_json, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print("phase=%s expectation_met=%s positive=%s suite=%d/%d ce_accepted=%d repro_rejected=%d/%d"
          % (phase, ok, report["positive"]["verdict"],
             report["own_suite"]["rejected_as_expected"], report["own_suite"]["cases"],
             sum(1 for r in ce if not r["rejected"]),
             sum(1 for r in repro if r["rejected"]), len(repro)))
    for r in ce:
        print("   %-7s rejected=%-5s expected_code_seen=%-5s codes=%s"
              % (r["id"], r["rejected"], r["expected_code_seen"], ",".join(r["observed_codes"])))
    for r in repro:
        print("   %-8s rejected=%-5s codes=%s" % (r["id"], r["rejected"], ",".join(r["observed_codes"])))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
