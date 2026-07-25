# 资源型企业营收建模指南

## 适用场景

当企业营收来源于消耗物理或逻辑存量时，使用 `reserve_depletion` 模型：

| 行业 | 存量类型 | 流入 | 流出 | 关闭存量 |
|---|---|---|---|---|
| **矿业** | 矿产储量(吨/盎司) | 勘探增储、并购 | 采出消耗 | 剩余储量 |
| **医药** | 商业化产品管线 | 新药获批 | 专利到期、停产 | 在售产品 |
| **房地产** | 可售土地储备(平方米) | 新购土地 | 开发消耗 | 剩余土储 |
| **制造业** | 产能计划(单位/年) | 新建产线 | 退役淘汰 | 可用产能 |

共同结构：**期初存量 + 新增 − 消耗 = 期末存量**，消耗量经转化后产生营收。

## 模型选择

| 情况 | 推荐模型 | 原因 |
|---|---|---|
| 有储量/存量的期初期末数据和年度消耗量 | `reserve_depletion` | 内置库存流量桥接和连续性校验 |
| 可售量已知（直接给出年度产量/销量） | `resource` | 简单 volume × price |
| 约束是加工能力而非储量 | `capacity_utilization` | 产能×利用率×收率×价格 |
| 仅有增长率假设 | `direct_growth` | 回退方案，置信度打折 |

## 必需参数

| 驱动 | 维度 | 说明 |
|---|---|---|
| `opening_reserves` | `reserve_volume` | 年初存量 |
| `additions` | `reserve_volume` | 年内新增（勘探增储、并购、再评估、管线新增） |
| `depletion` | `reserve_volume` | 年内消耗（采出、开发、到期、退役） |
| `closing_reserves` | `reserve_volume` | 年末存量 = 期初 + 新增 − 消耗 |
| `recovery_rate` | `ratio` | 消耗量转化为可售产品的比率（0~1） |
| `realized_price` | `revenue_per_unit` | 可售产品单位实现价格 |
| `other_revenue` | `revenue` | 副产品、回收、附属收入（可选） |

## 库存流量不变量

引擎每年强制校验：
```
opening_reserves + additions - depletion = closing_reserves
```
年度间连续性：
```
closing_reserves[t-1] = opening_reserves[t]
```

## 各行业参数映射

### 矿业（如紫金矿业）
- `opening_reserves`: 探明+概略矿产金当量储量（吨）
- `additions`: 勘探增储、并购新增、资源重估
- `depletion`: 采出并处理的矿石量
- `closing_reserves`: 剩余储量
- `recovery_rate`: 选冶回收率
- `realized_price`: 平均实现金属价格（元/吨）

### 医药
- `opening_reserves`: 已获批商业化产品数量
- `additions`: 新药获批上市
- `depletion`: 专利到期、主动退市
- `closing_reserves`: 在售产品数量
- `recovery_rate`: 市场渗透率
- `realized_price`: 单产品平均营收

### 房地产
- `opening_reserves`: 可售土地储备（平方米）
- `additions`: 新购土地
- `depletion`: 投入开发的土地
- `closing_reserves`: 剩余可售土储
- `recovery_rate`: 可售面积比率
- `realized_price`: 平均售价（元/平方米）

### 制造业
- `opening_reserves`: 年初可用产能（单位/年）
- `additions`: 新建产线投产
- `depletion`: 产线退役
- `closing_reserves`: 年末可用产能
- `recovery_rate`: 产能利用率
- `realized_price`: 单位产品价格

## 敏感性分析建议

典型敏感性目标：
- `depletion`（消耗量/产量）— 产能爬坡节奏不确定性
- `recovery_rate`（回收率/转化率）— 技术工艺变化
- `realized_price`（实现价格）— 市场价格波动
- `additions`（新增量）— 勘探成功/并购执行/管线进展

注意：`reserve_volume` 维度允许负值（如储量下调修订），敏感性测试可覆盖下行场景。

## 与其他模型的配合

- 主要商品段使用 `reserve_depletion`
- 副产品段（已知可售量）使用 `resource`
- 产能约束明显的段使用 `capacity_utilization`
- 无储量数据时才用 `direct_growth`（回退方案）

## 研究覆盖自定义维度

资源型企业可在九维基础上增加自定义维度：
- `reserves`: 储量分级、资源量、储量寿命
- `processing`: 回收率、选冶能力、冶金复杂度
- `regulatory_permits`: 采矿权、环保审批、土地使用权
- `pipeline`: 药物管线阶段、临床试验进展
