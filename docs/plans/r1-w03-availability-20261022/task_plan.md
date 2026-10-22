# W03-A RF narrative 可用时间证据

唯一母接口：CWP `docs/plans/du11-source-closure-2026-10-18/r1-holdout-20261021/W03-current-interface.md`。本线独占 RF `codex/r1-narrative-availability`，基线92b69682。

## 范围

仅 `scripts/company_wiki_narrative_contracts.py`、相关新测试与本计划。raw receipt/1 仅加 optional `availability_evidence`，复用 source-clock/1；manifest pub 仍null，旧省略/null兼容，known future/invalid publication优先。projected/3不接single-proof。原immutable bundle、generation、配置、CI/hooks、安装、CWP/FF均不改。

## 大节点

- [x] 读取冻结接口、真实validator和既有golden，确认源码与exclusive工区。
- [x] A：先固定有效wire及时间/范围负例，保存真实validator RED。
- [x] B：最小消费者接线，同测试GREEN，相关golden/reader/clock回归及静态检查。
- [x] C：正常commit、源码/旧安装SHA/清理/未覆盖范围交接ROOT，等待集中非作者独审与真实producer组合。

## Next Step
C产品已正常commit、清理与机器交接齐备；等待ROOT非作者独审及实际producer组合，不自行合主线/推送/安装。

## 验收界限

本线不调用任何provider/LLM、不下载资料、不替ROOT验收producer。ROOT先consumer后producer顺序发布/安装；W03-B 0.9/v5真实选择/正式摘要/context与W07仍开放。

## ROOT事件补正后的最终冻结

产品 `b76fb96f9b410abceefc6b264120c5101654492b`，实际event反例3RED→47新例全GREEN；最终相关296PASS/1既有SKIP。保留旧asof=None/no-proof兼容，没改旧测试。

**Next Step:** ROOT按最终产品做集中非作者独审与新producer真实组合；仅ROOT负责顺序发布/选择安装。

## 当前唯一下一步

消费者非作者独审26例已通过。**Next Step:** ROOT对新producer进行实际公开CLI→RF组合，随后先consumer后producer发布/安装；本线工程实现与交接完成。
