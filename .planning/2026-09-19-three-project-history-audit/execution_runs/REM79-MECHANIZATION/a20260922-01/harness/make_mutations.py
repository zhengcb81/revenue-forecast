#!/usr/bin/env python3
"""make_mutations.py — materialize the three pre-declared mutations.

Every operation below was declared in the FROZEN oracle (oracle.md §7 /
oracle_table.json "mutations", red sets recorded BEFORE this script existed).
Files are written only inside this attempt.
"""
import hashlib
import json
import sys
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parent.parent
OUT = ATTEMPT / "mutations"


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def read_lines(rel: str):
    text = (ATTEMPT / rel).read_text(encoding="utf-8")
    return text.split("\n")


def write_lines(rel: str, lines):
    p = ATTEMPT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(("\n".join(lines)).encode("utf-8"))
    return sha(p.read_bytes())


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema": "rem79-mutation-manifest/1",
        "red_sets_declared_in": "oracle_table.json (frozen before these files existed)",
        "mutations": {},
    }

    # ---- MUT-A: strip the domain parenthetical from payload line 4 (idx 3) ---
    src = "corpus/neg_domain_lines.md"
    lines = read_lines(src)
    payload = lines[3]
    start = payload.index("（**域：")
    end = payload.index("落于本行**）") + len("落于本行**）")
    mutated = payload[:start] + payload[end:]
    assert "落于本行" not in mutated, "domain parenthetical not fully stripped"
    assert "每一个" in mutated, "marker lost while stripping"
    lines[3] = mutated
    digest = write_lines("mutations/a_strip_domain.md", lines)
    manifest["mutations"]["a_strip_domain"] = {
        "source": src,
        "source_sha256": sha((ATTEMPT / src).read_bytes()),
        "target": "mutations/a_strip_domain.md",
        "target_sha256": digest,
        "operation": "delete substring （**域：…落于本行**） from payload line 4 only",
        "expect_flagged_lines": [4],
    }

    # ---- MUT-B: add a domain qualifier to payload line 4 (idx 3) ------------
    src = "corpus/pos_synth_frev_r406.md"
    lines = read_lines(src)
    lines[3] = lines[3] + " (domain: 19-probe measurement set)"
    digest = write_lines("mutations/b_add_domain.md", lines)
    manifest["mutations"]["b_add_domain"] = {
        "source": src,
        "source_sha256": sha((ATTEMPT / src).read_bytes()),
        "target": "mutations/b_add_domain.md",
        "target_sha256": digest,
        "operation": "append ' (domain: 19-probe measurement set)' to payload line 4 only",
        "expect_flagged_lines": [],
    }

    # ---- MUT-C: off-by-one: insert one empty line at the top ---------------
    src = "corpus/pos_synth_frev_r502.md"
    original = (ATTEMPT / src).read_text(encoding="utf-8")
    mutated = "\n" + original
    p = ATTEMPT / "mutations/c_offbyone.md"
    p.write_bytes(mutated.encode("utf-8"))
    digest = sha(p.read_bytes())
    manifest["mutations"]["c_offbyone"] = {
        "source": src,
        "source_sha256": sha(original.encode("utf-8")),
        "target": "mutations/c_offbyone.md",
        "target_sha256": digest,
        "operation": "insert one empty line at the top (payload moves line 4 -> line 5)",
        "oracle_baseline_payload_line": 4,
        "expect_reported_payload_line": 5,
    }

    (OUT / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("mutations written:")
    for name, meta in manifest["mutations"].items():
        print(f"  {name}: {meta['target']} sha256={meta['target_sha256'][:16]}…")
    return 0


if __name__ == "__main__":
    sys.exit(main())
