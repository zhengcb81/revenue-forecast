# RED.md — ZR-1009 legacy 路由/代码删除门（阶段 I 收官卡）

## 探针（全部在当前机器实跑）

- **G1 无 ZR-1009 验收套件**：glob `tests/**/*zr1009*` → 零命中。
- **G2 无删除门组合验收**：CA-003 codegraph_freeze（commit 绑定/统计/sentinel）、CA-004 legacy_disposition（71 FC 处置）、CA-109 legacy_gate（caller 扫描/分类）均存在但各自独立；无"caller 诚实报告 + ≥2 周期 zero-hit + N-1 批准目标 + 删除后全绿"组合验收。
- **G3 真实现状（只读确认）**：legacy-gate 对三仓扫描 → verdict=callers_found（2 findings：revenue .github/workflows/quality.yml → verify_closure_ledger/closure_ledger，successor CA-201）——诚实证明删除未批准（CA-304 门保持）；legacy_disposition counts {I:31,C:26,S:9,P:5}、closure_items 5（FC-150x class P）。

## 既有能力（不重复建设）

- uc.legacy_gate.scan_callers/classify/report；uc.codegraph_freeze.freeze/verify/index_repo（scratch 三仓真实 CLI 往返已在 test_codegraph_freeze.py 证明）；uc.legacy_disposition.parse/validate/build/verify（71 FC 行 + 10 waves + 精确计数 + 无环）。

## 结论

G1~G2 为真实缺口（`still_missing`）；实施 = revenue `tests/test_zr1009_legacy_removal.py`（9 tests：C1 caller 门诚实报告/scratch 隔离；C2 两轮 freeze→verify zero-hit + 重现 fail-closed；C3 disposition 验证 + N-1 批准目标；C4 删除后索引漂移检测 + 新 freeze 全绿 + 门 isolated），产品零改动、零真实删除。
