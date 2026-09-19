# W01 oracle（冻结于运行被测实现之前）

冻结时间：2026-09-19；写于任何被测函数运行之前（修改前对照除外；所有 expected 在运行 case 前已成文）。
锚定对象：doctor `diagnose` 输出的逐根错误列表 + `SourceCatalog`/`scan_catalog` 每根 strategy/adapter 选择与 per-root fail-closed 错误。
说明：doctor 与 scan 共用同一判定函数 `effective_root_profile`（D-W01-A，设在 config.py）；本 oracle 的所有 expected 由本文件自带的判据手推，不由被测函数生成。

## 通用种子规则（手推判据）

判据分类（与 decision.md 一致）：
- R1 unknown_adapter：adapter_id 声明但不在 REGISTERED_ADAPTERS。
- R2 no_scanner_impl：已注册但不在 scanner factory 表。
- R3 version_unsupported：adapter_version_range 声明区间不含注册版本 "1.0.0"；语法不支持同样判此。
- R4 unknown_profile：admission_profile_id 声明但不在 ADMISSION_PROFILES。
- R5 readonly_with_write_target：read_only=True 且 canonical_write_target 非空。
- R6 half_activated(a)：root 无 adapter_id 且快照解析为 v2（生产 CFG-REAL 形状）。
  half_activated(b)：adapter 声明 root 的 admission_profile_id 与注册表 profile 不一致。
  half_activated(policy)：legacy_bridge_enabled=true 且任一 v2 flag=true（记为 root "runtime_policy"）。
- strategy 预测：`v2_scan_shadow 有效 or adapter_id 声明` → "adapter"，否则 "legacy"（=F-BAR-10 现行）。
- prod flags（复制原件）：legacy_bridge=false, v2_bundle=false, persist=true, resolve_active=true,
  resolve_shadow=true, scan_shadow=true → cutover=v2。
- CFG-GOOD policy flags 全 false → cutover=v1（批准的 legacy 状态）。

## W01-P1（CFG-GOOD）— 预期

布局：companies(带 company_raw_v1)/portfolio(带 dayu_filing_v1)/dropbox_stock(无 adapter)/future_lake(sidecar)。
policy：全 false + 无 bridge → legacy 批准态。

1. doctor：effective-config 部分零错误（三个根全部满足：company_raw/dayu 声明可派遣 adapter；
   dropbox 无 adapter 但快照缺失→legacy 批准态；future_lake sidecar 可派遣）。
   （非本判据的其他基础 noise，如 redirected dropbox 路径/安全 master 占位警告，两项对照前后一致，单独记录。）
2. doctor 推测的每根 adapter_id：company_raw=company_raw_v1；dayu_portfolio=dayu_filing_v1；
   dropbox_stock=None(legacy)；future_lake=sidecar_filing_v1。
3. scan（dry_run=False，隔离 scratch 库，v2_scan_shadow=False）：strategy =
   {company_raw: adapter, dayu_portfolio: adapter, dropbox_stock: legacy, future_lake: adapter}
   —— 与 doctor 推测完全一致（P1 主断言）。
4. 实扫：company_raw 根 1 份原件（Acme 2025.pdf + .source.json sidecar）→ 1 条 original_primary
   候选 + sidecar 作 metadata（非独立 document）；dropbox plain 文件照 legacy 扫；每根 status 正常无 error。

## W01-P2（CFG-FIFTH = CFG-GOOD + archive_extra）— 预期

5. doctor：archive_extra（directory + sidecar_filing_v1 + read_only=true + 无 canonical_write_target）
   不因 root 名陌生被拒，零 effective-config 错误。
6. scan：strategy 含 archive_extra: adapter；实扫候选只含 2 个 .txt 原件（a.txt 有 sidecar →
   original_primary；b.txt 无 sidecar → original_primary + missing_sidecar 修复提示）；
   独立 .source.json 文件（c.source.json）不被当独立原件（documents 位置数 = 2，
   无任何以 .source.json 结尾的 document 标题）。

## W01-N1（CFG-REAL）— 预期

布局：三根（company_raw/dayu_portfolio/dropbox_stock）均无 adapter_id + 生产 flags
（scan_shadow=true）；future_lake 带 sidecar；路径全部重定位到 scratch。

修改前（managed evidence）：
- doctor：无 effective-config 洞见（生产 doctor 不读 policy），对 CFG-REAL 输出 healthy 噪声
  （dropbox 路径检查因 redirect 报失效——记录为基线，不计入判定）；核心差异= doctor 与真实
  scan 的 effective 判定不同源。
- 真实扫描（隔离库）：每根走 adapter（use_adapter = v2 快照 True），三根 adapter_for 全部
  拒绝（"no adapter_id"），per-root error_detail，批次继续；无静默 legacy 回落，不 healthy。

修改后（被测）：
- doctor：per root 逐根列出：company_raw / dayu_portfolio / dropbox_stock 各自
  half_activated(R6a)；错误消息含 root 名与 "no_adapter_but_snapshot_v2" 形状描述；
  doctor NOT healthy（effective-config 部分非零）。
- 真实扫描（隔离库）：三根各自 fail-closed，error_details 中逐根错误类别 = half_activated
  （与 doctor 相同类别）；strategy 记录仍为 adapter（与现行 use_adapter 规则一致），不静默
  legacy；future_lake 保持正常（scratch 无内容 → 无候选，无 error）。
- 不把 unknown 归并为同一错误：CFG-REAL 每个失败根的错误类别 = half_activated，且
  N2 的五变异类别互不相同（见下）。

## W01-N2（五变异，独立 case）— 预期

基础：单根（kind=company_raw，路径 scratch 内，无快照 → legacy 批准态），逐 case 单变异。

| case | 变异 | doctor 预期 | scan 预期（隔离库、无静默回落） |
|---|---|---|---|
| N2-1 | adapter_id: nonexistent_adapter_9f | load 拒绝 CFG-01：“adapter_id 'nonexistent_adapter_9f' not registered”；类别 unknown_adapter | load 同拒；无 scan 执行 |
| N2-2 | adapter_id: generic_document_v1（已注册无 factory） | 加载通过；doctor 类别 no_scanner_impl（单根一条） | fail-closed per root，类别 no_scanner_impl（消息来自同一判定接线；现状为 dispatch 消息 "has no scanner adapter implementation"） |
| N2-3 | adapter_id: company_raw_v1 + adapter_version_range ">=1.11.0"（eleven） | 加载通过；doctor 类别 version_unsupported（1.0.0 ∉ [1.11,∞)） | fail-closed per root，类别 version_unsupported（修改前 baseline：现行 scan 无版本门，会正常扫——记录 before 值） |
| N2-4 | admission_profile_id: no_profile_zz | load 拒绝 CFG-02：“unknown (CFG-02)”；类别 unknown_profile | load 同拒 |
| N2-5 | 错误区分证明 | 五个 case 的错误类别/文本互不相同：unknown_adapter / no_scanner_impl / version_unsupported / unknown_profile 各自独立（另 CFG-REAL=half_activated 亦不同） | 不为第五 root 放行所有 directory：archive_extra 只有带可派遣 adapter 才通过 N2 放行面 |

## W01-N3（能力/激活组合）— 预期

- N3-1 readonly_with_write_target：directory 根 + sidecar_filing_v1 + read_only: true +
  canonical_write_target: "${PROJECT_ROOT}/scratch/write_target"。
  before baseline：生产 loader 以 "unknown fields: ['canonical_write_target']" 拒绝（CFG-01 邻近）。
  after：loader 接受字段传递至 RootSpec；doctor 类别 readonly_with_write_target；
  scan fail-closed per root（同类别），无写目标副作用（原件/配置/policy 无副作用：仅 scratch
  库内错误记录）。
- N3-2 half_activated(b)：directory 根 + sidecar_filing_v1 + admission_profile_id:
  generic_document_v1（≠ 注册表 financial_evidence_v1）。
  加载通过；doctor 类别 half_activated（detail= adapter profile 与 registry 不一致）；
  扫描 fail-closed per root。
- N3-3 无副作用断言：所有负例运行后，生产仓 hash 与运行前一致（binding 复核），scratch 内
  仅出现 catalog.sqlite3 与其 journal。

## 修改前对照（before）记录格式

`before/effective-config.before.json`：每根记录两入口预测——doctor 的（现行：无 adapter 视角）
vs scan 的（v2_scan_shadow_from_snapshot + adapter_for 判拒）。CFG-REAL 期望不同源性显现：
doctor three-root 无洞见（healthy 噪声），scan 三根 adapter 拒绝。
`before/per-root-scan-and-resolve.json`：Modification 前对 CFG-GOOD/CFG-FIFTH 先记录 baseline
（strategy 与失败面——用生产 source 只读跑一次实扫 scratch 库），作为 after 的对照。

## 退出判据映射

- 配置负例在预检（doctor）被拦：N1/N2/N3 的 doctor 输出非零且类别独立。
- 合法额外同构 root 被实扫/resolve 证明：CFG-FIFTH archive_extra 实扫候选=2，
  sidecar 不作独立原件。
- 不外推未知布局/真实部署：dropbox_stock 不被赋予 adapter；此判断依据=sidecar_filing_v1
  与 Dropbox 实际布局无法在本 attempt 内只读证明（卡停止规则），记录于本文件与 samples
  （CFG-GOOD dropbox root 保持无 adapter）。
