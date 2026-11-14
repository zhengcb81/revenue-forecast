"""Pin the content commit into the handoff files."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WORKTREE = ROOT.parents[1]
SHA = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(WORKTREE), text=True).strip()


def main() -> int:
    if len(SHA) != 40:
        raise SystemExit("HEAD is not a 40-char commit")
    handoff_json = ROOT / "handoff.json"
    payload = json.loads(handoff_json.read_text(encoding="utf-8"))
    payload["head_commit"] = SHA
    payload["release_tag_or_commit_for_dashboard"] = SHA
    handoff_json.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    handoff_md = ROOT / "handoff.md"
    text = handoff_md.read_text(encoding="utf-8")
    text = text.replace("CONTENT_COMMIT_PLACEHOLDER", SHA)
    handoff_md.write_text(text, encoding="utf-8", newline="\n")
    print(json.dumps({"pinned": SHA}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
