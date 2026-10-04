# RATCHET-FIX-ARCHIVE —— 父自执行的 archive 拆分载体（**补建**）

> **补建缘由（复审 P3-2）**：`archive_retired_evidence.py` 的 19→7 拆分由**父亲手执行**（`§四十二 裁定一` 授权），当时**未建载体**（A/B/C 三组均不含该文件、亦无 `pre_image/`）⇒ 独立复审以 `git show HEAD:` 作前像替代。**本载体现补建以补齐归属与留痕**，不改任何产品码。

## 归属与依据
- **执行者**：父（编排层）· **授权**：`OWNER_DECISIONS §四十二 裁定一`（「我修棘轮」）
- **触发**：`pre-push` 门禁原文 `archive_retired_evidence.py max complexity 19 exceeds frozen 7`（09-22 `ac4ebd0` PROMOTION-EXEC B3/B4/B5 引入）
- **门禁口径度量**（`test_fc1204_complexity_ratchet.py::_max_complexity`）：**pre = 19 → post = 7** ≤ 冻结 7 ✓

## 前后像（sources of truth）
| 件 | 来源 | sha256 | bytes |
|---|---|---|---|
| `pre_image/archive_retired_evidence.py` | `git show HEAD:src/company_wiki/source_catalog/archive_retired_evidence.py`（K=HEAD blob，**非载体留痕**） | `bbe855e4495e82d2a40b0185c9db8efa2639449fdd5f768120538abb992b28ac` | 9894 |
| `post_image/archive_retired_evidence.py` | 在树现值 | `4cd950caa0c53042d15f03a00bd197db457a4e0b8aa7f09181b8dae01e87c1ac` | 11925 |

## 拆分内容（行为零变）
把原 19 复杂度的单体 `archive_retired_evidence` 按**同一直线步骤**拆为 7 个 ≤6 的顶层函数：
`_validate_required_now`(D3 校验) · `_target_paths`(D2/D3 唯一命名与目录) · `_write_snapshot_rows`(流式写 TEMP) ·
`_check_reconciliation`(计数对账 fail-closed) · `_verify_and_publish`(自校验后原子发布) · `_write_manifest`(清单原子写) ·
主函数仅做编排（`try/finally` + 残留清理）。
**不变项**：顺序、异常类型与文案、文件布局、D2/D3/D5 全部 fail-closed 保证、`__all__` 导出面。

## 验证（本次与复审两路）
- 门禁：`_max_complexity` **7/7** ✓；`pytest tests/contract/test_fc1204_complexity_ratchet.py` 的 `frozen` 组 **PASSED**
- 复审独立证：archive 端到端补 `now=` 真跑 6 行 —— report/行序/gz 文本 sha/字节数/manifest 载荷**全同**；负路径（自校验篡改、对账不符）异常类型+文案全同、零发布零残留
- 复审：字符串常量多重集 63→69（**短常量丢 0**）· 公开签名逐字相同 · 无函数被删/不可达

## 未决（转 owner，见 `RATCHET-FIX-REVIEW` 报告）
- **P2-1**：`test_source_catalog_archive_retired.py` 2 条红 = 调用点缺 `now=`（`ac4ebd0` 引入 `now` 后测试未跟改；**与本拆分无因果**，复审已用绑定证明：异常在 call binding 处抛出、函数体从未进入）
- **P3-1**：C 组 `handoff` 的 `post_image_sha256["observability.py"]` 命名方向（裸字节 vs LF 归一）相反 —— 已在 `register §165-E` 登记
