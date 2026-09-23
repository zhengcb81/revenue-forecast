# recovery/README.md — exact revert for FIX-W06-GAPS/a20260922-01

本卡全部改动 = 「在副本上修 + 两个产品测试文件」。**生产源码（revenue-forecast `scripts/`、
company-wiki `src/`）零字节改动**（binding.json `product_source_integrity` 全绿为证），
I-06-A 原始 attempt 零改动。恢复 = 把 `before/` 原件拷回去：

## 1. 产品测试面（唯一被写入的生产树文件）

```powershell
$A = "...\execution_runs\FIX-W06-GAPS\a20260922-01"
# 1a. 还原被收紧的既有测试（before/ 中为逐字节原件，sha256 见 before/MANIFEST.json）
Copy-Item -Force "$A\before\rf\test_fc905b_trusted_receipt.py" `
  "C:\Users\郑曾波\Projects\revenue-forecast\tests\test_fc905b_trusted_receipt.py"
# 1b. 删除新增测试
Remove-Item "C:\Users\郑曾波\Projects\revenue-forecast\tests\test_message_contract_pins.py"
```

校验：`test_fc905b_trusted_receipt.py` 恢复后 sha256 =
`e5c965e5bfea67593772555d12ef68a325206e2559018b3333dbe715478b9684`（见
`before/MANIFEST.json`）。

## 2. 副本面（attempt 目录内，无需恢复即无产品影响）

iso/ 下全部为修复副本；若要回到「仅原件」状态：删除 `iso/` 与 `scripts/` 即可
（`before/` 保留原件；`evidence/`、`changes.diff`、`binding.json`、`decision.md`、
`handoff.json` 为审计记录，**保留、不改写**——no historical rewrites）。

## 3. 不可逆性说明

- 没有 git 写入、没有数据库/状态文件遗留在产品树（全部 sqlite 副作用发生在 `%TEMP%\fix-w06-gaps\`）。
- product tests 运行产生的 `__pycache__` 已用 `-B`/`PYTHONDONTWRITEBYTECODE=1` 抑制。
- 若 company-wiki hunks（changes.diff `repo:company-wiki` 段，PROPOSED ONLY）将来被审查者应用到
  产品源，应用本身另立卡记录；本 attempt 未应用。
