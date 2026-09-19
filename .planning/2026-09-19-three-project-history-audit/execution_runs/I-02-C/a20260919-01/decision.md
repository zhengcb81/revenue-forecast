# I-02-C / a20260919-01 — 决定：register-existing 恢复入口（D-W02 补充）

日期：2026-09-19。owner：company-wiki 来源系统实施者。性质：**D-W02 的补充决定**（I-02-A
decision.md 明确预留的「已存在 raw 注册的具体 API/CLI 与允许调用者；是否延伸现有 ensure
入口」项），并延续 I-02-B 的错误信封/副作用契约。本卡不改 oracle，先冻结方案再实施。

## 固定输入（逐字段取自 acquisition_aftercheck.json，不按公司名猜路径）

| 样本 | 真实生产路径 | 固定 hash | size |
|---|---|---|---|
| HK | `C:\Users\郑曾波\Projects\company-wiki\companies\小米集團－Ｗ\raw\financial_reports\annual\2026-04-28_hkexnews_12127452_2025年度報告.pdf` | ffd733761633f464d90f6829e9b2d3e089f2dee7054b8ebfe91ef617f222da7c | 4405561 |
| US | `C:\Users\郑曾波\Projects\company-wiki\companies\MICROSOFT CORP\raw\financial_reports\annual\2026-07-29_sec_0001193125-26-323660_MICROSOFT CORP 10-K 2026-06-30.htm` | e3de0053021c02b033272b55551e383b31dba288c86cc12da2e32375e40ecfff | 8585615 |

修改前独立重算（本 attempt 执行记录）：两文件 sha256+size 均与卡固定值一致；byte-identical
复制到 `samples/real_roots/{hk,us}/`（隔离树上平铺，历史子树布局在 case 树里复现）。
sidecar **原样复制不改写**：历史 `receipt.staged_path`（指向生产 staging 的历史路径，现已不
需存在）保留为 provenance 事实，不作迁路径这项历史来源事实的改写。

## 采用方案：canonical_writer 新增 `register_existing_raw` 原语 + `acquisition_service.ensure`
**延伸恢复入口（显式 recovery 输入）**，CLI 以 `ensure --register-existing --recovery-manifest` 接线

### 方案 A（本卡实施）与候选 B 的对比

- **候选 B：仅 canonical_writer 新增 `import_existing_sidecar` API，ensure 不感知**。拒绝
  作为唯一方案：原始故障（IND-D06，runs/07/08/09/10）的断点在 ensure 的
  downloadable 调用链——二次复用经 ensure/resolve 返回 not_found；如 ensure 不去感
  recovery，调用方（filing-fetch 唯一入口）无法在不发明新编排器的情况下走到恢复分支，
  「不重下」目标落空。
- **候选 A'（单纯 ensure 先扫 journal+文件系统自动定位 raw）**：拒绝「自动扫盘定位」部分——
  由文件名/目录推导 raw 位置等于以路径推定身份，正是 N1c 类攻击面（伪 provider ID、
  从文件名补 provider/fiscal_year 会被无声通过）。位置必须由**绑定 manifest 的调用者显式给
  出**；journal 只用于核对，不用于发现。
- **采用 A：writer 原语 + ensure 显式 recovery 输入**。理由：
  1. writer 是唯一 canonical 写入/注册 owner（单一实施 owner），身份/完整性校验天然在它
     的 `_validate_staged` 同级；注册阶段与下载路径共享同一 scan 四道门（completion /
     per-root / target-registered / exact-identity）与同一 provenance 语义 → 阶段可审计。
  2. ensure 延伸为「恢复只消费已证明成功的持久阶段」（D-W02 原文）：恢复键 =
     request(provider/provider_document_id/entity/kind) × sidecar 持久 download receipt
     × bytes hash（本卡重算）× 目标 root（company_raw containment）× root policy
     （reusable_for_filing）。
  3. receipt 不假造：全部身份字段逐字段取自**已落盘的原始 sidecar**（writer
     `_write_provenance` 当时写入的持久 receipt），并对**当前字节**重算 sha256/size 完成核
     对；唯一「差异」是把 receipt.staged_path 指回实测 verify-through 的现行 raw 路径
     （构造 receipt 时显式记载 `recovery_source="existing_raw"`；历史 staged_path 仍在
     sidecar 原字节里）。没有 sidecar / receipt 链 → 拒绝（N1d），不假造。

### 冻结的接口（本卡 4 允许文件内实施）

```text
canonical_writer.CanonicalSourceWriter.register_existing_raw(
    request: SourceRequest, *, raw_path: Path, sidecar_path: Path
) -> CanonicalImportResult(status=REGISTERED_EXISTING_RAW, recovery_source=existing_raw)
  - 前置（顺序）：root policy 可复用 → raw 存在且在 company_raw root 内（目标 root 绑定）
    → sidecar 存在且 == raw 的相邻 provenance（<raw>.source.json，防换包）
    → sidecar schema/字段完整（receipt/candidate/identity 齐备，缺 → provenance_incomplete）
    → bytes 校验：size + sha256(现行字节) == sidecar.content_sha256/byte_size（假造 receipt
      装不进来；N1b 篡改 1 字节即拒）
    → 身份契约：request.provider/provider_document_id 必须显式提供且 == sidecar；entity/
      document_kind/fiscal_year（请求给定时）== sidecar；从不从文件名推导（缺即拒）
    → 已注册文档状态 retired/quarantined → 拒绝（绝不调 _reactivate_if_retired；root 级
      retired 也阻挡 → 不恢复 active，不返回合格 handle）
    → 注册阶段复用 I-02-A 四道门（gate0 中断/gate1 completion/gate2 per-root/
      gate3 target_not_registered/gate4 exact_resolve_identity_mismatch），扫描 receipt
      由同一 scan_catalog(target_content_sha256s=…) 生成
    → 幂等：同 bytes 已注册 → 直接 exact resolve，返回同 identity，无新增行
    → 拒收码（CanonicalImportError 稳定短语）：existing_raw_root_not_reusable /
      existing_raw_missing_sidecar / existing_raw_provenance_incomplete /
      existing_raw_bytes_mismatch / existing_raw_identity_contract /
      existing_raw_status_not_active
acquisition_service.SourceAcquisitionService.ensure(request, *, recovery: SourceRecoveryInput|None)
    SourceRecoveryInput(raw_path, sidecar_path)（frozen dataclass，相邻性同样校验）
    - resolution 已 REUSED → 走原 reused 返回（P2 零新增）
    - 否则 recovery 走 writer.register_existing_raw；成功 → journal outcome=
      registered_existing_raw（additive 枚举）+ SourceEnsureStatus.REGISTERED_EXISTING
      （acquisition=null：如实报告没有发生 discovery/下载，不造 AcquisitionResult 假象）
      失败 → journal outcome=failed / reason=existing_raw_register_failed，原样抛出
cli.ensure --register-existing --recovery-manifest <json>（manifest: raw_path/sidecar_path/
    authorized_caller="I-02-C sample-copy-manifest"）；与 --allow-download 互斥（写入
    恢复路径永不下载，故也不做 paused-acquisition 审计/暂停判定）
```

### 兼容影响（冻结）

1. `SourceEnsureResult.acquisition` 类型放宽为 `AcquisitionResult | None`；旧路径永远非
   None，仅恢复路径为 null（additive JSON，消费方读 failed/reused 语义不变）。
2. `ACQUISITION_OUTCOMES` 增 `registered_existing_raw`（additive；旧行可读不变，schema 1.0）。
3. `CanonicalImportStatus` 增 REGISTERED_EXISTING_RAW（additive enum，旧消费方按未知值
   fail-closed 处理——本 card 内 writer 返回值只经 ensure/cli 通道）。
4. 沿用 I-02-A 契约：scan completion/target_files 语义、四道门错误短语逐字保留；沿用
   I-02-B：失败信封如实报副作用，raw 保留不回收，恢复只走注册。
5. 扫描/resolve/registry 实现引用 I-02-A/I-01-A 的 override 副本（models/scanner/service/
   config/adapter_dispatch），行为契约与该两 attempt 的冻结决定一致，本卡不改动它们。

### 反例/拒绝的替代（汇总）

- 假造 staging receipt + 走既有 import_staged：拒绝——previewed hash 校验虽做，但 receipt
  的 staged_path 语义是「本次下载暂存」，把它换指向 canonical raw 是制造一次没发生的
  下载事件；journal 的 download 事件无法如实归零。
- 删除后重建 sidecar 再注册：拒绝——sidecar 是不可变 provenance，重建 = 造事实。
- `_reactivate_if_retired` 偷换为恢复路径：拒绝（卡 N2 明令）——恢复入口必须在 retired/
  quarantine 时不返 green；重新获取是唯一「回 active」路径。
- 从文件名/目录名推导 provider/fiscal_period：拒绝——身份只能来自 sidecar 持久字段或
  显式请求字段（N1(c) 拒绝码覆盖）。
- 无可靠 receipt 时以存在推定合法：拒绝——缺 sidecar 或 sidecar 无 receipt → 拒收（D-W02
  「无可靠 receipt 的拒绝规则」）。

### 恢复规则（冻结）

- register-existing 任何阶段失败：不删 raw / sidecar / 已提交行；错误如实分类；
  journal 记 failed，下一次恢复从同一 manifest 重入（幂等）。
- 同 bytes retired/quarantined 或 root 禁复用：**本入口永不**调
  _reactivate_if_retired、不 UPDATE active、不返回 ResolutionResult 匹配；恢复动作 returns
  拒收码，处置权留给人（documents restore CLI 或重新授权下载——都不在本卡自动发生）。
- catalog 损坏/manifest 丢失：停该样本（卡停止条件），保留现场。

### 复用 ≠ 审核 / 复用 ≠ 工件完成（挂接 I-02-A 契约）

- register→qualification→exact resolve 三阶段全部完成后返回的 handle 只证明 source 链
  资格；`prompt_injection_status` 缺 review receipt 时如实 `not_reviewed`，`bundle_usable`
  独立计算（本卡无审核、无 artifact）→ 复用成功仍阻断，不宣称审核/工件完成。
