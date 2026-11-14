"""Record the content-vs-handoff commit distinction and the review outcome."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> int:
    handoff_json = ROOT / "handoff.json"
    payload = json.loads(handoff_json.read_text(encoding="utf-8"))
    ordered = {}
    for key, value in payload.items():
        ordered[key] = value
        if key == "release_tag_or_commit_for_dashboard":
            ordered["handoff_commit_note"] = (
                "the handoff record itself is updated by follow-up commits on this branch; the commit "
                "pinned above is the self-contained content commit where the input, the job artifacts "
                "and every evidence file resolve. The authoritative handoff is the branch tip."
            )
    payload = ordered
    payload["review"]["round3"] = {
        "verdict": "PASS-with-findings",
        "open_p1": 0,
        "open_p2": 0,
        "open_p3": 4,
        "note": (
            "delta re-check of the content commit: P1-1/P1-2/P3-4 closed; one P2 (stale input hash in "
            "task_plan.md) fixed after the report; remaining P3s are the disclosed limitations "
            "(empty publication audit artifact, catalog admission NOT_RUN, Alibaba NOT_RUN with route 4 "
            "not replayed in that round, management-target ledger NOT_RUN)."
        ),
    }
    handoff_json.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )

    handoff_md = ROOT / "handoff.md"
    text = handoff_md.read_text(encoding="utf-8")
    anchor = "- `release_tag_or_commit_for_dashboard` = 同上（40 位、`git rev-parse` 可解析）"
    replacement = (
        anchor
        + "\n- 说明：交接记录本身由本分支后续 commit 维护；上面 pin 的是**自包含内容 commit**"
        "（输入/作业产物/证据全部可在该 commit 解析）。权威 handoff = 本分支 tip。"
    )
    text = text.replace(anchor, replacement)
    handoff_md.write_text(text, encoding="utf-8", newline="\n")
    print(json.dumps({"round3": payload["review"]["round3"]["open_p1"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
