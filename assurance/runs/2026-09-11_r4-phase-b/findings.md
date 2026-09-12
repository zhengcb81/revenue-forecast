# R4 Phase B 发现（findings）

> 本文件在 B 设计阶段只记录**从阶段 A 继承的事实**与**设计期发现**；产品实测结果一律留待 B08/B.VR。

## F-B01-1：`B.DR` 独立设计审查 = **rejected**（1×P0 + 7×P1 + 9×P2 + 3×P3）→ 本版 v0.1.1 逐条更正

审查记录 [reviews/B.DR.json](reviews/B.DR.json)（reviewer session `7ad6f0f0-…`，非作者会话；17 条 claim_checks 中 **8 条未复现**）。**未复现的声明是最有价值的部分**——它证明"文档写了"≠"事实成立"。

| 发现 | 严重度 | 事实（已由作者复核） | v0.1.1 处置 |
|---|---|---|---|
| **B-DR-01** | **P0** | `policy_2x.py` **并非整体无生产调用者**：`cli.py:835` `_policy_export_payload` → `:849-851 export_policy_2x(config)`，由 `:811`（ensure）/`:831`（policy-export）/`:1182`（**resolve**）调用；其 payload 是 filing-fetch **FC-501 containment / ZR-405 policy_hash 唯一来源**（`filing_contracts.py:450/461-497`）。v0.1 据此把它列为"可停用/禁改"是错的。**同一 P0 亦被 A.AR-05 与 A.VR-05 独立命中** | [b-design](b-design.md) P-4 与 §B07 范围表、[file-scope](file-scope.md) §2 首行改为"**在产、字节/hash 契约冻结、不得按 R-3 停用**"；A 侧 root-contract 更正为 v0.4.1 并把 R-3 范围收窄为**仅准入 loader** |
| B-DR-02 | P1 | B01 的"旧字段版本映射"**交付物缺失**，而 task_plan/test-map 已声明完成 → gate 第一项无审查对象 | [b-design §B01.2](b-design.md) 补齐 **14 字段映射表**（含迁移条件），并要求产出 `field-owner-map.json` |
| B-DR-03 | P1 | B05 只盯 `metadata_json` 不够：`scanner.py:1078-1081` 的 UPDATE 还由 priority 胜出者写 `title/source_type/document_kind/published_date/source_status/primary_source_id`，开关在 `:1038` | §B05 改为**覆盖整条 UPDATE 的全部列**；并删除"完全移除 priority"的过强表述 |
| B-DR-04 | P1 | B02/B04 漏了 **`resolver._handle`（`:1142-1224`）**：`:1153-1165` 二次 canonical 过滤 + `:1166 is_file()` 才是"撤首选→自动切换"的落点 | §B02 明确**两处同改**（`service._annotate_locations` + `resolver._handle`）；file-scope F2 补锚点 |
| B-DR-05 | P1 | B07 的"无 companies fallback"实现在**禁止仓**（`filing_contracts.py:485-486`），且 `adapters/*`、`adapter_dispatch.py`、`cli.py` 未分类 | §B07 新增**范围重划表**：B 只保证"不新增 fallback + 合同显式声明"；消费者侧实现**归 C**；`cli.py:835-857` 冻结、adapters 列 forbidden |
| B-DR-06 | P1 | `.rejections`"只标记不屏蔽"与风险文件"拒绝在排序之前"**自相矛盾**，且无测试 ID 承接 | §B02 第 2 段改为**保持排除语义**（`.rejections` 属资格段）；风险文件同步更正；验收挂 L04 |
| B-DR-07 | P1 | B03 只在打开时校验 → **TOCTOU 未闭合**（Windows 共享模式只在打开时裁决） | §B03 改为"**读后对实际返回字节复验**"，并把"仅打开时校验"列为禁止 |
| B-DR-08 | P1 | B02 第 3 段"查询期真读字节"可能触发**云占位 hydration**（`dropbox_stock`），违反 A03 R3/P-5 与 L01"零网络" | §B02 第 3 段加硬约束：**资格判定不得联网**；需 hydration 的候选一律 `unavailable` |
| B-DR-09~17 | P2 ×9 | ① F1–F8"逐一等于 A01 §0"不成立（`reader.py` 非 A01 冻结项）；② F8 的"行号 `:1-3384`"实为字节数；③ **已存在两处活 `_effective_reusable`**，只禁"新增"不够；④ B05 的 provenance 落点/持久化未定（需 `store.py`）；⑤ owner R-6 的 5 个同型排序文件未分类；⑥ preview/verified_input **无承载接口**；⑦ R-1/R-2/R-4 未绑定测试 ID；⑧ `--verify-only` 只锚定运行时 HEAD、`reviewed_commit` 不校验、`reviews/**` 不在账内；⑨ "未执行任何 CLI"纯自述 | ① file-scope §5 逐行标注；② F8 改为符号锚点 + "共 86 行"；③ §B01 改为"收敛现存两处、不得出现第三处"；④ §B05 决定**B 只在读取合同输出 provenance、不落库**（持久化升级为独立工作包）；⑤ file-scope §3 给出 9 处的 allowed/forbidden 分类；⑥ §B06 明确 preview 合同归 B06 并须给出承载字段/命令；⑦ test-map §1b 新增**裁定↔测试绑定表**；⑧ checkpoint 生成器改为报告 `source_revision`/`head_revision` 并显式列出 `does_not_prove`，且 `reviews/**` 纳入清单；⑨ checkpoint 的副作用字段改为**如实披露**（`-shm` 由本次推送的 gate 触碰） |
| B-DR-18~20 | P3 ×3 | ① handbook 无"§2.5"（正确为 §1 第 5 项 + §3）；② 变更记录时间"23:3x"与实际（07:43–07:46）不符；③ 反覆盖表把 O03 标"不属 B"却承认交叉，L06/L11 阶段列与矩阵不符 | 风险文件 §5 + test-map §2 就地更正；变更记录改真实时间 |

- **教训（已写入 risk-and-stop-rules §4）**：把"某个符号无调用者"提升为"某个模块/路径无调用者"必须**重追 caller**——本轮 P0 正是这样产生的。
- **状态**：v0.1.1 已就地更正；按 B.DR 的要求，**需由另一名独立 reviewer 出 `B.DR-rev2`**，且 rev2 必须基于**新的冻结提交与新的输入哈希集**。

## F-B00-1：B 的三个改动热点全部落在阶段 A 已实测的"残留"上，不是凭空设计

- 证据（阶段 A 实测，含行号与哈希）：
  - **候选选择"先 canonical 后筛"**：`resolver.py:912-921` 在 `is_canonical` 上过滤，而 `is_canonical` 由 `service.py:643-653` 的 `(root_priority, root_id, relative_path, location_id)` 排序取 `ordered[0]` 决定 → 未被选中的同版本副本在查询早期即被屏蔽。
  - **metadata 真伪由 priority 决定**：`scanner.py:1007-1081`，关键比较 `:1038`。
  - **复用判定不读显式声明**：`resolver.py:782-786`/`:933-940` 只看 `root.kind`（owner 裁定 R-2 要求 `false` 生效）。
- 影响：B02/B05 是**同一根因**（"位置/优先级被当成业务判据"）在两个层面的表现；B 的整改应**一次收敛**，避免打补丁式两处各改一半。

## F-B00-2：owner 裁定把"改不改"与"怎么改"分开了，B 因此可以在不碰代码的前提下完成设计

- 证据：[owner-rulings-2026-09-11.md](../2026-09-11_r4-phase-a/owner-rulings-2026-09-11.md) 六条全部是"方向 + 登记"，且明示"不授权现在修改产品代码"。
- 影响：B 的实施入口是 **owner 批准 [file-scope.md](file-scope.md)**（DEV 工作包 + 文件范围），而不是本次对话里的"接着做"。设计可以连续推进，代码不能。

## F-B00-3：B08/B09 的硬前置是**隔离副本**，而隔离副本不必是 49.7 GB 的拷贝

- 证据：矩阵 L01–L12 的机制层可用"新建小 catalog + 既有测试的 tmp-catalog 机制"覆盖（wiki 既有测试即如此运行，见 [a06-baseline-plan.md](../2026-09-11_r4-phase-a/a06-baseline-plan.md) §1 盘点）；只有"真实四 root 端到端读取"（B09/L02/L09/L12 的 R1 层）需要真实字节。
- 影响：**G8 可分两级**——① 机制层隔离目录（成本低，可立即建，只需 owner 同意"允许在非生产路径创建目录"）；② 真实字节读取（需要在隔离根下引用真实文件，**只读**）。把 G8 当成"复制 50 GB"会无谓阻塞 B08。

## F-B00-4：B 的"零副作用"证明不能靠作者声明（阶段 A 的教训）

- 证据：阶段 A 的 [boundary-audit.md](../2026-09-11_r4-phase-a/boundary-audit.md) —— `-shm` mtime 不是可靠的"未开库"判据（本机至少三类合法开库动作），且作者自证不构成独立证据。
- 影响：B08 的"独立文件/OS 观察"必须由**独立 reviewer**执行并记录**方法**（观察什么、怎么观察、看到什么），作者只提供被观察对象。

## F-B00-5：设计期就能排除的一个错误方向——"用 priority 排序就不会有问题"

- 证据：矩阵 L08 明确要求"swap priority/scan order 不改变业务元数据"；执行计划 §B05 明确"不以 priority 决定真伪"。
- 影响：B02 第 4 段保留 `priority` **只作排序**，B05 把 priority 从 metadata 真伪判定中**完全移除**；任何"给 priority 更高的权重让它更权威"的方案都直接违反验收。
