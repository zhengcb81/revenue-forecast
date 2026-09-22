<!-- REM79 corpus NEGATIVE-A: lines pairing a universal quantifier with a same-line domain qualifier; frozen expectation: zero flags (oracle table below) -->

<!-- src: task_plan.md:1994 -->
`[^\s]+` 关闭了 **r4 与 r5 关闭过的每一个字符、以及两者泄漏过的每一个字符**，**只剩空格**（**域：95 个可打印 ASCII 字符 @ pre-break 位，shape `Bo<c>t\n`，树 r4/r5/r6；空白字符 `\t \r \v \f \n` 不在该域内且同样泄漏——见 F-REV-R6-02；本域限定由 r6 复审提出、父代理直接落于本行**）——而该位置的空格意味着值是**多 token 串**，即**已登记的 `C10` OPEN 形态**，不是 token 类的问题。
<!-- src: task_plan.md:1977 -->
⇒ **Round 75 节该引用已过时，以本节为准。** 更正写法**带域**：**在那 19 个探针上**，r5 的类关闭了那些探针所含的形态；**它没有关闭该族**——全字符扫描下仍有**七个单字符**放行凭据，其中三个（`&`、`'`、`|`）**是 r4 曾经关掉的**。
<!-- src: task_plan.md:1952 -->
例如：**任何含「只有 / 全部 / 没有 / 整个族」的句子，必须在同一行带一个可解析的域字段**，并在生成载体的脚本里**断言该字段存在**。
<!-- src: task_plan.md:2018 -->
⇒ **本轮起，r6 自己的载体按该规则书写**：凡「只有 / 全部 / 没有 / 整个族 / 零代价」形态的断言，**域写在同一行**。
<!-- src: findings.md:503 -->
  - **⇒ 判据**：**凡在载体里写「只有 X」/「没有 Y」/「全部 Z」，必须同行给出该断言的**域**（探针集、行集、树集）。**没有域的否定性断言，一律按未验证处理。**
<!-- src: findings.md:528 -->
  - **⇒ 判据（第三次立，必须换形态）**：**规则必须从散文变成机制。** 具体：**任何含「只有 / 全部 / 没有 / 整个族 / 零代价」的句子，必须在同一行带一个可解析的域字段**；生成载体的脚本**断言该字段存在**，缺失即拒写。**只写在散文里的规则，已经被证伪三次。**
<!-- src: findings.md:544 -->
  - **⇒ 判据（REM-78）**：**含「只有 / 全部 / 没有 / 整个族 / 零代价」的句子，必须带可解析的域字段；生成载体的脚本断言该字段存在，缺失即拒写。**
<!-- src: progress.md:800 -->
⇒ **结论句必须把「测量集」写进句子里**；**没有域的否定性断言一律按未验证处理**。
<!-- src: REMEDIATION_REGISTER.md:331 -->
| **REM-78** | 计划级 | **P2（方法）** | **「结论句必须带域」这条规则已被证伪三次**（r3 / r4 / r5）。**只写在散文里的规则不生效** | **待机制化**：含「只有/全部/没有/整个族/零代价」的句子须带可解析域字段，生成脚本断言其存在 |
<!-- src: REMEDIATION_REGISTER.md:291 -->
**没有域的否定性断言，一律按未验证处理**。
<!-- src: execution_runs/I-14-D/a20260919-01/review.md:382 -->
> `[^\s]+` closes **every character r4 or r5 closed and every character either of them leaked, except the space** — 域=95 个可打印 ASCII @ pre-break 位、shape `Bo<c>\n`/`Bo<c>t\n`、树 r4/r5/r6；空白字符 `\t \r \v \f \n` 不在该域内且同样泄漏 — which is the registered `C10` OPEN shape, not a token-class question.
<!-- src: execution_runs/I-14-D/a20260919-01/review.md:415 -->
- r7 round findings — all INFO, none blocking: **F-REV-R7-01**: the pre-r7 bytes of `handoff_r6.json` were never pinned, so that carrier's r6-content claim is verified field-by-field and by JSON validity, not by reconstruction (domain: that one carrier; all other carriers have pins the reviewer reproduced). **F-REV-R7-02** (record nit): the carriers' `--src iso/product_narrow_r6/src` forward-slash notation does not reproduce the pinned measure-file bytes; the pins were produced with `--src .\iso\product_narrow_r6\src` (+5 JSON bytes from escaped backslashes) — counts, rc and verdict identical either way (domain: the two files in `_r7_measure_20260922/`). **F-REV-R7-03**: `review.md ## r7` and the handoff r7 block do not restate the full carried list; it survives via the untouched `## r6` section — not a closure (domain: those two r7 texts).
<!-- origin: this oracle's own text; appears verbatim in oracle.md section 3 as line O1 -->
凡含「只有 / 全部 / 没有 / 整个族 / 零代价 / 无一 / 每一个」或 EN `only` / `all` / `none` / `every` / `whole family` / `zero cost` 形态的断言行，必须同行带域字段（域：本 oracle 冻结词表，§3）。
<!-- origin: this oracle's own text; appears verbatim in oracle.md section 3 as line O2 -->
本 oracle 的每一个期望行都同时登记 file、line 与 expect，缺失同行域的登记按未验证处理（域：§5 期望表；机器表 = oracle_table.json）。
