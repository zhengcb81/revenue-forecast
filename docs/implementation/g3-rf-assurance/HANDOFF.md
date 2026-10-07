# G3-RF-ASSURANCE 交接（HANDOFF）

- 施工仓：`C:/Users/郑曾波/Projects/_g3/RF-ASSURANCE/revenue-forecast`
- 分支：`codex/g3-rf-assurance`（不合 main）
- base：`1a2f9428a599504eb8355fcaebf86c6cbcaccbb3`
- 范围：质量层改报告、manifest 默认 SHA+size、安装包按技能 runtime 职责收敛。全部 TDD，离线，模型/下载/生产写 0，用户安装目录写 0。

---

## 1. 旧门：实际 caller 与退休处理

### 1.1 strict-mypy 目标集（`uc.quality.strict_targets`）

| 项 | 内容 |
|---|---|
| base 行为 | 逐行正则在 `<repo>/.github/workflows/*.yml` 找 `python -m mypy …`；revenue 的 workflow 已改为 `run: python tools/pre_push_gate.py` → 找不到 → `ValueError` → `compute_baseline` 崩 → `quality-verify` 红 |
| 实际 caller | 仅 `uc.quality.compute_baseline`（`freeze`/`verify` 共用）。**无其他生产 caller**（已 grep 全仓）。测试 caller 只有 `test_zr104_quality.py`（本身不直接调） |
| 现行为 | 先读该仓 workflow 的内联 mypy（filing/wiki 仍内联，语义不变）；没有内联则**只读跟随** workflow 里 `python tools/<x>.py` 的委托，用 AST 从被委托文件里取 `-m mypy` 目标（revenue → `tools/pre_push_gate.py`）。不恢复 workflow 内联 mypy，不执行任何 YAML 文本，不重新冻结 |
| 退休/保留 | 保留为真当前工具；退休的只是“workflow 内联文本是唯一机器源”这个假设 |
| 兼容 | `strict_targets(repo_name, root) -> list[str]` 签名不变，找不到入口仍 `ValueError`（本仓=失败，邻仓=not_available） |

revenue 解析结果 = `scripts/contracts/{__init__,constants,document,evidence}.py` + `scripts/{schema_compatibility,filing_fetch_client,trust_anchor}.py` = **7 个文件，与冻结 baseline 逐字节一致**。

### 1.2 覆盖率 ratchet（`_verify_coverage`，84→0 / 8 模块 floor→`{}`）

| 项 | 内容 |
|---|---|
| base caller | `uc.quality.verify` → `uc.cli cmd_quality_verify`（子命令 `quality-verify`，非空即 exit 1）。**只此一条**；`tools/run_coverage_gates.py` 与 `.coveragerc` 是被读的历史报告解码器，自己“decide nothing” |
| G2 已做的退休 | `.coveragerc fail_under = 0`、`tools/run_coverage_gates.py PER_MODULE_MINIMUM = {}`（仍写成 `ast.Assign` 字面量以便 AST 读） |
| base 阻断点 | `_verify_floor_map` 的 “frozen floor … lost (constraint removed)” 对 8 个模块 floor 逐条判违规 → 退休动作被旧层当“弱化” |
| 现行为 | 同样的比较原样保留，但写进 `quality_report` 的 `diagnostics`，不再进 `failures`；消息里明确标 `retired engineering threshold, diagnostic only`。冻结值不改、不重冻、不改历史账目 |
| 仍失败的情况 | `.coveragerc` 或 `run_coverage_gates.py` **在本仓存在但读不出来/解析失败** → `_dimension` 给 `status="error"` → `failures` → `quality-verify` exit 1 |

### 1.3 复杂度 / 硬编码 / 死 caller / product_tree / 邻仓 HEAD

| 维度 | base caller | 现在 |
|---|---|---|
| `verify._verify_types/_verify_complexity/_verify_hardcoding/_verify_dead_callers` | 只有 `uc.quality.verify` | 函数本体移入 `uc/quality_report.py`，输出改为 `diagnostics`；名称/语义（只增/只减方向）保持，只是不再决定退出码 |
| `product_trees` 相等 | `verify` 判违规 → exit 1 | **历史对比报告**：`product_trees/<repo>: historical comparison — frozen … != current …`；解析不到（邻仓缺失/非 git）→ `not_available` + scope，frozen 值保留为历史记录 |
| `dead_callers.input_hash` | 变化即违规 | 诊断 |
| 旧 workflow 文本差异（FC-1101 scan pattern/targets） | 违规 | 诊断 |
| `check_critical_complexity` | 无生产 caller（AST 门，`_complexity_for` 文案引用） | 原样保留，`MAX_CRITICAL_COMPLEXITY == 10` 断言仍绿 |
| `freeze` | `quality-freeze` 子命令（CAS 写 baseline） | 原样保留；**本卡没有执行过任何 freeze，冻结 baseline 字节未动** |

### 1.4 manifest mtime（5 处 `--mtime` 默认 strict）

| 项 | 内容 |
|---|---|
| 实际 caller | `uc.cli._require_no_drift`（默认参数 `check_mtime=True`）← `state-bootstrap`(179) / `lock-acquire`(126) / `state-update`(230) / `closure-advance`(542) / `env-freeze`(764)；`cmd_manifest_verify` ← 子命令 `manifest-verify`。仓外 caller：`tools/drift_patrol.py:136`（**已显式传 `--mtime off`**）、`tests/test_ca303_arch_quality.py::test_c5`（默认值）、`tests/test_zr905_audit_self_test.py:209/217` 与 `tests/test_zr907_drift_patrol.py:79`（**都显式 `check_mtime=False`**）、`tests/test_ca301_clean_checkout.py`（**显式 `env-freeze --mtime off`**） |
| 改动 | `uc.manifest.verify` 默认 `check_mtime=False`；`uc/cli.py` **5 处 `--mtime` 默认 `off`**，`getattr(args, "mtime", "off")`，`_require_no_drift` 默认 SHA+size。`check_mtime=True` = 显式旧 strict |
| 语义统一 | 库 / CLI / current test 走同一条 `_collect` 代码路径：hash/size/missing/escape 永远在 `problems`；mtime 在 strict 时进 `problems`，否则进 `mtime_diagnostics()` 并由 `manifest-verify` 打成 `NOTE:`（不改退出码） |
| 退休方式 | 不是删检查，而是把“checkout 时间”降级为诊断；严格模式仍是显式选择 |

### 1.5 安装同步（`tools/sync_installations.py`）

| 项 | 内容 |
|---|---|
| 实际 caller | `tools/drift_patrol.py:66`（**默认 check，只读**）；`tests/test_zr804_platform_shape.py:169`（**真实 `--apply` 到 `~/.agents`、`~/.codex` —— 本卡按禁令未运行**）；`tests/test_fc1004_platform.py:89,99`（`--apply --destination <tmp>`，只写 tmp）；`tests/test_ci_smoke_plan.py`、`tests/test_rf_release_checklist.py` 断言它**不在**日常/发布门里；`scripts/revenue_forecast.py --version` 的 `_root_directories` 是**镜像常量**（边界外，见 §3） |
| 改动 | `ROOT_DIRECTORIES` 去掉 `tests`；`installation_diff` 只比 owned runtime；`sync_installation` 改为 tmp staging + 逐文件 `os.replace`，**不再整目录替换**，未知文件/用户配置/`output`/旧残留全保留；`installable_files`/`manifest`/`import_installation`/`unique_destinations`/`main` 签名与返回不变；`main` 无 `--apply` 时仍然 0 写 |
| 退休方式 | “安装一致 == 技能可用”这个隐含门被拆掉：diff 不再把整个安装树（含旧 repo-only 残留）算作 MATCH 责任，也**不把残留当使用许可** |

---

## 2. 真正的输入错误如何失败（保留的失败集，闭集）

| 类别 | 入口 | 失败表现 |
|---|---|---|
| manifest 缺文件 | `uc.manifest.verify` / `manifest-verify` | `ManifestError: manifest missing: …` → CLI `DRIFT: …` → **exit 1**（不再 traceback） |
| manifest 非 JSON / 非对象 / schema≠1 | 同上 | `ManifestError` → **exit 1**；**文件字节不变**（绝不 build/update 自动修复） |
| 路径逃逸 | `_resolve_entry_path` 拒绝绝对路径、盘符、`..`、resolve 后出根 | `path escapes repository root: …` → **exit 1**（base 时能“验证通过”，是真实缺口） |
| 冻结输入缺失 | `_collect` | `frozen input missing: …` → exit 1 |
| 指定 SHA / size 不符 | `_collect` | `hash drift` / `size drift` → exit 1（同 size 换字节由 SHA 拦） |
| quality 显式输入不可读 | `uc.cli._quality_report_from` | `QUALITY-VIOLATION: baseline not found/unreadable …` → **exit 1**，文件不被创建也不被修复 |
| quality 非法配置 | `_invalid_configuration` | `config: schema_version …`、`config: unit …`、`config: <key> must be a JSON object` → exit 1 |
| 本仓（revenue）维度读不出来 | `_dimension` → `status="error"` | `input: <repo>/<dimension> unreadable: …` → exit 1 |
| codegraph 工件读不出来 | `compute_baseline` | `dead_callers` 记 `status="error"` → `input: dead_callers artifact unreadable: …` → exit 1 |
| 实际进程非零 | `uc.quality_report.run_probe`（`quality-report --run-types`） | 只看 `returncode`：`returncode==2`、输出无 `FAILED` 字样 → `type-check: process exited 2 …` → exit 1 |

**明确不再失败的（诊断）**：覆盖率 floor 丢失/下降、复杂度 max、冻结 allowlist、死 caller 数量、product_tree 漂移、邻仓 HEAD/存在性、旧 workflow 文本差异、mtime 差异。

---

## 3. 边界外 caller —— MAIN 精确接线表

> 本卡只交表，不在写集外动任何文件。

| # | 位置 | 现状 | MAIN 要做的精确动作 | 不做的后果 |
|---|---|---|---|---|
| W1 | `scripts/revenue_forecast.py:73-95`（`--version` 分支，约 `:81` `_root_directories = {"agents","config","references","scripts","tests"}`，注释明写 “Match tools/sync_installations.py installable_files”） | 仍含 `"tests"`，与新的 `tools/sync_installations.ROOT_DIRECTORIES` 不同步 | 从该 set 字面量里删掉 `"tests"`（仅此一项；不动任何预测逻辑） | 实测：canonical `--version` → `manifest_sha256=c58de2c159dcfcf5`，按新集合同步出的安装副本 → `76b37ec851b558eb`，两者不等 → `tests/test_zr804_platform_shape.py::test_installed_copy_executes_with_canonical_identity` 的 `copy_out.stdout == canonical_out.stdout` 断言红 |
| W2 | `tests/test_zr804_platform_shape.py:169-180 _sync_installations()` | 会向 `~/.agents`、`~/.codex` 真实 `--apply` | 二选一：① W1 落地后原样保留；② 改为 `--destination <tmp>` 的隔离同步，避免测试写用户安装目录 | 该测试在任何人跑全量测试时写用户安装目录；**本卡按禁令从未运行它** |
| W3 | `assurance/unified_completion/README.md:21-22,35` | 文档写“严格：hash+size+mtime / `--mtime off` 干净 checkout 模式” | 把默认值描述改成：默认 `hash+size`（mtime 为诊断），`--mtime strict` 为显式旧严格模式 | 文档与 CLI 默认值相反 |
| W4 | `references/{extended-models,input-construction,model-library,schema-migration-3.6-to-3.7}.md` 共 4 处 `` `tests/…` `` 贡献者指引 | 安装包不再带 `tests/` | 在 SKILL.md 已写清“仓库工程测试留仓内”的前提下，按需把这 4 处改成“仓库内运行”措辞 | 用户在安装副本里按文档找不到这些文件（文档性，非运行时） |
| W5 | 卡给的责任混合命令的 conftest 同名冲突（pytest 9.1.1） | 已由 `test_manifest.py` 本地 `REPO_ROOT` 绕开本卡4文件 | 若要彻底修：把 `assurance/unified_completion/tests/conftest.py` 的内容改为不依赖模块名 `conftest`（或给两棵树加 `__init__.py`）；其余 11 个 UC 测试仍 `from conftest import REPO_ROOT`（`test_cli_evidence/test_control/test_dag/test_legacy_disposition/test_receipt_shas/test_scenarios/test_zr001/test_zr003/test_casfile/test_concurrent_10`）在混合会话里仍会 ImportError | 只影响“同一 pytest 会话混跑两棵测试树”；分树跑不受影响 |

**runtime 依赖集合（安装包应有内容，已实测）**：
`.gitignore`、`CHANGELOG.md`、`SKILL.md`、`agents/**`、`config/**`、`references/**`、`scripts/**` = 75 个文件。
静态证据：`python docs/implementation/g3-rf-assurance/runtime_closure_scan.py` → `scanned files: 72`，`tests/tools/assurance/audit_review/compatibility/e2e/examples` 命中全 0。

**三安装副本下一步（MAIN）**：
1. 先落 W1，再谈安装，否则任何一次 `--apply` 都会放大 `--version` 身份不一致。
2. `~/.agents/skills`、`~/.codex/skills` 在本卡之前就已各 24 文件 DIFF（缺 `references/*.md`、`scripts/research/*.py` 及16个 `tests/*.py`）；`~/.claude/skills` 的 `revenue-forecast` 是指向 `~/.agents` 的链接，已被 `unique_destinations` 去重。
3. W1 落地后一次性 `python tools/sync_installations.py --apply` 即可：新的定点同步会更新 owned 文件并保留未知/`output`；收敛后旧 `tests/` 残留会留在盘上（保留未知文件的既定语义），**它既不算 drift 也不再被 diff 责任覆盖**；如需清理由 MAIN 显式删除。
4. 本卡**没有**在任何用户安装目录执行过写操作。

---

## 4. RED → GREEN

| # | RED（base 实测） | GREEN（实现后） |
|---|---|---|
| 1 委托当前 mypy 入口 | `ValueError: no 'python -m mypy' command found in .github/workflows/quality.yml`（2 个测试） | 解析到 `tools/pre_push_gate.py` 的4个目标，展开=冻结的 7 文件 |
| 2 coverage 门退休 | 同上 ValueError 先炸（无法走到比较） | `verify(...) == []`，`diagnostics` 里有 `revenue/coverage: … retired engineering threshold, diagnostic only` |
| 3 邻仓不在 | `compute_baseline` → `git rev-parse` 对不存在目录抛 `ValueError` | `status="not_available"` + scope；product_tree `None` + `product_tree_scopes`；不造 0、不复制 revenue 集 |
| 4 干净 checkout 同 SHA/size 不同 mtime | 默认 `verify` 报 7 条 `mtime drift` | 默认 `[]`，`mtime_diagnostics()` 给诊断，`check_mtime=True` 仍报 |
| 5 同 size 换字节 | **base 即绿**（SHA 拦住）→ 记为守卫 | 仍绿；新增“路径逃逸”反例 base 能通过 → 现 `path escapes repository root` |
| 6 return2 无 FAILED | **导入错误 RED**（`uc.quality_report` 不存在） | `run_probe` 以 `returncode` 判定：2 → `ok=False` |
| 7 独立安装包 | `installable` 含 `tests/`；tmp 安装带 `tests/` | 75 文件 runtime 闭包；tmp 安装无 `tools/`、`tests/`、`assurance/`，`--help`/`--version`/模板生成全部 exit 0 |
| 附夹具/导入错误 A | 卡给的混合责任命令在 base 收集失败（conftest 同名覆盖） | `test_manifest.py` 本地 `REPO_ROOT`，混合命令可跑 |
| 附夹具/导入错误 B | 子进程读 GBK 字节 `UnicodeDecodeError` | `errors="replace"` |

`test_zr104_quality.py` / `test_manifest.py` 里被语义变化影响的4 个既有断言已同步改写（tamper → 报告不阻断；`payload == committed` → 改为“确定性 + 类型目标集仍复现冻结值”；`compute_baseline` 允许 not_available；mtime 默认 quiet/strict loud），改写理由都写在测试 docstring 里。

---

## 5. 命令、时长与副作用

| 命令 | exit | 秒 | passed/failed | 副作用 |
|---|---|---|---|---|
| 责任包：`python -m pytest -q <卡4文件 + 本卡4新包>` | **0** | **20** | **74 / 0** | 只写 `.planning/g3-rf-assurance/scratch`（运行前 absent，运行后已删除恢复 absent） |
| `python -m ruff check <13 改动文件>` | 0 | <2 | — | 无 |
| `python -m pytest -q assurance/unified_completion/tests/` | 1 | 238 | 228 / 13 | 13 项与 base 完全相同（stash 对照），与本卡无关 |
| `python -m pytest -q tools/tests/` | 0 | 8 | 29 / 0 | 只写 tmp |
| 受影响根测试 7 文件 | 1 | 46 | 56 / 7 | 7 项与 base 相同；base 第8项 `fc1004::test_install_sync_gate_detects_drift` 本卡**转绿** |
| `python tools/pre_push_gate.py`（卡要求最后跑一次，11 包未改） | 1 | 8 | 105 / 2 | ruff+mypy 全绿；2 项是 `test_p5_source_default_cli_e2e` 需要 `_g3/RF-ASSURANCE/filing-fetch`，**base 完全相同**（独占 worktree 无邻仓，卡禁止写其他仓） |

副作用合计：模型调用 0、下载 0、生产写 0（`assurance/runs/*`、冻结 control、manifest、baseline 均未写）、用户安装目录写 0、真实整套 sync/import-installation/备份恢复 0。

未运行（按禁令）：`tests/test_zr804_platform_shape.py`（会 `--apply` 到用户安装目录）。

---

## 6. 真正的 remaining（不由本卡解决）

1. **W1**（`scripts/revenue_forecast.py --version` 的 `_root_directories`）未落之前，`test_zr804_platform_shape` 的身份断言在“新集合同步过”的安装上会红。实测数值见 §3。
2. **W2/W3/W4/W5** 见 §3 接线表。
3. 三个安装副本仍是 24 文件 DIFF（本卡不修，且先要 W1）。
4. `pre_push_gate` 的2 项邻仓依赖失败是**本 worktree 环境**限制；在有邻仓的 main checkout 里该 107 项仍应为全绿（卡给的既定事实），MAIN 并线后按精确 CI 复核即可。
5. UC 全量里 13 项失败、根测试里 7 项失败均已在 base 逐一 stash 对照确认为**历史遗留**（`test_receipt_shas` 的三元组 git 对象、`test_zr001` 的 evidence SHA、`test_zr102` 场景 e2e、`test_zr105` 冻结 workflow hash、`test_zr907`/`test_rf_release_checklist` 的安装 DIFF、`test_ca301` 的邻仓 checkout），不在本卡写集，单列不扩大。
