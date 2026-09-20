"""Insert the independent reviewer's opinions on the open questions into card_facts.json.

The relayed review instruction requires the reviewer's independent positions to be recorded in the
hand-off artefacts WITHOUT the implementer adopting them as decisions. This script appends a
`reviewer_opinions` list to each card's facts file (UTF-8, no BOM), leaving everything else intact.
"""

from __future__ import annotations

import json
import os
import sys

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
    "reviewer's remit. Both sides were measured (see recovery/probes/signed_driver_probe.json and "
    "the signed-driver observation).",
    "OQ-04 (this card's own fourth question, card-specific): the reviewer separately closed the "
    "domain-edge part of it - both endpoints are inclusive with zero gap (1.0 accepted, 1.0000001 "
    "refused) - and, for the M13 invalid-observation variant, judged the 'do not repack the frozen "
    "fixture, open a labelled probe instead' handling ACCEPTABLE. This card's own text is in "
    "handoff.json; the implementer does not adopt the reviewer's opinion as its own decision.",
    "OQ-05 (pytest / historical suite): the reviewer AGREES that this card does not need it: the "
    "batch's evidence chain is a single standard-library-only runner plus frozen JSON, and the "
    "historical 97 tests / 216 subtests are not part of it. If the owner requires a re-run it "
    "should be registered as a SEPARATE regression gate, not folded into the formula sign-off "
    "conditions.",
]


def main() -> int:
    for path in sys.argv[1:]:
        with open(path, encoding="utf-8-sig") as handle:
            doc = json.load(handle)
        doc["reviewer_opinions"] = OPINIONS
        doc["reviewer_opinions_note"] = (
            "recorded from the relayed independent review of 2026-09-20; these are the REVIEWER's "
            "positions and are NOT adopted as decisions by the implementer")
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(doc, handle, ensure_ascii=False, indent=1)
            handle.write("\n")
        with open(path, "rb") as handle:
            bom = handle.read(3) == b"\xef\xbb\xbf"
        print("%s: reviewer_opinions=%d bom=%s" % (os.path.basename(os.path.dirname(path)),
                                                   len(OPINIONS), bom))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
