# P7-RF 交接：经营校准绑定与支持范围诊断

绝对路径：`C:/Users/郑曾波/.codex/worktrees/m3-acceptance-20261010/revenue-forecast/.planning/p7-rf-scoped-calibration/HANDOFF.md`（同目录 handoff.json）。

## 1. 结果

**engineering_complete**（本卡写集内）。共用校准诊断缺陷已修：`_calibration` 现在消费 observation `binding_status` 并把 calibration scope/output 绑定到真实 native DAG；新增只读诊断 CLI `economic-support-diagnostics/1`。未做（属 MAIN/真实研究）：三仓集成与安装、版本接线（MAIN patch）、R16/R17/R18 真实公司研究（见 remaining）。

## 2. base / branch / delivery

- base：`6883bf00548abb9891eab6762aeaa89e3898b202`（4.2.0 / opt-in 3.9）
- branch：`codex/p7-rf-calibration-binding`
- delivery HEAD：`05aa2661c9cdc34cb7e9ce3cf7e83b43bee7f556`（本 HANDOFF 所在的后续 docs commit 见 handoff.json note）
- normal hooks commit：ruff / mypy public contracts / host assumption guard 全部 Passed（见提交输出）；push 状态见 §6。

## 3. 根因 → 正负控 → 实现 → 结果（真实命令/exit/日志，路径相对本 PWF）

| 阶段 | 命令 | exit | 日志（sha256 前 16） |
|---|---|---|---|
| 复现 | attempts/m1/repro.py（三反例纯函数反例） | 0 | 输出记录于 findings.md M1 节 |
| RED | `python -X utf8 -B -m pytest tests/test_scoped_calibration_support.py -v` | 1（5 failed=反例, 2 passed=正控） | attempts/m1/red_test_scoped_calibration_support.log（97a2d362…） |
| RED | `python -X utf8 -B -m pytest tests/test_research_support_diagnostics.py -v` | 1（5 failed=CLI 缺失） | attempts/m1/red_test_research_support_diagnostics.log（6da049c1…） |
| GREEN | `python -X utf8 -B -m pytest tests/test_scoped_calibration_support.py tests/test_research_support_diagnostics.py tests/test_research_evidence_roles.py -v` | 0（25 passed） | attempts/m2/green_responsibility.log（2225ce4c…） |
| static | `ruff check <6 files>` + `mypy scripts/research_support_diagnostics.py scripts/research/native_dependencies.py` | 0/0 | attempts/m2/static.log（fc315d60…） |
| E2E | `python -X utf8 -B %TEMP%/p7-rf-scoped-calibration/m3_e2e.py`（真实 build_auditable_case.py + run_target_measurement_e2e.py 正负控；脚本存档 attempts/m3/m3_e2e.py） | 0（ALL_PASS 23/23） | attempts/m3_e2e.log（da721f7c…，含输入/linked-input SHA） |
| 兼容 | 应用 MAIN_INTEGRATION_PATCH.patch 后 `pytest tests/test_data_contract.py tests/test_schema_compatibility.py tests/test_m3_schema_compatibility.py tests/test_m3_period_flow_contract.py tests/test_registry_artifact_audit.py tests/test_rf_coverage_report.py` | 0（88 passed；回退后 5 pin 失败 + 4 rf_coverage 下游 ERROR 复现） | attempts/m2/compatibility_main_patch_trial.log（9803fcd7…） |
| 独立复核 | 只读 agent 自建反例验证两不变量 + API 形状 + 3 个对抗探针 | 全 PASS | attempts/m3/independent_review.md（0638561e…） |

E2E 要点：正控 referenced_range/公式值 100/110/120/engine 4.2.1/stable-fsum/1/snapshot/markdown 渲染/诊断 CLI SegmentA FY2026 supported×3；负控（CE1）unverified + `conversion_observation_unverified_scope:<pid>:<claim>`、magnitude 空、consolidated_forecast 与 confidence.score 与正控逐字节一致（诊断不改算术）。正负 input.json SHA 相同（b515d368…），差异仅在 research.json。

## 4. 对外 API / 兼容 / MAIN 最小接线

- 保持：`analyze_operating_research(data, validated)` 签名与 research-adequacy/1 顶层键、operating-research/1 输入结构、收入 Low/Base/High 算术、stable-fsum/1 confidence 总分、来源 API 与 period 合同、无 optional research 返回 None。
- 变化：带 unbound conversion / 非 native scope 的输入在 4.2.1 下 re-emit 为 unverified（旧 4.2.0 输入/报告原字节保留，按 pinned 4.2.0 emitter 校验）；诊断新细节在新 CLI 输出，revenue_report 通用展示未改。
- **MAIN 接线（必须）**：应用本 PWF `MAIN_INTEGRATION_PATCH.patch` —— 5 处 version-pin 断言 4.2.0→4.2.1（tests/test_data_contract.py:463、tests/test_schema_compatibility.py:28、tests/test_m3_schema_compatibility.py:41、tests/test_m3_period_flow_contract.py:115,345）+ `scripts/schema_compatibility.py` 3.7/3.8 emit 行加 "4.2.0"（保持旧 4.2.0-emitted 3.7/3.8 工件为 documented emitter；3.9 行已含）。不应用则分支存在 5 pin 失败 + test_rf_coverage_report 4 个下游 ERROR（其子进程要求 test_schema_compatibility exit 0）。

## 5. 保护 / 恢复 / 费用

- TEMP：全部证据先复制入 PWF attempts/，随后删除 %TEMP%/p7-rf-scoped-calibration（含 m1/m2/m3）、%TEMP%/p7-rf-review、临时基线 worktree（git worktree remove，共享对象库未复制 870MB 历史）。无全湖备份。
- 原件/配置/邻仓：canonical assurance 3 文件与 output/ 为 owner WIP，未读作夹具、未改、未提交；fixtures 全部新生成合成件；未改 golden/hash。
- registry：每个 run_forecast/snapshot 子进程 REVENUE_PUBLICATION_REGISTRY 指向 owned TEMP；实测 publications.jsonl 仅落 m3/{pos,neg}/native/ 内。
- 外部 provider/model 调用 0，新增费用 USD 0（harness 自身推理不冒作项目供应商调用）。
- 环境噪声记录（非本卡）：ca202 c1_samples 在干净 base 即失败；zr806/zr1004/zr709/ca302/fc1307a 等 journey/canary/vendored 测试在 base 树随并行会话对 sibling 实况目录的改动而翻转（同一绝对路径、时间依赖，已双向复现）；compatibility_manifest 等 "only in base" 为基线 worktree 的 git 状态依赖。

## 6. CI / 安装候选 / 限制

- CI：exact CI 未触发（分支仅本地提交时记录 not_triggered；push 后状态见 handoff.json）。
- 安装候选（MAIN 执行）：`scripts/research/evidence_roles.py`、`scripts/research/native_dependencies.py`、`scripts/research_support_diagnostics.py`、`scripts/contracts/constants.py`（仅版本常量）、`CHANGELOG.md`、`SKILL.md`（3 处定点）、`references/evidence-role-calibration.md`、`references/economic-support-diagnostics.md`、`tests/test_scoped_calibration_support.py`、`tests/test_research_support_diagnostics.py`、`tests/fixtures/scoped_calibration_support/**`、MAIN patch 内 6 文件。
- 限制：诊断 CLI 为 validation-level（run_forecast 层的模型 driver 规则仍由计算层强制）；诊断不等于买方经济质量认证。

## research_remaining（不因本卡关闭）

原 R16/R17/R18 真实公司幅度、管理目标/并购控制、三年路径、时序与 joint stress 仍需原件研究与四独立审查；本卡工程通过不把这些 unsupported 自动凑成三年成功。W09 真实研究缺口保留。
