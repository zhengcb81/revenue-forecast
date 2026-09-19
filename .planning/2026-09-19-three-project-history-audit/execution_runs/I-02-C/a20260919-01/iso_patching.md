# iso_patching — 隔离环境与实施范围记录（I-02-C / a20260919-01）

1. **依赖**：`yaml`（PyYAML）+ `requests/urllib3/idna/certifi/charset_normalizer` 从 I-02-A
   attempt 的 `iso/venv/Lib/site-packages` **离线复制**（无 pip、无网络）。运行时仅出现
   `RequestsDependencyWarning`（stderr），不参与业务判定。

2. **override 结构**：`scripts/w02c_bootstrap.py` 沿用 I-01-A/I-02-A 同一合成 package 手法
   （`company_wiki` / `source_catalog` / `adapters` 的 `__path__` 指只读 CW 仓库 src）。
   预注册：
   - D-W02 契约链（I-02-A 冻结并在该用零差异的副本）：`models.py`（I-02-A override 副本，
     含 ScanReport completion/target 契约）、`scanner.py`（I-02-A）、`service.py`（I-02-A）、
     `config.py` / `adapter_dispatch.py` / `config_doctor.py`（I-01-A/I-02-A 链）；
   - 本卡 4 个允许修改文件：`canonical_writer.py`（基线 = I-02-A 的 override 副本，含四道门）、
     `acquisition_service.py` / `acquisition_journal.py` / `cli.py`（基线 = 生产原件，逐字节）；
   其余未修改文件（resolver/store/policy/lock/prompt_injection 等）按需从只读 src 懒加载，
   与 I-02-A 已验收 bootstrap 相同。`canonical_writer` 必须先于 `acquisition_service` 注册，
   以避免包相对导入第二实例（见 decision.md 契约延续；setup 幂等标记防止 runner 二次注册造
   成 class identity 分裂）。

3. **Windows MAX_PATH**：case 树放在短物理路径 `%TEMP%/w02c/a20260919-01_case_scratch/<case>`，
   运行结束把全部 case 树复制回 `after/case_scratch_retained/`（sqlite journal 除外）。
   `samples/real_roots` 在 attempt 树内平铺放置 attempt 环境（US 文件原子树布局会超
   MAX_PATH）；完整生产子树布局在 case 树内复现。

4. **来源事实（不迁移不改写）**：两个生产原件+sidecar 以 byte-identical 复制进
   `samples/real_roots/{hk,us}/`；sidecar 的历史 `receipt.staged_path`（生产 staging 历史
   路径）原样保留；register-existing 校验的是**现行** raw 路径的字节（manifest 显式提供），
   不要求历史 staged_path 存在。

5. **注入边界**：deny-on-call provider stub、retire/quarantine 注入、sidecar 损坏等全部在
   `scripts/w02c_cases.py` / `w02c_cli_probe.py`（harness 侧）；4 个 override 产品副本不含
   任何 harness/fake 代码。P1/P2 走真实 scanner+resolver+writer+store+journal，仅
   provider 适配器由 harness 桩替代并在每次运行清零计数。

6. **同 bytes 复制纪律**：`env.place_sample` 每次复制后断言 sha256+size == 卡固定值；
   `hashlib.sha256` 由 runner 重算（非复用 trust 标注）。N1b 的篡改字节插入后文件保
   持篡改态（不自愈），catalog 无目标行。

7. **cli 入口**：`ensure --register-existing --recovery-manifest`（新增两个 flag；不新增
   子命令）。与 `--allow-download` 互斥；不走 paused-acquisition 审计路径；provider registry
   为 `cli._no_provider_registry()`（deny-on-call）。验证经 `scripts/w02c_cli_probe.py`
   用真实 `cli.main(argv)` 完成（rc=0、status=registered_existing、raw bytes 不变）。
