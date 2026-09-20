# review.md — I-05-A / a20260919-01

> ## PENDING independent review
> **本文件由实现者撰写，不构成任何验收结论。** 实现者未自签 `accepted`、未写 `passed`。
> 独立 reviewer 必须自己重算至少一个专属 oracle，并攻击文末列出的案例。
>
> **r4（2026-09-19，第三次复审后）：答案仍是 changes_required（P1-A/B/C，单根因）。**
> 已按复审指定的最小修法修复；红→绿变异证据、复核性数字更正、旧 RED 字节缺口登记见
> 同目录 eview_r4_disposition.md\（并见 \evidence/README.md\、\evidence/p1-mutations.json\）。
> 产品仓仍为**零改动**，状态保持 eview_pending\，实现者未自签任何 accepted。
> **r2（2026-09-19，复审后）：复审结论 `changes_required`（F-I05A-01..09）已逐条处置。**
> 逐条 file:line、新 raw rc 与新哈希见同目录 `review_r2_disposition.md`；本节 §1–§5 保留
> r1 的原始自述**不改写**，其"同一把门"等表述已在 r2 disposition 中更正与限定。
> 状态仍为 `review_pending`（实现者不自签）。

- card: I-05-A（parent I-05），attempt `a20260919-01`
- 状态：`review_pending`
- 实现者：本 attempt；reviewer：RF reviewer（另会话）

## 1. 我实际做了什么（可核对清单）

1. 建立隔离环境：`iso/venv`（从 I-00-A 模板解释器复制；`Scripts/python.exe` sha256 `0e818a1f…42cd` 与模板一致）、
   `iso/cw/src`（company-wiki `src/` 完整副本）、`iso/cw/tests`（产品合同测试副本）。
2. 冻结样本：`samples/annual_normalized.md`（1233 B，sha256 `f878cb59…1dcf`），含释义 / 主营业务 / 经营讨论
   三个明确区块；`samples/annual_source.txt`（sha256 `b70346ce…4513`）作为 `source_sha256` 绑定来源。
3. 冻结 oracle（`oracle.md`，在任何被测调用前成文，含原因码表与 3.1.2 的自我纠错披露）。
4. 修改前 RED（`before/`）：用**真实** `extract_sections_catalog` + `summarize_catalog` 产出工件，
   再逐项独立变异；实测 8/8 个变异仍被当普通可用结果返回（`reason_reported=null`）。
5. 最小修改（attempt 内 `iso/cw/src`，仅两文件）：
   - `section_query.py`：`list_sections` 走 `artifact_handle.validate_artifact`（同一把门）+ 索引内容/切片长度/span 归属校验；
     拒绝时抛 `SectionQueryQualificationError(reason, next_action)`；行选择加 `ORDER BY created_at DESC, artifact_id DESC`。
   - `section_extractor.py`：`LEFT JOIN artifacts sec … AND sec.status='completed'`（原为任意行即算"已有"）。
6. 修改后 GREEN（`after/`）：同一 harness 同一攻击面全部转为预期拒绝/预期通过。
7. 隔离回归：`iso/cw` 下 5 个合同测试文件 **63 passed / 1 deselected**（deselected 测试在**原始**字节上同样失败，
   见 `before/cmd-tests-pristine.stdout.txt`：该测试需要真实 PDF parser，本 venv 无 PyMuPDF/docling）。
8. 生产仓零写入：`after/prod-anchor-hashes-after.json` 与 `before/prod-porcelain-before.json` /
   `after/prod-porcelain-after.json` 对比；CW 只有卡片声明的两个 pre-existing 修改。

## 2. 正例 / 负例逐条预期与实际

| case | 冻结预期 | before（原始字节） | after（本 attempt 修复） | 证据 |
|---|---|---|---|---|
| c0 正例 | 可用；2 个切片；标题 `[公司业务概要, 经营情况讨论与分析]`；索引 hash == 行 hash；span 全部存在 | PASS | PASS | `*/case_results.json.c0` |
| c1 `status='failed'` | `sections_status_not_completed`，不返回内容 | counterexample（返回可用内容） | PASS | `*/artifact-mutation-matrix.json` |
| c2 缺 `schema_version` | `sections_binding_error` | counterexample | PASS | 同上 |
| c3 `source_sha256='0'*64` | `sections_binding_error` | counterexample | PASS | 同上 |
| c4 删除索引文件 | `sections_file_missing` | counterexample | PASS | 同上 |
| c5 改写索引但不更新行 hash | `sections_binding_error` | counterexample | PASS | 同上 |
| c6 `created_at='2099-…'` | `sections_binding_error` | counterexample | PASS | 同上 |
| c7 索引改写为不存在的 span_id **且同步更新行 hash** | `sections_span_unbound` | counterexample | PASS | 同上 |
| c8 删除 `evidence_spans` 行 | `sections_span_unbound` | counterexample | PASS | 同上 |
| n2a 只有 failed sections 行 | 重算必须发生（`completed>=1`），消费者返回新建的合格行 | counterexample（`completed=0`） | PASS | `*/case_results.json.n2.subcases.n2a` |
| n2b 只有旧版本 completed 行 | **observation（未修）**：仍被算作"已完成" | observation | observation | 同上 |
| n2c 当前版本 completed 行 | 控制：不重算（`completed==0`）且仍可读 | PASS | PASS | 同上 |
| p2 无 summary 行 | sections 仍可用；summary 不伪造；`absent_roles=[consumer_analysis, markdown, summary]` | PASS | PASS | `*/case_results.json.p2` |
| n3 两条同 role 行 | 不得返回旧行内容（`STALE-OLD-VERSION`） | counterexample（**返回了旧内容**） | PASS | `*/case_results.json.n3` |

## 3. 独立复算（我不会用它替代 reviewer 的复算）

- `before/independent-slice-check.json` / `after/independent-slice-check.json`：脚本**不 import company_wiki**，
  从样本文本手工定位偏移（producer 坐标系起点 259），核对 `char_start/char_end` = 108/207、207/339，
  切片文件长度 == span 长度，内容 strip 换行后 == 独立切片；索引 sha256 重算 `141f176b…fe3c` == artifact 行。
- `before/legacy-section-probe.json`：历史最小 fixture 复现"failed 行 + 不存在索引/span 被当普通结果返回"。
- `after/legacy-section-probe.json`：同一脚本在修复后 `blocked_by_fixture_schema`——**不是**修复的正面证明，
  只是"最小历史 fixture 无法表达新门"的如实记录；正面证明来自真实 catalog case。

## 4. 已知局限 / 未验证（如实列出）

1. **`normalized` 步骤的偏差**：真实 sections/summary producer 已运行；`normalized` 行的**输入字节**是按
   `normalizer` 写盘形状构造的（本机无 PDF parser 依赖）。见 `oracle.md` §1.2 与 handoff open questions。
2. **c0 期望常数的一次修正**：冻结时误以为治理章节也会产出切片（写 3，实测 2），在写入最终 `before` 证据前改为 2。
   完整披露见 `oracle.md` §3.1.2；reviewer 若判定这构成事后贴合，可给 `changes_required`。
3. **D-W05 未签**：五个 OPEN 项未实施（`decision.md`）。本 attempt 只做了 FROZEN-1/2 两项，理由见 decision §0。
4. **c4 的原因码映射**：`artifact_file_missing` → `sections_file_missing`。这是本 attempt 的命名选择，
   reviewer 可要求改用校验器原始 reason。
5. **`as_of_date=""`**：本 attempt 不把 `documents.published_date` 传作 `as_of_date`。
   理由：该门是 `as_of > now[:10]`，用**发布日**比较会让"审计当天尚未发布"的文档被拒；实测触发过。
   这是行为决策，**未被 D-W05 冻结**，reviewer 应重点复核（见 §5 attack 3）。
6. **n2b 未修**：旧 generator 版本的 completed 行仍被算作"已完成"。这是有意的范围限制，不是遗漏。
7. **生产规模未测**：全部 case 都是单文档 scratch catalog；对 25.7M 行/49.7 GB 生产库的性能与并发未测。

## 5. reviewer 请优先攻击

1. **c7 是否真的只能由 span 检查拦下**：请独立构造"索引与行 hash 一致、切片文件长度一致、但 span 属于另一个
   document_id"的案例（本 attempt 的 c7/c8 只覆盖"不存在"，未覆盖"存在但属于别的文档"）。
2. **`_derived_root` 反推**（`section_query.py`）：把索引放在 `<catalog>/derived` 之外但仍自洽的路径上，
   验证是否 fail-closed，并判断错误原因是否误导（`artifact_path_outside_allowed_root`）。
3. **`as_of_date=""` 决策**：构造 published_date 在未来、但 created_at 合法的工件，判断拒绝/放行哪个才是正确语义。
4. **n3 的选择规则**：把两条行的 `created_at` 设为相同、artifact_id 逆序，验证 `ORDER BY created_at DESC, artifact_id DESC`
   仍确定；再构造"新行是 failed、旧行是 completed"，判断该返回哪一行（本 attempt 未冻结此情形）。
5. **n2a 的重算范围**：验证 `status='completed'` 过滤是否会让"partial"状态的 sections 行被无限重算或永不重算。
6. **c0 常数修正**：判断 §3.1.2 的自我披露是否足以接受，或应记为 `changes_required`。
7. **B10 ratchet 的诚实性**：确认 `section_query.py` 的 parse 站点仍落在 `list_sections` 内、
   `_qualification_failure` 不再触碰该列（本 attempt 因此**没有**改 `read_chain.py` 的基线表）。

---

# r5 — 独立复审（第四轮）裁决转录（**载体落定，非实现者自签**）

以下裁决正文由独立 reviewer 撰写、经父 agent 授权转录；转录方式为**逐字节追加**，
不改写本文件既有字节。来源报告卡内副本：`evidence/I-05-A/reviewer_report_r4.md`。

<!-- BEGIN REVIEWER VERDICT (verbatim, byte-exact) -->
## ④ 可粘贴进 `review.md` 的裁决正文

> **独立复审（第四轮）结论：`accepted_scoped`。**
> 第三轮的 P1-A/P1-B/P1-C（同一根因：记录偏移从未与内容强制比对）经我独立复算确认**已关闭**。
> **证据（我方自建树，非采信自述）**：修复前字节 `iso/prefix_r3/section_query.py = 5fbbe49a…cac1` 上，I1（双偏移 +2）、I2（+5）、I3（`normalized` 全部 `failed`）三例均 `returned`（`substring_only`/`no_source` 当时是**通过**标签）；修复后 `iso/fixed/section_query.py = 06a1a6ea…ebceb7` 上同一批注入分别被 `sections_binding_error`×2 与 `sections_no_normalized_source` 拒绝。
> **per-origin 强制**：我另造三类注入——①只把**第二条**偏移 +3（第一条不动）；②偏移 +1 **且**内容同时平移一位；③把切片替换为**行内**（非行边界）等长片段——三者全部被拒；接受路径上不再出现 `substring_only`/`no_source`（我逐例核对：所有 `returned` 用例的每个条目 `window_match == "source_window"`）。无窗口对齐约束时差一 origin 会吸收伪造偏移，该约束确属判据的一部分。
> **fail-closed**：`normalized` 行置 `failed` 与整行删除两种注入都得到新原因码 `sections_no_normalized_source`，不再以 `no_source` 放行。
> **未过度收紧**：`c0` 正例（含前导/尾随换行、跨行切片）两片 `source_window`、`window_positions=[0,1]`；25 例套件 `25 passed` rc=0；7 文件隔离回归 `88 passed, 1 deselected` rc=0（含 b10 读链与复杂度 ratchet）；`section_query.py` 最高函数复杂度按仓库自带度量 **11 ≤ 冻结 12**（r2=10、prefix_r3=9）。
> **记录与留痕**：C14 已改为"18 passed (r2, superseded) / measured_now 25 passed"，原值保留在 `declared_r2`；`evidence/p1-mutations.json` 记录了 pre/post 两次查询的 `module_sha256` 断言（`5fbbe49a…` → `06a1a6ea…`）；`changes.diff` 860 行仅两文件；探针 9/11 拒绝（m6 回退旧 VALID 行、m5 死锁不计）。`oracle.md` 仅追加附录 C（我以字节前缀比对证明 `r4[:23204] == r3 全文`，正文与附录 A/B 一字未改），C 内明确宣告 B.1/B.2 的相关表述过时。旧 RED 字节（r2 阶段 `3 failed / 15 passed`）确已因 A2 重跑覆盖而丢失，**如实登记为不可复算缺口且未补造**（oracle C.4 + handoff + disposition §r4.6），`iso/prefix_r3/` 冻结保留。
> **生产与门**：CW HEAD 未变、porcelain 仍仅两行、13/13 锚点匹配；RF 自 `7d7ea1ed` 起的三段提交（8702/7420/0 文件）**均无非 `.planning/` 路径**，本卡 porcelain 无非 `.planning` 增删；filing-fetch porcelain 空；`PLAN\reviews` 目录 mtime 与最新文件 mtime 均停在 2026-09-19，**无 ≥2026-09-20 02:00 的文件**；状态 `review_pending`（未自签）；`section_extractor` 仍无版本比较，D-W05 OPEN-1..7 保持未签，I-05-B/C 不得据此开工。
> **已披露边界（不阻塞，供消费方注意）**：①偏移 +1 且内容不变的声明仍可被解释为另一个合法 origin（文本完全相同，非内容旁路），故 `char_start` 不应被当作精确索引；②`role/title` 不参与绑定校验（我构造的 `roleswap2` 会把另一节文本以本节的 role/title 服务），这是设计边界而非本次缺陷。
> **遗留 P3（不阻塞，建议随下一卡追加更正）**：oracle 附录 C 的前像字节数 14924 B 有误（实测 r3 末态 23204 B，且追加性已由前缀比对独立证明）；`after/prod-anchor-hashes-after.json.attempt_fixed` 由 r3 的三元组变为 `null`；`evidence/p1-mutations.json` 键名 `I1_offsets_plus_one` 对应 `delta=2`；`binding.json` 仍记旧 RF HEAD `7d7ea1ed…`（live `cc78c529…`，影响为零）。

<!-- END REVIEWER VERDICT -->
