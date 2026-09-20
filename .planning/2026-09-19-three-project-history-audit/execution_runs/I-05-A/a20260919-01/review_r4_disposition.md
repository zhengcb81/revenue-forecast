
---

# r4 — 第三次复审（P1-A/B/C）处置（追加式；**未自签**）

第三次复审 verdict：`changes_required`，**单根因**。已按复审指定的最小修法修复并留下红→绿变异证据。

## r4.1 根因确认

`_window_matches` 是**自证**的：它先 `body.find(needle)` 定位片段，再令
`start = found + char_start - origin`。于是
`body[start:start+len] == fragment` 恒成立（窗口是从片段反推出来的），**记录的偏移从未参与判定**。

后果正是复审三条：

- **P1-A**：任何"落在 body 范围内"的 `char_start/char_end` 都被标成 `source_window`；
- **P1-B**：偏移改坏后落到 `substring_only` 分支，而该分支仍 `return None` ⇒ 等价于修复前行为；
- **P1-C**：`if not bodies: return None` 把"候选集为空"当成"无来源"放过。

## r4.2 修法（严格照复审条目）

1. `_window_matches(fragment, bodies, char_start, char_end)`：对**每个候选 origin** 断言
   `body[origin+char_start : origin+char_end].strip("\n") == fragment.strip("\n")`；
2. 无任何 origin 通过 ⇒ `sections_binding_error`（**拒绝**），不再降级为 `substring_only` 通过；
3. `if not bodies:` ⇒ `sections_no_normalized_source`（**fail-closed**，消息含"没有可读的 normalized 工件"）；
4. `window_match` 三态收紧：`source_window` 只能由第 1 条命中产生；`substring_only` / `no_source`
   **只能是拒绝原因**（`_windows_match_or_block` 里它们都返回非 None）。

**追加的一条约束（实测必需）**：窗口必须与文档自身的**行边界对齐**（`_aligned()`：`start == 0` 或
`body[start-1] == "\n"`，且 `stop` 落在行尾/文末）。理由已实测留证：只有"逐 origin 比较"时，
`origin-1` 那种差一 origin 会重新吸收被伪造的偏移——+2 偏移伪造仍命中（我先写成
`for base in (origin, origin - 1)`，实测 `I1(+2)` 仍 `source_window`；去掉该松弛并加对齐约束后
`I1` 变为拒绝）。trim 语义本身不变（`oracle.md §3.1.1`）。

## r4.3 变异证据（红→绿）

`evidence/p1-mutations.json`（脚本 `scripts/w05a_p1_mutations.py`，可由第三方复跑）：

| 注入 | 修复前（`iso/prefix_r3/section_query.py` = `5fbbe49a…cac1`） | 修复后（`iso/fixed/section_query.py` = `06a1a6ea…ceb7`） |
|---|---|---|
| `I1` 两个偏移 +2（内容不动，index 与行 hash 同步） | `returned`，`window_match = [substring_only, substring_only]` | **`refused`**，`sections_binding_error` |
| `I2` 两个偏移 +5 | `returned`，`window_match = [substring_only, substring_only]` | **`refused`**，`sections_binding_error` |
| `I3` 所有 `normalized` 行置 `failed` | `returned`，`window_match = [no_source, no_source]` | **`refused`**，`sections_no_normalized_source` |

脚本在每次查询前**断言被测模块自身 sha256** 等于报告记录的哈希 ⇒ "读到旧模块"不可能伪装成修复。
关于 +1 vs +2：冻结的 trim 语义会把边界换行符剥掉，因此 +1 位移在**修复后**仍可能复现同一段文本；
+2 把内容字符移出窗口，是决定性伪造。该事实已写入 `evidence/README.md` 与 `oracle` 附录 C.2。

正例未被误伤：`c0` 仍 PASS，两片 `window_match = source_window`、`window_positions = [[0,1],[0,1]]`。

## r4.4 复核性数字更正（保留原值 + 说明）

| 项目 | 复审指出 | 我此前的值 | 以实测为准 | 说明 |
|---|---|---|---|---|
| 新增回归用例数 | 文件实际 25，声明 18 | `commands.json C14` 写 "18 passed" | **25 passed** | C14 记录已改；原 "18" 保留在 `declared_r2` 字段并附更正说明；**未改动任何测试来对齐旧数字** |
| `section_query.py` 最高函数复杂度 | 机器实测 9 | 我在 r2/r3 文里写过 10、11 | **最终 11**（机器实测，r3 阶段为 9；r4 新增对齐约束后为 11，仍 ≤ 冻结 12） | 三个值都如实保留并标注测量时点 |
| `changes.diff` 行数 | 我写过 846，实测 812 | 846 | **860**（最终字节） | 846 是 r3 修订中的中间值，812 是 r3 收尾值，均保留；以最终重生成的 860 为准 |
| 拒绝探针数 | 我写过 "10 rejected" | 10 | **9 / 11** | 11 个探针中 m5 复现版本死锁（`completed=0`）、m6 回退旧 VALID 行，故"拒绝"恰为 9 |

## r4.5 oracle 附录 A.2/A.4 更新方式

**只追加**：新增**附录 C**。正文、附录 A、附录 B 一字未改。C 开头明确写出
"附录 B.1/B.2 中 'substring_only 是降级标注、源窗口命中即可通过' 的表述已过时，以 C.1/C.2 为准"，
并附前像大小（追加前 `oracle.md` = 14924 B）。A.2 的原因码表与 A.4 的 C7 判据**仍然有效**，
附录 C 只新增 `sections_no_normalized_source`。

## r4.6 旧 RED 字节：如实登记为缺口

`after/cmd-tests-i05a.stdout.txt` 在 r2 阶段曾是 03:13:56 的 `3 failed / 15 passed` 输出；
A2 处置时被最终字节的 GREEN 运行**整体覆盖，原字节未另行留档，已丢失**。
丢失时点 = A2 处置（r3/r4 之间）；原因 = 直接重跑覆盖。
该 RED 运行的事实内容仍可引用第四次复审报告中的原文与栈
（`E AttributeError: 'list' object has no attribute 'get'` @ `section_query.py:190`），
但**原始文件不可复算**，已登记于 `oracle` 附录 C.4 与 `handoff.open_questions`。**未补造证据。**

## r4.7 本轮实际的命令与 raw rc

| 命令 | raw rc | 要点 |
|---|---|---|
| `pytest tests/contract/test_i05a_section_qualification.py`（最终字节） | **0** | `25 passed` |
| 全量隔离回归（7 个合同文件） | **0** | `88 passed, 1 deselected`（b10 读链 + 复杂度两个 ratchet 通过） |
| `w05a_p1_mutations.py`（P1 红→绿） | 0 | I1/I2/I3 均 `returned → refused`，模块 sha256 断言通过 |
| `w05a_cases.py before|after` | 0 | before：c1–c8+n2a+n3 counterexample；after：c0–c8/n2a/n2c/p2/n3 全 PASS，n2b observation |
| `w05a_attack_probes.py before|after` | 0 | before **0/11** 拒绝（全部 returned）；after **9/11** 拒绝 + m5/m6 两个已知例外 |
| `section_query.py` 最高函数复杂度（机器自算） | — | **11** ≤ 冻结 12 |

## r4.8 新 hash 与隔离

| 文件 | sha256 |
|---|---|
| `iso/fixed/section_query.py` | `06a1a6eade3531dab0c66e14064f29a91898a4a16d627efa7d39b69371ebceb7` |
| `iso/fixed/section_extractor.py` | `0f201c6865cfbfc168df9069e141d4b874a991c9155668241c2ffb7c1a39f3f0` |
| `iso/prefix_r3/section_query.py`（冻结的修复前字节） | `5fbbe49ad1a36149581bb1ef6447f4d3dfa29c25113db1797b66ebafa3c2cac1` |
| `changes.diff` | 860 行（仅上述两文件） |

生产锚点 13/13 与卡片一致；CW porcelain = `[' M CLAUDE.md',' M README.md']`。
**DOWNSTREAM BINDING**：`revenue-forecast` HEAD 现在是
`66bd75f1250d310cee8157daa5c4a85ef41f6a36`（复审提到的 `ddc81ab` 是它的**祖先**；HEAD 因他人后续提交而漂移）。
本卡只做**只读 git 查询**，未在该仓任何路径写入，未 commit。

## r4.9 仍存在的缺口

1. **D-W05 OPEN-1 / OPEN-7 未签**（历史工件回填与重算、`as_of_date` 差异）——未自决。
2. **A2 覆盖掉的 RED 原始字节已丢失**（见 r4.6），不可复算。
3. 未跑真实跨仓入口 `sections-list` CLI 到业务后果；`artifact_read` 语义属 I-05-B。
4. 未测生产规模与并发；未跑 CW 全量套件；新原因码的其它消费方影响未穷尽。
5. `_slice_roots=(derived,)` 的收紧仍未与 `service.query_source_bundle` 实际传参交叉验证。
