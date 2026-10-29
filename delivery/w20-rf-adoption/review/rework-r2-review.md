# W20 R2 定点补完审查记录（rework-r2-review，2026-10-29）

对应 ROOT 第二轮返工单：`company-wiki/docs/plans/du11-source-closure-2026-10-18/review/w20-reception-r2-20261029/RETURN_RF.md`（受审 HEAD `b2979af6`、代码 `e4657377`）。R1 三项已被 ROOT 确认关闭（返工单"已关闭，保留成果"节）。本文件记录 R2 两项修复（`956b51d4`）+ 复审 P3 收敛与墙钟 flake 收敛（`f75c9fe2`）的独立审查结论。此前各轮审查（initial/final/rework-review）保留不覆盖。

## R2 返工复审（2026-10-29，全新独立 agent，复审 956b51d4）

### 两项裁定（全部独立探针实测，9 组探针在 repo 外自清）

| 返工项 | 裁定 | 证据摘要 |
|---|---|---|
| RF-R2-01/P1 claim 材料边 | FIXED | ROOT material_probe 场景（同capture两次真实consume、CEO vs 表格行、同claim_id/param、A forecast配B receipt）→ B span unverifiable+`receipt_claim_material_mismatch`、cited_by空；A+A正例 used；混合双回执 invalid 不吞 valid；产物内嵌 claim locator/excerpt_sha256 矛盾各自命名拒绝；缺字段→`material_field_missing_unknown` info 宽松不加门禁；/3 多父投影正例仍 used 零假诊断（claim.locator==structured_value.source_locator）；合法多证据（两span两claim同参数）双 used 无误伤；合同逐行对齐 consume `_claim`/`_source_locator`，无字符串金标（grep 验证），索引一次建立 per-dep O(1) |
| RF-R2-02/P2 zlib 归一 | FIXED | 19B 坏 DEFLATE 两种形态真实 CLI 子进程 → exit 2、`input_decompress_failed`、无 traceback、无半输出；except 精确四元组（含 zlib.error，无裸 except）；限额不动；正常/恰好limit/超limit/截断边界全保持 |

strip 语义裁定：`text_sha256` 内部先 strip 再哈希（contracts/evidence.py:173），consume 写的 `text_sha256(raw_text)` ≡ 引擎校验值，audit 比对值与 claim 字段恒一致，无空白敏感性（端到端探针验证）。

### 新发现

**[P3]** /1 span 的 structured_value 含 stray `source_locator` 键时合法链被误报（审计按键存在判投影，consume 按 context schema 判）——fail-closed 方向、已知 writer 不产出该形状、不阻塞；建议按 schema_version 判投影。另确认 `material_field_missing_unknown` 每 dep 至多 1 条 info，合法 run 为 0 条，无爆炸。

**OPEN_findings=[P3]，verdict：PASS（两项返工 FIXED）**；测试实测 41 passed（9.03s）+ 回归 76/133 passed + ruff clean。

## P3 收敛复验（同一独立 agent，复验 f75c9fe2）

修复：span_material 按 `context.schema_version == "revenue-narrative-context/3"` 判 projectedness（与 consume 适配器同规则），键存在判断移除；新增守护测试 `test_legacy_span_with_stray_source_locator_key_stays_legacy`。

复验：**P3 FIXED**（9 组探针全量重跑无回归；/1 stray 键场景反转确认 used 零假诊断；/3 投影、材料交换、矛盾、缺字段、多证据、strip、坏 DEFLATE 全部保持）。先在的墙钟 flake（`test_scaling` 的 `t1 > 0.02` 下限在快机器偶发击穿，实测中位 14.6ms 与修复前同量级、与本次改动无关）由作者随后收敛为恒执行的"比例+绝对余量"断言 `t2 < 4.0*t1 + 0.05`，5 次连跑稳定。

**OPEN_findings=[]，verdict：PASS**

## 最终交付绑定（R2 轮）

- implementation/tested/reviewed commit：`f75c9fe2`（R2 链：`b2979af6` → `956b51d4` 两项修复 → `f75c9fe2` P3 收敛+flake 收敛）
- 改动文件 SHA256（f75c9fe2 时点）：
  - `tools/narrative_adoption_audit/audit.py` = `f140cc0f3331e7076b7edbcac2b533e19c8215ea42b8f0bb8f3d5464317f7fb0`
  - `tools/narrative_adoption_audit/cli.py` = `436c6487cca3d6d4591b7237098d49f8275d035b70ebf07d5684c08a6147ff35`
  - `tests/test_w20_narrative_adoption_audit.py` = `d4dccbc6a4bf4f7413c7ee9d3597457d0708c345297e125174b372b346f53880`
  - `tools/narrative_adoption_audit/README.md`、`tests/test_w20_narrative_adoption_e2e.py` 本轮未改动（仍为 8b221153 时点 SHA）
- 新增命名码：`material_field_missing_unknown`（info）；CLI 新归一 `zlib.error` → `input_decompress_failed`
