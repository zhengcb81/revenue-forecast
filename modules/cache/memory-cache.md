# 缓存管理逻辑

## 核心功能

本模块提供缓存的读取、写入、时间戳检查、搜索策略决策等核心功能。

## 导入依赖

```python
import json
import os
from datetime import datetime, timedelta
import re
from pathlib import Path
```

## 1. 初始化缓存系统

### 创建基础缓存目录
```python
def init_cache_system():
    """
    初始化整个缓存系统

    Returns:
        cache_base_dir: 缓存根目录路径
    """
    cache_base_dir = "revenue-forecast-cache"

    # 创建主目录
    os.makedirs(cache_base_dir, exist_ok=True)

    print(f"✅ 缓存系统已初始化: {os.path.abspath(cache_base_dir)}")
    return cache_base_dir
```

### 初始化公司缓存
```python
def init_company_cache(company_name):
    """
    初始化公司缓存目录和metadata.json

    Args:
        company_name: 公司名称

    Returns:
        company_cache_dir: 公司缓存目录路径
    """
    from modules.cache.cache_structure import sanitize_company_name

    cache_base_dir = init_cache_system()
    company_dir = sanitize_company_name(company_name)
    company_cache_dir = os.path.join(cache_base_dir, company_dir)

    # 创建目录
    os.makedirs(company_cache_dir, exist_ok=True)
    os.makedirs(os.path.join(company_cache_dir, "search-results"), exist_ok=True)

    # 检查metadata.json是否已存在
    metadata_path = os.path.join(company_cache_dir, "metadata.json")

    if os.path.exists(metadata_path):
        print(f"ℹ️ 公司缓存已存在: {company_cache_dir}")
        return company_cache_dir

    # 创建初始metadata.json
    metadata = {
        "company_name": company_name,
        "sanitized_name": company_dir,
        "company_type": "unknown",
        "type_confidence": 0.0,
        "first_analysis_date": datetime.now().strftime("%Y-%m-%d"),
        "last_analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "analysis_count": 0,
        "cache_version": "v2.1.0",
        "dimension_cache_status": {},
        "search_keywords_history": {}
    }

    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"✅ 公司缓存目录已创建: {company_cache_dir}")
    return company_cache_dir
```

## 2. 缓存文件路径管理

### 获取缓存文件路径
```python
def get_cache_file_path(company_name, dimension):
    """
    获取维度缓存文件路径

    Args:
        company_name: 公司名称
        dimension: 研究维度名称

    Returns:
        file_path: 缓存文件完整路径
    """
    from modules.cache.cache_structure import sanitize_company_name

    cache_base_dir = "revenue-forecast-cache"
    company_dir = sanitize_company_name(company_name)
    return os.path.join(cache_base_dir, company_dir, f"{dimension}.md")
```

### 获取metadata.json路径
```python
def get_metadata_path(company_name):
    """
    获取metadata.json文件路径

    Args:
        company_name: 公司名称

    Returns:
        metadata_path: metadata.json完整路径
    """
    from modules.cache.cache_structure import sanitize_company_name

    cache_base_dir = "revenue-forecast-cache"
    company_dir = sanitize_company_name(company_name)
    return os.path.join(cache_base_dir, company_dir, "metadata.json")
```

## 3. 时间戳检查逻辑

### 核心检查函数
```python
def check_cache_freshness(company_name, dimension):
    """
    检查缓存新鲜度

    Args:
        company_name: 公司名称
        dimension: 研究维度名称

    Returns:
        dict: {
            "status": "fresh" | "stale" | "outdated" | "not_exists",
            "last_updated": datetime object (or None),
            "days_diff": float,
            "hours_diff": float,
            "reason": str,
            "recommendation": str
        }
    """
    cache_path = get_cache_file_path(company_name, dimension)

    # 检查文件是否存在
    if not os.path.exists(cache_path):
        return {
            "status": "not_exists",
            "last_updated": None,
            "days_diff": float('inf'),
            "hours_diff": float('inf'),
            "reason": "缓存文件不存在",
            "recommendation": "需要全新搜索（6-10次）"
        }

    # 读取文件并解析时间戳
    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()

            # 解析**缓存时间**：格式
            if first_line.startswith("**缓存时间**"):
                timestamp_str = first_line.split("：**")[1].strip()
                try:
                    last_updated = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    # 如果解析失败，使用文件修改时间
                    last_updated = datetime.fromtimestamp(os.path.getmtime(cache_path))
            else:
                # 如果第一行不是时间戳，使用文件修改时间
                last_updated = datetime.fromtimestamp(os.path.getmtime(cache_path))

    except Exception as e:
        print(f"⚠️ 读取缓存文件失败: {e}")
        return {
            "status": "not_exists",
            "last_updated": None,
            "days_diff": float('inf'),
            "hours_diff": float('inf'),
            "reason": "文件读取错误",
            "recommendation": "需要全新搜索"
        }

    return calculate_cache_status(last_updated)
```

### 计算缓存状态
```python
def calculate_cache_status(last_updated):
    """
    根据最后更新时间计算缓存状态

    Args:
        last_updated: 最后更新时间(datetime对象)

    Returns:
        dict: 缓存状态信息
    """
    current_time = datetime.now()
    time_diff = current_time - last_updated
    days_diff = time_diff.total_seconds() / 86400  # 转换为天数
    hours_diff = time_diff.total_seconds() / 3600  # 转换为小时

    # 判断新鲜度
    if days_diff < 1:
        status = "fresh"
        reason = f"很新鲜（{int(hours_diff)}小时前更新）"
        recommendation = "完全复用缓存（不搜索）"
    elif days_diff < 7:
        status = "fresh"
        reason = f"新鲜（{int(days_diff)}天前更新）"
        recommendation = "复用为主，1-2次验证搜索"
    elif days_diff < 30:
        status = "stale"
        reason = f"较陈旧（{int(days_diff)}天前更新）"
        recommendation = "缓存+更新，3-5次补充搜索"
    else:
        status = "outdated"
        reason = f"已过期（{int(days_diff)}天前更新）"
        recommendation = "参考缓存，全新搜索（6-10次）"

    return {
        "status": status,
        "last_updated": last_updated,
        "days_diff": days_diff,
        "hours_diff": hours_diff,
        "reason": reason,
        "recommendation": recommendation
    }
```

## 4. 搜索策略决策

### 基于缓存状态推荐搜索策略
```python
def get_search_strategy(company_name, dimension):
    """
    获取搜索策略

    Args:
        company_name: 公司名称
        dimension: 研究维度名称

    Returns:
        dict: {
            "search_count": int,
            "use_cache": bool,
            "cache_mode": str,
            "search_intensity": str,
            "description": str
        }
    """
    freshness = check_cache_freshness(company_name, dimension)

    strategies = {
        "not_exists": {
            "search_count": 8,
            "use_cache": False,
            "cache_mode": "none",
            "search_intensity": "high",
            "description": "全新搜索（8次，全面搜集信息）"
        },
        "outdated": {
            "search_count": 6,
            "use_cache": True,
            "cache_mode": "reference",
            "search_intensity": "high",
            "description": "参考旧缓存，全新搜索（6次）"
        },
        "stale": {
            "search_count": 4,
            "use_cache": True,
            "cache_mode": "base",
            "search_intensity": "medium",
            "description": "缓存为基础，中等更新（4次）"
        },
        "fresh": {
            "search_count": 1,
            "use_cache": True,
            "cache_mode": "primary",
            "search_intensity": "low",
            "description": "复用为主，少量验证（1次）"
        }
    }

    strategy = strategies[freshness["status"]]
    strategy["freshness_info"] = freshness

    return strategy
```

### 根据维度重要性调整搜索强度
```python
def adjust_search_count_by_importance(base_strategy, dimension_importance):
    """
    根据维度重要性调整搜索次数

    Args:
        base_strategy: 基础搜索策略
        dimension_importance: 维度重要性（"high"/"medium"/"low"）

    Returns:
        adjusted_strategy: 调整后的搜索策略
    """
    search_count = base_strategy["search_count"]
    importance_multiplier = {
        "high": 1.5,
        "medium": 1.0,
        "low": 0.75
    }

    adjusted_search_count = int(search_count * importance_multiplier[dimension_importance])
    adjusted_search_count = max(adjusted_search_count, 1)  # 至少1次

    base_strategy["search_count"] = adjusted_search_count
    base_strategy["description"] = f"{base_strategy['description'].split('（')[0]}（调整：重要度={dimension_importance} => {adjusted_search_count}次）"

    return base_strategy
```

## 5. 缓存数据写入

### 创建新的缓存文件
```python
def create_cache_file(company_name, dimension, analysis_content, search_count):
    """
    创建新的缓存文件

    Args:
        company_name: 公司名称
        dimension: 研究维度名称
        analysis_content: 分析内容（字符串）
        search_count: 使用数据源数量

    Returns:
        cache_path: 缓存文件路径
        file_size: 文件大小
    """
    # 获取缓存路径
    cache_path = get_cache_file_path(company_name, dimension)

    # 构建完整文件内容
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    next_update = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

    file_content = f"""# {dimension}

**缓存时间**：{current_time}
**数据来源**：web_search × {search_count}次
**下次更新建议**：{next_update}（7天后）
**分析员**：Claude AI

---

{analysis_content}

---

**生成时间**：{current_time}
**缓存版本**：v2.1.0
"""

    # 写入文件
    with open(cache_path, 'w', encoding='utf-8') as f:
        f.write(file_content)

    file_size = os.path.getsize(cache_path)
    print(f"✅ 缓存文件已更新: {cache_path}")

    return cache_path, file_size
```

### 更新metadata.json
```python
def update_metadata(company_name, dimension, search_count, file_size):
    """
    更新metadata.json中的维度状态

    Args:
        company_name: 公司名称
        dimension: 研究维度名称
        search_count: 使用数据源数量
        file_size: 缓存文件大小（字节）

    Returns:
        bool: 是否成功更新
    """
    metadata_path = get_metadata_path(company_name)

    # 读取现有metadata
    try:
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
    except Exception as e:
        print(f"⚠️ 读取metadata.json失败: {e}")
        return False

    # 更新维度状态
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 检查新鲜度并设置状态
    days_diff = check_cache_freshness(company_name, dimension)["days_diff"]
    if days_diff < 7:
        cache_status = "fresh"
    elif days_diff < 30:
        cache_status = "stale"
    else:
        cache_status = "outdated"

    metadata["dimension_cache_status"][dimension] = {
        "last_updated": current_time,
        "cache_status": cache_status,
        "source_count": search_count,
        "file_size": file_size
    }

    # 更新分析次数和最后时间
    metadata["analysis_count"] += 1
    metadata["last_analysis_date"] = current_time

    # 保存回文件
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"✅ metadata.json已更新: {metadata_path}")
    return True
```

## 6. 缓存数据读取

### 读取缓存文件内容
```python
def read_cache_content(company_name, dimension):
    """
    读取缓存文件内容

    Args:
        company_name: 公司名称
        dimension: 研究维度名称

    Returns:
        dict: {
            "content": str,
            "timestamp": datetime,
            "source_count": int
        }
    """
    cache_path = get_cache_file_path(company_name, dimension)

    if not os.path.exists(cache_path):
        return None

    with open(cache_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 解析时间戳
    first_line = content.split('\n')[0]
    timestamp_str = first_line.split("：**")[1].strip()

    try:
        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        timestamp = datetime.fromtimestamp(os.path.getmtime(cache_path))

    return {
        "content": content,
        "timestamp": timestamp,
        "source_count": extract_source_count(content)
    }
```

### 从内容中提取元数据
```python
def extract_source_count(cache_content):
    """
    从缓存内容中提取数据源数量

    Args:
        cache_content: 缓存内容字符串

    Returns:
        int: 数据源数量
    """
    match = re.search(r'web_search × (\d+)次', cache_content)
    if match:
        return int(match.group(1))
    return 0

def extract_cache_timestamp(cache_content):
    """
    从缓存内容中提取时间戳

    Args:
        cache_content: 缓存内容字符串

    Returns:
        datetime: 时间戳，解析失败返回None
    """
    first_line = cache_content.split('\n')[0]
    if first_line.startswith("**缓存时间**"):
        timestamp_str = first_line.split("：**")[1].strip()
        try:
            return datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            pass
    return None
```

## 7. 缓存清理与维护

### 清理过期缓存（可选）
```python
def cleanup_outdated_cache(days_threshold=60):
    """
    清理长期未更新的缓存（手动调用）

    Args:
        days_threshold: 天数阈值（默认60天）

    Returns:
        deleted_count: 清理的缓存文件数量
    """
    cache_base_dir = "revenue-forecast-cache"

    if not os.path.exists(cache_base_dir):
        return 0

    deleted_count = 0
    current_time = datetime.now()

    # 遍历所有公司目录
    for company_dir in os.listdir(cache_base_dir):
        company_path = os.path.join(cache_base_dir, company_dir)

        # 检查是否为目录
        if not os.path.isdir(company_path):
            continue

        # 读取metadata.json
        metadata_path = os.path.join(company_path, "metadata.json")
        if not os.path.exists(metadata_path):
            continue

        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)

            last_analysis = datetime.strptime(metadata["last_analysis_date"], "%Y-%m-%d %H:%M:%S")
            days_diff = (current_time - last_analysis).days

            # 如果超过阈值，标记为可删除
            if days_diff > days_threshold:
                print(f"🗑️ 公司缓存过期: {company_dir} (最近分析: {days_diff}天前)")
                deleted_count += 1

        except Exception as e:
            print(f"⚠️ 读取metadata失败: {e}")

    print(f"ℹ️ 共发现 {deleted_count} 个过期缓存（阈值: {days_threshold}天）")
    return deleted_count
```

## 8. 调试与日志

### 启用详细日志
```python
import logging

def setup_cache_logging(level=logging.INFO):
    """
    设置缓存系统日志

    Args:
        level: 日志级别
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger = logging.getLogger("cache_manager")
    return logger
```

### 缓存统计信息
```python
def get_cache_statistics():
    """
    获取缓存统计信息

    Returns:
        dict: 统计信息
    """
    cache_base_dir = "revenue-forecast-cache"

    if not os.path.exists(cache_base_dir):
        return {"total_companies": 0, "total_files": 0, "total_size": 0}

    total_companies = 0
    total_files = 0
    total_size = 0

    # 遍历所有公司目录
    for company_dir in os.listdir(cache_base_dir):
        company_path = os.path.join(cache_base_dir, company_dir)

        if not os.path.isdir(company_path):
            continue

        total_companies += 1

        # 计算该目录文件
        for root, dirs, files in os.walk(company_path):
            for file in files:
                if file.endswith('.md') or file.endswith('.json'):
                    total_files += 1
                    file_path = os.path.join(root, file)
                    total_size += os.path.getsize(file_path)

    return {
        "total_companies": total_companies,
        "total_files": total_files,
        "total_size_bytes": total_size,
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "avg_per_company": round(total_size / (1024 * 1024) / max(total_companies, 1), 2)
    }
```

---

## 9. 验证检查点 ⭐⭐⭐ 强制执行

**重要**: 完成缓存系统初始化后,必须执行验证检查点!

### 验证检查点: CP-1, CP-2, CP-3

**验证器位置**: `core/validators/cache_validator.py`

**使用方法**:

#### 方法1: Python代码调用

```python
# 导入验证器
import sys
sys.path.append("core/validators")
from cache_validator import validate_cache_setup

# 执行验证
company_name = "宝马集团"
success, data = validate_cache_setup(company_name)

if success:
    print("✅ 缓存系统验证通过,可以继续下一步")
    metadata = data["metadata"]
    search_results_dir = data["search_results_dir"]
else:
    print("❌ 缓存系统验证失败,请修正错误后重试")
    sys.exit(1)
```

#### 方法2: 命令行调用

```bash
# 切换到工作目录
cd /path/to/your/project

# 执行验证
python core/validators/cache_validator.py 宝马集团

# 预期输出(成功时):
# ============================================================
# 🔍 缓存系统验证检查点
# ============================================================
# 📍 CP-1: 缓存路径验证
#   ✅ 根目录: /path/to/revenue-forecast-cache
#   ✅ 公司目录: /path/to/revenue-forecast-cache/宝马集团
# ✅ CP-1验证通过: 缓存路径正确
#
# 📍 CP-2: metadata.json验证
#   ✅ 文件存在: revenue-forecast-cache/宝马集团/metadata.json
#   ✅ JSON格式有效
#   ✅ 必需字段完整: 5个
# ✅ CP-2验证通过: metadata.json完整有效
#
# 📍 CP-3: search-results/目录验证
#   ✅ 目录存在: revenue-forecast-cache/宝马集团/search-results
# ✅ CP-3验证通过: search-results/目录存在
#
# ============================================================
# ✅ 所有缓存检查点通过 (CP-1, CP-2, CP-3)
# ============================================================
```

### 验证检查点说明

#### CP-1: 缓存路径正确性验证 🔴 致命

**验证标准**:
- ✅ 根目录必须是: `revenue-forecast-cache/`
- ✅ 公司目录必须是: `revenue-forecast-cache/{公司名}/`
- ❌ 禁止使用: `cache/`, `.cache/`, `tmp/cache/` 等其他路径

**失败后果**: 禁止继续分析

#### CP-2: metadata.json存在性验证 🔴 致命

**验证标准**:
- ✅ `metadata.json` 必须存在
- ✅ JSON格式必须有效
- ✅ 必须包含字段: `company_name`, `created_at`, `last_analyzed`, `analysis_count`, `cache_status`

**失败后果**: 禁止继续分析

#### CP-3: search-results/目录验证 🟡 警告

**验证标准**:
- ✅ `search-results/` 子目录必须存在
- ✅ 路径: `revenue-forecast-cache/{公司名}/search-results/`

**失败后果**: 警告但可继续,系统会自动创建

### 强制执行要求

**⚠️ 重要**: 完成第一步"初始化缓存系统"后,必须执行验证检查点!

```python
# 正确的执行流程
# 步骤1: 初始化缓存
cache_dir, metadata = init_company_cache("宝马集团")

# 步骤2: 验证检查点(必须执行!)
success, data = validate_cache_setup("宝马集团")
if not success:
    raise Exception("❌ 缓存验证失败,停止执行!")

# 步骤3: 继续后续步骤
...
```

---

**验证检查点版本**: v1.0
**验证器文件**: core/validators/cache_validator.py
**最后更新**: 2026-01-13
