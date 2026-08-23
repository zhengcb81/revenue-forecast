# ZR-1001 工作单元卡（preflight）— I 首卡：release 预备（副本完整性/容量预算/备份可读/回滚预飞/授权）

- 领取时间：2026-08-23T02:50Z（UTC）
- 唯一入口：`audit_review/README.md` §0；`current_next=ZR-1001`（ZR-907 closure → ZR-1001）；锁 ZR-1001（owner=zr1001-implementer，nonce 27bd5093…）。
- 依赖：Phase 0~9 accepted（A~H 全闭 ✅——accepted 89/117，阶段 H 6/6 全闭）。

## 领取前五问

1. **推进哪个用户目标/痛点？** 阶段 I（渐进发布）首卡——release 窗口前置条件（registry："生产副本、容量、备份可读性、回滚命令预飞；integrity/fingerprint、耗时/空间预算、用户授权；未满足不进入窗口"）。现状缺口（RED G1~G3）：无聚合的 release 就绪检查（副本 fingerprint/容量/备份/回滚/授权无统一验证）；无授权标记机制。
2. **production entrypoint 是什么？** 新 `tools/release_readiness.py`：三仓 HEAD fingerprint + catalog sqlite `PRAGMA integrity_check` + assurance/runs 容量预算（空间/耗时上限）+ 备份可读性（既有备份路径存在可读）+ 回滚命令预飞（git checkout 前 HEAD 记录/回滚步骤 dry-run 验证）+ 用户授权标记（release_authorization.json——release owner 签名确认进入窗口）。
3. **RED？** grep release_readiness/release_authorization → 零命中；无 release 就绪聚合检查。
4. **允许改哪些文件？** revenue：新 `tools/release_readiness.py`、新 `tests/test_zr1001_release_readiness.py`；receipts/ZR-1001/**、locks、state.json、README 镜像、planning docs。禁止：产品代码改动、真实 catalog/root 写、下载、LLM、真实回滚执行（dry-run/预飞验证）。
5. **下一单元解锁？** ZR-1002（Reader 先上线——company-wiki 产品切换，大卡）。本卡不做：真实切换（ZR-1002+）、legacy 删除（CA-304/ZR-1009）。

## Acceptance criteria

- **C1 副本完整性（杀 G1）**：三仓 HEAD fingerprint 一致可查（git rev-parse 三仓）+ catalog.sqlite3 `PRAGMA integrity_check` == ok（真实 catalog 只读）。
- **C2 容量/耗时预算（杀 G1）**：assurance/runs 与报告目录空间预算（上限常量）+ 全量回归耗时预算（881+106 基线 ~150s 参考值）——测试断言当前值 ≤ 预算。
- **C3 备份可读 + 回滚预飞（杀 G2）**：备份路径（assurance/backup 或既有备份位置）存在可读；回滚命令预飞：记录当前三仓 HEAD 为回滚点（rollback_manifest.json——dry-run 不执行）+ 验证回滚步骤可解析。
- **C4 用户授权（杀 G3）**：`assurance/runs/release_authorization.json` 授权标记（owner/reason/at_utc——本卡首次签发授权进入窗口；未授权时 readiness 判定 blocked）。
- **C5 质量门**：全量回归零回退（基线 881 passed + 106 subtests）、ruff clean、ratchet 绿、skill-sync MATCH、独立 reviewer 复放。产品代码零改动。

## 边界

- hermetic：真实 catalog 只读（integrity_check 只读查询）；备份/授权写入 assurance/runs/（审计输出目录）。
- 回滚"预飞"= 记录回滚点 + 验证步骤解析，不执行真实回滚。
