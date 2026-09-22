# recovery/README.md — E1E7-ERRATA-LANDING a20260921-01

本目录承载**恢复与复核**说明。本卡没有产生需要「回滚」的中间产物；
唯一的外部改动是四次**纯追加**，其前像已完整在册。

## 1. 事实基线（append 前像，均已哈希锁定）

| 卡 | 文件 | bytes_before | sha256_before |
|---|---|---|---|
| M05 | `execution_runs/M05/a20260919-01/oracle.md` | 14790 | `081a206b072303314140eb3e69dfe1b04de400bddd89dc7b1b17c167dfada555` |
| M14 | `execution_runs/M14/a20260919-01/oracle.md` | 19339 | `c2f7cc4e1337552a2f89aa427d6a3bd00c020d6f91f47fb42ea0a790e2da0988` |
| M20 | `execution_runs/M20/a20260919-01/oracle.md` | 13074 | `b43abd8dafe0f5812cfdbd6847fbf332384840982960874f29967657c776672a` |
| M24 | `execution_runs/M24/a20260919-01/oracle.md` | 26216 | `67c3cae63bb679e2fca3956271d32d6dfcbbf82847295bc904036da6418771ca` |

append 后的值见 `../handoff.json → per_card_results` 与 `../evidence/after_hash/`。

## 2. 复核（任何时刻可重跑，只读）

```pwsh
Get-FileHash -Algorithm SHA256 <file>          # 应等于 handoff.per_card_results.sha256_after
```

```python
# 前缀证明（前像 = 整个旧文件）
d = open(path,'rb').read()
assert hashlib.sha256(d[:BYTES_BEFORE]).hexdigest() == SHA256_BEFORE
# 精确追加证明
assert d[BYTES_BEFORE:] == b"\n" + open(landed_text,"rb").read()
# 插入-only
tags = {op[0] for op in difflib.SequenceMatcher(None, before_lines, after_lines).get_opcodes()}
assert tags <= {"equal","insert"}
```

现成证据：`../evidence/prefix_proof/*.json`、`../evidence/after_hash/*.json`、
`../evidence/diff_summary/*.json`、`../evidence/proof_summary.json`、
`../evidence/independent_verify.json`（独立复算，含 attempt 树 mtime 扫描）。

## 3. 若编排层裁定「撤销本追加」（默认**不**建议）

append-only 的可逆形式是**截断到前像**，不是编辑：

```python
data = open(path,'rb').read()
open(path,'wb').write(data[:BYTES_BEFORE])      # 截断后 sha256 必须 == SHA256_BEFORE
```

- 截断**只**允许由编排层授权执行，并须另立一条记录（T1-12 ①：禁止「回改为从未追加」而不留痕）。
- 截断会使本 attempt 的 `per_card_results.sha256_after` 失效 —— 必须同时登记新值与授权来源。
- **禁止**修改前 `BYTES_BEFORE` 之内的任何字节；那会同时毁掉 pin 证明与冻结正文。

## 4. 若需更正追加节内的文字（例如日期标签 2026-09-21 vs 实际 2026-09-22）

只能**再起一轮 T1-12 ① 追加**（新增一节、旧行不动），不得就地编辑。
见 `../decision.md` DEC-E1E7-5 与 `../evidence/provenance_time_note.json`。

## 5. 不要做的事

- 不要改 `evidence/**/*.json`（E 列表点名的载体仍待编排层另行授权）。
- 不要动 `scripts/` 产品树、不要跑 pytest、不要执行 git 写命令。
- 不要把本卡 `handoff.status = review_pending` 当作已验收 —— 实现者不自签。
