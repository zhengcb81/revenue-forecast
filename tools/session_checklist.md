# 会话收尾检查单（R4.3 简化版）

按“相关责任 / 大节点”收尾。**不要求**每个会话跑完整仓内 pytest、真实跨仓
E2E、安装副本全 MATCH、重跑历史 197 场景，或把用户配置 checkout 回 HEAD。
日常短责任只有一个入口：`python -B tools/pre_push_gate.py`
（`.github/workflows/quality.yml` 跑的同一条命令）。

## 责任边界

- [ ] 本会话只改了自己卡片允许写的文件；`scripts/**`、forecast / calculation /
      evidence / narrative / source adapter / closure 规则、生产 config 与
      三个 owner 日志未动。
- [ ] 改过 `tests/**` 时，已记下 `tools/sync_installations.py` 的安装副本
      **待同步**（交 MAIN 合入后定点同步；本会话不 run `--apply`，也不把
      安装差异变成新门）。

## Owner 与配置保护

- [ ] `git status` 中每一个未提交的 `config/` 变更都能解释（为什么改、谁改的）。
      无法解释 = 事故：先恢复并记进 `progress.md`。
- [ ] `assurance/runs/daily_alert.jsonl`、`weekly_alert.jsonl`、
      `weekly_manifest.json` 三个 owner 日志保持未提交原状；不 checkout、
      不 reset、不暂存。
- [ ] 临时根（basetemp / scratch）本轮新建的文件已清理，绝对路径核过归属，
      没有使用 `git clean` 或跨 shell 的整串删除。

## 提交

- [ ] `python -B -m ruff check tools tests` 与 `python -B tools/pre_push_gate.py`
      绿 —— 这是日常短责任，不是全套。
- [ ] 正常 `commit` 到自己的施工分支；需要时 `push` 同名施工分支。
      不擅自合 main、不写 installed。
- [ ] 真实待办写进 `progress.md` / 交接文档，不用“应该没问题”代替。

## 只在大节点显式发起（不是会话收尾资格）

- [ ] 完整仓内 pytest（相关责任文件，一次集中节点）：

      python -B -m pytest -q --tb=short -p no:cacheprovider <相关测试文件> --basetemp <独占短临时目录>

- [ ] coverage 显式运行（数据只落独占 scratch，低数字仅诊断）：

      python -B tools/run_coverage_gates.py --run --scratch <DIR>

- [ ] 完整六门 ratchet（同样显式指定 scratch）：

      python -B tools/final_ratchet.py --full --coverage-scratch <DIR>

- [ ] 安装副本全 MATCH / `--apply`、mutation patrol、历史 197 重跑：
      由发布或大节点命令显式发起，不作为每个会话的收尾条件。

## 记录

- [ ] 本会话做了什么、遇到什么错误、**实测时长与用例数**（如实记录，不设
      数字门，不用旧计数冒充本次结果），写入本卡的 `progress.md`。
