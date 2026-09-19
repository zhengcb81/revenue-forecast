# I-03-B review.md — 独立 reviewer 复核（a20260919-01）

- Reviewer：独立 reviewer（非实施者，filing 侧）；日期：2026-09-19。
- 权限：只读三仓 + iso venv 重跑；除本 review.md 外零写入（重跑临时输出已即时删除，attempt 目录恢复原状）。
- **结论：accepted_scoped**。

## 1. 重跑结果（iso venv，-X utf8 -B，cwd=attempt）

- `scripts\w03b_cases.py iso/override/gap_plan.py` → **rc=0，21/21 pass**（C01—C14 planner 面、HASH-D6、三市场 6 场景全 pass），与本 attempt `after/w03b-after.json` 一致。
- `iso/pre/pre_fix_assertions.py iso/baseline/gap_plan.py` → rc=0，**G-B1..G-B5c 全部 fail**（RED 满覆盖），与 `before/pre_fix_assertions.json` 一致。
- 抽验 G-B1（字典序核心缺陷）：baseline 下 `newer_revision_ids` actual=[] 且 `not_published` actual=true——旧实现 `max(accession 字典序)` 把 z-old（filed 2026-03-01）当最新，a-new（filed 2026-04-01）被无视，gap 虚假关闭；与 I-03-A probe `newer_date_lower_id` 完全同构。G-B2 反向（newer_revision=[z-old]）、G-B3 双候选齐入 missing + 逆序不等价，均复现。
- 远端逆序 gap_hash：修后 C01/C03/C04 `reverse_order_equivalent` pass；HASH-D6 `hash_order_independent` pass。reviewer 保留案例（全新 id/roots：m-root-77/q-doc-3，G-B1+G-B2 双向重放 + 逆序 hash 等价）独立验证 **PASS**。
- future：G-B4 修后 future=[a-future]、missing=[]、不进任何可下载/可复用当期集合，pass。

## 2. 逐核对点

1. **重跑/抽验**：见 §1，全部复现。
2. **纯选择面对齐 I-03-A**：C14 以 planner 面 missing 排序（period_start DESC：miss-p1→p2→p3）实现，批次事务语义明确声明归 I-03-C；C15 在 oracle.md 复用表显式标 `out_of_scope(I-03-C)`、不做截断断言——无越权。抽算五格与 I-03-A 冻结输出逐值一致：C07（period_key=`annual_report|unknown|unknown`、不入 missing、显式 unknown 桶）、C08（unknown_missing_date、不参与新近/不进 missing）、C09（conflicting、不 actionable）、C10（unknown_empty_success、not_published=false、no_gap 计划级 true）、C13（future 桶、保守 not_published=false）。
3. **changes.diff / override 源码**：diff 仅覆盖 `iso/baseline/gap_plan.py → iso/override/gap_plan.py` 单文件；grep 复核 override 内 accession/`_candidate_id` 仅出现在 `_sort_key`（D6 哈希确定性 tiebreak）与 `_batch_key` 尾位 tiebreak，**新近性判定路径（`_newest_remote`：filed_at 分箱→max 日期→`_same_day_state` 修订链）无任何字典序**；旧 L167-170 max 字典序与 L228-242 hash 同源排序确认删除。period 键三元组 `kind|period_start|period_end` 落地（缺任一→explicit_unknown，不从 fiscal_year 反推，无默认日期）；`capture_ready=False` 进 `unusable_local` 显式桶不可复用（B5a 实测）；三市场样本字段来源均有 `field_source_simulation` 声明，无 fixture 修补。
4. **修前断言真实性**：文件 mtime 序为 pre_fix_assertions.py 18:06:27 → before JSON 18:06:34 → override 18:12:15，断言先于修复存在；断言全部为固定字面量 expected（id/状态/桶名），不从被测排序函数计算。
5. **生产未触碰**：`git status --porcelain src/company_wiki/source_catalog/` 空（rc=0）；生产 gap_plan.py 实测 sha256 = `d18391b7…907c79f` 与卡内锚点及 binding 输入 hash 一致；iso/baseline 与生产逐字节同 hash；override = `f0452bea…`。
6. **未决项**：handoff open_questions 第 1 条即 I-03-A 未定义的"本地无受信日期 + 远端不同 accession"——副本保守落 `unknown_candidates(reason=local_date_missing)`、不进 missing/newer，列为待高级裁决开放问题，未私自填写为行为定案；另如实记录 ambiguous 下 already_covered 边界折中待复核、not_published 恒 false 遗留依赖、C15 执行面移交。共 4 条开放问题，无私自裁决定案。

## 3. 资格与限定

- **本验收仅授予隔离副本（iso/override）的纯选择面实现资格**：不授予生产部署；gap_plan.py 合入生产须走 I-03-C/D 的 schema 落地、哈希/授权重建与消费端验收。
- **T-GAP（生产 checkout pytest）绑定归 I-00-B**；本 attempt 未运行生产 pytest（生产未修改，运行只能复验旧行为），以同断言组在 isolate 等价复现——该等价性已被本次重跑独立确认。
- **C15 批次截断/completed_partial/remaining 与全部执行面（close_gap/authorization）归 I-03-C**，本卡验收不含。
- 三市场样本为手工 metadata 模拟，不外推为真实 provider（CN 交易所/HKEX/SEC）验收。
- 记录一处非阻断观察：override `_candidate_dates` 含 `published_date` 回退（local 句柄），已在 iso_patching.md §2 作映射声明，属 I-03-A §1.4 授权的逐文件映射范围；生产落地时须经 I-03-C/D 确认 catalog 字段真实性。

## 4. 保留案例（供后继卡复验）

- reviewer 保留案例：root=`m-root-77`、修订 id=`q-doc-3`（未在实现者任何 fixture 中出现）双向重放 G-B1/G-B2 + 远端逆序 hash 等价，本次 PASS。后继卡（I-03-C/D）合入生产前应重放此案例及 G-B1—B5 全组。
