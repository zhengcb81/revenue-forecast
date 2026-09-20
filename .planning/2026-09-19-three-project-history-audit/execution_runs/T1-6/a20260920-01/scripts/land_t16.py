#!/usr/bin/env python3
"""T1-6 landing — add back the missing cross-year case to M24 cases.json.

OWNER_DECISIONS.md §13 T1-6 (owner-ruled, TIER-1): "select (c): add back one
cross-year case with a DIFFERENT input to `cases.json` ... no need to touch the
card prose". Rationale given by the owner: it does not modify the frozen prose,
does not consume the one-off controlled re-freeze budget, and restores the
consistency between the case set and the card text.

What is actually missing, measured (see ../t16_reachability_probe.json):
  * the frozen card's own `negative_patch` IS what the live `CONT-BREAK` uses
    (opening[200,251] / closing[250,251]) -> that patch reaches the FY2028
    CROSS-YEAR anchoring guard, message `opening_arr continuity failed: FY2028`
  * the reviewer's prescribed second case (opening[200,250] / closing[251,251])
    reaches the FY2027 OWN-BALANCE guard, message
    `opening_arr stock-flow balance failed: FY2027`
So the missing half is the OWN-BALANCE case, and its input genuinely differs.

EDIT SHAPE — this is a PURE APPEND to the `cases` array:
  * the pre-existing 11 cases are re-serialised byte-for-byte identically
    (verified below by re-parsing the pre-image and comparing the rendered
    form of each case against the pre-image's own rendering)
  * exactly one new case object is added at the end of `cases`
  * `required_message_ids` gains the new id (this is an in-place FIELD edit and
    is proven separately by the prefix/suffix/delta triangle below)
Nothing else is touched: no expectation, no tolerance, no frozen prose.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
RUN = HERE.parent                      # .../execution_runs/T1-6/a20260920-01
EXEC_RUNS = RUN.parent.parent          # .../execution_runs
M24 = EXEC_RUNS / "M24" / "a20260919-01"
LIVE = M24 / "evidence" / "M24" / "cases.json"
ISO = RUN / "iso"
PRE_COPY = ISO / "cases_pre.json"

NEW_CASE_ID = "CONT-BREAK-OWNBALANCE"

PRE_BYTES = 6185
PRE_SHA = "263b78b3e27d687f074bc20db109ff50e5915681c571224a564001863cf4750f"

NEW_CASE = {
    "id": NEW_CASE_ID,
    "kind": "set_driver_multi",
    "expected": "ModelRegistryError",
    "base_input": "continuity_positive",
    "why": (
        "T1-6 (OWNER_DECISIONS.md §13): the card's own negative_patch makes BOTH "
        "years balance and breaks only the CROSS-YEAR anchor, so it exercises "
        "the FY2028 anchoring guard. This case is its complement and uses a "
        "DIFFERENT input: FY2027 itself fails its own bridge by 1, which "
        "exercises the FY2027 OWN-BALANCE guard. Reaches the guard the reviewer "
        "recorded as reachable in oracle.json hand_notes.continuity_negative_note."
    ),
    "driver": None,
    "expect_message_contains": "stock-flow balance failed: FY2027",
    "expect_message_basis": (
        "the type-only assertion is too weak for this case: a length/lookup "
        "guard could raise the same exception class for the wrong reason, so the "
        "refusal MESSAGE is frozen too and the runner fails the case if the "
        "message does not contain this substring. The substring is deliberately "
        "the one named by OWNER_DECISIONS.md §13 T1-6; the measured message "
        "carries the `opening_arr ` prefix BEFORE it, so a substring test holds."
    ),
    "value": {
        "opening_arr": [200, 250],
        "closing_arr": [251, 251],
    },
}


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def render_cases_array(cases: list) -> str:
    """Render the `cases` array exactly as json.dumps(indent=1) would, so the
    pre-existing entries can be compared rendered-vs-rendered."""
    return json.dumps(cases, indent=1, ensure_ascii=False)


def main() -> int:
    report: dict = {"card": "T1-6", "attempt": "a20260920-01"}

    # ---- 0. pre-image anchor ----
    pre = LIVE.read_bytes()
    report["pre_image"] = {
        "path": str(LIVE.relative_to(EXEC_RUNS)),
        "bytes": len(pre),
        "sha256": sha(pre),
        "matches_expected_anchor": len(pre) == PRE_BYTES and sha(pre) == PRE_SHA,
    }
    if not report["pre_image"]["matches_expected_anchor"]:
        print(json.dumps(report, indent=1, ensure_ascii=False))
        raise SystemExit("PRE-IMAGE ANCHOR DRIFT — aborting, nothing written")

    d = json.loads(pre.decode("utf-8"))
    pre_ids = [c["id"] for c in d["cases"]]
    report["pre_case_ids"] = pre_ids
    if NEW_CASE_ID in pre_ids:
        raise SystemExit(f"{NEW_CASE_ID} already present — nothing to do")

    # ---- 1. prove the pre-existing cases render identically (pure append) ----
    # Re-render the pre-image's OWN cases array and confirm it round-trips, so we
    # know the renderer is faithful before we use it to build the post image.
    pre_render = render_cases_array(d["cases"])
    d_reparsed = json.loads(pre_render)
    report["renderer_is_faithful"] = d_reparsed == d["cases"]

    # ---- 2. build the post image by APPENDING one case ----
    post = json.loads(pre.decode("utf-8"))  # fresh copy
    post["cases"].append(NEW_CASE)
    post["required_message_ids"] = list(post["required_message_ids"]) + [NEW_CASE_ID]

    # ---- 3. prove the 11 pre-existing cases are byte-identical when rendered ----
    prefix_renders_equal = (
        render_cases_array(post["cases"][:len(pre_ids)]) == pre_render
    )
    report["existing_cases_rendered_identically"] = prefix_renders_equal

    out_bytes = (json.dumps(post, indent=1, ensure_ascii=False) + "\n").encode("utf-8")
    report["post_image"] = {"bytes": len(out_bytes), "sha256": sha(out_bytes)}
    report["delta_bytes"] = len(out_bytes) - len(pre)

    # ---- 4. prefix / suffix triangle on the raw bytes ----
    # The change is an in-place edit inside `required_message_ids` PLUS an append
    # at the end of `cases`. So neither a pure-prefix nor a pure-suffix argument
    # covers it; we instead prove the STRUCTURAL claim directly:
    #   * every pre-existing case object is present and unmodified
    #   * exactly one case id is new
    post_d = json.loads(out_bytes.decode("utf-8"))
    post_ids = [c["id"] for c in post_d["cases"]]
    report["post_case_ids"] = post_ids
    report["added_case_ids"] = [i for i in post_ids if i not in pre_ids]
    report["removed_case_ids"] = [i for i in pre_ids if i not in post_ids]
    report["pre_existing_cases_unmodified"] = all(
        post_d["cases"][i] == d["cases"][i] for i in range(len(pre_ids))
    )

    # field-level diff, excluding the two intended targets
    diffs = []
    for k in set(d) | set(post_d):
        if d.get(k) != post_d.get(k):
            diffs.append(k)
    report["changed_top_level_fields"] = sorted(diffs)
    report["changed_fields_are_exactly_intended"] = sorted(diffs) == [
        "cases", "required_message_ids",
    ]
    report["required_message_ids_before"] = d["required_message_ids"]
    report["required_message_ids_after"] = post_d["required_message_ids"]

    # ---- 5. write only into the attempt-local iso tree ----
    ISO.mkdir(parents=True, exist_ok=True)
    if not PRE_COPY.exists():
        PRE_COPY.write_bytes(pre)
    out = ISO / "cases_t16.json"
    out.write_bytes(out_bytes)
    report["wrote"] = str(out.relative_to(RUN))
    report["live_frozen_file_not_written"] = True

    (RUN / "t16_landing_report.json").write_text(
        json.dumps(report, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
