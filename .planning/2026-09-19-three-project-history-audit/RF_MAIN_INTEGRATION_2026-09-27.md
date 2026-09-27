# revenue-forecast 主线整合记录（2026-09-27）

## 基线与范围

- 整合基线：已直查远端 `main`、`fcap` 均为 `ee0a82bfd1eec935cf4e567eb42f0ef79efa0226`。本地旧 `main` 不作为基线；phase-14、phase-19 与复审工作树均无相对该基线的独有提交。
- 本次只整合 RF 未提交的 `assurance/unified_completion/uc/{scenarios,closure}.py`、相应测试、四份计划记录，以及 `DEF-I00C-GATE-NEG`、`DEF-MSFT-CANONICAL-DUP`、`T3-DIAG` 的审查证据。基线之后的 company-wiki 产品改动不属于本次 RF 提交。
- `assurance/runs/weekly_alert.jsonl`、`weekly_manifest.json` 与新周任务日志构成一个独立的失败运行记录；三件均留在原工作树，待周任务归属方处理，不以本次 RF 缺陷提交部分纳入。

## 证据空间与隔离

- 三组证据逐文件核对 SHA-256：`DEF-I00C-GATE-NEG` 初次筛入 20 件／95,865 B；`DEF-MSFT-CANONICAL-DUP` 的 handoff 明列 98 件交付文件，共 22,620,151 B；`T3-DIAG` 初次筛入 7 件／30,370 B。DEF-I00C 的 `tmp/` 不在已签交付清单，可排除；MSFT 的 `rig/w/` 和 `rig/harness/fixture/` 虽含重复测试字节，却在已签清单内，故本批完整纳入，待未来另行重签轻量归档规则后再考虑压缩。
- 三组历史证据的原始换行本身属于被审字节，`.gitattributes` 仅对这三组路径禁用换行转换；MSFT 98/98 个已签文件暂存 Git blob 与对应原始字节相同。代码与计划正文继续沿用仓库现有 LF 约定。
- `RATCHET-FIX-A/B/C` 是 company-wiki 棘轮工位证据，仍在独立处理；RF 主线不打包这些在飞目录。隔离候选仅从 RF 已提交基线和逐文件固定的本地候选构成，测试不读取 company-wiki 脏工作树作为通过依据。
- 整合时只按上列明确路径暂存，禁止 `git add -A`；Git 在受限沙箱中将大量历史 `execution_runs` 误报为删除，已用正常权限复核原工作树无这些删除。

## 放行判据

1. RF 定向 `test_scenarios.py`、`test_closure.py` 通过；按 owner 后续 §四十三，缺哈希但有证据路径必须拒绝并显示 `evidence_hash_pending=1`，无路径仍拒绝，缩小后继卡不能抹去原义务。
2. 独立临时目录重跑 9 个冻结负例，要求 9/9 拒绝且正向控制通过；完整 `assurance/unified_completion/tests` 的失败须分类，不能用已有旧复审代替最终字节复核。
3. 暂存清单、`git diff --check` 与 hooks/远端 CI 审查通过后，才快进远端 `main`；推送前后核对远端 SHA。`DEF-MSFT-CANONICAL-DUP` 的生产 G3 回放、company-wiki 推送、R4 位置透明 reader 均未由本次 RF 并线放行。

## 与 company-wiki R4 的接口边界

RF 已提交的 `scripts/company_wiki_source.py` 仍直接读取 company-wiki 内部 DAG 与 `canonical_path`。这是 R4 C.local 待迁移的既有债；本批 assurance 变更未增加路径耦合。company-wiki 未提交的 `artifact_dag.py` 会改变 summary 依赖，故本批不能把其脏工作树算成 RF 验收基线。未来真实来源正向 E2E、字节哈希和移位身份不变验收仍归 R4 大节点。

## 本轮已执行的门禁及未放行事项

- 隔离候选的场景与三仓报告定向测试：22 passed；ruff 通过；冻结九负例的临时可移植副本：9/9 拒绝、正向控制通过，N6 registry 路径仅改为隔离 `UC_ROOT`，原冻结证据字节未改。
- RF 原工作树的完整 pre-push gate：ruff、compile、mypy、meta/binding、已安装技能一致性、真实 roots E2E 与真实数据套件均 GREEN。跨仓真实年报离线 E2E：S2/S3/S5/S6/S4 五项 PASS，`network_scope=none`、`production_writes=0`，独立临时目录已清理。S2 是当前 review gate 的预期拒绝，不是正向预测成功。
- 候选 `scenario-verify` 读真实 197 项：`unsatisfied=197`、`closure_ready=false`、`evidence_hash_pending=197`。这是诚实保留的证据缺口；`fixture_hash` 不可用证据 JSON 的 SHA 冒充。后续须分别做证据字节绑定与场景语义复审（含 READ-10/READ-11），才能声明 CA-105 完成。
- 原 RF 工作树在候选冻结后出现的 `findings.md` 与 RATCHET 计划追加段存在控制字符、断词和在飞状态；不混入本次已审查批次。周任务失败记录三件也独立处理。
