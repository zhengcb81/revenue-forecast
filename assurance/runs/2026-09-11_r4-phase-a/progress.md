# R4 Phase A 进度（progress）

## 2026-09-11 — A01 启动（只读）

- **授权**：owner「做R4 主计划」（2026-09-11）。按 handbook §2/§3 解释为**只读 A01 起点**；不覆盖任何写/执行/联网/删除/自启动。
- **建立 run 目录**：`revenue-forecast/assurance/runs/2026-09-11_r4-phase-a/`（**不在审计证据目录内**，符合"不写回本审计证据"）。
- **输入冻结（实测）**：wiki `7d4852f`（干净）、revenue `4c8bc27`（仅运行指针未跟踪）、filing `b44edd8`（干净）；12 个候选定位文件 sha256/字节已记录（见 [baseline-map.md](baseline-map.md) §0）。
- **A01 产出**：主链 query→identify→resolve→open→消费 的 5 跳映射、跨仓子进程 spawn 点、root/kind 分支、9/7 以来"已变更"标记（绝不复原旧 bug）。
- **本步实际副作用**：无 CLI 执行；未读写产品数据；未联网；未起进程；未改产品文件。

---

## 2026-09-11 21:0x–21:4x — A02/A03/A04 草案 → owner 批准 → `--help` manifest → A.DR 首轮 rejected → v0.2 更正

### 1. 授权落位

owner 三项批准：**① A 阶段精确 DEV/数据读取许可；② `--help`-only command manifest；③ VR reviewer 指派**。据此执行了 **52 次 `--help` 探针**（52×rc=0）并把 A01 §4 从"源码 grep 的 47"更正为"**41 顶层 + 10 嵌套 = 51 节点 / 47 叶子**"。**未**越界的动作：产品写入、`--dry-run`、真实数据命令、网络、删除、worker 恢复。

### 2. 三轮文档与首轮复审

| 轮 | 内容 | 结果 |
|---|---|---|
| v0.1 | A02 root-contract / A03 operation-contract / A04 identity-contract 草案 | 提交 A.DR |
| A.DR | 独立复审（reviewer 会话 `7cd316cc-…`，非作者会话） | **verdict = rejected**：8×P1 / 5×P2 / 3×P3；确认正向事实 12/12 输入哈希、3 HEAD、51 节点结构、checkpoint 产物哈希、跨仓 spawn 引用、目录隔离 |
| v0.2 | 16 项发现**逐条就地更正**（见 [findings.md](findings.md) F-A01-9 的映射表） | 本文以下各条 |

### 3. v0.2 更正清单（逐条）

| 发现 | 严重度 | 更正位置 | 要点 |
|---|---|---|---|
| A-DR-01 | P1 | [root-contract.md](root-contract.md) 更正 1 + R7 | `symlink_policy` 解析但**从不被读取** = 假保证字段 |
| A-DR-02 | P1 | root-contract 更正 2 + R8、[baseline-map.md](baseline-map.md) §1②/§2 | 复用链不存在；只看 `root.kind`；`reusable_for_filing: false` **fail-open**；`priority` 分支是字符串字面量 |
| A-DR-03 | P1 | root-contract 更正 3 + R8 | `canonical_write_target` 强制存在于**无生产调用者**的 `policy_2x.py`；活 loader `config.py` 直接拒绝该字段 |
| A-DR-04 | P1 | [operation-contract.md](operation-contract.md) 更正 1 + §2.1/§2.3 | `identify --refresh` = 网络 + 写，移出只读面并登记为高风险 |
| A-DR-05 | P1 | operation-contract 更正 2 + §2.2/§2.3 | 补 7 个漏列叶子命令（`worker-*`×5、`derived-audit`、`import-portfolio`）；47 叶子完整性对账闭合 |
| A-DR-06 | P1 | baseline-map §1.1 + F-A01-2 | 子进程面重建为 **7 模块 / 12 spawn 点**；删除 `company_wiki_source.py` 的 **docstring 伪引用** |
| A-DR-07 | P1 | [identity-contract.md](identity-contract.md) 更正 1/2 + R4 | R4 重述为**目标**；点名残留（`service.py:643-653` 选择键含 priority/root_id/path；`resolver.py:912-921` 路径过滤）；V3 静态一半已答 |
| A-DR-08 | P1 | [boundary-audit.md](boundary-audit.md) + F-A01-8 + 快照扩展 | `-shm` 被**环境未知进程**触碰；覆盖盲区修复；G5 登记为**操作员动作** |
| A-DR-09 | P2 | 本文件 + [task_plan.md](task_plan.md) + [checkpoint.json](checkpoint.json) | 三份台账一致化：step/gate/pending_review 与 HEAD/dirty 重冻结 |
| A-DR-10 | P2 | operation-contract 更正 4 + §2.1 | help 文本错配更正（`identity-enrichment preview` / `activation preview`）；`extraction-quality` 不再标"自述只读" |
| A-DR-11 | P2 | [inputs.json](inputs.json) 新增 + task_plan G3/G4 | 输入清单（依赖/lockfile/schema 常量）；command-manifest 缺失改为**门禁条目**而非散文 |
| A-DR-12 | P2 | operation-contract 更正 3 + §2.2 | 轴 X 拆为 **X-local**（本地导出）与 **X-egress**（对外外发） |
| A-DR-13 | P2 | identity-contract 更正 3/4 + R6 表 + V5 | R6 补 owner/机制/存储/负例；V5 命令收紧为**无 `--refresh`** |
| A-DR-14 | P3 | root-contract 更正 4 + §1 | 引用拆分：`root_id` 唯一性 `config.py:86-88`；`kind` 准入 `models.py:39/141-142` |
| A-DR-15 | P3 | baseline-map §1③ + F-A01-3 | `ensure` 三道闸重述（`--allow-download` / `latest_as_of` / paused 拒绝 + `--allow-acquisition-while-paused` 才记审计） |
| A-DR-16 | P3 | task_plan G6 | reviewer 身份戳记须由**会话外部**写入（作者不代签） |

### 4. 新增产物

- [inputs.json](inputs.json)：三仓 HEAD/dirty + 12 个输入哈希 + **依赖/lockfile 哈希**（wiki 5 件 + filing `pyproject.toml`）+ schema 常量（`1.2.0` / normalizer `1.0.0` / 可升级集 `{1.0.0,1.1.0}`）+ 解释器。
- [boundary-audit.md](boundary-audit.md)：A-DR-08 的证据、受控实验、归因限制与 G5 门禁。
- [evidence/observe_catalog_companions.ps1](evidence/observe_catalog_companions.ps1) + 观测产物：被动观测 `-shm`/`-wal`（**不开库、不执行 CLI**）。
- [evidence/run_cli_help_matrix.py](evidence/run_cli_help_matrix.py) v2：快照覆盖三件套 + `side_effect_scope`（列出 `not_covered` 与解释限制）。
- `reviews/A.DR.json`：首轮复审记录（reviewer 由 owner 指派；ID 为 reviewer 自报，G6 待外部戳记）。

### 5. 本步实际副作用（如实）

- **执行过**：`--help` 探针（52 次 manifest ×2 轮，owner 批准范围）；wiki `tools/pre_push_gate.py`（CI 等价门，5 项全绿）；只读文件读取（源码/git/文件元数据）；被动观测脚本（**不开库、不执行 CLI**）。
- **未执行**：任何数据命令、`--dry-run`、网络、删除、任务注册、worker 操作、产品文件写入。
- **已知偏差（已归因，v0.2 定案）**：A01 期间生产库 `-shm` 出现两次前移（21:18:15、21:26:47）——**已归因于本会话自己的强制 pre-push gate**（`tools/pre_push_gate.py` 的 real-data 套件对生产 catalog 跑 pytest；当晚 push 5 次，GitHub Actions 时间戳 #139 21:19:16 / #140 21:27:44 与之吻合；22:03 手动跑同一 gate 复现，`-shm` → 22:05:03）。**只有 `-shm` 前移，主库与 `-wal` 全程未变 → 无逻辑写入证据**。同时 `--help` 探针、纯 import、25 min 被动观测窗、wiki CI 等价门**均零前移**（阴性对照）。v0.1 的边界快照未覆盖 `-shm`/`-wal` 属**证据缺陷**（已修复）；v0.1 中"本会话未执行任何会打开 catalog 的代码路径"的**更强说法已撤回**——push 协议本身就会（只读）打开它。详见 [boundary-audit.md](boundary-audit.md)。

### 5b. 并行核对：FC-705 门（只读，2026-09-11 22:00 运行后）

- 权威账本 `company-wiki/.source_catalog/legacy_periods.json`：**period 10 = 2026-09-10T21:00:13Z → 2026-09-11T21:00:18Z = 24:00:05（首个真正 ≥24h 窗口）**，`legacy_bridge_hits=0`；period 11 已开。
- `close_gate.close_allowed = false`，**唯一原因** = `period 9: window 23:59:52 is shorter than 24h`（历史窗口，不可补救）→ 预计 **2026-09-12 22:00** 后转 true（last-two = P10+P11）。
- daily `run_id=20260911T210001Z`、`ok=true`、`problems=[]`、`legacy_hits=[]`；triplet = revenue `cd0c0ca` / filing `b44edd8` / wiki `7d4852f`。GP-009 Daily → **6/7**。
- 该核对的副作用：**只有** 22:00 每日任务自身的只读开库（§3.4 标定）；本 run 未执行任何数据命令。

### 6. 未完成 / 阻塞

1. **A.DR rev2**（本 run 下一步）：更正后的 A01–A04 + inputs/boundary-audit 送独立复审。
2. **owner 裁定 6 项**（task_plan G2）：`symlink_policy`、`reusable_for_filing`、两套准入实现收敛、`privacy_class` 缺省、R6 owner、R4 严格读法。A.DR 要求**先裁定再冻结 A02**。
3. **G5/G6**：独立边界观测与 reviewer 戳记 → 需操作员动作。
4. **A05/A06**：样本清单 + 隔离副本（生产库 49,677,344,768 B，禁止行为探针）。
5. 错误状态码全集（A06 冻结对象）未整理。

### 7. 下一步（精确）

- 提交更正 commit → 启动 **A.DR rev2**（独立、非作者）→ 若通过，向 owner 提交 6 项裁定请求 + A05 样本清单。
