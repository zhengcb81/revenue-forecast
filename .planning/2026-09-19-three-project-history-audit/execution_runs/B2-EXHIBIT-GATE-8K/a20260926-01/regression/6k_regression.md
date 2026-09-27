# B2 · 6-K 行为不变的逐字节对比表（回归证明）

- 冻结件 = **改动前**的 iso 上运行 harness `freeze` 落盘（`results/6k_frozen_before.json`、`results/adapter_frozen_before.json`）；
- 改动后件 = `changes.diff` 应用后的 iso 上运行 `check` 落盘（`results/dayu_gate_check.json`、`results/adapter_copy_check.json`）。
- 判定方式：把**整个结构** `json.dumps(..., indent=2, sort_keys=True)` 后取 **SHA-256**，两个 sha 必须相同（不只是文件名相同）。

## A. dayu 层 —— `list_filing_files(form_type="6-K")` 的 descriptors 全字段 JSON

| # | 断言 | 冻结件（改动前） | 改动后 | 字节 | 判定 |
|---|---|---|---|---|---|
| A1 | `include_exhibits=True` 全字段 JSON | `649d906c3bc03bccd19c51849e78363646f36c7636ce8753173a884086def2bd` | `649d906c3bc03bccd19c51849e78363646f36c7636ce8753173a884086def2bd` | 3318 = 3318 | **逐字节相同** |
| A2 | 冻结文件本身 | `aa79e08f2bfeeba5…` | — | 3415 | 冻结件落盘于改动前 |

文件名清单（两份逐项对照）：

| include_exhibits | 改动前 filenames | 改动后 filenames | 判定 |
|---|---|---|---|
| True | `d123dex991.htm, form6kcover.htm, q12025pressrelease.htm, sample-6k.htm, sample-6k.xsd, sample-6k_htm.xml` | `d123dex991.htm, form6kcover.htm, q12025pressrelease.htm, sample-6k.htm, sample-6k.xsd, sample-6k_htm.xml` | **相同** |
| False | `sample-6k.htm, sample-6k.xsd, sample-6k_htm.xml` | `sample-6k.htm, sample-6k.xsd, sample-6k_htm.xml` | **相同** |

## B. company-wiki adapter 层 —— 6-K filing 的 `discover()+fetch()` 完整结果对象

| # | 断言 | 冻结件（改动前） | 改动后 | 判定 |
|---|---|---|---|---|
| B1 | 结果对象（candidates/receipt/staged_files/staged_hashes/payload）整体 | `0c9000a11443dba1a505534d80dfb3f2d8717bcef705734a494d02e89ef41b7c` | `0c9000a11443dba1a505534d80dfb3f2d8717bcef705734a494d02e89ef41b7c` | **逐字节相同** |
| B2 | staged 文件集合 | `tm2412704d1_6k.htm` | `tm2412704d1_6k.htm` | **相同** |
| B3 | candidate `adapter_payload_json`（provenance sidecar 的候选段） | `{"content_sha256":"edddeadad75c1875e9f9b26b99682fccfb9fe6e7b11284a7acba5f40d83ebb2b","dayu_document_id":"fil_6k","primary_filename":"tm2412704d1_6k.htm"}` | `{"content_sha256":"edddeadad75c1875e9f9b26b99682fccfb9fe6e7b11284a7acba5f40d83ebb2b","dayu_document_id":"fil_6k","primary_filename":"tm2412704d1_6k.htm"}` | **相同** |
| B4 | receipt `content_sha256` | `edddeadad75c1875e9f9b26b99682fccfb9fe6e7b11284a7acba5f40d83ebb2b` | `edddeadad75c1875e9f9b26b99682fccfb9fe6e7b11284a7acba5f40d83ebb2b` | **相同** |

## C. 10-K（非授权 form，附带回归）

| 断言 | 冻结件 | 改动后 | 判定 |
|---|---|---|---|
| 10-K 结果对象整体 | `7507acadb06e691ba923ce1d9acb689d9df122ebff491af5fa009696ca9f3109` | `7507acadb06e691ba923ce1d9acb689d9df122ebff491af5fa009696ca9f3109` | **逐字节相同** |
| 10-K staged 集合 | `msft-20250630.htm` | `msft-20250630.htm` | **相同** |

## D. 这张对比表确实会咬（变异证据）

- **M2**（删共享分支一行，6-K 走到被改动的代码）→ dayu rc=`2`，红 = `G3_6k_list_byte_identical, G4_6k_expected_names_present` ⇒ A1/A2 断言变红。
- **M3**（adapter 闸门放宽为 `{6-K, 8-K}`，让 6-K 也走新复制逻辑）→ adapter rc=`1`，红 = `A4_6k_result_byte_identical_to_before` ⇒ B1–B4 断言变红。

> 结论：6-K 在**两层**（dayu 远端清单、company-wiki staging/payload/receipt）的输出与改动前**逐字节相同**；10-K 亦逐字节相同。
