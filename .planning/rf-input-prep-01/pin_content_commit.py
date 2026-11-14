"""Point the handoff at the commit that now holds the complete evidence set."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WORKTREE = ROOT.parents[1]
SHA = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(WORKTREE), text=True).strip()
PREVIOUS = "1009258075f835c5d5f7d4cff563cb8fc722c740"


def main() -> int:
    if len(SHA) != 40 or SHA == PREVIOUS:
        raise SystemExit("HEAD must be the new content commit")
    path = ROOT / "handoff.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["head_commit"] = SHA
    payload["release_tag_or_commit_for_dashboard"] = SHA
    payload["inputs"][0]["superseded_reason"] = payload["inputs"][0].get("superseded_reason", "")
    note = payload.get("handoff_commit_note", "")
    payload["handoff_commit_note"] = (
        note.replace(PREVIOUS, SHA)
        if note
        else "the handoff record itself is updated by follow-up commits on this branch"
    )
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

    handoff_md = ROOT / "handoff.md"
    text = handoff_md.read_text(encoding="utf-8")
    text = text.replace(
        f"- **内容交付 commit**：`{PREVIOUS}`（输入 + 作业 + 证据全部在该 commit 内）",
        f"- **内容交付 commit**：`{SHA}`（输入 + 作业 + 快照 + 诊断 + 六路线证据全部在该 commit 内）",
    )
    handoff_md.write_text(text, encoding="utf-8", newline="\n")
    print(json.dumps({"pinned": SHA}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
