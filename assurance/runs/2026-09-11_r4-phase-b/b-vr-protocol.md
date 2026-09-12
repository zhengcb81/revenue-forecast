# B.VR 验证协议（待 G8 隔离副本就绪后执行）

> 依据：执行计划 §B08（"独立 VR 在新隔离环境重跑 L01–L12 和必要旧 C01–C10；独立文件/OS 观察证明本地零副作用"）+ 矩阵 L01–L12 + handbook §4（真实性分层）与 §5（独立审查）。
> 状态：**协议就绪，未执行**（需 G8；机制层可先做，见 §1）。执行者必须是**独立 reviewer**（非实现者、非本设计作者）。

## 0. 前置门

| 门 | 要求 | 现状 |
|---|---|---|
| B.DR | 设计被接受（或 accepted_with_findings） | **三轮 rejected**；剩余 P1 为 scope 决定（S-1…S-6） |
| B 实施 | owner 批准 DEV 工作包 + 文件范围（handbook §1 第 5 项） | **未批准** |
| G8 | 隔离副本（**两级**：机制层小 catalog / 真实字节读取） | **未建** |
| G7 | 真实语料样本清单确认 | **未确认** |
| D.SAFE 交叉 | 不涉及删除/写路径（B 只读） | 见 [risk-and-stop-rules.md](risk-and-stop-rules.md) |

## 1. 两级隔离（可直接采用 [findings.md](findings.md) F-B00-3）

| 级别 | 内容 | 构造方式（**不碰生产**） | 可验证 |
|---|---|---|---|
| **L1 机制层** | 小 catalog（几份合成/真实拷贝的 PDF + 多 root/多副本） | 既有测试的做法：`tmp_path` + `CatalogConfig(catalog_dir=…)` + `RootSpec(...)`（实测见 `tests/contract/test_source_catalog_resolver.py:9-45`） | L01–L12 的**机制面**（候选选择、切换、失败语义、TOCTOU 注入、metadata 合并、资格标签、错误五值） |
| **L2 真实字节层** | 在隔离根下**引用真实文件**（只读），或在隔离目录内**复制**样本 | 从 A05 的 `corpus-manifest` 取路径；**只读挂载/复制**，不改用户原文件 | L02/L09/L12 的 R1 层（真实 parser/索引行为、真实字节、零副作用观察） |

**禁止**：把生产 catalog（49,677,344,768 B）当作 L1/L2 的容器；在 L1 里用人工构造的 catalog 行**冒充**真实 parser/索引结果（B08 明文禁止）。

## 2. 必跑清单（L01–L12 → 隔离级别 → 观察方式）

| 测试 | 级别 | 步骤要点 | **必须独立观察的东西** |
|---|---|---|---|
| L01 | L1+L2 | 四副本分别索引 → `query`/`open`；四副本同时存在并**调换 priority** | 业务投影与字节不随 priority 变化；**零网络** |
| L02 | L2 | 既有四 root 覆盖组：按真实 adapter 索引 → 查公司/期间 → 读取 | 每 root 成功/缺口单列；引用与原文相符；**不因 root 名产生新分支** |
| L03 | L1+L2 | 撤首选 → 撤两份 → 移动/改名 → 恢复同 hash → 全失效 | **撤首选后自动切换**（`_handle` 的合格清单路径）；全失效 = `unavailable`，**不取另一修订、不自动下载** |
| L04 | L1 | 第五 root 只新增注册；另测未知 adapter / 显式 deny / 未注册 root | 合法第五根**无需消费者代码改动**；未知/deny 拒绝 |
| L05 | L1 | 打开后替换文件 / 同 size 改内容 / 路径重指 / symlink·reparse 逃逸 | **只返回验证版本的字节**或明确失败；**TOCTOU 不混读**；越界零读/写；无 mtime 冒充 hash。**注意**：本机不支持 symlink（A06 基线里该用例 skip）→ 必须在支持 symlink 的环境或用**目录联接**构造 |
| L06 | L1 | 占用 / ACL 拒绝 / 云占位不可读 / 损坏 PDF / 超大文件 / 读取中断 | 明确原因 + 同版本副本选择；**有限资源、可取消**（对应 B02 预算与取消） |
| L07 | L1+L2 | 搬目录重索引 → 用旧 locator 再打开；真实修订并存 | 原引用仍指原字节；**新旧不由 mtime/词序决定**；未知关系 = `ambiguous` |
| L08 | L1 | 同 source 两 root **交换 priority/扫描顺序**；完整/缺字段/矛盾字段 | 业务事实不变；可信字段**有来源**；**冲突保留**（`conflicts` + `ambiguous`），**不得按 priority 择一**；含"先缺后补"分支（capture_ready 恢复路径） |
| L09 | L2 | 真实本地 PDF：缺下载 URL/捕获日志，但有本地导入 source hash | `preview` 可读并标 provenance 缺口；**正式合同缺身份/期间则不通过**；不伪造 URL、不默认联网 |
| L10 | L1+L2 | 同文档原文 ready / 文本缺失 / sections 失败 / summary 安全拒绝，逐次请求不同能力 | **只检查所需能力**；原文不因无 summary 消失；**LLM/正式分析不得继承 preview 许可**；含 A07 的 **VR-N21**（无门外发出口） |
| L11 | L2 | 当前协议 / 明确支持 N-1 / 缺版本 / 未知 schema / 缺 policy，从 filing/revenue 真实入口调用 | 兼容由**单 adapter** 转换且来源不变；未知**拒绝**；**无 companies 静默 fallback**；无第二权限语义。**B 只签 wiki 侧**，消费者侧记"未验" |
| L12 | L1+L2 | 真 `query_local` → `open` 两次；不完整/不存在/本地 latest 分别运行；**旁观**文件/DB/子进程/network | 查询**零写/联网/worker 控制**；不以 `ensure` 填缺；原文读取**有真实读 I/O**（不得声称零成本）；二次 0 parser/LLM/download **由独立观察证明**。观察点须含 `normalizer.py:516` 的 multiprocessing spawn 与 `evidence_query.py` 的查询路径 |

## 3. 独立观察方法（B08 的核心要求，不能只信应用自报）

1. **文件层**：跑前/跑后对隔离根做**全树快照**（相对路径 + size + sha256 + mtime），只允许出现在**事先声明的允许写集**内；
2. **DB 层**：隔离 catalog 的主库/`-wal`/`-shm` 三件套快照；**主库与 `-wal` 不得变化**（`-shm` 可能因打开而变，须在报告里按本机已标定的机制解释）；
3. **进程层**：记录进程树（父/子/PID/命令行），证明**没有多起 Python/未声明子进程**；
4. **网络层**：独立观察（OS 层或代理日志）证明 L01/L12 期间**零外发**；
5. **反面证据**：报告必须列出**未能观察**的面（如真实云占位、真实 provider）并标 `not_verified`，不得以"未观察到"代替"已证明不存在"。

## 4. 证据格式（每例一行，禁止汇总代替逐例）

```json
{"test_id": "L03", "level": "L1", "isolation": "<绝对路径>",
 "command": "<逐字 argv>", "started_at": "...", "ended_at": "...",
 "expected": "<矩阵原文的验收句>", "observed": "<实测>",
 "verdict": "pass|fail|blocked|not_verified",
 "observation_evidence": ["<快照文件相对路径>", "..."],
 "raw_stdout_path": "...", "rc": 0}
```

**不算通过**：skip/unknown/rc0 空输出；用人工构造 catalog 行冒充真实 parser；只跑机制层却宣称 R1；把 preview 可读当正式输入可用；把"未观察到反例"当"已证明不存在"。

## 5. 与 B.AR 的分工

| 门 | 负责 |
|---|---|
| **B.VR** | 本协议 §2 的 L01–L12（隔离环境）+ §3 的独立观察 |
| **B.AR** | **从原文**独立复算身份与 hash（`document_id`/`content_sha256`/locator 三元组），并做真实四 root + 第五 root 的端到端最小读取（L02/L09/L12 的 R1 层）；**不重复** B.VR 的机制面 |
| 二者关系 | B.VR 通过 ≠ B.AR 通过；反之亦然（矩阵 §"分层"要求：某层通过不回填另一层） |
