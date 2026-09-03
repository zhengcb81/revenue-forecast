# GP-008/009 部署脚本：注册 Windows 定时任务

> **需要管理员权限运行**。本脚本只注册任务，不执行删除。
> 运行前请确认 Python 路径和项目路径正确。

## 前置条件

- Windows 10/11 with Task Scheduler
- Python 3.12+ 在 PATH 中
- revenue-forecast 项目在 `C:\Users\郑曾波\Projects\revenue-forecast`

## 注册命令

以管理员身份打开 PowerShell，运行：

```powershell
# GP-008: 每日 T2 运行（legacy deletion observation）
cd C:\Users\郑曾波\Projects\revenue-forecast
python tools\daily_t2_schedule.py register

# GP-009: 每周 T3 运行（real download assurance）
python tools\weekly_t3_schedule.py register
```

## 验证

```powershell
# 检查任务状态
python tools\daily_t2_schedule.py query
python tools\weekly_t3_schedule.py query

# 运行一次手动验证（可选）
python tools\daily_t2_schedule.py run-daily `
  --catalog .source_catalog\catalog.sqlite3 `
  --manifest compatibility\current.json `
  --report-root assurance\runs
```

## 取消注册

```powershell
python tools\daily_t2_schedule.py unregister
python tools\weekly_t3_schedule.py unregister
```

## 任务详情

| 任务 | 频率 | 时间 | 说明 |
|---|---|---|---|
| revenue_daily_t2 | 每日 | 03:30 | T2 只读验证，写 daily_manifest.json |
| revenue_weekly_t3 | 每周 | 周日 04:30 | T3 真实下载验证，写 weekly_manifest.json |

> **2026-09-03 修复注记（revenue 3552795）**：daily 任务注册动作只带裸
> `--run-daily`，而 run-daily 的 --catalog/--manifest/--report-root 原为
> required——SYSTEM 03:30 触发必 argparse 失败（exit=2），daily_manifest
> 永远不写、观测窗口永远不累积。修复后三参数默认生产路径（catalog=
> company-wiki/.source_catalog/catalog.sqlite3、manifest=compatibility/
> current.json、report-root=assurance/runs）。任务 action 指向脚本路径，
> **已注册任务无需重注册**，代码落盘即生效。

## 观测目标（GP-008）

注册后开始累积观测：
- 连续 2 个 ≥24h 零 `legacy_bridge_hits` 窗口 → CA-304 可执行删除
- 本计划只建立观测起点，不执行删除

## 自然时间目标（GP-009）

注册后开始累积：
- 7 Daily + 2 Weekly + 1 Monthly + 1 alert drill 完成后回填 closure ledger
- 本计划只注册调度起点，不等自然时间
