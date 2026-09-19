# oracle.md — I-02-C / a20260919-01（冻结于任何被测函数调用之前）

冻结时刻：2026-09-19，写于 iso/override 任何修改与任何 runner 调用之前。预期值全部独立
推导（固定样本 hash 来自卡原文 + acquisition_aftercheck.json；错误码来自 decision.md 冻结
的收录码词汇表），不调用被测函数生成。

样本（已由修改前核对确定，见 after/sample-copy-manifest.json）：

- HK：sha256=ffd733761633f464d90f6829e9b2d3e089f2dee7054b8ebfe91ef617f222da7c，
  size=4405561，provider=hkexnews，provider_document_id=12127452，fiscal_year=2025，
  entity=小米集團－Ｗ，security_id=01810，market=HK，form_type=FY。
- US：sha256=e3de0053021c02b033272b55551e383b31dba288c86cc12da2e32375e40ecfff，
  size=8585615，provider=sec，provider_document_id=0001193125-26-323660，
  fiscal_year=2026，entity=MICROSOFT CORP，security_id=MSFT，market=US，form_type=10-K。

全局不变量（所有正/负例）：

- I0.1 provider deny-on-call stub 计数：discover=0 且 fetch=0（全 case 汇总后仍 0）。
- I0.2 真实生产路径字节不变（只读）；复制品 hash == 固定 hash；除 N1b case 树外所有
  case 树内 raw bytes before/after 相同。
- I0.3 sidecar 字节不改写（除 N1d case 的 case 内副本先行破坏），历史
  `receipt.staged_path` 原样保留。

## W02C-P1（正例，HK 与 US 各自独立 case 树）

前置：raw+sidecar 已放置于 case 树 companies/<公司>/raw/financial_reports/annual/，
catalog 初始扫描后对应 sources/documents/locations 行为 0（未注册形态）；providers 全
deny-on-call。

预期（每样本）：

- P1.1 ensure(request, recovery=...) 返回 status=`registered_existing`，canonical_import.
  status=`registered_existing_raw`；acquisition 为 null（如实无 discovery/下载）。
- P1.2 resolution.status=REUSED_EXACT，match.content_sha256 == 固定 hash，
  match.canonical_path == case 树内该 raw 绝对路径；provider/provider_document_id/
  fiscal_year 保持原始值（HK: hkexnews/12127452/2025；US: sec/0001193125-26-323660/2026）。
- P1.3 注册阶段 receipt：scan target_files 含该 content_sha256 且 registered=true；
  register→qualification（documents 1 行 + locations active 1 行 + sources 1 行，
  content_sha256/byte_size 匹配）→ exact resolve 三阶段一一可见（registration-stages.json）。
- P1.4 raw+sidecar 字节 hash before/after 相同；staged 目录无新增文件；journal 新增
  outcome=registered_existing_raw 行，attempt 内容含 content_sha256/canonical_path/provider。
- P1.5 复用 ≠ 审核：envelope (build_resolution_envelope) 中 prompt_injection_status=
  not_reviewed、bundle_usable=False（缺审核 receipt；不宣称工件/审核完成）。

## W02C-P2（正例：第二次 exact 复用）

前置：P1 已完成注册。调用原 exact 请求（同 entity/kind/fiscal_year/provider/pdoc）经
ensure 无 recovery（allow_download=False）。

- P2.1 resolve/ensure 返回 reused（reader envelope：status=reused，reason=
  existing_catalog_source_reused_before_adapter）；同一 source_id/content_sha256/版本。
- P2.2 零新增：sources/documents/locations 计数与 P1 后一致；journal 无
  downloaded_new/reused_after_discovery 之外的下载类新增行；provider 计数仍 discover=0/
  fetch=0；无新原件（canonical 文件集合不变）。
- P2.3 envelope 仍 prompt_injection_status=not_reviewed、bundle_usable=False（复用≠审核）。

## W02C-N1（四个负例，各独立 case 树；每个都预期：异常为 CanonicalImportError、含
对应稳定短语、catalog 对应 sources/documents/locations 行为零新增、provider 计数 0、
不改写 sidecar、不自动从文件名补身份）

| 案号 | 注入（case 树内副本上做） | 冻结预期错误短语 |
|---|---|---|
| N1a(删sidecar) | 删除 raw 相邻 `<raw>.source.json` | `existing_raw_missing_sidecar` |
| N1b(篡改1字节) | raw 复制品第 16 字节 FLIP 后放回 case 树（sidecar 原样） | `existing_raw_bytes_mismatch` |
| N1c(伪造provider ID) | 请求 provider=`sec`/provider_document_id=`12127452`（张冠李戴）+ 另一变体（request.provider 缺省 None） | `existing_raw_identity_contract` |
| N1d(缺receipt链) | case 内 sidecar 副本去掉 `receipt` 键后放回 | `existing_raw_provenance_incomplete` |

- N1 公共：journal 各新增 outcome=failed / reason=existing_raw_register_failed 一行；
  catalog 四表对目标 hash 均无行（登记 0）；无 handle 返回。
- N1c 补充：缺省 provider 的请求同样拒绝（不从文件名自动补 provider/fiscal_year）。
- N1b 补充：篡改后字节 hash 与固定值不同，被拒后 case 内 raw 保持篡改字节（不得自愈改回），
  catalog 无行。

## W02C-N2（边界负例，各独立 case 树）

- N2a（同 bytes 已 retired）：P1 注册成功后经 store.retire_document 把 document_id 置
  retired，再次以相同 manifest/请求调 register-existing——预期：CanonicalImportError
  `existing_raw_status_not_active`；**绝不**调用 _reactivate_if_retired（harness spy 计
  数=0，实施后同复查）；documents.source_status 仍=retired；不返回 ResolutionResult/
  handle；provider 计数 0；sidecar/raw 字节不变。
- N2a2（quarantined 变体）：同上但 SQL 将 document source_status 置 quarantined——预期
  同 N2a（同短语拒绝）。
- N2b（root 禁复用）：case 树根配置 company_raw root 以 reusable_for_filing=False 建库，
  raw 已在树内但未注册——预期：CanonicalImportError `existing_raw_root_not_reusable`；
  registration 的后续阶段（扫描注册/resolve）不运行（fail-early）；catalog 保持空目标行；
  provider 计数 0。

## 逐案拒绝后的持久化预期（公共）

- 拒绝路径 journal 只增 failed 行；已注册行（N2a 登记后 retire 的行）保持原状态，
  恢复/拒绝路径不清洗任何已有行。

## 记录产物

- after/zero-provider-events.json：全 case provider 计数表（必须全 0）。
- after/registration-stages.json：P1 两样本 register→qualification→exact resolve 的逐阶
  段证据（run id / content hash / 行数 / journal attempt id）。
- after/exact-resolve.before-after.json：两样本注册前（未注册形态，not found/reused 状态
  实测）与注册后（REUSED_EXACT + identity + envelope 资格字段）对照。
