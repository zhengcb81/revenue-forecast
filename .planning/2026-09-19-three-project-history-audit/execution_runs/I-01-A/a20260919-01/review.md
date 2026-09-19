# review.md — I-01-A / attempt a20260919-01（独立 reviewer）

结论：**accepted_scoped**（附 3 项记录性发现，均非阻断）

reviewer：独立复核，只写本文件与 attempt 内 `review_rerun/`（reviewer 自跑证据）；三仓零写。

## 各核对点结论（一句话）

1. **decision.md（D-W01）**：合格——给出候选 A/B/C 与理由（A=既有 config.py 内 `effective_root_profile` 共享函数；B 拒因新增未走审路径；C 拒因 doctor 反向依赖 scanner 重模块），有反例段（不给第五 root 全面放行、不用关 v2 当修复、不以后缀猜 Dropbox）、恢复规则（撤 attempt 差异、生产 hash 不变）与拒绝替代论述。
2. **oracle.md（改前冻结）**：合格——五组（P1/P2/N1/N2×4/N3×3）expected 均具体到错误类别与逐根列表（如 N1 要求 company_raw / dayu_portfolio / dropbox_stock 各自 half_activated 且 NOT healthy；N2-2 写明 no_scanner_impl；N3-1 写明 readonly_with_write_target），非仅"会失败"。oracle mtime 11:38:32 早于 before 运行 11:45 与 after 运行 11:50，冻结时序成立。oracle 与 after 场景一一对应（9 case 全在 after/nine-family 中出现）。
3. **diff 范围**：合格——重算 hash：override 的 adapter_dispatch / service / models 与生产原件同 hash（无差异），实际差异仅在 config_doctor.py、config.py、scanner.py（≤卡允许的 6 文件清单）；生产原件 hash 与卡锚点/hash 全部一致（config_doctor 7351cec…、scanner f039d5f… 等）。
4. **iso venv 重跑 9 case**：全部 rc=0；与实现者存储证据逐 case 对比（剔除时间戳）：除 P1 doctor 的 dropbox 路径文案因 run 目录不同外全部 MATCH（N2×4、N3×2 完全一致；P1/P2/N1 业务字段一致）。产物齐：`effective-config.after.json`、`per-root-scan-and-resolve.json`、`config-copy-hashes.json` 均存在且内容完整。
5. **生产未触碰**：`git status --porcelain scripts/ src/company_wiki/source_catalog/` 输出为空；tests/test_config_doctor.py mtime 2026-09-01，未被本卡触碰。见"发现 3"（仓库另有本 attempt 之前的文档 dirty，与本案无关）。
6. **oracle 独立性**：未发现篡改——oracle 文本与实现消息不同源（oracle 用类名判据描述"no_adapter_but_snapshot_v2 形状描述"，实现消息措辞不同；oracle N2-2 引用现行 dispatch 消息为已登记现状而非观察结果）。expected 由 oracle 自带判据（R1–R6）手推，判据与被测函数不共享生成路径；负例覆盖完整（五变异类别不吞并、CFG-REAL half_activated 独立）。mid-run classifier 修正（N2-no_scanner_impl 与 N3-profile_mismatch 第二次运行）如实记录于 commands.json / after2/，oracle 未随后改（mtime 未变）。
7. **自评未决项**：三项均如实处理——dropbox_stock 三份样本均保持无 adapter 声明（停止规则遵守，未凭后缀映射）；test_e2e_f03 名单断言未删、未改生产测试（留待后续隔离步骤）；scanner error_details 容量 <5 说明如实记录（CFG-REAL 3<5 正常显示）。

## 五组用例 reviewer 实际复跑摘要（review_rerun/，override 副本，隔离 scratch 库实扫）

- **P1**：strategy {company_raw:adapter, dayu:adapter, dropbox_stock:legacy, future_lake:adapter}，errors=0，company_raw 1 份原件 + sidecar 为 metadata（非独立 document），与 doctor 推测一致。
- **P2**：archive_extra（陌生 root 名）零拒绝，实扫 2 份 .txt 原件；a.txt.source.json 与 c.source.json 均未成为独立 document（archive_extra locations/documents=2，无 .source.json 标题）。
- **N1**：doctor 逐根列出三根 half_activated（错误含 root 名，doctor NOT healthy）；实扫三根各自 fail-closed、类别同为 half_activated，无静默 legacy 回落，future_lake 无副作用。
- **N2×4**：unknown_adapter / no_scanner_impl / version_unsupported / unknown_profile 四类互异且稳定拒绝；N2-3 记录修改前无版本门 baseline。
- **N3×2**：readonly_with_write_target 与 half_activated(profile mismatch) 分别稳定拒绝；run 目录内无 write_target 目录产生，生产原件/配置/policy 无副作用。

## 发现（记录性，非阻断）

1. **P2 侧写子断言部分未观察到且未记偏差**：oracle 预测 "a.txt 有 sidecar → original_primary；b.txt 无 sidecar → original_primary + missing_sidecar 修复提示"。实际 `missing_sidecar` 在 P2 报告 0 次出现（a/b 均为 original_primary、无修复提示字段）；`.source.json` 排除独立原件的核心断言成立。建议后续 attempt 手动对齐步骤补一条偏差记录（oracle 子断言 vs 观测），不改判结论。
2. **两次 correction rerun 透明但 commands.json 仅记 raw_rc 数组**，argv 逐条未存全（launcher—case 映射可由 run 目录名重建）；已有 after2 专门证据目录，可接受。
3. **公司仓另有今日 11:20 的 CLAUDE.md / README.md 边界提示 dirty**（引用 I-16 卡），时间在本 attempt（11:33+）开始之前，非本卡实施者所写，也不在本卡允许触碰范围；不判入本卡，仅记录以区别于"本卡新改动为零"。`.coverage / coverage.json` 为系统原有 dirty。

## 限定申明

- 本审查不授予生产部署资格；生产 YAML / runtime policy 未改也不得改。
- 不构成对真实 Dropbox 布局的适配认证：dropbox_stock 在全部样本中无 adapter 声明，退役判断仅在本 attempt 隔离范围内成立。
- 本结论仅覆盖隔离副本（iso/override + samples 副本 + scratch 库）中的 doctor/scan 配置能力判断；不授予旧名-list 断言后续改分类的完成状态，也不构成上级完成条件（跨卡用户旅程未跑）。

## reviewer 产物（本 attempt 内，均为本轮运行生成）

- `review_rerun/`：9×case JSON + err + run 目录（reviewer 以 iso venv 独立重跑）。
- 证据来源：after/、after2/、before/、changes.diff、binding.json、commands.json、decision.md、oracle.md、iso_patching.md、handoff.json 均为实现者只读复用，reviewer 未改写。
