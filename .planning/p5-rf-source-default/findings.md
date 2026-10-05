# findings — P5-RF 默认来源迁移

## 活动调用链清单（施工输入，2026-10-05 实读 main 8a153f33）

### 生产默认入口（须迁移）
- `scripts/source_preparation.py::prepare_source`（默认 `source_reader_v2=False`）→
  legacy 分支 `_prepare_legacy_source`（scripts/source_preparation.py:218-269）调用
  `company_wiki_source.select_artifact_roles` / `verify_artifact_reads` / `build_revenue_source_record`，
  会读 normalized/summary/sections 正文 —— 是 CWP 旧 derived 的真实 RF 消费者。
- CLI：`source_preparation.py` `--source-reader-v2` opt-in（line 310）；缺
  `--company-wiki-catalog-config` 时 v2 已具名失败（`_catalog_config_for_reader`，
  line 81-94，"SourceRef v2 requires company_wiki_catalog_config"，且在外发前抛出）。
- v2 candidate 校验/事件校验已存在：`_validate_v2_candidate` / `_v2_resolution_events`。
- 上层（forecast/revenue_forecast.py）不调用 prepare_source，只消费 record。

### 活动测试调用点（默认翻转后 必须迁移/仍绿的判定）
| 文件 | 调用形式 | 默认翻转后首个破裂断言 | 迁移方向 |
|---|---|---|---|
| tests/test_fc1002_three_process_e2e.py:71,142 | 真实FF兄仓+IsolatedLake，无 v2 flag | :78 rc==0（缺 catalog config→exit3）；receipt 断言 bundle_status/artifact_read=normalized | 加 --company-wiki-catalog-config；改 v2 receipt 语义 |
| tests/test_fc1003_uj.py:47 | UJ-01 成功/UJ-04,UJ-07 失败 | UJ-01 rc==0；UJ-04/07 消息是 not_found/gap（现成 config 未传） | 传 catalog config |
| tests/test_fc1004_platform.py:124 | 真实链 UTF-8 成功 | :131 rc==0 | 传 catalog config |
| tests/test_preparation_e2e_success.py:172 | 手工 sqlite fixture + source_catalog.yaml 已写好（:141-151） | :178 rc==0 | 传 catalog config；receipt 断言改 v2 |
| tests/test_zr709_zijin_journey.py:689 | J1 成功 + 缺失回退，机器专用 | :708 rc==0；receipt 语义истор | 传 catalog config；改断言 |
| tests/test_zr802_combined_journeys.py:92 | C1 成功/C1 缺失/冲突失败/C3 | :216/:287/:320 rc==0；失败消息 not_found/ambiguous rust | 传 catalog config |
| tests/test_zr803_chaos_recovery.py:84 | 锁场景成功 | :122 rc==0 | 传 catalog config |
| tests/test_zr804_platform_shape.py:92 | 大小写/缺兄仓 fail-closed | :125 rc==0 | 传 catalog config |
| tests/test_zr805_t3_authorization.py:119 | not_found 消息 pin | :139 "not_found" in error | 传 catalog config |
| e2e/run_cross_repo_chain_e2e.py | S2/S3 旧 review 拒绝 oracle | CODE_PINS SHA + "prompt injection not reviewed" pin | argv 加 catalog config；S2/S3 断言改 v2 语义 |
| tests/test_message_contract_pins.py:146-154 | pin literal "parser/llm counts absent from the resolution envelope — fail closed instead of fabricating 0" | 只要该 literal 仍在 _prepare_legacy_source 即绿 | 保留 helper |
| tools/tests/test_complexity_ratchet.py:41 | "source_preparation.py": 17 | 新分支别超 17 | 重构保持 |
| tests/test_skill_doc_executable.py | SKILL.md 含 entry+--allow-download | 无 flag pin | SKILL.md 更新示例 |

### 不可动/历史
- `.planning/2026-09-19-three-project-history-audit/*`、`assurance/`、`audit_review/`：历史账本，
  非施工输入；3,833 条 ACL 假删除不作为输入。
- 源仓 fcap checkout：assurance/runs/weekly_alert.jsonl、weekly_manifest.json 为 owner 改动，不动。

## 设计决策
- `prepare_source` v2-only：catalog config 缺失/不可用→RuntimeError（具名、外发前）；FF 命令
  一律 `--source-ref-v2`；legacy handle（resolution_envelope）不再被生产默认接受。
- `_prepare_legacy_source` 保留为隔离历史离线 fixture 入口：仅测试直接调用；文件中显式注明
  "non-production"。`--source-reader-v2` CLI flag 变录入 no-op（无新双开关、无 fallback）。
- 流程复杂度：prepare_source 改为无 v2 条件分支，应低于冻结 17。

## 边界备注
- CWP 生产 derived（2.826 GB）不在本卡删除；消费侧迁移完成 ≠ 生产清理（MAIN S5）。
