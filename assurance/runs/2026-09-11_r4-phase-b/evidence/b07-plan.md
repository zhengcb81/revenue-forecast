# B07 实施计划（唯一版本化读取合同，**wiki 侧**）——v0.1（2026-09-12）

> **状态（2026-09-12）**：①②③ 已在**隔离 worktree**（`r4b06-wip`，基线 `f0aacbf`）实现并自测通过——契约声明写在版本常量旁（版本政策 / 五值词汇 / **无目录级 fallback** / 消费者侧归 C），`build_resolution_envelope` 对**未知版本显式拒绝**（fail closed），新增 F10 `test_r4b07_version_contract.py` **4 用例**；既有信封用例 18 条不回归，棘轮 2 passed。④ **`B-payload-hash` 已可执行且通过**（见 [findings.md](../findings.md) F-B07-1，独立于本 worktree）。**待移植到主检出 + 独立复审。**

> 依据：[b-design.md](../b-design.md) §B07（范围重划：**B07 只签 wiki 侧**；消费者侧 adapter/fallback 归 **C**）；允许集 [file-scope.md](../file-scope.md) §3b：**B07 = F2（合同版本与五值拒绝）+ F8（`export_policy` 语义不变）** + F10（仅新增测试）。
> 完成定义（设计原文）：**四件**——① wiki 侧版本化合同；② 未知版本**显式拒绝**；③ **不新增** fallback 分支（并显式声明"本接口无目录级 fallback 语义"）；④ **payload hash 不变**。**不含 N-1**（登记为跨仓待定义项）。

## 1. 现状（实测锚点）

| 事实 | 锚点 |
|---|---|
| 合同版本常量 | `resolver.py` 的 `SOURCE_RESOLVER_SCHEMA_VERSION`（`SourceHandle.schema_version` / `ResolutionResult.schema_version` 同源） |
| 五值拒绝（接口模型） | `operation-contract.md` §2.4：`not_found`/`not_indexed`/`unavailable`/`blocked`/`ambiguous`（**与 `ResolutionStatus` 的五值不是同一套**：后者是 `reused_exact`/…/`identity_conflict`） |
| 版本校验在哪 | wiki 侧**只接受 `"1.0"`**（`resolver.py` 的版本检查）；消费者侧同样只接受 `"1.0"`（`filing-fetch/scripts/filing_contracts.py` 的 `RESOLUTION_ENVELOPE_SCHEMA_VERSION`）——**两侧都没有 N-1 规则**（B-DR4-03 已把 N-1 移出完成定义） |
| 现有的"fallback"面 | `resolve` 内部有 legacy bridge（由 runtime policy snapshot 的 `legacy_bridge_enabled` 门控）——**不是**目录级 fallback；设计禁止的是"缺 policy 时静默退回 `companies` 目录"这类语义 |
| `B-payload-hash` | = `resolve` 输出里 **policy_export payload** 的字节/hash 不变（**不是** `ResolutionEnvelope` 的字节）。当前登记为 **blocked**：无冻结基线、且原以为"取值需待批 CLI" |
| `policy_2x` 的 payload 可达性 | **已实测可达且无需 CLI**：`cli._policy_export_payload(config)` 是纯函数（B01 的验收用例即在用它）；其 hash **与机器相关**（内嵌每个 root 的绝对 `path_ref`，见 [findings.md](../findings.md) **F-B01-9**：本机 `c773099b…` / CI Linux `ca3b7f5d…`） |

## 2. 本步交付（四件）与落点

### ① 版本化合同 + ② 未知版本显式拒绝（F2 + F10）

- 在**合同处**（`SourceHandle`/`ResolutionResult`/`ResolutionEnvelope` 的 docstring 与常量旁）**显式写明**：本接口的版本策略是"**只接受当前版本，未知版本必须显式拒绝**"，并列出拒绝时使用的**接口五值**（`not_found`/`not_indexed`/`unavailable`/`blocked`/`ambiguous`）——**不新增状态**。
- 新增负例（F10）：未知 `schema_version` 的输入（构造一个 `"2.0"` 的句柄/结果）必须被拒绝，且**不得**因此读到别的目录或降级服务。
- **不做**：不加 N-1 规则、不加版本协商字段（那属跨仓协议工作）。

### ③ 无新增 fallback + 显式声明（F2 + F10）

- 在合同 docstring 里**显式声明**："wiki 侧本接口**没有目录级 fallback 语义**"（即：找不到合格副本就按五值显式失败，**不会**改读 `companies/` 下别的位置）。
- 负例：构造"请求的版本不存在、但同实体在 `companies` 下有别的版本"的场景 ⇒ 必须 `missing`/`not_found`（**不取另一修订**），与 B04 的 L03 用例同向但**针对合同层**。

### ④ `B-payload-hash`：**把它从 blocked 变成可执行**（F10 + run 目录证据）

设计残留的阻塞理由是两条：**无冻结基线**、**取值需待批的 CLI**。第二条**已被实测证伪**（纯函数可调）。因此本步改为**可执行的相对校验**：

1. 建 **pre-B 的只读 worktree**（`cab1fd6^`，即 B 第一次产品改动之前），用**显式 `project_root`**（避免 `${PROJECT_ROOT}` 随检出目录漂移）计算 `_policy_export_payload`；
2. 在当前树用**同一个 `project_root`** 重算；
3. **逐字节比较** payload（hash + 序列化字节），把两次结果与比较脚本写进 run 目录（`evidence/b07_payload_baseline.py` + `.json`）；
4. 结论只有两种：**相同** ⇒ `B-payload-hash` 在"这条修订窗口 + 该 project_root"下**满足**（并注明：绝对值与机器相关，跨机器不可比，见 F-B01-9）；**不同** ⇒ **阻断合入**，除非同时提交跨仓迁移。

> 这是本步**最有价值**的一项：它把一条挂了很久的 `blocked` 门变成**有命令、有产出、可复跑**的检查。**不**声称跨机器可比。

## 3. 明确不在 B 签名内（归 C）

- **消费者侧**：`filing-fetch/scripts/filing_contracts.py` 的 adapter 转换、`revenue-forecast/scripts/company_wiki_source.py` 的许可门、任何 `companies` fallback 代码 —— **归 C**；B 只在验收记录里注明"消费者侧未验"。
- **消费者接线到 `read_verified_bytes`**（B03 的字节入口）：同样属**消费者仓** ⇒ 归 **C**。B03 的实施记录里那句"接消费者归 B07"**是错的**，已在 [b03-implementation.md](b03-implementation.md) §4 更正为"归 C；B07 只交 wiki 侧合同（含对该入口的声明）"。

## 4. 用例清单（F10，映射 L11/L12）

| 用例 | 覆盖 | 矩阵 |
|---|---|---|
| 当前版本被接受（正例） | 合同可用 | L11 |
| 未知版本**显式拒绝**，且理由落在五值内 | ② | L11 |
| 请求版本不存在但同实体有别的版本 ⇒ 不取另一修订、不读目录外 | ③ | L11/L03 |
| 合同声明里**没有**目录级 fallback（断言 docstring/常量处的显式声明存在，防止被改回去） | ③ | L11 |
| `resolve` **零写**：读路径不产生 DB 写、不联网、不触碰 worker 控制（用只读连接 + 无网络探针断言） | L12 | L12 |
| `B-payload-hash` 相对校验脚本可复跑（同一 machine/project_root 下逐字节相同） | ④ | `B-payload-hash` |
| 二次 0 parser/LLM/download 的**独立观察** | **不在本步**（需 B08 的隔离观察，A-VR-09 的 `normalizer.py:516` spawn）——登记 | L12 |

## 5. 停止规则

命中即停并记录：需要改 F2/F8/F10 之外的文件；需要在消费者仓改代码（那是 C）；需要真实隔离副本或真实语料；payload 逐字节比较出现差异且无法在本步内解释。
