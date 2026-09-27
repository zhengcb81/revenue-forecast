# I-14-E-TESTSIDE after/analysis.md — 三臂对照、判据逐条判定、边界自证

attempt：`execution_runs/I-14-E-TESTSIDE/a20260924-01`。`status=review_pending`，实现者不自签。

---

## 1. 一句话结论

**修法已施加并可交付（`after/changes.diff`，只含 `tests/**`，1 个文件），边界自证通过；
但本会话的权限范围使产品启动器在看门狗之前就退出，⇒ 红的"时序形态"、绿、变异三者
均未证实**——不造绿，全部如实登记（`handoff.json.unverified`、`oracle-addendum-C`）。

## 2. 采用的修法（详见 `oracle.md §2`，冻结于首跑之前）

```
t0  = 同一次测试内、用看门狗自己的时钟（$StartedAt → Start-Process）实测的
      "launch → .source_catalog/fake_worker_count.txt 落盘"
H   = -WorkerHangTimeoutSeconds = min( max(2.0, 4*t0), t0 + 3.0 )
```

- **只改 1 个参数**（`worker_hang_timeout_seconds`），断言 `== 2`、
  `unresponsive/restarting.reason == "session_start_timeout"`、外层 `timeout=15` 全部原样。
- **下界**：源卡全部独立测量的最坏上尾 2.486 s ⇒ 需 `t0 ≥ 0.6215`；cpu8 实测 t0 最小
  0.642(startproc)/0.656(popen) ⇒ `4*t0 ≥ 2.568 > 2.486 > 2.303`；地板分支最坏 1.164 < 2.0。
- **上界（本卡在建议 1 之上的唯一增补）**：行为① 睡 5 s ⇒ 子进程①在 `t0+5` 干净退出，
  若 `H ≥ t0+5` 看门狗永不触发 ⇒ `next(...)` 抛 `StopIteration` ⇒ **换一种红**。
  裸 `max(2.0,4*t0)` 在 `t0 ≥ 1.667 s` 越界，而源卡 cpu8 Q1 **p90 = 2.133 s** 落在该区
  ⇒ 必须钳制到 `t0+3`（保留 ≥2 s 触发余量）。
- **不用的两条**（`oracle.md §2.5` 写死）：建议 3（放宽 `== 2`→`>= 2`）缺测试维护者的
  书面理由、且会让变异失去判别力 ⇒ 弃用；建议 2 单用源卡已实测无效 ⇒ 不取。
- **节点②不施加**：源卡 M-B 端到端 16/16 全绿（quiet 8/8、cpu8 8/8），源卡自己的 H5 结论是
  "未观测到抖动带"⇒ **复现不出红** ⇒ 按"缺证据写未证实、不造绿"只登记不改。

## 3. 冻结与顺序自证

| 项 | 值 |
|---|---|
| `oracle.md` sha256 | `4c15948e24a2650bf055dddd02b5cc230b561b89de1cf0f34c9a0e293b28f658`（18520 B） |
| 冻结时刻 | 2026-09-25T20:42:26Z（`before/freeze_instant.json`） |
| 冻结前发生的 pytest 运行 | **0**（`runs_started_before_freeze: 0`） |
| 追加式 erratum | `oracle-addendum-A.md`（basetemp 落点，首跑前）、`oracle-addendum-C.md`（会话阻断）；**主文一字未改** |
| expected 来源 | 全部来自源卡 `evidence/frozen_band_raw_record.json`（我独立复数：48 行、T0 6/24、T4 6/24、翻转、12 次 `assert 3/4 == 2`）与 `after/child-lifetime-*.json` / `wrapper-latency-*.json`；**没有任何 expected 来自本卡重跑** |

## 4. 三臂结果（原始 rc 全部保留）

同形条件：`-m pytest -p no:cacheprovider -p tside_probe -q -B`、单节点、逐次全新 basetemp、
stripped env、`condition=cpu, burners=8`（源卡 M-B/M-A 的 cpu8 形态）、driver 超时 90 s、
basetemp 长 55 字符（产品判据 `within-budget`，不迁移）。

| 臂 | N | 原始 rc | verdict | `child_started` | 传给启动器的 H | 导出的 H（t0） | 墙钟 s |
|---|---|---|---|---|---|---|---|
| 红（修前，写死 0.5 s） | 6 | `[1,1,1,1,1,1]` | 6×failed | **0×6** | 0.5 | —（未改动，无探针） | 6.09/6.63/7.51/8.64/13.84/8.79 |
| 绿（施加后） | 6 | `[1,1,1,1,1,1]` | 6×failed | **0×6** | **2** | 2.0（t0=0.483, 0.2065, 0.3106, 0.3095, 0.4089, 0.1944） | 13.20/7.04/7.58/7.74/9.77/5.68 |
| 变异 M1（导出公式退回 0.5 s） | 6 | `[1,1,1,1,1,1]` | 6×failed | **0×6** | 0.5 | 0.5（t0 首例 0.475） | 7.40/8.76/9.98/9.27/10.47/9.50 |

**每一次运行的事件序列都是 `['starting', 'launcher_exception']`** ——
message：`Cannot convert argument "process", with value: "", for "Assign" to type
"System.IntPtr": "Cannot convert null to type "System.IntPtr"."`
（= `source_catalog_worker.ps1:341` 的 `$Child.Handle` 为 null）。

**负载（独立测量，不是"感觉"）**：

| 臂 | ambient before | with_load | after | 每 pass spawn 中位 ms | 每次运行 cpu_loop_300k ms |
|---|---|---|---|---|---|
| 红 | 6.496 | **10.760** | 11.780 | 94.3 | 38.1–62.4 |
| 绿 | 6.144 | **11.018** | 9.032 | 132.1 | 20.1–42.4 |
| 变异 | 1.930 | **9.703** | 9.343 | 60.5 | 23.1–40.4 |

（单位 = busy cores / 12 逻辑核；探针 = 3 s 进程 CPU 差分 + `sleep(20ms)` 超调 +
固定 30 万次循环耗时 + `python -c pass` spawn 延迟。绿臂负载 **不低于** 红臂
⇒ 满足 `oracle.md §3.D.5` 的"同条件"要求。源卡 cpu8 的 spawn 参考值为 1042.8/882.0 ms，
本机当时的 ambient 只有 ~1.9–6.5 核（源卡当时 ~8.8 核），已如实登记为环境差异。）

## 5. 判据逐条判定

| 判据（冻结于 oracle） | 结果 | 说明 |
|---|---|---|
| **E-red**（§3.C）：cpu8 下复现时序红，形态 = `assert N==2` / `TimeoutExpired` | **未达成** | 观察到的红是 `launcher_exception`（`starts=0`），**不是**源卡形态；实现者不把它读成"时序红被复现" |
| **E-green**（§3.D）：同条件 6/6 绿 + 四条时序子判据 | **未达成 / 不可证** | 6/6 在同一环境阻断处失败；t0 与 H 的导出本身**工作正常**（见 §4 绿臂列），但节点的四条时序断言一条都没被执行到 |
| **E-mutation**（§3.E）：M1 ≥1 红且与绿有判别力 | **未达成（无判别力）** | M1 6/6 红，但与绿臂**同因**失败 ⇒ 不构成变异证明 |
| **E-boundary**（§3.F） | **达成** | `after/boundary_check.json` → `verdict: BOUNDARY_OK`、`all_required_equal: true` |
| 负载独立测量（要点 5） | **达成** | §4 表：每臂 3 个 CPU 差分窗 + 每次运行 2 个探针 + 每 pass spawn 延迟 |

## 6. 阻断的证据链（为什么绿不可证）

1. **不经 pytest**：`harness/manual_supervisor_probe.py` 直接用 iso 的 ps1 跑同一个假项目
   ⇒ 2/2 次 `rc=1`、`launcher_exception`、`fake_worker_count.txt` 从未生成。
2. **PowerShell 对照**：`Start-Process … -PassThru` **带** redirect（TEMP 目标 / 仓库目标 /
   仅 stdout / 仅 stderr / `-NoNewWindow` / delay+`Refresh`）→ `.Handle` **全部为空**；
   **不带** redirect → `handle=[2960]`；裸 .NET `Process.Start` + redirect → `handle=[3056]`。
3. **根因探针**：`harness/openprocess_probe2.py` ⇒ `PROCESS_ALL_ACCESS`（`0x1F0FFF`/`0x1FFFFF`）
   对**一切**目标 `winerror=5`（含本会话自己的子进程、含 `explorer`），
   而 `QUERY_LIMITED`/`QUERY_INFORMATION`/`TERMINATE` 可用。
   ⇒ PS `Start-Process` redirect 分支需要的那种句柄在本会话拿不到。
4. **与源卡的对照**：同一台机器、同一份 ps1（sha `5c12cd74…bc311`，与真仓逐字节相同）在
   2026-09-21 产出过真实 `child_started`（每树 7–16 次、被杀 uptime 0.5xx s）⇒ **当时拿得到**。
5. 本会话为 DSH **workspace-write** 沙箱、审批禁用 ⇒ 该限制**不能在会话内解除**。
   解除路径与重跑配方见 `oracle-addendum-C §C3`。

## 7. 边界自证（要点 2、9）

| 检查 | before | after | 相等 |
|---|---|---|---|
| 真仓 `CW/src`（152 文件 / 1 870 859 B） | `34ee472e…92af` | `34ee472e…92af` | ✓ |
| 真仓 `CW/scripts`（135 文件 / 1 583 829 B） | `e7ccf6e3…847f` | `e7ccf6e3…847f` | ✓ |
| 真仓 `CW/tests`（348 文件 / 2 962 813 B） | `369aa19e…1c8e` | `369aa19e…1c8e` | ✓ |
| 真仓 `pytest.ini` / 根 `conftest.py` | `2e33e8c7…` / `8cd6ea39…` | 同 | ✓ |
| `iso/src`、`iso/scripts`、`iso/config`、`iso/pytest.ini`、`iso/conftest.py` | — | — | ✓（与真仓同 manifest） |
| `iso/tests` | `369aa19e…1c8e`（= 真仓，拷贝忠实） | `c6e51084…d456` | **按预期改变**（唯一改动面） |

- `git -c core.quotepath=false diff HEAD --name-only`：总 3826 行**全部在 `.planning/` 下**，
  **非 `.planning` = 0**（`after/boundary_check.json.git_diff_non_planning`）。
- `after/changes.diff`：**只含** `tests/contract/test_source_catalog_worker_bootstrap.py`
  1 个文件；`git -C company-wiki apply --check` **exit 0**（只读校验，未写真仓）。
- 真仓 `git status --porcelain`：before 3 行、after 3 行（**拷贝前既有**，本卡未增删）。
- 源卡 `I-14-E/a20260919-01`：**未读改写**——本卡只读它；其 status 与字节未动。

## 8. 未证实 / 未做（`handoff.unverified` 同步）

1. **绿未证实**、**变异未证实判别力**、**红的时序形态未复现**（原因 §6）。
2. **节点②未施加**（无可复现的红；源卡 M-C 窗口擦线现象登记为 unverified）。
3. 第一次红臂（`red/band-red-attempt1-infra-invalid.json`，N=6）**整体作废**：pytest
   `mkdir(mode=0o700)` 目录在本会话"连 owner 都不可列"（CPython 文档写明该参数
   Windows 上忽略），已加 harness 侧 shim 统一恢复文档语义；作废理由与证据保留未删。
4. 受污染目录 `%TEMP%\i14ets\{d11,r11…r16,…}` **无法删除**（rmdir/rmtree 均
   `PermissionError`），三臂改用全新工作根 `%TEMP%\i14ets-b`。
   本 attempt 目录内同批探针残留同样**删不掉/不删**，逐个登记：
   `r/`（MAX_PATH 探针的空目录链，见 `oracle-addendum-A §A1`）、
   `w/`（短名路径探针留下的空目录）、`probe_att_m700`（mode=0o700 探针，**已不可列**）、
   `probe_att_m777`、`probe_att_m777kw`（正常对照，各含 1 个 `f.txt`）。
   三者都不在 `changes.diff` 的作用面内，也不影响 §7 的任何 manifest。
5. band 行内 `tside_trace`/`reports` 两个字段存在**驱动按偏移读取的归因缺陷**
   （三臂首行有值、其余行漏读）；**权威数据**是逐臂 JSONL：`<arm>/tside-trace.jsonl`（6 条，
   含 UTC 时间戳）、`<arm>/reports.jsonl`（12 条 = 6 shim + 6 call，含完整 traceback）、
   `<arm>/basetemp-decisions.jsonl`（6 条）。臂级事实（rc / verdict / H / child_started /
   负载）来自 pytest stdout 与每次运行自己的 launcher 事件，**不受该缺陷影响**。
6. 本卡**没有**：改产品代码、写真仓 `tests/**`、改源卡任何字节/status、写五份计划文件、
   代签 ACCEPT、晋升、git 写操作、联网。

## 9. 源卡遗留缺口的覆盖情况（任务第 9 条）

| 源卡缺口 | 本卡覆盖 |
|---|---|
| `review.md §3.3`：本卡（源卡）没有消除抖动，需要测试侧改动 | **已施加**：修法写进 iso 测试并以 `after/changes.diff` 交付；**但绿未证实**（§6），故只能算"施加完成、验证待续" |
| `review.md §3.4`：卡文要"修产品测试时序"与任务书"生产仓只读"的口径冲突 | **已解决**：`OWNER_DECISIONS.md §二十五` 选项 A 另立本卡；源卡字节与 status 全程未动 |
| `review.md §3.1` ①（`quiet` 臂实为 ~8.8 核外部负载） | **照录**，与本卡修法无关；本卡自己的 ambient 已独立测量（§4） |
| `review.md §3.1` ②（源卡节点②端到端被削减） | **照录**，与本卡修法无关；节点②本卡不施加（§2） |
