# `B.VR`（B01）复审处置表 —— verdict = `accepted_with_findings`（1×P1 / 3×P2 / 2×P3）

> 复审记录：[reviews/B.VR-b01.json](../reviews/B.VR-b01.json)（独立会话，自行重跑全量/覆盖率/变异，并用**真实 pre-change 树**复核了 F-B01-7 的论证）。
> 处置落地：company-wiki 提交 **`be2e4ed`**（产品 3 文件 + 2 个验收文件）+ 本 run 目录更正。修复前**逐条自证**（见 [b01-review-verify.json](b01-review-verify.json) 与两个变异 harness：[b01_mutations.py](b01_mutations.py)、[b01_x2_agreement_probe.py](b01_x2_agreement_probe.py)）。

| # | 级别 | 复审结论（要点） | 我的复现（**先复现再改**） | 处置 |
|---|---|---|---|---|
| **B-VR01-01** | **P1** | 我冻结的"跨仓 policy hash"是**错的产物**：filing-fetch 消费 `cli._policy_export_payload` = `policy_2x.export_policy_2x`（`c773099b…`），而我冻的是 `policy.export_policy`（`cf0ac2ad…`）。于是"解析器与导出不可能分歧"这句话**对真正要紧的那个导出不成立** | 独立复算：consumer payload hash = `c773099b…`（= 在产 `runtime_policy.json` 值）；两个导出在**在产配置**下可复用集合相同（4 个 root），所以这个混淆**看不出来**；但在"显式声明与 kind 列表冲突"的配置上，把 `policy_2x._effective_reusable_2x` 一行改回 kind-only ⇒ consumer 说"声明 false 的 root **可复用**"（fail-open）且 payload hash 变化，而我原来的 **6 个用例仍全绿** | ✅ **已修（`be2e4ed`）**：验收用例改为**同时冻结两个 hash 并标注各自角色**；新增用例把 **consumer payload 的可复用集合**与**解析器的可观察行为**（服务 / `no_reusable_root_location`）在"冲突配置矩阵"上比对——该变异现在**被杀**。`policy_2x` 的副本仍在（S-3 冻结导出路径，不可删），已登记为**残余**并把"一致性"交给断言而非文字 |
| **B-VR01-02** | P2 | 我写的因果句是**假的**：去掉候选级过滤后变红的是 `test_r4b01_resolver_set_matches_the_exported_policy`，**不是** `test_r4b01_explicit_false_is_not_reusable`（后者根本不进 `_select_candidate`） | 变异 `filter_off`：**只有**集合一致性用例失败（1 failed / 5 passed）——与复审一致 | ✅ **已修**：[findings.md](../findings.md) F-B01-6 与 [b01-implementation.md](b01-implementation.md) §2.1 改为实测口径（并注明原句错在哪） |
| **B-VR01-03** | P2 | 抽样复核 B05 的 P2 修复（B-VR05-04）**过窄**：`_classification` 对 sidecar `document_kind` 做 `casefold`，而我的"声明判定"是**逐字比较** ⇒ `"Annual_Report"` 被判为**派生**，"声明压派生"失效并**制造假冲突 + blocked** | 新用例先红后绿：把 `_DECLARATION_CASEFOLDED` 清空 ⇒ 用例失败（冲突列表多出 2 条）；恢复 ⇒ 通过 | ✅ **已修**：`scanner.py` 的声明比较改为**按列归一化**——`document_kind` 走 `casefold`（镜像分类器），自由文本/日期列仍**逐字**比较（否则文件名派生的值会冒充声明）；新增用例 `test_r4b05_case_variant_declared_kind_is_still_a_declaration` |
| **B-VR01-04** | P2 | "显式声明生效"**依赖配置写法**：准入点接受**带引号的布尔**，`bool("false")` = True ⇒ 声明 `false` 被当作**可复用**（fail-open），且 `"true" is not True` 会让 CFG-05/CFG-07 检查**整条跳过** | 独立复现：`reusable_for_filing: "false"` 被准入，`_effective_reusable` 返回 **True** | ✅ **已修**：准入点新增 **CFG-08**（bool 或 null，否则 `CatalogConfigError`），`read_only` 一并检查；新增用例覆盖两个字段。判定放在**独立函数**里——内联版会把 `config.py` 的棘轮值从 46 顶到 **50**，被棘轮当场抓住（这正是 S-7 要求的"新判定进新函数"） |
| **B-VR01-05** | P3 | `not reusable_root_ids or ...` 这个"空集=不过滤"的逃逸在 `resolve()` 路径上**不可达**（文档级门先拒），但作为**默认值方向是 fail-open** | 代码路径核对：`resolve` 在集合为空时对每个文档记 `no_reusable_root_location`；`_select_candidate` 只被 `_handle` 调用 | ✅ **已修**：**删除逃逸**，成员资格成为硬条件（空集 = 什么都不合格）；新增用例**直接调用**选择器：空集 ⇒ 拒（`placeholder_no_handle`），有集合 ⇒ 服务。变异 `filter_off` 现在**同时杀掉**该用例与集合一致性用例 |
| **B-VR01-06** | P3 | 记录精度：(a) 我把"4 passed"写成复杂度棘轮，而该文件只有 **2** 个用例（4 = 复杂度 + 覆盖率两张表；且跟踪的 `coverage.json` 是**陈旧**的，属 B-VR05-08 的延续）；(b) FC-1001 的 `strict xfail` 接受**任何**失败 | 计数核对：`test_fc1204_complexity_ratchet.py` 确有 2 个 `def test_` | ✅ **已修（记录）**：[b01-implementation.md](b01-implementation.md) §3.2 改为分列（复杂度 2 passed；覆盖率须在**新测量**下才绿）；FC-1001 的标记补 `raises=AssertionError`（见 revenue 提交），使"标记不再能吞掉别的失败类型" |

## 复审未能验证的部分（如实登记）

- revenue 的 **pre-push 门整体**（复审只跑了 FC-1001 单文件：8 passed / 1 xfailed）；我本轮的推送**完整跑过**该门（含真数据套件）= GREEN。
- filing-fetch **端到端**（复审只做代码阅读，无网络）；本步也不声称跨仓端到端。
- 我探针里的两行"`sidecar_suffixes`"场景（复审未复跑）；该场景只用于 F-B01-7 的根因论证，结论不依赖它。
- 泄漏 worker（PID 17684）"清理后即过"的主张三：复审拒绝在未杀死该进程的情况下下结论（我只在 F-B01-7 记录里说过"清理后通过"，措辞已按此收紧）。
- **并发干扰（我造成的，如实记）**：复审测量期间我在**独立 worktree** 里跑了一次全量套件（PID 29016 等并非其进程），其报告中第二条失败（`test_zr409…::test_c2_journey_dayu_only_real_sample`，单独跑通过）**很可能**由此并发导致。教训：worktree 隔离的是**代码**，不是**机器资源**；下一步起，复审期间不在同一台机器上并行跑全量套件。
