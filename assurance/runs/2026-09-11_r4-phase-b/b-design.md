# B 阶段设计（b-design）—— 位置透明索引与只读读取

> 状态：**DESIGN_ONLY**。本文件只描述"要做什么、改哪些文件、怎么验"，**未修改任何产品代码**。
> 依据：R4 执行计划 §B（B01–B10）、阶段 A 冻结合同（[root-contract v0.4](../2026-09-11_r4-phase-a/root-contract.md)、[operation-contract v0.3.1](../2026-09-11_r4-phase-a/operation-contract.md)、[identity-contract v0.3.1](../2026-09-11_r4-phase-a/identity-contract.md)）与 owner 六项裁定。
> 精确定位与哈希见 [file-scope.md](file-scope.md)；测试映射见 [test-acceptance-map.md](test-acceptance-map.md)；风险与停止规则见 [risk-and-stop-rules.md](risk-and-stop-rules.md)。

## 总原则（来自阶段 A 合同，B 不得违反）

| 编号 | 原则 | 来源 |
|---|---|---|
| P-1 | 能力四轴（可读/可写/可外发/可复用）**互不推导**；任一声明不得推出另一轴 | A02 R1 |
| P-2 | 未注册 root / 显式 deny 不因"默认等价"放行 | A02 R2 |
| P-3 | **假保证字段不得留在"已强制"清单**（`symlink_policy` 现状即此） | A02 R7（owner R-1） |
| P-4 | **同一份 YAML 不得有两套准入实现**；以生效的 `config.py` 为唯一来源 | A02 R8（owner R-3） |
| P-5 | 纯查询接口不得触网/不得 `ensure`/不得改 worker 状态/不得写 catalog | A03 §1 规则 R3 |
| P-6 | 路径诊断信息**不得进入业务身份**（位置代表权由路径决定 = 现存残留，登记整改） | A04 R4（owner R-6） |
| P-7 | 显式 `reusable_for_filing: false` **必须生效**（当前 fail-open） | owner R-2 |
| P-8 | `privacy_class` 缺省**不再默认可外发** | owner R-4 |

---

## B01 —— 字段唯一 owner 与旧字段版本映射

**目标**：为每个 root 字段指定**唯一 owner**，消除"同一语义两处实现/两处读取"的可能。

| 语义 | 唯一 owner（设计） | 现状（阶段 A 实测） | 本步要做的决定 |
|---|---|---|---|
| 物理位置（path、adapter、symlink 政策、大小/编码限制） | **storage 层**（`config.py` 加载 → `models.RootSpec`） | `config.py:70-118`（活）+ `policy_2x.py:39/164`（无生产调用者） | 按 owner R-3：**停用 `policy_2x` 路径**，`config.py` 为唯一准入 |
| 业务身份（document_id、version/source_hash、locator） | **catalog 层**（`models.py` + `service.py` 投影） | `service.py:621-663` 规范位选择含路径/优先级（残留） | 按 owner R-6：登记整改，B 只**不改语义**，先在读取合同上把 locator 显式化 |
| 可复用资格 | **policy 层单一函数**（**不得新增第二套 effective_reusable**） | 复用判定只看 `root.kind`（`resolver.py:782-786`/`:933-940`） | 按 owner R-2：让 `reusable_for_filing: false` 生效；实现点=同一处判定，不新增并行实现 |
| 外发策略 | **动作边界**（调用外部服务的那一刻） | `llm_summarizer.py:333-337` 按 `privacy_class` 造白名单 | 按 owner R-4：缺省改为不外发；策略仍在动作边界读取 |
| 文档证据质量（期间/页码/locator 完整度） | **不由 root 字段承载**（与能力正交） | A02 C5 | B 不引入"质量即能力"的推导 |

**旧字段版本映射**（B01 交付物）：为下列字段给出"保留 / 弃用 / 改名"的目标与迁移条件——
`read_only`、`reusable_for_filing`、`symlink_policy`、`priority`、`privacy_class`、`cohort`、`canonical_write_target`、`adapter_id`/`adapter_version_range`、`allowed_document_kinds`、`allowed_statuses`、`sidecar_suffixes`、`max_file_size`、`encoding`、`routes`。
**硬要求**：任何弃用都必须**先测 N-1 支持合同**（L11），且**不得让合法旧引用突然不可读**。

**DR 检查点**：字段合并/弃用方案；不得新增第二套 effective_reusable；显式 `false` 含义保留（owner R-2）。

---

## B02 —— 同版本候选 location 的选择

**目标**：把"选哪一份文件"从"先取 canonical 再筛"改为**先构造全部合格候选，再在合格集合内排序**。

现状问题（阶段 A 实测）：`resolver.py:912-921` 先在 `is_canonical` 上过滤，`is_canonical` 又是 `service.py:643-653` 按 `(root_priority, root_id, relative_path, location_id)` 取 `ordered[0]` 得到的 → **未被选中的同版本副本在查询早期就被屏蔽**，读者无从知道还有别的合格副本。

**设计**：四段式选择（顺序即语义）
1. **注册/能力**：location 所属 root 已注册，且该 root 具备所需能力（读/复用）——按 A02 R2，未注册即出局；
2. **状态**：`location_status == 'active'`，且不是 provider 拒绝路径（`.rejections`，`resolver.py:918-920` 的既有语义**保留**，但改为**标记而非优先屏蔽**）；
3. **实际可读 + 同 hash**：能打开且能读到与目标 `content_sha256` 相同的字节（读取策略见 B03）；
4. **健康/IO 偏好**：仅在此**已合格集合**内按 `priority` → `root_id` → `relative_path` → `location_id` 排序（保留现行 tiebreak 语义，但**只用于排序，不用于资格**）。

**输出**：`canonical`（排序结果第一）与**完整候选清单**（含每个候选的排除原因），供诊断与 B04 的移动解析使用。

**测试**：L01（四副本分别/同时索引 + 调换 priority）、L02（既有根覆盖组）、L03（撤首选/撤两份/移动改名/全失效）、L04（第五 root 只新增注册；未知 adapter/显式 deny/未注册）。
**DR 检查点**：不靠"先 canonical 后筛"屏蔽其他副本；优先级只在合格集合排序。

---

## B03 —— 稳定只读字节提供

**目标**：`open_version` 返回的字节必须是**已验证版本**的字节；不得出现 TOCTOU 混读。

**设计**（按优先级）
1. **固定已打开句柄**：打开 → 取 size/mtime **快照** → 流式 hash → 校验 `content_sha256` → **在同一句柄上**读回内容（Windows 上以 `FILE_SHARE_READ` 打开并禁止写入者替换；句柄生命周期由调用方限定）；
2. **受控快照**：若句柄不可固定（云占位/被占用/跨卷），退化为**读取既有受控快照**（已存在的 normalized/derived 产物），并在返回值中显式标注 `bytes_source=snapshot` 与快照 hash；
3. **失败即显式**：hash 不符/中断/占位未下载/ACL 拒绝/损坏文件 → 返回**明确原因**（可重试/不可重试），**不回落到"看起来相同"的另一份**。

**禁止**：只信 `mtime` 或文件名判断版本；在 `query`/`open` 内部**隐式新建快照并宣称零写**（新建快照属**另需批准的准备动作**，写入路径与磁盘占用必须单列）。
**纯读取不建缓存**（执行计划 §B03 原文）。

**测试**：L05（打开后替换/同 size 改内容/路径重指/symlink 逃逸 → 稳定流或快照；越界零读/写；无 mtime 冒充 hash）、L06（占用/ACL/云占位/损坏 PDF/超大文件/中断 → 明确原因 + 同版本副本选择；有限资源可取消）。

---

## B04 —— 路径留在诊断，引用不因搬家失效

**目标**：绝对路径与 `location_id` **只用于诊断**；文件移动后 `source`/`version`/`locator` 仍可解引用。

**设计**：
- **不重编号**已被引用的 source（引用用 `document_id` + `source_hash` + locator 三元组，locator 内含 `root_id` + 相对路径）；
- 搬家 → 重新索引产生**新的 location 行**，旧 location 以 `location_status` 标记（`moved`/`missing`），**引用链不断**；
- 解析时按 B02 的四段式**在新候选集合上重新定位**，命中同 hash 即视为同一版本（不触发重新下载、不改变模型输入）；
- 旧引用找不到任何合格副本 → `unavailable`（显式终态），**不自动取另一修订**。

**测试**：L03（撤首选/移动/改名/恢复同 hash/全失效）、L07（搬目录重索引后旧 locator 再打开；真实修订与同 hash 并存；新旧不因 mtime/accession 词序决定；未知关系 ambiguous）。

---

## B05 —— metadata 合并：来源优先，冲突保留

**目标**：业务元数据**不随位置改变**；冲突**保留**而不是按 `priority` 默选。

现状问题（阶段 A 实测）：`scanner.py:1007-1081` 以 `metadata_priority` 比较 root 优先级（`:1038 elif root.priority <= existing_document["metadata_priority"]`）→ **优先级参与"哪份 metadata 算真"**。

**设计**：
1. 每个 metadata 字段记录 **provenance**（来自哪个 root/source、抓取时间、原始片段/hash）；
2. 多来源**一致** → 取值 + 合并 provenance 列表；
3. 多来源**冲突** → 保留全部候选值 + 冲突标记，**不自动择一**（业务侧显式选择或保持"待选择"）；
4. `priority` **只**用于"当读取需要单一时"的**候选排序**（B02 第 4 段），不得改变已记录的 provenance 与冲突事实。

**测试**：L08（同 source 两 root，交换 priority/扫描顺序；完整 metadata 与缺字段/矛盾字段 → 业务事实不变、可信字段有来源、冲突保留）。
**DR 检查点**：swap priority/scan order 不改变业务元数据。

---

## B06 —— 本地可读与正式 capture 分离

**目标**：本地能读**不等于**正式可信；preview 合格**不等于** forecast 合格。

**设计**：
- 返回值携带**资格标签**：`preview`（本地可读、provenance 可能有缺口）vs `verified_input`（身份 + 期间 + 来源齐备，可用于正式分析）；
- 缺下载 URL / 缺捕获日志但有本地导入 hash → **可 preview**，并显式标注缺口；
- 身份或期间不明 → **正式合同不通过**（不是"默认可信"）；
- 缺文本时只返回**所需产物的 pending 状态**，不伪造 `https_url`，不默认联网补齐。

**测试**：L09（真实本地 PDF 缺 URL/捕获日志；分别请求 preview 与正式输入）、L10（原文 ready/文本缺失/sections 失败/summary 安全拒绝，逐次请求不同能力 → 只检查所需能力；LLM/正式分析不继承 preview 许可）。

---

## B07 —— 唯一版本化读取合同

**目标**：对外只有一个**版本化**读取合同；不兼容要**明确报错**，旧客户端在**边界 adapter** 一次性转换。

**设计**：
- 合同版本号 + schema 校验：当前协议、明确支持的 **N-1**、缺版本、未知 schema、缺 policy 五类输入各有明确结果；
- 旧客户端（filing/revenue）通过**边界 adapter** 转换，**不改其调用方语义**；
- 缺 policy 时**禁止**静默退回 `companies` 目录（无 fallback）；
- 不得让合法旧引用突然不可读 → **先测 N-1 支持合同**（L11）。

**测试**：L11（当前协议/支持 N-1/缺版本/未知 schema/缺 policy，从 filing/revenue 真实入口调用）。

---

## B08–B10（实施与验收，本轮不执行）

- **B08**：独立 VR 在**新隔离环境**重跑 L01–L12（+必要旧 C01–C10），并用独立文件/OS 观察证明本地零副作用；不得用人工构造 catalog 结果冒充真实 parser/索引；特殊云场景无法测就**如实标注限制**。
- **B09**：真实四 root + 第五 root 新注册，做一次端到端 `query → open → consumer` 最小读取；错副本/移动/离线逐例复验；独立 AR 从原文重新核身份与 hash；**只允许隔离副本变化**，不改用户原文件。
- **B10**：小范围切到单一读取链，旧入口仅保留显式版本 adapter；记录**可回退版本**与旧字段移除条件；变更经独立审查后才切换；无法兼容则**停止切换**，不永久双跑。

**共同前置**：隔离副本（G8）、owner 样本确认（G7）、D.SAFE 交叉（H01 见风险文件）。
