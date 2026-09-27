# R9 批 3 执行前置复核 — 对照 `01_r9_packet.md` 与 2026-09-11 的树

> 状态：**PLAN_ONLY / 未执行**。本文件补齐 [r9_batch3_checklist.md](r9_batch3_checklist.md) 里"3b/3c 需要替代路径与回滚"这一空白，
> 并对照权威执行包 [revenue `assurance/fc/Phase-14/01_r9_packet.md`](../../fc/Phase-14/01_r9_packet.md)（下文简称"包"）。
> 本轮只读 + 文档：**未删任何文件、未改产品代码**（`git status -- src tests scripts .github` = 0）。

## 0. 结论先行（三件事）

1. **批 3 的权威范围 = 包的 §1 清单（7 项）**，不是我先前列的"3a/3b/3c"。**包里没有 `artifact_backfill.py`**——这与 2026-09-10 的复核一致（它是 FC-901 运维工具，owner 同日撤销了 3a）。**我此前的 3a/3b/3c 拆分作废，以包为准。**
2. **包的进入条件与行号已过期**，且**包文件不在 company-wiki**（见 §3）——执行前必须刷新，否则会按旧坐标动手。
3. **级联替代路径已由包 §3 指定**，本文件把每一项落到"今天的实测调用者 → 具体动作 → 回滚 → 验证"（§2）。**`legacy_close_gate.py` 现在每晚都在观测链上跑**，删除次序必须最后。

## 1. 权威范围（包 §1，7 项）与今日实测调用者

| # | 删除对象 | 包内依据 | **2026-09-11 实测调用者** | 级联动作（包 §3 指定 → 今日落点） |
|---|---|---|---|---|
| 1 | `_scan_root_v1` + v1 分派分支（scanner.py） | v2 生产生效，v1 只读回退不再需要 | 生产：`scanner.py:1401`（facade 默认分支）、`shadow_parity.py:94`、`trace_parity.py:206`；测试：`test_scanner_facade.py`、`test_company_raw_adapter.py:34`、`test_trace_parity_fc601.py`、`test_source_catalog_pipeline.py:435`（monkeypatch） | facade 默认改 **v2**（`scan_root_via_adapter`，已 fail-closed 不回落 v1）；`shadow_parity`/`trace_parity` 的对账基线改用 v2 或随包退役；上列测试同步改/删 |
| 2 | scanner facade 的 v1 默认分支（包写 `scanner.py:1357-1360`；**实际 `1375-1407`**） | 默认改 v2 | `scanner.py:1388` 的 `if v2_scan_shadow:` / `1401` 的 v1 返回 | 默认路径改 v2；`v2_scan_shadow` 参数在 v1 删除后由 GP-002 引入的透传链一并清理（`service.py`/`canonical_writer.py` 的 `v2_scan_shadow_from_snapshot`） |
| 3 | `backfill_v2.py`（整模块） | R9 backlog | **生产**：`dropbox_governance.py:22` `from .backfill_v2 import classify_bucket`、`:162` 调用；`run_backfill` 仅自身 CLI(`:337`) + 测试 | **先把 `classify_bucket` 内联进 `dropbox_governance` 或迁到新家**，再删模块；`test_backfill_v2.py`/`test_backfill_buckets_fc402.py` 随迁 |
| 4 | `portfolio_promoter.py` + CLI `import-portfolio` | R9 backlog | **生产**：`cli.py:27` 导入、`:523` 子命令注册、`:1336/:1395/:1400` 分发；`architecture_gate.py:181` 允许清单；ratchet | 删 CLI 子命令 + parser + 相关测试；`architecture_gate` 允许清单同步收缩 |
| 5 | `visibility_bridge.py`（legacy bridge 循环） | bridge OFF；`_source_metadata` 的 bridge 路径删除 | 生产：`resolver.py:567 def _source_metadata` 及其 bridge 分支（`:822`/`:1115` 调用点）、`scripts/legacy_observer.py:32/99`；测试：`test_legacy_observation.py:83`、`test_fc1204_tier1_gaps.py:23`（`set_visibility`）；`architecture_gate.py:263` 引用其 `LEGACY_PROFILE_KEYS` 语义 | 先删 `resolver._source_metadata` 的 `legacy_bridge_allowed` 参数路径 → 更新调用者与测试 → 删模块 → 同步 architecture_gate 注释/语义 |
| 6 | `legacy_close_gate.py` + observer 的 close-gate 部分 | WU-1500 使命完成 | **生产：`scripts/legacy_observer.py:308-310`（每晚 22:00 都在跑）**；测试 `test_legacy_observation.py` 多处；ratchet | **必须最后删**：先让本门通过（09-12 预期）→ 再决定 observer 命运（**保留 canary-matrix 部分 vs 整体退役 → owner 决策**）→ 然后删 gate 模块与其测试 |
| 7 | `flags.py` 的 `legacy_bridge_enabled` 依赖链 | bridge 删除后无该 flag | `flags.py:26`（FLAGS）、`:37`（REQUIRES）、`resolver.py:322`、`architecture_gate.py:127/139/278`；**数据面**：`.source_catalog/runtime_policy.json` 仍带该 flag | 删 FLAGS/REQUIRES/EXCLUDES 条目 + resolver 读取点 + architecture_gate 建模；**快照里已存在的字段需兼容处理**（历史快照要能读，不能因缺字段崩） |

**附带项（包 §2 门测试第 4 条）**：`architecture_gate._ROOT_HARDCODE_ALLOWED_FILES` 必须把 `scanner.py` 移出（v1 根分支删除后 token-free）；FC-1201 冻结 ratchet **只允许收缩**。

## 2. 执行协议（包 §2/§4 + 今日落点）

**执行前 RED 基线（2026-09-11 实测，只读）**：

```
cd company-wiki
$env:R9_GATE='1'; python -m pytest tests/contract/test_r9_v1_removal_gate.py -q
  → 4 failed  （test_deleted_modules_are_unimportable / test_v1_scanner_function_is_absent /
                test_bridge_flag_removed_from_flags / test_allowlist_shrinks_after_scanner_cleanup）
python -m pytest tests/contract/test_r9_v1_removal_gate.py -q
  → 4 skipped （默认不跑，日常套件不受影响）
```
这 4 条断言就是**执行时的 oracle**：全绿 = 波次落地；任一仍红 = 未完成。

**顺带实测到的 allowlist 现状**：`architecture_gate._ROOT_HARDCODE_ALLOWED_FILES` 当前含
`scanner.py`、`backfill_v2.py`、`portfolio_promoter.py`（以及 `adapter_dispatch.py`、`admission.py`、
`architecture_gate.py`、`canonical_writer.py`、`cli.py` 等）——波次后至少 `scanner.py` 必须移出（门测试第 4 条），
`backfill_v2.py`/`portfolio_promoter.py` 随模块删除一并移出（FC-1201 ratchet **只允许收缩**）。

```
冻结基线（三仓 HEAD + legacy-gate/final_ratchet 输出）
  → 预置 RED 门测试已存在：company-wiki/tests/contract/test_r9_v1_removal_gate.py（默认 skip，R9_GATE=1 才真跑）
  → 按 §1 顺序执行（3/4/5/7 先做级联替代 → 1/2 切默认 → 6 最后）
  → 门测试 RED→GREEN（R9_GATE=1）
  → wiki 全量套件零新失败 + 三仓 CI 全绿 + legacy-gate 复扫 findings=0 + final_ratchet 零残留
  → mutation：复活任一被删对象必须让门变红
  → schema-2.0 receipt + 独立 reviewer + can_accept → Phase 14 账本 R9=COMPLETE → Phase 15 解锁
```

**回滚**：整波一个 commit（或按 §1 分组多 commit），`git revert` 即可；`visibility_bridge`/`backfill_v2` 的替代是**代码搬迁**，回滚同样靠 revert，无数据变更。**唯一有数据面影响的是 item 7**（runtime_policy 快照的 flag 字段）——必须保证旧快照仍可读。

## 3. 执行包本身的三处缺陷（执行前必须处理）

| # | 缺陷 | 证据 | 建议 |
|---|---|---|---|
| 1 | **指针跨仓**：company-wiki 的门测试 docstring 写 `assurance/fc/Phase-14/01_r9_packet.md`，但该路径在 company-wiki **不存在**，实际在 **revenue-forecast** | `test_r9_v1_removal_gate.py:6`；`revenue-forecast/assurance/fc/Phase-14/01_r9_packet.md`（39 行） | 修 docstring 为跨仓路径（**改测试文件属产品改动，待授权**；本轮未改） |
| 2 | **进入条件过期**：包写"period 6 已入账…预计 08-15T05:28Z 后满足" | 包第 3 行 | 执行时以权威账本 `close_gate_allowed` 为准（当前 last-two = P8 ✓/P9 ✗；**预计 2026-09-12 22:00 通过**） |
| 3 | **行号过期**：包引 `scanner.py:1357-1360`，实际 facade 在 `1375-1407`；FC-1201 卡行号同样是旧修订 | 包 §1 第 2 行、§1 表首行 | 执行时按**符号**定位，不按行号；包内行号仅作历史参考 |

**另需注意（包写就之后的新增事实）**：`v2_scan_shadow` 透传链（GP-002）、`canonical_writer` 的第二扫描方、observer 的每晚接线（09-03~09-06）都是包写完之后才出现的——**执行时必须按今天的树重新核对，不能照抄包**。

## 4. 待 owner 决策（3 项）

1. **observer 命运**：R9 后不再需要观测 → observer 是**保留 canary-matrix 部分**还是**整体退役**？（包 §3 未定，属执行时的语义决定）
2. **政策门**：批 3 是否仍按 2026-09-06 决定"等 v2 迁移完全稳定"再执行？技术门（FC-705）预计 09-12 22:00 满足，但**技术门 ≠ 执行许可**。
3. **receipt 形态**：包要求 schema-2.0 receipt + 独立 reviewer + can_accept —— 确认沿用该门槛。

## 5. 明确不做

- 本文件**不执行任何删除**：`git status -- src tests scripts .github` = 0 条目。
- 不把技术门通过当作执行许可；不改冻结集（v5）、`audit_review/`、历史 receipt。
- 不按包内旧行号动手；不照抄包内过期进入条件。
