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
| A-DR-06 | P1 | baseline-map §1.1 + F-A01-2 | 子进程面重建为 **7 模块 / 9 真实调用点**（v0.3 更正计数，A-DR2-04）；删除 `company_wiki_source.py` 的 **docstring 伪引用** |
| A-DR-07 | P1 | [identity-contract.md](identity-contract.md) 更正 1/2 + R4 | R4 重述为**目标**；点名残留（`service.py:643-653` 选择键含 priority/root_id/path；`resolver.py:912-921` 路径过滤）；V3 静态一半已答 |
| A-DR-08 | P1 | [boundary-audit.md](boundary-audit.md) + F-A01-8 + 快照扩展 | `-shm` 前移**已全部归因**（推送前 gate / 手动 gate / 22:00 每日任务，均只读）；覆盖盲区修复；G5 登记为**操作员动作** |
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

- **执行过**：`--help` 探针（52 次 manifest ×3 轮，owner 批准范围）；**wiki 与 revenue 两个 `tools/pre_push_gate.py`**（CI 等价门；revenue 的 gate 含 real-data 套件，会**只读**打开生产 catalog——见 §5）；**revenue 推送 10 次 + wiki 推送 3 次**（GitHub Actions #134–#142 / #100–#102，全部 success 或进行中）；只读文件读取（源码/git/文件元数据）；被动观测脚本（**不开库、不执行 CLI**）。**v0.3.1 补记（A-DR3-12）**：v0.3 此处漏记 gate 运行与推送次数。
- **未执行**：任何数据命令、`--dry-run`、网络、删除、任务注册、worker 操作、产品文件写入。
- **已知偏差（已归因，v0.3 定案）**：生产库 `-shm` 的**全部 7 处**已观测前移均有归属——`21:18:15`/`21:26:47`/`22:10:11` = 本会话 **#139/#140/#141 推送前的强制 gate**；`22:05:03` = **22:03 手动 gate（未推送）**；`22:00:02`/`22:00:18` = 22:00 每日任务；四者都由 `tools/pre_push_gate.py` 的 real-data 套件（`:184-199`）或 wiki `legacy_observer.py --read-only` **只读**打开该库。**只有 `-shm` 前移，主库与 `-wal` 全程未变 → 无逻辑写入证据**。当晚推送计数更正为 **revenue 8 次（#134–#141）+ wiki 2 次（#100/#101）**，全部 CI success。阴性对照：`--help` 探针（52×2）、纯 import、99 样本观测窗（末样本 21:59:53）、wiki CI 等价门**均零前移**。v0.1 的边界快照未覆盖 `-shm`/`-wal` 属**证据缺陷**（已修复）；v0.1 中"本会话未执行任何会打开 catalog 的代码路径"的**更强说法已撤回**。详见 [boundary-audit.md](boundary-audit.md) §2/§3.3。

### 5b. 并行核对：FC-705 门（只读，2026-09-11 22:00 运行后）

- 权威账本 `company-wiki/.source_catalog/legacy_periods.json`：**period 10 = 2026-09-10T21:00:13Z → 2026-09-11T21:00:18Z = 24:00:05（首个真正 ≥24h 窗口）**，`legacy_bridge_hits=0`；period 11 已开。
- `close_gate.close_allowed = false`，**唯一原因** = `period 9: window 23:59:52 is shorter than 24h`（历史窗口，不可补救）→ 预计 **2026-09-12 22:00** 后转 true（last-two = P10+P11）。
- daily `run_id=20260911T210001Z`、`ok=true`、`problems=[]`、`legacy_hits=[]`；triplet = revenue `cd0c0ca` / filing `b44edd8` / wiki `7d4852f`。GP-009 Daily → **6/7**。
- 该核对的副作用：**只有** 22:00 每日任务自身的只读开库（§3.3 标定）；本 run 未执行任何数据命令。

### 5c. A.DR rev2（独立复审，第二轮）= **rejected** → 第三轮就地更正（v0.3）

- 复审记录：[reviews/A.DR-rev2.json](reviews/A.DR-rev2.json)（reviewer session `b31cbc67-…`，非作者会话；1×P1 / 7×P2 / 3×P3；首轮 16 项中 **10 项闭环、6 项未闭环**：A-DR-01/06/08/10/13/16）。
- **P1（已修）**：`checkpoint.produced_files` 中 4 个文件的**已提交 blob 与记录 sha256 不符**（差异恰为 CRLF 字节数）——它们在 `.gitattributes` 生效前入库。→ 该 4 个文件已 `git add --renormalize` 重新入库，`build_checkpoint.py` 重算，并**逐条校验 committed blob == 记录值**（见 checkpoint 的 `produced_files_verification`）。
- **P2 已修**：① 陈旧"ambient/unknown"文本四处同步为归因后表述（`cli-help-matrix.json`、`run_cli_help_matrix.py`、`inputs.json`、`progress.md` + wiki 侧）；② `-shm` 记录补到审查时刻 22:10:11 并逐一说明；push 计数写实（revenue 10 + wiki 3）并登记"手动 gate 未推送"这一类；③ `is_symlink` 措辞更正（实测 5 行命中，结论不变）；④ 子进程计数更正为 **9 个调用点 + 4 处默认绑定**；⑤ 撤回"证伪"越权表述；⑥ `activation preview` 行按叶子 help 原文改写；⑦ company-wiki 漂移（`478bb92`，仅台账）与"不写回审计证据目录"的表述收窄。
- **P3 已修**：观测窗末样本/间隔数字、`§3.3` 编号、F-A01-8 重复"处置"块；引用精度（`models.py:97`、`llm_summarizer.py:333-337`、3 个测试文件/9 处调用、`ensure` ③ 的 `args.allow_download and` 连接条件、`service.py:772` 第三处排序）；新增 **owner 授权记录**与**作者会话 ID**，并把 handbook §3 的 `card.json`/`baseline.json`/`data-manifest.json` 列入缺件清单。

### 5d. A.DR rev3（第三轮独立复审）= **accepted_with_findings** → v0.3.1 纯文本更正

- 复审记录：[reviews/A.DR-rev3.json](reviews/A.DR-rev3.json)（reviewer session `70b62d2f-…`）。**0×P0 / 0×P1 / 5×P2 / 8×P3**；首轮 16 项 → **11 项闭环**（余 A-DR-06/08/09/13/16），次轮 11 项 → **5 项闭环**（余 A-DR2-02/04/05/08/10/11）。
- **P1 完全闭环**：19/19 `produced_files` 的记录 sha256 == `git cat-file blob HEAD:…` == 工作树字节；reviewer 独立在 `3e0c8f3` 处复现了失败态（4 个文件、LF→CRLF 变换后逐字符命中旧值），并对 `--verify-only` 做了对抗测试（篡改摘要/幽灵路径均被检出；**唯一空过面是清单为空时 checked=0**——脚本只证"记录==blob"，不证清单完整性）。
- **v0.3.1 已修（本提交）**：① checkpoint LEDGER 随 v0.3.1 前进（step/current_gate/next_step/G1/actual_side_effects/reviewed_commit_note/inputs_note，并补 22:26:59 第七处前移与 revenue 10 次推送）；② 撤回传播到位（`identity-contract.md` 的"归属未明"→已归因、`observe_catalog_companions.ps1` 的 ambient 措辞删除、wiki `ca63ff2` 记入 inputs.json 与台账）；③ `boundary-audit.md` §2 的"5 次/两处"改写并与 §3.3 一致；④ `baseline-map.md` 头部 CLI 声明与 §5 的 12→9 计数；⑤ A04 的 R4 残留清单扩到 9 处同型排序；⑥ `root-contract.md` 的 loader 调用者计数（定义/导出/导入 vs 真实调用）；⑦ 三份合同与 task_plan 的版本标签 → v0.3.1；⑧ 缺件清单补 `requirements.csv`；⑨ 观测 CSV 表头与数据列数一致化（6 列，去 BOM）；⑩ `progress.md` 副作用补记 gate/推送 + `operation-contract` §2.2 S 行去掉重复的 `activation preview`。
- **未闭环项的处置**：A-DR-06/08/09/13/16 与 A-DR2-02/04/05/08/10/11 的剩余部分均为**本轮已就地修正的同一批文本**或**只能由 owner/操作员完成**的事项（G2 六项裁定、G5 独立观测、G6 指派原件、G7 样本清单、G8 隔离副本）；reviewer 明确"更正后即可作为 B/C 基线，但 A02 在 G2 前不得冻结"。

### 5e. owner 裁定（G2，2026-09-11）→ **A02 封版**

- owner 回"按你建议办"，六条全部按建议定案，逐条见 [owner-rulings-2026-09-11.md](owner-rulings-2026-09-11.md)：**R-1** `symlink_policy` 按假保证字段处置（登记整改，倾向删字段）；**R-2** `reusable_for_filing: false` 必须生效（高优先）；**R-3** 两套准入实现收敛到生效的 `config.py`；**R-4** `privacy_class` 缺省改为默认不外发（高优先）；**R-5** A04 R6 指派 `identity-enrichment`+`security_identity`；**R-6** A04 R4 保持目标并登记 9 处整改。
- **A02 据此封版**（[root-contract.md](root-contract.md) v0.4：§5 默认值面与 §6 问题已带裁定结论）。
- **边界**：本次裁定**只定方向与登记整改**，**未改产品代码/配置/DB/任务**；R-1…R-4/R-6 进入 B/C 范围，实施前仍需按 §2.5 批准精确 DEV 工作包。

### 6. 未完成 / 阻塞

1. **G5/G6**：独立边界观测与 reviewer 指派**原件** → 需操作员动作（checkpoint 已从会话外部代记三个 reviewer ID，但缺操作员持有的指派凭证）。
2. **G7/G8**：A05 真实语料样本清单 + 隔离副本（生产库 49,677,344,768 B，禁止行为探针）。
3. **A05/A06** 本体未开始；错误状态码全集（A06 冻结对象）未整理。
4. **B/C 整改项**（R-1…R-4、R-6）：每项实施前需精确 DEV 工作包批准。
5. **handbook §3 缺件**：`card.json`、`baseline.json`、`data-manifest.json`、`requirements.csv`（已在 checkpoint 缺件清单登记）。

### 7. 下一步（精确）

- 提交本裁定与 A02 封版 → 推送并自盯 CI 至绿 → 等 owner/操作员给 **A05 样本清单（G7）** 与 **隔离副本（G8）**；B/C 整改项按优先级（R-2/R-4 先行）准备精确 DEV 工作包。
