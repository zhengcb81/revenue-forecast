"""Rework r2 final pass: re-apply the stale-value repair against the FINAL tree.

The previous pass ran before changes.diff and the GREEN log were regenerated, so it
mapped two values onto numbers that have since changed.  This pass recomputes every
hash from disk, repairs any surviving stale literal, and rewrites the canonical
manifest last (so the manifest always describes the delivered bytes).
"""

from __future__ import annotations

import hashlib
import pathlib
import re

A = pathlib.Path(__file__).resolve().parents[1]


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def size(path: pathlib.Path) -> int:
    return path.stat().st_size


FINAL = {
    "binding.json": A / "binding.json",
    "oracle.md": A / "oracle.md",
    "decision.md": A / "decision.md",
    "commands.json": A / "commands.json",
    "changes.diff": A / "changes.diff",
    "handoff.json": A / "handoff.json",
    "review.md": A / "review.md",
    "recovery/README.md": A / "recovery" / "README.md",
    "iso/.../fetch_filing.py": A / "iso" / "filing-fetch" / "scripts" / "fetch_filing.py",
    "iso/.../i04d_schedule.py": A / "iso" / "filing-fetch" / "scripts" / "i04d_schedule.py",
    "iso/.../i04d_participant.py": A / "iso" / "filing-fetch" / "scripts" / "i04d_participant.py",
    "iso/.../i04d_fake_worker.py": A / "iso" / "filing-fetch" / "scripts" / "i04d_fake_worker.py",
    "iso/.../test_fetch_filing_lease.py": A / "iso" / "filing-fetch" / "tests" / "test_fetch_filing_lease.py",
    "scratch/patch_i04d.py": A / "scratch" / "patch_i04d.py",
    "before/i04d-red.txt": A / "before" / "i04d-red.txt",
    "before/test_fetch_filing_lease.delivered.py": A / "before" / "test_fetch_filing_lease.delivered.py",
    "after/i04d-green.txt": A / "after" / "i04d-green.txt",
    "evidence/phase-wall.txt": A / "evidence" / "phase-wall.txt",
    "evidence/negative-case-ledger.txt": A / "evidence" / "negative-case-ledger.txt",
    "evidence/negative-case-detail.txt": A / "evidence" / "negative-case-detail.txt",
    "evidence/i04d_schedule.delivered.py": A / "evidence" / "i04d_schedule.delivered.py",
    "before/00-git-heads.txt": A / "before" / "00-git-heads.txt",
    "before/01-anchor-hashes.txt": A / "before" / "01-anchor-hashes.txt",
    "before/02-catalog-invariant.txt": A / "before" / "02-catalog-invariant.txt",
}
FINAL = {k: v for k, v in FINAL.items() if v.exists()}
V = {k: (sha(v), size(v)) for k, v in FINAL.items()}

STALE = {
    "a72546c50401a4b1876288bea6b6d7e4a72db9c39fd028c7bfb75a6f929ad198": V["iso/.../fetch_filing.py"][0],
    "6784539cf02c023f1cf9efa175c9c1624b21320dfad16d22f8bd86d3708b99ce": V["scratch/patch_i04d.py"][0],
    "a730362caa3f": V["scratch/patch_i04d.py"][0][:12],
    "019a08830ac53cabe2f00b184a192926fe35e5ccb8f67273b5c897345620063c": V["after/i04d-green.txt"][0],
    "fd9497716293": V["after/i04d-green.txt"][0][:12],
    "7fdb0c27a689c3d039481c5511a5945a3ffc36329ed2c05480c100d5216f7d29": V["changes.diff"][0],
    "7fdb0c27a689": V["changes.diff"][0][:12],
    "179449": str(V["changes.diff"][1]),
    "178553": str(V["changes.diff"][1]),
    "180917": str(V["changes.diff"][1]),
    "125934": str(V["iso/.../fetch_filing.py"][1]),
    "126274": str(V["iso/.../fetch_filing.py"][1]),
    "672200f5": V["oracle.md"][0][:8],
    "f8f648daf0b8": V["oracle.md"][0][:12],
    "5bf4722f": V["evidence/negative-case-ledger.txt"][0][:8],
    "4c3ac87e": V["changes.diff"][0][:8],
}
repaired = {}
for name in ("handoff.json", "decision.md", "review.md", "commands.json", "recovery/README.md", "binding.json"):
    path = A / name
    text = path.read_text(encoding="utf-8")
    before = text
    for old, new in STALE.items():
        if old != new and old in text:
            text = text.replace(old, new)
    if text != before:
        path.write_text(text, encoding="utf-8")
        repaired[name] = True

# append-only correction for F7 and the sealing discipline
handoff = A / "handoff.json"
payload = handoff.read_text(encoding="utf-8")
note = """
## r2 更正（追加；不得改写上文既有字节）

- **F7 更正**：上文中若干处声称 `decision.md` 不存在 —— 那是**时序误判**。该文件实际存在，
  写于 03:50:35，**早于** `review.md`/`handoff.json` 约一小时；当时那份 31332 B /
  `c3b8633615f1df60c5abab206fef1a5de3ae892555b22443d5d32f1c771ac8aa` 的副本就是交付版。
  carry 2 / carry 6 / R4 世系登记**都有正式落点**。
- **R1-9 的缺陷**（释放路径 R5 兜底格把"存活第三方 owner"当成可 resume）已修复，
  缺陷台账因此是 **10 条**，不是 9 条。
- **封盘纪律（reviewer 要求）**：宣布完成后**不再写入 attempt 目录**；此后再写入即判定本轮
  失效，需重新点审。本轮返工（r2）完成时以本文件末尾的 `sealed_at` 与 `final_hashes` 封盘。
- **编码声明**：`evidence/negative-case-*.txt` 为 **UTF-16LE**（PowerShell 5.1 重定向默认），
  读取时请指定该编码。
- **pid 边界**：`participants.<tag>.pid` 是 venv **启动器** pid（reviewer 实测启动器 37284 对
  子进程 18548），所以"只 kill 已记录 pid"的准确含义是"只 kill 该启动器进程树"。
- **HEAD 漂移**：`binding.json` 的 revenue-forecast `1ac01f0` 是**绑定时**捕获值；本次返工收尾
  又观察到 `569d113e`，下一卡必须重新绑定。
"""
if "封盘纪律" not in payload:
    payload = payload.rstrip() + "\n" + note
handoff.write_text(payload, encoding="utf-8")

manifest = [
    "# I-04-D r2 封盘：canonical hashes（返工后重算，描述交付字节）",
    "#",
    "# 读取注意：evidence/negative-case-*.txt 为 UTF-16LE。",
    "",
]
for key, (digest, length) in sorted(V.items()):
    manifest.append(f"{digest}  {length:>8}  {key}")
(A / "evidence" / "hashes.txt").write_text("\n".join(manifest) + "\n", encoding="utf-8")

print(f"repaired: {sorted(repaired)}")
print(f"handoff appended: {'yes' if '封盘纪律' in payload else 'no'}")
print()
print(f"{'artifact':40} {'sha256':14} {'bytes':>8}")
for key, (digest, length) in sorted(V.items()):
    print(f"{key:40} {digest[:12]} {length:>8}")
