# FC-1003 WU 卡片 — 95 场景矩阵全覆盖（机器覆盖门）

> 创建 2026-08-12（FC-1002 accepted 后）。Owner: revenue（三仓引用）。状态 pending。

## 现状盘点（2026-08-12）
- registry: 95 mandatory（`compatibility/scenario_registry.json`，FC-102 冻结）。
- receipts 覆盖 58/95（三仓 11/12 receipts 的 scenario_results 提取）。
- 缺口 37：AUD-01~08（Phase 11/FC-1105）、UJ-01~08（Phase 15/FC-1503）、IDX-01~08（FC-1004）、PORT-02（FC-1004/1205）、DL-01/04/05/06/10、LT-03/04/06/09、EX-02、SAFE-05/06。
- **DL/LT 测试存在**（filing-fetch test_fc803_minimal_download.py + company-wiki latest/gap/close_gap 测试）——receipt 用 `LT-09/DL-04` 组合标注，标准单 ID 扫描漏掉。
- **问题本质**：无机器覆盖门；标注格式不统一（组合 ID、receipt-only、无标注测试）。

## 设计（scenario_coverage.py，机器门）
1. **覆盖证据源**（并集）：
   - 三仓测试文件 docstring `SCENARIO: EX-01 EX-02 ...` 标注（标准格式，允许组合拆分）。
   - 三仓 receipts scenario_results（ID 容错：`A/B` → A、B）。
2. **范围过滤**：按 registry tier_entries 的 owner_fc——只要求 owner_fc 属已 accepted 的 FC 或本 Phase 前；AUD（FC-1105）、UJ（FC-1503）、IDX（FC-1004）、PORT（FC-1205/1004）自动豁免（非本 FC 范围）。
3. **输出**：覆盖矩阵（ID × tier × 证据源）+ 缺口清单 + exit 非零当有缺口。
4. **测试**：门自身的测试（缺口检测、豁免、组合拆分）。

## 步骤
1. 实现 `compatibility/scenario_coverage.py` + `tests/test_scenario_coverage.py`（RED→GREEN→mutation）。
2. 跑门 → 精确缺口清单（豁免后）。
3. 给已有测试补 SCENARIO 标注（receipt 已证的 58 ID 映射到测试文件）。
4. 真缺口补测试（DL/LT/EX-02/SAFE-05/06 的 Phase 8 测试标注或补）。
5. 全量 + pre-commit + receipt + reviewer。

## 执行纪律
- 16 步；改测试文件后提交前 sync_installations --apply（R4.2）。
- receipts: revenue-forecast/assurance/fc/FC-1003/。
