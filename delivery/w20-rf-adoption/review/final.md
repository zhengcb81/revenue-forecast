# W20 独立复审报告（final，2026-10-28）

复审对象：commit `8b221153`（分支 `codex/w20-rf-adoption-20261028`，树干净），修复 diff `5f88ac3f..8b221153`。复审 agent 为从未参与实现与初审的全新独立审查者；方法：逐条读码核对 + 独立 python 探针（真实 DU11 线材、真实 `consume_narrative_input`、真实 `run_forecast`、正式形状约束文档、引擎 `parameter_uses` 交叉验证，探针均在仓库外临时目录且已清理）。

## 初审发现逐条核销

| id | 判定 | 证据 |
|---|---|---|
| F1 (P0) | FIXED | `_span_support_use` 重写（audit.py:569-617）：仅 `use=="support"`（或 pre-/4 结构分区）授予支撑；context_only/unresolved 显式标记独立跟踪；/4 未分组→unresolved（与 reader 拒绝同构）。消费点（audit.py:806-819）对 context/unresolved 一律 not_used_when_provable，有回执绑定发 `context_span_bound_as_support` 且不服从。独立探针 15/15 过（含 /4 伪造回执、/2 与 /4 混合视图、/1 不回归） |
| F2 (P0) | FIXED | 约束索引按类型重写（audit.py:389-419）与引擎 `_constraint_uses`（dependencies.py:117-136）逐类型同构；elimination-only 差分探针：audit wired == 引擎 uses；intact elimination 回执判 used（虚假 not_used_when_provable 消除） |
| F3 (P2) | FIXED | `receipt_formula_refs_missing`（info）宽松继续；非 None 仍比对→`receipt_run_mismatch`；探针双向验证+单测 |
| F4 (P2) | FIXED | 新增第16组三个 /4 测试（真实 /4 线材经真实契约+真实 adapter） |
| F5 (P3) | FIXED | KNOWN_CONSUMPTION_FIELDS 与真实 /3 回执构造精确匹配 |
| F6 (P3) | FIXED | span `source_sha256` 回退 `parent_source_refs[0].content_sha256` |
| F7 (P3) | FIXED | `resource` 收敛 `{max_items, items}`；items_capped 零残留 |
| S2-1 (P1) | FIXED | 负载 2400/4800 + `t1 > 0.02` 下限；实测 t1=0.029s、ratio=2.49，比例断言真实执行 |
| S2-2 (P1) | FIXED | BIREN_INPUT 逐字节前后对比 |
| S2-3 (P1) | FIXED | CLI 失败分支（缺失/坏JSON/非对象/max-input-bytes）全测，exit 2 + 命名 stderr |
| S2-4 (P1) | FIXED | 篡改 bundle→`narrative_wire_refused`→exit 0→不为被拒线材发明 item |
| S2-5 (P1) | FIXED | 错 formula_refs→unverifiable+`receipt_run_mismatch` |
| S2-6 (P2) | FIXED | e2e docstring 声明 guard 边界与入口无网络检视 |
| S2-7 (P2) | FIXED | `--pretty` 改 `open("x")` 独占创建；探针验证二次拒绝 rc=2 |

## 新发现问题（均为 P3 备注，不构成 OPEN）

- 审计接线闭包比引擎"略宽"两处残余（方向保守，真实合同形状下探针证明 wired == 引擎 uses）。
- 修复自带 sum_cap 测试 fixture 用了非法段键控形状（测试仍有效）。
- `--pretty` 分支无直接单测（独占创建由标准库保证且探针已验证）。
- 观感项：`context_span_bound_as_support` 诊断名在 unresolved 场合复用（detail 含实际标记）；约束 citation location 粒度收窄（ids 仍带 constraint_id/type/scenario）。

## 测试结果

- `python -B -m pytest -q --tb=short -p no:cacheprovider tests/test_w20_narrative_adoption_audit.py tests/test_w20_narrative_adoption_e2e.py` → 26 passed（17.61s）
- e2e 背靠背两次独立运行：2 passed / 2 passed，运行后 `git status` 零残留
- scaling 单独复跑 2 次均过

## 最终判定

allowlist 核对：`git diff --stat 0991e25d..8b221153` 恰 12 文件全在 allowlist 内。既有语义抽查无回归。

**OPEN_findings = []**
**verdict: PASS**
