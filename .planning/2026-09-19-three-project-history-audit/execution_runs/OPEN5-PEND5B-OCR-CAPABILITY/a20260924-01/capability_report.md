# OPEN5-PEND5B · OCR 能力落地报告（PEND-5b）

- **卡 / attempt**：`OPEN5-PEND5B-OCR-CAPABILITY` / `execution_runs/OPEN5-PEND5B-OCR-CAPABILITY/a20260924-01/`
- **角色**：`capability_landing`（能力落地工位）
- **授权**：`OWNER_DECISIONS.md` **§二十六（2026-09-24 深夜，原话逐字）第 2 行** —— owner 首答「**1，授权，2，要**」→ 父澄清提问 → owner 答「**两项都要（PEND-5b 装 + E1 交会计面）**」⇒ 本项 = **`PEND-5b` 装 OCR 引擎授权**（映射行原文见 `provenance.json` 条目 `auth-01`）
- **背景依据**：`execution_runs/I11A-OPEN5-ENVOWNER/a20260924-01/ruling.md` —— RC-1 根因（正文 CJK 字体无 `/ToUnicode`、内嵌 TrueType 无 `cmap`，5 个解析库同族乱码，**「换工具不是恢复路径」**）；恢复路径 **S2 明写「先 CN-ZIJIN 可读样本验证，再打 HK 探针」**
- **生成时间（UTC）**：2026-09-25T21:2x（本地实测窗口 2026-09-25T20:41–21:2xZ）
- **结论：`CAPABLE`**（判据见 §6/§7；锚词 0 命中不成立 —— 实测 5/5 锚词命中、origin 文字层同页 0 命中）

---

## 1. 后端选型：`rapidocr 3.9.2` + `onnxruntime 1.30.0`（CPU）+ `pypdfium2 5.13.0`

**选定**：纯 pip 可装、**模型随 wheel 内置、离线可用**的 OCR 栈（候选优先级 ① 纯 Python OCR）。

| 候选 | 判定 | 理由（实测/元数据） |
|---|---|---|
| **`rapidocr` 3.9.2**（选定） | ✅ | 纯 Python wheel（27,275,208 B），**PP-OCRv6 det/rec + cls 模型内置**（3 个 `.onnx`，31,749,509 B，装完即离线可用 —— 冒烟日志逐条 `File exists and is valid`，**零模型下载**）；`requires_python = <4,>=3.8` 含 3.13；CPU 推理走 onnxruntime |
| `rapidocr-onnxruntime` 1.4.4（派单举例的直选） | ❌ | PyPI 元数据 `requires_python = **<3.13**,>=3.6` —— 本机**唯一解释器是 3.13.9**，装不上（不是被否决，是不可用）；`rapidocr` 即其官方后继包 |
| `easyocr` | ❌ | 依赖 torch —— Windows 单件 wheel 体积即触 **>200 MB 登记线**，且离线体积大 |
| `paddleocr` / `paddlepaddle` | ❌ | 推理框架体积大、依赖面宽，同体积纪律下不选 |
| **tesseract 类（需系统二进制）** | ❌ **未装** | 依派单纪律：需系统级二进制的 ⇒ 不装（本项也不需要 —— 纯 pip 后端已跑通，故**不产生** `BLOCKED-NEEDS-SYSTEM-BINARY`） |
| 「换 PDF 解析库」 | ❌（背景已否决） | ruling.md 探针 C/E：PyMuPDF/pypdf/pdfminer/pypdfium2/pdftotext 5 库同族乱码 —— 文件内不存在码→Unicode 映射 |

**渲染器**：`pypdfium2 5.13.0`（3,885,553 B wheel，比 PyMuPDF 更小；ruling 探针 G 已证渲染通道本身完好，本次实测 44 页全部出图）。

## 2. 安装落点（硬纪律 1）

- **全部落点 = 本卡 attempt 内**：`venv/`（3,012 文件 / 277,906,824 B，含 `Lib/site-packages`）+ `_dl/`（下载件与回执）+ `_work/`、`_shim/`、`_tmp/`。
- **系统级改动 = 0**：未改 `PATH`、未装 Windows 包管理器包、未写全局 `C:\Miniconda` site-packages、未动系统 Python。
- **安装机制**：pip 的网络路径在本沙箱不可用（见 §4），改为 **urllib 下载 PEP427 wheel → 直接解包进 venv `site-packages`**（`_work/build_env.py`，自带 PEP503 索引解析 + 依赖闭包 BFS + `#sha256` 分段校验 + spec 严格校验）。23 个包（22 wheel + 1 sdist）、依赖闭包自解析、`verify all_ok=True`（全部 import 通过）。
- venv 自带 `pip 25.2`（ensurepip 经 shim 成功），**但安装未使用 pip**（仅留档可用性）。

## 3. 沙箱环境障碍与处置（如实登记）

| 障碍 | 实测 | 处置 |
|---|---|---|
| **`os.mkdir(0o700)`/`mkdtemp()` 建出不可写目录**（派单纪律 6，已复现） | `mkdtemp`、`mkdir 0o700` 在**计划目录与平台 TEMP 均** `[Errno 13]`；`mkdir 0o777` 正常 | `_shim/sitecustomize.py` 把 `os.mkdir` 模式强制 0o777，**仅经 `PYTHONPATH` 对指定进程生效**（进程内，不是系统级）；临时目录一律显式路径 |
| **pip 三次有界尝试全部失败**（硬试上限 3 次后弃用） | ① `pip --isolated download six`（无 shim）11.7s 即 `[Errno 13] pip-unpack-*\six...whl.metadata`；②③ 带 shim 的 `download rapidocr` 在 **`Getting page https://pypi.org/simple/...` 卡死**至 harness 超时（日志 `_dl/pip_dl2.log`、`_dl/pip_download.log` 末行为证）；早期另有一次 `pip download PyYAML` 180s 无果 | **换机制不换目标**：同网同主机 urllib 实测 200/0.14–0.36s ⇒ 改走 urllib+解包路线（一次成功）。pip 全部尝试与日志留档（`provenance.json` env-04..07） |
| **Windows MAX_PATH（260）** | 首轮安装在 `...onnxruntime\tools\ort_format_model\ort_flatbuffers_py\fbs\*.py`（**267 字符**）报 `FileNotFoundError`（Windows 超限症状） | 解包 IO 用 `\\?\` 扩展前缀 + 单文件失败不中断（实测 `extract_failure_count=0`） |
| **antlr4 版本约束无 wheel** | `omegaconf 2.3.1` 硬 pin `antlr4-python3-runtime==4.9.*`，而 PyPI 上 **4.9.x 只有 sdist 无 wheel**（wheel 自 4.11 起）；装 4.13.2 实测 `Could not deserialize ATN with version 3 (expected 4)` | 严格 spec（fail-closed，不放宽）→ **sdist 4.9.3 源码安装**（纯 Python，`src/antlr4/` 布局映射解包），先清旧版再装；`omegaconf` import 随之通过 |

## 4. 下载与网络（纪律 3）

- **选定下载合计 = 112,399,186 B（23 件：22 wheel + 1 sdist）**，逐件 URL / 取回 UTC / 字节 / sha256（与 PyPI `#sha256` 分段比对全通过）/ 用途 = `provenance.json` 条目 `dl-01..23`（汇总 `downloads_summary`）。
- **单件最大 = 44,000,345 B（opencv_python）**，**单件 >200 MB = 0 件**（无需体积预登记）。
- 额外透明登记：**弃用拣选 1 件** `antlr4_python3_runtime-4.13.2` 144,462 B（留盘未装，`dl-orphan-01`）；瞬态索引/元数据页（23 个 PEP503 索引 URL + 2 个 PyPI JSON，未留盘）；pip 诊断期取回 `six-1.17.0` wheel 11,050 B（落在 pip 临时目录，随临时目录消亡）。
- **模型下载 = 0**（3 个 onnx 随 wheel 内置）。

## 5. 自检（S2 门：先 CN-ZIJIN 可读样本）✅ 通过

- 样本：`company-wiki/companies/紫金矿业/raw/financial_reports/annual/2026-03-20_cninfo_1225023658_紫金矿业集团股份有限公司2025年年度报告.pdf`（79,925,886 B，`sha256=01819e1c7daad939…`，**只读**）
- 链路：**渲染第 1 页（200 dpi，3,218 ms）→ rapidocr OCR（7,169 ms，230 字符，均分 0.9964）→ 锚词**
- **锚词命中：`紫金` ✅（第 1 页）、`年度报告` ✅（第 1 页）、`收入` ✗（封面无此词，门要求 ≥1）⇒ 门通过**
- 交叉一致：同页 origin 文字层可读（236 字符），OCR 摘录与文字层内容一致（`紫金矿业集团股份有限公司…2025年年度报告…`）⇒ **链路在可读样本上等价于原文提取**
- **顺序纪律**：本门先于任何 HK 探针执行（`_work/cn_selfcheck.json` 时间戳早于全部 `hk_probe*.json`）

## 6. HK 探针（`HK-XIAOMI-AR2025`，只读）—— 锚词 5/5 命中

- 目标：`company-wiki/companies/小米集團－Ｗ/raw/financial_reports/annual/2026-04-28_hkexnews_12127452_2025年度報告.pdf`
- **4,405,561 B / `ffd733761633f464d90f6829e9b2d3e089f2dee7054b8ebfe91ef617f222da7c` / 415 页**（开测前 Get-FileHash 复核 = 派单值 ✓，全程只读）
- 4 轮共 **43 页**（10.36% 覆盖）：`1,2,30,40,44,46,47,48,49,50,53,55,56,57,59,60,65,67,68,71,72,88,90,112,115,118,124,135,140,160,200,242,243,272,275,277,325,337,355,356,395,399`（200 dpi）

| 锚词 | OCR 命中页数 | 命中页 |
|---|---|---|
| `小米` | **27** | 1,30,40,44,46,48,50,55,56,57,59,60,65,68,72,88,90,112,118,124,135,140,160,200,242,272,356 |
| `年度報告` | **22** | 1,2,43,47,49,53,55,57,59,65,67,71,115,135,243,275,277,325,337,355,395,399 |
| `收入` | **2** | 115, 337 |
| `分部` | **1** | 337 |
| `毛利` | **1** | 337 |
| **合计（锚词×页）** | **53** | — |

**对照（决定性）**：同样 43 页，**origin 文字层锚词命中合计 = 0**（`text_layer_anchor_hit_pages_union` 全空；正文文字层非空但为乱码，如 p337 文字层 1,014 字符、5 锚词全 False）。OCR 独有的 53 个命中页 vs origin 的 0 ⇒ **「正文不可读是字体问题、OCR 可绕」被实测证明**。

**抽样片段（`ocr_reconstruction`，非原文提取）**：

- **p337（分部附注，4 锚词一次全中）**：`合併財务报表附註 … 分部資料及收入（续）… 分部收入 186,439,777 / 123,200,191 / 37,440,346 / 4,136,860 / 351,217,174 / 106,069,513 / 457,286,687 … 銷售成本 (166,173,621)… 毛利/(虧損) 20,266,156 / 28,423,382 / 28,640,277 / (1,287,429) / 76,042,386 / 25,763,461 / 101,805,847`（分部收入与毛利数字行整体可读）
- **p115（ESG 重要性议题，`收入` 命中）**：`…在財務重要性方面…對收入、運營成本、資本開支、資產減值、供應鏈穩定性、合規成本及品牌價值的影響…`

## 7. 封面反证（派单第 4 条）

- **origin 文字层（封面 p1）**：35 字符 —— `2025\r\n股份代號：1810（港幣櫃台）及 81810（人民幣櫃台）`（ruling 记 PyMuPDF 取 36 字符，pypdfium2 计 35 —— 差 1 为末尾换行计法差异；封面**可见的** `小米集团`/`2025年度報告` 不在文字层里，因该字体 ToUnicode 只覆盖股份代號那一行）
- **OCR 链路（同页）**：`股份代號：1810（港幣櫃台）及81810（人民幣櫃台）\nMI\n小米集团\n(於開曼群島註冊成立以不同投票權控制的有限公司)\n2025年度報告` —— **读出与 origin 文字层相同的那一行**，并**多读出**文字层根本给不出的 `小米集团…2025年度報告`
- ⇒ **反证成立**：同一文件内「可读片段」OCR 复现一致 + 「不可读正文」OCR 读出而 origin 文字层 0 命中 ⇒ 正文乱码是字体映射问题，OCR 可绕开。
- 读不出的部分（如实）：封面 OCR 也有一处小误差（`及 81810` 的空格丢失；`小米集团` 被模型按简体字形输出 —— 见 §8）。

## 8. 能力边界（如实登记）

1. **性质**：全部产物标 `ocr_reconstruction` —— **图像→文本的重建，不是原文提取**；数字/版式/顺序可能与排版不完全一致，**永不冒充 origin 文本**（本报告全部引文均带此标）。
2. **准确度**：无 ground-truth 对照，**未做 WER/CER**；可报的是模型置信均分（43 页均值 **0.9807**，页间 0.92–0.99）与人工抽查：数字行（分部收入/毛利）逐位可读；已见误差类型 = **简繁混写**（`合併財务报表附註` 应为 `合併財務報表附註`）、**字形近似**（`IoT→loT`、`&→×A`）、封面 logo 字形按简体输出（`小米集团`）。
3. **速度（单线程 CPU，200 dpi）**：渲染均 219 ms/页（83–657）；OCR 均 **12,177 ms/页**（5,613–18,362）；43 页总墙钟 535.9 s。**全篇 415 页估算 ≈ 86 分钟**（未执行全篇，属成本边界）。
4. **覆盖**：**43/415 = 10.36%** 抽样页；`分部`/`毛利` 在抽样中各命中 1 页（p337）——锚词在全篇的**分布未穷举**，后续取证若需特定附注页，可先用「文字层数字密度」定位再定点 OCR（本次两轮定位法已验证有效）。
5. **失败页 = 0**：44 次渲染-OCR（43 HK + 1 CN）**零 `ocr_error`**、零渲染失败。
6. **繁体支持**：5 个锚词全部命中（含繁体 `年度報告`/`分部`/`毛利`），但简繁混写误差存在 ⇒ 引用前需人工核字。
7. **本能力只解锁「可读性路径的工具面」**：证据等级认定、新 attempt 取证（S3）、双路径复核（S4）、行业复裁+会计定级（S5）**均未做、不由本卡做**。

## 9. git / 写入面（纪律 2、5）

- `git diff HEAD`（仓库根，`core.quotepath=false`）：**总计 3,826 条，非 `.planning` = 0**；untracked 非 `.planning` = 50 条，前缀 `.tmp-r41-mutation / assurance / h2.log / h2.log.err / probe_root_m777*` **全部为既有路径，本卡 0 条**。
- `company-wiki` 仓 3 个改动文件（`CLAUDE.md`/`README.md`/`src/.../artifact_dag.py`）mtime 均为 **2026-09-23 13:08:38**（早于本卡会话）⇒ **非本卡所为**；本卡对产品仓**只读**（两份源 PDF 仅 Get-FileHash/解析）。
- **零 git 写**：未执行 `add/commit/checkout/stash/reset/restore` 任何变体。
- **写入面 = 仅本 attempt 目录**：3,104 文件 / 410,325,718 B（venv 277.9 MB、_dl 112.6 MB、_work 19.8 MB 含 44 张渲染 PNG 19,572,165 B —— 每张 sha256 记于 `hk_probe*.json`/`cn_selfcheck.json`）。
- **JSON 写后重解析通过、UTF-8 无 BOM、纯 LF**（`provenance.json`、`handoff.json`、全部 probe/aggregate 产物）。

## 10. 结论

> **`CAPABLE`** —— 本计划在**本卡隔离 venv 内**获得了对「字体无 ToUnicode/cmap」类 PDF 的 OCR 读取能力：自检门（CN-ZIJIN 第 1 页锚词）通过后，对 `HK-XIAOMI-AR2025` 43 页探针 **5/5 锚词命中（53 个锚词×页）**，**同页 origin 文字层命中 = 0**，封面反证成立，零失败页。安装只落本卡 venv、零系统级改动、单件下载均 <200 MB、全部 sha256 校验通过。

**本卡没有做**（边界声明）：未系统级安装（无 PATH/Windows 包/全局 site-packages 改动）· 未写任何产品仓（`company-wiki`/`filing-fetch`/`revenue-forecast` 非 `.planning` 写入 = 0）· 未解除 `OPEN-5`、未解锁 `I-11-B`/`I-07-B`、未产生 ACCEPT/STATUS 变更 · **未把 OCR 输出当一手披露**（全部标 `ocr_reconstruction`）· 未做 S3 新 attempt 取证 / S4 双路径复核 / S5 定级（归编排层与专业 reviewer）· 未穷举全篇 415 页。

**产物**：`venv/` · `provenance.json`（49 条）· `capability_report.md`（本文件）· `handoff.json` · `_work/{build_env.py,probe_ocr.py,aggregate.py,make_provenance.py,cn_selfcheck.json,hk_probe*.json,hk_probe_aggregate.json}` · `_dl/{build_receipts.json,install_report.json,verify.json,build_env.log,pip_*.log}` · `_shim/sitecustomize.py`
