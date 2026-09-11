# R4 Phase A 运行计划（task_plan）

> 运行目录：`revenue-forecast/assurance/runs/2026-09-11_r4-phase-a/`（获准 run 目录；**本 run 的证据产物只落在本目录**——注意同一会话另于 22:08:29 在 company-wiki 提交 `478bb92`，仅改该仓 `PLANNING_STATUS.md` 与该审计目录的 `progress.md`/`task_plan.md` **台账**（+31 行，无产品代码/配置），见 [baseline-map.md](baseline-map.md) §0 的漂移记录与 A-DR2-08）
> 权威来源：[R4 执行计划](../../../../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/simplified-execution-plan.md) · [真实测试矩阵](../../../../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/simplified-test-matrix.md) · [接班手册 §2/§3](../../../../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/execution-handbook.md)
> 状态：**A01–A04 v0.3.1 完成；A.DR rev3 = accepted_with_findings（0×P0/P1）；owner 六项裁定已定（G2）→ A02 封版（v0.4）**；阶段整体仍 **NOT_IMPLEMENTATION_AUTHORIZED**
> 最后更新：2026-09-11 23:0x 本地

## 授权边界（本 run 生效）

- owner 2026-09-11 批准（原文三项）：**① A 阶段精确 DEV/数据读取许可；② `--help`-only command manifest；③ VR reviewer 指派**。
  - 据此：A01–A04 的**只读设计**可做；`--help` 探针可执行（command-manifest 已记录）；A.DR 可提交。
- **仍未授权**：产品代码/配置/DB 写入、`--help` 之外的任何真实命令执行（含 `--dry-run`）、网络、下载、LLM 外发、任务注册/自启动、删除、worker 恢复。
- 按 handbook §2.5：**首次实施前须由 owner 批准精确 DEV 工作包与文件范围**；本 run 不越过该门（A05/A06 仍被该门阻塞）。

## A 阶段 8 步与状态（A-DR-09 一致化后）

| 步骤 | 动作 | 产出 | 状态 |
|---|---|---|---|
| **A01** | 重核三仓代码/配置，映射 query→identify→resolve→open→消费、子进程/hash、root 分支与副作用 | [baseline-map.md](baseline-map.md)（v0.3） | **完成（草案 v0.3）**：§0 输入冻结 + §1 主链 + §1.1 子进程 **7 模块 / 9 真实调用点（+4 处默认绑定）** + §2 root 分支 + §4 CLI 表面积 + §5 未覆盖项；A.DR rev1/rev2 独立复核 12/12 哈希、3 HEAD、51 节点/47 叶子结构 |
| **A02** | 冻结四个已批准 root 的读取等价；root capability 与文档证据质量分开；显式 deny/未注册 root 不放行 | [root-contract.md](root-contract.md)（v0.4，**已按 owner 裁定封版**） | **完成（v0.4 封版）**：更正 A-DR-01/02/03/14 与 A-DR3-08；规则 R7/R8；§5 四条默认值面**已由 owner 裁定**（R-1/R-2/R-4），§6 问题 2 **已裁定 R-3** |
| **A03** | 定义 `query_local` / `open_version` / `request_work` 三接口；本地 latest 只指已索引集合 | [operation-contract.md](operation-contract.md)（v0.3.1） | **完成（草案 v0.3.1）**：更正 A-DR-04/05/10/12/15 与 A-DR3-04/A-DR3-13；47 叶子命令完整性对账闭合；`identify --refresh` 与 `ensure` 的 flag 条件已分轴 |
| **A04** | 定义对外引用 `document_id` + 版本/source hash + locator；路径诊断不入业务身份 | [identity-contract.md](identity-contract.md)（v0.3.1） | **完成（草案 v0.3.1）**：更正 A-DR-07/13 与 A-DR3-02/A-DR3-06；R4 重述为目标并点名残留（含 9 处同型排序）；R6 补齐 owner/机制/存储/负例；V3 静态一半已答 |
| **A05** | 独立 Data-Agent 从**真实资料**挑报告/版本并标注 | corpus-manifest + 独立 oracle | **阻塞**：需精确数据读取许可（owner 已给 A 阶段原则许可，**样本清单未提交**） |
| **A06** | 冻结 L01–L12 本地测试与错误状态；生成小型只读 trace/profile（禁止整库重复扫描） | 每例基线结果 | **阻塞**：需数据读取许可 + 行为探针 manifest（`--dry-run` 属另一份 manifest，未批准）+ **隔离副本** |
| **A07** | 独立 VR 核查询/读取的身份-字节-来源合同；preview 不扩大正式分析/LLM 许可 | 设计负例与副作用审查 | 未开始（需独立 reviewer，实现者不得自签） |
| **A08** | 独立 AR 签"合同/基线可供实施"；生成旧目标→阶段/test 初版映射 | 只解锁 B 的目标明确性 | 未开始 |

## 阶段门与门禁项（不可自签）

| # | 门禁 / 前置 | 状态 |
|---|---|---|
| G1 | **A.DR 设计审查**（A01–A04 完成后，独立 reviewer） | rev1 **rejected**（[reviews/A.DR.json](reviews/A.DR.json)，8×P1/5×P2/3×P3）→ v0.2；rev2 **rejected**（[reviews/A.DR-rev2.json](reviews/A.DR-rev2.json)，1×P1/7×P2/3×P3，16 项中 10 项闭环）→ v0.3；rev3 **accepted_with_findings**（[reviews/A.DR-rev3.json](reviews/A.DR-rev3.json)，0×P0/0×P1，5×P2/8×P3）→ **v0.3.1 纯文本更正已并入本提交**；reviewer 明确"无需重跑探针"，**不再安排 rev4** |
| G2 | **owner 裁定 6 项开放问题**（见下） | ✅ **已裁定（2026-09-11，"按你建议办"）**：逐条见 [owner-rulings-2026-09-11.md](owner-rulings-2026-09-11.md) → **A02 据此封版**；R-1/R-2/R-3/R-4/R-6 登记为 B/C 整改项（R-2/R-4 高优先），R-5 已指派 owner。本裁定**不授权现在改产品代码** |
| G3 | **inputs.json 输入清单**（依赖/lockfile/schema 版本） | ✅ 已补：[inputs.json](inputs.json) |
| G4 | **command-manifest 缺失登记**（A-DR-11 要求：不得只写在散文里） | ✅ 已补：`--help` 探针 manifest = [command-manifest.json](command-manifest.json)（owner 已批）；**行为探针（`--dry-run`）manifest 尚未提交**，属 A06 前置，登记为 blocked |
| G5 | **独立边界观测（OS 级）**（A-DR-08 要求以独立观测替代作者声明） | **pending，需操作员动作**；**归因已完成**（`-shm` 前移 = 本会话强制 push gate 只读打开生产库 + 22:00 每日任务；见 [boundary-audit.md](boundary-audit.md) §2/§3.3）。仍保留本门：作者自证不构成独立证据 |
| G6 | **reviewer 独立性戳记**（A-DR-16：ID 不得由 reviewer 自报） | **pending**：需编排方/操作员在 checkpoint 中从 reviewer 会话外部写入指派记录。**本 run 已按此要求把两个 reviewer ID 记入 checkpoint 的 `reviewer_assignments`（作者从会话外部代记），但仍缺"操作员持有的指派原件"** |
| G7 | **A05/A06 数据读取的样本清单** | **pending**：owner 已给原则许可，样本清单待 A05 提交后逐项确认 |
| G8 | **隔离副本**（行为探针与 VR 的硬前置） | **pending**：生产 catalog **49,677,344,768 B**，禁止在其上做行为探针 |

### G2 六项裁定结果（owner 2026-09-11「按你建议办」；详见 [owner-rulings-2026-09-11.md](owner-rulings-2026-09-11.md)）

| # | 结论 | 后续 |
|---|---|---|
| R-1 | `symlink_policy` = 假保证字段 → 从"已强制"剔除，登记整改（倾向**删字段**，或让现有 5 处 `is_symlink` 判断读同一政策） | B/C 登记（中） |
| R-2 | `reusable_for_filing: false` **必须真的生效**；`None` 仍表示跟随 kind | B/C 整改（**高**） |
| R-3 | 两套准入实现：**以生效的 `config.py` 为唯一来源**，停用无生产调用者的那套；`canonical_write_target` 暂不引入 | B/C 整改（中） |
| R-4 | `privacy_class` 缺省改为**默认不外发**（要外发须显式声明） | B/C 整改（**高**） |
| R-5 | A04 R6 的 owner = `identity-enrichment` + `security_identity`；机制=追加式映射；存储位置在 VR 核清 | A04 R6 表已填 |
| R-6 | A04 R4 = **目标**（非现状）；9 处"路径+优先级决定正本"**登记整改**，不要求现在改代码 | B/C 登记（线） |

## 停止条件

- 需要写产品文件 / 起进程 / 联网 / 读真实语料正文 / 触碰 worker·任务·自启动 → **停并请授权**。
- 发现并发漂移（HEAD 变化、他人在写同一文件）→ 重审受影响部分，不覆盖别人变更。
- **本次实际触发的停止点**：G5/G6（本机无独立观测能力）与 G8（无隔离副本）→ 未执行任何行为探针。

## 变更记录

| 时间（本地） | 变更 |
|---|---|
| 21:0x | A01 基线映射（只读） |
| 21:1x | A02/A03/A04 草案 v0.1 |
| 21:1x | owner 批准 `--help`-only manifest → 52 次探针（52×rc=0）→ A01 §4 更正面 |
| 21:23 | A.DR 首轮 verdict = **rejected** |
| 21:3x–21:4x | 就地更正 A-DR-01…16；新增 [inputs.json](inputs.json)、[boundary-audit.md](boundary-audit.md)、F-A01-8/F-A01-9；快照覆盖扩展到 `-shm`/`-wal` 并重跑 manifest |
| 22:03–22:11 | `-shm` 归因闭环（手动 gate 22:05:03、#141 推送 22:11:22）；v0.2 推送（revenue #141、wiki #101，均 success） |
| 22:2x | A.DR **rev2 = rejected**（1×P1/7×P2/3×P3；16 项中 10 项闭环）→ 第三轮就地更正（v0.3）：blob 字节规范化、四份陈旧文本同步归因、`is_symlink` 措辞、9 个 spawn 调用点、`activation preview` 行、漂移记录、授权/会话 ID、缺件清单 |
| 22:4x | A.DR **rev3 = accepted_with_findings**（0×P0/P1，5×P2/8×P3）→ **v0.3.1 十项纯文本更正**；推送后 CI 全绿（revenue #143、wiki #102） |
| 23:0x | **owner 六项裁定（G2）**："按你建议办" → [owner-rulings-2026-09-11.md](owner-rulings-2026-09-11.md)；**A02 封版 v0.4** |
