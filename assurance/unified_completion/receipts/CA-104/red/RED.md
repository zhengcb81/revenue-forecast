# CA-104 RED 证据

> 规则：RED 从公开/生产入口触发、先证明当前行为确实失败、由独立 oracle 验证。

## RED-A：99 条 receipt 命令零输出 hash——复用旧 stdout 不可检测

全部 receipts/**/*.json 的 command 条目（99 条）无 stdout_sha256/stderr_sha256，
无 duration、无 collected 计数——"改短命令/少收集测试/复用旧 stdout"都无法机器检测。

## RED-B：CI 中存在 `|| true`

company-wiki `.github/workflows/ci.yml:80`：
`python scripts/collect_news.py --help || true` —— 允许非强制失败的反模式。
（修复归 CA-201；本卡登记 finding。）

## RED-C：结构化业务失败但 process=0 会被记 pass

现有 receipt 命令只记 exit_code 与文字 result；exit 0 + 业务失败（如测试收集数
下降、引擎 rc=2 被包装）无机器区分。

## RED-D：基建错误无分类、秘密值无保护

env 值、路径等秘密无脱敏规范；网络/权限类失败与产品失败混为一谈。

## 新工具对照（本卡实现）

`uc.commands`：CommandSpec（argv/cwd/env allowlist/timeout/tier/side-effect budget）
→ CommandResult（exit_code、business_outcome（pass/structured_failure/infra_error）、
collected/passed/failed/skipped（pytest 输出解析）、duration、stdout/stderr sha256、
时间戳；env 值永不记录）→ 不可变 result artifact（CAS 发布）→ replay-diff 重放
对比 current code 差异。
