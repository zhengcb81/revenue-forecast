# F4 · RF 普通入口失败的冷读回执

本仓源码 `d1672f5a24c7b66639b2480bdce4ce16ce7008da`。基于远端 `f90d28ad4d240e507d3867f71e09fbf012a881b0` 在独立克隆完成。[本仓 F4 计划](feedback-20261117.md)继续维护宿主和运行范围。

## 原因与修复

用已安装的预测入口提交损坏的本地 JSON，真实进程退出 2。普通出站包保留 `JSONDecodeError` 和原运行身份，另一进程通过 `rf_job_feedback.py reconcile` 能找到原异常，却缺少总控使用的 `job_status` 和 `cost_state`。来源校验失败后原子进程退出 3 的真实场景也漏这两个字段。此缺口位于 RF 回执投影。

按原本仓 `rf-cli/1` 回执核对运行、尝试与步骤。只有原生回执保存了非零整数退出，才返回 `job_status=failed`。当原记录明确表明未派发时，返回 `cost_state=not_applicable`。其余费用保留 `unknown`，没有凭据就不报零。缺原回执、错绑或不具备可确认退出证据时仍为 `unknown`。原生错误码、原副作用状态和引用一并保留。公开读口不重新启动原操作，持久作业继续使用自身状态和用量收据。

## 测试与独立审查

- 两条真实公开 CLI 回归先红，均因缺两个字段。修复后从新进程读回同一拒绝和来源子进程失败。来源作业保持一次来源尝试、计算和发布零尝试，历史费用仍未知。重复查证未执行新业务。
- 邻近旧测试依赖整个 `observations` 字典相等。在干净基线独立复现，`failure_reason=upstream` 是现行合法失败证据。改为精确断言原下载数 0、采集调用数 2、原失败原因 `upstream`。本次未改该业务生产者。
- Windows 3.13 最终定向 35 项通过，21.70 秒。最初扩大测试中有一次临时根的原子写入 `WinError 5`。干净基线同例通过，标准宿主定向复跑恢复包 10 项通过，最终 35 项包含该例。未调整原子写入或降低断言。
- 独立 agent 对最终源码复跑候选核心 6 项和作业合同 8 项。另用独立的真实入口验证冷读两次、错绑、缺原回执和无法确认的退出。原观察与 SQLite 证据 SHA 一致，恢复触发的新业务和费用均为零。Ruff、mypy、Git 提交钩子通过。所有测试使用隔离路径和本地替身。

定向测试命令

```powershell
python -B -X utf8 -m pytest -q -p no:cacheprovider tests/test_f4_failure_coverage.py tests/test_rf_job_facade_cli.py tests/test_rf_job_recovery.py tests/test_rf_job_status_contract.py tests/test_rf_job_concurrency.py
```

## 部署交接

正式总控仍调用 RF 固定发布检出下的 `scripts/rf_job_feedback.py`，已安装预测入口继续调用已有日志生产者，不需要另装读口。仅由总控推进发布检出并用实际安装入口复验；并行 RF 主工区和统一设置不纳入本仓补修。收件确认由总控负责，业务终态与实际费用是独立事实。

## 远端完整 CI 夹具修复

首次发版 `597c6bc2` 和其父版 `f90d28ad` 均在远端完整来源与预测检查失败。Ubuntu 3.12 在 `f90d28ad` 的干净归档复现 `test_catalog_write_failure_preserves_previous_publication_and_retries_once` 未触发异常。共享原子 writer 从 `f7c7c45f` 起使用较短的 `.rf-*.tmp`，旧测试仍按旧目录索引文件名前缀匹配，未执行约定的 13 字节半写中断。[本次远端故障](https://github.com/zhengcb81/revenue-forecast/actions/runs/45283601584/job/138074080032) · [父版远端故障](https://github.com/zhengcb81/revenue-forecast/actions/runs/44927702861)

夹具以目标目录的实际文件系统身份及独占写入匹配同一原子路径。原目录索引字节、真实半写和退出、单次重试、失败的暂存件清理均有断言。独立代理核对三次真实暂存写入，只有初次成功和重试进入替换。Windows 邻近两项通过；在同一 Ubuntu 原始归档仅替换测试夹具即可由红转绿。

按 GitHub 配置创建独立 Ubuntu Python 3.12 环境，运行 `python -B tools/pre_push_gate.py --ci`。Ruff、16 个公开类型文件通过，行为检查 **766 passed、46 subtests passed**，38.85 秒。例行提交检查负责静态扫描，推前原有 12 项固定冒烟，完整目录写入故障由远端 CI 执行。现有检查职责和生产代码均保持不变。
