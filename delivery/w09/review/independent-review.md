# W09-RF-RESEARCH 独立审查报告（第一轮）

- 审查者角色：独立 review agent（非实施者口吻；未参与任何实施步骤）
- 审查时间：2026-10-23 21:00–21:20 UTC
- 被审版本：
  - `forecast/main-input.json`（on-disk SHA `cb155a827f6a241b…`，engine canonical `93ba13a5207a…`）
  - `forecast/stress-input.json`（on-disk SHA `7f0cf9d92d4a…`，engine canonical `4c82c3c1baf5…`）
  - 三张方法卡的工作树版本（见 JSON 内逐文件 SHA）
- 审查方式：22 个真实探针脚本全部实际执行（命令清单见 JSON `probes_actually_run`）；所有结论来自实际重算，不来自实施者自述。

## 结论：FAIL（2 个 MAJOR，修复后需复审）

不通过的原因不是预测数字或证据语义——这两方面实际核验全部通过——而是两处**可复现性缺陷**：一个哈希记录错误会让第三方无法按账本重放切片，一个是备忘录引用了已被自己推翻的早期 SHA。此外确认了一个实施者自查已列出的结构问题，一并归档。

## 实际核验通过的部分（列明证据，非"没发现问题"）

1. **49/49 并集覆盖、无重复**。独立重算 old role counts = 31 mechanism + 18 conversion，new = 26/21/2；新旧两侧逐 claim 的 role/target/source 全部与账本一致，`UNDOCUMENTED changed claims: 0`（p6/p8）。
2. **18 条价格反控**逐条确认 old=conversion、new=conversion，`problems=[]`（p8）。这 18 条**不是**待修项，实施者没有为通过校验而"修"它们。
3. **3 条 Biology H2 rebase** 的算术基础独立复算成立：2,677,175,030.51 − 125,160.49万元 = 1,425.57013051（p12），新摘录确实是年报 p14 **生物学**段（p8）。
4. **2 条无机制 claim**（`claim_driver_other`、`claim_driver_discontinued`）确认降为 history_base，新摘录各自只含历史下降行 / 终止经营零收入行；native 输出新增 "no future-mechanism evidence" 限制（p8/p14）；`unknown_mechanism_no_role_fix` 在两个输入中出现 0 次（p8）。
5. **桥全部重算通过**：19 个量逐位一致；六分区 2025 加总 = 45,456.16577418（diff 0）；TIDES 单计 tides25+non_tides_fy25=chem_total_2025（p12）。65.82% 与 61.57% 两个分母分别出现、未混用（p12/p13）。
6. **原生链真实执行**：6 个 capture 目录里 `input-0001`/`consume-0001` 的 SHA 与 request.json 逐字节相等（p17）；registry 6 条 `prev_line_sha256` 链、首条 prev 为空属正常创世行（p19）；main/stress 的 forecast `input_sha256` 与快照 `input_sha256` 相等（p17）。
7. **三情景 segment_subtotal 与封存旧输出逐位相同**（p14）；置信分 24.01705900038857 前后相同（p16）。
8. **诚实性**：`observed_range` 新旧两侧非空计数均为 0；12 项校准全 unverified；未发现编造的 ASP/利用率/取消率/队列/经验区间（p16/p18 的全文扫描只命中说明文字与既有披露数字）。
9. **RPO**：kind=management_guidance、role=value_range、值 42207.0646 不变、segments/growth_driver_tree/sensitivity_tests 中 0 次出现（p22）；FY2025 期末 RPO 存量仍是 reported point-in-time fact。
10. **方法卡**：新增段落均为通用判据，无公司名/中文分部名/D&M 词变成规则；泛化例用订阅平台+项目服务结构，含 1 正例 3 反例（refs.diff 全文核对）。

## 发现的问题

### MAJOR-1：拆分片段的 `contiguous_range_sha256` 记成了父切片的哈希（影响 10 行账本）

- **位置**：`research/excerpts.json` 的 `chemistry_dm_operating`、`chemistry_r_operating`；由此污染 `claim-changes.json` 中 10 行（`claim_driver_non_tides` + 9 条 non-TIDES activity）的 `contiguous_range_sha256`。
- **发现方式**：p4/p21 从页文本按 `start/end` 重切并重算 SHA。`chemistry_dm_operating`（span 657..920）记录的是父 657..1250 的哈希 `716627fa…`，真实切片哈希应为 `d26e03ca…`；`chemistry_r_operating`（span 920..1250）同样记录 `716627fa…`，真实应为 `d4d7df24…`。`excerpt` 本身与切片逐字相等（`exact=True`），即**摘录是对的，账本哈希是错的**。
- **根因**：`verify_excerpts.py` 拆分时用 `{**chem.items()}` 浅拷贝继承了父记录的 `contiguous_range_sha256`，只重算了 `excerpt_sha256`。
- **为什么是 MAJOR**：账本的显式承诺是"按 start/end 可重放切片"，这 10 行不可重放。不是 CRITICAL，因为 `excerpt_sha256`（native 实际校验的字段）正确、输入可通过校验、预测数字不受影响。
- **建议修复**：每个拆分片段重算自己的 raw 哈希；`verify_excerpts.py` 加自检断言（任一记录的 contiguous 哈希必须等于按 span 重切的重算值）；重建输入与全部下游产物并重跑链。

### MAJOR-2：`research-memo.md` 引用已被覆盖的早期 request SHA

- **位置**：`research/research-memo.md` §3 写"main `4454ce57…`，stress `852ba877…`"。
- **发现方式**：p18/p20 全 delivery 目录 grep——这两个 SHA 只在备忘录（和探针脚本）里出现，不在任何 capture 目录、request.json、native-calls.jsonl 或 registry 中；实际冻结 request SHA 是 main `770cd309…`、stress `c0c45687…`。这是实施者自己在 C 阶段重跑全链后未同步备忘录留下的陈旧引用。
- **根因**：B 阶段早期几轮迭代（补 observations、修 Testing、统一版本串）每轮都重置 recorder；备忘录在 20:1x 写成后没有随最终链更新。
- **为什么是 MAJOR**：memo 是给 ROOT 的第一入口，引用不存在的执行凭据比不引用更糟。
- **建议修复**：memo 改为引用 `native-chain.json` 中的最终 SHA；以后 memo 中的任何哈希必须来自机械读取，不得手抄。

### MINOR-1：memo 的"逐位相同"措辞会被误读为整文件逐位相同

- **位置**：memo §3/§6 说主/压力输出与封存旧输出"逐位相同"。
- **事实**（p14）：`segment_subtotal` 三情景逐位相同；但整份 forecast JSON 并非逐字节相同——`confidence.limitations`、`research_adequacy`（735 个叶子差）等因角色/观测修复而改变，这正是修复的目的。
- **建议**：措辞改为"三情景 segment_subtotal 逐位相同"，并说明其余差异是预期修复效果。

### MINOR-2：`excerpts.json` 的 `count_proposals=20` 与准备包声明的 47/49 不符

- **发现**（p3）：`count_proposals` 统计的是 `excerpts` 字典键数（20 个模板段），不是 claim 数（49）或摘录提案数（47）。字段名易误读。
- **建议**：改名或在 purpose 里注明"unique excerpt templates, not claims"。不影响任何校验。

### 确认实施者已自查修复的（不计新问题）

实施者在 `progress.md` 自列了四个缺陷（return 早退丢 observations、RPO 未入账本、Testing 越界缺陷未修、版本串不一致），本轮审查在 p8/p17 中独立复核确认这些修复真实存在。

## 需要复审的内容

MAJOR-1、MAJOR-2 修复后：重放 `verify_excerpts.py`（应含自检）、重建 main/stress 输入、重跑 6 次原生链、重建 `native-chain.json`/`sensitivity.json`/`acceptance-checkpoints-graded.json`/`cleanup/receipt.json`，并逐行重放账本 contiguous 哈希（含 out-of-union 与 RPO 行）。
