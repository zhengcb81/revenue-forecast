# I-05-A r4 定点复审报告（独立 reviewer，第四轮）

预注册（运行前冻结）：`%TEMP%\planrev4\rev\PREREGISTRATION_R4.md`，sha256 `0e884affbef1fc7436d9c9a5d46f1ef9cbf83aadab57112947adcedea48a8785`。
全部运行在 `%TEMP%\planrev4` 副本；生产仓与 PLAN 只读（本轮我**零写入** PLAN，裁决正文在 §6 交父 agent 转录）。

| tree | section_query.py | 说明 |
|---|---|---|
| `T4_prefix_r3` | `5fbbe49a…cac1` | `iso/prefix_r3`（修复前，冻结） |
| `T4_r4` | `06a1a6ea…ebceb7` | `iso/fixed` + `iso/cw/src`（实测一致） |
| `T4_r2` | `b3ffc6c5…1bce8` | 第二轮代码（对照） |
| `T4_pristine` | `a40d54a3…4f49` | 生产原始字节 |

## ① 判定：`accepted_scoped`

你要求的 1–3 项全部成立，且**无新矛盾**：per-origin 强制已真实生效（我自造的第三种注入与"偏移+1 且内容平移"都被拒），fail-closed 已落地（新原因码可复算），行边界对齐**没有**过度收紧（正例与 25/88 两套回归全绿）。据此按原卡口径授予资格。

范围（授予）：sections 消费者资格门（FROZEN-1/2）＋下列反例闭合：c0–c8、n2a/n2c、p2、n3；m1/m2/m2b/m2c/m3/m3b/m4/m4b/m7；被审方 I1/I2/I3；以及我本轮自造的 `only_second` / `midline` / `fabricated` / `plus1_content` / `roleswap`。
范围（未授予，仍为未签 owner 门）：D-W05 OPEN-1..7 的一切决策（含历史无哈希工件的回填/重算、`as_of_date` 口径）；I-05-B / I-05-C 不得据此开工；`disclosure_adaptation` / `accuracy` 按原登记另行验收。

## ② 若拒的最小修法

**不适用（本次判接受）。** 下列 P3 不阻塞，建议随下一卡一并处理，且**只许追加**（不得改写已冻结的正文/附录 A/B）：

- **P3-1 oracle 前像字节数错误**：附录 C 写"`oracle.md` 在 r3 结尾时为 14924 B"，实测 r3 末态为 **23204 B**（14924 落在正文 §5 "未签专业决策" 内；附录 A 起点 16119、B 起点 20726、C 起点 23212）。**追加性本身我已独立证明**（见 §1.6）。修法：在附录 D 追加一条更正（不要改 C 正文）。
- **P3-2 证据字段回退**：`after/prod-anchor-hashes-after.json.attempt_fixed` 在 r3 为 `{section_query:5fbbe49a…, section_extractor:0f201c68…, max_function_complexity_section_query:9}`，r4 变成 `null`。修法：追加补写 r4 的三元组（`06a1a6ea…` / `0f201c68…` / `11`）。
- **P3-3 命名易误读**：`evidence/p1-mutations.json` 的键名 `I1_offsets_plus_one` 对应 `mutation_detail.delta = 2`（README 已解释，但键名仍会误导）。修法：在 README/附录补一行注记，或下次改用 `I1_offsets_plus_two`。
- **P3-4 基线漂移（沿用第三轮）**：`binding.json` 仍记 RF HEAD `7d7ea1ed…`；live 已是 `cc78c529…`。影响为零（见 §5 的核验），仅需补记。
- **P3-5 角色/题名与内容不互相校验（已披露的边界）**：`roleswap2`（保留 role/title，采用另一条的 path+offset）被接受并按 `source_window` 服务。内容确实是文档在声明偏移处的合法行对齐窗口，因此**源/span 绑定成立**；未校验的是 role/title↔内容。任何冻结 oracle 都未要求该校验，故不作缺陷；建议在 `SectionEntry` 文档与附录里写明"role/title 由 index 声明、不参与绑定校验"。

## §1 逐条独立核验

### 1.1 是否真的 per-origin 强制（你要求的第 1 项）

命令：`py -X utf8 -B %TEMP%\planrev4\rev\r4probe.py <tree> <tag> [case…]`

修复前（`T4_prefix_r3`，RED 复现，与你的 `evidence/p1-mutations.json` 一致）：
```
i1_plus2           returned  None   business_overview:substring_only@[];mda:substring_only@[]
i2_plus5           returned  None   ...substring_only@[]
i3_no_normalized   returned  None   ...no_source@[]
c0                 returned  None   business_overview:source_window@[109];mda:source_window@[208]
```

修复后（`T4_r4`）：
```
c0                 returned  None   business_overview:source_window@[0, 1];mda:source_window@[0, 1]
i1_plus2           error     sections_binding_error
i2_plus5           error     sections_binding_error
plus3              error     sections_binding_error
plus4              error     sections_binding_error
plus1_content      error     sections_binding_error
only_second        error     sections_binding_error
midline            error     sections_binding_error
fabricated         error     sections_binding_error
roleswap           error     sections_binding_error
plus1              returned  None   business_overview:source_window@[0];mda:source_window@[0]
roleswap2          returned  None   business_overview:source_window@[0, 1];mda:source_window@[0, 1]
i3_no_normalized   error     sections_no_normalized_source
i3b_no_row         error     sections_no_normalized_source
```

- **决定性自造注入**：`only_second` —— 只把**第二条**的偏移 +3（第一条不动，index+metadata 全键同步、行 hash 更新）→ **拒绝**。证明是**逐条（per-entry）**而不是"整件只要有一条能对上就放行"。
- **偏移 +1 且内容平移一位**（`plus1_content`：offset +1 且切片内容取 `body[cs+1 : cs+1+len]`）→ **拒绝**。这是"用 origin 松弛吸收偏移伪造"的最直接攻击，已被堵住。
- **无接受路径把 `substring_only` 当通过**：我逐例核对了接受标签——所有 `returned` 的用例 `all_source_window = True`；`substring_only` / `no_source` 只出现在**拒绝原因**里（`T4_prefix_r3` 上它们才是通过标签）。这一点我以脚本字段复算，不依赖叙述。
- **残留 `plus1`（偏移 +1、内容不动）被接受**：内容是**同一段真实文本**（trim 后字节相同），被解释为 origin=1 的合法行对齐窗口，与你们 README/oracle C.2 的说明一致。**我判定它不是内容旁路**（没有伪造、没有跨节替换），属如实披露的边界；但消费方不应把 `char_start` 当精确索引（可差一个前导换行）。

### 1.2 fail-closed（第 2 项）

```
i3_no_normalized  -> error sections_no_normalized_source   （UPDATE artifacts SET status='failed' WHERE artifact_role='normalized'）
i3b_no_row        -> error sections_no_normalized_source   （DELETE 该行）
```
修复前同两例为 `returned` + `no_source` 标签（`T4_prefix_r3` 上复现）。新原因码与恢复动作在 `NEXT_ACTION_BY_REASON` 中可读。

### 1.3 行边界对齐是否过紧（第 3 项）

- `c0` 正例：两片 `window_match=source_window`、`window_positions=[0,1]`（含前导/尾随换行、跨多行的切片）→ 未被误杀。
- 25 例套件：`25 passed, 1 warning in 5.38s`，rc=0。
- 7 文件全量隔离回归：`88 passed, 1 deselected, 1 warning in 17.79s`，rc=0（含 b10 读链与复杂度两个 ratchet）。
⇒ 对齐约束**没有**过度收紧；且 `plus1` 的存在说明它在"边界±1"方向上也不苛刻。

### 1.4 数字更正的证据链（第 4 项）

| 声明 | 我复算的结果 | 出处 |
|---|---|---|
| C14 以 25 为准，原 18 保留 | ✅ C14 现为 `expected_business_result:"18 passed (r2, superseded)"`、`declared_r2:"18 passed / rc=0"`、`measured_now:"25 passed / rc=0 (final bytes)"`、证据注记已被 C17 覆盖 | `commands.json`（C1–C21，共 21 条） |
| 复杂度 10 / 9 / 11 | ✅ 用仓库自带 `test_fc1204_complexity_ratchet._max_complexity`：r2=**10**、prefix_r3=**9**、r4=**11**（冻结上限 12） | 我的复算 |
| diff 860 行、仅两文件 | ✅ 860 行；`--- a/` 只有 section_query.py 与 section_extractor.py | `changes.diff` |
| 拒绝探针 9/11 | ✅ `after/review-attack-probes.json`：9 拒绝、1 `returned`（m6 回退旧 VALID 行）、1 其他（m5 `completed=0` 死锁） | 该 JSON |
| 我的变异脚本可复算 | ✅ `evidence/p1-mutations.json` 记 `pre_fix_sha256=5fbbe49a…` / `fixed_sha256=06a1a6ea…`；I1/I2 `post_fix=sections_binding_error`、I3 `post_fix=sections_no_normalized_source`，`verdict_change=returned -> refused`；脚本在查询前断言模块 sha256（读其源码可核） | 该 JSON + `scripts/w05a_p1_mutations.py` |

### 1.5 旧 RED 字节的"不可复算缺口"是否诚实

- `iso/prefix_r3/section_query.py` 冻结在 `5fbbe49a…cac1`（与报告一致），未被覆盖 ✅。
- 当前 `after/cmd-tests-i05a.stdout.txt` 含 `25 passed` 且**不含** `3 failed` ✅。
- `3 failed, 15 passed` 只出现在 `commands.json` / `oracle.md`（C.4）/ `review_r3_disposition.md` / `review_r4_disposition.md`（§r4.6）的**文字登记**中；**全树没有任何伪造的 RED 文件** ✅。
- 登记文字明确写"原字节未留档、已丢失、丢失时点=A2 处置、原因=直接重跑覆盖、**未补造证据**"，并把它列入 `handoff.open_questions` ✅。判定：**诚实**。

### 1.6 oracle 只追加

- 我持有的 r3 末态 `oracle.md`（23204 B）与 r4 `oracle.md`（26421 B）逐字节比对：**`r4[:23204] == r3 全文`（True）**，即正文与附录 A/B **一字未改**，仅追加附录 C（+3217 B）✅。
- 附录 C 开头明写"附录 B.1/B.2 的 'substring_only 是降级标注、源窗口命中即可通过' 已过时，以 C.1/C.2 为准"，并冻结了 C.1 判据、C.2 绑定精确定义（含对齐约束）、C.3 新原因码、C.4 缺口 ✅。
- **唯一不实**：C 里的前像字节数 14924 B（见 P3-1）。

## §5 生产零改动与其余口径

- **company-wiki**：HEAD `f39bd5a64224cd0c7aa098f23f64bf3811fa8939` 未变；porcelain 恰 `[' M CLAUDE.md',' M README.md']`（**r3-after → r4-after 的 CW 差异：非 `.planning` 新增/删除均为 NONE**）；三模块 hash 与冻结锚点一致；`after/prod-anchor-hashes-after.json.all_anchors_match_card = true`（13/13）。
- **revenue-forecast**：HEAD 已前移到 `cc78c5298acd5a5ff8b898d9aa237fc5a8559979`（审计留档提交）。我逐段核验 `7d7ea1ed..HEAD`（8702 文件）、`e9544495..HEAD`（7420 文件）、`cc78c529..HEAD`（0 文件）**均无非 `.planning/` 路径**；porcelain 的 r3→r4 差异中非 `.planning` 新增/删除均为 **NONE**；产品 `scripts/` 下无 `w05a*` 模块。
- **filing-fetch**：porcelain 空 ✅。
- **`PLAN\reviews` 未写（两个口径都给）**：目录 mtime `2026-09-19 09:14:20`；**目录内最新文件 mtime `2026-09-19 10:05:32`**；**mtime ≥ 2026-09-20 02:00 的文件数 = 0** ✅。
- **状态**：`handoff.status = review_pending`，`reviewer_status` 明写"实现者未自签、未使用 accepted/passed 标签" ✅。
- **未签 owner 门**：`iso/fixed/section_extractor.py` 仍只有 `sec.status='completed'`（328/341），**无版本比较**；`decision.md` OPEN-1..5 仍标未签、§7 OPEN-7 仍在；`handoff.blocked_by = "D-W05 七项专业决策未签：I-05-B/I-05-C 在签名前不得开工"` ✅。
- **回归未被我方忽略**：`after/case_results.json` 的 `section_query_source_sha256 = 06a1a6ea…`，c0–c8 全 PASS（原因码与冻结表一致）、n2a/n2c PASS、n2b observation、p2 PASS、n3 PASS（titles 正确）✅。

## ③ 未能验证的部分

1. 未跑真实跨仓消费入口（`sections-list` CLI→业务后果）；`artifact_read` 是"角色选择"还是"实际读取"仍属 I-05-B。
2. 未测生产规模（25.7M 行 / 49.7 GB）与并发/锁；未跑 CW 全量套件（仅 7 个合同文件）。
3. `role/title ↔ 内容` 一致性的**可行性**未验证（我只证明了当前不校验；未评估"用窗口首行对 title/ordinal"是否对所有真实文档成立——那会是一条新要求）。
4. 旧 RED 原字节不可恢复，其机器可核性无法补证（仅事实内容可引用）。
5. `_slice_roots=(derived,)` 未与 `service.query_source_bundle` 真实传参交叉验证（按代码路径判定）。
6. attempt 目录 MAX_PATH 行为未系统测。
7. oracle 前像 14924 B 的**来源**无法判定（我实测 r3 末态 23204 B；未找到任何 14924 B 的中间态文件）。

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
