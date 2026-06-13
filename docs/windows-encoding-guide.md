# Windows UTF-8 编码问题指南 v1.0

> 创建日期: 2026-06-13
> 适用范围: Windows 上运行 revenue-forecast skill 的所有 Python 脚本
> 关联模块: `core/encoding.py`

---

## 一、问题根源

Windows 默认 locale 为简体中文，导致：

```
locale.getpreferredencoding() = cp936
sys.stdout.encoding            = gbk
```

当 Python 脚本以 UTF-8 写入中文字符串、但终端以 GBK 解码输出时，就会出现 `??` 或乱码。最典型的触发场景是 `python << EOF ... EOF`（heredoc）内联脚本。

---

## 二、三种解决方案（按推荐顺序）

### 方案 1（推荐）: 使用 `core/encoding.py`

所有 revenue-forecast 自带脚本（`validate_report.py`、`validate_steps.py`、`init_cache.py`、`verify_config.py`、`core/*.py`、`core/validators/*.py`）在 v2.6.0 起已在入口处统一调用：

```python
from core.encoding import setup_utf8_console
setup_utf8_console()
```

无需额外操作。

### 方案 2: 在 shell 会话中导出环境变量

**Git Bash**:
```bash
export PYTHONIOENCODING=utf-8
export PYTHONUTF8=1
```

**PowerShell**:
```powershell
$env:PYTHONIOENCODING="utf-8"
$env:PYTHONUTF8="1"
```

**CMD**:
```cmd
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
```

### 方案 3: 在 heredoc 首行手动设置

```python
python << 'EOF'
import sys, io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
print("中文输出测试")
EOF
```

---

## 三、验证方法

运行以下命令，若中文正常显示（无 `??`），则编码已修复：

```bash
python << 'EOF'
import sys, os
sys.path.insert(0, r"C:\Users\郑曾波\.claude\skills\revenue-forecast")
from core.encoding import setup_utf8_console
setup_utf8_console()
print("中文测试: 微软营收增长预测分析")
print("数字测试: 复合年增长率 = 11.4%")
EOF
```

**预期输出**:
```
中文测试: 微软营收增长预测分析
数字测试: 复合年增长率 = 11.4%
```

---

## 四、已修复的文件清单（v2.6.0）

| 文件 | 修复方式 |
|------|---------|
| `core/encoding.py` | 新增统一引导模块 |
| `validate_report.py` | 头部调用 `setup_utf8_console()` |
| `validate_steps.py` | 头部调用 `setup_utf8_console()` |
| `init_cache.py` | 头部调用 `setup_utf8_console()` |
| `verify_config.py` | 头部调用 `setup_utf8_console()` |
| `core/*.py` (14 个) | 头部 try/except 调用 |
| `core/validators/*.py` (8 个) | 头部 try/except 调用 |

---

## 五、常见问题

**Q: 为什么 core/*.py 用 try/except 包裹编码调用？**

A: 这些是库模块，可能被外部代码 `import` 使用。如果外部环境路径未配置导致 `core.encoding` 无法导入，try/except 保证模块加载不会失败——此时输出编码由调用方（入口脚本）已设置的 UTF-8 决定。

**Q: 在 Linux/macOS 上需要这些设置吗？**

A: 不需要。`setup_utf8_console()` 在非 Windows 平台仅调用 `reconfigure(encoding='utf-8')`，多数发行版默认就是 UTF-8，调用是无害的 no-op。

**Q: 如何永久设置环境变量？**

A: PowerShell 永久设置：
```powershell
[Environment]::SetEnvironmentVariable("PYTHONUTF8", "1", "User")
[Environment]::SetEnvironmentVariable("PYTHONIOENCODING", "utf-8", "User")
```
