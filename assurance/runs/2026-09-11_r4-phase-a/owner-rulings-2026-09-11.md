# Owner 裁定记录（2026-09-11，R4 阶段 A / G2）

> 背景：A.DR（独立设计复审）三轮的意见里，有 **6 项不是文字问题、而是"要不要改产品行为"的方向选择**。复审明确要求：**先由 owner 裁定，再冻结 A02 合同**。
> 本页用大白话记录裁定内容与后续动作，供后续阶段（B/C）直接引用；技术细节见 [root-contract.md](root-contract.md) R7/R8 与 [identity-contract.md](identity-contract.md) R4/R6。
> **授权与范围**：owner 2026-09-11 回复"按你建议办"（对下列 6 条建议逐条采纳）。本裁定**只决定方向与登记整改项**，**不授权现在修改产品代码**；任何代码改动仍须按 R4 第 2.5 节先批准精确工作包。

## 裁定一览

| # | 问题（大白话） | 现状（代码事实） | **owner 裁定** | 落到哪里 |
|---|---|---|---|---|
| **R-1** | 配置写了"遇到符号链接就拒绝"，但代码从不读这一行 → 假的安全感 | `symlink_policy` 只被解析/默认化（`config.py:79/140`、`models.py:101`、`policy_2x.py:39/164`），在 resolver/service/scanner/store/reader 与整个 `src` 内**无任何读取点**；仓库内另有 5 处独立 `is_symlink()` 判断，但都不看该字段。**同类还有 `read_only`**（A-VR-06：无读取点，写轴实际由 `kind == 'company_raw'` 决定，`canonical_writer.py:126-131/284-287`） | **按"假保证字段"处置**：从合同的"已强制"清单剔除（已做），并登记为整改项——**要么实现真实检查（让现有 5 处判断读同一政策），要么删除该字段**。倾向**删除**（避免继续误导），实现成本另评。**v0.4.1：`read_only` 按同一标准追加登记** | root-contract R7/§5；B/C 整改登记 |
| **R-2** | 配置写 `reusable_for_filing: false` 表示"不要复用"，但**写了也不生效** | 复用判定只看 `root.kind ∈ reusable_root_kinds`（`resolver.py:782-786`/`:933-940`），从不读该字段 → 显式 `false` 无法关闭复用（fail-open） | **让 `false` 真的生效**（显式关闭必须被尊重，属 fail-closed 方向）；`None` 仍表示"跟随 kind 政策" | root-contract C4/§5；B/C 整改登记（**优先级高**） |
| **R-3** | 同一份 YAML 有**两套准入检查**，规则相反 | 生效的 `config.py` 把 `canonical_write_target` 当未知字段**拒绝**（`:75-84`）；`policy_2x.py:49/:121-131` 却实现了写目标校验（loader 真实调用仅 `policy_3x.py:95` + 3 个测试文件） | **以生效的 `config.py` 为唯一来源**，停用没有生产调用者的那套；`canonical_write_target` 字段的去留随之决定（当前实际不可用 → 若近期无需求，建议**暂不引入**，需要时在 `config.py` 里正式实现） | root-contract R8；B/C 整改登记 |
| | | ⚠️ **范围更正（2026-09-12，三份独立复审 P0：B-DR-01 / A-AR-05 / A-VR-05）** | **R-3 的适用范围 = 仅"准入 loader"**（`load_root_policy_2x`）。**`export_policy_2x` 是在产的**（`cli.py:835/849-851`，由 `:811` ensure / `:831` policy-export / `:1182` resolve 调用），且是 filing-fetch **FC-501 containment / ZR-405 policy_hash 的唯一来源**（`filing_contracts.py:450/461-497`）——**不得按 R-3 停用**。本页 v1 曾把它与 loader 混为一谈，已收窄。**若 owner 希望连导出路径一并收敛，属新裁定**，需附跨仓 policy_hash 迁移方案 | root-contract R8 第 2 条 |
| **R-4** | 配置不写"隐私级别"时默认"公开"，即**默认允许外发到外部 AI** | `privacy_class` 默认 `"public"`（`models.py:105`）；LLM 出口按该字段构造白名单（`llm_summarizer.py:333-337`） | **改为默认不外发**：缺省值取"仅内部"，要外发必须**显式**声明公开（新 root 一律显式声明） | root-contract §5；B/C 整改登记（**优先级高**） |
| | | ⚠️ **范围扩大（2026-09-12，A.VR-04）** | 整改范围须包含**无门的正文外发**：`company_wiki/src/company_wiki/legacy_research_ingest.py:128-136`（`content[:8000]` → `self._llm.generate`，**不读 privacy_class、不查 receipt、不做字节绑定**）。这是独立于 `worker` 的**第二条 LLM 出口且完全无门**；须在 A06/L10 增加负例（A.VR 的 VR-N21） | operation-contract §2.3 第 0 条 |
| **R-5** | 规则"公司改名后旧引用必须还能解析"没有负责人 | A04 R6 只有规范句，无 owner/机制/存储/负例 | **指派 owner**：`identity-enrichment`（断言路径）+ `security_identity`（证券主数据/别名刷新）作为共同负责人；机制=**追加式**映射（不覆盖），存储位置在 VR 阶段用隔离副本核清 | identity-contract §2 R6、§5 问题 2 |
| **R-6** | 规则"路径不能决定身份"，但代码**确实**用"路径+优先级"决定哪份算正本（**计数口径已核对，2026-09-12**：本行 v1 写"9 处"但实际枚举 **11 个锚点**；A 侧 [identity-contract](identity-contract.md) §1 另列 **13 个点**——差异来自"是否把 canonical 选择键与路径过滤计入"，两处已各自注明） | 规范位/取值顺序由 `(root_priority, root_id, relative_path, location_id)` 决定：`service.py:329/:527/:643-653/:772`、`canonical_writer.py:287`、`duplicate_cleanup.py:210/:486`、`normalizer.py:1600/:1892`、`llm_summarizer.py:371`、`evidence_query.py:269` | **认作"需要整改"**：R4 保持为**目标**（不是现状），9 处登记进 B/C 的整改与验收范围；**不要求**现在改代码 | identity-contract §1 R4、§5 问题 1；B/C 整改登记 |

## 后续动作（已登记，未执行）

1. **A02 可以封版**：本页即 G2 的裁定依据；A02 合同（root-contract v0.4.1）按上表定稿，不再挂"待 owner 裁定"。**R-3 的范围以本页的范围更正为准（只含准入 loader）**；若 owner 要一并收敛导出路径，需新裁定。
2. **仍未完成、且不属于本裁定的**：A05 真实语料样本清单（G7）、隔离副本（G8）、操作员级独立边界观测与 reviewer 指派原件（G5/G6）。
2. **B/C 整改清单**（按优先级，v0.4.1 更新）：
   - 高：R-2（显式 `false` 生效——**落点三处**：`resolver.py:782-786`/`:933-940`、`policy.py:67-72`、`policy_2x.py:308-312`（第三处在在产导出路径内，**不可删**，只能**对齐语义**，且其输出变化须与跨仓 policy_hash 迁移绑定））、R-4（默认不外发 **+ `legacy_research_ingest.py:128-136` 的无门出口**）；
   - 中：R-3（**仅**准入 loader 收敛为一套；导出路径不在内）、R-1（假保证字段处置：`symlink_policy` **与 `read_only`**）；
   - 线：R-6（路径不入身份投影，**11 个排序锚点**；identity-contract §1 记 13 个点，口径差异已注明）、R-5（R6 的存储与负例在 VR 中核清）。
3. **三份独立复审的结论（2026-09-12）**：A07 = `accepted_with_findings`（11 项，含 22 条负例与 5 值错误模型）、A08 = `rejected`（映射已产出，13 行无法指派）、B.DR = `rejected`（20 项，含上述 P0）。→ 合同已就地更正为各 v0.4.1，B 设计需按其 P1 全面重做后送 rev2 复审。

## 边界

- 本页只记录**方向与登记**：未改产品代码/配置/DB/任务/worker，未执行数据命令，未下载/外发。
- 三个仓库当晚的推送均走各自强制 gate 且 CI 全绿；gate 的 real-data 套件会**只读**打开生产 catalog（该事实已在 [boundary-audit.md](boundary-audit.md) 归因并披露）。
