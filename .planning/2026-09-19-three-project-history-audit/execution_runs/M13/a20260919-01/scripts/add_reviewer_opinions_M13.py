"""Record the independent reviewer's opinions on the open questions in M13's hand-off artefacts.

M13 has no card_facts.json (its documents are hand-written), so this variant writes the reviewer's
positions into handoff.json and appends them to decision.md. They are explicitly labelled as the
REVIEWER's opinions, not as decisions adopted by the implementer. Standards library only.
"""

from __future__ import annotations

import json
import os
import time

OPINIONS = [
    "OQ-01 (binding): the independent reviewer accepted this attempt's handling - the code under "
    "test is byte-identical to production and the isolation semantics were measured to hold - and "
    "characterises the residual question as provenance DOCUMENTATION: the owner should state in "
    "writing either (a) that a self-built read-only snapshot byte-identical to production is "
    "accepted as equivalent to the I-00-B binding, or (b) that I-00-B must add a materialisation "
    "step and later cards must reference its output. The implementer does NOT adopt this as a "
    "decision; it is the reviewer's opinion, carried for the owner.",
    "OQ-02 (silent zero-fill): the reviewer AGREES to register it and OPPOSES fixing it in this "
    "batch; the reviewer's own independent enumeration found the same surface (31 optional driver "
    "slots without an explicit default across 24 models) and suggests the owner require an explicit "
    "value or an explicit null at the D (disclosure-adaptation) stage instead of changing the "
    "formula-layer semantics.",
    "OQ-03 (signed driver vs the non-negative revenue check): the reviewer AGREES to register and "
    "OPPOSES fixing it in this batch. The reviewer adds that the check is PER ROW, so a single "
    "negative year during a clawback refuses the whole row, while the correct accounting treatment "
    "depends on the presentation convention (net presentation vs separate lines) - an accounting "
    "reviewer's remit. Both sides were measured (recovery/probes/signed_driver_probe.json: "
    "performance_fee_revenue = -100 -> refused by the non-negative-revenue check).",
    "OQ-04 (invalid frozen observation OBS-SIGNED-PERF-FEE): the reviewer judged the handling "
    "ACCEPTABLE - do not repack the frozen fixture, keep the invalid observation and answer the "
    "factual question with a labelled post-hoc probe - and asked for the invalid observation to be "
    "marked inside cases.json, which revision r3 did with an append-only annotation whose only "
    "difference is proven by evidence/M13/cases_annotation_repack.json.",
    "OQ-05 (pytest / historical suite): the reviewer AGREES that this card does not need it: the "
    "batch's evidence chain is a single standard-library-only runner plus frozen JSON, and the "
    "historical 97 tests / 216 subtests are not part of it. If the owner requires a re-run it "
    "should be registered as a SEPARATE regression gate, not folded into the formula sign-off "
    "conditions.",
]


def main() -> int:
    attempt = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    handoff_path = os.path.join(attempt, "handoff.json")
    with open(handoff_path, encoding="utf-8") as handle:
        doc = json.load(handle)
    doc["reviewer_opinions_on_open_questions"] = OPINIONS
    doc["reviewer_opinions_note"] = (
        "recorded from the relayed independent review of 2026-09-20; these are the REVIEWER's "
        "positions and were NOT adopted as decisions by the implementer")
    with open(handoff_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(doc, handle, ensure_ascii=False, indent=1)
        handle.write("\n")

    decision_path = os.path.join(attempt, "decision.md")
    with open(decision_path, encoding="utf-8") as handle:
        text = handle.read()
    heading = "## 独立复核者对上述开放项的意见（**不是本实现者的决定**）"
    if heading in text:
        print("decision.md already carries the reviewer-opinions section")
    else:
        text = text.rstrip("\n") + "\n\n" + heading + """

以下为 2026-09-20 独立复核转达的**复核者立场**，原样承接，**未由实现者采纳为决定**；owner 需据此自行
裁定（复核者对 OQ-02 / OQ-03 明确表示「同意登记、反对在本批修」）：

""" + "\n".join("- %s" % item for item in OPINIONS) + "\n"
        with open(decision_path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)

    print("handoff.json reviewer_opinions=%d; decision.md updated; %s"
          % (len(OPINIONS), time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
