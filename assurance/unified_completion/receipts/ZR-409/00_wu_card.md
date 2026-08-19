# ZR-409 工作单元卡（preflight）— 配置新增 future_lake + 三真实 root 用户旅程（阶段 D 出口）

- 领取时间：2026-08-19T18:56Z（UTC）
- 唯一入口：`audit_review/README.md` §0 与机器状态；`current_next=ZR-409`，ZR-408 accepted + closure→ZR-409；锁 ZR-409（owner=zr409-implementer，nonce 1b13251e…）。
- 依赖：ZR-401~408 全部 accepted ✅（阶段 D 前置全闭）。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** 阶段 D 出口（exec plan §6.9）："fourth-root 只改配置/adapter fixture、产品 core diff=0"。EX-08（新 future_lake root + sidecar adapter 仅改配置即可复用，证明真正泛化）已在合成目录由 test_future_root_config_only/ZR-403 矩阵证明；本卡把它落到**生产配置**，并以**三真实 root 只读用户旅程**（companies 紫金 / dayu-only 1548 / Dropbox 星环）证明任一 policy 允许 root 从 resolver 旅程成功。
2. **production entrypoint 是什么？** `company-wiki/config/source_catalog.yaml`（生产配置，现 3 根 p10/20/30）+ 只读旅程：wiki CLI `resolve`（读模式，真实 catalog）对三真实样本 exact 复用；EX/LT/DL/IDX/UJ 场景由既有验收套件承担（scenario→test 映射钉死）。
3. **哪个 current-triplet 行为是 RED？**
   - **G1**：生产配置无 future_lake（第四根缺失）——policy-export 输出 3 根；添加后必须仅凭配置即可被 loader/scan/policy-export/resolver 接受（产品零改动）。
   - **G2**：三真实 root 旅程无生产级只读验证记录——dayu-only 样本（HK 1548/2021/pdoc 10225111/hkexnews，内容 72b3ed25… companies 无同 hash）与 Dropbox 样本（CN 688031/2024/pdoc 1223325316/cninfo，星环 2024 年报）从未以 resolve exact 旅程验证（handle 经 policy、download=0、不复制到 companies、外部 root 零写）。
   - **G3**：EX/LT/DL/IDX/UJ 场景→测试映射无统一钉死（各场景散落在 ZR-206/301~408 各套件；需一张映射表 + 复跑证明全绿）。
   - 既有已钉死（不重复）：EX-01~07/DBX/DL/LT/IDX 各族已由 FC-603/604、ZR-402/403/405/406/407/408、FC-801/804、test_future_root_config_only（EX-08 合成版）覆盖。
4. **允许改哪些文件？** company-wiki `config/source_catalog.yaml`（新增 future_lake 根：directory + sidecar_filing_v1 + reusable，p40）+ `future_lake/`（仓库内 fixture 目录，adapter fixture——README 占位）；新测试 `tests/contract/test_zr409_fourth_root_real_journeys.py`（真实根只读旅程：resolve 三样本断言 + 生产配置四根加载/policy-export 断言 + 根指纹只读断言）。禁止：产品 src 改动（core diff=0）、真实 catalog 写、下载、外部 root 写。
5. **下一单元解锁条件？本单元不解决什么？** ZR-409 accepted = **阶段 D 出口** → 阶段 E（ZR-501~510）。本卡不做：生产 config.py 切换 3.0 loader（**ZR401-REV-003 显式再延期**：那是产品代码变更，违反本卡 core-diff=0 约束；移交阶段 I/CA-303 记录）、真实下载（DL-04~06 留 ZR-802/806 T3）、ProcessingDemand（ZR-507）。

## 领取前机械门（弱模型清单 §2）

- [x] ZR-408 accepted（closure.next=ZR-409）。
- [x] triplet 冻结：revenue `de4430b…`、wiki `71aa798…`、filing `5a1c18f…`。
- [x] 现状事实：生产 config 3 根（company_raw p10/dayu p20/dropbox p30，reusable_root_kinds 全三 kind）；真实样本已核（dayu-only 1548/2021 内容 72b3ed25… 无 companies 同 hash；Dropbox 688031/2024 星环年报带完整 sidecar 身份；紫金 601899/2025 pdoc 1225023658）；EX-08 合成证据已在（test_future_root_config_only 5 tests）；dayu-only 样本选择符合 exec plan §6 T2 要求（dayu 独有，非 companies 副本冒充）。

## 卡片字段（runbook §4）

- **Owner repo**：company-wiki（生产配置 + fixture + 只读旅程测试）+ revenue（receipt）。
- **Current-state drift verdict**：`still_missing`——G1~G3。
- **Acceptance criteria**：
  - **C1 第四根仅配置（杀 G1）**：生产 config 新增 `future_lake`（kind directory、adapter sidecar_filing_v1、reusable、p40、path ${PROJECT_ROOT}/future_lake）→ loader 接受、policy-export 输出 4 根（含 future_lake reusable=true）、scan 不因该根报错（空/fixture 根）、resolve 路由不受影响；**产品 src diff=0**（`git diff -- src/` 为空）。
  - **C2 三真实 root 只读旅程（杀 G2）**：对生产 catalog 以 read-only resolve 验证三样本 exact 复用——(a) companies 紫金 601899/2025/pdoc 1225023658 → canonical 在 companies；(b) dayu-only HK 1548/2021/pdoc 10225111 → REUSED_EXACT、canonical 在 dayu portfolio、内容未复制到 companies；(c) Dropbox CN 688031/2024/pdoc 1223325316 → canonical 在 Dropbox root。全部 download_events=0；旅程前后真实三根+catalog 指纹不变（零写断言）。
  - **C3 场景映射全绿（杀 G3）**：EX/LT/DL/IDX/UJ 场景→验收测试映射表（写进 receipt）+ 复跑映射套件全绿（EX-01~08、LT-01~10、DL-01~03/07~10、IDX-01~08、UJ-01/02/04/06/07 中已实现的 T1/T2 项；DL-04~06/UJ-03/05/08 等 T3 项标注移交 ZR-802/806）。
  - 质量门：wiki unit 787 + 受影响 contract 全绿；ruff clean；产品 src 零改动；独立 reviewer 复放。
- **Stop conditions / handoff**：需要改产品 src、真实 catalog 写、下载、外部 root 写 → 立即停止。

## Annex：三真实样本与场景映射

| 旅程 | 样本 | 身份 | 断言 |
|---|---|---|---|
| companies | 紫金矿业 2025 年报 | CN/601899/pdoc 1225023658/cninfo | REUSED_EXACT、canonical∈companies、dl=0 |
| dayu-only | 1548（HK）2021 年报 | HK/1548/pdoc 10225111/hkexnews | REUSED_EXACT、canonical∈portfolio、companies 无新增、dl=0 |
| Dropbox | 星环科技 2024 年报 | CN/688031/pdoc 1223325316/cninfo | REUSED_EXACT、canonical∈Dropbox、dl=0 |
