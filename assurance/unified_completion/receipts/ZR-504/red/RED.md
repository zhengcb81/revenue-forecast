# ZR-504 RED 探针证据（2026-08-19）

探针（company-wiki, wiki HEAD e8e2926）：合成 pages fixture 直喂 `adapt_pdf_pages`（无真 PDF），检查 locator 页码保真现状。

## 探针 A：3 页纯文本（页1 两段、页2 两段、页3 一段）

```
page_count: 3
loc: page=1 para=0 chars=0-21   status=parsed
loc: page=1 para=1 chars=23-34  status=parsed
loc: page=2 para=0 chars=36-45  status=parsed
loc: page=2 para=1 chars=47-54  status=parsed
loc: page=3 para=0 chars=56-65  status=parsed
```
机制保真：物理页序 1..3、页内 paragraph_index 从 0、char 全局连续（页间 "\n\n" +2 偏移正确计入 21→23→36→47→56）、normalized_text 页序拼接。

## 探针 B：error 页路径（页2 error="renderer crashed"）

```
page_count: 3
loc: page=1 para=0 chars=0-5    status=parsed flags=()
loc: page=2 para=None chars=None-None  status=failed flags=('parser_error',)
loc: page=3 para=0 chars=7-12   status=parsed flags=()
```
error 页 → failed span 页码保留、后续页序号与 char 偏移不破坏（7-12 全局连续）。

## 探针 C：非连续页序

`[page(1), page(3)]` → PageAwarePDFAdapterError（物理页序强制连续拒绝）。

## 结论（G1~G3 性质判定）

**产品机制已保真**（物理页序强制、char 全局偏移、error 页页码保留、非连续拒绝均内建且探针验证通过）——RED 为**"无测试钉死"型**：G1 逐页 locator golden 无测试、G2 页错误路径无断言、G3 page_count（ZR-501）与 locator 页码集无交叉验证。本卡产品改动预期为零（test-only golden 钉死），若测试实施中发现缺口再修 parser。
