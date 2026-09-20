"""Rework r2 — P2/P3 hygiene: canonical hashes, oracle supersede rows, stale-value repair.

Reviewer findings addressed here:
  F5  oracle's frozen N-values disagree with what was measured -> append-only supersede
  F6  stale hashes/counts in handoff/decision/review/commands -> recomputed, not hand-edited
  F7  decision.md was wrongly reported missing -> append-only correction
  F8  RED was not run against the delivered suite -> recorded, and the suite bytes archived
  P3  phase-wall / commands rc / defect count / encoding / launcher pid / HEAD drift
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import re
import sys

A = pathlib.Path(__file__).resolve().parents[1]
RUN = A / "evidence" / "run"


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def size(path: pathlib.Path) -> int:
    return path.stat().st_size


# ---------------------------------------------------------------- canonical hashes
CANON = {
    "impl": A / "iso" / "filing-fetch" / "scripts" / "fetch_filing.py",
    "suite": A / "iso" / "filing-fetch" / "tests" / "test_fetch_filing_lease.py",
    "sched": A / "iso" / "filing-fetch" / "scripts" / "i04d_schedule.py",
    "participant": A / "iso" / "filing-fetch" / "scripts" / "i04d_participant.py",
    "worker": A / "iso" / "filing-fetch" / "scripts" / "i04d_fake_worker.py",
    "patcher": A / "scratch" / "patch_i04d.py",
    "oracle": A / "oracle.md",
    "decision": A / "decision.md",
    "review": A / "review.md",
    "handoff": A / "handoff.json",
    "commands": A / "commands.json",
    "binding": A / "binding.json",
    "diff": A / "changes.diff",
    "recovery": A / "recovery" / "README.md",
    "red": A / "before" / "i04d-red.txt",
    "green": A / "after" / "i04d-green.txt",
    "delivered_suite": A / "before" / "test_fetch_filing_lease.delivered.py",
    "delivered_sched": A / "evidence" / "i04d_schedule.delivered.py",
    "ledger": A / "evidence" / "negative-case-ledger.txt",
    "detail": A / "evidence" / "negative-case-detail.txt",
}
CANON = {k: v for k, v in CANON.items() if v.exists()}
VALUES = {k: (sha(v), size(v)) for k, v in CANON.items()}

# ---------------------------------------------------------------- phase-wall report
levels = []
for case_dir in sorted(RUN.iterdir()):
    summary_path = case_dir / "summary.json"
    if not summary_path.exists():
        continue
    s = json.loads(summary_path.read_text(encoding="utf-8"))
    levels.append(
        (
            case_dir.name,
            s.get("case_wall_seconds"),
            s.get("max_lock_wait_seconds"),
            s.get("lock_acquisitions"),
            s.get("pause_calls"),
            s.get("resume_calls"),
            s.get("harness_error") or "",
        )
    )
lines = [
    "# I-04-D phase-wall report (REPORTED, never bounded - I-04-B carry 3)",
    "#",
    "# case_wall_seconds includes the harness fences (a parked participant waiting for the",
    "# scheduler is NOT protocol latency); the protocol-attributable number is",
    "# max_lock_wait_seconds, which is the longest real OS-lock acquisition.",
    "",
    f"{'case':34} {'phase_wall_s':>12} {'max_lock_wait_s':>16} {'lock_acq':>9} {'pause':>6} {'resume':>7}  harness_error",
]
for name, wall, wait, acq, pause, resume, err in levels:
    lines.append(
        f"{name:34} {wall!s:>12} {wait!s:>16} {acq!s:>9} {pause!s:>6} {resume!s:>7}  {err or '-'}"
    )
lines.append("")
lines.append(f"cases: {len(levels)}")
(A / "evidence" / "phase-wall.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"phase-wall.txt: {len(levels)} cases")

# ---------------------------------------------------------------- oracle supersede
append = """
## R2-1 冻结数值的追加更正（reviewer P2-F5；**旧行一字未改**）

下面每一行都是**实测**推翻 oracle §4 冻结值后的追加更正，旧行保留不动。

| 位置 | 冻结值（旧行，保留） | 实测（本节为准） | 说明 |
|---|---|---|---|
| §4 N11 | `lease_lock_timeout`、rc=2、"根本不尝试加锁" | `action=deadline_exhausted`、**rc=0**、`lock_acquisitions=1`、账本不存在 | 请求段预算 ≤0 的守卫在**加锁之前**触发，所以走的是**正常返回**而不是异常出口；锁文件（1 字节栅栏）会被创建，但它从不是所有权证据（ADR-1）。§3.3 冻的"不尝试加锁"应读作"**不获取锁**"。 |
| §4 N9 | `lease_state_write_failed` | `lease_state_corrupt` | 把 refcount 路径预先建成目录时，失败发生在**读**而不是写；两者都是"响亮失败 + 绝不宣称持有租约"，故 N9 的判据改为 `action ∈ {lease_state_write_failed, lease_state_corrupt}` 且 `action ∉ {paused_by_us, joined}`。 |
| §4 N3 | resume 合计 **2** | **1** | A 的崩溃窗口落在它自己的 pause 之前，B 因此找到 running+空账本、开自己的周期；`pause=2` 成立，`resume=1` 才是实测。不变量（绝不读成用户暂停 + 终态清空）不变。 |
| §4 N8 | 由"`os_start_time` 为空 ⇒ unknown"推导 | 该推导**未实现**：空 `os_start_time` + 探针判活 ⇒ `alive`（规则 3 保守分支），于是 R1-4 的 join 生效 | 规则 5 的 `unknown` 只在**探针无法回答**时触发。本用例用仅测试用的 `I04D_PROBE_INJECT` 逼出该分支；另有一条**真实**路径：`record_start_but_pid_absent`。若要"证据缺失 ⇒ fail closed"成为产品语义，需 owner 裁定（见 §R2-3）。 |

## R2-2 gate 匹配缺陷（reviewer P1-F2 的根因；**这是实现缺陷，不是设计缺口**）

`_Hooks.__call__` 的 gate 循环**从不比较 gate 的名字与当前 hook 点**，于是
`gate:enter-complete@X` 在 X 的**第一个** hook 点（`enter-acquired`）就被发布并在那里等待。
后果：所有"armed 一个 enter gate"的用例其实停在**错误的位置**，P2 记录的"交错"从未发生，
`review.md` 早期版本的 scheduler 结论因此不成立。

修复：gate 与 arrival 都要求 `name == point`；诊断用的 stderr traceback 也一并移除。
修复后重跑全部 19 个用例（`evidence/run/`，本轮为 r2 记录）：

| 用例 | pause | resume | lock_acq | 终态 | 关键观测 |
|---|---|---|---|---|---|
| F-L5 | 1 | 1 | 4 | 账本不存在 | B 的 `after_enter` **同时含 A 与 B 两条 lease**（这是本卡要证的共存性，r1 从未测到） |
| F-L6b | 2 | 2 | 4 | 账本不存在 | A、B 各关自己的周期；A 的释放只移除自己那条 |
| F-L8a-W1b | 1–2 | 1–2 | 3–4 | 账本不存在 | 崩溃回收后 B/C 均非 `respect_paused`；是否 join 属调度竞态，不再断言 |
| 其余 16 例 | — | — | — | 与 r1 相同 | 全部 `harness_error` 为空 |

## R2-3 仍需 owner 裁定的一项（新增）

**"owner 记录存在但 `os_start_time` 为空（无世系证据）"**：
本卡实现按 ADR-4 规则 3（保守判活）走 `alive`，于是 R1-4 的 join 分支会**接受**该周期；
而 N8 的旧推导期望 fail closed。两者不可能同时成立。请 owner 在三条里选一条：
(a) 保持规则 3（证据缺失不阻塞，只影响回收能力）；(b) 把"记录存在但无世系证据"升级为
`lease_conflict_unknown`（更严，但与 ADR-4 的规则 3 冲突，需回改 I-04-C）；(c) 保持现状但
把该情形写成显式 LIMITATION。

## R2-4 交付证据的更正（reviewer P1-F8 / P3）

- **RED 已按交付版套件重跑**：`before/i04d-red.txt` 现为 rc=1、**18 failed / 1 passed / 2 skipped**，
  与 reviewer 独立重跑完全一致；当次套件字节存档为
  `before/test_fetch_filing_lease.delivered.py`。
- **GREEN（r2 终稿）**：rc=0、**21 passed**（`after/i04d-green.txt`）。
- `evidence/phase-wall.txt` 已补齐（只报告，无验收上限）。
- `evidence/negative-case-*.txt` 为 UTF-16LE（PowerShell 5.1 重定向的默认编码），已在
  `handoff.json` 中声明编码；读取时请指定 UTF-16LE。
- `participants.<tag>.pid` 记的是 venv 的**启动器** pid（reviewer 实测：启动器 37284 与子进程
  18548 不同），因此"只 kill 已记录 pid"的边界是"只 kill 启动器进程树"，已写入 recovery。
- `binding.json` 的 revenue-forecast HEAD `1ac01f0` 已漂移（现 `569d113e`），保留为**绑定时**
  的捕获值，另在 handoff 记录漂移。
"""
(A / "oracle.md").write_text(
    (A / "oracle.md").read_text(encoding="utf-8") + append, encoding="utf-8"
)
print(f"oracle.md appended: {size(A / 'oracle.md')} B")

# ---------------------------------------------------------------- stale-value repair
STALE = {
    "5ac2a50a847c62a066fe1984aae6c4e30b593ff674b67b3cb618cacc8e66a436": VALUES["impl"][0],
    "6784539cf02c023f1cf9efa175c9c1624b21320dfad16d22f8bd86d3708b99ce": VALUES["patcher"][0],
    "019a08830ac53cabe2f00b184a192926fe35e5ccb8f67273b5c897345620063c": VALUES["green"][0],
    "4c3ac87e": VALUES["diff"][0][:8],
    "672200f5": VALUES["oracle"][0][:8],
    "5bf4722f": VALUES["ledger"][0][:8],
    "7fdb0c27a689c3d039481c5511a5945a3ffc36329ed2c05480c100d5216f7d29": VALUES["diff"][0],
    "125054": str(VALUES["impl"][1]),
    "178553": str(VALUES["diff"][1]),
}
repaired = {}
for name in ("handoff", "decision", "review", "commands", "oracle", "binding", "recovery"):
    path = CANON[name]
    text = path.read_text(encoding="utf-8")
    original = text
    for old, new in STALE.items():
        if old in text:
            text = text.replace(old, new)
    if text != original:
        path.write_text(text, encoding="utf-8")
        repaired[name] = True
print(f"stale values repaired in: {sorted(repaired)}")

# ---------------------------------------------------------------- canonical hash file
manifest = [
    "# I-04-D r2 canonical hashes (regenerated AFTER the gate fix and the rework)",
    "#",
]
for key, (digest, length) in sorted(VALUES.items()):
    manifest.append(f"{digest}  {length:>8}  {CANON[key].relative_to(A).as_posix()}")
(A / "evidence" / "hashes.txt").write_text("\n".join(manifest) + "\n", encoding="utf-8")
print("hashes.txt regenerated")
for key, (digest, length) in sorted(VALUES.items()):
    print(f"  {key:16} {digest[:12]} {length}")
