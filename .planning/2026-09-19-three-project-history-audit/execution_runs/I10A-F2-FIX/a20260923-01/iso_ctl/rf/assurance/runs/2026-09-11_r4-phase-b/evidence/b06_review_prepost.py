"""Compare the pre-B06 / post-B06 envelope dumps (question f).

pre  = resolver.py from 5138546^   (pre-B06)
post = resolver.py from 5138546    (B06)   run twice for a run-noise control
"""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).parent


def load(name: str) -> dict:
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def flat(prefix: str, value) -> dict:
    if isinstance(value, dict):
        out = {}
        for key, item in value.items():
            out.update(flat(f"{prefix}.{key}", item))
        return out
    return {prefix: value}


pre, post, post2 = (
    load("b06_review_pre.json"),
    load("b06_review_post.json"),
    load("b06_review_post2.json"),
)


def diff(left: dict, right: dict) -> dict:
    out = {}
    for case in ("plain", "conflict"):
        for part in ("resolution", "envelope"):
            a, b = flat(f"{case}.{part}", left[case][part]), flat(f"{case}.{part}", right[case][part])
            keys = sorted(set(a) | set(b))
            changed = {k: [a.get(k, "<absent>"), b.get(k, "<absent>")] for k in keys if a.get(k, "<absent>") != b.get(k, "<absent>")}
            out[f"{case}.{part}"] = changed
    return out


control = diff(post, post2)
b06 = diff(pre, post)
report = {
    "control_post_vs_post2_run_noise": control,
    "b06_pre_vs_post": b06,
    "b06_changes_are_only_qualification": all(
        all(key.endswith("qualification") for key in changed)
        for changed in b06.values()
    ),
    "envelope_keys_pre": sorted(json.loads(json.dumps(pre["plain"]["envelope"])).keys()),
    "envelope_keys_post": sorted(json.loads(json.dumps(post["plain"]["envelope"])).keys()),
}
print(json.dumps(report, ensure_ascii=False, indent=2, default=str)[:6000])
(HERE / "b06_review_prepost.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
)
