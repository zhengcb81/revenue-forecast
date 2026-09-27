# FC-1202 独立评审重放日志 (reviewer-fc1202-independent)

> 评审时间: 2026-08-12T21:15Z。评审者身份 `reviewer-fc1202-independent`，implementer `honest-implementer`。
> 决策: **ACCEPTED**（零 blocking findings）。
> 全部重放在干净 git worktree 中进行（F-6 规则：base 复现用独立 base worktree，绝不 `git checkout <rev> -- <paths>` 于主 checkout）。

## 1. Triplets（git rev-parse 实测，非手写）

| repo | base | result (feat) | 备注 |
|---|---|---|---|
| revenue | `84d4967d31ef92ec45a570aafeed94d4a9897e87` | `b34097dd0b86fb25aacb70bd320715cf25189d02` | fcap HEAD = `20180f94967bbbd0805a8fa217b9cacb1cb29741` = feat + receipt/docs-only（已核实无代码改动） |
| filing | `592fae6108722299673981db4d329ad8906248bb` | `b7ef9cca0747b108184f00e3e519aeb046be9d2b` | |
| wiki | `b3b45aa57a88dd890f19b7930e8ae8f377156dd9` | `a6937f34081cdc928704d511e0b011f71b061a90` | |

Worktrees（评审后全部移除）: `.fcap-review/fc-1202/{result-revenue,base-revenue,result-filing,base-filing,result-wiki,base-wiki}`。

## 2. Diff 复核（逐 commit 全文审查）

**revenue `b34097d`** (8 files, +371/−9): `config/filing_fetch.json`(新, schema 1.0, `${USER_PROFILE}/Projects/filing-fetch`)、`scripts/filing_fetch_client.py`（`load_filing_fetch_root()` 严格 loader：精确字段集 `{schema_version, filing_fetch_root}`、schema_version=="1.0"、trimmed 文本、`${SKILL_ROOT}/${USER_PROFILE}` token、未知 token 拒绝、展开后绝对、目录存在、含 `scripts/fetch_filing.py`；`resolve_filing` 参数 None 时读 config；模块级 `_DEFAULT_FILING_FETCH_ROOT` **已删除**；`--filing-fetch-root` help 更新）、`scripts/source_preparation.py`（`prepare_source` + CLI 增 `--filing-fetch-root` 透传）、`tests/test_filing_fetch_client.py`、`tests/test_source_preparation.py`、`tests/test_fc1002_three_process_e2e.py`（链测试显式传 `--filing-fetch-root FILING_ROOT`）、`assurance/fc/FC-1202/00_wu_card.md`、`audit_review/.../findings.md`（发现 58）。**无额外改动。**

**revenue `20180f9`** (2 files, docs-only): `assurance/fc/FC-1202/11_implementer_receipt.json`(新) + `work_unit_registry.md` 状态行（FC-1202 pending → in_progress）。**无代码改动。**

**filing `b7ef9cc`** (6 files, +486/−24): `scripts/fetch_filing.py`（相对 `company_wiki_root` → `FilingFetchError(config_error)`，删除 `selected.parent / root` 回退）、`tools/config_doctor.py`(新 262 行：三仓契约 doctor，filing config 精确 schema + 拒 `allowed_handle_roots` + wiki `source_catalog.yaml` 结构检查（schema_version / reusable_root_kinds 非空 string 列表 / roots 列表）+ revenue config 若 `--revenue-root` 给定；**零 root 路径硬编码**)、`.github/workflows/quality.yml`（stale 块替换为 `python tools/config_doctor.py --revenue-root "$HOME/Projects/revenue-forecast"`）、`SKILL.md`（Notes 重写为 policy-snapshot 语义）、`tests/test_config_doctor.py`(新 10 测试)、`tests/test_fetch_filing.py`（绝对 root 更新 + 1 负向测试）。**无额外改动。**

**wiki `a6937f3`** (2 files, +108/−30): `scripts/config_doctor.py`（`diagnose()` 增 `filing_fetch_config` 参数；兄弟查找 `root.parent/"filing-fetch"` **已删除**，参数 None 时跳过跨仓检查；`main()` 增 `--filing-fetch-config`；重构使 dropbox_stock 缺失不再提前 return 跳过 filing 检查——**latent order bug 修复**）、`tests/test_config_doctor.py`（1 更新 + 2 新增）。**无额外改动。**

计数注记（非阻塞）: 任务描述称 "8 new config tests" 实为 9 个（多 `test_explicit_param_bypasses_config`）；"wiki 2 updated + 2 new" 实为 1 updated（`test_e2e_f03_filing_allowance_smuggled_fails` 就地更新）+ 2 new。

## 3. Focused 测试（result worktrees）

| 套件 | 结果 |
|---|---|
| revenue worktree `test_filing_fetch_client.py + test_source_preparation.py` | **28 passed** |
| revenue 主 checkout（链测试需真实 sibling filing+wiki）三件套 | **31 passed in 8.05s**（implementer 声称 30——实测 31：17 client + 11 source_prep + 3 chain；计数偏差，非阻塞） |
| filing `test_config_doctor.py` | **10 passed** |
| filing `test_fetch_filing.py -k "relative_company_wiki_root or editing_config_moves_root"` | **2 passed** |
| wiki `test_config_doctor.py + contract/test_dropbox_config_invariants.py` | **13 passed** |

链测试运行前后对三个主 checkout 做 git status 快照 + `llm_cost_log.csv` md5：全部一致，评审活动零副作用。（FC-1002 测试用 `PROJECT_ROOT.parent/"filing-fetch"` 兄弟布局——fixture 布线，非生产策略。）

## 4. RED-at-base（base worktrees，拷贝新测试文件覆盖 base 版本）

| repo | 测试 | base 失败原因（正确理由） |
|---|---|---|
| revenue | `test_filing_fetch_client.py`（整模块） | **collection ERROR: ImportError cannot import name 'load_filing_fetch_root'**（base 无 loader） |
| revenue | `test_prepare_source_forwards_filing_fetch_root` | **TypeError: prepare_source() got an unexpected keyword argument 'filing_fetch_root'** |
| revenue | `test_cli_forwards_filing_fetch_root` | **SystemExit: 2 — unrecognized arguments: --filing-fetch-root**（base CLI 无此参数） |
| filing | `test_config_doctor.py`（整模块） | **ModuleNotFoundError: No module named 'config_doctor'**（base 无 tools/config_doctor.py） |
| filing | `test_relative_company_wiki_root_is_rejected` | **AssertionError: FilingFetchError not raised**（base 相对 root 静默按 config 父目录解析） |
| wiki | `test_explicit_missing_filing_config_is_reported` | **TypeError: diagnose() got an unexpected keyword argument 'filing_fetch_config'**（base 无此参数） |
| wiki | `test_e2e_f03_filing_allowance_smuggled_fails`（更新版） | **TypeError 同上**（base 无此参数） |

**重要发现（非阻塞，分析性）**: `test_no_implicit_sibling_lookup_without_arg` 按原样在 base **通过**——因为 base 的 latent order bug（fixture 无 dropbox_stock root → `_cross_repo_checks` 提前 `return`）使兄弟查找不可达，测试被 bug 掩盖。评审者用 dropbox 存在变体证明该测试的区分力：**同一 fixture 加 dropbox_stock root 后，base FAILS**（兄弟查找发现走私的 allowed_handle_roots）、**result PASSES**（无查找，显式参数 only）。该测试的守卫价值真实（M5 直接击杀复活的兄弟查找），但不能单独作为 RED-at-base 证据。

## 5. Mutation 重放（result worktrees，反向编辑，全部击杀并还原，worktree 复绿）

| Mutation | 变更 | 击杀证据 |
|---|---|---|
| M1 | revenue 改名 `load_filing_fetch_root` → `_MUTATED` | 整模块 collection ERROR: ImportError（'Did you mean: load_filing_fetch_root_MUTATED'） |
| M2b | revenue 删除 `main()` 中 `filing_fetch_root=args.filing_fetch_root` 透传 | `test_cli_forwards_filing_fetch_root` FAILS（captured kwargs 无 filing_fetch_root） |
| M3 | filing 恢复 `root = selected.parent / root` 回退 | `test_relative_company_wiki_root_is_rejected` FAILS（FilingFetchError not raised） |
| M4 | filing 删除 `reusable_root_kinds` 结构检查块 | `test_wiki_yaml_missing_reusable_kinds_fails` FAILS（assert False） |
| M5 | wiki 恢复 None → `root.parent/"filing-fetch"` 兄弟查找 | `test_no_implicit_sibling_lookup_without_arg` FAILS（走私兄弟 config 被检出） |

还原后三个 result worktree `git status` 全净，focused 套件复绿（28 / 10+2 / 10）。

## 6. 全量套件（精确数字）

| 套件 | 结果 | 预存在失败核实 |
|---|---|---|
| revenue `pytest tests/ tools/tests/ -q`（主 checkout，sibling 布局所需） | **513 passed / 1 failed / 106 subtests (287.21s)** | 1 failed = `tools/tests/test_audit_baseline.py::test_collects_baseline_facts`：UnicodeDecodeError 'utf-8' … 0xd4（GBK subprocess，finding 31 / PORT-01，FC-1205 范围）。**base worktree 复现同失败** ✓ 预存在。 |
| filing hermetic `pytest tests -q --tb=short --ignore=test_real_tool_conformance.py --ignore=test_e2e_download.py` | **289 passed / 6 skipped / 54 subtests (74.92s)** | 零失败 |
| wiki `pytest tests/ -q`（result worktree，PYTHONPATH 指向 worktree src 防 .pth 串到主 checkout） | **2241 passed / 2 failed / 1 skipped (468.03s)** | 2 failed = `test_check_unique_test_symbols.py` PORT-01 对（TypeError NoneType + UnicodeDecodeError 0xd4/0xa1）。**base worktree 复现同 2 失败** ✓ 预存在。 |

主 checkout 副作用核查：全量套件前后 status 快照 + `llm_cost_log.csv` md5 一致。评审期间 revenue 主 checkout 新出现 `M findings.md`（发现 59）与 `?? assurance/fc/FC-1203/`——时间戳 22:05、内容为 FC-1203 preflight，系 implementer 并发会话产物，**非本评审运行所致**（本评审最后一次快照 diff 为空）。

## 7. Config doctor 现场冒烟

- filing result worktree: `python tools/config_doctor.py --revenue-root C:/Users/郑曾波/Projects/revenue-forecast` → **exit 0**，"OK: three-repo configs healthy"。
- 负向：temp JSON 含 `allowed_handle_roots` → **exit 1**，`CONFIG-PROBLEM: filing-fetch config must NOT carry allowed_handle_roots`（+ 精确字段集问题）。
- wiki 主 checkout（只读）: 无参 → **exit 0** OK healthy（跨仓检查跳过、无兄弟查找）；`--filing-fetch-config <真实 filing config>` → **exit 0** OK（跨仓检查跑通）；`--filing-fetch-config <不存在路径>` → **exit 1** CONFIG-PROBLEM "does not exist"（fail-closed，非静默跳过）。
- 注：result-wiki worktree 中 wiki doctor 报 `catalog_dir is not a directory`——`.source_catalog` 是未跟踪运行时目录，fresh worktree 缺失所致，环境假象非代码问题（主 checkout 中同一命令 OK）。

## 8. 非阻塞 findings

- **FC-1202-F1 (info)**: 测试计数偏差——任务描述 "8 new config tests" 实为 9；implementer receipt "30 passed" 实为 31（17+11+3）。均偏保守方向（多测无害）。
- **FC-1202-F2 (info)**: 任务描述 wiki "2 updated + 2 new tests" 实为 1 updated + 2 new。
- **FC-1202-F3 (info)**: `test_no_implicit_sibling_lookup_without_arg` 在 base 按原样通过（被 latent order bug 掩盖，见 §4）——守卫有区分力但需 dropbox 存在前提；RED-at-base 证据由 explicit-missing 测试 + dropbox 变体实验承担，M5 提供 result 侧直接击杀。
- **FC-1202-F4 (info)**: wiki doctor 在无 `.source_catalog` 运行时目录的 fresh worktree 会报 catalog_dir 问题——诚实报告而非静默，环境假象。
- **FC-1202-F5 (info)**: filing `tools/config_doctor.py` 用 `Path.home()`/`USERPROFILE` 回退与 revenue wiki doctor 同构——CI Ubuntu 无 USERPROFILE 时的行为一致性依赖 ci_checkout_siblings 布局（findings 58 已记录），无新风险。

## 9. 结论

**ACCEPTED。** Diff 外科手术式且与描述精确一致（revenue 8+2 文件、filing 6 文件、wiki 2 文件，全部在 allowed_files 内，零越界改动）。Focused 全绿；RED-at-base 7/7 正确理由（no-implicit-lookup 的 order-bug 掩盖已实证分析）；M1/M2b/M3/M4/M5 全击杀并干净还原；三个全量套件精确命中预期数字，唯一失败均为复现于 base 的预存在 PORT-01；doctor 正/负冒烟 exit 0/1 正确。评审全程未改动任何主 checkout 工作文件。
