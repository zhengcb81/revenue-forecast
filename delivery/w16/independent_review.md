# W16-RF-BASIS 独立审查（最终汇总入口）

- 审查方式：按用户要求拆分为 6 个独立小片并发/顺序执行（S1–S5 静态只读对照 + S6 执行型独立运行与反例）。各片审查agent均未参与实现。
- 被审代码：初始 84e2152f；finding 修复后复审为 cb60bd21；95c25c4b 仅一行 lint 注释措辞（S3-1 处置），无功能变化。
- 分片原始报告（COMMON §4 要求保留原件）：
  - S1 写入范围+硬编码：`review_s1.md` — 0 finding（双 PASS）
  - S2 B02/B03 语义：`review_s2.md` — 5 PASS；S2-1 Low（DU5 正则重复）、S2-2 Info（legacy 报告字节级新增小节）
  - S3 B04 复算桥：`review_s3.md` — 5 PASS；S3-1 Low（lint 注释偏强）、S3-2 Low（component 无非负约束）
  - S4 B05/B06 链路与断言：`review_s4.md` — 5 PASS；S4-1 Low（ytd 未走 CLI）、S4-2 Info（中文目录仅成功例）
  - S5 兼容性+质量：`review_s5.md` — 6 PASS；S5-1 Medium（engine_unit 别名误拒+缺尺度校验，与 S2-1 同根）、S5-2 Low（非数字 extracted_value 裸 ValueError）、S5-3 Info（lint 冗余）
  - S6 执行型：`review_s6_exec.md` — 0 finding；独立运行 41+41 测试与真实 CLI（中文/空格目录）全绿；7 个自建反例全部判定正确（反向混合重述=放行+标不可比；非基年组件=放行；篡改簇 4 变体含删 input_document/自洽伪造=全部拦截；复数单位拼写=拒绝；claim 期间错配=拒绝）

## 逐 finding 处置（全部闭环）

| ID | 严重度 | 处置 | 位置 |
|---|---|---|---|
| S5-1 | Medium | 已修：DU5 新增公共 `money_unit_currency`/`money_unit_scale_factor`，revenue_basis 改调公共层并新增 engine_unit 尺度==文档单位校验（额外关闭尺度盲缺口）；新增正反测试 | cb60bd21 |
| S2-1 | Low | 已修（同 S5-1 根因）：删除复制的归一化正则与私有表直查 | cb60bd21 |
| S3-2 | Low | 已修：component value 非负 require + 测试 | cb60bd21 |
| S5-2 | Low | 已修：`_extract_matches` 安全数值比较，非数字串不再裸 ValueError + 测试 | cb60bd21 |
| S4-1 | Low | 已修：CLI 增加 ytd 案例（断言 stderr 中文消息） | cb60bd21 |
| S4-2 | Info | 已顺带修复：ytd 错误案例使用中文目录名，子进程钉 UTF-8 管道 | cb60bd21 |
| S3-1 | Low | 已修：lint 注释如实声明只做 schema 层校验 | 95c25c4b |
| S2-2 | Info | 记录不改：加法诊断为卡片允许输出；渲染措辞"未声明/不视为已核实"符合 B02 | — |
| S5-3 | Info | 记录不改：观感问题不影响机读 | — |

## 复审证据

- cb60bd21 后：`tests/test_w16_revenue_basis.py`（32）+ `tests/test_w16_revenue_basis_cli.py`（9）= 41 PASS；受影响回归 172 PASS（data_contract/recognition_bridge/publication_pipeline/golden_behavior_lock/du5_money_unit_registry/input_quantity_conversion/du5_root_unit_boundaries/lint_input）；`tools/pre_push_gate.py` GREEN（595 PASS 1 skip）。
- S6 独立复跑（审 cb60bd21）：W16 41 PASS、回归 41 PASS、真实 CLI 端到端（中文+空格目录）exit 0 且输出内容断言通过；其 4 个篡改突变证明输出绑定校验不可绕过。

## 最终判定

- 未解决本范围 finding：**0**（blocker 0 / major 0；Medium 1 已修；Low 6 已修；Info 3 中 1 已顺带修复、2 记录保留不改：S2-2 加法诊断为允许输出、S5-3 观感问题）
- 独立审查关键链路已独立执行、反例已由审查者自建（7 个）。
- 判定：**通过（PASS）**，可交接 ROOT。
