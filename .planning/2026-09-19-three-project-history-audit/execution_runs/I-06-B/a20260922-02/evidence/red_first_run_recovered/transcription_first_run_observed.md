# transcription_first_run_observed.md — 首跑工件转录件（执行者会话直读，非原始字节）

> **来源声明（防伪造误读）**：以下内容是本 attempt 执行者在 run2 结束后、run3 覆写前，用 `read` 工具
> **直接读到的文件全文**（以及 run1 崩溃时的控制台输出）。原文件随后被 run3 同名覆写，**原始字节已不可
> 得、原始 sha256 未记录**。本件 = 如实转录，**不是**原始工件的字节副本，不可作为独立可复核的原始证据
> 使用；其可信面为：与 `%TEMP%` 抢救批（run2_kwarg_typeerror_230554-56，J 目录 CreationTime 23:05:56）、
> 三处文字自述、以及 run3 修复后同例结果三方互证。对应复审 F-01。

---

## 1. run2 首版 `evidence/red/I.json`（finished_at 2026-09-22T23:05:56，read 工具全文直读）

```json
{
  "case": "I",
  "title": "same-key multi-writer: defined rejection, zero silent loss (P6-A)",
  "iso": "original",
  "ruling_clause": "FIX-W06-GAPS oracle P6-A; probe06 lost-writes; OPEN-6 §7.4 F; OPEN-4 §4.1 counterexample (i)",
  "verdict": "FAIL",
  "checks": [
    {
      "name": "I1_hook_interleave_and_outcomes",
      "ok": false,
      "detail": "hook_fired=True outcomes=[{\"writer\": \"A\", \"outcome\": \"TypeError\", \"text\": \"__main__.record_kwargs() got multiple values for keyword argument 'reviewer'\"}, {\"writer\": \"B\", \"outcome\": \"TypeError\", \"text\": \"__main__.record_kwargs() got multiple values for keyword argument 'reviewer'\"}] third=[{\"writer\": \"A\", \"outcome\": \"TypeError\", \"text\": \"__main__.record_kwargs() got multiple values for keyword argument 'reviewer'\"}, {\"writer\": \"B\", \"outcome\": \"TypeError\", \"text\": \"__main__.record_kwargs() got multiple values for keyword argument 'reviewer'\"}] (every attempt must be an ack or a defined 'concurrent write conflict' rejection — never a bare/other escape)"
    },
    {
      "name": "I2_no_silent_loss_every_ack_provable",
      "ok": false,
      "detail": "acks=0 unprovable=[] primary=null audit=null — an acked write that neither the primary receipt nor the audit trail can prove was silently displaced (probe06 lost_write_count=7 shape)"
    },
    {
      "name": "I3_count_conservation",
      "ok": false,
      "detail": "acks=0 rejections=0 attempts=2 (conservation: acks+rejections == attempts, zero third outcomes)"
    }
  ],
  "raw": {
    "I_hook_fired": true,
    "I_writer_B_outcome": {
      "writer": "B",
      "outcome": "TypeError",
      "text": "__main__.record_kwargs() got multiple values for keyword argument 'reviewer'"
    },
    "I_attempts": [
      {
        "writer": "A",
        "outcome": "TypeError",
        "text": "__main__.record_kwargs() got multiple values for keyword argument 'reviewer'"
      }
    ],
    "I_final_primary": null,
    "I_final_audit": null
  },
  "error": null,
  "seconds": 0.044,
  "finished_at": "2026-09-22T23:05:56"
}
```

## 2. run2 首版 `evidence/red/J.json`（finished_at 2026-09-22T23:05:56，read 工具全文直读）

```json
{
  "case": "J",
  "title": "detected_and_ignored disposal gate fail-closed (OPEN-6 C1/C3, P5-b)",
  "iso": "original",
  "ruling_clause": "OPEN-6 C1/C2/C3 (§5); FIX-W06-GAPS oracle P5-b",
  "verdict": "FAIL",
  "checks": [
    {
      "name": "J1_disposal_gate_rejects",
      "ok": false,
      "detail": "type=TypeError text=\"__main__.record_kwargs() got multiple values for keyword argument 'reviewer'\" (expect prefix 'disposal authorization unavailable: ', first gap = ignore_reason / trust root not established)"
    },
    {
      "name": "J2_zero_product_semantic_rows",
      "ok": true,
      "detail": "product-semantic detected_and_ignored rows after the attempt = 0 (OPEN-6 C3: identity not established ⇒ rows must be 0)"
    }
  ],
  "raw": {
    "J_exception": "TypeError: __main__.record_kwargs() got multiple values for keyword argument 'reviewer'",
    "J_receipt": null
  },
  "error": null,
  "seconds": 0.041,
  "finished_at": "2026-09-22T23:05:56"
}
```

注：此为 I/J「首版」= run2 产物。**run1（23:05:37–39，GBK 崩溃）从未写出 I.json/J.json**（其在 case G
打印处即崩），其残存面 = A..G 的 JSON（已覆写，ABSENT）+ 下方控制台输出转录。

## 3. run1 崩溃控制台输出（GBK UnicodeEncodeError，观察于崩溃当时）

```
[original]   A FAIL idempotency key includes request identity  FAILED=['A1_two_rows_distinct_ids', 'A2_distinct_demand_keys', 'A3_row_binds_own_request_sha256']
[original]   B PASS register-blocks-until-reviewed (recoverable)
[original]   C FAIL N-1 migration adds columns (P1)  FAILED=['C1_migration_adds_6_columns', 'C2_old_rows_preserved', 'C4_upgraded_db_usable']
[original]   D FAIL claim loser defined refusal (P2-B)  FAILED=['D1_loser_defined_refusal_not_none', 'D2_byid_refusal_defined', 'D3b_loser_defined_refusal']
[original]   E FAIL explicit expire → re-claim, no stranding (P3-A/B)  FAILED=['E1_explicit_expire_entry_exists', 'E2a_post_expiry_refusal_defined', 'E2b_byid_post_expiry_refusal_defined', 'E3_expire_reclaims_running_expired', 'E4_lease_cleared_after_expire', 'E5_reclaimable_after_explicit_expire']
[original]  F1 FAIL N-1 errors surface as store-owned types (P1-e)  FAILED=['F1_claim_store_owned', 'F1_list_active_store_owned']
[original]  F2 FAIL lock errors wrapped (P6-B)  FAILED=['F2_lock_error_wrapped']
[stderr]
Traceback (most recent call last):
  File "<attempt>\scripts\run_cases.py", line 1328, in <module>
    raise SystemExit(main())
                    ^^^^^^^^^^^^
  File "<attempt>\scripts\run_cases.py", line 1301, in main
    print(f"[{args.iso}] {case_id:>3} {verdict:<4} {title}"
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
          + (f"  FAILED={failed}" if failed else ""), flush=True)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
UnicodeEncodeError: 'gbk' codec can't encode character '\u21c4' in position 28: illegal multibyte sequence
[exit code: 1]
```

（`\u21c4` = case G 标题里的 `⇄`；崩溃点在 case G 的 print，G 的 JSON 当时已写出。行号为当次
run_cases.py 版本——该文件其后经编码修复与 reviewer-kwarg 修复，现盘 sha
`1656124425564bc553cc5c6c9918e3a355157016bc1a4b8f34713967d9115930`，见 binding.json。）

## 4. 与抢救批的互证

- run2 批 `i06b_J_vdm9zquk` / `i06b_I_jx_5wegc` CreationTime = 2026-09-22 23:05:56 —— 与上述两 JSON 的
  `finished_at` 同秒 ⇒ 批次归属确证。
- run1 批末目录 `i06b_G_ccj29i_n` CreationTime = 23:05:39 —— 与「崩溃于 case G」确证。
- 三处文字自述（commands/decision/handoff）对本缺陷的描述与上述转录内容一致。
