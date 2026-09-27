# I-14-E-TESTSIDE-R2 / a20260926-01 — oracle.md（门 -1 记录 + 施加步骤的携带清单）

**本 attempt 状态：`blocked`（在门 -1 即停）。**
本卡是 R2 重跑：派单声明父提权会话探针 `UNBLOCKED`（self pid=4028 ok=True lasterr=0；child
ok=True lasterr=0；VERDICT=UNBLOCKED，2026-09-26 17:5x）。按纪律 19（**父提权可 ≠ 你可**），
本 attempt 先自跑同款探针，**结果 = `STILL_BLOCKED`** ⇒ 按派单硬性条款**立即停、报 blocked
（合格结果）**：未做 iso 拷贝、未跑任何红/绿/变异运行、未施加任何测试侧改动、未写产品仓任何字节。

权威冻结判据**不**在本文件重冻：仍是
`execution_runs/I-14-E-TESTSIDE/a20260924-01/oracle.md`
（sha256 `4c15948e24a2650bf055dddd02b5cc230b561b89de1cf0f34c9a0e293b28f658`，冻结于
2026-09-25T20:40Z、先于该轮任何运行）+ 追加式 `oracle-addendum-A.md`（basetemp 落点）与
`oracle-addendum-C.md`（会话环境阻断与三臂降级）。本文件只登记门 -1 事实、被触发的阻断、
以及**为下一个有权会话预先写好的**施加步骤与变异清单（避免第三次从头推导）。

---

## 1. 门 -1 能力探针（本会话，权威）

- 脚本：`harness/gate1_openprocess_probe.py`（本 attempt 内；含 PS 对照探针
  `harness/gate1_ps_handle_probe.ps1`）
- 运行：2026-09-26T17:13:09Z（UTC），本会话 pid=10628，python 3.13.9
- 原始输出：`evidence/gate-1-openprocess-raw.txt`（逐字）；结构化：
  `evidence/gate-1-openprocess-result.json`

**原始输出逐字（`evidence/gate-1-openprocess-raw.txt` 全文）：**

```
GATE1 session_pid=10628 python=3.13.9 started_utc=2026-09-26T17:13:09Z
STEP1 spawn child pid=18464
STEP2-3 {"pid": 10628, "mask": "0x1F0FFF", "open_ok": false, "rc": 0, "lasterr": 5, "close_ok": null}
STEP2-3 {"pid": 18464, "mask": "0x1F0FFF", "open_ok": false, "rc": 0, "lasterr": 5, "close_ok": null}
STEP2-3 {"pid": 10628, "mask": "0x1000", "open_ok": true, "rc": 436, "lasterr": 5, "close_ok": true}
STEP2-3 {"pid": 18464, "mask": "0x1000", "open_ok": true, "rc": 436, "lasterr": 5, "close_ok": true}
STEP4 wait child rc=0
STEP5 ps rc=0
STEP5 with_redirect: PSREDIRECT pid=1120 handle_nonnull=False handle= read_error=You cannot call a method on a null-valued expression.
STEP5 no_redirect_contrast: PNOREDIRECT pid=12264 handle_nonnull=True handle=2800 read_error=
SELF_ALL_ACCESS_ok=False CHILD_ALL_ACCESS_ok=False PS_REDIRECT_HANDLE_ok=False
VERDICT: STILL_BLOCKED
DISPOSITION: stop immediately; report blocked (qualified result); no destructive substitute permitted.
```

（注：`0x1000` 行的 `lasterr: 5` 是上一次调用遗留的 sticky 值；该两次 `open_ok=true`
即句柄 rc=436、CloseHandle 成功，为对照行，与既往被阻断会话的形态一致。）

### 四步（spawn → open → close → wait）判定

| 步 | 目标 | 掩码 | 结果 |
|---|---|---|---|
| spawn | 子进程 pid=18464 | — | 成功 |
| open（self） | pid=10628 | `PROCESS_ALL_ACCESS 0x1F0FFF` | **handle=0，lasterr=5（ACCESS_DENIED）** |
| open（child） | pid=18464 | `0x1F0FFF` | **handle=0，lasterr=5** |
| close | — | — | ALL_ACCESS 两次无句柄可关；对照行 `0x1000` 关闭成功（close_ok=true） |
| wait | 子进程 | — | rc=0 |

### 复审 S8-1 判据②（产品真实机制，独立于 ctypes）

| 形态 | 结果 |
|---|---|
| `Start-Process` **带** `-RedirectStandardOutput/-RedirectStandardError -PassThru` | **`.Handle` 为 null**（读句柄抛 "null-valued expression"）—— 即 `source_catalog_worker.ps1:340-341` 拿到的形态 |
| 对照：**不带** redirect | `.Handle`=2800 非空（与会话内既往观测一致） |

**判据①（ctypes `OpenProcess` 自生子进程非 0 句柄）失败；判据②（PS redirect `.Handle`
非 null）失败** —— 两条独立机制一致 ⇒ 本会话与上一轮被阻断会话同构。

## 2. 被触发的阻断（写死）

- `blocked_by_env` = **`ENV-OPENPROCESS-ALLACCESS-DENIED`（在本会话仍然成立）**。
- 触发器（任一即停，本次**两条同触**）：
  1. `OpenProcess(0x1F0FFF)` 对 **self 或 own-child** 返回 0 且 `GetLastError()==5`；
  2. PS `Start-Process -RedirectStandard* -PassThru` 的 `.Handle` 为 null。
- 派单硬条款（逐字执行）："若你仍 DENIED ⇒ 立即停、报 blocked（合格结果）—— 禁止任何
  破坏性替代。" 本 attempt 未尝试任何替代路径（无绕开 Job 句柄、无改启动器、无降权掩码替代
  施加、无重试碰运气）。

## 3. 施加步骤清单（**携带给下一个有权会话**，不重推导）

以下步骤在上一轮已冻结（`a20260924-01/oracle.md` §2/§4/§5 + reviewer_report §8 S8-2），
本文件**逐字携带要点**、不改变任何判据；下一个会话只需：

1. **门 -1 自证**（同款探针，判据①或②任一通过即可，本 attempt 用的是双判据更严口径）；
2. **SUT 复位**：iso 拷贝自 `a20260924-01/iso`（或重拷真仓），tests 文件必须复位为原始字节
   sha256 `32515aa60d5fbfbca0778ee68e778ada7ff3bcf238f91930bb621d84aec005c1`（= 真仓
   `company-wiki/tests/contract/test_source_catalog_worker_bootstrap.py` 现值，本 attempt
   只读复核仍同值）；启动器 sha `5c12cd740cc36abf95f3b9559485472d9d9a760143d27de46e3aaa7b4bbc311`
   （本 attempt 只读复核仍同值）；
3. **三臂**按冻结 §4：C1=cpu8（8 忙循环）、每臂 N=6、driver 超时 90 s、basetemp
   `%TEMP%` 内 52–60 字符（addendum-A 口径）、`-p tside_probe` shim 统一生效；
   - 红（修前，写死 0.5 s）：判据 §3.C——≥1 红（期望 6/6），红形态 = `assert … == 2` /
     `TimeoutExpired`（**不再是** `launcher_exception`）；
   - 绿（施加后 `H = min(max(2.0, 4*t0), t0+3)`）：§3.D 四条子判据 + 6/6；
4. **红绿双向变异（≥2，见 §4）**；
5. 交付 `after/changes.diff`（只含 `tests/**`，逐文件披露）+ `retry_result.json` +
   `handoff.json`（`status=review_pending`、`implementer_signed=false`、不代签、不晋升）；
6. 边界自证：`iso/src`、`iso/scripts`、真仓全部锚点逐字节不变；
   `git -c core.quotepath=false diff HEAD --name-only` 非 `.planning` = 0。

## 4. 变异清单（红绿双向，为下一个有权会话预注册）

| 变异 | 改动（唯一被变异元素） | 预注册预期红 | 判别对象 |
|---|---|---|---|
| **M1**（冻结 §3.E 原样） | 导出公式退回写死 `0.5`（t0 探针与记录保留） | cpu8 下子进程②寿命 0.642–2.486 s > 0.5 ⇒ 被杀 ⇒ `child_started ≥ 3` ⇒ `assert … == 2` 红 | **下界**：H 必须盖住启动带宽上尾 |
| **M2-upper**（本文件新预注册） | 语义上界钳制 `t0 + 3.0` → `t0 + 10.0`（其余一字不改） | H ≥ t0+10 > t0+5 ⇒ 子进程①（count 落盘后睡 5 s 自净退）先于看门狗退出 ⇒ 事件缺 `child_unresponsive` ⇒ `next()` 抛 `StopIteration` ⇒ 红（墙钟 ≈ t0+5+ε < 15 s） | **上界**：钳制是节点语义必需（oracle §2.3），去掉必红 |

- 两个变异**各自只动一个元素**，把绿判据从两侧夹住：M1 证"太小必红"、M2-upper 证"太大必红"、
  绿证"公式本身恰好不红"。
- 派单"变异 ≥2"由 M1 + M2-upper 满足；冻结 §3.E 的可选 M2（`H=2.0` 只留地板）仍**不纳入**
  （概率性、无判别力，原文理由不变）。

## 5. 本 attempt 实际写入面（全部在 `.planning` 内本 attempt 目录）

```
harness/gate1_openprocess_probe.py          门 -1 探针
harness/gate1_ps_handle_probe.ps1           门 -1 PS 机制探针（由上者在运行时落盘）
evidence/gate-1-openprocess-raw.txt         门 -1 原始输出（逐字）
evidence/gate-1-openprocess-result.json     门 -1 结构化结果
before/freeze_instant.json                  本文件的冻结时刻与 sha256
oracle.md                                   本文件
retry_result.json                           门 -1 四步 + 施加/各臂未执行登记
handoff.json                                status=blocked、gate-1_unblocked=false 等
```

**未做/未写**：iso 未拷贝、venv 未拷贝、红/绿/M1/M2-upper 未运行、`changes.diff` 未产出
（真仓 `company-wiki/tests/**` 仍为未施加的原始字节 `32515aa6…005c1`，本 attempt 只读复核）、
产品仓零写入、无 git 写操作、未跑 `git status`（只用只读 `rev-parse`/`diff --name-only`）。
另登记一个上一轮的既有文书缺陷（本 attempt **不**回改上一轮任何字节）：
`a20260924-01/harness/tside_probe.py` 文档串引用的 `oracle-addendum-B.md` 实际不存在
（该轮只落了 addendum A 与 C）。

## 6. 解除条件（不变，指向 reviewer §8 S8-1/S8-2）

在一个其令牌能对**自生子进程** `OpenProcess(PROCESS_ALL_ACCESS)` 成功的会话（判据①），
或 PS `Start-Process … -RedirectStandard* -PassThru` 的 `.Handle` 非 null（判据②）——
即 owner/派工侧提供**真正另一宿主/权限环境**（父的提权会话已证可；本 DSH 子会话仍不可）。
该会话按 §3 步骤与 §4 变异清单执行即可；expected 无需重算（全部来自源卡原始数据）。
