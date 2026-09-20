# evidence/ — I-05-A / a20260919-01

第三次复审（P1-A/B/C）要求的**变异证据**，可由第三方复跑。

| 文件 | 内容 |
|---|---|
| `p1-mutations.json` | 三次注入在**同一批**注入后 catalog 上、分别用 `iso/prefix_r3/section_query.py`（修复前）与 `iso/fixed/section_query.py`（修复后）查询的结果对比 |

复跑命令（隔离 venv，工作目录 = attempt 根）：

```
<attempt>\iso\venv\Scripts\python.exe -X utf8 -B scripts\w05a_p1_mutations.py <attempt>\iso\prefix_r3\section_query.py
```

脚本会：用真实 producer 建 3 个独立 catalog → 各自注入 → 对每个注入先写回 prefix 字节查询一次、
再写回 fixed 字节查询一次；查询前**断言**被测模块自身的 sha256 等于报告里记录的哈希，
因此"读到旧模块"不可能伪装成修复。

注入：
1. `I1_offsets_plus_one` —— 两个偏移同时 +2（内容不动，index 与行 hash 同步）。
   说明：+1 位移在冻结的 trim 语义下仍可能复现同一段文本（边界是换行符），故取 +2 作为决定性伪造。
2. `I2_offsets_way_off` —— 两个偏移同时 +5。
3. `I3_no_normalized_source` —— `UPDATE artifacts SET status='failed' WHERE artifact_role='normalized'`。

期望（修复后）：三条全部 `refused`，原因码分别为 `sections_binding_error`×2 与
`sections_no_normalized_source`；修复前三条全部 `returned`。

## 键名注记（第四轮复审 P3-3）

`p1-mutations.json` 的键名 `I1_offsets_plus_one` 实际对应 `mutation_detail.delta = 2`。
原因：冻结的 trim 语义会剥掉边界换行符，+1 位移在修复后仍可能复现同一段文本；
因此取 +2 作为决定性伪造。键名不改（避免破坏既有字据的稳定引用）。
