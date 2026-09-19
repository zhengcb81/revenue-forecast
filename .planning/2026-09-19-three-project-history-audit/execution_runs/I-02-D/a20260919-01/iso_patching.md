# iso_patching — 隔离环境与实施范围记录（I-02-D / a20260919-01）

1. **依赖**：`yaml` + `requests/urllib3/idna/certifi/charset_normalizer` 从 I-02-C attempt 的
   `iso/venv/Lib/site-packages` **离线复制**（无 pip、无网络）。运行时仅出现
   `RequestsDependencyWarning`（stderr），不参与业务判定。

2. **override 结构**：`scripts/w02d_bootstrap.py` 沿用 I-01-A/I-02-A/I-02-C 同一合成
   package 手法（`company_wiki`/`source_catalog`/`adapters` 的 `__path__` 指只读 CW 仓库
   src）。预注册：
   - D-W02 契约链（I-02-A 冻结副本）：`models.py`/`scanner.py`/`service.py`/`config.py`/
     `adapter_dispatch.py`/`config_doctor.py`；
   - I-02-C 已冻结副本（本卡零差异继承）：`canonical_writer.py`（R1-R7 门 + 四道门）、
     `acquisition_service.py`（SourceRecoveryInput 恢复分支）、`acquisition_journal.py`
     （registered_existing_raw outcome）、`cli.py`（ensure --register-existing 接线）；
   - **本卡 3 个允许修改文件中唯一实际改动**：`canonical_writer.py` import_staged dedup
     分支（dedup 资格检查 + staging 清理时点，见 changes.diff Part 2）；
     `acquisition_service.py` / `acquisition_journal.py` 本卡**零差异**（逐字节 == I-02-C
     副本，presence 记录在 changes.diff Part 2 空段）。
   其余未修改文件（resolver/store/policy/lock/prompt_injection 等）按需从只读 src 懒加载。
   `canonical_writer` 先于 `acquisition_service` 注册；setup 幂等标记防止二次注册造成
   class identity 分裂。

3. **Windows MAX_PATH**：case 树放短物理路径 `%TEMP%/w02d/a20260919-01_case_scratch/<case>`。
   retained 快照只复制 case 的 sqlite（catalog.sqlite3，journal 除外）与顶层状态，不复制
   深层 raw 子树（首次整树复制触发 WinError 3 MAX_PATH；raw hash 已逐 call 记录在
   idempotency-matrix.json）。

4. **P2 两进程**：`scripts/w02d_worker.py` 为独立真实进程（subprocess.Popen，非线程/非
   multiprocessing 同进程）；文件轮询 barrier（`ready.<pid>` 两进程互等）；对**同一**
   scratch catalog 并发 ensure(request, recovery)。stdout/stderr 由父进程捕获入
   `raw-cli-logs/worker*.log`，结果 JSON 入 `raw-cli-logs/worker*.result.json`，完整
   trace 入 `after/two-process-trace.json`。失败只停本卡启动的 scratch 进程。

5. **注入边界**：deny-on-call provider stub、N2a 新 hash 变体（staging 内 flip 第 16 字节
   + receipt 重算）、N3b retire 注入等全部在 harness（`scripts/w02d_cases.py`/
   `w02d_worker.py`）；override 产品副本不含任何 harness/fake 代码。

6. **同 bytes 复制纪律**：`env.place_sample` 每次复制后断言 sha256+size == 卡固定值；
   `hashlib.sha256` 由 runner 重算（非复用 trust 标注）。

7. **oracle 独立 SQL**：`env.sql_state()` 直接 `sqlite3.connect(db_path)` 数
   sources/documents/locations 行（不经被测 store API）；journal 行经
   `AcquisitionJournal.read_all()`（校验无损坏尾行）。
