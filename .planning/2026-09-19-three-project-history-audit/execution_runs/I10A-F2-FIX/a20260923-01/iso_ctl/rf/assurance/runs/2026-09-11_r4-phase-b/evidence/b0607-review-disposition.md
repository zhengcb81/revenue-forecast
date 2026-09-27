# `B.VR`（B06）与 `B.VR`（B07）复审处置表 —— 两者均 = `accepted_with_findings`

> 记录：[reviews/B.VR-b06.json](../reviews/B.VR-b06.json)（1×P1 / 4×P2 / 3×P3）、[reviews/B.VR-b07.json](../reviews/B.VR-b07.json)（1×P1 / 2×P2 / 3×P3）。两个独立会话**并行**完成（我明确要求它们**只跑定向用例、不跑全量套件**，避免互相制造负载假失败）。
> 处置提交：**`3740857`（B06）**、**`f2ba5c1`（B07）**（用 [transplant_split.py](transplant_split.py) 的 `--steps b06,b07` + `git apply --cached` 按 hunk 拆成两步独立提交）。
> 两个复审都**复现了作者的关键数字**：B06 复现 12 用例/50 条邻域/ruff，并对**共享列畸形输入做了 27 种 fuzz（含 10 MB 与 bytes 列）零崩溃**；B07 复现了 4 用例、payload 比较（`identical: true`、`bd1a359f…`、1216 B、`5659a22f…`），并**独立确认被比较的对象就是消费者的产物**（`filing_contracts._policy_document_hash` = `c773099b…` = 在产 `runtime_policy.json`）。

## B06

| # | 级别 | 复审结论 | 我的复现 | 处置 |
|---|---|---|---|---|
| **B-VR06-01** | **P1** | **期间规则与计划相反**：无 `fiscal_year` 的句柄被判 `verified_input`（`exact` 下 `fiscal_year=None`、以及 `latest_as_of`——正是 filing-fetch **禁止** `fiscal_year` 的模式）；`b06-plan.md` §2/§4 写的是"期间 = fiscal_year 且 (period_end 或 published_date)"、"无 fiscal_year ⇒ blocked + period_missing"；代码与用例断言相反，**变异 M11（把代码改成合规）被该用例杀掉** ⇒ `period_missing` **不可达**，期间那一半标签是空话 | 实测 [b06_period_probe.py](b06_period_probe.py)：`exact` 无 fy ⇒ **没有句柄**（`fiscal_year_mismatch`）；**`latest_as_of` 无 fy ⇒ 服务出句柄且 `fiscal_year=None`**（只有 `published_date`）⇒ 该状态**在真实管线里可达** | ✅ **已修（`3740857`）**：**期间只认期间事实**（`fiscal_year` **或** `fiscal_period`）；`published_date` 是"何时发布"而非"覆盖哪个期间"⇒ 仅凭它 ⇒ `period_missing` ⇒ **`blocked`**。用例**反转为**"只有 published_date ⇒ blocked"并补 `fiscal_period` 正例；**新增端到端用例**（`latest_as_of` 真实服务出的无 fy 句柄 ⇒ `blocked + period_missing`）——**P2-04 的"规则级不可达"因此变成可达** |
| **B-VR06-02** | P2 | "与 `metadata_status` 同一事实"只在**格式良好**的元数据上成立：畸形共享列时读侧**抛异常**（`AttributeError`/`JSONDecodeError`）而 B06 说 `verified_input`；`store=None` 时同样说 `verified_input` | 确认两条 | ✅ **部分已修 + 部分登记**：新增 `qualification.conflict_check`（`"store"` / `"not_available"`）⇒ **不再暗示"检查过"**；我的畸形输入硬化（见 B06 记录）保证**不崩**，但**读侧抛异常**属 B05 读路径的独立缺陷，**登记为后续工作包**（不在本步范围） |
| **B-VR06-03** | P2 | **变异 M6 存活**：整份定向用例集合都无法发现"信封完全忽略缺口规则" | 接受（这正是"用例只测规则函数、没测接线"的后果） | ✅ **已修**：新增 `test_r4b06_an_envelope_labels_a_handle_that_carries_gaps`——用**手搓 `ResolutionResult`**（句柄带 `url_missing` 缺口）驱动 `build_resolution_envelope`，断言信封给出 `preview`+`url_missing`；忽略规则即失败 ⇒ M6 被杀 |
| **B-VR06-04** | P2 | 实施记录把身份/期间/来源三条说成"经真实 `resolve` 可达"，实际是**规则级**，且**管线产不出**（扫描器总会写 ≥1 条实体行；只有真冲突可达）⇒ **F-B01-7 登记的那一半没有触发点**，而 B06 的验收行读起来像"已覆盖" | 接受 | ✅ **已修**：期间那条**现在真的可达**（见上）；身份/来源两条仍是规则级——已在记录里写明，并把 **F-B01-7 的"sidecar/身份"要求**标注为**无可达触发点**（需 F3/F5/F6 侧机制，属范围问题） |
| **B-VR06-05** | P2 | 响应级 `blocked` **对消费者不可见**（`outcome=reused_existing`、bundle available、`capture_ready` 为真 ⇒ 消费者门照样放行），且验收表里**没有 not_verified 标记** | 确认 | ✅ **已登记**：在 [test-acceptance-map.md](../test-acceptance-map.md) 的 B06 行标注**消费者侧许可对齐 = `not_verified`（归 C）**；B06 只提供事实，这一点被写明而非暗示 |
| **B-VR06-06/-07/-08** | P3×3 | `AMBIGUOUS` 未端到端产生；用例数/短语精度；CFG-08 措辞（修前是 `RootSpec.__post_init__` 抛 TypeError，**不是**"存成 falsy None"） | 接受 | ✅ 记录措辞已按实测更正（CFG-08 的说明改为"准入点拒绝"，不再说"存成 None"） |

## B07

| # | 级别 | 复审结论 | 我的复现 | 处置 |
|---|---|---|---|---|
| **B-VR07-01** | **P1** | **合同文字是一句假保证**：我新写的"当请求版本**没有合格副本**时，答案必须是显式失败（missing/not_found）"**不成立**——按 owner 批准的 **S-10 规则 2**，当**没有任何副本通过验证**时，**允许一行凭目录声明被服务**（trace 记 `unverified_<status>_on_pre_b02_canonical`）。复审实测：覆盖已索引文件字节后再解析 ⇒ `reused_exact`、句柄 sha `442ae3b7…` 而与磁盘字节 `82b1519d…` 不符 | 确认：**行为**是 S-10 批准的，**错的是文字**（且该文字的读者正是阶段 C 的适配器实现者） | ✅ **已修（`f2ba5c1`）**：在契约注释里**点名这个例外**（S-10 规则 2、trace 标记、以及"需要验证字节请用 `read_verified_bytes`"），并在 B07 的用例 docstring 里同样注明 —— **保证不再以无条件句出现** |
| **B-VR07-02** | P2 | 未知版本的拒绝**只在一个入口**执行：`read_verified_bytes` 对 `"2.0"` 句柄仍返回 `verified` + 字节；`SourceHandle`/`ResolutionResult` 构造不校验；当前版本结果 + 外来句柄可被接受并原样带出 `"2.0"`；CLI 的只读 ensure 从不构造信封 | 接受（**潜伏**：仓内没有产生者能给外来版本盖章 ⇒ P2 而非 P0） | ✅ **已修**：`read_verified_bytes` 现在先校验 `handle.schema_version` ⇒ 不符返回 `unavailable` + **`unsupported_version`**（命名常量），**不再验证字节**；新增用例。**dataclass 构造层不校验**这一点**登记为潜伏项**（要动 F5 `models.py` 的构造语义，收益低、破坏面大） |
| **B-VR07-03** | P2 | 声明的五值错误模型与实际不符：新拒绝是**裸 `ValueError`**（设计期待 `not_found`/`blocked`），wiki 侧没有"未知版本 ⇒ 五值失败"的映射 | 确认 | ✅ **登记（不改行为）**：`ValueError` 是**调用方/编程错误**（该 API 的误用），五值模型管的是**解析结果**；已在契约注释与本节写明这一区分。**若 owner 要求严格按五值表达**，那是把"内部 API 误用"也变成合同状态，属**另一次范围裁定** |
| **B-VR07-04** | P3 | payload 门**不记录修订**、且只是**单一配置上的字节相等**（复审的 M5"kind-only 复用"变异**存活**）⇒ 它验证的**不是** F8"导出语义不变" | 接受——这正是"可执行化"的边界 | ✅ **已登记**（本节 + [findings.md](../findings.md) F-B07-1 补注）：该门证明的是"**在产配置下 payload 逐字节未变**"，**不是**语义等价；语义面由 B01 的一致性用例覆盖（那一条正是杀 M5 的用例） |
| **B-VR07-05** | P3 | 用例里 `not any("served" in item ...)` **永远为真**（没有任何代码写 "served"）⇒ 假断言 | 确认（我自己写的） | ✅ **已修**：改为"拒绝必须被解释"——断言 trace 非空**且**含版本类原因（`fiscal_year`/`no_canonical`/`rejected`） |
| **B-VR07-06** | P3 | 验收表把 **L12"查询零写"记在 B06/B07 上**，但 B07 **没有** L12 用例（该观察归 B08） | 确认 | ✅ **应在验收表改正**（与本轮 F-B00-6 的点名工作同批）；已在本节登记，表内标注 `L12 → B08（独立观察）` |

## 两个复审共同指出的、我认同的边界

- **消费者侧一律未验**：B06 的资格标签没有任何消费者读它、B07 的适配器转换归 C——两份记录都只签 wiki 侧，**这一点在记录里是明写的**，复审确认没有夸大。
- **全量套件未由复审重跑**（我只允许定向集合）；B06 复审用"1910 = 1900+8+2"的算术**旁证**了我的全量数字，并确认失败两项分别是泄漏 worker 与 CI 已 ignore 的 zr409。
