# D-W01 决定 — doctor 与 SourceCatalog.scan 共用同一 effective 配置解析（I-01-A / I-02-A）

日期：2026-09-19。attempt：a20260919-01。本决定按卡 I-01-A 兼允许范围（可在 config.py 内新增函数，不引入新文件路径）冻结。

## 候选

- **A（采纳）**：在既有 `src/company_wiki/source_catalog/config.py` 内新增共享函数
  `effective_root_profile(root, *, scan_shadow_active)`（单一 effective 判定；纯函数，只依赖
  `models.RootSpec` + `adapters.registry`），config_doctor 与 scanner._scan_catalog_impl 均调用
  这一函数得到同一判定结构。
- **B（拒绝）**：新建共享模块 `source_catalog/config_effective.py`。理由：卡允许直接改 config.py，
  B 增加一个未经本批架构 reviewer 具名走过的路径，且引入 config/scanner 之外的第 4 个 import
  面，无增益。
- **C（拒绝）**：把判定做成 scanner 内部函数，doctor 反向 import scanner。理由：doctor（脚本层）
  反向依赖 scanner 重模块（store/normalizer 等 import 面），且 scan "只接线" 原则要求 scanner
  复用同一判定而不是拥有它。

## 采纳后行为（冻结）

1. `effective_root_profile` 返回 dict：`root_id/kind/read_only/adapter_id/adapter_registry/
   version/version_range/scanner_impl/admission_profile_id/strategy/errors`。`strategy` 是本函数
   对 scan 的预测：`"adapter"` if (v2_scan_shadow 有效 or adapter_id 声明) else `"legacy"`，
   与 F-BAR-10 现行 `use_adapter = v2_scan_shadow or root.adapter_id is not None` 完全一致。
2. 错误类别（独立、互不相吞）：`unknown_adapter / no_scanner_impl / version_unsupported /
   unknown_profile / readonly_with_write_target / half_activated`。判据：
   - unknown_adapter：adapter_id 已声明但不在 REGISTERED_ADAPTERS。
   - no_scanner_impl：已注册但不在 scanner factory 表（generic_document_v1 现状）。
   - version_unsupported：adapter_version_range 声明的区间不含注册版本（1.0.0）。
     区间语法：>=,>,==,<,<=,!= 逗号分隔；不支持区间 → 同期 version_unsupported（更严）。
   - unknown_profile：admission_profile_id 已声明但不在 ADMISSION_PROFILES。
   - readonly_with_write_target：read_only=True 且 canonical_write_target 非空（该字段本卡
     补入 config loader 的允许字段，加载器原先直接拒绝该字段于 unknown fields）。
   - half_activated：无 adapter_id 的 root 在 v2_scan_shadow 有效（快照解析为 v2/present）时仍走
     旧 legacy 读法 = 未批准组合（生产 CFG-REAL 形状）；以及 adapter 声明的
     admission_profile_id 与注册表 profile 不一致（未批准激活组合）。快照缺失/invalid 解析为
     非 v2（与 GP-002 degrade-to-v1 一致），此时无 half_activated。
   - policy 级：legacy_bridge_enabled=true 且任一 v2 flag=true → 以 root_id="runtime_policy"
     行报 half_activated（激活组合表：bridge 与 v2 并开是未批准半激活）。CFG-REAL 生产 policy
     bridge=false，不触发此行。
   - 错误收集不 mutually exclusive：多缺陷 root 列全部缺陷；但任一缺陷导致该 root 在 scan 中
     失败关闭（不产候选、记按 root 的 error_detail、批次继续），无 legacy 回落，与 FC-303 EX-08
     / F-BAR-10 现行 per-root 语义一致。
3. doctor（config_doctor.diagnose）接线：加载 config 成功后新增
   `_effective_config_checks(config, root_cfg_dir, problems)`：解析 catalog_dir 下
   runtime_policy.json（缺失/解析失败 → scan_shadow_active=False，与 scanner 同规），逐 root
   判定，并把每个错误以 `root '{root_id}' adapter_id=... effective-config: {code}: {detail}`
   追加。旧 `_ALLOWED_DIRECTORY_ROOTS` 名单删除（⇒ 不再有 root 名 allowlist；kind=directory 根
   的合规由上述能力契约决定：声明可派遣 adapter 的根合法；无 adapter 根仅允许在没有有效 v2
   快照的批准 legacy 状态下运行，否则 half_activated）。这替换旧
   `test_e2e_f03_second_directory_root_fails_fast` 的实现依据（旧断言反映旧名单；卡明示按
   D-W01 分类对齐，且 WX-P2 要求陌生 root 名不被拒）。
4. scanner（_scan_catalog_impl）接线：在每个 root 的 strategy 记录后、调用
   scan_root_strategy 前，用同一 `effective_root_profile(root, scan_shadow_active=v2_scan_shadow)`
   判断；有错 → 记 error_detail（沿用 <5 容量上限）、errors/new_errors +1、continue；无错 →
   按原有行为继续。不其它改动。
5. config.py 最小增值：paths 同旧；allowed_root_fields 增加 `canonical_write_target`（传递进
   RootSpec；cohort 不开）；adapter_version_range 变可判定区间输入（models 已有字段，此前
   loader 透传但不校验；本卡不改 models/models 模型，仅 loader 透传已支持字段）。
6. service.py：不改正主路径（v2 flag 解析已与卡锚点一致）。diff 可为空或仅注释级；presence
   记录在 changes.diff。

## 反例（拒绝理由）

- 不用"关 v2 / 开 legacy bridge" 当修复：CFG-REAL 生产 policy 不得改动即可复现错误分类。
- 不为第五 root 放行所有 directory：archive_extra 必须声明可派遣 adapter 才能通过 doctor；
  纯 directory 根只有在无有效 v2 快照的批准 legacy 状态才放行。
- 不以文件后缀猜 Dropbox 布局：CFG-REAL/CFG-GOOD 中 dropbox_stock 保持无 adapter 声明；
  判断依据在 samples 不改化，停止规则记录在 oracle.md。

## 兼容影响与恢复

- 仅本 attempt 副本（A\iso\override + doctor 副本）生效；生产仓零写。回滚 = 删除本 attempt
  差异，生产原件 hash 不变（见 binding.json before/after）。
- 既有测试影响声明：GP002 转发与 F-BAR-10 语义不动（对应 test 文件不修改）；旧 doctor 名单
  断言按本决定改为能力分类（不删测试，改动发生在此后分派的手动对齐步骤的隔离测试，不在本卡
  产品范围内）。
