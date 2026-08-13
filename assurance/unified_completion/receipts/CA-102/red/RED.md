# CA-102 RED 证据

> 规则：RED 从公开/生产入口触发、先证明当前行为确实失败、由独立 oracle 验证。

## RED-A：现有 receipt 无 canonical hash——篡改不可检测

全部 assurance/unified_completion/receipts/**/*.json（CA-001~101）无 `canonical_hash`
字段；没有机器工具对 receipt 做内容校验。scratch 副本篡改一个字节后，无任何
现有工具能检出（git 之外）。

## RED-B：commands/scenarios 为空的 receipt 无门

CA-001 receipt `scenario_results: []`、`commands` 有值；部分 receipt commands 为空。
新 schema 要求 implementer receipt commands 非空；scenario 为空须显式
`scenario_note` 豁免，否则红。

## RED-C：policy_sha256="not-applicable" 滥用

旧 FC receipt（assurance/fc/FC-1001/11_implementer_receipt.json）含
`"policy_sha256": "not-applicable"`——新 schema 将其判为非法（policy 不适用须用
显式字段 + 说明，不得用占位字符串冒充 hash）。

## RED-D：伪 hash 历史前科

CA-003/CA-004 receipt 曾出现手写伪 sha（b06cfbfc…/f4320231d3b3…），已人工修复 +
test_receipt_shas 守卫。新 schema 在验证层内置 triplet 真实性检查（git cat-file），
使伪 hash 在 receipt 层就不可能。

## 新工具对照（本卡实现）

`uc.receipt`：kind 分型必填字段、canonical hash（排序序列化→sha256，可重算）、
N/N-1 策略（未知字段容忍、未知 schema 版本拒绝）、triplet git 对象真实性、
policy_sha256 格式门、篡改必红。
