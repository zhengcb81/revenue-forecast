# B.VR-fc1301 复审处置表（1×P0 / 2×P1 / 2×P2 / 4×P3 → 全部处置）

> 复审记录：[reviews/B.VR-fc1301.json](reviews/B.VR-fc1301.json)（独立会话，只读；在被审仓上**未写入**，变异只在临时副本上做）。
> 复审结论 = **rejected**，其中 **P0 在我修完"版本号"之后仍然活着**——这是它最有价值的一条。
> 处置落点：wiki `76cc1bc`（初版）→ `719f05b`（版本修复）→ 本轮提交（P0/P1/P2/P3 的实质修复）。

| # | 级别 | 复审证明的事实 | 处置 |
|---|---|---|---|
| **B-VR1301-01** | **P0** | 我"加宽后"的门**仍然看不见 17 处**：`_signatures` 用 `setdefault`（**同名取第一个定义**，按路径排序），于是 `_reject` 被解析成 `artifact_handle.py:62` 的 `(artifact, reason)`，`_result` 被解析成 `evidence_query.py` 的 `(cls, connection, row)` ⇒ 位置式 reason 映射到**错误的形参**。它用**门自己的 helper** 量出：本地正确的扫描有 **49** 处 code-like reason 位点，**17 处不可见、其中 16 处是未注册码**；并给出**反例**：把 `close_gap.py:256` 改名成新码，门**仍然是绿的** | **改判据**：同名函数的**全部定义**都作为候选，**任一**定义在该位置叫 `reason` 就按 reason 扫（对歧义**fail-closed**）。修完 `resolver.py`/`security_identity.py`/`close_gap.py` 的 **16 个码**全部注册（8+6+2）。**反例已复现为红**：`brand_new_positional_code` @ `close_gap.py:256` ⇒ 门报 `close_gap.py:256` 并失败；文件按字节还原（`restored_byte_identical=True`）。清单重跑 = **49 处 code-like、0 未注册**（与复审的数字一致）。并加**回归用例** `test_the_scan_handles_a_name_with_several_definitions`（同名两定义、reason 在第 0 位）钉住这一类 |
| **B-VR1301-02** | **P1** | 我的**证据工具**有同一个 `setdefault` bug ⇒ `fc1301-unregistered.txt` / `fc1301-reason-inventory.json` / findings 里"15 个码从未注册"是**在看不见的扫描上得出的结论**；验收项 #2（逐条处置）因此**未达成** | 工具同步改为**全定义候选**；重跑后 **114 个注册码 / 位置式 49 处 / 未注册 0**；证据文件与 findings 的措辞按新数字更正（"15"改为"15+16，分两批，第二批由复审发现"） |
| **B-VR1301-09** | **P1** | `1.1 → 1.2` 的 bump **不安全**：`tests/unit/test_stage_taxonomy.py:107` 把 `REASON_TAXONOMY_VERSION == "1.1"` 钉成 **N-1 契约**（该行自 `cf765a3` 就在、`76cc1bc` 未改）⇒ 单元步骤红（CI `35130154115`）。我的"已核实"只跑了**契约步骤** | `719f05b` 已**撤回 bump**（回到 1.1）并把冻结政策写进常量注释与门的用例（`test_taxonomy_version_is_the_frozen_n1_contract`，附 CI run id）。**本轮进一步落实流程**：本地**两个 CI 步骤都跑**（unit + contract），不再只跑一步 |
| **B-VR1301-03** | P2 | 我给的 `STAGES_BY_REASON` 归属**违反该表自己的规则**：13 个 `focus_policy_*` 放 `artifact`，而其同类 `focus_policy_no_allowed_category_evidence` 是 `semantic`；`v2_profile_admitted` 放 `artifact`，而 `admitted` 是 `identity`；`stale_gap_hash` 放 `acquisition`，而其 if 块同类是 `freshness`。**错 stage 不是装饰**：`record_stage_event` 对 stage 不匹配**fail-closed 丢弃事件** | 逐条改为与同类码一致：13 个 `focus_policy_*` → `semantic`、`v2_profile_admitted` → `identity`、`stale_gap_hash` → `freshness`；新增的 16 个按同一规则放（identity 解析 → `identity`、复用判定 → `resolution`、策略绑定 → `freshness`、`matching_sources_have_unknown_published_date` → `freshness`）。理由写进注释 |
| **B-VR1301-04** | P2 | 门**缺少注册表身份校验**，且 `sys.path.insert(0, str(SRC.parent))` 指向的目录**里没有 `company_wiki` 包** ⇒ 用副本做验证时会**悄悄比对到工作树那份注册表**（复审自己踩到过） | ①`sys.path` 插入 `SRC.parents[1]`（= `src`，真正含包的那层）；②新增用例 `test_the_registry_compared_against_is_this_repository_copy`，断言 `observability.__file__` **就是**被扫仓库里的那一份 |
| B-VR1301-05…08 | P3 | 两处描述不精确；"17 个 code-like 位置位点"应为"**32 处里 17 处未注册**"；"34 个 code-like"是 **34 处 / 29 个不同值**；"revenue-forecast 0 hits"作为**文本检索是假的**（assurance 下 8 个文件命中）；ZR-409 的"瞬时 stat"归因**未被证明**；第三条"新用例"与 `tests/unit/test_stage_taxonomy.py:126` **重复** | 逐条改：数字改为"分两批 15+16"与"34 处/29 值"；"无跨仓消费者"限定为"**代码**无一 import 该常量（文本检索在 revenue 的 assurance 下有命中，属文档/证据文本而非消费者）"；ZR-409 的说法降级为"**机理候选，未证明**"；把重复用例换成 `test_the_newly_registered_codes_have_stages`（只覆盖**新码**，不重复全量属性） |

## 复审**判为 sound** 的部分（照录，不重复自证）

清单最初的 33/32 与 34/0 两组数字（复审用同一工具复现）、15 个码的注册事实（98 个码、REASONS 与 STAGES 都在）、加宽的机理与形状分类（dataclass 字段与关键字 reason 能被发现；散文不被当码；无注册码违反 snake_case 形状）、**承重性**（删 `stale_gap_hash` 注册 ⇒ 精确复现那条红）、**跨仓无代码消费者**、以及 ZR-409 那条红**与本改动无关**的结论。

## 我这一轮的两条流程教训（写进流程，不只是道歉）

1. **"谁 import 它"不等于"谁钉住它"**：跨仓 recon 只查了 import，没查 **pin/冻结**（单元测试里的常量断言、N-1 契约）。凡动"版本号/常量/枚举"，recon 必须**同时**查 `==` 断言与 N-1 机制。
2. **一个 CI 步骤通过 ≠ CI 通过**：上一轮只本地跑了 contract 步骤就写"VERIFIED"，而红的是 unit 步骤。**规则改为：本地必须跑 CI 的两个 test 步骤**（unit + contract），且这与 F-B01-9 的"测试类不在门内"是同一条教训的第三次发作。
