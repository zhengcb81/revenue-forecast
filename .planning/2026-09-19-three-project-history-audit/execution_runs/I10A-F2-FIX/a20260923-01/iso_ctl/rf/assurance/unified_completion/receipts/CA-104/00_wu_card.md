# CA-104 工作单元卡（preflight）— 命令注册与本次执行 attestation

- 领取时间：2026-08-14T02:55Z（本地）
- 唯一入口：`audit_review/README.md` §0 `current_next=CA-104`；units.CA-103.status=accepted + closure。
- 依赖：CA-102（accepted ✅）。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** P01（假绿）：命令执行的可审计性——argv/cwd/env allowlist/timeout/tier/side-effect budget 注册，结果 artifact 含 exit/业务 outcome/collected/duration/stdout-stderr hash，不可变，可重放对比。
2. **production entrypoint 是什么？** receipts 的 commands 数组（现为自由文本，99 条零输出 hash）；CI workflows。
3. **哪个 current-triplet 行为是 RED？** (a) 99 条 receipt 命令零 stdout/stderr hash——复用旧 stdout 不可检测；(b) wiki ci.yml:80 `collect_news.py --help || true`；(c) 少收集测试无 collected 计数 attestation；(d) 结构化业务失败但 process=0 会被记 pass；(e) 基建错误无分类。
4. **允许改哪些文件？** uc/commands.py、tests/test_commands.py、receipts/CA-104/**。禁止：产品代码/配置/CI/catalog/roots/旧计划（CI 的 `|| true` 修复归 CA-201，本卡只登记 finding）。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 CA-105/CA-106（依赖 CA-104）。不解决：197 场景 registry（CA-105）、oracle/ledger（CA-106）、CI 修复（CA-201）。

## 领取前机械门（弱模型清单 §2）

- [x] CA-103 accepted（机器状态）。
- [x] 三仓 HEAD：revenue=CA-103 closure 提交（领取时重读）；filing/wiki 未变。
- [x] manifest-verify 严格 OK。
- [x] 工作文件 allowlist 不重叠；locks 单 writer。
- [x] 短 ASCII 控制组：测试用 tmp_path。

## 卡片字段（runbook §4）

- **Owner repo**：revenue-forecast（控制面）。
- **Base triplet / plan hash**：见上；plan hash = CA registry `861e28f9…`。
- **Current-state drift verdict**：`still_missing`——无命令注册与结果 artifact。
- **Production callers**：before=0；after=command-run/verify/replay CLI。
- **Scenario IDs / real tier**：治理工具卡；T0 契约/变异测试。
- **RED**：见 receipts/CA-104/red/。
- **Independent oracle**：stdout/stderr hash 重算、env 脱敏、marker 解析、CAS 不可变。
- **Acceptance criteria**：result 含 exit/业务 outcome/collected/pass/fail/skip/duration/stdout-stderr hash；同命令 current code 重放差异可见；秘密值不入 receipt。
- **Stop conditions / handoff**：同 CA-001。
