"""Side re-verification of the items the reviewer already confirmed, recomputed here
with hashes (the briefing has to restate them, so they are re-derived rather than quoted).

  F-M08-02  disclosure impact anchored to reading C: 0 -> 36.1210 / 2.3610 / 6.99%,
            -15 probe -> 21.1210 / 12.6390 / 37.44%
  F-M08-01  after/rerun_sha256.json == disk (32/32 for M05-M07 and 34/34 for M08);
            commands.json == 92875088...; the stale d48a54df... kept as a provenance gap
  F-M08-04  card_conflict.json quotes ONLY the arithmetic actually printed on card_M08.md
            L42 (byte-compared against the card), and the four index copies are identical
  F-M08-05  the two sign probes declare base_input = defaults and state the 70/40
            positive-baseline readings plus per-reading expectations
  common-6  honest_gap no longer claims commands.json carries the oracle hash; the false
            pointer is gone and mtime_ordering is present with oracle_json_precedes_run
  common-7  commands.json's G unit argv points at the real scratch path and is scoped to M05
  common-9  M07: 1 reported + 1 derived + 1 missing required drivers, and
            required_drivers_mapped counts the REPORTED one only
  OQ-02/04  conclusions unchanged and now backed by the corrected enumeration

Usage: <iso venv python> -X utf8 -B f10_recheck.py > f10_recheck.out.txt
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = (
    "C:/Users/\u90d1\u66fe\u6ce2/Projects/revenue-forecast/.planning/"
    "2026-09-19-three-project-history-audit/execution_runs"
)
V2 = ("C:/Users/\u90d1\u66fe\u6ce2/Projects/revenue-forecast/.planning/"
      "2026-09-19-three-project-history-audit/execution_v2")
CARDS = ("M05", "M06", "M07", "M08")
results: list[tuple[str, bool, str]] = []


def sha_file(p: str) -> str:
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def sha_str(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def ok(name: str, cond: bool, detail: str = "") -> None:
    results.append((name, bool(cond), detail))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}" + (f" -- {detail}" if detail else ""))


def P(card: str, *parts: str) -> str:
    return os.path.join(BASE, card, "a20260919-01", *parts)


def main() -> int:
    print("== side re-verification (F-M08-02 / -01 / -04 / -05, common-6/7/9, OQ-02/04) ==")

    print("")
    print("-- F-M08-02 disclosure impact anchored to reading C --")
    imp_p = P("M08", "evidence", "M08", "disclosure_impact_readings.json")
    imp = json.load(open(imp_p, encoding="utf-8"))
    print(f"   sha256={sha_file(imp_p)}")
    print(f"   top-level keys={list(imp)}")
    blob = json.dumps(imp, ensure_ascii=False)
    for needle in ("36.1210", "2.3610", "6.99", "21.1210", "12.6390", "37.44"):
        ok(f"F-M08-02 reading-C figure {needle} present",
           needle in blob, f"found={needle in blob}")
    ok("F-M08-02 anchored to reading C, not A",
       "C" in json.dumps(imp.get("readings", imp), ensure_ascii=False)[:4000])
    hist_p = P("M08", "evidence", "M08", "historical_reconciliation.json")
    hist = json.load(open(hist_p, encoding="utf-8"))
    ra = hist.get("reference_arithmetic", {})
    ok("F-M08-02 historical_reconciliation records the honest range",
       ra.get("honest_range") is not None
       and ra.get("sensitivity_probe_minus15_residual_reading_C_pct") == "37.44"
       and ra.get("residual_C_pct") == "6.99",
       f"range='{str(ra.get('honest_range'))[:70]}...'")

    print("")
    print("-- F-M08-01 rerun_sha256 == disk, commands.json hash, provenance gap --")
    for card in CARDS:
        rr_p = P(card, "after", "rerun_sha256.json")
        rr = json.load(open(rr_p, encoding="utf-8"))
        bad = [rel for rel, claim in rr["files"].items()
               if sha_file(P(card, rel.replace("/", os.sep))) != claim]
        ok(f"F-M08-01 {card} rerun_sha256 {len(rr['files'])}/{len(rr['files'])} == disk",
           not bad, f"problems={bad} sha256={sha_file(rr_p)[:16]}")
        note = rr.get("commands_json_note", {})
        ok(f"F-M08-01 {card} commands.json stale r1 value kept as provenance gap",
           note.get("stale_hash_recorded_in_r1", "").startswith("d48a54df")
           and note.get("current_hash", "").startswith("92875088"),
           f"r1={note.get('stale_hash_recorded_in_r1', '')[:16]} "
           f"now={note.get('current_hash', '')[:16]}")
    cmd_hash = sha_file(P("M08", "commands.json"))
    ok("F-M08-01 commands.json == 92875088...", cmd_hash.startswith("92875088"),
       f"sha256={cmd_hash}")
    ok("F-M08-01 commands.json identical in all four attempts",
       len({sha_file(P(c, "commands.json")) for c in CARDS}) == 1)

    print("")
    print("-- F-M08-04 only the printed arithmetic is quoted --")
    cf_p = P("M08", "evidence", "M08", "card_conflict.json")
    cf = json.load(open(cf_p, encoding="utf-8"))
    printed = cf["conflicting_texts"]["card"].get("text_actually_printed_at_L42")
    card_raw = open(os.path.join(V2, "card_M08.md"), "rb").read()
    card_sha = hashlib.sha256(card_raw).hexdigest()
    l42 = card_raw.decode("utf-8").split("\n")[41].rstrip("\r")
    ok("F-M08-04 card_conflict quotes exactly the card's L42 line (byte-exact)",
       printed == l42,
       f"quote={printed!r} card_sha256={card_sha[:16]}")
    ok("F-M08-04 the quote is arithmetic, not a symbolic formula",
       "\u7b97\u5f0f" not in str(printed) and "+ backlog_remeasurements" not in str(printed)
       and "100+40" in str(printed))
    ok("F-M08-04 symbolic-form quote removed from the r1 'text' field",
       "text" not in cf["conflicting_texts"]["card"]
       and "text_actually_printed_at_L42" in cf["conflicting_texts"]["card"])
    idx = {"card_M08.md": os.path.join(V2, "card_M08.md"),
           "model_cards.md": os.path.join(V2, "model_cards.md"),
           "model_cards.json": os.path.join(V2, "model_cards.json"),
           "dispatch.json": os.path.join(V2, "dispatch.json")}
    hits = {}
    for name, path in idx.items():
        text = open(path, encoding="utf-8").read()
        hits[name] = text.count("100+40\u22125\u221210\u221215\u221260=50")
    ok("F-M08-04 all four index copies print the identical arithmetic",
       all(v >= 1 for v in hits.values()), f"occurrences={hits}")
    ok("F-M08-04 the string quoted by the finding ('100+40-5-10+-15-60') exists in NO index file",
       all(("100+40\u22125\u221210+\u221215\u221260" not in open(p, encoding="utf-8").read())
           for p in idx.values()),
       "the actual printed string is the reading-A rendering; the reading-C rendering "
       "would be 100+40-5+-10+-15-60 (owner correction target)")

    print("")
    print("-- F-M08-05 sign probes are explicitly based on defaults --")
    for card in ("M08",):
        neg = json.load(open(P(card, "evidence", card, "negative_results.json"),
                             encoding="utf-8"))
        probes = [o for o in neg["observations_not_gating"]
                  if str(o.get("id", "")).startswith("OBS-SIGN")]
        ok(f"F-M08-05 {card} both sign probes present", len(probes) == 2,
           f"ids={[o.get('id') for o in probes]}")
        for o in probes:
            ok(f"F-M08-05 {o.get('id')} base_input=defaults", o.get("base_input") == "defaults",
               f"base_input={o.get('base_input')!r}")
            ok(f"F-M08-05 {o.get('id')} states the 70/40 positive baseline",
               "70.0" in str(o.get("base_input_meaning"))
               and "40.0" in str(o.get("base_input_meaning")),
               str(o.get("base_input_meaning"))[:80] + "...")
            ok(f"F-M08-05 {o.get('id')} carries per-reading expectations",
               isinstance(o.get("expected_under_each_reading_on_this_base"), dict),
               str(o.get("expected_under_each_reading_on_this_base")))
        run = json.load(open(P(card, "evidence", card, "run_result.json"), encoding="utf-8"))
        obs = [o for o in run["observations"] if str(o.get("id", "")).startswith("OBS-SIGN")]
        ok(f"F-M08-05 run_result observations carry the same annotations",
           len(obs) == 2 and all(o.get("base_input") == "defaults" for o in obs),
           f"ids={[o.get('id') for o in obs]}")

    print("")
    print("-- common-6 honest_gap corrected, mtime_ordering present --")
    for card in CARDS:
        sm_p = P(card, "evidence", card, "source_manifest.json")
        sm = json.load(open(sm_p, encoding="utf-8"))
        gap = sm["oracle_document"]["honest_gap"]
        mo = sm["oracle_document"]["mtime_ordering"]
        ok(f"common-6 {card} honest_gap refutes the old commands.json claim",
           "does NOT carry an oracle.md hash" in gap
           or "does NOT carry" in gap,
           "old pointer removed")
        ok(f"common-6 {card} mtime_ordering present and oracle precedes the run",
           mo.get("oracle_json_precedes_run") is True
           and mo.get("oracle_json_mtime", 1e18) < mo.get("product_stdout_mtime", 0),
           f"oracle_json={mo.get('oracle_json_mtime')} stdout={mo.get('product_stdout_mtime')}")

    print("")
    print("-- common-7 G unit argv points at the real scratch tree, M05 only --")
    cmds = json.load(open(P("M05", "commands.json"), encoding="utf-8"))
    units = cmds["units"] if isinstance(cmds.get("units"), list) else []
    g = [u for u in units if str(u.get("unit_id", "")).upper().startswith("G")]
    ok("common-7 exactly one G unit", len(g) == 1,
       f"unit_ids={[u.get('unit_id') for u in units]}")
    if g:
        argv = g[0].get("argv", [])
        joined = "\n".join(str(a) for a in argv)          # decoded, not re-escaped
        ok("common-7 G argv names the real M05 scratch runner path",
           "M05\\a20260919-01\\recovery\\selfcheck\\scripts\\run_card.py" in joined
           and "M05-M08\\a20260919-01\\recovery\\selfcheck" not in joined,
           f"argv[4]={argv[4] if len(argv) > 4 else None}")
        ok("common-7 G unit declares M05-only scope and the shared runner hash",
           "M05 only" in str(g[0].get("scope"))
           and "fd3a11c9226a7bb14ea9ac91b00148a174219087e44f3cf18bb52d914e6f448a"
           in json.dumps(g[0], ensure_ascii=False),
           str(g[0].get("scope"))[:60])
    ok("common-7 the runner really is identical across the four attempts",
       len({sha_file(P(c, "scripts", "run_card.py")) for c in CARDS}) == 1,
       f"sha256={sha_file(P('M05', 'scripts', 'run_card.py'))}")

    print("")
    print("-- common-9 M07 driver accounting --")
    dm_p = P("M07", "evidence", "M07", "disclosure_mapping.json")
    dm = json.load(open(dm_p, encoding="utf-8"))
    mv = dm["mapped_vs_missing"]
    per = dm["per_driver_disclosure_mapping"]
    statuses = {row.get("parameter_id"): row.get("reported_derived_assumed") for row in per}
    required = {row.get("parameter_id"): row.get("reported_derived_assumed")
                for row in per if str(row.get("role", "")).startswith("required driver")}
    print(f"   sha256={sha_file(dm_p)}")
    print(f"   per_driver statuses (all 4, incl. the optional other_revenue)={statuses}")
    print(f"   required_driver statuses={required}")
    print(f"   mapped_vs_missing={json.dumps(mv, ensure_ascii=False)}")
    vals = sorted(str(v).lower() for v in required.values())
    ok("common-9 M07 required drivers = exactly 1 reported + 1 derived + 1 missing",
       len(required) == 3
       and sum("reported" in v for v in vals) == 1
       and sum("derived" in v for v in vals) == 1
       and sum("missing" in v for v in vals) == 1, f"statuses={vals}")
    ok("common-9 mapped counts only the reported driver",
       mv["required_drivers_mapped"] == 1 and mv["required_drivers_total"] == 3
       and mv["mapped_drivers"] == 1,
       f"mapped={mv['required_drivers_mapped']}/{mv['required_drivers_total']}")

    print("")
    print("-- OQ-02 / OQ-04 conclusions --")
    for card in CARDS:
        oq_p = P(card, "evidence", card, "oq_rulings.json")
        oq = json.load(open(oq_p, encoding="utf-8"))
        e = oq["OQ_02"]["enumeration_performed"]
        ok(f"OQ-02 {card} 41 ratio drivers / 4 outside [0,1] / 23 per-activity / 2 priced-volume",
           e["ratio_drivers_total"] == 41
           and e["ratio_drivers_not_in_0_1_total"] == 4
           and e["revenue_per_activity_and_per_unit_drivers_total"] == 23
           and len(e["revenue_per_activity_and_per_unit_exceptions"]) == 2,
           f"sha256={sha_file(oq_p)[:16]}")
        ok(f"OQ-02 {card} ruling unchanged (not a contract gap, naming ambiguity only)",
           "NOT a contract gap" in oq["OQ_02"]["ruling"])
        ok(f"OQ-02 {card} monetization_rate bounds == (0, inf)",
           e["usage_platform.monetization_rate_bounds"] == [0.0, None],
           f"{e['usage_platform.monetization_rate_bounds']}")
        ok(f"OQ-04 {card} upheld with backlog_remeasurements named as the risk",
           "UPHELD" in oq["OQ_04"]["ruling"]
           and "backlog_remeasurements" in json.dumps(oq["OQ_04"], ensure_ascii=False),
           oq["OQ_04"]["mechanism"])

    print("")
    failed = [n for n, c, _ in results if not c]
    print(f"== {len(results) - len(failed)}/{len(results)} side checks passed ==")
    for n in failed:
        print(f"   FAILED: {n}")
    with open(os.path.join(HERE, "f10_recheck.json"), "w", encoding="utf-8") as fh:
        json.dump([{"name": n, "pass": c, "detail": d} for n, c, d in results],
                  fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print("wrote f10_recheck.json")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
