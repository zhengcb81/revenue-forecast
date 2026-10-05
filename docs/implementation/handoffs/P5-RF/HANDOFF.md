# P5-RF handoff — 默认来源迁移至 SourceRef v2

- **Lane**: P5-RF（cwp-harness 分包 `p5_rf_source_default_migration`）
- **Repo**: `C:/Users/郑曾波/Projects/revenue-forecast`
- **Worktree**: `C:/Users/郑曾波/Projects/cwp-lanes-20261005/rf-source-v2`
- **Branch**: `codex/p5-rf-source-default`（从 published `origin/main`）
- **Base commit**: `8a153f3387ae75fb172e70f8ab63ffd38100779a`（= 卡片要求的基准）
- **Delivery commit**: `31fe65e6bf673a29f1ab3ac6f7b64248246ca6a2`
- **状态**: 实现完成、本地已提交（未 push）；handoff 文档为第二个提交

## 1. 语义变更（生产默认）

`scripts/source_preparation.py`（FC-904/1202 提取后的唯一生产入口）：

- `prepare_source` **只走 SourceRef v2**：filing-fetch 子进程一律带
  `--source-ref-v2`（pathless SourceRef），随后 `open_source_version_v2`
  以 `--company-wiki-catalog-config`（**必需**）经 company-wiki reader CLI
  做逐字节校验的 raw open。
- 缺配置 / 配置不可读 → `_catalog_config_for_reader` 在**任何外发
  （subprocess/网络/下载）之前**具名抛出 `RuntimeError`（CLI → exit 3
  structured error，`error_code=upstream`，消息含
  `company_wiki_catalog_config`）。
- legacy 正文读取（`select_artifact_roles` / `verify_artifact_reads` /
  `build_revenue_source_record` 的 normalized/summary/sections 消费）
  仅存于隔离 helper `_prepare_legacy_source`（docstring 标注
  non-production），**默认路径不可达**；测试直接调用该 helper 保留历史
  离线契约（fc904/fc905b/source_preparation env 契约等）。
- `--source-reader-v2` 变为**兼容 no-op**（无新双开关、无 fallback）。
- receipt v2 语义：`artifact_read == []`（绝不声明读过 derived body）、
  `parser_calls/llm_calls` honest-None、`producer_events == []`、
  `artifact_read_events == []`、capture/pathless（record 内无
  `canonical_path`/绝对路径）。v2 已允许的 `not_reviewed` 诊断语义保持。

SKILL.md 入口段与命令示例同步（含必需的 catalog config 参数与 no-op 说明）。

## 2. 改动文件

生产/文档：
- `scripts/source_preparation.py`（默认翻转 + 具名前置失败 + legacy 隔离）
- `SKILL.md`（入口描述与两条命令示例）

新增测试（验收）：
- `tests/test_p5_source_default_v2.py`（单元/TDD，9 用例）
- `tests/test_p5_source_default_cli_e2e.py`（公共 CLI 真三仓 E2E，2 用例）

fixture 升级（RF 自有测试 fixture，非生产）：
- `tests/e2e_support/isolated_lake.py`：CWP 合法 RuntimePolicySnapshot
  （scan 后盖戳、`policy_hash = export_policy_2x(yaml-loaded config)`、
  legacy bridge 合法开）、sidecar 补 `source_title/published_date/
  retrieved_at`、URL host 改 `offline-cdn.fixtures.invalid`（过
  `valid_source_url` 的 `.example` 屏蔽）。

级联迁移（默认翻转后按 v2 语义更新或加 catalog-config/兄仓回退）：
- `tests/test_source_preparation.py`、`tests/test_fc904_artifact_selection.py`、
  `tests/test_fc905b_trusted_receipt.py`、`tests/test_zr701_f1_draft_formal.py`
- `tests/test_fc1002_three_process_e2e.py`（含"删 derived 后二次旅程仍成功"）
- `tests/test_fc1003_uj.py`、`tests/test_fc1004_platform.py`、
  `tests/test_zr802_combined_journeys.py`、`tests/test_zr803_chaos_recovery.py`、
  `tests/test_zr804_platform_shape.py`、`tests/test_zr805_t3_authorization.py`、
  `tests/test_zr709_zijin_journey.py`（fixture relative_path/时区字段修复）、
  `tests/test_preparation_e2e_success.py`（迁 IsolatedLake 配方）、
  `tests/test_message_contract_pins.py`（CW_DIR lanes 回退）
- `.planning/p5-rf-source-default/{task_plan,findings,progress}.md`

## 3. 测试与门（本机，2026-10-05）

| 命令 | 结果 |
|---|---|
| `python -m pytest -q tests/test_p5_source_default_v2.py` | 9 passed（RED 前态：8 failed/1 passed） |
| `FF_V2_CODE_ROOT=…/filing-fetch CWP_V2_CODE_ROOT=…/company-wiki python -m pytest -q tests/test_p5_source_default_cli_e2e.py` | 2 passed（27s，真实三仓） |
| 17 套件相关回归（p5×2、source_preparation、fc904/905b/1002/1003/1004、zr701/802/803/804/805、preparation_e2e、ratchet、单owner、skill-doc） | **98 passed** |
| 契约套件（message_pins、three_repo、cross_repo、zr1102、zr1104） | 25 passed, 3 skipped, 1 failed（见 §5-b） |
| `python -m ruff check scripts/ tests/` | All checks passed |
| pre-commit hooks（ruff + host-assumption guard 等） | 全过（随 31fe65e6） |

RED→GREEN：`test_p5_source_default_v2.py` 在翻转前实跑 8 failed / 1 passed
（缺配置不具名失败、默认不走 v2、legacy 正文可被默认触达、CLI 未传
配置、坏候选错误语义等）；实现后 9/9 绿。

## 4. 独立验收（卡 §6）

`test_p5_source_default_cli_e2e.py` 以**公共 CLI、不传
`--source-reader-v2`** 驱动真实三仓（FF/CWP 当前已提交代码）：
1. 全程 raw 校验路径、`artifact_read==[]`、零下载、无路径泄露；
2. **删除全部 derived 文件 + derived 树 + artifacts 表行后**，二次旅程
   仍成功且零下载（消费侧独立于旧 derived）；
3. **篡改已存 raw 字节** → fail-closed 拒绝（`source reader refused`），
   还原原文后自愈为同一 `snapshot_sha256` 且零下载。

## 5. 已知限制 / 未修债务（hold）

- **(a) CI pinned FF 无 `--source-ref-v2`**：compatibility `current_triplet`
  filing=`89c8bdb2` 不支持该 flag（实测 usage error），故 CI real-roots
  的真实链路 job 无法跑 v2 默认路由；本 E2E 以
  `FF_V2_CODE_ROOT/CWP_V2_CODE_ROOT` env 门控（CI 缺省 skip，skip 文案
  指向本文）。**需 MAIN 重绑 compatibility（或确认 FF pin 升级）**。
- **(b) CWP HEAD API 漂移**：本地 company-wiki `1cfec10`(2026-10-04)
  删除 `prompt_injection_guard.evaluate_review` →
  `test_message_contract_pins::test_lowercase_sha256_family_pinned`
  本地失败；pinned wiki `a640400` 含该 API（`git show` 实证）→ CI 绿。
  与本 lane 无关。
- **(c) lanes 布局本地失败（预存，非本 lane 引入）**：worktree 父目录
  无兄仓 junction 时，以下家族失败（CI junction 下绿）：sibling 路径族
  （fc1302 `_manifest` triplet、contract_registry/scenario_coverage 的
  ADR·marker 兄仓文档、dropbox fc505 `filing_contracts`、
  compatibility_manifest、ca20x/fc1102 的 filing-fetch 路径、T3 suite
  缺失、triplet 对象检查）。关键文件已做 baseline 双侧对照（同错）。
- **(d) 本地环境缺口**：`test_narrative_source_preparation_e2e`(11)
  需 `CWP_NARRATIVE_CODE_ROOT`（缺省具名失败，属其自身边界设计）。
- **(e) live-data 机器测试既有失败**：`test_zr806_real_t2_samples`/
  `test_zr1004_small_cohort`（读 owner 生产 wiki + 真 Dropbox）在
  baseline 与本 lane **完全同错**（4 failed/13 passed 双侧一致）——
  生产数据/上游现状问题，非本 lane。
- **(f) `e2e/run_cross_repo_chain_e2e.py` 标 historical fixture**：
  S1–S6 legacy 链场景与其 `CODE_PINS`（钉旧版 source_preparation sha）
  成对标旧；本机与 CI 均因依赖门 skip。v2 默认路由的集中验收已由
  §4 新 CLI E2E 承接。若 owner 机带生产输入重跑该 runner，需 MAIN
  按 v2 语义重写场景（或维持 legacy 配对显式按历史 fixture 运行）。
- **(g) 生产清理边界**：消费侧（RF 默认路由）迁移完成 ≠ 生产删除；
  CWP 生产 derived（2.826 GB）与调用方清理仍归 MAIN S5（本 lane 未
  触碰任何生产数据/owner 原始树）。
- 单行消息字面（`parser/llm counts absent … fail closed` 等 message pins）
  保持原样（pins 测试绿）；未触碰 validation 规则/合同注册表 →
  validation-runtime 自检不适用。

## 6. 提交与未提交状态

- 提交 1（代码+测试+PWF）：`31fe65e6bf673a29f1ab3ac6f7b64248246ca6a2`
- 提交 2（本文档 + handoff.json）：见 `git log` 顶部
- 提交后工作树仅剩 owner 的预存未跟踪文件（`assurance/…/weekly_*.jsonl`
  等，属于 owner，未动）；本 lane 无遗留未提交改动。
- 未 push（按卡默认本地提交，push 由 MAIN 决定）。

## 7. 验证命令（复现）

```bash
cd C:/Users/郑曾波/Projects/cwp-lanes-20261005/rf-source-v2
python -m ruff check scripts/ tests/
python -m pytest -q tests/test_p5_source_default_v2.py
FF_V2_CODE_ROOT=C:/Users/郑曾波/Projects/filing-fetch \
CWP_V2_CODE_ROOT=C:/Users/郑曾波/Projects/company-wiki \
python -m pytest -q tests/test_p5_source_default_cli_e2e.py
```
