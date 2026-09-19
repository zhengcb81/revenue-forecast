# review.md — I-02-C / a20260919-01 独立复核（reviewer）

日期：2026-09-19。复核身份：独立 reviewer（只读三仓 + iso venv 重跑；除本文件外未写任何文件，临时备份目录已删除）。

## 结论：accepted_scoped

## 每核对点一句

1. **重跑**：在 attempt cwd 用 `iso/venv/Scripts/python.exe -X utf8 scripts/w02c_cases.py` 重跑，rc=0，`{"failed_cases": []}`；重跑生成的 case_results / zero-provider-events / registration-stages / exact-resolve.before-after / sample-copy-manifest 五份 JSON 与原 attempt 输出逐字节相同（确定性复现）。CLI probe（`w02c_cli_probe.py`）重跑 rc=0，真实 `cli.main` 返回 status=`registered_existing`、canonical_import.status=`registered_existing_raw`、recovery_source=`existing_raw`、acquisition=null（如实无下载事件）。
2. **P1 抽验 / 字节一致**：生产原件现在重算 sha256+size 与卡固定值一致（HK `ffd73376…`=4405561；US `e3de0053…`=8585615），与 `samples/real_roots/{hk,us}` 副本 sha256 逐字节一致；sidecar sha（8228741d…/1cbfb1a2…）与 manifest 一致；P1 两样本 provider discover=0/fetch=0。
3. **N2**：`_reactivate_if_retired` spy 计数=0（runner 在 main 前后安装/卸载包装器，N2a/N2a2 案例内断言计数未变）；documents.source_status 保持 retired/quarantined 不恢复 active；不返回合格 handle；N1b 篡改后字节保持篡改态不自愈，catalog 无目标行。
4. **oracle 冻结**：oracle.md mtime 2026-09-19 14:38:44 早于 iso/override/canonical_writer.py 14:43:53 与 case runner 15:18；预期错误短语（existing_raw_missing_sidecar / existing_raw_bytes_mismatch / existing_raw_identity_contract / existing_raw_provenance_incomplete / existing_raw_status_not_active / existing_raw_root_not_reusable）在实现副本中逐字存在且一一对应；未发现实施后改 oracle 贴合结果的迹象。
5. **changes.diff 范围**：diff 仅含 4 个允许文件（canonical_writer / acquisition_service / acquisition_journal / cli）的 iso/override 副本；生产原件 4 文件 sha256 与 binding 的 prod_source_hashes_pre_edit 全部一致（即生产源码未被改写）。
6. **R1–R7 门核对（读 iso/override/canonical_writer.py 实码，非文件名推断）**：R1 root policy `_effective_reusable` 最先 fail-early；R2 raw 存在且必须 resolve 后位于绑定 company_raw root 内（containment，出树→identity_contract 拒）；R3 sidecar 必须是 `<raw>.source.json` 相邻文件（resolve 后比对）；R4 顶层身份字段+candidate/request/receipt+receipt 必填字段逐项查缺（缺→provenance_incomplete，从不从文件名补）；R5 用现行字节重算 sha256+size 对 receipt（N1b 单字节翻转即拒）；R6 request.provider/provider_document_id 显式且与 receipt/sidecar/entity/kind/year 一致；R7 已注册同 bytes 为 retired/quarantined 时直接拒（在 scan 注册阶段之前，绝不调 _reactivate_if_retired）。随后 register 阶段复用 I-02-A 的 scan 门 0–3 与 exact_resolve_identity_mismatch 门 4。顺序合理（先资格/完整性/身份，再状态，再注册）。
7. **生产未触碰**：`git -C CW status --porcelain src/company_wiki/source_catalog/` 为空；`.source_catalog/catalog.sqlite3` 最后修改 2026-09-19 07:31（早于本 attempt 14:31–15:30 的活动窗口，shm 的 10:59 touch 为连接打开的读侧副产物）；两生产 raw/sidecar 现时 sha 与 before 基线一致——本卡对生产 catalog 仅只读。
8. **样本 manifest**：sample-copy-manifest 两原始件 sha/size（ffd733…/4405561；e3de0053…/8585615）与卡目标完全一致，byte_identical=true。
9. **自评未决项**：handoff open_questions 恰四条（W03/W05 隔离 pytest nodeids 待 I-00-B 实现-后绑定；CLI 层负例未单独跑；samples 平铺放置属 MAX_PATH 环境妥协、生产子树布局在 case 树复现；RF source_preparation 端到端属 I-07/消费方范围）——四条如实，未见隐瞒。
10. **资格分界（P1/P2 输出如实分开）**：P1/P2/CLI probe 的 envelope 均报 `prompt_injection_status=not_reviewed`、`bundle_usable=false`、download_events=0；acquisition=null；journal 只增 registered_existing_raw 行。evidence 文本全量检索无"预测/审核完成"类越界表述。

## 限定申明

- 本卡只获得**注册=来源链资格**：注册成功仅证明来源链资格（source-chain qualification），不构成审核资格、不构成工件完成、更不构成预测可用/预测成功。
- 生产 catalog 未注册任何真实条目：两个真实样本的注册只发生在隔离 scratch case 树与 samples 副本上；CW 生产 `.source_catalog` 及生产 raw/sidecar 全程只读未改。
- 复用（reused / registered_existing）≠ 审核、≠ 工件完成、≠ 消费端预测资格；prompt_injection_status=not_reviewed / bundle_usable=false 为未完成的如实声明。
- 遗留：CLI 层负例与 W03/W05 隔离 pytest nodeids 绑定仍为 I-02-D/E / I-00-B 待办，不在本卡范围。

## reviewer 重跑证据摘要

- `w02c_cases.py` rc=0；5 份 after JSON 与原输出逐字节一致（含 deterministic journal attempt_id）。
- `w02c_cli_probe.py` rc=0；raw_bytes_unchanged=true，sha=ffd73376…。
- 生产 raw sha256 现算：HK ffd733761633f464d90f6829e9b2d3e089f2dee7054b8ebfe91ef617f222da7c / 4405561；US e3de0053021c02b033272b55551e383b31dba288c86cc12da2e32375e40ecfff / 8585615。
- CW `git status --porcelain src/company_wiki/source_catalog/` 无输出。
