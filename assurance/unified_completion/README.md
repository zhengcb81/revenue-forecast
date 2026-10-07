# unified_completion — 统一完成保障控制区（CA-001 bootstrap）

唯一执行入口仍为 `audit_review/README.md`；本目录是它要求的机器状态、锁、
receipt 与离线重验工具的实现所在。**本 README 不构成第二个任务入口。**

## 布局

```text
assurance/unified_completion/
  uc/            控制工具包（casfile / lock / manifest / state / control / dag / cli）
  tests/         51 个测试（含 10 轮跨进程并发 mutation）
  manifests/     plan_inputs.json（44 个冻结输入的机器清单）
  state.json     机器状态真源（schema v1；CA-101/102 将版本化）
  locks/         单 writer/TTL/CAS 锁（按需创建）
  receipts/      CA-001 的 preflight/RED/implementer/reviewer/closure receipts
```

## 用法（仓库根，PYTHONPATH=assurance/unified_completion）

```text
python -m uc.cli manifest-verify          # 离线重验全部冻结输入（默认校验 hash+size；mtime 只作诊断）
python -m uc.cli manifest-verify --mtime strict # 显式检查历史文件时间（可选）
python -m uc.cli lock-acquire|status|release --resource <r> --owner <o>
python -m uc.cli state-show | next
python -m uc.cli state-update --unit CA-001 --status accepted --reviewer <id>
python -m uc.cli closure-advance --next CA-002 --phase <p> --owner <o> --reviewer <id>
```

## 干净 checkout 复核流程（reviewer 必读）

1. `git -c core.autocrlf=false clone <repo> <clone>`（避免 CRLF 转换破坏冻结字节）。
2. 冻结输入尚未全部提交（历史证据 + 计划程序的脏工作树）：
   `Remove-Item <clone>\audit_review -Recurse -Force` 后
   `Copy-Item -Recurse -Force <repo>\audit_review <clone>`（Copy-Item 保留 mtime）。
3. `manifest-verify --mtime off`（hash+size 强制；git checkout 无法复现 mtime）。
   mtime drift 属预期，只作诊断；hash/size drift 仍然失败。
4. 锁/状态变更命令与 `closure-advance` 在重放时加 `--mtime off`；
   真实控制面默认也按 hash+size 校验，不以 checkout 时间判定内容是否一致。

## 已知缺口（successor：CA-002/CA-004）

- 冻结输入未全部提交（README 与 2026-08-13 计划目录未跟踪；部分旧 FCAP 文件工作树≠提交内容）。
- git checkout 无法复现冻结 mtime（默认只报告诊断，不阻断）。
- 历史 legacy receipt/closure 工具（tools/closure_gate.py 等）无锁无 CAS，由 CA-109 隔离。
