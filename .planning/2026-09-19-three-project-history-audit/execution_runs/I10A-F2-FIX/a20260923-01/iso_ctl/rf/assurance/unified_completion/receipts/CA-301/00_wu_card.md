# CA-301 工作单元卡（preflight）— J：clean checkout 独立复放（阶段 J 首卡）

- 领取时间：2026-08-31T16:38Z（UTC）
- 唯一入口：`audit_review/README.md` §0；`current_next=CA-301`（CA-206 closure → CA-301，DAG 解锁）；锁 CA-301（owner=ca301-implementer，nonce 973f2c56…）。
- 依赖：全部 mandatory ZR/CA 功能单元、CA-206（阶段 A~I + H CA 部分全闭 ✅）。

## 领取前五问

1. **推进哪个用户目标/痛点？** 阶段 J 首卡——clean checkout 独立复放（registry："独立 reviewer 在三个干净 checkout、精确 candidate triplet 重建环境；不复用实施者工作树/cache/未登记 fixture；T0/T1 全跑、required T2/T3/Monthly 证据新鲜；所有 receipt/hash 重算；结果与 candidate closure 一致"）。现状缺口（RED）：无复放组合验收；**188 个 receipt 中 11 个 canonical mismatch（历史短 hash triplet）**。
2. **production entrypoint 是什么？** `tools/ci_checkout_siblings`（manifest current_triplet 驱动 checkout）；`uc.envfreeze`（collect/freeze/verify：head/branch/push_state/dirty + catalog 只读指纹 + 精确相等门）；`uc receipt` canonical 算法；CA-206 soak 窗口（新鲜证据门）。
3. **RED？** glob tests/**/*ca301* → 零命中；无 triplet 可重建 + env verify + receipt 全量重算 + 状态重放组合；真实扫描发现 11 个短 hash receipt（ZR-709/802/803/804/805）。
4. **允许改哪些文件？** revenue：新 `tests/test_ca301_clean_checkout.py` + 修复 11 个历史 receipt（补全 40-hex + 重签）；receipts/CA-301/**、locks、state.json、README 镜像、planning docs。禁止：产品代码改动、真实 catalog 写、下载、LLM。
5. **下一单元解锁？** CA-302（三类真实用户旅程终验）/CA-303（架构硬编码终审，并行）。本卡不做：真实 clean checkout 复放执行（reviewer 在部署时执行）；R9 删除（CA-304）。

## Acceptance criteria

- **C1 triplet 可重建**：manifest current_triplet 三个 commit 均为有效 git 对象（cat-file -e）；ci_checkout_siblings 无浮动 main/硬编码 pin。
- **C2 env collect/verify**：uc.envfreeze.collect 对真实 trio 只读收集（head/branch/push_state）；verify 精确相等 + 字段漂移检测。
- **C3 receipt/hash 全量重算**：全部 188 个 11/12 receipts canonical hash 从 payload 重算一致（**发现并修复 11 个历史短 hash triplet 缺陷**）；state.json sha256 确定性。
- **C4 重放一致**：状态重放（只读）复现 candidate closure（current_next 在位 + accepted ≥100 + 每 accepted 单元有 implementer/reviewer）。
- **C5 新鲜证据门**：required T2/T3/Monthly 证据按可信时间戳判定（CA-206 soak 语义）——陈旧证据保持 pending。
- **C6 质量门（卡级）**：相邻回归（envfreeze 13 + CA-206 13）零回退、revenue 全量零回归（基线 973+106）、ruff clean、独立 reviewer 复放。产品代码零改动。

## 边界

- 只读 + tmp 隔离；零网络（remote_lookup 离线注入）、零下载、零 LLM；真实 clean checkout 复放为部署/reviewer 动作（本卡验收机制）。
