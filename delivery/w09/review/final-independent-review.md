# W09-RF-RESEARCH 最终独立复审报告（第二轮）

- 审查者角色：最终独立复审 agent（第二轮；非实施者口吻；未参与任何实施或第一轮修复）
- 审查时间：2026-10-23 21:55–22:55 UTC
- 输入文件：第一轮 `review/independent-review.{md,json}`（结论 FAIL，2 MAJOR + 2 MINOR）、实施者 `review/review-fixes.md`
- 审查方式：本轮所有结论来自**独立重算与真实重跑**（探针脚本与输出全部保存在 `review/_probe2/`，命令清单见 JSON `probes_actually_run`），不采信实施者 `review-fixes.md` 的任何自述。

## 结论：PASS_WITH_MINOR

6 项全部机械验证通过。两个 MAJOR 的修复真实、完整、可复现；全链确实在修复后重建；预测与反控零回归。另发现 3 条新的 MINOR/INFO 级观察（无一是数据缺陷，见文末），不阻塞交接。

---

## FIX-1（原 MAJOR-1）：拆分片段哈希 —— VERIFIED

**片段自身哈希**。从页文本独立重切并重算（`_probe2/f1a_out.txt`、`f11_out.txt`）：

| 片段 | span | 记录值 | 重算值 | 一致 |
|---|---|---|---|---|
| `chemistry_dm_operating` | p11 [657, 920) | `d26e03ca396c4046…` | `d26e03ca396c4046…` | ✅ |
| `chemistry_r_operating` | p11 [920, 1250) | `d4d7df247a7121e3…` | `d4d7df247a7121e3…` | ✅ |

两者与第一轮审查者重算的期望值（`d26e03ca…` / `d4d7df24…`）**逐位一致**；摘录文本与切片逐字节相等。父记录 `chemistry_non_tides_operating`（[657,1250)，已无 excerpt 正文）保留 `716627fa…`，对其自身 span 是正确的，并带 `split_into` 指向两个子片段。

**全账本重放**（`f1b_out.txt`）。对每一条带 `contiguous_range_sha256` 的账本行——49 行并集 + 1 行 RPO（`out_of_union_requirement_repairs.rows[0]`，`rpo_expected`，p184 [547,674]，`4a5f337872964f50…`）——从 `verified-source-pages.json` + `source-page-addendum-20261023.json`（两个文件 SHA 先对照施工卡核验：`66dced5b…`/`993cc92c…` 均符）按 `contiguous_span` 重切并重算 SHA：**50/50 全部匹配，0 错，0 缺页**。9 行 `out_of_union_repairs` 本身不含 `contiguous_range_sha256` 字段（只有 span + 摘录文本），其一致性通过模板交叉核对覆盖。

**59 行 × 模板交叉核对**：每行的 span 切片 == 其 `excerpt_id` 模板的 excerpt 正文、行哈希 == 模板 `contiguous_range_sha256`、行 `new_excerpt_sha256` == 模板 `excerpt_sha256` —— **0 不一致**。原 MAJOR-1 涉及的 10 行（9 条 non-TIDES activity + `claim_driver_non_tides`）逐行 64 字符全量复核，0 错。

**工具自检断言**。`verify_excerpts.py` 第 136–148 行确实包含自检循环：对每条含 excerpt 的记录，按 span 重切，断言 `raw_sha256(重切片) == contiguous_range_sha256`、`重切片 == excerpt`、`10 <= len(strip) <= 500`，任一不符直接 raise。见下文 R2-MINOR-1 关于其覆盖位置的观察。

**可复现性**。我把 `verify_excerpts.py` 复制为 `_probe2/verify_excerpts_rerun.py`（仅把 OUT 重定向到 `_probe2/excerpts_rerun.json`）真实重跑：exit 0，且输出与盘上 `research/excerpts.json` **逐字节相同**（两侧 SHA `19824ddbfa4d4c20…`）。即盘上文件就是修复后工具的确定性产物。

## FIX-2（原 MAJOR-2）：memo 哈希 —— VERIFIED

- `research-memo.md` 中 `4454ce57`、`852ba877` **0 次出现**（程序化 grep，`f2_out.txt`）。
- 全 delivery/w09 扫描（排除 `review/_probe*`）：这两个陈旧 SHA 只出现在审查文档自身（`independent-review.{md,json}`、`review-fixes.md`）里，作为第一轮问题记录被引用——这是应当保留的。
- memo §3 现在引用 main `770cd309…` / stress `c0c45687…`，与 `native-chain.json` 6 个 call 的 `request_sha256` 逐位一致（main 三 call 全 `770cd309353c…`，stress 三 call 全 `c0c45687f9cf…`）；补记的 engine 侧 canonical 输入 SHA `93ba13a5…`/`4c82c3c1…` 与 forecast/snapshot 的 `input_sha256` 一致。memo 里再无其他手抄哈希（hex token 全集已列举核对）。

## FIX-3（原 MINOR-1）：“逐位相同”措辞 —— VERIFIED

memo §3 新增专门段落 **“‘逐位相同’的确切含义”**：明确限定为“三情景 `segment_subtotal` 与封存旧输出逐位相同”，并说明 forecast JSON 其余差异（limitations 新增两条 no-future-mechanism、research_adequacy 0→66 条 typed observation、若干 calibration reason 变化、约 735 个叶子）全部是角色/观测修复的**预期效果**；§3 压力条目写“与封存旧压力输出的三情景 subtotal 相同”；§6 有交叉引用。

我用独立 leaf-diff 复核了措辞背后的数字：main vs 封存 changed leaves = **735**（另有 added 1125 / removed 37，全部来自 observation/limitation 的预期新增），而 3 个情景的 segment_subtotal 节点全部相同——memo 新措辞与机械事实吻合。（遗留一处见 R2-MINOR-2。）

## FIX-4（原 MINOR-2）：count 字段语义 —— VERIFIED

`excerpts.json` 的 `purpose` 明确写明：“the count_* fields below count **UNIQUE EXCERPT TEMPLATES** (contiguous source ranges), NOT claims (49 in the review union) and NOT per-claim excerpt proposals (47 in the preparation package)”。计数字段并排给出：`count_excerpt_templates_verified=22`、`count_excerpt_templates_proposals=20`、`count_claims_in_review_union=49`、`count_preparation_excerpt_proposals=47`，歧义消除。全部 22 个模板从页字节重验（contig 哈希 + 原文 + strip 哈希）：0 错。

## FIX-5（修复后全链重建）—— VERIFIED

- **6 个 call 全部干净**：`native-chain.json` `all_calls_clean=true`；每个 call `child_started=true`、`exit_code=0`、`input_complete/output_complete=true`、`frozen_matches_request=true`。
- **冻结字节独立复核**（`f6c_out.txt`）：6 个 request.json 的 SHA 与 native-chain 记录一致；每个 capture 目录的 `input-0001-*` 与 request.json **逐字节相等**，`consume-0001-*` 与冻结输入逐字节相等；stdout/stderr 与记录字节数一致。
- **identical_old**：`native-chain.json` `sealed_comparison` 6/6（main/stress × low/base/high）`identical=true`。我**真实重跑了 `reconcile_chain.py`**：exit 0，stdout `{"all_calls_clean": true, "calls": 6, "main_identical_old": true, "stress_identical_old": true}`；重跑后 `native-chain.json` 未变（SHA 仍为 `b3b2e9ac…`，与 graded artifact 记录一致）——幂等，证明盘上文件就是该脚本产物。
- **三情景独立重算**（`f5c_out.txt`）：从 `forecast/main-forecast.json` + `stress-forecast.json` 对封存 `final3-forecast.json`（`41ea79efa319226a…`，与卡一致）+ `final3-shared-stress.json` 逐路径比较 segment_subtotal：main/stress 各 3 节点全部相同（如 main base 2026=59466.12444323827 / 2027=69526.2277014774 / 2028=77228.85767968993）；stress−main = −4500/+3600/0 复核成立。
- **input_sha256 链**：forecast `input_sha256` == snapshot `input_sha256`（main `93ba13a5…`，stress `4c82c3c1…`）。
- **链是真重建**：6 个 request 目录时间戳 `20261023T2052–2053Z`、registry 注册时间 20:53:05–20:54:04，均晚于第一轮探针看到的旧链（20:12–20:13），即链在修复后确实重跑过，不是旧产物回收。
- **registry**：6 行，`prev_line_sha256` 链完整（首行 prev 为 null 的正常创世），每行 `line_sha256` 可复现，snapshot `artifact_id`（main `4372da1c…`、stress `4bf5aed3…`）与 native-chain 一致。（注：第一轮 p19 输出里的行哈希是旧链的值，与现盘上 registry 不同属正常——链已重建。）

## FIX-6（回归检查）—— VERIFIED

| 检查 | 结果 |
|---|---|
| 49/49 行、0 重复、49 个唯一 claim_id | ✅（`f6a_out.txt`） |
| 旧角色 31+18 / 新角色 26/21/2 | ✅ 从行数据独立重算，与汇总字段一致；整输入层面 sealed→new 角色净变化 = mechanism −5 / conversion +3 / history +1 / value_range +1，恰好等于已记载的三类修复（3 rebase→conversion、2 unknown→history_base、RPO→value_range），无其他任何角色变动（`f12_out.txt`） |
| 18 价格反控 | ✅ 账本 old/new 双侧 + main/stress 输入双侧全部 `conversion_assumption`，0 违例 |
| `unknown_mechanism_no_role_fix` | ✅ 两个输入均 0 次出现 |
| RPO | ✅ `management_guidance` / `value_range` + `exact_value`，值 42207.0646 不变，0 个收入 DAG 消费（parameters/segments/growth_driver_tree/sensitivity_tests 均无引用） |
| 检查点评级 | ✅ 10/10 PASS；graded 文件记录的 8 个 artifact SHA 与盘上文件全部一致（`f6c_out.txt`） |
| `cleanup/receipt.json` | ✅ `restored=true`；8 个保护 artifact 的 SHA 与字节数与盘上一致 |
| 交付体积 | ✅ 23,916,862 B = **22.81 MiB** < 32 MiB（含两轮探针目录） |
| 封存/只读输入未被改动 | ✅ final3-forecast/final3-input/verified-source-pages/addendum 的 SHA 重验均与施工卡一致 |

---

## 新发现（本轮，均不阻塞）

**R2-MINOR-1 — 自检循环的覆盖位置**（`verify_excerpts.py` L140–148）。自检断言循环执行时 `rows` 里只有 22 个模板中的 21 个；`testing_h1_own` 在循环**之后**才加入，代码内只做了长度断言。即防回归护栏本身暂不覆盖第 22 个模板。这不是数据缺陷——该模板已被本轮独立重验（contig 哈希与切片逐字匹配，[88,400]），引用它的 9 行账本交叉核对干净——但 `review-fixes.md` 描述自检“对每条含 excerpt 的记录”生效，与代码实际覆盖面有一行差距。建议把循环移到 `main()` 末尾。

**R2-MINOR-2 — memo §2.1 残留一处未限定的“逐位相同”**（research-memo.md L62：“重算结果与封存旧输出**逐位相同**”）。其指针 `native-chain.json` 本身只比较 segment_subtotal，且 §3 已定义“逐位相同的确切含义”，通读不会被误导；但孤立看这句话，仍是 MINOR-1 指出的那类不精确。被点名的 §3/§6 两处已完全合格。

**R2-INFO-3 — 修复说明的字段名不准确**。`review-fixes.md` 说补了 `count_excerpt_templates` 字段；实际字段名是 `count_excerpt_templates_proposals` / `count_excerpt_templates_verified`。产物本身无歧义、修复意图（模板≠claim 的消歧）完全达成，仅说明文字不精确。

三条均不影响第一轮任何修复的有效性，不构成数据/执行/可复现性缺陷，故结论为 **PASS_WITH_MINOR** 而非 FAIL；也不建议为它们再触发一轮全链重建（R2-MINOR-1 若要修，只需移动循环位置并重跑 `verify_excerpts.py`——输出应逐字节不变——属零风险小改，可与 ROOT 后续维护合并处理）。

## 复审范围与限制

- 本轮只验证第一轮 4 个问题的修复 + 修复后重建完整性 + 预测回归；第一轮已核实通过的桥接算术、诚实性扫描、方法卡泛化等未重复全量复算（第一轮探针凭据保留于 `review/_probe/`，且本轮对其中关键结论做了抽样复核：三情景相同、置信分 24.01705900038857 的上下文、observed_range 为 null 的语义均未随修复漂移）。
- 我对 `verify_excerpts.py` 与 `reconcile_chain.py` 的重跑均为**输出重定向到 `review/_probe2/` 或幂等验证**（`reconcile_chain.py` 重写 `native-chain.json` 内容与盘上逐字节一致，SHA 前后相同 `b3b2e9ac…`），未改动任何交付产物；对工作区只写了 `review/_probe2/` 与两份本报告文件。
- 机器可读明细见 `final-independent-review.json`；每条结论都能在 `review/_probe2/f*_out.txt` 中找到对应原始输出。
