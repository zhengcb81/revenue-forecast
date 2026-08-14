# CA-103 RED 证据

> 规则：RED 从公开/生产入口触发、先证明当前行为确实失败、由独立 oracle 验证。

## RED-A：无 revision 元数据——"第一个 receipt"是任意选择

当前全部 receipts/CA-***/*.json 无 revision/supersedes 字段。同一单位目录下多个
receipt 时没有任何机器规则选择"最新有效"——closure 依赖人工纪律。审计记录
FC-504 类 r1/r2 混淆（旧 receipt 的 revision 语义混乱）。

## RED-B：无 reviewer 配对校验

无工具校验 reviewer receipt 引用的是哪个 implementer receipt（reviewed_object
hash 可任意）、reviewer 是否与 implementer 分离、是否存在唯一 reviewer 决策。

## RED-C：changes_required 后旧 accepted 可回退覆盖

若单位曾有旧 accepted receipt，而最新 revision 被 reviewer 判 changes_required，
现有流程没有任何机器规则阻止旧的 accepted 状态被当作当前完成。

## RED-D：P1/P2/P3 finding 无强制后继

CA-001 复核曾产出 F1/F2 阻断 finding——靠人工修复闭环，无机器强制后继与
phase-exit 阻断。

## 新工具对照（本卡实现）

`uc.revision`：receipt revision 链（supersedes 校验：无环、无分叉）、最新有效
revision 选择、reviewer 配对（reviewed_object_sha256 == 所选 implementer receipt
的 canonical_hash、reviewer ≠ implementer）、决策优先级（最新 reviewer 决策优先，
旧 accepted 不可回退覆盖）、finding P1/P2/P3 强制后继与 phase-exit 阻断。
