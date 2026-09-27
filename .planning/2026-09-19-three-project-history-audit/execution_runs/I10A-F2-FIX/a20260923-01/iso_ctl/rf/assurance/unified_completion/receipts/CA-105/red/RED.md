# CA-105 RED 证据

> 规则：RED 从公开/生产入口触发、先证明当前行为确实失败、由独立 oracle 验证。

## RED-A：场景覆盖依赖 ID 文本出现，无机器 result registry

旧 receipt 的 `scenario_results` 只记录 id/status/note 文本，无 evidence path、
fixture/sample hash、oracle——SCENARIO 文本出现即可被 closure 当作覆盖。

## RED-B：无机器可算的 required 总数

197 场景从未被机器枚举；closure 无法回答"缺哪一项"。本卡构建 registry 后首次
得到机器总数 197（旧 95 + 新 102，交集 0——含新矩阵的 AUD2-01..08，实测 94+8=102
与冻结声明一致）。

## RED-C：placeholder 状态可假绿

旧 receipt 存在 `pending:FC-*` 式 fixture 与 `scenario-defined` 预算文本；新
registry 要求状态仅为 machine enum 且 evidence_path/fixture_hash 显式。

## RED-D：T1 替代 T2 无门

旧流程对 tier 无 machine 记录；新 registry 每场景记录 tier（矩阵表格行可提取
部分，其余 `matrix_defined` 如实标记）。

## 新工具对照（本卡实现）

`uc.scenarios`：解析两个冻结矩阵 → 197 场景注册表（source/tier/status/evidence
path/fixture hash/oracle）→ verify（源 hash + 场景集合漂移检测）→ closure_report
（unsatisfied 数机器可算；当前 197/197 unsatisfied = 阶段 B 的正确诚实状态，
随 C~G 阶段逐项填充）。
