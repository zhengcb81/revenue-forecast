# 独立数据链路审计

执行日期：2026-09-18—19；预测信息截止保持 2026-09-18。审计者与三家预测生产者分离。本文所有“通过”限于本次列出的实测对象；没有将历史单测、生产者口述或文件存在当作全流程通过。

## 已验证结果

| 项目 | 证据与独立检查 | 结论 |
|---|---|---|
| 跨目录原件索引和字节一致性 | 只读 SQLite mode=ro、PRAGMA query_only=ON 保存148条标题/实体关联记录；对紫金2024/2025和微软FY2024/FY2025的20个 active location与8个artifact独立重算hash/size，全部匹配 | 这4份年报的原件/sidecar/派生文件完整性通过；不等于派生物可复用 |
| 同字节跨根去重 | 紫金 company_raw 与 Dropbox PDF hash一致；微软 company_raw 与dayu主HTML hash一致。documents.csv、locations.csv、artifacts.csv与SQLite相应条目及canonical位置吻合 | 抽样去重和位置索引通过；未验证Dropbox-only/dayu-only返回handle |
| 紫金已有文档 reuse | `runs/03_zijin_fetch_reuse` 原始响应：verified active 601899/CN；FY2025；sha `01819e1c…`与独立raw核验一致；calls=2/downloads=0，parser/llm=0，outcome=reused_existing | filing-fetch原件复用分支通过 |
| source preparation安全阻断 | `runs/02_zijin_source_reuse`：exit3，stdout空，stderr明确prompt_injection_status=not_reviewed；对应fetch响应也为not_reviewed | fail-closed机制通过；端到端流程受阻，不能交付正式来源record |
| 小米无授权缺失 | `runs/04_xiaomi_source_reuse`错误内部保留not_found、不授权不下载；最外层报upstream/exit3 | 拒绝行为正确；错误分类合同不符，见IND-D02 |

证据文件：`catalog_baseline.json`（包含所选公司文档、location、manifest、assertion和artifact元数据）；`raw_artifact_verification.json`（磁盘hash/size实核）；原始运行证据在同级`../runs/`。抽样路径在上述JSON保留完整绝对路径，不复制或改写来源文件。

## 发现

### IND-D01｜P1｜capture_ready之后，正式消费者缺少可操作的来源review步骤

**预期**：按SKILL唯一入口source_preparation复用已存在年报时，可以获得合规source record，或返回明确、可执行的补充review/修复步骤；raw capture、content safety review、parsed artifact readiness的层次应能让消费者分辨。

**实际**：真实紫金年报被filing-fetch标记`capture_ready=true`、qualification=`verified_input`、gaps=[]，同时`prompt_injection_status=not_reviewed`、bundle_usable=false。消费者安全阻断正确，但运行过程止于泛化upstream错误。`prompt_injection.py`有记录receipt函数，`prompt_injection_guard.py`有scan_text与shadow-only evaluate_review；本次逐字查阅主CLI、source-catalog.md、OPERATIONS.md及revenue session-checklist未找到这一步的生产命令或指南。不能通过手填not_detected、绕开唯一入口或直接数据库UPDATE把测试变成通过。

**复现**：先用`requests/zijin_2025.json`执行source_preparation，再执行fetch_filing复用；对照`runs/02_*`、`runs/03_*`。源代码定位：revenue-forecast/scripts/source_preparation.py:145–150；company-wiki/src/company_wiki/source_catalog/prompt_injection.py记录函数；prompt_injection_guard.py模块说明。

**影响**：下载/复用成功不能进入预测研究的正式来源路径，执行者可能误以为capture_ready意味着所有下游前置条件满足。此项是可用性与流程完整性问题，不是建议移除安全拒绝。

**建议**：明确不同ready状态；提供受支持的review命令与来源hash/规则版本绑定、可审计回执、最小修复提示；SKILL给出阻断后下一步。本轮只记录，不改代码/生产数据。

### IND-D02｜P2｜缺文件的正常业务结果被外层入口归类为internal/upstream错误

**预期**：source_preparation文件头约定“1=not found/not admissible，3=internal”；调用方应能区分缺文档、身份异常、超时与内部崩溃。

**实际**：小米无授权reuse的`not_found`经filing-fetch/client仍为exit2，而source_preparation统一抛RuntimeError并报`error_code=upstream`/exit3。真实内容可从嵌套字符串读到，结构化分类已经丢失。

**复现与证据**：`runs/04_xiaomi_source_reuse/run.json`及stderr；source_preparation.py:10、110、213–216。

**影响**：编排器无法可靠地将“授权下载可解决的缺失”与重试性技术故障分开，可能重复重试或错误中止。

**建议**：保留上游error_code/retryable/候选信息，入口统一稳定退出码；增加真实缺文档分支验收。

### IND-D03｜P2｜已保存派生物普遍不满足当前复用绑定，需将索引完成与可复用覆盖分开

**预期**：已完成且来源hash、producer和schema有效的artifact才可复用；无法复用时有明确最小重算路径。

**实际**：4份抽样年报8个artifact均存在且字节匹配；紫金两份normalized=`partial`，其schema/source_sha256为空；两份summary也无schema/source_sha256。微软FY2024两者binding为空；FY2025 normalized绑定有效但summary source_sha256为空字符串。紫金fetch bundle明确拒绝normalized（artifact_status_not_completed）和summary（artifact_schema_unsupported），valid_handles={}。这证明拒绝生效，亦证明“已解析/已保存”统计不能当作当前复用有效覆盖。

**证据**：`raw_artifact_verification.json`全部8条artifact；`runs/03_zijin_fetch_reuse/stdout.txt`bundle.invalid。index/artifacts.csv仍可正确显示旧artifact完成/partial状态，但没有readiness字段。

**影响**：来源数量和派生文件数看似充足，正式消费者仍必须重新处理或阻断，研究工时与复用收益被高估。

**建议**：status/index同时显示raw-ready、normalized-ready、summary-ready及invalid reason；受控地对旧工件补处理或最小重算。不得仅改schema字段让旧工件伪装有效。

### IND-D04｜P2｜目录基线扫描时间与信息日相隔29天，not_found不能证明磁盘不存在

**实际**：4个root的last_scanned_at全部为2026-08-20T21:26:55Z。审查时截止日为9/18。`runs/01_catalog_status`自身timed_out=true但exit0，完成状态有竞态，不据此证明后台健康。

**证据**：catalog_baseline.json.roots；runs/01_catalog_status/run.json。

**影响**：9月研究可能遗漏8月后的年报、中报和公告；无法从旧catalog准确区分真实缺文档与新文件尚未入索引。此项只判断本次基线新鲜度，不断言后台停机原因。

**建议**：resolve回传last scan时间/新鲜度状态，缺文档审计加入范围明确的磁盘与索引对照，避免无依据重下载。

### IND-D05｜P2｜filing-fetch文档对跨目录handle边界自相矛盾

**实际**：filing-fetch/SKILL.md:38、50宣称所有handle必须位于companies子树，:140之后及生产source_catalog.yaml又声明可从dayu/Dropbox注册根只读复用。4份抽样实际主canonical皆在company_raw，因此本次不能用这些样本声称外部根handle验证已成功。

**建议**：区分新文件canonical写入约束与注册根复用约束，并补实际仅外部根样本。当前记文档风险，不把未经测试的外部根行为判为缺陷。

### IND-D06｜P1｜生产扫描策略与root配置不兼容，港美新文件落盘后无法注册和复用

**预期**：授权ensure下载完成后，canonical raw与不可变sidecar保存，扫描注册同一来源，精确resolve返回handle；第二次读取无需下载。

**实际与复现**：`runs/07_xiaomi_source_download_authorized`和`runs/08_msft_source_download_authorized`真实走dayu完成新raw/sidecar保存，却报`canonical file was written but exact provider identity did not resolve`。`runs/09_*`及`runs/10_*`再次reuse均not_found。独立重算小米sha=`ffd73376…`、微软sha=`e3de0053…`与sidecar一致，两者在sources/documents/locations/source_metadata_assertions四表均为0。

**已确认根因**：独立只读scan_runs，两次扫描实际都为completed_with_errors、files_seen=0，原因是`v2 scanner unavailable (fail closed): root 'company_raw' has no adapter_id (2.x policy required)`。当前runtime_policy启用v2_scan_shadow，但生产company_raw未声明adapter_id。canonical_writer.py:183之后调用scan_catalog却没有处理其错误报告，继续exact resolve，最终错误将真正的扫描配置问题表述成provider identity无法解析。

**证据**：`acquisition_aftercheck.json`记录两次真实scan报告、四表查询、文件hash、sidecar、runtime policy、worker control；canonical_writer.py:183–212；scanner.py:855–890。不是“shadow只写assertion”的推测，当前实际失败发生在root adapter预条件。

**影响**：合法下载后来源链断裂，落盘文件不能被技能复用，重试可能再次下载，且错误指引不准确。原件与sidecar仍保留，不因审计失败删除或改写。

**建议**：先在写raw前验证生产扫描策略与全部必需root兼容；让导入消费scan结果，并回传确切错误、canonical path/hash和可恢复状态；修复后从已落盘raw重建索引，避免重新下载。配置迁移、处理遗留文件和回归测试另立修复任务，本轮未实施。

### IND-D07｜P2｜A股上游访问拒绝的可重试属性在跨层包装中丢失

`runs/12_zijin_h1_download_authorized`实际CN路径discover收到HTTP403/upstream_unavailable。访问失败属于供应商或运行环境阻断，不能仅据403判定模型代码缺陷；但原始retryable=true经过company-wiki包装成fatal/retryable=false、source_preparation仅保留截断嵌套字符串，损失可操作诊断。建议保留结构化cause chain，分别报告供应商阻断与程序失败。

## 边界与结论

港股、美股市场路由及新raw/sidecar字节完整性已实测通过，新文件注册/再次复用实测失败；A股既有复用通过，缺失下载受HTTP403阻断。用户原有worker暂停状态独立核验仍为paused，未被自动恢复。

148条公司限定基线没有可安全用于external-only复用的年/中报样本：微软dayu-only旧年报均retired；紫金真实年报已有company_raw，Dropbox-only同名项实际为sidecar且缺日期；小米无已分类年/中报。因此Dropbox-only/dayu-only返回handle的真实运行边界保持未证实，未全库扩大扫描。

三家公司正式预测均未产出，经济审查及整体判定见`review.md`。
