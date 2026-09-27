# BOOKKEEP-REPAIR / a20260923-01 — oracle.md（修复清单冻结；先于任何修复写入）

- CARD: **BOOKKEEP-REPAIR**（记录级修复，零产品代码）— 关闭 AUDIT-DESIGN / AUDIT-GOAL / AUDIT-INTEGRITY 报出的簿记偏差。
- PLAN = `C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit`
- ATTEMPT = `execution_runs\BOOKKEEP-REPAIR\a20260923-01`
- 派单：父 agent（`session-bfecd191-fbc3-4a66-8ed1-6562479bf102`），原 9 项 + 扩容 5 项（#10–14）+ 2 项（#15–16）+ BL-2/#18（#17–18）+ 2 项（#19–20）= **20 项**。
- 冻结时点：2026-09-23（本文件写入后不再修改；如需更正走 append-only 勘误）。
- 通则：**append-style + 原值留痕**（凡改写处原值逐字保留于 `*_historical` 字段/兄弟件）；execution_v2 冻结件、reviewer 报告/载体**字节不动**；不写产品代码；不跑 git 状态变更命令；严格增量。

## 0. 前像锚点（before-state，sha256 全值 / bytes；测量于任何修复写入之前）

| 文件 | sha256（before） | bytes |
|---|---|---|
| `task_plan.md` | `4096a44d69061cef60a61c2479ccebeabc3d4c24faea0e0d36b72c001bc687bf` | 251126 |
| `findings.md` | `23440bafc93e8b719626368dde973b828d62d960a6807a14c8d538a4127f4591` | 90521 |
| `progress.md` | `eaecac7876b423a0340ac494d2aab6f46eba6873e74571b329342331299e3e87` | 198604 |
| `REMEDIATION_REGISTER.md`（不改，仅产 fold 块） | `3a23fc993af76d0dd76f5326c53687aa4d6cd0e99c0711ad43cdecf56b0a7864` | 188440 |
| `README.md`（无引用命中，不动） | `4ee64e33238532b9f5b882e5fa7a7d2241e995f25f1f2e48646e76c0e6717850` | 6955 |
| `outward_requests\_provenance.json` | `90ac345328871dfc6c147c87b28710a14bad4f6655b36090c0651120af94c1ac` | 8578 |
| `execution_runs\I-14-F-R1\a20260922-01\review.md` | `7f1808993e4e30884aeca26ad14d5ce2ac149e77e452646ed5a64a53e48a8a83` | 6029 |
| `execution_runs\B1-I08C-product-fixes\a20260921-01\handoff.json` | `c5696e780a9470cf22dd41333e05c24a82783080b7fd006862e181c25e624259` | 26788 |
| `execution_runs\B1-I08C-product-fixes\a20260921-01\reviewer_report.md`（冻结载体） | `6bfd2922cdf3418416731e62098567d20ab1dcdc98429d8cc1e899e721e7951b` | 37224 |
| `execution_runs\I-14-D\a20260919-01\reviewer_report_r2.md`（冻结载体） | `58f92dd7e3a3f66639dbdab4743455a878c4122500ac2d8d132e2eae2bee6c2c` | 39824 |
| `…\reviewer_report_r3.md`（冻结载体） | `c617c43a7f674b6b9098a252c10aa354f3634d4c345aa5133d75287e26aa003b` | 44008 |
| `…\reviewer_report_r4.md`（冻结载体） | `f27a85a51596075b795d885a5ca5120bcd4ccbf057ce9c3d9f9075ff9d294bc6` | 51860 |
| `…\reviewer_report_r5.md`（冻结载体） | `9f8fdba98c473ec9510d53e4a605fba4072cf8e276485c5c091f83e7683311d5` | 49279 |
| `execution_runs\B5-plan-level-remediation\a20260921-01\binding.json`（不动，仅勘误） | `96733875e7556f0606220bda8ea1fbaea7d462f66b392132538dafc8c53d499a` | 22652 |
| `execution_runs\B5-plan-level-remediation\a20260921-01\handoff.json`（不动） | `ca69b8f46d275fdb3509d26a49b42585a7825d24723fd5fd97f98bcd7da17de3` | 31133 |
| `execution_runs\B5-fix-g1a-g3\a20260922-01\binding.json`（不动） | `c6ef61034a0c2f0382bdb6de6901df8a805cbd25c4eb78e959eea5accc56136` | 12490 |
| `execution_runs\I-05-C\a20260919-01\handoff.json`（不动，仅勘误注记于 _provenance） | `7c4f4719a19150dd5aba63f82d62c94dc6af0a999fc8b8ba43fa6a1411823778` | 11226 |
| `execution_runs\PROMOTION-EXEC\a20260922-01\binding.json`（不动，仅注记） | `2626314d8830835fae8b2b7024bd1474aa3a8dba6ecd7c361762a0af18a7b103` | 9657 |
| `execution_runs\I-14-F-R1\a20260922-01\reviewer_report.md`（冻结载体） | `8ce87ef6d31087da65e556be4736a8c8f7734594575cf868149df383e5f62a1c` | 15841 |
| `execution_runs\I-06-A|I-06-B\a20260919-01\rulings_transcribed_2026-09-22.md`（双卡同字节，冻结） | `5ef8d863e3656962836f83eee4ddd87e8712b174491715cbd856b8593fcb8d91` | 139717 |

REM-79 checker **before-run**（v1.2.0-correction2，PWF 三文档）：rc=1，**4 violations**（task_plan.md:1630[全部]、findings.md:633[all]、findings.md:684[none]、progress.md:1060[全部]）——存证 `evidence/rem79_before.{txt,json}`。

## 1. 修复项 × 期望 after-state（冻结判据）

| # | 项 | 修复动作（写面） | 期望 after-state |
|---|---|---|---|
| 1 | PWF 同步缺口（GOAL ⑤） | `findings.md` 尾部追加 2026-09-23 节：I-07-C 条（含 holdout 双结果）+ I-09-C 条；`task_plan.md` 尾部追加 2026-09-23 节：DW15-prune-repair（正名）+ I-07-C 卡号 | 两文件仅尾部新增；既有行 0 改动；四卡号/正名在 PWF 可检索 |
| 2 | REM-79 四行补域（REM-94） | 四行行内追加域限定（计数式，逐行真于内容） | checker 对 PWF 三文档 rc=0 |
| 18 | progress.md:1060 计数限定（INTEGRITY F7） | 并入 #2：限定词带实数计数（N=4） | 同上 |
| 3 | I-14-F-R1 review.md stub 双口径（D4） | 落地式 review.md 翻转：status→`accepted_scoped` + status_authority 转录块 + `verdict_is_transcribed_not_authored:true` + reviewer_report sha 钉；**原 stub+原 09-22 landing 块逐字保留**于 `review_stanb_stub_historical` / `carrier_landing_20260922_historical` 字段 | 首行 status=accepted_scoped；stub 全文在内；reviewer_report.md 字节不动 |
| 4 | B1-I08C review.md 槽（D4） | 新建 landing 式 review.md，转录 `accepted_with_conditions` 裁决（reviewer_report.md sha 钉）+ 词汇映射注记 | review.md 存在；映射注记「accepted_with_conditions ≡ accepted_scoped 带遗留件」在内 |
| 7 | B1 原卡回填（DEV-2.2） | 同 attempt（#4 收敛）：handoff.json `status: review_pending→accepted_with_conditions`（映射≡accepted_scoped+carried_findings）+ `status_before_bookkeeping_fix` 等留痕字段 | handoff 状态回填；原值留痕字段在 |
| 5 | 验收词词汇映射（D4 全局） | decision.md 映射表（8 处超界 + 自查补全形）+ register `## 七十七` fold 块 | 映射表含 ACCEPT≡accepted_scoped 等全映射 |
| 6 | I-14-D r2-r5 无 pin（GOAL ⑤） | `<ATTEMPT>/i14d_report_pins.json`：四报告 sha256/bytes 实测钉，post-hoc 披露 | 清单 4 行全值；retro-pin 声明在 |
| 8 | D8 提交信息欠复述 | decision.md 注记 + fold 块（commit 不可变，注记式） | 注记含 C12/F-REV-D-02/F-REV-D-03 三欠账 |
| 9 | 「注册时点版本」限定（FAB-1 残留） | register 引用行（1449/1483/1501/1541/1563）行内追加 **(sha256,版本域,留存位) 三元组**注记；RESPONSES.md 已有勘误=不动 | 五引用行均带三元组 |
| 10 | B5 binding 失配（D7） | B5-fix attempt 新建 `binding_erratum_20260923.md`（不动原 binding） | 两哈希全值+现值复算+归因+原值留痕声明 |
| 11 | _provenance.json:75 陈旧字节（D12） | 尾部追加 `errata_2026_09_23` 键（原行不改） | 现值 11226 B/sha 入注 |
| 12 | 批 8/9 门记录（DEV-2.1） | decision.md 附 register 形式正式门记录行 ×2（对齐批 1-3 行式）+ fold 块 | 两行含 10/10 门绿+push log 时点 |
| 13 | D6 冻结次序注记 | decision.md 准文（供 RF-RATCHET-FIX/REST-A review 引用）——不动两卡 | 准文含「冻结次序偏差=补偿核已做」 |
| 14 | D10 意外真实下载 | decision.md 一行（引用 `E2E-EXPAND/a20260923-01/evidence/accidental_auto_gate_run/`）| 含已披露+删除证明+不追认 |
| 15 | D1b 证据件缺失（最高项） | B1-I08C attempt 新建 `evidence_erratum_20260923.md`；**严禁创建 production_anchors.txt** | 勘误声明「未产出/登记时点即缺/不事后补件」+ 实测搜证 |
| 16 | D1c 族（4 小项） | decision.md「D1c 族注记表」4 行 + fold 块 | 各行含原自陈位置引文 |
| 17 | BL-2 bind-time 钉漂移（INTEGRITY） | decision.md 一行 + 三元组格式提示 | 302bd10b…vs fdc75e0a…非断链定性 |
| 19 | B5 harness 可重定位性（事故根因） | B5-fix attempt 新建 `harness_relocatability_erratum.md` + `scripts_fixed/`（两脚本修复版副本，输出可重定位；**原脚本不动**）| 修复版可用 args/env 指向新 attempt |
| 20 | I-06-B 历史破门注记 | decision.md 三行（历史例外已披露/现行链以 a20260922-02 为准/不可回改历史）+ fold 引用 | 三行齐 |

## 2. 交付面（nine-step，record-repair 形）

oracle.md（本件）/ binding.json（全部触碰件 before/after sha）/ commands.json（含 REM-79 before/after 跑）/ decision.md（逐项映射+原值留痕证明+fold 块）/ changes.diff（记录修的可读差分，binding 表为准）/ handoff.json（review_pending/unsigned/unmapped/unproven）/ evidence/（REM-79 前后输出、i14d pins、sha 表）/ recovery.md（精确 before 钉还原法）。

## 3. 明令禁止（负清单）

1. 不创建 `before/production_anchors.txt`（D1b 铁律）。
2. 不改任何 reviewer_report*.md、reviewer_report*.sha256、execution_v2\**、RESPONSES.md、rulings_transcribed*.md、三 T2 ruling.md、B5 原/fix 的 binding.json/既有证据。
3. 不改 PWF 三文档既有行（仅行内 #2 限定追加 + 尾部追加节）。
4. 不跑 git 写命令；不写产品树（revenue-forecast / company-wiki / filing-fetch）。
5. 不自签任何验收：本 attempt 终态 `review_pending`，`implementer_signed=false`。
