# W03-A RF availability：当前唯一实施入口

状态：**READY_FOR_ROOT_FINAL_TYPED_CURRENT_RECHECK**。最终产品 `2de4b9d3ad3c032c89a1987a3b2141610ac91233`，分支 `codex/r1-narrative-availability`。母接口：CWP `docs/plans/du11-source-closure-2026-10-18/r1-holdout-20261021/W03-current-interface.md`，另含2026-10-22 ROOT对current proof metadata原语义的明确补正；详情在handoff。

## 已完成

- [x] Raw receipt/1单一optional proof接现source-clock；保持pub null、旧shape、projected/3 exact与bundle/generation。首RED22FAIL/20PASS留证。
- [x] ROOT actual-event缺口3RED，经common事件接线修复；旧current无proof兼容保留。
- [x] ROOT current语义补正2RED：不以read UTC日制造historical cutoff，current proof只作已校验metadata与actual-event basis，manifest日期不改。
- [x] ROOT既有公共check含真实12模块；9类型债RED用4处已有guard后type-only cast修复，无新条件/ignore/第二gate。
- [x] 49新例与相关12文件 **298PASS/1既有POSIX SKIP，7.30s**；公共mypy12/全ruff/正常commit hooks绿，golden不改，测试根恢复不存在。
- [x] 自有交接、源码SHA/LF、当前安装expectedOld0af及原94b历史、RED/GREEN/清理证据齐备。
- [ ] ROOT最终非作者typed/current签收及main发布/选择安装（本line不自签）。旧26/b76报告只签旧版本；其重放旧current原因码差异如实保留。

## Next Step

ROOT按2de最终源码补审、必要公开CLI组合后ff主线/正常推送，先consumer兼容发布并按0af旧SHA选择安装，再producer。保留ROOT母仓assurance等其他WIP，不合并清理它们。

本线不写CWP/FF/ET、生产配置、CI/hooks、安装或默认，不调用下载/收费API。W03-B/W07仍由总PWF推进。
