# Findings — P7-RF

本卡完整已复现实证、根因与稳定接口见 IMPLEMENTATION_CARD.md §§1–3；这些是施工起因，不是本卡已经实施的结果。

写集只限本卡；MAIN保留AUTO共同接线/跨仓安装与并线。另两卡物理目录和源码写集不同，不等待它们的新接口。原件/配置/旧证据与其他ownerWIP不改。

环境/工具配置沿项目实际设置，不猜供应商或模型。默认项目provider/model/新增费用均0；外部harness自身推理不冒作项目供应商调用。已有累计USD20/2M与旧unknown保留。

RF历史跟踪约870MB，本次复用干净树避免再复制；不在本卡删除历史.planning。每个真实发现/失败追加于此，不覆盖旧证据。

## M1 实测发现（2026-10-10，独立harness）

1. 基线：`tests/test_research_evidence_roles.py` 11 passed（当前代码、未施工）。
2. 三反例全部复现（脚本见 attempts/m1/repro.py，输出见 attempts/m1/repro.log）：
   - CE1 三conversion observation scope→无关业务：binding=unverified_scope×3，calibration 仍 referenced_range，magnitude 仍支持 3 个未来输出。
   - CE2 三conversion observation period→FY2031：binding=unverified_period×3，同样误绿。
   - CE3 range端点observation+calibration.scope 同改无关产品：binding=unverified_scope（两端点），conversion仍bound，仍误绿。
   - 正控确认：基线 calibrated_document 中 reference_upper 不入收入DAG → binding=unverified_scope 但属合法独立参考（referenced_range 应保留）；reference_lower/conversion_* 均 bound。
3. 根因定位：`evidence_roles.py::_calibration` 仅检查 conversion 是否"被某条conversion observation披露"（parameter_ids 包含），不消费 `binding_status`；也不校验 calibration.scope 与 output 实际被哪个 segment 消费的一致性。
4. 关键既有机制：
   - `native_dependencies.observation_binding` 已产出 bound/unverified_scope/unverified_period/related_not_positive_support/historical_context/unverified_claim_binding。
   - `native_dependencies.parameter_scopes(data, parameters, pid)` 返回实际消费该参数的 segment 名集合，可判 output 真实 scope。
   - `_calibration` 现有 reasons 机制：reasons 非空即降级 unverified；status=="stress" 保持 stress；referenced_range 要求 status=="calibrated" 且无 reasons。
   - output scenario 已有硬校验（scenario in (None,"all",scenario)），情景交叉借用现已被硬拒。
   - confidence 强重算：`validate_confidence_recomputation` 比较整个 research_adequacy（源输入重算），诊断与输入同步篡改不构成绕过面（诊断非输入）。
5. 版本链事实：
   - `SKILL_VERSION`(constants.py)=ENGINE_VERSION=4.2.0；`schema_compatibility.SCHEMA_EMIT_ENGINES` 3.7/3.8 行={"4.1.0","4.1.1",ENGINE_VERSION}，3.9 行={"4.2.0",ENGINE_VERSION}。
   - 升 4.2.1 影响：version-pin 断言失败（test_data_contract.py:463、test_m3_period_flow_contract.py:115,345、test_m3_schema_compatibility.py:41、test_schema_compatibility.py:28；test_registry_artifact_audit.py:36 合成receipt用"4.2.0"字面量）；且 3.7/3.8 行升后不含"4.2.0"，旧 4.2.0-emitted 3.7/3.8 输出 output-mode 校验会拒——两处都在写集外。
   - 先例 d9e63597（4.1.1→4.2.0）：卡内只升 constants 版本常量+注释；CHANGELOG/SKILL/version-pin 测试接线放自己 .planning 的 MAIN_INTEGRATION_PATCH.patch（trial-verified），提交信息记录 9 个已知 baseline-diff 失败。本卡写集额外直接允许 CHANGELOG，故本卡直接写 CHANGELOG 4.2.1 节，其余接线同样走 MAIN patch+文档化失败清单。
   - tools/release_checklist.py 要求 CHANGELOG 有当前 SKILL_VERSION 节。
6. `tools/run_target_measurement_e2e.py:28` 自身已把 REVENUE_PUBLICATION_REGISTRY 指到其 output root；M3 仍按卡要求给每个子进程显式设 owned TEMP env 并核查路径。
7. 相邻面：test_native_research_bindings/test_published_foundation_roundtrip 只断言 mechanism_adequacy/inventory，不校准状态；golden_behavior_hashes.json 属 backlog/bank/capacity/subscriber/volume 域——均不受本次校准语义修复影响（实现后仍集中跑确认）。

## 冻结的新CLI样例（economic-support-diagnostics/1）

输入：native forecast input JSON（只读）。输出（stdout 或 --output 路径）：

```json
{"schema_version":"economic-support-diagnostics/1","input_sha256":"<sha256 of input bytes>","requested_years":["FY2026","FY2027"],"company":"<name>",
 "segments":[{"segment":"Segment A","entries":[{"scenario":"low","year":"FY2026","status":"supported|conditional|unsupported",
   "reasons":["...具体关系/ID原因..."],"supported_parameter_ids":[],"unsupported_parameter_ids":[],"calibration_ids":[],"claim_ids":[]}]}],
 "economic_truth_inferred":false}
```

只读：不写输入/来源/生产registry，不调用模型/下载；reasons 必须引用具体 calibration/parameter/claim ID，不允许单条 insufficient。

## M2 实施记录（2026-10-10）

1. 实现：`evidence_roles.py::_calibration(data)` 新增三类 scoped binding reasons（conversion_observation_<binding_status>:<pid>:<claim_id>、calibration_scope_not_native_business:<scope>、calibration_output_scope_mismatch:<output>:<scope>-><actual>，经 native_dependencies.parameter_scopes）；独立 range 端点不加 DAG 绑定要求（upper 正控保持合法）。`native_dependencies.py` 抽出 `segment_roots`（未展开 driver+recognition 根），`segment_ancestry` 复用，行为等价。
2. 新 CLI `scripts/research_support_diagnostics.py`：只读 validate+analyze，per segment×year×scenario supported/conditional/unsupported，reasons 含 calibration_not_referenced_range passthrough（带引擎原因）、calibration_scope_not_covering、no_optional_operating_research_declared；--output 拒绝覆盖已存在文件；无模型/下载/registry 写。
3. 版本：SKILL_VERSION 4.2.0→4.2.1（constants.py 仅版本常量+注释）；CHANGELOG 新增 4.2.1 节（写集内允许）。
4. MAIN_INTEGRATION_PATCH.patch（本PWF，76行，git apply --check 通过、双向 trial-verified）：5处 version-pin 断言（test_data_contract.py:463、test_schema_compatibility.py:28、test_m3_schema_compatibility.py:41、test_m3_period_flow_contract.py:115,345）4.2.0→4.2.1 + schema_compatibility.py 3.7/3.8 emit 行加 "4.2.0"（保持旧 4.2.0 工件为 documented emitter；3.9 行已含字面 "4.2.0"）。应用后 72 passed；回退后 5 failed 复现。
5. 静态：ruff（6文件）与 mypy（research_support_diagnostics.py、native_dependencies.py）均 clean，沿既有标准。
6. 责任 GREEN：test_scoped_calibration_support 8 passed（含篡改诊断不得绕过 strong recompute、stress 不变、FY27/Segment B 不自动支持）；test_research_support_diagnostics 6 passed；既有 test_research_evidence_roles 11 passed。
7. test_ca202_daily_t2_runner::test_c1_samples_check_sees_bound_artifacts 在干净 base 6883bf00 即失败（stash 双向验证）——worktree assurance 工件属 owner WIP 环境缺件，非本卡改动；全量套件双跑差分进行中。
