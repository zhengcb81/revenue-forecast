"""Final r4 verification for M01-M04.

Checks that every point-review remediation item landed, that NO measured value or
frozen judgement changed, and that no production repository was written.

ASCII-only stdout.
"""

from __future__ import annotations

import hashlib
import io
import json
import os

RF = os.path.join(os.environ["USERPROFILE"], "Projects", "revenue-forecast")
PLAN = os.path.join(RF, ".planning", "2026-09-19-three-project-history-audit")
CARDS = ["M01", "M02", "M03", "M04"]


def attempt(card):
    return os.path.join(PLAN, "execution_runs", card, "a20260919-01")


def evidence(card):
    return os.path.join(attempt(card), "evidence", card)


def sha(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def jload(path):
    with io.open(path, encoding="utf-8") as handle:
        return json.load(handle)


def tload(path):
    with io.open(path, encoding="utf-8") as handle:
        return handle.read()


def main():
    problems = []
    for card in CARDS:
        a, e = attempt(card), evidence(card)
        review = tload(os.path.join(a, "review.md"))
        oracle = tload(os.path.join(a, "oracle.md"))
        handoff = jload(os.path.join(a, "handoff.json"))
        qual = jload(os.path.join(e, "qualification.json"))
        sm = jload(os.path.join(e, "source_manifest.json"))
        r4 = jload(os.path.join(e, "revision_r4.json"))

        # ---- P1-1 ----
        if card in ("M02", "M04"):
            if oracle.count("## 修订 r2 索引") != 1:
                problems.append("%s P1-1: r2 index append count = %d" % (card, oracle.count("## 修订 r2 索引")))
            if "本节为事后补记：r2 轮曾声称已追加本节但实际未落盘" not in oracle:
                problems.append("%s P1-1: missing the honest 'claimed but never landed' wording" % card)
            rec = r4["items"]["P1-1"]
            if rec.get("oracle_md_bytes_before_r4_append") not in (7838, 10495):
                problems.append("%s P1-1: unexpected pre-append byte count %r"
                                % (card, rec.get("oracle_md_bytes_before_r4_append")))
        else:
            if "## 修订 r2 索引" in oracle:
                problems.append("%s P1-1: unexpected r2 index on this card" % card)

        # ---- P1-2 ----
        sc = os.path.join(a, "recovery", "r2_exit_code_selfcheck", "selfcheck_result.json")
        if not os.path.exists(sc):
            problems.append("%s P1-2: no per-card selfcheck_result.json" % card)
        else:
            doc = jload(sc)
            rcs = {c["id"]: c["raw_returncode"] for c in doc["cases"]}
            want = {"A_corrupted_oracle_expectation": 3, "B_corrupted_case_plan": 1,
                    "C_uncorrupted_card": 0, "D_corrupted_positive_input": 2}
            if rcs != want:
                problems.append("%s P1-2: selfcheck rc map %s != %s" % (card, rcs, want))
            if not doc.get("all_cases_as_expected"):
                problems.append("%s P1-2: all_cases_as_expected false" % card)
            if "recovery/r2_exit_code_selfcheck/selfcheck_result.json" not in handoff["evidence_paths"]:
                problems.append("%s P1-2: evidence_paths missing the (now existing) selfcheck file" % card)

        # ---- P1-3 ----
        revs = [x["revision"] for x in handoff["revision_history"]]
        if revs != ["r1", "r2", "r2", "r3", "r4"]:
            problems.append("%s P1-3: revision_history rounds %s" % (card, revs))

        # ---- P2-1 ----
        if handoff["status"] != "accepted_scoped":
            problems.append("%s P2-1: status=%r" % (card, handoff["status"]))
        if handoff["reviewer_status"] != "point_review_returned":
            problems.append("%s P2-1: reviewer_status=%r" % (card, handoff["reviewer_status"]))
        if handoff.get("reviewer_scope") != "formula only":
            problems.append("%s P2-1: reviewer_scope missing" % card)
        if not handoff.get("reviewer_finding"):
            problems.append("%s P2-1: reviewer_finding missing" % card)
        if "accepted_scoped" not in handoff["qualifications"]["formula"]:
            problems.append("%s P2-1: qualifications.formula lost accepted_scoped" % card)

        # ---- P2-2 ----
        if qual["formula"]["status"] != "accepted_scoped":
            problems.append("%s P2-2: formula.status=%r" % (card, qual["formula"]["status"]))
        if qual["formula"]["not_yet_independently_reviewed"] is not False:
            problems.append("%s P2-2: not_yet_independently_reviewed not false" % card)
        if "independent_review" not in qual["formula"]:
            problems.append("%s P2-2: independent_review block missing" % card)
        if qual["formula"].get("implementer_claim") != "pass":
            problems.append("%s P2-2: implementer_claim changed" % card)
        # ---- discipline: these two columns must never move ----
        if qual["disclosure_adaptation"]["status"] != "unmapped":
            problems.append("%s DISCIPLINE: disclosure_adaptation changed" % card)
        if qual["accuracy"]["status"] != "unproven":
            problems.append("%s DISCIPLINE: accuracy changed" % card)
        if handoff["qualifications"]["disclosure_adaptation"] != "unmapped":
            problems.append("%s DISCIPLINE: handoff disclosure qualification changed" % card)
        if handoff["qualifications"]["accuracy"] != "unproven":
            problems.append("%s DISCIPLINE: handoff accuracy qualification changed" % card)

        # ---- P2-3 ----
        versions = sm["oracle_versions"]["oracle_md_versions"]
        if len(versions) < 2:
            problems.append("%s P2-3: oracle_md_versions has %d entries" % (card, len(versions)))
        else:
            current = versions[-1]["sha256"]
            if current != sha(os.path.join(a, "oracle.md")):
                problems.append("%s P2-3: current entry %s != disk %s"
                                % (card, current[:12], sha(os.path.join(a, "oracle.md"))[:12]))

        # ---- P3-1 ----
        r3 = jload(os.path.join(e, "revision_r3.json"))
        entry = r3["authoritative_hashes_at_r3_closeout"]["evidence/revision_r3.json"]
        if not str(entry.get("sha256", "")).startswith("SELF-REFERENCE:"):
            problems.append("%s P3-1: self-reference not made explicit" % card)
        after = jload(os.path.join(a, "after", "rerun_sha256.json"))
        if "evidence/revision_r3.json" not in after.get("self_hashes", {}):
            problems.append("%s P3-1: real r3 hash not recorded externally" % card)
        elif after["self_hashes"]["evidence/revision_r3.json"] != sha(os.path.join(e, "revision_r3.json")):
            problems.append("%s P3-1: external r3 hash is stale" % card)

        # ---- P3-2 ----
        items = sm["revision_r2"]["review_items"]
        if card != "M03" and "F-M03-01" in items:
            problems.append("%s P3-2: F-M03-01 still listed" % card)
        if card != "M04" and "F-M04-01" in items:
            problems.append("%s P3-2: F-M04-01 still listed" % card)
        if "F-M02-01(pending ruling)" not in items:
            problems.append("%s P3-2: F-M02-01 reservation lost" % card)
        for q in handoff["open_questions"]:
            if "evidence/<card>/first_run_forensics.json" in q:
                problems.append("%s P3-2: placeholder forensics path still present" % card)
            # on the non-M01 cards the pointer must now point at M01 and say why
            if card != "M01" and "first_run_forensics" in q:
                if "M01's evidence/M01/first_run_forensics.json" not in q:
                    problems.append("%s P3-2: forensics pointer not redirected to M01" % card)

        # ---- P3-3 ----
        scr = handoff.get("shared_copy_registration", {})
        if "identical_across_cards" not in scr or "per_card_distinct_evidence" not in scr:
            problems.append("%s P3-3: shared-copy registration missing" % card)

        # ---- verdict paste + reviewer scope ----
        if review.count("## 独立 reviewer session 点复审（裁决）") != 1:
            problems.append("%s verdict section count != 1" % card)
        if review.count("## 点复审未予验证的事项（原样承接，不得当作已证）") != 1:
            problems.append("%s reviewer-scope block count != 1" % card)
        if "accepted_scoped" not in review:
            problems.append("%s verdict text missing accepted_scoped" % card)

        # ---- M03 provenance permanence ----
        if card == "M03":
            rec = tload(os.path.join(a, "recovery", "README.md"))
            if "PERMANENT provenance event" not in rec:
                problems.append("M03: provenance event not registered in recovery/README.md")
            if not any(q.startswith("M03 PERMANENT provenance event") for q in handoff["open_questions"]):
                problems.append("M03: provenance event not in handoff.open_questions")
        # M04: ACTIVE stop must still be present and not weakened
        if card == "M04":
            if "STOP_DISCLOSURE_ADAPTATION" not in review:
                problems.append("M04: STOP_DISCLOSURE_ADAPTATION missing from review.md")
            hit = json.dumps(handoff.get("stop_conditions_hit", []))
            if "STOP_DISCLOSURE_ADAPTATION" not in hit:
                problems.append("M04: stop_conditions_hit lost the ACTIVE stop")
            al = tload(os.path.join(e, "accounting_decision.md"))
            if "ACTIVE `STOP_DISCLOSURE_ADAPTATION`" not in al and "ACTIVE STOP" not in al:
                problems.append("M04: accounting_decision.md lost the ACTIVE stop wording")

        # ---- discipline: measured values unchanged ----
        oracle_json = jload(os.path.join(e, "oracle.json"))
        run = jload(os.path.join(e, "run_result.json"))
        expected_map = {"M01": [220.0, 110.0, 0.0], "M02": [80.0, 0.0, 120.0],
                        "M03": [305.0], "M04": [730.0]}
        if oracle_json["positive"]["expected_float"] != expected_map[card]:
            problems.append("%s DISCIPLINE: frozen expected changed" % card)
        if run["negative_summary"]["passed"] != run["negative_summary"]["total"]:
            problems.append("%s DISCIPLINE: negatives no longer all rejected" % card)
        if run["negative_summary"]["total"] != {"M01": 11, "M02": 11, "M03": 13, "M04": 15}[card]:
            problems.append("%s DISCIPLINE: negative count changed" % card)
        # ---- JSON parse + encoding ----
        for root, _d, files in os.walk(a):
            if os.sep + "iso" + os.sep in root + os.sep or root.endswith(os.sep + "iso"):
                continue
            for name in files:
                p = os.path.join(root, name)
                if name.endswith(".json"):
                    try:
                        jload(p)
                    except Exception as exc:  # noqa: BLE001
                        problems.append("JSON parse failure %s: %s" % (p, exc))
                if name.lower().endswith((".txt", ".md", ".json", ".diff", ".py", ".ps1")):
                    with open(p, "rb") as handle:
                        if handle.read(2) in (b"\xff\xfe", b"\xfe\xff"):
                            problems.append("UTF-16 file: %s" % p)
        # ---- production unchanged ----
        binding = jload(os.path.join(a, "binding.json"))
        for rel, want in binding["production_source_hashes"].items():
            if sha(os.path.join(RF, rel.replace("/", os.sep))) != want:
                problems.append("production drift %s (%s)" % (rel, card))

    if problems:
        print("PROBLEMS (%d):" % len(problems))
        for p in problems:
            print("  -", p)
        return 1
    print("r4 verification: all checks pass, %d cards" % len(CARDS))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
