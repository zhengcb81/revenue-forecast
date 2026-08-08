# 会话收尾检查单（R4.3）

会话结束前逐项执行。任何一项失败都必须先解释/恢复，再收尾。

## 配置卫生（N-05 教训）

- [ ] `git status` 中**每一个**未提交的 `config/` 变更都有解释（为什么改、谁改的）。
      无法解释 = 事故：立即 `git checkout -- <file>` 恢复并记录到 progress.md。
- [ ] `config/source_catalog.yaml`（company-wiki）/ `config/company_wiki.json`（revenue）
      与 git HEAD 一致（`git diff --exit-code`）。

## 安装同步（N-06 教训）

- [ ] `python tools/sync_installations.py` 输出全部 MATCH（漂移即 exit 1）。
      漂移时：先 `--apply` 同步，再确认 MANIFEST 一致。
- [ ] 任一安装副本的 `scripts/revenue_forecast.py --version` 的
      `manifest_sha256` 与 canonical 相同（肉眼漂移检查）。

## 测试与验证

- [ ] `python -m pytest tests -q` 全绿
- [ ] `python e2e/run_revenue_forecast_e2e.py` PASS
- [ ] `python scripts/publication_registry.py audit` exit 0

## 记录

- [ ] 本次会话做了什么、遇到什么错误，写入 `review_audit/progress.md`
      （跨会话唯一可信日志）。
