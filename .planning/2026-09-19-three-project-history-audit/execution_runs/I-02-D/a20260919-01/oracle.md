# oracle.md — I-02-D / a20260919-01（冻结于任何被测函数调用之前）

冻结时刻：2026-09-19，写于 iso/override 三个允许文件任何修改与任何 runner 调用之前。
预期值全部独立推导：样本 hash/size 取卡+I-02-C sample-copy-manifest 固定值（已在本
attempt 修改前重算一致，见 binding.json）；错误短语取 I-02-A/I-02-C decision.md 冻结
词汇表；journal 去重语义按 acquisition_journal.py:87 现行实现（内容 hash）独立推演。
**不调用被测函数生成 expected。**

样本（byte-identical 复制，修改前已重算核对）：

- HK：sha256=ffd733761633f464d90f6829e9b2d3e089f2dee7054b8ebfe91ef617f222da7c，
  size=4405561，sidecar sha=8228741d…，provider=hkexnews，provider_document_id=12127452，
  fiscal_year=2025，entity=小米集團－Ｗ，security_id=01810，market=HK，kind=annual_report。
- US（仅作无关预注册内容）：sha256=e3de0053…，size=8585615。
- request_id 固定：三次重入用同一 SourceRequest（同 entity/kind/year/provider/pdoc/
  as_of/mode/allow_download）→ 同 request_id。

全局不变量（所有正/负例）：

- I0.1 provider deny-on-call stub 计数 discover=0 且 fetch=0（P2 两进程亦然）。
- I0.2 生产路径只读；case 树内 raw bytes（除注入案例外）before/after 相同。
- I0.3 逻辑完成键：同 bytes 在 sources(+content_sha256)/documents(active)/locations
  (active original_primary, company_raw) 恰好 **1** 行/location——用独立 sqlite3 SQL 直接
  数（oracle 独立实现，不调用被测模块）。
- I0.4 审计 attempt 键：acquisition_attempts.jsonl 每行 attempt_id = 内容 hash；重放同
  outcome → 同 attempt_id → 不新增行；不同 outcome/错误 → 新行。审计历史**不压缩**。

## W02D-P1（正例：一次成功已登记 → 同 request 重放三次）

前置：clean case 树；HK raw+sidecar 放置（未注册形态，先放 US 无关条目作基线内容）；
第一次 ensure(request, recovery) 经 I-02-C 入口成功注册。然后**同 request** 再进三次
（带同 recovery manifest 的 register-existing 重入 ×2 + 一次 catalog-first 纯 reuse）。

预期：

- P1.1 第一次：status=registered_existing；之后每次重入返回可对账调用结果：
  - register-existing 重入：catalog-first → status=reused（resolution REUSED_EXACT），
    journal outcome=reused_before_download；
    （若实现返回 registered_existing_raw 幂等结果，亦须 journal 可对账且零新增行——两者
    之一，以实测记入 matrix；不得既不新增行又报 imported/downloaded。）
  - 纯 ensure（无 recovery，allow_download=False）：status=reused。
- P1.2 逻辑层：三次重放后 sources(content_sha256=HK) == 1；documents(active) == 1；
  locations(active original_primary company_raw) == 1；canonical 文件集合不变（零新
  raw/零新下载）；sidecar 字节不变。
- P1.3 审计层：journal 按 outcome 语义保留——`registered_existing_raw` 1 行（首次）+
  reused 类行（重入；同内容重放按内容 hash 去重不重复膨胀）+失败类（无）。总行数 ≥1 且
  = 独立语义数；**不等于 1 条强制压缩**，也**不得每重放一次盲目 +1 下载类行**。
- P1.4 每次调用可对账：返回 dict 含 schema_version/request_id/content_sha256/
  resolution.status；三次返回的 match.source_id/content_sha256/canonical_path 一致。
- P1.5 provider 计数全程 0。

## W02D-P2（正例：两进程 barrier 并发注册同一已存 raw）

前置：两份 clean scratch 副本同参数构造（同一 case 树两个进程会共享 sqlite——预期即
如此：两独立**进程**（subprocess，真实进程隔离）对**同一** catalog 注册同一 raw）。
每进程：装 bootstrap→建 service→barrier（文件轮询 barrier，两进程都到齐才放行）→
ensure(request, recovery)→把 stdout/stderr/exit/返回 status 写各自 JSON。

预期：

- P2.1 最终逻辑层：sources==1、documents(active)==1、locations==1（两进程竞争后只有
  一个有效登记）。
- P2.2 两进程返回：**至少一个** REGISTERED_EXISTING/registered_existing_raw 成功；
  另一进程要么同样成功幂等（同 identity），要么 CatalogOperationLockedError 类可重试
  竞争（exit≠0 但错误分类为锁竞争）——两者都合格；**不允许**两进程各自报「新登记成功」
  而逻辑层出现 2 行。
- P2.3 journal 不丢：所有行可读、无截断/损坏尾行（read_all 不抛）；成功行 ≥1。
- P2.4 raw+sidecar 字节不变；provider 计数 0。

## W02D-N1（负例：同 bytes 不同 provider identity）

前置：clean 树，HK raw+sidecar 注册成功（P1 形态）；然后构造**下载路径变体**：staging
内放同 bytes 副本（hash==HK_SHA），candidate/receipt 携带**不同 provider identity**
（provider=sec / provider_document_id=0001193125-26-323660——US 的身份、HK 的字节），
调 writer.import_staged(request_hk, candidate_us_identity, receipt_us_identity)。

预期：

- N1.1 **不返回 DEDUPLICATED 成功**：抛 CanonicalImportError，短语含
  `exact provider identity did not resolve` 或 `(exact_resolve_identity_mismatch)`
  （I-02-A gate4 词汇，fail-closed）。
- N1.2 staging 文件**保留**（不删——恢复证据）；已注册 canonical raw+sidecar 字节不变。
- N1.3 逻辑层无任何新行（sources/documents/locations 不变）；无新 raw 文件。
- N1.4 journal：dedup 未成功 → 无 deduplicated_after_download 成功行；由 service 层
  包装调用时 journal 增 1 行 failed（reason=canonical_import_failed）；直接 writer 层
  调用（不经 service）则 journal 不变（writer 无 journal——oracle 按调用层如实记录）。
- N1.5 provider 计数 0（import_staged 不触 adapter）。

## W02D-N2（负例：同 request 换 hash / identity / policy）

- N2a（换 hash=新版本）：同 request 字段但 bytes 为**新内容**（HK 样本第 16 字节 flip，
  新 hash）→ 预期：不得命中旧完成状态（旧 journal registered_existing_raw/reused 行不
  被复用为「已完成」）；走新 import 路径产生**新 source 行**（新 content_sha256），
  旧 raw 文件与行**不被覆盖/删除**；canonical 目标文件名按 hash-suffix 纠偏不冲突。
  journal 新增新 hash 的 imported/registered 行。
- N2b（换 identity）：同 bytes、request.provider/pdoc 换成不同值（如 provider=sec）→
  经 register-existing：Gate R6 `existing_raw_identity_contract` 拒绝；经 import_staged：
  同 N1（exact resolve 不命中）。不命中旧完成；需重新资格审查（resolution 不返回
  REUSED_EXACT handle）。
- N2c（换 policy）：root reusable_for_filing=False 的树上对同 bytes 调 register-existing
  → `existing_raw_root_not_reusable` 拒绝（I-02-C R1 契约延续）；不产生行。

## W02D-N3（负例：dayu/external 同 bytes 或 retired 同 bytes）

- N3a（dayu 同 bytes）：case 树加 dayu_portfolio root，同 bytes 文件只存在于 dayu root
  （companies/ 内无）→ 走 import_staged（下载路径）→ 预期 **IMPORTED_NEW**（不是
  dedup）：`_existing_original` 不把 dayu 位置当 canonical dedup 目标；canonical 落在
  company_raw root；不把外部 root 同 bytes 当写目标。契约=
  test_writer_dedup_ignores_dayu_portfolio_locations 原样（不扩大恢复授权）。
- N3b（retired 同 bytes，register-existing 路径）：注册成功后 retire，同 manifest 重入
  register-existing → `existing_raw_status_not_active` 拒绝；不调 _reactivate_if_retired
  （spy 计数 0）；document 保持 retired；不返回 handle。
- N3c（retired 同 bytes，显式 re-download import_staged 路径）：同 bytes 重新下载
  import → Phase 15.6 契约原样：imported 成功且 document 回 active（显式用户重获权，
  与 N3b 的恢复入口边界不同——两者界定不改）。

## 记录产物（oracle 独立 SQL/文件清单）

- after/idempotency-matrix.json：每 case 逐次调用的 status/journal 行数/SQL 行数/provider
  计数矩阵（P1 三次、N1、N2a/b/c、N3a/b/c）。
- after/two-process-trace.json：P2 两进程各自 stdout/stderr/exit/status/barrier 时间戳、
  最终 SQL 行数、journal 完整行。
- after/logical-rows-vs-attempts.json：全部 case 的 SQL 有效记录数（sources/documents/
  locations）vs journal attempt 行数（按 outcome 分组）——审计允许多条，业务唯一。
- 独立 SQL：runner 内直接 sqlite3 连 db_path 数行（不用被测 store API 数行作 oracle）。
