# I-14-E-TESTSIDE review.md — 独立验收（由独立 reviewer 填写；实现者**未**自签）

本文件由实现者留出结构，**结论由 reviewer 写**。实现者身份：I-14-E-TESTSIDE implementer agent。
`handoff.json.status = review_pending`、`implementer_signed = false`。

## 0. reviewer 应先读什么（不看实现者的通过摘要）

1. `oracle.md`（冻结 2026-09-25T20:42:26Z，`before/freeze_instant.json` 记其 sha256
   `4c15948e…8f658`）+ `oracle-addendum-A.md`（basetemp 落点）+
   `oracle-addendum-C.md`（**会话环境阻断，决定本卡能否给绿**）。
   —— 先确认判据是**运行前**写死的：`oracle.md` 的 mtime 必须早于 `red/band-red.json` 等三臂产物。
2. `before/hashed_before.json` → `after/hashed_after.json` → `before/final_hashes.json`
   / `after/final_hashes.json` / `after/boundary_check.json` —— 逐字节不变性。
3. `after/changes.diff` + `after/changes.manifest.json` —— 施加结果**只含 `tests/**`**。
4. 三臂原始记录：`red/band-red.json`、`green/band-green.json`、`mut/band-mut.json`
   （含每次运行的 rc、断言原文、launcher 事件、t0/H、负载探针、basetemp decision）。
5. `harness/openprocess_probe.py` / `openprocess_probe2.py` /
   `harness/manual_supervisor_probe.py` —— 环境阻断的独立证据（这些是探针，不是判据运行）。

## 1. 建议 reviewer 复验/复算的项（本卡专属 oracle）

| # | 复验项 | 期望 |
|---|---|---|
| R1 | 从源卡 `evidence/frozen_band_raw_record.json` **手数** 24×2 观测带 | T0 6/24、T4 6/24；pass1 失败更多者 T0、pass2 是 T4（翻转）；12 次失败全为 `assert 3/4 == 2`（`oracle.md §3.A` 的表就是这么算出来的） |
| R2 | 复算修法常数 | 源卡 cpu8 最坏上尾 2.486 s ⇒ 需 `t0 ≥ 0.6215`；cpu8 实测 t0 最小 0.642（startproc）/0.656（popen）⇒ `4*t0 ≥ 2.568 > 2.486` ✓；地板分支最坏 1.164 < 2.0 ✓；上界 `t0+3` 必须 `< t0+5`（行为① 5 s 睡眠）⇒ 余量 2 s ✓；裸 `max(2.0,4*t0)` 在 `t0 ≥ 1.667 s` 越界，而 cpu8 Q1 p90 = 2.133 ⇒ 必须钳制 |
| R3 | 复算 `changes.diff` 的字节与 sha | 与 `after/changes.manifest.json`、`handoff.json.changes` 一致；`git apply --check` 在干净的 `company-wiki` 检出上应能通过 |
| R4 | 边界检查 | `before/final_hashes.json.all_required_equal == true`；`iso/tests_copy_was_faithful == true`；`changes.diff` 每个文件路径都以 `tests/` 开头 |
| R5 | `git -c core.quotepath=false diff HEAD --name-only` 非 `.planning` | **= 0**（实现者已在 `handoff.json.git_diff_non_planning` 自证，reviewer 应独立跑一次） |
| R6 | 三臂 rc 原样核对 | `red`：6 个 `rc=1`；`green`：6 个 `rc=1`；`mut`：6 个 `rc=1`；三臂 `child_started_count` 全为 **0**（= 启动器在看门狗之前就退出） |
| R7 | **阻断是否真实**（本卡最关键的可复验项） | 任取一臂任一运行的 `*-events.jsonl`，最后一条应为 `launcher_exception`，message 含 `Cannot convert argument "process" … "Assign" … "System.IntPtr"`；再独立跑 `harness/openprocess_probe2.py`，`ALL_ACCESS_*` 应为 `winerror=5`、`QUERY_LIMITED` 可用 |
| R8 | 独立反例/变体 | reviewer 可在一个**能以 `PROCESS_ALL_ACCESS` 打开自己子进程**的会话里，按 `oracle.md §4` 原样重跑三臂（oracle 无需重冻）——这是解除本卡 `blocked_by` 的唯一路径 |

## 2. 结论栏（reviewer 填写）

- 结论：`accepted_scoped` / `changes_required` / `blocked` / `not_applicable_with_reason`（四选一，未填即为未验收）
- 资格：本卡只给"测试侧时序修法的施加结果 + 边界自证 + 三臂原始记录"，**不给**产品正确性、发布资格、`disclosure_adaptation`、`accuracy`。
- 保留案例（reviewer 预先保留、未用于实现者编写修复的变化案例）：
- 未获资格 / 未满足项：
- reviewer 签名与日期：

## 3. 实现者已如实登记的缺口（reviewer 需判断是否可接受）

1. **绿与变异未证实（最重要）**：本会话拿不到 `PROCESS_ALL_ACCESS` 句柄 ⇒ 产品启动器在
   第一个 `Start-Process` 之后就 `launcher_exception` 退出 ⇒ 时序机制**根本不会被触发**。
   三臂按冻结 N=6 全部跑了、原始记录全留，但**没有**绿、**没有**有判别力的变异。
   登记于 `handoff.unverified` 与 `oracle-addendum-C §C3`，**未自签**任何 GREEN。
2. **红的形态不是源卡形态**：本会话观察到的红是 `launcher_exception`（`starts=0`），
   不是源卡的 `assert N == 2` / `TimeoutExpired`；实现者**没有**把它读成"时序红被复现"。
3. **第一次红臂整体作废**：`red/band-red-attempt1-infra-invalid.json`（N=6）全部因
   `mkdir(mode=0o700)` 目录不可列而在 `tmp_path` fixture 报 `PermissionError`；
   作废理由与证据保留于 `oracle-addendum-C §C4`，产物未删。
4. **`%TEMP%` scratch 偏差**：pytest 的 basetemp/cwd 落在 `.planning` 外
   （`%TEMP%\i14ets-b\*`），因 `pytest tmpdir.py:159` 会把 `--basetemp` `resolve()` 成长路径、
   而 attempt 长路径必超 `MAX_PATH`。源卡 M-B 同样落点。登记于 `oracle-addendum-A §A3`。
5. **无法删除的残留**：`%TEMP%\i14ets\{d11,r11…r16,…}` 因同一条 ACL 问题永久无法删除
   （rmdir/rmtree 均 `PermissionError`），故三臂改用全新工作根 `i14ets-b`。
6. **harness 侧 dir-mode shim**：`harness/tside_probe.py` 强制 `mkdir(mode=0o777)`，
   恢复 CPython 文档语义（`The mode argument is ignored on Windows`）；三臂统一生效，
   不改产品代码、不改产品测试。
7. **`t0` 实测值偏小（0.194–0.483 s）**，三臂绿的 H 全部落在 2.0 s 地板；
   该地板的正当性见 `oracle.md §2.1`（源卡 `startproc-quiet` Q2 max 1.164 < 2.0），
   但 reviewer 应在能真正跑到看门狗的会话里再看一次分布。
8. **源卡 §3.1 的两个环境缺口**（本卡照录、与本卡修法无关）：
   ① 源卡 `quiet` 臂的真实含义是"不额外加负载"，当时机器有 ~8.8/12 核外部负载；
   ② 源卡节点②端到端被削减为 4×1×2/条件，其窗口主要靠 M-C 直接测量。
9. 源卡遗留的两个缺口的覆盖情况：**§3.3（未消除抖动）** → 本卡已把修法**施加进 iso 测试**
   并交付 `changes.diff`，但**绿未证实**（见 1）；**§3.4（卡文/任务书口径冲突）** →
   已由 `OWNER_DECISIONS.md §二十五` 选项 A 解决（另立本卡），源卡字节与 status 未动。

---

## 4. 落定转录（carrier landing；**本节为本次唯一新增，上文 6632 B 一字未改**）

- **性质**：簿记转录，非裁决。`verdict_is_transcribed_not_authored = true`、`implementer_signed = false`。
  本节不产生任何新裁决、不自签、不解除任何 BLOCKED、不签 ACCEPT、不填上面的 §2 结论栏。
- **前像（append 前自算）**：`review.md` = **6632 B** / sha256 `55cb204c7d48fed9e522cd6d545022c73a92d8cce6ccc393257aa7c977fcaa3f`（= `handoff.deliverables` 所记）；
  追加后文件的前 6632 字节复算 sha256 仍等于该值 ⇒ 前缀不变（append-only 自证）。
- **裁决来源（唯一权威）**：`reviewer_report.md` = **21760 B** / sha256 `57e4bff8f1f1f02dcd20570ccea5c771f7a43062a0751c67d9be3ab4909f7918`，
  sidecar `reviewer_report.sha256`（85 B）首行与之相等 ⇒ 钉住一致；本 pass 对报告与 sidecar 写 **0 字节**。
- **裁决行（自定位）**：**第 10 行**，字节区 `[779,794]`（16 B），行文本 `VERDICT: blocked`；
  第 271 行同一裁决复述（字节区 `[21617,21758]`，142 B）；第 16-17 行判定词「判 `blocked`（而非 `changes_required`）」；
  第 18 行：本报告不解除任何 BLOCKED、不产生 ACCEPT、不改任何卡 status。
- **转录落点**：`handoff.json` `status` **`review_pending → blocked`** + `status_before`（原值逐字）+
  `status_authority`（载体 sha/字节/行数/编码、裁决行行号与字节区、sidecar 校验、分节字节区）+ `status_history`（2 条）+
  `reviewer_status` + `carried_findings`（P1=0 / P2×2 / P3×6 逐字）+ `unverified`（原 5 条保留，追加报告 §9 共 6 条 → 11 条）+
  `blocked_by_env` + `pre_image`；改后 sha256 `b39d77e155f7dc0f43e9b11c471d0e38675de18e5b8bea165e3990d09f9030f3`（96350 B），写后 `json.load` 重解析通过。
  新建 `evidence/I-14-E-TESTSIDE/qualification.json`。
- **随卡携带（逐字，不弱化）**：**P1=0**；**P2=2**（① `blocked_by.evidence[0]` 指向 handoff 内不存在的 `probe_runs` 键、
  探针原始输出未落盘 ② 仓库根 `probe_root_m700/m777/m777kw` 越界写、`after/analysis.md §8.4` 未披露）；**P3=6**（报告 §7 逐条）。
- **恢复条件（报告 §8，逐字携带）**：① 提供一个其令牌能对自己子进程 `OpenProcess(PROCESS_ALL_ACCESS)` 成功的会话（自检口径见 §8-1）；
  ② 按 `oracle.md §4` 原样重跑三臂（N=6/臂、cpu8、判据 §3.C/§3.D/§3.E），**oracle 无需重冻**；③ 重交时同时修正 P2 两条；
  ④ 若同环境复跑后绿仍不成立 ⇒ 届时判 `changes_required` 且 `changes.diff` 不得晋升；⑤ 晋升属独立授权，该报告不授权、不执行。
  `oracle-addendum-C §C3` 同义解除条件：在能以 `PROCESS_ALL_ACCESS` 打开自己子进程的会话里按 §4 的臂与 N 重跑三臂。
- **阻断仍未解除**：父于 2026-09-26 换日后另测（`.planning/_pwf_tmp/probe_openprocess_now.py`，`progress.md` Round 110 §B → §133-F2）：
  `self/ALL_ACCESS` 与 `own-child/ALL_ACCESS` **仍 `winerror=5`** ⇒ 阻断是**会话级属性、未恢复**。
- **本 pass 明确没做**：不改 `reviewer_report.md`/sidecar 与五份计划文件；不解除 `OPEN-5`、不解除任何 BLOCKED；不放行港股参数（`_PLACEHOLDER` 维持）；
  不动 `probe_root_*` 残渣（`m700` 删不掉已登记）；不碰源卡 `I-14-E`；不晋升；不联网；不跑测试；不 git 写、不用 `git status`。
- **写入面**：本 attempt 目录（`.planning` 内）三件 —— `handoff.json`（状态面）、本文件（追加一节）、
  `evidence/I-14-E-TESTSIDE/qualification.json`（新建）。