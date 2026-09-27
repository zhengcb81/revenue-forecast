# -*- coding: utf-8 -*-
"""R5 全路径还原修复版（P2-2 持久化）。

原缺陷：I-16-A/_recovery_drill.py L42 `dst = out_root/repo/Path(source_path).name`
        丢弃父目录 ⇒ 109 行 → 104 目的地、5 件同名覆盖（__init__.py×5、README.md×2 等 sha 各异）。
本实现：按 repo 根映射剥前缀得**完整相对路径**，写入后**逐目的地复读比对**。
验收：rows=109、distinct=109、collisions=0、pre/post mismatch=0、on_disk=109。
"""
import json
import sys
import hashlib
import os
import shutil
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

SRC = r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\I-16-A\a20260926-01"
DST = os.path.dirname(os.path.abspath(__file__))
ROOTS = {
    "RF": r"C:\Users\郑曾波\Projects\revenue-forecast",
    "CW": r"C:\Users\郑曾波\Projects\company-wiki",
    "DAYU": r"C:\Users\郑曾波\Projects\dayu-agent\dayu-agent",
}

man = json.load(open(os.path.join(SRC, "snapshot_manifest.json"), encoding="utf-8-sig"))
files = man["files"]
out = Path(DST) / "drill_restore_fullpath"
if out.exists():
    shutil.rmtree(out)

seen = set()
collisions = []
pre_mm = []
for row in files:
    repo = row["repo"]
    root = Path(ROOTS[repo])
    sp = Path(row["source_path"])
    try:
        rel = sp.relative_to(root)
    except ValueError:
        rel = Path(*sp.parts[1:]) if sp.is_absolute() else sp
    dst = out / repo / rel
    key = str(dst).lower()
    if key in seen:
        collisions.append(str(dst))
    seen.add(key)
    dst.parent.mkdir(parents=True, exist_ok=True)
    data = (Path(SRC) / row["snapshot_path"]).read_bytes()
    dst.write_bytes(data)
    if hashlib.sha256(data).hexdigest() != row["source_sha256"]:
        pre_mm.append(row["source_path"])

post = []
for row in files:
    repo = row["repo"]
    root = Path(ROOTS[repo])
    sp = Path(row["source_path"])
    try:
        rel = sp.relative_to(root)
    except ValueError:
        rel = Path(*sp.parts[1:]) if sp.is_absolute() else sp
    d2 = (out / repo / rel).read_bytes()
    if hashlib.sha256(d2).hexdigest() != row["source_sha256"]:
        post.append(row["source_path"])

on_disk = len([f for f in out.rglob("*") if f.is_file()])
res = {
    "rows": len(files),
    "distinct_destinations": len(seen),
    "collisions": collisions,
    "pre_write_mismatch": pre_mm,
    "post_write_recheck_mismatch": post,
    "files_on_disk": on_disk,
    "ok": (not pre_mm) and (not post) and (not collisions) and on_disk == len(files),
    "claim": "snapshot 层按完整相对路径逐文件字节相等（修复 basename 覆盖缺陷后）",
    "fix_note": "P2-2 persisted; supersedes I-16-A/_recovery_drill.py L42 basename landing",
}
with open(os.path.join(DST, "r5_fullpath_result.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
print(f"rows={len(files)} distinct={len(seen)} collisions={len(collisions)} "
      f"pre_mm={len(pre_mm)} post_mm={len(post)} on_disk={on_disk}")
print("R5_RESULT:", "GREEN" if res["ok"] else "RED")
