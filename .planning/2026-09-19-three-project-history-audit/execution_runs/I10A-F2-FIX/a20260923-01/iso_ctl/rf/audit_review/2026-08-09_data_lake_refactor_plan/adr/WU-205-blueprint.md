# ADR WU-205：目标架构蓝图与 fitness functions（ARC-FIT-01~06）

> 计划版本：2.1-full-refactor-execution-cards | 状态：冻结（contract_frozen）

## 目标包/模块图

- company-wiki：RootPolicy/registry、scanner facade、v1 scanner（legacy，冻结）、
  v2 orchestrator、adapters（SPI）、normalizer、admission、assertion ledger、
  resolver v1/v2、SourceBundle。
- filing-fetch：protocol client、reuse/latest/download coordinator、canonical capture。
- revenue：source-preparation orchestrator、validated source record、纯 forecast calculator。

## Fitness functions（每条被违反应使 gate 失败）

| ID | 规则 |
|---|---|
| ARC-FIT-01 | scanner v2 只依赖 adapter interfaces/normalizer/admission/persister ports（禁 network/fs） |
| ARC-FIT-02 | adapters 不反向依赖 resolver/scanner/download/parser/LLM |
| ARC-FIT-03 | resolver v2 不 import scanner/adapters，不读 legacy metadata keys |
| ARC-FIT-04 | filing-fetch/revenue 不 import company-wiki 私有 Python 模块（只经版本化 CLI/contract） |
| ARC-FIT-05 | calculator 不依赖 filesystem/network/catalog |
| ARC-FIT-06 | legacy 模块只能被 facade/compat tests 调用，不得获得新产品 caller |

## 校验

```bash
python -m pytest audit_review/2026-08-09_data_lake_refactor_plan/tools/tests/test_architecture_boundaries.py -q
# 14 passed（ARCH-01~05 + ARC-FIT-01~06 + 扫描边界）
```
