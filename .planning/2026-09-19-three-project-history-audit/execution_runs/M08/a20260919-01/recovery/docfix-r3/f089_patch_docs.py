"""F-M08-08 / F-M08-09 fix: put the qualified repack ledger where hash ledgers live,
and point M08's DEC-M08-1 at handoff.json.owner_action_required.

What changes, per card:
  binding.json   + docfix_r3_hash_ledger   (repack scope, old/new hashes, annotation proof)
  handoff.json   + docfix_r3_hash_ledger, OQ-02 counts corrected (original wording preserved
                 inside the ledger), revision r2 -> r3
  decision.md    + an appended "hash ledger r3" section (append-only; the r1 text stays)
                   M08 additionally gets the DEC-M08-1 r3 correction, appended, with the
                   r1 wording preserved verbatim above it

Three verified reference states are used so the ledger is a real three-column account:
  r1 = reviewer's snapshot copy/         (verified: oracle.md hashes to the authoritative v1 claim)
  r2 = reviewer's snapshot copy_r2/      (verified: oracle.md hashes to the pre-r3 whole-file hash)
  r3 = the attempt tree on disk now

Usage: <iso venv python> -X utf8 -B f089_patch_docs.py [--apply] > f089_patch_docs.out.txt
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
REVIEW = "C:/Users/\u90d1\u66fe\u6ce2/AppData/Local/Temp/m05m08-review-20260920-025942"
COPY, COPY_R2 = os.path.join(REVIEW, "copy"), os.path.join(REVIEW, "copy_r2")
CARDS = ("M05", "M06", "M07", "M08")
APPLY = "--apply" in sys.argv

dedupe = json.load(open(os.path.join(HERE, "f06_dedupe.json"), encoding="utf-8"))
verify = json.load(open(os.path.join(HERE, "f06_verify.json"), encoding="utf-8"))
oqs = json.load(open(os.path.join(HERE, "f07_fix_oq.json"), encoding="utf-8"))
named = json.load(open(os.path.join(HERE, "f08_named_files.json"), encoding="utf-8"))
repack = json.load(open(os.path.join(HERE, "f08_repack_diff.json"), encoding="utf-8"))

DEC_TEMPLATE = open(os.path.join(HERE, "decision_r3_template.md"), encoding="utf-8").read()
DEC1_TEMPLATE = open(os.path.join(HERE, "decision_m08_dec1_template.md"),
                     encoding="utf-8").read()
for_enum = "recovery/docfix-r3/f07_enumerate.py"
dec_m08_pointer = (
    "\n### 4) DEC-M08-1 指向 owner 三步（F-M08-09）\n\n"
    "`M08/decision.md` 的 DEC-M08-1 已在**本文件上方**的「DEC-M08-1 · r3 correction」节"
    "（紧接 r1 原文之后追加）改写为**追加式更正**：明确指向 "
    "`handoff.json.owner_action_required` 的三步（含「禁止重新挑选算例」约束），"
    "r1 原文逐字保留在更上方，未删除。\n"
)


def sha_file(p: str) -> str:
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def walk(root: str) -> dict[str, str]:
    out = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in ("venv", "__pycache__")]
        for name in filenames:
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, root).replace("\\", "/")
            # this pass's own tooling and raw outputs live here; they are enumerated
            # by snapshot_tree.py instead, so that a ledger does not depend on the
            # log file of the very run that writes it
            if rel.startswith("recovery/docfix-r3/"):
                continue
            out[rel] = full
    return out


def changed_between(root_a: str, root_b: str) -> tuple[list, list, list]:
    a, b = walk(root_a), walk(root_b)
    changed, added, removed = [], [], []
    for rel in sorted(set(a) & set(b)):
        if sha_file(a[rel]) != sha_file(b[rel]):
            changed.append({
                "path": rel,
                "sha256_before": sha_file(a[rel]),
                "sha256_after": sha_file(b[rel]),
                "bytes_before": os.path.getsize(a[rel]),
                "bytes_after": os.path.getsize(b[rel]),
            })
    for rel in sorted(set(b) - set(a)):
        added.append({"path": rel, "sha256_after": sha_file(b[rel]),
                      "bytes_after": os.path.getsize(b[rel])})
    for rel in sorted(set(a) - set(b)):
        removed.append({"path": rel, "sha256_before": sha_file(a[rel]),
                        "bytes_before": os.path.getsize(a[rel])})
    return changed, added, removed


def with_kinds(card: str, rows: list) -> list:
    pf = repack[card]["per_changed_file"]
    out = []
    for row in rows:
        entry = dict(row)
        info = pf.get(row["path"])
        if info and "kinds" in info:
            entry["diff_kinds"] = info["kinds"]
            entry["annotation_only"] = info["annotation_only"]
        out.append(entry)
    return out


def load(path: str):
    return json.load(open(path, encoding="utf-8"))


def dump(obj) -> bytes:
    return (json.dumps(obj, indent=1, ensure_ascii=False) + "\n").encode("utf-8")


def r1_r2_r3() -> None:
    print("== reference states ==")
    for card in CARDS:
        r1 = os.path.join(COPY, card, "a20260919-01", "oracle.md")
        r2 = os.path.join(COPY_R2, card, "a20260919-01", "oracle.md")
        print(f"   {card}: r1 oracle.md={sha_file(r1)[:16]} "
              f"r2 oracle.md={sha_file(r2)[:16]} "
              f"r2_is_pre_r3={sha_file(r2) == dedupe[card]['oracle_md_sha256_before']}")


def main() -> int:
    print("== F-M08-08 / F-M08-09: qualified repack ledger + DEC-M08-1 correction ==")
    print(f"apply={APPLY}")
    r1_r2_r3()
    ledger_out: dict[str, object] = {}
    for card in CARDS:
        at = os.path.join(BASE, card, "a20260919-01")
        bpath = os.path.join(at, "binding.json")
        hpath = os.path.join(at, "handoff.json")
        dpath = os.path.join(at, "decision.md")
        # idempotency guard: never append the r3 section twice
        for p in (bpath, hpath, dpath):
            blob = open(p, encoding="utf-8", newline="").read()
            if "docfix_r3_hash_ledger" in blob or "consistency revision r3" in blob:
                raise SystemExit(
                    f"{card}: {p} already carries the r3 addendum; restore the r2 copy "
                    "from the reviewer snapshot before re-applying"
                )
        before = {p: sha_file(p) for p in (bpath, hpath, dpath)}

        repack_changed, repack_added, repack_removed = changed_between(
            os.path.join(COPY, card, "a20260919-01"), os.path.join(COPY_R2, card, "a20260919-01")
        )
        r3_changed, r3_added, r3_removed = changed_between(
            os.path.join(COPY_R2, card, "a20260919-01"), at
        )
        named_rows = []
        for key, info in named.items():
            c, rel = key.split("/", 1)
            if c == card:
                named_rows.append({
                    "path": rel,
                    "sha256_r1": info["sha256_r1"],
                    "sha256_now": info["sha256_now"],
                    "changed": info["changed"],
                    "annotation_only_proof": info.get(
                        "annotation_only_proof_deep_equal_after_stripping_added_keys"),
                    "added_keys": info.get("added_keys", []),
                    "removed_keys": info.get("removed_keys", []),
                    "changed_pre_existing_leaves": info.get(
                        "changed_pre_existing_leaves", {}),
                    "pre_existing_leaves": info.get("pre_existing_leaves"),
                })

        ledger = {
            "generated_by": (
                "implementer, document/evidence consistency pass r3 "
                "(findings F-M08-06 / F-M08-07 / F-M08-08 / F-M08-09)"
            ),
            "qualification": (
                "'the frozen artefacts were not changed' is hereby QUALIFIED: the v1 frozen "
                "body of oracle.md and every frozen expectation (positive / continuity / "
                "defaults / negatives / tolerances / rejection conditions / disclosure "
                "figures) are byte-unchanged, and no product file was touched. What DID "
                "change is (a) oracle.md as a whole, because revision r2 appended a response "
                "section and r3 merged a duplicated r2 section into one and appended a "
                "provenance-gap note, and (b) the evidence files listed under repack_scope, "
                "which were repacked in r2 to carry new annotations. Every one of those byte "
                "differences is accounted for below."
            ),
            "reference_states": {
                "r1": "reviewer snapshot copy/ -- verified r1: each card's copy/oracle.md "
                      "hashes to the authoritative v1 claim carried inside oracle.md",
                "r2": "reviewer snapshot copy_r2/ -- verified r2: each card's "
                      "copy_r2/oracle.md hashes to the pre-r3 whole-file hash",
                "r3": "the attempt directory on disk after this pass",
            },
            "oracle_md_hash_ledger": {
                "v1_frozen_body_sha256": dedupe[card]["authoritative_v1_claim"],
                "v1_frozen_body_prefix_bytes": dedupe[card]["authoritative_v1_cut"]["payload_bytes"],
                "v1_frozen_body_prefix_chars": dedupe[card]["authoritative_v1_cut"]["char_offset"],
                "v1_still_reproducible_from_current_file": verify[card][
                    "P5_v1_claim_reproduces"],
                "whole_file_sha256_r1": sha_file(
                    os.path.join(COPY, card, "a20260919-01", "oracle.md")),
                "whole_file_sha256_r2": dedupe[card]["oracle_md_sha256_before"],
                "whole_file_sha256_r3": dedupe[card]["oracle_md_sha256_after"],
                "note": (
                    "handoff.json.input_hashes['oracle.md'] is the BINDING-TIME value = the v1 "
                    "frozen body hash. It is historical by design and does not equal the "
                    "whole-file hash of any later revision; it remains reproducible from the "
                    "current file as sha256(oracle.md[:prefix_bytes])."
                ),
            },
            "input_hashes_note": (
                "binding.json.input_hashes and handoff.json.input_hashes are the PRE-RUN (r1) "
                "input hashes captured before the product run (binding.json: "
                "created_before_runs = true). They are historical by design and are NOT "
                "claimed to equal the current bytes. For M08 the entry for "
                "evidence/M08/cases.json is affected: the r2 repack added four annotation keys "
                "and nothing else, which is proven below and in "
                "recovery/docfix-r3/f08_named_files.out.txt."
            ),
            "repack_scope_r1_to_r2": {
                "changed": with_kinds(card, repack_changed),
                "added": repack_added,
                "removed": repack_removed,
            },
            "named_by_F_M08_08": list(named_rows),
            "r3_pass_scope_r2_to_r3": {
                "changed": r3_changed,
                "added": r3_added,
                "removed": r3_removed,
            },
            "proofs": {
                "annotation_only": "recovery/docfix-r3/f08_named_files.out.txt "
                                   "(strip the added keys -> deep-equal to the r1 object)",
                "structural_diff": "recovery/docfix-r3/f08_repack_diff.out.txt",
                "oracle_dedup": "recovery/docfix-r3/f06_verify.out.txt",
                "enumeration": "recovery/docfix-r3/f07_enumerate.out.txt",
                "machine_readable": f"evidence/{card}/docfix_r3.json",
            },
            "corrections": [
                {
                    "finding": "F-M08-07",
                    "field": "handoff.json.open_questions[1] (OQ-02)",
                    "was_original_r2": (
                        "only the ratio dimension defaults to [0,1] (40 drivers, 3 explicit "
                        "documented exceptions plus 2 priced-volume exceptions)"
                        if card == "M08" else
                        "only the ratio dimension defaults to [0,1] (40 drivers, 3 explicit "
                        "and documented exceptions)"
                    ),
                    "now": (
                        "only the ratio dimension defaults to [0,1] (41 drivers, 4 outside "
                        "[0,1], plus 2 priced-volume exceptions in the per-activity family)"
                    ),
                    "why": "the registry has 41 ratio drivers; direct_growth.growth_rate "
                           "(domain (-1, inf)) was missing from the list of exceptions",
                },
            ],
        }
        if card != "M08":
            ledger["named_by_F_M08_08"].append({
                "note": "this card has no evidence file named by F-M08-08; its r1->r2 changes "
                        "are documentation only (see repack_scope_r1_to_r2)",
            })

        # ---- binding.json ----
        b = load(bpath)
        b["docfix_r3_hash_ledger"] = ledger
        # ---- handoff.json ----
        h = load(hpath)
        h["docfix_r3_hash_ledger"] = ledger
        h["revision"] = "r3"
        h["revision_note"] = (
            "r3 = document/evidence consistency pass (F-M08-06 dedup, F-M08-07 counts and "
            "attribution, F-M08-08 qualified repack ledger, F-M08-09 DEC-M08-1 correction). "
            "No expectation, tolerance, negative case, disclosure figure or product file "
            "changed."
        )
        for i, q in enumerate(h.get("open_questions", [])):
            if isinstance(q, str) and q.startswith("OQ-02"):
                if card == "M08":
                    h["open_questions"][i] = (
                        "OQ-02 (M06) - RESOLVED BY INDEPENDENT REVIEW (counts corrected in r3 "
                        "per F-M08-07): monetization_rate having no [0,1] bound is NOT a "
                        "contract gap, only a naming ambiguity. Enumeration (by the "
                        "implementer, checked by the reviewer): all 23 revenue_per_activity / "
                        "revenue_per_unit drivers carry the default (0, inf); only the ratio "
                        "dimension defaults to [0,1] (41 ratio drivers, of which 4 do not take "
                        "it: bank_revenue.asset_yield, bank_revenue.funding_cost, "
                        "store_cohorts.new_store_productivity and "
                        "direct_growth.growth_rate, whose domain is (-1, inf)), plus 2 "
                        "priced-volume exceptions in the per-activity family; "
                        "usage_platform.monetization_rate = (0.0, inf) is correct contract. If "
                        "anything changes it should be the attribute NAME, not the bound. The "
                        "r2 wording of this entry said '40 drivers, 3 explicit documented "
                        "exceptions plus 2 priced-volume exceptions' and is preserved in "
                        "docfix_r3_hash_ledger.corrections. See evidence/M08/oq_rulings.json "
                        "and evidence/M08/oq_rulings_enumeration.json."
                    )
                else:
                    h["open_questions"][i] = (
                        "OQ-02 (M06) - RESOLVED BY INDEPENDENT REVIEW (counts corrected in r3 "
                        "per F-M08-07): not a contract gap. Every revenue_per_activity / "
                        "revenue_per_unit driver carries the default (0, inf) bound (23 of "
                        "them), and only the ratio dimension defaults to [0,1] (41 ratio "
                        "drivers, 4 of which do not take it, plus 2 priced-volume exceptions); "
                        "usage_platform.monetization_rate = (0.0, inf) is therefore correct "
                        "contract, and the residual issue is NAME ambiguity only. If anything "
                        "changes it should be the attribute name, not the bound. The r2 wording "
                        "of this entry said '40 drivers, 3 explicit and documented exceptions' "
                        "and is preserved in docfix_r3_hash_ledger.corrections. See "
                        f"evidence/{card}/oq_rulings.json and "
                        f"evidence/{card}/oq_rulings_enumeration.json."
                    )

        # ---- decision.md ----
        dtext = open(dpath, encoding="utf-8", newline="").read()
        nl = "\r\n" if "\r\n" in dtext else "\n"
        rows = ["| file | sha256 r1 | sha256 now (read from disk) | verdict |",
                "|---|---|---|---|"]
        for row in named_rows:
            verdict = ("annotation-only (strip added keys -> deep-equal to r1)"
                       if row.get("changed") else "UNCHANGED (byte-identical to r1)")
            now_p = os.path.join(at, row["path"].replace("/", os.sep))
            rows.append(f"| `{row['path']}` | `{row['sha256_r1'][:16]}…` | "
                        f"`{sha_file(now_p)[:16]}…` | {verdict} |")
        detail = repack[card]["per_changed_file"]
        for rel, info in detail.items():
            if rel not in {r["path"] for r in named_rows} and "kinds" in info:
                now_p = os.path.join(at, rel.replace("/", os.sep))
                now_h = sha_file(now_p) if os.path.exists(now_p) else "ABSENT"
                rows.append(f"| `{rel}` | `{info['sha256_r1'][:16]}…` | "
                            f"`{now_h[:16]}…` | r2 response edit, "
                            f"kinds={info['kinds']} |")
        check = "" if card == "M08" else (
            "本卡在 F-M08-08 点名的证据文件上没有变化：`M06/M07 negative_results.json` 与 "
            "`M07 run_result.json` 与经校验的 r1 快照**逐字节相同**（见 `f08_named_files.out.txt`）。\n\n"
        )
        section = DEC_TEMPLATE.format(
            card=card,
            oracle_before=dedupe[card]["oracle_md_sha256_before"],
            oracle_before_bytes=dedupe[card]["oracle_md_bytes_before"],
            oracle_after=dedupe[card]["oracle_md_sha256_after"],
            oracle_after_bytes=dedupe[card]["oracle_md_bytes_after"],
            removed_bytes=verify[card]["P2_deleted_bytes"],
            removed_sha=verify[card]["P2_deleted_sha256"],
            inserted_bytes=verify[card]["P2_inserted_bytes"],
            inserted_sha=verify[card]["P2_inserted_sha256"],
            kept_bytes=verify[card]["P1_kept_region_bytes"],
            kept_sha=verify[card]["P1_kept_region_sha256_after"],
            v1_claim=dedupe[card]["authoritative_v1_claim"],
            v1_offset=dedupe[card]["authoritative_v1_cut"]["char_offset"],
            v1_bytes=dedupe[card]["authoritative_v1_cut"]["payload_bytes"],
            gap_claim=dedupe[card]["provenance_gap_claim"],
            oq_before=oqs[card]["sha256_before"],
            oq_after=oqs[card]["sha256_after"],
            enum_sha=oqs[card]["enumeration_evidence_sha256"],
            repack_scope_table=check + "\n".join(rows),
            dec_m08_pointer=dec_m08_pointer if card == "M08" else "",
        )
        add = (DEC1_TEMPLATE if card == "M08" else "") + section
        if not dtext.endswith(nl):
            dtext += nl
        new_dtext = dtext + nl + add.replace("\n", nl)
        new_decision = new_dtext.encode("utf-8")
        new_b = dump(b)
        new_h = dump(h)

        print("")
        print(f"-- {card} --")
        print(f"   repack_scope_r1_to_r2: changed={len(repack_changed)} "
              f"added={len(repack_added)} removed={len(repack_removed)}")
        print(f"   r3_pass_scope_r2_to_r3: changed={len(r3_changed)} "
              f"added={len(r3_added)} removed={len(r3_removed)}")
        for row in named_rows:
            print(f"   named {row['path']}: changed={row['changed']} "
                  f"annotation_only={row.get('annotation_only_proof')}")
        for p, label in ((bpath, "binding.json"), (hpath, "handoff.json"),
                         (dpath, "decision.md")):
            pass
        print(f"   binding.json {before[bpath][:16]} -> "
              f"{hashlib.sha256(new_b).hexdigest()[:16]}")
        print(f"   handoff.json {before[hpath][:16]} -> "
              f"{hashlib.sha256(new_h).hexdigest()[:16]}")
        print(f"   decision.md  {before[dpath][:16]} -> "
              f"{hashlib.sha256(new_decision).hexdigest()[:16]}")

        if APPLY:
            open(bpath, "wb").write(new_b)
            open(hpath, "wb").write(new_h)
            open(dpath, "wb").write(new_decision)
            for p, blob in ((bpath, new_b), (hpath, new_h), (dpath, new_decision)):
                got = sha_file(p)
                assert got == hashlib.sha256(blob).hexdigest(), p
            print("   APPLIED")
        ledger_out[card] = {
            "binding.json": {"sha256_before": before[bpath],
                             "sha256_after": hashlib.sha256(new_b).hexdigest()},
            "handoff.json": {"sha256_before": before[hpath],
                             "sha256_after": hashlib.sha256(new_h).hexdigest()},
            "decision.md": {"sha256_before": before[dpath],
                            "sha256_after": hashlib.sha256(new_decision).hexdigest()},
            "repack_scope_r1_to_r2_changed": len(repack_changed),
            "r3_pass_scope_r2_to_r3_changed": len(r3_changed),
        }

    with open(os.path.join(HERE, "f089_patch_docs.json"), "w", encoding="utf-8") as fh:
        json.dump(ledger_out, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print("")
    print("wrote f089_patch_docs.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
