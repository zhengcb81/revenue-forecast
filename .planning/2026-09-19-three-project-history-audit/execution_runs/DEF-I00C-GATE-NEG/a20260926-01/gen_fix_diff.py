"""Generate fix_diff.md: unified diffs pre->post for the three modified files,
with byte-exact pre/post image sha256 records."""

import difflib
import hashlib
import pathlib

HERE = pathlib.Path(__file__).resolve().parent

PAIRS = [
    (
        "assurance/unified_completion/uc/scenarios.py",
        "scenarios.py",
        "524fc1e6d6ba6a841e36f339c1aaf4e14bd7f26ec3ed6f04c83669d082544f29",
    ),
    (
        "assurance/unified_completion/uc/closure.py",
        "closure.py",
        "952abfe0ea39ced076e3b83090de79e90ee95e5a39d94d8711377f65a446300e",
    ),
    (
        "assurance/unified_completion/tests/test_scenarios.py",
        "test_scenarios.py",
        "14f3910e9817f4834ec539326fe118b69e4c652a9a812dae6b114bd292b67597",
    ),
]

out = [
    "# 修复 diff — DEF-I00C-GATE-NEG",
    "",
    "前像来源：git HEAD blob（字节级提取）。两个 uc 文件的前像 sha256 与 I-17-B",
    "证据件 `six_negatives_result.json.combination` 逐一吻合；后像 = 修复后生产",
    "文件（与本目录 `post_image/` 备份 sha 一致，终态已核实）。",
    "",
]
for repo_path, local, pre_sha in PAIRS:
    pre = (HERE / "pre_image" / local).read_text(encoding="utf-8").splitlines(keepends=True)
    post = (HERE / "post_image" / local).read_text(encoding="utf-8").splitlines(keepends=True)
    post_sha = hashlib.sha256((HERE / "post_image" / local).read_bytes()).hexdigest()
    diff = list(
        difflib.unified_diff(
            pre,
            post,
            fromfile="a/" + repo_path,
            tofile="b/" + repo_path,
            lineterm="",
        )
    )
    add = sum(1 for l in diff if l.startswith("+") and not l.startswith("+++"))
    rem = sum(1 for l in diff if l.startswith("-") and not l.startswith("---"))
    out += [
        f"## {repo_path}",
        "",
        f"- 前像 sha256: `{pre_sha}`",
        f"- 后像 sha256: `{post_sha}`",
        f"- 变更规模: +{add} / -{rem} 行",
        "",
        "```diff",
    ] + diff + ["```", ""]

(HERE / "fix_diff.md").write_text("\n".join(out), encoding="utf-8")
print("fix_diff.md written,", len(out), "lines")
