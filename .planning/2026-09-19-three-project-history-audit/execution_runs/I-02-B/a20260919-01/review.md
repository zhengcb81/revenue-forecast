# 独立复核 — I-02-B / a20260919-01（reviewer：独立复核人，2026-09-19）

## 结论：**accepted_scoped**（限定范围内接受；见末尾限定申明）

## 复核记录

1. **重跑（必核点1）**：以 attempt cwd 用 `iso/venv` python `-X utf8 -B scripts/w02b_cases.py` 复跑，rc=0，静默（无未捕获输出）；9/9 case 重跑通过且 after/* 于 14:21 全量重新生成后与我逐文件读取的原样一致（sample：p1_cw L1/L2/L3 逐层 envelope 中 code=upstream_unavailable、retryable 为 Python bool True、request_id 同层贯通一致（CW 深层为 urn，符合 oracle 顶部 amendment）、cause_chain 保留 dict 结构不被拼接；n2_unknown/n2_string/n2_malformed 的 fail-closed 断言均直接从 `after/raw-cli-logs/` 原文读证）。
2. **P1 抽验**：L3 stdout → L2 stderr → L1 stderr 三层 code/retryable/request_id/cause_chain 逐层无漂移，旧四键（status/error_type/error/retryable）保留；CN403 原始结构以 hermetic shim 只读重放，未发真实请求。
3. **N3 抽验**：journal 1 条 outcome=failed、reason=canonical_import_failed、content_sha256 与种子文件 bytes hash 一致；`side_effects_json` 中 download_events=1、raw_bytes_saved=1280（非 0、不缺省），envelope 逐层透传到 L1；retained staging 1 文件 1280 bytes 保留现场。
4. **N4 判据**：n4a（catalog_busy）信封 retryable=True 且**无任何重试循环**（override 源码 grep 无 retry/while-attempt 实现）；n4b（identity_contract）retryable=False 写 journal；两 attempt_id 不同、request_id 同。本卡未触碰预算/deadline 算法——catalog/db 类信封 retryable 仅"提示可重试性"，触发权留 I-04（未越权抢写 FF/I-04 领域）。
5. **N1/N2 抽验**：n1_long >800 字符中文消息与嵌套 dict cause_chain 在 L1 envelope 逐字段保留、无 800 截断边界、local_diag_ref 指向 raw-cli-logs 完整 UTe-8 归档且内容=上游原始输出；n2a 未知 code fail-closed 归 fatal 且原始 weird_provider_code 保留进 cause_chain(envelope_normalization)；n2b retryable='true' 字符串 fail-closed 归 False 并记 envelope_validation["raw":"true"]；n2c 畸形 JSON 不猜 envelope，全文归档 local_diag_ref。
6. **oracle 独立性（必核点2）**：oracle.md 对每 case 冻结了具体字段/码/布尔/退出码/保留要求（含每层 exit、逐层 request_id 对齐、种子哈希比对），开头的 SourceRequest.request_id=urn 派生属性 amendment 亦在实施前落纸；未见"expected 由被测函数生成的贴合痕迹"——expected 是手工逐字段推导，且 normalize 分支细节（envelope_normalization/envelope_validation stage 名）在 decision.md 先冻结。
7. **改动范围（必核点3）**：changes.diff（hash ca2abca… 匹配 binding）恰好覆盖允许的 6 文件（CW error_taxonomy / acquisition_service / acquisition_journal / cli + RF source_preparation / filing_fetch_client），无 allowlist 外 diff。iso 副本核对：`structured_error` 将 cause_chain 以 dict list 原样嵌入、旧键只加不改（cli.py:1552-1590 处组装信封不 join dict）；字符串 cause 形态保留（向后兼容）；unknown code fail-closed 恒 flush fatal/false（error_taxonomy.py:229-267，`retryable = False # n2a: unknown code NEVER opens the retry door`）；source_preparation 800 字符截断删除，非零子进程优先解析合法 JSON envelope 结构化转发，非法则全文归档 + 160 字符短摘要（n1/n2c 实测）。
8. **生产未触碰（必核点4）**：`git -C company-wiki status --porcelain src/company_wiki/source_catalog/` 空（CW 生产整洁）；RF `git status --porcelain scripts/source_preparation.py scripts/filing_fetch_client.py` 空（RF 两生产文件无本卡改动）。所有改动仅在 iso/override 副本上。
9. **自评如实（必核点5）**：4 条未决项（I-04 owner ratify 信封与结构化转发、request_id urn 深层回传姿势、I-00-B 补 pytest nodeid、D-W02 余项归 I-02-C/D）在 decision.md 与 handoff.json open_questions 如实一致；assertion exit_probe 为 sanity 级额外负例（真实修改后 cli.main() 进程内运行、嵌套 dict 逐字保留不拼接），无发明产品 CLI、不越权。
10. **信封契约与 D-W02 连贯（必核点6）**：I-02-A decision 明确"错误信封/字段映射/唯一要求 = D-W02 其余项，本卡不冻"，I-02-B 以补充决定冻结 cross-cli-error-envelope/1.0，与 I-02-A 的 canonical-import 稳定短语契约衔接（n3 journal reason=canonical_import_failed 即 A 卡冻结短语）。

## 观察项（不影响接受）

- oracle P1 写"cause_chain 首条注明 not_bad_data 归因"，p1_cw 实际首条是 {"error_class","reason":"adapter_or_staging_failed"}；`not_bad_data` 归因出现在 n1_long 的嵌套 cause_chain 中（原始样本自带）。进程归因语义满足 P1（未归因数据错误），但字面与 oracle 冻结文本不完全逐字对齐——oracle 措辞应当作"语义要求"读。
- ledger 以 note 字段表达 "attempts_run=1 / retry_decision_owner=I-04 deadline"（oracle 期望的独立字段未单独建），语义等价（每 case 恰 1 条 journal、无重试实现、note 明示归属 I-04）。
- N4 两子案各自独立 scratch/journal（各 1 条行），非同一文件两行，"互不覆盖"以 attempt_id+独立文件达成，弱于 append-only 校验但满足语义。
- 杂物：attempt 根目录有 tmpdiag3/upstream_raw_*.txt、scripts/__pycache__/ 存留；均在 attempt 内（allowed_write_roots），无生产污染，建议后续清理。

## 限定申明

- 本结论**不授予生产部署资格**：implementer 全部改动限于隔离副本；生产目录零改动；向生产推广须走后续 IO 卡正式链。
- 本结论**不授予 filing-fetch（FF）领域修改资格**：FF 内部实现归 I-04 owner；本卡只冻结信封消费/转发的兼容姿势。
- **信封契约（cross-cli-error-envelope/1.0 字段名/取值集/fail-closed 规则）的实施者冻结尚未获 I-04 owner ratify**：生效作为 FF 侧约定前必须由 I-04 owner 批签，届时须按 decision.md 更新 oracle 后方可释放任何 FF 改动。
