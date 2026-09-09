# GP-008/009 部署脚本：注册 Windows 定时任务

> **2026-09-07优先状态**：本组下方9/6覆盖后又有其他任务推进。revenue HEAD=6682ecf，latest daily=20260906T210001Z/ok=false/空triplet；DEFAULT_PERIODS改为wiki账本，旧revenue green不代表当前资格。Git确认R9 revenue批1+2工具/测试及CI step已删，wiki批3日志记录延后；不重复执行、不在此追认其全量验收。当前差异见[状态覆盖](../../../../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/current-delta-2026-09-07.md)，整改以同目录执行手册为编排依据。CI协议是现有WP11输入，旧命令/批准不是本轮push、真实测试、网络、任务或删除授权。保留下方原日志及批准字节。

> [当前状态总入口](../../../PLANNING_STATUS.md)

> **2026-09-09 状态修正**：GP-006（real-roots 阻断且绿）、GP-008（自然触发闭环）、GP-010（sections 7/7）、N-1/FC-150x、CI 协议两项已关闭；GP-009 monthly 1/1、drill 1/1、daily 3/7、weekly 0/2 自然累积中；FC-705 仍关（P7 窗口差 19 秒）。当前逐项结案与证据见 [gp_tail_closure_2026-09-08.md](gp_tail_closure_2026-09-08.md)。

## 2026-09-06 最新状态与领取规则（优先于下方全部旧覆盖/命令/批准摘要）

2026-09-08规划覆盖：用户只批准planning调整，不授权实施、重新注册、删除或运行。原痛点审计继续保留，活动整改使用[R4虚拟数据湖计划](../../../../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/simplified-execution-plan.md)及其测试矩阵/旧WP迁移表。A/B本地读取、C生产、D运维、M收入按实际依赖推进，不再叠加旧15包95门。本组只作历史执行/批准来源，不并行领取第二套队列，不把旧批准扩大为新动作许可。

- GP-008参数错误已在revenue HEAD `2ff20d9`修复，注册器现为`run-daily`。旧“代码仍阻塞/必须先改拼写”失效；部署Action及自然触发仍未独立闭环，不自动重注册。
- latest观测daily manifest=`20260905T194055Z`、period=2、ok=true，绑定旧`2cbd585`而非当前HEAD；legacy一个ended_at完成窗口、第二个未完成，close_allowed=false。旧9/3唯一run/零completed不再是最新状态，仍不可按预计日期放行。
- GP-010观测为normalized7/7、review7/7、summary6/7、sections5/7，安全拒绝保留，列表式缺口未闭。kind宽范围历史产物214份与精确7份cohort不是同一范围；按owner已有处置保留，不执行旧“DELETE+重扫即无外部副作用”的回滚说法。
- 117 accepted/197 passed不是原目标完成证明：9/6审计找到required tier、真实消费、业务计算、失败账本和发布等实质反例。历史receipt/批准原字节不改，禁止批量重签来制造当前资格。
- 新H01自动prune归档覆盖风险是worker恢复前置。当前整改全部NOT_IMPLEMENTATION_AUTHORIZED；旧授权不自动包含新scope/新版本。GP/R9历史批准保留，但继续执行需WP01/12/13/14相应门、真实数据E2E和当前精确授权。

以下9/2–9/5内容均为有日期的历史快照，不是新的可执行指令；若与本节冲突按本节及新计划处理。真实报告、完整观察、受控删除未完成，不以文档同步勾成完成。

## 2026-09-05 阻塞警示（覆盖下文旧“无需重注册”及22:00修复记录）

请勿直接按旧说明重注册或启动任务。当前HEAD虽已修电源条件、StartWhenAvailable并把触发改为22:00，但注册器仍生成--run-daily，parser只接受子命令run-daily；安全解析探针仍失败。必须先完成另行授权的代码修复，并核对既有task实际Action。若修改注册Action而非增加CLI兼容，既有任务也要受控更新；不能笼统声称“代码落盘即生效”。

owner的9/5提权诊断记录证明旧任务曾因错过开机时刻/电源条件失败，并记录已重注册22:00；但重注册后的Action文本与成功自然触发仍缺独立复核。weekly源码生成run-weekly，未见同类拼写缺陷。

唯一已见daily记录是9/3手动run 20260903T211059Z/period1；零个completed窗口。等待真实7/2/1/1审核和两个≥24h零hit窗口，不保证日历日期。

以下命令仅作修复并获授权后的参考，不由本次文档同步执行。手动run使用默认catalog（company-wiki/.source_catalog/catalog.sqlite3），不要指向revenue仓内不存在的catalog。

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
  --catalog ..\company-wiki\.source_catalog\catalog.sqlite3 `
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
| revenue_daily_t2 | 每日 | 22:00 | T2 只读验证，写 daily_manifest.json |
| revenue_weekly_t3 | 每周 | 周日 04:30 | T3 真实下载验证，写 weekly_manifest.json |

> **2026-09-03 修复注记（revenue 3552795）**：daily 任务注册动作只带裸
> `--run-daily`，而 run-daily 的 --catalog/--manifest/--report-root 原为
> required——SYSTEM 03:30 触发必 argparse 失败（exit=2），daily_manifest
> 永远不写、观测窗口永远不累积。修复后三参数默认生产路径（catalog=
> company-wiki/.source_catalog/catalog.sqlite3、manifest=compatibility/
> current.json、report-root=assurance/runs）。任务 action 指向脚本路径，
> **已注册任务无需重注册**，代码落盘即生效。
>
> **2026-09-04 重注册记录**：09-04 03:30 调度实测未触发（daily_manifest
> 停留在 09-03 21:11 手动 run1；无 alert 文件）→ owner 于管理员会话重新
> 执行 register（daily + weekly），确认 registered。窗口时间线随之修正：
> run2 09-05 03:30 → run3 09-06 → run4 09-07 → gate 最早 ~09-07 03:30 后
> （详见 progress.md / n1_r9_removal_request.md §5）。09-04 另完成 weekly
> T3 首跑预检（测试文件在位、FILING_FETCH_E2E_DOWNLOAD 门名一致、4 测试
> 可收集——周日 04:30 首跑风险已降低）。

## 观测目标（GP-008）

注册后开始累积观测：
- 连续 2 个 ≥24h 零 `legacy_bridge_hits` 窗口 → CA-304 可执行删除
- 本计划只建立观测起点，不执行删除

## 自然时间目标（GP-009）

注册后开始累积：
- 7 Daily + 2 Weekly + 1 Monthly + 1 alert drill 完成后回填 closure ledger
- 本计划只注册调度起点，不等自然时间
