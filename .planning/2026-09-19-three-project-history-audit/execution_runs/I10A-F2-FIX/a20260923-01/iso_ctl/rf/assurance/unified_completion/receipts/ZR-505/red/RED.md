# ZR-505 RED 探针证据（2026-08-19）

探针（company-wiki, wiki HEAD 2781df9）：合成含表 pages fixture 直喂 `adapt_pdf_pages`（页2 含 2×2 表：str/int/bool/null）。

## 探针 A：表格 locator 与值保真

```
page_count: 2
loc: page=1 table=None row=None col=None   text='第一页正文'          （段落 span）
loc: page=2 table=None row=None col=None   text='经营数据表'          （段落 span）
loc: page=2 table=0 row=0 col=0  raw='产量'  value='产量'  text='产量'
loc: page=2 table=0 row=0 col=1  raw=100    value='100'   text='100'
loc: page=2 table=0 row=1 col=0  raw=True   value='true'  text='true'
loc: page=2 table=0 row=1 col=1  raw=None   value=None   text=None
```
机制保真：cell locator (page, table_index, row_index, column_index) 全序、raw_value 类型不变形（str/int/bool/null）、value 文本化正确（str 原样/int→str/bool→true/null→None）、rows×cols 全覆盖。

## 探针 B：校验路径

`data=[["a"]]`（2×2 声明 vs 1 cell 实际）→ PageAwarePDFAdapterError（非矩形拒绝）。

## 结论（G1~G3 性质判定）

产品机制已保真（三维 locator、标量类型保真、矩形/标量/字段集校验内建）——RED 为**"无测试钉死"型**（同 ZR-504 模式）。本卡产品改动预期为零（test-only golden），若测试实施中发现缺口再修 parser。
