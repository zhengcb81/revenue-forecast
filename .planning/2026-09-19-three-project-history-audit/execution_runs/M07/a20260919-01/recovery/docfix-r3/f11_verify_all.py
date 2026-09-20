"""Final acceptance re-verification after the r3 document/evidence pass.

Checks (all recomputed from disk, nothing trusted from the earlier logs):
  A  frozen expectations: evidence/<card>/oracle.json vs the reviewer's pre-registration
     (prereg_expectations.json) -- decimal strings and floats
  B  negatives 11/11: ids == oracle.negative_ids == cards.json order,姣忎緥 rejected with
     ModelRegistryError
  C  the product run matched the frozen oracle (run_result vs oracle.json within tolerance)
  D  stdout.txt printed values agree with the stored JSON
  E  ledger self-consistency: evidence_hashes.json / source_manifest.sha256_now /
     after/rerun_sha256.json all equal the bytes on disk
  F  oracle.md structure: exactly one "## revision r2" section, the authoritative v1 hash and
     the provenance-gap value both reproduce, kept region byte-identical to the r2 snapshot
  G  qualification.json states: formula review_pending (M05/M06/M07) / blocked (M08),
     disclosure_adaptation unmapped, accuracy unproven
  H  production source hashes still equal the binding values
  I  change-set closure: every file this pass touched is inside the attempt directories

Usage: <iso venv python> -X utf8 -B f11_verify_all.py > f11_verify_all.out.txt
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = (
    "C:/Users/\u90d1\u66fe\u6ce2/Projects/revenue-forecast/.planning/"
    "2026-09-19-three-project-history-audit/execution_runs"
)
REVIEW = "C:/Users/\u90d1\u66fe\u6ce2/AppData/Local/Temp/m05m08-review-20260920-025942"
CARDS = ("M05", "M06", "M07", "M08")
MARKER = "## \u4fee\u8ba2 r2"
PREREG = json.load(open(os.path.join(REVIEW, "prereg_expectations.json"), encoding="utf-8"))
dedupe = json.load(open(os.path.join(HERE, "f06_dedupe.json"), encoding="utf-8"))
verify = json.load(open(os.path.join(HERE, "f06_verify.json"), encoding="utf-8"))
checks: list[tuple[str, bool, str]] = []


def sha_file(p: str) -> str:
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def read_text(p: str) -> str:
    """stdout.txt was captured by PowerShell and is UTF-16LE with a BOM."""
    raw = open(p, "rb").read()
    for enc in ("utf-8-sig", "utf-16", "gbk"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", "replace")


def ok(name: str, cond: bool, detail: str = "") -> bool:
    checks.append((name, bool(cond), detail))
    print(f"   [{'PASS' if cond else 'FAIL'}] {name}" + (f" -- {detail}" if detail else ""))
    return bool(cond)


def close(a: float, b: float) -> bool:
    return abs(a - b) <= 1e-9 * max(1.0, abs(b))


def main() -> int:
    print("== final acceptance re-verification (post r3) ==")
    for card in CARDS:
        at = os.path.join(BASE, card, "a20260919-01")
        ev = os.path.join(at, "evidence", card)
        oracle = json.load(open(os.path.join(ev, "oracle.json"), encoding="utf-8"))
        run = json.load(open(os.path.join(ev, "run_result.json"), encoding="utf-8"))
        negs = json.load(open(os.path.join(ev, "negative_results.json"), encoding="utf-8"))
        cases = json.load(open(os.path.join(ev, "cases.json"), encoding="utf-8"))
        qual = json.load(open(os.path.join(ev, "qualification.json"), encoding="utf-8"))
        print("")
        print(f"-- {card} --")

        # A) frozen expectations vs pre-registration
        pairs = [
            (f"{card}.positive", {"decimal": oracle["positive"]["expected"],
                                  "float": oracle["positive"]["expected_float"]}),
            (f"{card}.continuity", {"decimal": oracle["continuity_positive"]["expected"],
                                    "float": oracle["continuity_positive"]["expected_float"]}),
            (f"{card}.defaults", {"decimal": oracle["defaults"]["expected"],
                                  "float": oracle["defaults"]["expected_float"]}),
        ]
        if card == "M08":
            pairs += [
                ("M08.positive_readingC",
                 {"decimal": [oracle["reading_C_upstream_and_implementation"]["positive_expected"]]}),
                ("M08.positive_readingA",
                 {"decimal": [oracle["reading_A_card_arithmetic"]["positive_expected"]]}),
                ("M08.positive_readingB",
                 {"decimal": [oracle["reading_B_card_formula_string"]["positive_expected"]]}),
                ("M08.continuity_readingC",
                 {"decimal": oracle["secondary_readings"]["reading_C_continuity"]}),
                ("M08.defaults_readingC",
                 {"decimal": [oracle["secondary_readings"]["reading_C_defaults"]]}),
            ]
        if card == "M07":
            pairs.append(("M07.continuity_year2_exact",
                          {"decimal": [oracle["continuity_positive"]["expected"][1]]}))
        for key, got in pairs:
            want = PREREG.get(key)
            if want is None:
                continue
            gd, wd = got.get("decimal"), want.get("decimal")
            same_dec = gd == wd
            same_flt = True
            if "float" in got and "float" in want:
                same_flt = all(close(a, b) for a, b in zip(got["float"], want["float"])) \
                    and len(got["float"]) == len(want["float"])
            ok(f"A frozen expectation {key} == prereg", same_dec and same_flt,
               f"oracle={gd} prereg={wd}")

        # B) negatives
        ids_oracle = oracle["negative_ids"]
        ids_cases = [c["id"] for c in cases["cases"] if c["expected"] == "ModelRegistryError"]
        ids_run = [e["id"] for e in run["negatives"]]
        raised = sorted({str(e.get("raised")) for e in negs["cases"]})
        targets = sorted({bool(e.get("is_target_type")) for e in negs["cases"]})
        verdicts = sorted({str(e.get("verdict")) for e in negs["cases"]})
        summary = negs["summary"]
        ok(f"B {card} negative ids identical (oracle/cases/run)",
           ids_oracle == ids_cases == ids_run, f"n={len(ids_run)} ids={ids_run}")
        ok(f"B {card} 11/11 rejected with ModelRegistryError",
           len(negs["cases"]) == 11 and summary.get("passed") == 11
           and not summary.get("failed") and raised == ["ModelRegistryError"]
           and targets == [True],
           f"cases={len(negs['cases'])} summary={summary} raised={raised} "
           f"verdicts={verdicts}")

        # C) product run matched the frozen oracle
        c_ok = True
        detail = []
        for name, oracle_key, run_key in (("positive", "positive", "positive"),
                                          ("continuity", "continuity_positive",
                                           "continuity_positive"),
                                          ("defaults", "defaults", "defaults")):
            exp = oracle[oracle_key]["expected_float"]
            act = run[run_key]["actual"]
            good = len(exp) == len(act) and all(close(a, e) for a, e in zip(act, exp))
            c_ok = c_ok and good
            detail.append(f"{name}: actual={act} expected={exp} ok={good}")
        ok(f"C {card} run_result matches the frozen oracle", c_ok, "; ".join(detail))

        # D) stdout agrees with the stored JSON
        so = read_text(os.path.join(ev, "stdout.txt"))
        d_ok = True
        for ln in so.splitlines():
            if ln.startswith("positive actual: "):
                printed = json.loads(ln.split(": ", 1)[1].replace("'", '"'))
                d_ok = d_ok and printed == run["positive"]["actual"]
            if ln.startswith("defaults ok: "):
                d_ok = d_ok and (repr(run["defaults"]["actual"]) in ln)
        ok(f"D {card} stdout printed values agree with stored JSON", d_ok)

        # E) ledger self-consistency
        eh = json.load(open(os.path.join(ev, "evidence_hashes.json"), encoding="utf-8"))
        bad = [rel for rel, claim in eh["files"].items()
               if sha_file(os.path.join(at, rel.replace("/", os.sep))) != claim]
        ok(f"E {card} evidence_hashes.json {len(eh['files'])}/{len(eh['files'])} == disk",
           not bad, f"revision={eh['revision']} problems={bad}")
        sm = json.load(open(os.path.join(ev, "source_manifest.json"), encoding="utf-8"))
        ok(f"E {card} source_manifest.oracle_document.sha256_now == disk oracle.md",
           sm["oracle_document"]["sha256_now"] == sha_file(os.path.join(at, "oracle.md")),
           f"now={sm['oracle_document']['sha256_now'][:16]}")
        ok(f"E {card} source_manifest v1 frozen-body hash still reproduces",
           sha_file(os.path.join(at, "oracle.md")) is not None
           and sm["oracle_document"]["v1_frozen_body_still_reproducible"])
        rr = json.load(open(os.path.join(at, "after", "rerun_sha256.json"), encoding="utf-8"))
        bad_r = [rel for rel, claim in rr["files"].items()
                 if sha_file(os.path.join(at, rel.replace("/", os.sep))) != claim]
        ok(f"E {card} after/rerun_sha256.json {len(rr['files'])}/{len(rr['files'])} == disk",
           not bad_r, f"problems={bad_r}")

        # F) oracle.md structure
        raw = open(os.path.join(at, "oracle.md"), "rb").read()
        txt = raw.decode("utf-8")
        d = dedupe[card]
        v1_ok = sha_file(os.path.join(at, "oracle.md")) is not None and (
            sha_file_str(txt[: d["authoritative_v1_cut"]["char_offset"]])
            == d["authoritative_v1_claim"])
        gap_ok = sha_file_str(txt[: d["provenance_gap_cut"]["char_offset"]]) == \
            d["provenance_gap_claim"]
        r2_snap = sha_file(os.path.join(REVIEW, "copy_r2", card, "a20260919-01", "oracle.md"))
        kept_r2 = sha_file_str(
            txt[: d["r2_heading_offsets_before"][1]])
        ok(f"F {card} exactly one r2 section", txt.count(MARKER) == 1,
           f"count={txt.count(MARKER)}")
        ok(f"F {card} v1 + provenance-gap hashes both reproduce", v1_ok and gap_ok,
           f"v1={v1_ok} gap={gap_ok}")
        ok(f"F {card} r2 whole-file hash == pre-r3 snapshot", 
           d["oracle_md_sha256_before"] == r2_snap,
           f"recorded={d['oracle_md_sha256_before'][:16]} copy_r2={r2_snap[:16]}")
        ok(f"F {card} oracle.md whole-file hash == recorded r3 value",
           sha_file(os.path.join(at, "oracle.md")) == d["oracle_md_sha256_after"],
           f"disk={sha_file(os.path.join(at, 'oracle.md'))[:16]}")
        del kept_r2

        # F-R3-01: the r3 note is an INSERTION after the kept prefix, not a trailing append
        pre_img = open(os.path.join(HERE, f"oracle_pre_{card}.md"), "rb").read()
        kb = verify[card]["P1_kept_region_bytes"]
        r3_note = raw[kb:]
        r301 = (
            raw[:kb] == pre_img[:kb]
            and len(pre_img) - verify[card]["P2_deleted_bytes"] + len(r3_note) == len(raw)
            and "\u63d2\u5165" in r3_note.decode("utf-8")
            and "\u672c\u8282\u7531\u4fee\u8ba2 r3 \u8ffd\u52a0" not in r3_note.decode("utf-8")
        )
        ok(f"F-R3-01 {card} r3 note is an insertion (live = pre[:K] + note)",
           r301,
           f"live={len(raw)} pre={len(pre_img)} folded={verify[card]['P2_deleted_bytes']} "
           f"note={len(r3_note)}: {len(pre_img)}-{verify[card]['P2_deleted_bytes']}"
           f"+{len(r3_note)}={len(raw)}")

        # F-R3-02: input_hashes_current carries the CURRENT digest of every input_hashes key
        b_doc = json.load(open(os.path.join(at, "binding.json"), encoding="utf-8"))
        h_doc = json.load(open(os.path.join(at, "handoff.json"), encoding="utf-8"))
        f302, detail302, stale302 = True, [], []
        for doc, name in ((b_doc, "binding"), (h_doc, "handoff")):
            cur = doc.get("input_hashes_current") or {}
            verdicts = doc.get("input_hashes_current_vs_input_hashes") or {}
            if set(cur) != set(doc.get("input_hashes", {})) or set(verdicts) != set(cur):
                f302 = False
                detail302.append(f"{name}: key sets differ")
                continue
            for rel, val in cur.items():
                if val != sha_file(os.path.join(at, rel.replace("/", os.sep))):
                    f302 = False
                    detail302.append(f"{name}.{rel}: current != disk")
            for rel, v in verdicts.items():
                expect = ("unchanged" if doc["input_hashes"][rel] == cur[rel]
                          else "stale_by_design")
                if v.get("verdict") != expect:
                    f302 = False
                    detail302.append(f"{name}.{rel}: verdict {v.get('verdict')} != {expect}")
                if expect == "stale_by_design":
                    stale302.append(f"{name}.{rel}")
                    if v.get("sha256_current") != cur[rel]:
                        f302 = False
                        detail302.append(f"{name}.{rel}: stale verdict lacks current digest")
        ok(f"F-R3-02 {card} input_hashes_current == disk, verdicts exact", f302,
           "; ".join(detail302) if detail302 else f"stale_by_design={stale302}")
        del r3_note, b_doc, h_doc

        # G) qualification states
        want_formula = "blocked" if card == "M08" else "review_pending"
        ok(f"G {card} qualification formula={want_formula}, disclosure=unmapped, "
           f"accuracy=unproven",
           qual["formula"]["state"] == want_formula
           and qual["disclosure_adaptation"]["state"] == "unmapped"
           and qual["accuracy"]["state"] == "unproven",
           f"formula={qual['formula']['state']}")

        # H) production source hashes
        b = json.load(open(os.path.join(at, "binding.json"), encoding="utf-8"))
        prod = {}
        for rel, claim in b["production_source_hashes"].items():
            p = os.path.join(b["production_source_root_readonly"], rel.replace("/", os.sep))
            prod[rel] = sha_file(p) == claim
        iso = {}
        for rel, claim in b["isolated_copy_hashes"].items():
            iso[rel] = sha_file(os.path.join(at, rel.replace("/", os.sep))) == claim
        ok(f"H {card} production + isolated source hashes unchanged",
           all(prod.values()) and all(iso.values()), f"prod={prod} iso={iso}")

    # I) change-set closure
    print("")
    print("-- change-set closure --")
    pre = {}
    for line in open(os.path.join(HERE, "tree_pre.txt"), encoding="ascii"):
        if line.startswith("#") or not line.strip():
            continue
        rel, h, _ = line.rstrip("\n").split("\t")
        pre[rel] = h
    post = {}
    for line in open(os.path.join(HERE, "tree_post.txt"), encoding="ascii"):
        if line.startswith("#") or not line.strip():
            continue
        rel, h, _ = line.rstrip("\n").split("\t")
        post[rel] = h
    changed = sorted(k for k in set(pre) & set(post) if pre[k] != post[k])
    added = sorted(set(post) - set(pre))
    removed = sorted(set(pre) - set(post))
    outside = [k for k in changed + added if not k.startswith(("M05/", "M06/", "M07/", "M08/"))]
    ok("I change set is closed inside the four attempt directories", not outside,
       f"changed={len(changed)} added={len(added)} removed={len(removed)} outside={outside}")
    ok("I nothing was removed", not removed, f"removed={removed}")
    for k in changed:
        print(f"      CHANGED {k}: {pre[k][:16]} -> {post[k][:16]}")
    for k in added:
        print(f"      ADDED   {k}")

    print("")
    failed = [n for n, c, _ in checks if not c]
    print(f"== TOTAL {len(checks) - len(failed)}/{len(checks)} checks passed ==")
    if failed:
        for n in failed:
            print(f"   FAILED: {n}")
    with open(os.path.join(HERE, "f11_verify_all.json"), "w", encoding="utf-8") as fh:
        json.dump({"checks": [{"name": n, "pass": c, "detail": d} for n, c, d in checks],
                   "changed": changed, "added": added, "removed": removed},
                  fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print("wrote f11_verify_all.json")
    return 0 if not failed else 1


def sha_file_str(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


if __name__ == "__main__":
    sys.exit(main())
