# W09 审查问题修复记录

对照 `review/independent-review.json`（第一轮，结论 FAIL）逐项修复。两个 MAJOR 均已修复并全链重建；两个 MINOR 一并处理。

## MAJOR-1：拆分片段的 `contiguous_range_sha256` 记成父切片哈希（影响 10 行账本）

**修复（verify_excerpts.py）**
- 拆分逻辑改为：每个片段只继承父记录的**非哈希、非 span** 字段（`parent_keys` 白名单式排除 `excerpt`/`excerpt_sha256`/`contiguous_range_sha256`/`start_char_inclusive`/`end_char_exclusive`），然后**各自重算** `contiguous_range_sha256 = raw_sha256(first/second)`。
- 新增自检断言（防同类回归）：对**每条**含 excerpt 的记录，从页文本按 span 重切，断言 `raw_sha256(raw_slice) == contiguous_range_sha256`、`raw_slice == excerpt`、`10 <= len(strip) <= 500`。任何不一致直接 raise，不再可能静默通过。

**验证**
- 重跑后：`chemistry_dm_operating` = `d26e03ca396c…`（与审查者重算一致）、`chemistry_r_operating` = `d4d7df247a71…`（与审查者重算一致）。
- 用审查者同款方法独立重放**全部**账本行（49 union + 9 out-of-union + 1 RPO）：`rows with bad contig sha: 0`，RPO 行 OK。见 `review/_probe/fix_check.txt`。

**下游重建**：main/stress 输入重建→validate 通过→recorder 重置→6 次原生链重跑→`reconcile_chain.py` 全 clean 且 main/stress 三情景仍与封存输出相同→`sensitivity.json`/`acceptance-checkpoints-graded.json`/`consumed-inputs.json`/`cleanup/receipt.json` 全部重建。

## MAJOR-2：memo 引用已被覆盖的早期 request SHA

**修复（research-memo.md §3）**
- `4454ce57…`/`852ba877…` 改为机械读取自 `native-chain.json` 的最终值：main `770cd309…`、stress `c0c45687…`，并补记 engine 侧 canonical input SHA（main `93ba13a5…`、stress `4c82c3c1…`）。
- memo 中不再出现任何手抄哈希；全部指向 native-chain.json 作为唯一事实来源。

## MINOR-1："逐位相同"措辞易误读

**修复（research-memo.md §3、§6）**：限定为"三情景 `segment_subtotal` 逐位相同"，并注明 forecast JSON 其余差异（confidence limitations、research_adequacy、735 个叶子）是角色/观测修复的**预期效果**。

## MINOR-2：`count_proposals` 字段名易误读

**处理**：保持字段不更名（改名会动 20 条记录的 schema 且该字段无任何校验消费），在 JSON `purpose` 里显式注明其语义为"unique excerpt templates (22), not claims (49) or claim proposals (47)"，同时并排补充 `count_excerpt_templates_proposals`（=20，模板提案数）与 `count_excerpt_templates_verified`（=22，含拆分后的两个子模板）两个字段，消除歧义。已在 `verify_excerpts.py` 的 record 中落实。

## 第二轮复审（PASS_WITH_MINOR）后的三条收尾处理

第二轮复审结论 PASS_WITH_MINOR，三条新观察均已处理，且**均不触发任何产物重建**：

1. **R2-MINOR-1（自检循环位置）**：已把 `verify_excerpts.py` 的自检断言循环移到 `main()` 末尾（`testing_h1_own` 加入之后），使其覆盖全部 22 个模板而非 21 个。重跑后 `excerpts.json` **逐字节不变**（SHA 前后相同 `7E6F814D…`），属零风险护栏加固，不触发下游重建。
2. **R2-MINOR-2（memo §2.1 残留措辞）**：该处已改为"三情景 `segment_subtotal` 与封存旧输出逐位相同（含义界定见 §3）"，与 §3 的界定段落交叉引用。
3. **R2-INFO-3（本文件字段名笔误）**：本节上文已把"补了 `count_excerpt_templates` 字段"更正为实际的 `count_excerpt_templates_proposals` / `count_excerpt_templates_verified` 两个字段名。

## 修复后一致性复核（全部机械执行）

| 检查 | 结果 |
|---|---|
| verify_excerpts 自检断言 | 通过（22/22，含两个修复片段） |
| main/stress validate --verbose | valid / valid |
| 6 次原生链（validate/compute/snapshot × 2） | exit 全 0，frozen==request 全 true |
| 三情景 subtotal vs 封存 | main/stress 均相同 |
| 快照 input_sha256 == forecast input_sha256 | main/stress 均成立 |
| registry 链 | 6 条，prev 链完整 |
| 账本 contiguous 哈希重放（59 行） | 0 错 |
| 检查点评级 | 10/10 PASS |
| 交付体积 | 22.33 MB < 32 MiB 上限 |

## 备注

- 审查者在崩溃前实际执行的 22 个探针脚本与输出保留在 `review/_probe/`，作为第一轮审查的真实凭据；本轮修复的判定依据直接来自这些探针（p4/p21 发现 MAJOR-1，p18/p20 发现 MAJOR-2）。
- 第一轮 `independent-review.{md,json}` **原样保留**（结论 FAIL），不做事后修改，以便 ROOT 看到真实审查轨迹。
