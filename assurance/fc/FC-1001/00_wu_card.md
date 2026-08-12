# FC-1001 WU 卡片 — 统一 isolated lake fixture（Phase 10 基石）

> 创建 2026-08-12（Phase 9 COMPLETE 后）。状态 pending。Owner: revenue（fixture 供三仓复用，sys.path 模式已有：test_dropbox_full_chain_fc505.py）。

## 目标
单一 temp 目录内三根（companies + dayu + Dropbox）**同时**布局的真实目录形态 fixture：identity/provider snapshots（sidecars）、v2 artifacts（normalized/summary/sections 带 schema_version **column**——FC-906-d 教训）、corruption variants、manifest hash。约束：无真实路径泄漏（manifest 只含相对路径）、无网络、无外部写、Windows/Linux 可重现（路径分隔符无关）。

## 现有可复用基础
- FC-604 `test_three_root_consistency_fc604.py` 的 `_companies_fixture/_dayu_fixture/_dropbox_fixture`（sidecar schema、RootSpec kind→spec 映射、catalog 构造）。
- FC-906-a/d 的 producer v2 契约（schema_version column + metadata 双写、ISO created_at、validate_artifact 门）。
- 生产 canary 样本（紫金矿业/北方华创/平安 sidecar 结构）。

## 设计（isolated_lake.py）
- `class IsolatedLake`：`__init__(tmp_path, seed)` → `build() -> IsolatedLakeManifest`。
- 三根布局：
  - `companies/紫金矿业/raw/financial_reports/annual/紫金矿业2025年年报.pdf` + `.source.json`
  - `portfolio/601899/filings/fil_cn_xxx.pdf` + `meta.json`（dayu 模式）
  - `Dropbox/Stock/金融/保险/中国平安/中国平安2020年中期报告.PDF` + `.source.json`
- identity：entity 表/company_names 由 company_raw root 提供（FC-604 模式）。
- v2 artifacts：**预置**（INSERT artifacts 带 schema_version column='1.0' + metadata_json + derived/ 文件 + producer_events 行）——与生产 canary 同构，测试快；另有一个测试用真实 producer 验证可再生产。
- corruption variants（每个 fail closed 断言）：
  1. `hash_mismatch`：改 derived 文件内容（content_sha256 不匹配）
  2. `truncated_source`：改源 PDF（sources.content_sha256 漂移）
  3. `sidecar_missing`：删 .source.json（admission 拒绝）
  4. `location_inactive`：UPDATE locations status='quarantined'（resolver 不见）
  5. `column_drop`：UPDATE artifacts schema_version=NULL（bundle unsupported——FC-906-d 回归钉住）
- `manifest_hash()`：相对路径 + content sha256 排序拼接的确定性 hash；`manifest()` 无绝对路径。
- 测试 `tests/test_fc1001_isolated_lake.py`：
  - 确定性（同 seed 两次 build → 同 manifest hash）
  - manifest 无真实路径（无 `C:\`、`/Users/`、`郑曾波`）
  - 三根同请求矩阵 resolve 一致（复用 FC-604 CONTRACT_FIELDS）
  - 预置 v2 artifacts validate REUSABLE（列 + metadata）
  - corruption 5 变体各 fail closed（RED 目标：fixture 模块缺失 → ImportError）
  - 真实 producer 再生产验证（小文本文档，快）

## RED/GREEN/mutation
- RED：测试文件 ImportError（isolated_lake 不存在）。
- mutation：M1 删 corruption 断言（变体不再 fail closed → 测试死）；M2 改 manifest 拼 hash 方式（确定性破坏 → 死）。
- 全量：revenue 全量（396+ 基线零新失败）；ruff/compile。

## 执行纪律
- 16 步生命周期；revenue 提交前 `python tools/sync_installations.py --apply`（pre-commit 门禁，memory 教训⑦）。
- 独立 reviewer 干净 worktree（revenue 无大 catalog——reviewer 环境简单）。
- receipts: revenue-forecast/assurance/fc/FC-1001/（fc_id=FC-1001）。
