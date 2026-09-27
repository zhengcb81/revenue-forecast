# T1-F3-FIX decision（实现者说明 · attempt `a20260925-01`）

> 本文件记录**为什么这样修**与**哪些东西我故意没碰**。判定值不写在这里 —— 冻结值在 `oracle.md`
> （含两条 append-only erratum），实测在 `evidence/**`，复算入口是
> `scripts/verify_t1_f3_fix.py`。实现者**不代签 ACCEPT**。

---

## 1. 裁权来源（回源，非转述）

`execution_runs/I-14-B/a20260919-01/oracle.md` 的 `### 11.8`（L274–294，294 行全文；sha256
`b1eb5d0cf83dd8f059d7f011427447a4b79b211c19167f0190b2c140cb34ade6` / 28930 B，**只读、0 写入**）。
另回源读 `T1-10-FIX/a20260923-01/review.md` §7（L73–131）与 `reviewer_report.md` §7.3（L159–216，
sidecar `reviewer_report.sha256` 读回一致），以及登记册 L2103 / L2242。

## 2. 机制：`_parse` 全函数化（登记册 L2103 的用语逐项落地）

| # | 改动 | 为什么 |
|---|---|---|
| 1 | `_parse` 加 `isinstance(ts, str)` 护栏 + `try/except ValueError → None`，返回类型改 `datetime \| None` | 这是 §11.8 ③b 的**唯一授权机制**：`_parse` 不再抛，畸形时间戳从「内部错误」降为「无时序事实」 |
| 2 | 新增 `_echo_ts` | `computed` 的三个时间回显（`scheduled_at`/`started_at`/`observation_finished_at`）：**存在且解析不出 ⇒ null**，能解析 ⇒ **逐字节保持原样**，缺键 ⇒ null（与原来相同） |
| 3 | 新增 `_bad_ts_slot` + `_malformed_time_fields` | 判据写成「**键存在**且 `_parse` 解析不出」，因此**缺键永远不算畸形**（不变量：缺键行为不变），而 `""` / `null` / 非串这类**键在而值不对**的形状按 §11.8「类型/格式错误」拒绝 |
| 4 | `_all_timestamps` 只收可解析戳 | J6 的 `any(stamp > frozen_now)` 不再被 `None` 打崩 |
| 5 | `derive_window`：`started` 读不出 ⇒ `obs_finished` 一并置 `None`；`sample_stamps` 过滤；`command_total` 加 `started is not None`；`explicit` 窗口对过滤 | 观察区间要**两个端点**；端点缺一就不成区间。这样 `defect-2` 区（L189–212）**一个字节都不用改**，且 MUT-16/MUT-17/MUT-18 锚点原样 |
| 6 | `computed` 三处改走 `_echo_ts`；`schedule_lag_seconds` 加 `started is not None` | §11.8 ③b 前半句 |
| 7 | `_eligible` 入口过滤不可解析的记录 | 一处过滤同时解决：排序键不再出 `None`、J6 守卫行（**MUT-6 锚** `if _parse(entry["started_at"]) > frozen_now:  # J6`）**一字不改**、下游 `daily/weekly/monthly` 拿到的必是可解析记录 ⇒ `derive_calendar` **零改动** |
| 8 | `derive_login` 标签循环逐项 `is not None` 守卫 | `label_count` 与 `evidence_kind`（J14）**保留全量标签**：坏时间戳不得用来躲 J14/J13；只有时序量按可得事实算 |
| 9 | `classify` 在分派**之后**追加 `R-TIMESTAMP-MALFORMED` | 三个 `derive_*` 都**整体重赋值** `refusals`，放在分派前会被冲掉；放在分派后对未知 class 不生效（`_malformed_time_fields` 对未知 class 返回空 ⇒ `R-UNKNOWN_CLASS` 行为逐字不变） |
| 10 | `main()` 文档域显式 `if frozen_now is None: raise ValueError(...)` | `_parse` 变全函数后，**rc=2 会静默塌掉**。这一行是 §11.8 ①（rc=2 文档/调用域专属）的**必守**落点；对字符串畸形，`detail` 文本与修前**逐字节相同**（`Invalid isoformat string: '...'`，修前由 `datetime.fromisoformat` 抛出） |
| 11 | 新增测试族 `test_i14b_natural_window_timestamp_total.py`（19 例） | §11.8 ④ 的新族：13 例对修前 SUT **RED**、6 例是稳定行（两像都绿），修后 19/19 绿 |

**新码只加一个**：`R-TIMESTAMP-MALFORMED`。§11.8 ③b 是它的**唯一授权来源**；词表
`16 → 17`，其余 16 码一字未改（口径 `\bR-[A-Z0-9-]+\b`，两像各算一次，集合差 = `{新码}`）。

## 3. rc 域（修前 → 修后，实测）

| 形状 | 修前（`9b1ebda2…`） | 修后（`d1ced6ac…`） |
|---|---|---|
| `started_at="not-a-timestamp"` | **rc=4、无报告、整批 0 裁决**、stdout `internal_error: Invalid isoformat string: 'not-a-timestamp'` | **rc=0、报告写出、全批裁决**、`reject_claim` + `R-TIMESTAMP-MALFORMED` |
| `sampled_at[3]="not-a-timestamp"` | 同上 rc=4 | rc=0 同上 |
| 日历 `ledger.daily[4].started_at` 畸形 | 同上 rc=4 | rc=0 同上，`daily_count=4`（可得事实） |
| 登录 `labels[1].sampled_at` 畸形 | 同上 rc=4 | rc=0 同上，`label_count=3` |
| `started_at=["…"]`（**类型**错） | rc=4、`'list' object has no attribute 'endswith'` | rc=0、同一新码、`computed.started_at=null` |
| 顶层 `frozen_now_utc` 畸形（**文档域**） | rc=2 `malformed_input` | **rc=2 逐字节相同** |
| 顶层 `"cases":"abc"`（§11.8 未枚举） | rc=4 `internal_error` | **rc=4 逐字节相同**（rc=4 机关未被吞掉） |

## 4. 不变量的实测结论（`evidence/after/invariants.json` = **31 checks / 31 passed / PASS**）

- **良构逐字节**：`cases.r2.json` 门 before==after（rc 0 / ok / 34-34 / mismatch 0 /
  **`sut_report` sha 同为 `beb06495fcd93b2c…`**）；`cases.json` 门 before==after（rc 1 / mismatch `W1`
  的既有 superseded 态，两像同值、`sut_report` sha 同为 `6fa04855e762…`）。
- **四套件**：`32 / 18 / 23 / 29`，两像 failed 全 0、passed 相等；新族 **before 6 passed 13 failed → after 19 passed 0 failed**。
- **20 臂变异棘轮**：两像各 `mutation_count=20 / all red / all expected cases red / load_bearing=20`（修法未削弱任何判据锚）。
- **NC-MISSING**：`K7, S7a, S7b, S7c, S8, S9, S10` 7 行 before==after **逐字节全等**；`S7a/S7b/S7c = accept []`、
  `S8 = reject [R-EMPTY-EVIDENCE, R-FUTURE-CLOCK, R-SAME-INSTANT]`（**不含 `R-CLAIM-EXCEEDS`**）。
- **词表**：16 → 17，`after − before = {R-TIMESTAMP-MALFORMED}`，`before − after = ∅`。
- **批次负控**：before `B-NEG` rc=4/无报告（炸批，区分度在）；after `B-POS` rc=0、4 条 verdict、
  坏 case 单独被拒；`B-BYTE-1` 良构三条 verdict 与「只跑良构」**逐字节相同**；`B-BYTE-2`
  良构-only 报告 sha before==after。
- **四条变异臂全红**：A（`_parse` 还原为修前原文）TS1–TS5 **5/5 回 rc=4**；B（去掉新码）5/5 翻
  `accept_claim`；C（`computed` 不置 null）TS1/TS5 的 `started_at` 不再是 null；D（删降级）TS1/TS5 回 rc=4。
- **行不交界**：见 §5。
- **diff 可逆**：`changes.diff` 应用到左像 `9b1ebda2…` ⇒ 逐字节 = `d1ced6ac…`；新测试文件亦逐字节重建。
- **只读边界**：`git -c core.quotepath=false diff HEAD --name-only` → total 3826 / **非 `.planning` = 0**；
  两前置卡 `changes.diff`+`handoff.json` 与 I-14-B `oracle.md` 五个 sha **全部等于派发时的登记值**。

## 5. 行不交界（实测，`evidence/after/line_disjointness.json`）

本卡在左像 L2（`9b1ebda2…`，549 行）上的**改动 + 插入**行集（1-based；插入点保守记为其前后两行）：

```
89-92, 104-105, 123-124, 130, 132, 134-135, 150-151, 152, 167, 170-173,
249-250, 253, 259, 287-288, 417-419, 424, 489-490, 515-516
```

与外部区（由两前置的 `changes.diff` 用 difflib 映射到 L2，**自己算的、没采信转述**）：

| 外部区 | @L1（派发单原值） | @L2（实测） | 交集 |
|---|---|---|---|
| T1-10-FIX 新增内容 | `{60-74, 207-217}` | `{67-75, 81, 214-224}` | **∅** |
| T1-F2-FIX 新增内容 | `{56, 360}` / hunk `{53-59, 357-363, 439-444}` | `{56-63, 367-379, 461-476}` | **∅** |
| defect-2（quick_check/J15/J6 区） | `{182-205}` | `{189-212}` | **∅** |
| `_parse` 本体（**本卡授权面**） | `{82-88}` | `{89-95}` | **包含**（`89-92 ⊆ 89-95`） |

`foreign_hits = {}`。合并链自己重建过：`apply(D1, L0)==L1` 与 `apply(D2, L1)==L2` 均**逐字节 True**
（`evidence/line_zones.json`）。

## 6. 我**没有**做的事（逐条）

1. **没有**改两前置卡的任何字节或 status（5 个 sha 复核相等）。
2. **没有**改 `I-14-B/oracle.md`（`§11.8` 只读；**未追加**任何东西）。
3. **没有**写五份计划文件（`task_plan.md` / `findings.md` / `progress.md` / `REMEDIATION_REGISTER.md` /
   `OWNER_DECISIONS.md`）。
4. **没有**改词表既有 16 码中的任何一个字节。
5. **没有**代签 ACCEPT：`handoff.json` `status=review_pending`、`implementer_signed=false`。
6. **没有**晋升 / apply / merge / rebase 任何 `changes.diff`（零生产合并）。
7. **没有**执行任何有状态 git 命令（唯一 git 调用 = 只读的 `diff HEAD --name-only`）。
8. **没有**联网。
9. **没有**改 `.planning` 之外的任何文件（非 `.planning` 计数 = 0）。
10. **没有**在冻结前跑过任何 SUT / harness / pytest（`evidence/freeze.json` + mtime 序取证）。

## 7. 边界与未修项（提请父方裁，详见 `oracle.md` §8 与 ERRATUM-2）

| # | 形状 | 现状 | 为什么不修 |
|---|---|---|---|
| B1 | **缺必填时间戳键**（`fields["started_at"]` / `window["started_at"]` / `entry["started_at"]` / `label["sampled_at"]` 缺） | `KeyError` → rc=4（与修前**逐字节相同**） | §11.8 只授权 `_parse` 抛 `ValueError` 这一形状；派发单又明令「缺键行为不变」。**两令相交 ⇒ 不动**。提请裁：缺键是否也该 per-case 拒绝、配哪个码 |
| B2 | **容器族**（`windows`/`sampled_at`/`ledger.*` 非 list、`claim` 载体非对象、`clock_source` 容器） | 已由 T1-F2-FIX 处理，本卡**一字未触** | §11.8 ③a 归 T1-F2-FIX（已 `accepted_scoped`） |
| B3 | **`windows`/`labels`/`ledger.*` 元素本身非对象**（如 `windows=["x"]`） | `TypeError` → rc=4 | 这是「载体」族（§11.8 ③a），不是 `_parse` 的 `ValueError`；不在本卡授权机制内 |
| B4 | **顶层 `cases` 类型错**（`"cases":"abc"`） | rc=4（与修前逐字节相同，`CTRL-4` 臂） | §11.8 的 rc=2 枚举只列了「不可解析 / 缺键 / `frozen_now_utc` 不可解析」三形，未列「类型错」⇒ 不自填 |
| B5 | **`labels[].name` 非数值** → `float()` 抛错 | rc=4 | `name` 不是时间戳，§11.8 只授权**一个**新码；给非时间戳配码 = 越权。见 oracle ERRATUM-2 E2-d |
| B6 | 未知 class | `R-UNKNOWN_CLASS` 逐字不变（不做时间戳扫描） | 无授权、无必要 |

## 8. 仪器纠偏（全部在 SUT 修改之前，详录 `evidence/instrument_runs/README.md`）

- **IC-1**：`probes` 首跑的 direct-classify 子探针读错了输入（读了整份文档而非 `cases[0]`）⇒ 修脚本后**整族重跑**（7 条 CLI RED 判据两次取值相同）。
- **IC-2**：`ncmissing` 期望表里 `S9` 的**码序**写错（未按 `sorted`）⇒ 只改我的期望表，实测值自始未变。
- **IC-3**：`suites` 两次 plugin-less 运行被本沙箱 `0o700 → ACL` 打断（第 2 次 pytest 在打印汇总**前**崩溃）
  ⇒ **逐字节复制** T1-F2-FIX 的 `scripts/pytest_tmp_acl_plugin.py`（sha `e96890fe…` / 1725 B，与对方登记值相同），
  basetemp 名加 `g1_` 前缀避开三个不可删目录；原样留存 `instrument_runs/before_suites_run2_pluginless/`。
- **IC-4（见 oracle ERRATUM-1）**：TS-4 的 `label_offsets_seconds` 手算笔误（把 offsets 写成 errors），
  append-only 更正为 `[0, 10]`，该条标注「更正后复测」。
- 三次仪器运行期间 SUT 字节恒为 `9b1ebda2…`（`evidence/freeze.json` 记录的冻结值）。

## 9. 关键指纹（我实算）

| 对象 | sha256（前 16） | 字节 |
|---|---|---|
| `oracle.md`（冻结体 24326 B = `539dbb389c3e70b9…`，其后仅 append） | `ba17f83740104190…` | 31227 |
| `binding.json` | `a89f3bd2b9ba21c6…` | 8866 |
| `commands.json` | `90117d88fb834966…` | 9381 |
| 左像 `9b1ebda2…`（= T1-F2-FIX fixed iso） | `9b1ebda2b75c4d11…` | 23534 |
| 修复后 SUT `d1ced6ac…` | `d1ced6ac566d41cb…` | 30210 |
| `changes.diff` | `693d6239fd958545…` | 29067 |
| 新测试族 | `5e6644fa508a185c…` | 16144 |
| `scripts/verify_t1_f3_fix.py` | `c311fe9722158bc9…` | 59379 |
| `evidence/after/invariants.json` | `c608fce75d9abe99…`（31/31 PASS） | 9093 |
| `evidence/after/line_disjointness.json` | `715021966b9ed8fa…` | 2146 |
