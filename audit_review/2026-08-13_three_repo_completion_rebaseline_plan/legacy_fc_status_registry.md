# 旧71个FC逐ID状态投影

> 本表消除范围写法的歧义。它是只读审计投影，不修改旧registry。  
> 分类：`I=implemented_not_independently_verified`、`C=contradicted_by_current_behavior`、`S=stale_evidence`、`P=pending`。  
> 所有successor初始pending；旧accepted不能自动推进新状态。

## 原因码

| 码 | 含义 |
|---|---|
| B0 | 历史基线、triplet、数据或计划hash已漂移 |
| G1 | 组件/控制资产存在，但current-triplet独立重放缺失 |
| G2 | scenario/command/receipt/closure语义可假绿 |
| G3 | current triplet/upstream/dirty/config/skill未精确绑定 |
| P1 | RootPolicy/v1-v2/flag只到shadow或同请求策略分叉 |
| P2 | external-root consumer、eligible location或真实三root未贯通 |
| F1 | freshness/revision/multi-gap/download动作未闭环 |
| A1 | artifact lineage/binding/DAG/producer/safety未闭环 |
| E1 | 测试支架存在，但真实production E2E/tier/平台范围不足 |
| D1 | 动态runner存在，但scheduler/report/alert/freshness/soak未运行 |
| Q1 | hardcode/双路径/复杂度/type/encoding目标未完整达到 |
| O1 | SLO/容量/观测框架存在，但代理语义或持续证据不足 |
| Z1 | 旧最终关闭单元明确pending |

## 精确注册表

| FC | 旧登记 | 类 | 原因 | 唯一successor |
|---|---|---:|---|---|
| FC-000 | completed_plan_baseline | S | B0 | CA-002, CA-004 |
| FC-001 | completed_plan_baseline | S | B0 | CA-002, CA-004, ZR-001 |
| FC-002 | completed_plan_baseline | S | B0 | CA-001, CA-004 |
| FC-101 | accepted | I | G1 | CA-101, CA-102, ZR-101 |
| FC-102 | accepted | C | G2 | CA-104, CA-105 |
| FC-103 | accepted | C | G2 | CA-102, CA-103, CA-107, CA-108 |
| FC-104 | accepted | C | G3 | CA-002, ZR-105, CA-201 |
| FC-201 | accepted | I | G1 | CA-003, ZR-101, ZR-401, ZR-1003 |
| FC-202 | accepted | I | G1 | CA-003, ZR-101, ZR-404, ZR-1003 |
| FC-203 | accepted | I | G1 | ZR-1002, ZR-1003 |
| FC-204 | accepted | I | G1 | ZR-1003, ZR-1004 |
| FC-205 | accepted | I | G1 | CA-003, ZR-1002, ZR-1003 |
| FC-301 | accepted | I | P1 | ZR-401 |
| FC-302 | accepted | I | P1 | ZR-402 |
| FC-303 | accepted | I | P1 | ZR-402, ZR-403 |
| FC-304 | accepted | C | P1 | CA-003, ZR-403, ZR-404 |
| FC-305 | accepted | I | P1 | ZR-409, ZR-1003, ZR-1004, CA-304 |
| FC-401 | accepted | I | A1 | ZR-304, ZR-305, ZR-1005 |
| FC-402 | accepted | I | A1 | ZR-304, ZR-305, ZR-1005 |
| FC-403 | accepted | I | A1 | ZR-304, ZR-305, ZR-1005 |
| FC-404 | accepted | I | A1 | ZR-304, ZR-305, ZR-1005 |
| FC-405 | accepted | I | A1 | ZR-304, ZR-305, ZR-1005 |
| FC-501 | accepted | C | P2 | ZR-401, ZR-404, ZR-405 |
| FC-502 | accepted | I | P1 | ZR-501, ZR-502 |
| FC-503 | accepted | I | P1 | ZR-402, ZR-403, ZR-501, ZR-502 |
| FC-504 | accepted | S | P2 | CA-103, ZR-409, ZR-802, ZR-806 |
| FC-505 | accepted | C | P2 | ZR-405, ZR-409, ZR-806, CA-302 |
| FC-601 | accepted | I | P1 | ZR-402, ZR-409 |
| FC-602 | accepted | C | P2 | ZR-403, ZR-405, ZR-409 |
| FC-603 | accepted | I | P1 | ZR-409, ZR-802, ZR-806 |
| FC-604 | accepted | C | P2 | ZR-405, ZR-409, ZR-802, CA-302 |
| FC-701 | accepted | I | G1 | ZR-201, ZR-202, ZR-203 |
| FC-702 | accepted | I | G1 | ZR-204 |
| FC-703 | accepted | I | O1 | ZR-202, ZR-206 |
| FC-704 | accepted | I | G1 | ZR-307, CA-106 |
| FC-705 | accepted | S | P1 | CA-003, ZR-1003, ZR-1009, CA-304 |
| FC-801 | accepted | I | F1 | ZR-406, ZR-407 |
| FC-802 | accepted | C | F1 | ZR-406, ZR-407 |
| FC-803 | accepted | I | F1 | ZR-407, ZR-408, ZR-805 |
| FC-804 | accepted | C | F1 | ZR-408 |
| FC-805 | accepted | S | F1 | ZR-805, CA-203 |
| FC-901 | accepted | C | A1 | ZR-304, ZR-305, ZR-1005 |
| FC-902 | accepted | C | A1 | ZR-304, ZR-306, ZR-307 |
| FC-903 | accepted | I | P2 | ZR-307, ZR-404, ZR-405 |
| FC-904 | accepted | I | A1 | ZR-306, ZR-706 |
| FC-905 | accepted | C | A1 | ZR-302, ZR-303, ZR-307 |
| FC-906 | accepted | C | A1 | ZR-003, ZR-305, ZR-510, ZR-806 |
| FC-1001 | accepted | I | E1 | ZR-102, ZR-801 |
| FC-1002 | accepted | C | E1 | ZR-102, ZR-802 |
| FC-1003 | accepted | C | G2 | CA-105, CA-106, ZR-801 |
| FC-1004 | accepted | C | E1 | ZR-804 |
| FC-1005 | accepted | S | E1 | ZR-803, ZR-805, ZR-806 |
| FC-1101 | accepted | C | G3 | ZR-105, ZR-901, CA-201 |
| FC-1102 | accepted | C | D1 | ZR-902, CA-202 |
| FC-1103 | accepted | C | D1 | ZR-903, CA-203 |
| FC-1104 | accepted | C | D1 | ZR-904, CA-205 |
| FC-1105 | accepted | C | D1 | ZR-905, CA-205, CA-206 |
| FC-1201 | accepted | C | Q1 | ZR-401, ZR-402, ZR-403, ZR-404, ZR-405, ZR-406, ZR-407, ZR-408, ZR-409, ZR-906, CA-303, CA-304 |
| FC-1202 | accepted | C | P1 | CA-003, ZR-401, ZR-404, ZR-405, ZR-907 |
| FC-1203 | accepted | I | Q1 | ZR-104, ZR-906, CA-303 |
| FC-1204 | accepted | C | Q1 | ZR-104, ZR-906, CA-303 |
| FC-1205 | accepted | C | Q1 | ZR-204, ZR-804, ZR-906 |
| FC-1301 | accepted | I | O1 | CA-101, ZR-204, ZR-904 |
| FC-1302 | accepted | S | O1 | ZR-206, ZR-904, CA-202 |
| FC-1303 | accepted | I | O1 | ZR-206, ZR-904, CA-202, CA-205 |
| FC-1304 | accepted | S | O1 | ZR-206, ZR-904, CA-202, CA-206 |
| FC-1501 | pending | P | Z1 | CA-107, CA-108, CA-109 |
| FC-1502 | pending | P | Z1 | CA-301, CA-303 |
| FC-1503 | pending | P | Z1 | CA-302 |
| FC-1504 | pending | P | Z1 | CA-206, CA-304 |
| FC-1505 | pending | P | Z1 | CA-305, CA-306 |

## 机器验收

- 行数必须精确71，ID唯一。
- 分类计数必须精确：I=31、C=26、S=9、P=5。
- 每行successor至少一个，且每个精确ZR/CA ID都有定义。
- `accepted`只描述旧登记，不能被closure当新状态。
- 旧registry任何后续漂移只触发CA-004重审，不直接覆盖本表。
