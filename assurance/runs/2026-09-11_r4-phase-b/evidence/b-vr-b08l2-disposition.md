# `B.VR-b08l2` 复审逐条处置（B08 / G8 第②级）

> 复审记录：[reviews/B.VR-b08l2.json](../reviews/B.VR-b08l2.json)（**`APPROVE_WITH_FINDINGS`：0×P0 / 0×P1 / 2×P2 / 5×P3**；28 条主张：21 SUPPORTED / 4 PARTIAL / 2 REFUTED）
> 被审对象：`b08-level2-report.md`、`evidence/b08_isolated_env.py`、`evidence/b08_level2_run.py`、`evidence/b08_level2_probe.py`、`evidence/b08-level2-evidence.json`、`evidence/b08-level2-probe.json`、`evidence/b08-real-root-choice.json`、`owner-directive-2026-09-16.md`
> 纪律：复审的每一条**先复现再改**；改完的每一条在本文件里留"改在哪、怎么验证"。

## 复审自己给出的最强复现（它没被攻破的部分）

- 它把探针输出改到自己 temp **完整重跑** ⇒ 与仓库证据**逐字节相同**（递归比较 0 差异）；第三次在 `sys.addaudithook` 触发式看门狗下再跑一遍 `build_level2` + 探针 ⇒ `blocked_count=0`、**生产 catalog 打开次数 = 0**、所有写入都在 `%TEMP%`。
- 守卫 `selftest` **5/5**；它自造 **12 条**对抗路径 **12/12** 被拒且 `Test-Path` 证明**一个都没创建**；**4/4** NTFS junction 逃逸被拒；`parents[3]` 运行期验证正确（历史死代码确已修好）。
- 生产 catalog 元数据与记录**完全一致**（主库 49,677,344,768 B / `2026-09-08T21:23:21.072747Z`；`-wal` 0 B；`-shm` 32,768 B）。
- 它指出**任务提示里我给它的 sidecar 哈希是错的**（我写了 62 位十六进制）——**报告与证据里的值是对的**；它自己重算的正确值：`386487167b74b3b31949643d6f2a1853d161a909736f1a5da23ee9c17e9be3b0`。**我的笔误，记录在此。**

## 逐条处置

| # | 级别 | 复审证明的 | 我的处置 | 验证 |
|---|---|---|---|---|
| `B-VR08L2-01` | P2 | 篡改用例**不是内容比对**：`expected=0×64` 在 `resolver.py:1999-2010` 的句柄版本钉死门即被拒，**早于** `:2011` 构造路径 ⇒ **文件从未打开**；而报告 §2 与 L05 写成"在真实字节上/内容与请求版本不符" | **改口径**：报告 §2 第 3 例与 §3 L05 单元改为"只证明**请求/句柄边界的 fail-closed 合同**"；**真内容替换**需写真实文件（未授权）或复制真实语料进 temp（指令 §2/§3 明确未授权）⇒ **登记为缺口**，不声称覆盖；报告 §5 的 F5 同步 | 报告 §2/§3 文字；缺口写进 §3 L05 的"仍然缺什么"列 |
| `B-VR08L2-02` | P2 | `_real_root_state` 只覆盖**直接文件**：假根上"新增**空子目录**"与"**子目录内**任意深度新增文件"**都检测不到**（真根当前无子目录 ⇒ 潜伏）；`cap=200` 截断无标记 | **改工具 + 重跑**：`b08_isolated_env._real_root_state` 改 `rglob` **递归**，新增 `dir_count`/`dirs`/`capped_at`（cap 提到 500 并显式标记截断） | 重跑后两份证据：`file_count=2`、`dir_count=0`、`dirs=[]`、`capped_at=None`，`real_root_unchanged=true`、`production_catalog_unchanged=true` |
| `B-VR08L2-03` | P3 | `roots` 表**没有** `read_only`/`canonical_write_target` 列；证据里的 `root_spec`（`b08_isolated_env.py:244-245`）与 `held_handle_mode`（探针）是**硬编码字面量**却被当作观测 | **改工具**：`build_level2` 现在**读回**隔离 catalog 的 `roots` 行 → 新字段 `root_row_from_catalog` + `root_row_columns`；原硬编码块改名 `root_spec_intent` 并注明"**是意图不是观测**"；探针的 `held_handle_mode` 改读 `held.mode` | 新证据里 `root_row_from_catalog` = `{root_id, path, kind, priority, last_scan_run, last_scanned_at}`、`root_row_columns` 与上列一致（**确无** read_only 列）；探针输出 `held_handle_mode: "rb"` |
| `B-VR08L2-04` | P3 | 报告 §4"仓库与生产目录**无新增文件**"**字面为假**：本轮 Python 导入在 `evidence\__pycache__\` 留下 gitignored 的 `b08_isolated_env.cpython-313.pyc`（22,995 B，非生产数据） | **改口**（报告 §4）："**没有新增被跟踪文件、没有任何生产数据文件被改动**；证据文件是**提交**的预期产物"；并把该 `.pyc` 删掉 | `evidence` 下 `__pycache__` 计数 = **0**；报告 §4 文字已改 |
| `B-VR08L2-05` | P3 | L12 记"**覆盖**"，但同一行的"仍然缺什么"与 §3 读法都只说推进了"真实读取**半边**"，而 L05/L06 同类情形记"部分" ⇒ 定级不一致 | **改定级**：L12 改为 **部分（真实读取半边已达）**，并注明与 L05/L06 同口径 | 报告 §3 L12 行 |
| `B-VR08L2-06` | P3 | §4 隔离写入路径描述不准（实际在 `.source_catalog\` 下，且有 `-wal`/`-shm`） | **改描述**：`.source_catalog\catalog.sqlite3` + 扫描期间出现后消失的 `-wal`/`-shm` + `operation.lock.acquire` | 报告 §4 表格最后一行 |
| `B-VR08L2-07` | P3（**B08 范围外**） | 指令文件 §4 引用的键名 `explicitly_excluded` 与证据里的 `explicitly_excluded_not_run` 不符；且"逐条批 → 只读整批批准"的授权问题应由 B.AR 复审裁定 | **改键名**（并注明是笔误、由本复审指出）；在指令文件里补一段**授权口径**（只批只读子集、manifest 自带 `NOT APPROVED` 串原样保留、**最终裁定权交给 `B.VR-bar`**） | [owner-directive-2026-09-16.md](../owner-directive-2026-09-16.md) §3；B.AR 复审进行中 |

## 复审**明示没能核验**的（与本报告口径一致，不重复声称）

OS 级进程旁观（它的钩子只在 Python 进程内 ⇒ 别的进程/原生 Win32 打开**不可见**）；**生产 catalog 内容**（按规则只能 `stat` ⇒ "大小+mtime 不变"的内容写入**对它和工具都不可见**——**这是整条零副作用主张的残余风险**）；写者占用 / 并发替换 / 真实 ACL / 云占位 / symlink 逃逸；L03/L07/L10 的真实半边；A05 manifest 与全部 B.AR/B09 产物（另派 `B.VR-bar`）。

## 它顺手记下的两件环境事实（我不据此归属任何一方）

1. **HEAD 在复审中途移动**：它从 `09cce40` 开始，我并发提交了 `70c90d4`；它用 subprocess 按字节比对确认九个被审文件与提交 blob **逐字节相同**（它的第一次 `git show | Out-File` 比出过假哈希，是管道重编码假象，它已在记录里写明），因此结论适用于 `70c90d4`。
2. **生产 `-shm` 在它的会话里移动过两次**（`20:48:14.252430Z` → `21:00:15.342546Z` → `21:03:27.714877Z`），但**在被审窗口内未移动**（两份证据快照都是 `20:48:14`）；主库与 0 字节 `-wal` 始终未动。按 **G5** 纪律**不归属**。
3. 它的三次探针重跑**删掉了受审隔离根的临时 `-wal`/`-shm`**（内容不变，已在记录中披露）——**隔离根是实验产物、可重建**，不是生产数据。
