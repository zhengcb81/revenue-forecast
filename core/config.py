"""
配置加载模块 - 从 YAML 文件读取配置
提供统一的配置访问接口，避免硬编码
版本: v2.5.0
"""

# v2.6.0 统一 UTF-8 编码引导（避免 Windows cp936/gbk 中文乱码）
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
try:
    from core.encoding import setup_utf8_console as _setup_utf8_console
    _setup_utf8_console()
except Exception:
    pass

import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

_config: Optional[Dict[str, Any]] = None


def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    加载配置文件，支持自定义路径

    Args:
        config_path: 配置文件路径，默认为同目录下的 config.yaml

    Returns:
        配置字典
    """
    global _config
    if _config is None:
        if config_path is None:
            config_path = Path(__file__).parent / "config.yaml"
        with open(config_path, "r", encoding="utf-8") as f:
            _config = yaml.safe_load(f)
    return _config


def reload_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    强制重新加载配置文件

    Args:
        config_path: 配置文件路径

    Returns:
        配置字典
    """
    global _config
    _config = None
    return load_config(config_path)


def get_version() -> str:
    """获取框架版本号"""
    return load_config().get("version", "0.0.0")


# ============ 目录路径函数 ============


def get_cache_base_dir() -> str:
    """
    获取缓存根目录

    Returns:
        缓存根目录路径（相对路径）
    """
    return load_config()["directories"].get("cache_base_dir", "revenue-forecast-cache")


def get_output_dir() -> str:
    """
    获取输出目录

    Returns:
        输出目录路径（相对路径）
    """
    return load_config()["directories"].get("output_dir", "outputs")


def get_search_results_subdir() -> str:
    """
    获取搜索结果子目录名

    Returns:
        子目录名称
    """
    return load_config()["directories"].get("search_results_subdir", "search-results")


def get_templates_dir() -> str:
    """
    获取模板目录

    Returns:
        模板目录路径
    """
    return load_config()["directories"].get("templates_dir", "modules/templates")


def get_path(key: str) -> str:
    """
    获取路径配置（兼容旧接口）

    Args:
        key: 路径键名，如 'cache_base_dir', 'output_dir'

    Returns:
        路径字符串
    """
    return load_config()["paths"].get(key, "")


def get_all_paths() -> Dict[str, str]:
    """
    获取所有路径配置

    Returns:
        路径配置字典
    """
    return load_config().get("paths", {})


# ============ 维度文件函数 ============


def get_dimension_files(company_type: str = "default") -> List[str]:
    """
    获取指定公司类型的维度文件名列表

    Args:
        company_type: 公司类型标识

    Returns:
        维度文件名列表
    """
    config = load_config()
    dimension_files = config.get("dimension_files", {})

    # 如果指定类型不存在，使用默认
    if company_type not in dimension_files:
        company_type = "default"

    files = dimension_files.get(company_type)

    # 如果为null，使用默认
    if files is None:
        files = dimension_files.get("default", [])

    return files


def get_dimension_count(company_type: str = "default") -> int:
    """
    获取指定公司类型的维度文件数量

    Args:
        company_type: 公司类型标识

    Returns:
        维度文件数量
    """
    return len(get_dimension_files(company_type))


def get_brand_matrix_filename() -> str:
    """
    获取品牌矩阵文件名

    Returns:
        品牌矩阵文件名
    """
    return load_config()["search_results"].get(
        "brand_matrix_filename", "dimension-10-brand-matrix.md"
    )


def is_product_driven(company_type: str) -> bool:
    """
    判断是否为产品驱动型公司

    Args:
        company_type: 公司类型标识

    Returns:
        是否为产品驱动型
    """
    return company_type == "product-driven"


def has_brand_matrix(company_type: str) -> bool:
    """
    判断指定公司类型是否包含品牌矩阵分析

    Args:
        company_type: 公司类型标识

    Returns:
        是否包含品牌矩阵
    """
    config = load_config()
    company_types = config.get("company_types", {})
    company_type_config = company_types.get(company_type, {})
    return company_type_config.get("has_brand_matrix", False)


# ============ 公司类型函数 ============


def get_company_types() -> Dict[str, Dict[str, Any]]:
    """
    获取所有公司类型配置

    Returns:
        公司类型配置字典
    """
    return load_config().get("company_types", {})


def get_company_type_name(company_type: str) -> str:
    """
    获取公司类型的中文名称

    Args:
        company_type: 公司类型标识

    Returns:
        中文名称
    """
    company_types = get_company_types()
    return company_types.get(company_type, {}).get("name", company_type)


def get_company_type_description(company_type: str) -> str:
    """
    获取公司类型的描述

    Args:
        company_type: 公司类型标识

    Returns:
        描述文字
    """
    company_types = get_company_types()
    return company_types.get(company_type, {}).get("description", "")


def get_all_company_type_keys() -> List[str]:
    """
    获取所有公司类型的键名列表

    Returns:
        公司类型键名列表
    """
    return list(get_company_types().keys())


# ============ 模块路径函数 ============


def get_module_path(module: str) -> str:
    """
    获取模块路径

    Args:
        module: 模块名，如 'scoring', 'report', 'cache', 'language_strategy'

    Returns:
        模块路径字符串
    """
    return load_config()["paths"]["modules"].get(module, "")


def get_all_module_paths() -> List[str]:
    """
    获取所有必需模块的路径列表

    Returns:
        模块路径列表
    """
    modules = load_config()["paths"]["modules"]
    return list(modules.values())


def get_scoring_module_path() -> str:
    """
    获取评分模块路径

    Returns:
        评分模块路径
    """
    return get_module_path("scoring")


def get_report_module_path() -> str:
    """
    获取报告模块路径

    Returns:
        报告模块路径
    """
    return get_module_path("report")


def get_cache_module_path() -> str:
    """
    获取缓存模块路径

    Returns:
        缓存模块路径
    """
    return get_module_path("cache")


def get_language_strategy_module_path() -> str:
    """
    获取语言策略模块路径

    Returns:
        语言策略模块路径
    """
    return get_module_path("language_strategy")


# ============ 搜索结果函数 ============


def get_search_results_dir() -> str:
    """
    获取搜索结果子目录名

    Returns:
        子目录名称
    """
    return load_config()["search_results"].get("subdir", "search-results")


def get_dimension_pattern() -> str:
    """
    获取维度文件名模式

    Returns:
        文件名模式字符串
    """
    return load_config()["search_results"].get(
        "dimension_pattern", "dimension-{number}.md"
    )


# ============ 语言策略函数 ============


def get_report_language() -> str:
    """
    获取报告强制语言

    Returns:
        语言代码
    """
    return load_config()["language_strategy"].get("report_language", "zh-CN")


def get_default_search_language() -> str:
    """
    获取默认搜索语言

    Returns:
        语言代码
    """
    return load_config()["language_strategy"].get("default_search_language", "auto")


def get_search_language_for_origin(origin_type: str) -> str:
    """
    根据公司地域类型获取搜索语言

    Args:
        origin_type: 地域类型（chinese/foreign/mixed）

    Returns:
        语言代码
    """
    lang_map = load_config()["language_strategy"].get("search_language_map", {})
    return lang_map.get(origin_type, "auto")


# ============ 文件名函数 ============


def get_file_pattern(pattern_type: str, company: str = "") -> str:
    """
    获取文件名模式

    Args:
        pattern_type: 模式类型，如 'json_output', 'md_output'
        company: 公司名称，用于替换占位符

    Returns:
        格式化后的文件名
    """
    pattern = load_config()["file_patterns"].get(pattern_type, "")
    if company:
        return pattern.replace("{company}", company)
    return pattern


def get_json_output_filename(company: str) -> str:
    """
    获取JSON输出文件名

    Args:
        company: 公司名称

    Returns:
        文件名
    """
    return get_file_pattern("json_output", company)


def get_md_output_filename(company: str) -> str:
    """
    获取Markdown输出文件名

    Args:
        company: 公司名称

    Returns:
        文件名
    """
    return get_file_pattern("md_output", company)


def get_metadata_filename() -> str:
    """
    获取metadata文件名

    Returns:
        文件名
    """
    return load_config()["file_patterns"].get("metadata", "metadata.json")


# ============ 格式函数 ============


def get_format(key: str) -> Any:
    """
    获取格式配置

    Args:
        key: 格式键名，如 'date', 'datetime', 'separator_length'

    Returns:
        格式值
    """
    return load_config()["formats"].get(key)


def get_date_format() -> str:
    """
    获取日期格式

    Returns:
        日期格式字符串
    """
    return get_format("date")


def get_datetime_format() -> str:
    """
    获取日期时间格式

    Returns:
        日期时间格式字符串
    """
    return get_format("datetime")


def get_separator_length() -> int:
    """
    获取分隔线长度

    Returns:
        分隔线长度
    """
    return get_format("separator_length")


def format_timestamp() -> str:
    """
    格式化时间戳

    Returns:
        格式化的字符串
    """
    timestamp = get_format("datetime")
    current_time = datetime.now().strftime(timestamp)
    return get_format("timestamp").format(timestamp=current_time)


# ============ 情景概率函数 ============


def get_scenario_probabilities(probability_type: str = "default") -> Dict[str, float]:
    """
    获取情景概率配置

    Args:
        probability_type: 概率类型（default/high_certainty/high_risk/national_strategy）

    Returns:
        概率字典
    """
    config = load_config()
    scenario_probs = config.get("scenario_probabilities", {})
    return scenario_probs.get(
        probability_type,
        scenario_probs.get(
            "default", {"optimistic": 0.25, "base": 0.50, "pessimistic": 0.25}
        ),
    )


def get_optimistic_probability(probability_type: str = "default") -> float:
    """
    获取乐观情景概率

    Args:
        probability_type: 概率类型

    Returns:
        概率值
    """
    return get_scenario_probabilities(probability_type)["optimistic"]


def get_base_probability(probability_type: str = "default") -> float:
    """
    获取基准情景概率

    Args:
        probability_type: 概率类型

    Returns:
        概率值
    """
    return get_scenario_probabilities(probability_type)["base"]


def get_pessimistic_probability(probability_type: str = "default") -> float:
    """
    获取悲观情景概率

    Args:
        probability_type: 概率类型

    Returns:
        概率值
    """
    return get_scenario_probabilities(probability_type)["pessimistic"]


# ============ 验证函数 ============


def get_required_fields(field_type: str) -> List[str]:
    """
    获取必需字段列表

    Args:
        field_type: 字段类型，如 'metadata', 'report'

    Returns:
        字段名列表
    """
    return load_config()["validation"].get(f"{field_type}_required_fields", [])


def get_metadata_required_fields() -> List[str]:
    """
    获取metadata必需字段

    Returns:
        字段名列表
    """
    return get_required_fields("metadata")


def get_report_required_fields() -> List[str]:
    """
    获取报告必需字段

    Returns:
        字段名列表
    """
    return get_required_fields("report")


# ============ 评分函数 ============


def get_scoring_table() -> List[Dict]:
    """
    获取评分表配置

    Returns:
        评分表列表，每项包含 cagr_range, score_range, rating
    """
    return load_config().get("scoring_table", [])


def get_score_for_cagr(cagr: float) -> tuple:
    """
    根据 CAGR 获取对应的评分区间和评级

    Args:
        cagr: 复合年增长率

    Returns:
        (score_range, rating) 元组

    Raises:
        ValueError: 如果 CAGR 超出所有定义的区间
    """
    for entry in get_scoring_table():
        cagr_min, cagr_max = entry["cagr_range"]
        if cagr_min <= cagr < cagr_max or (cagr_max == 100 and cagr >= cagr_min):
            return tuple(entry["score_range"]), entry["rating"]

    raise ValueError(f"CAGR {cagr}% 超出评分范围 [0, 100]")


def get_rating_for_cagr(cagr: float) -> str:
    """
    根据 CAGR 获取评级

    Args:
        cagr: 复合年增长率

    Returns:
        评级文字
    """
    _, rating = get_score_for_cagr(cagr)
    return rating


# ============ 缓存新鲜度函数 ============


def get_cache_freshness_config() -> Dict[str, int]:
    """
    获取缓存新鲜度配置

    Returns:
        新鲜度配置字典
    """
    return load_config().get(
        "cache_freshness", {"fresh_hours": 24, "stale_days": 7, "outdated_days": 30}
    )


# ============ 搜索策略函数 ============


def get_search_strategy_config() -> Dict[str, Any]:
    """
    获取搜索策略配置

    Returns:
        搜索策略配置字典
    """
    return load_config().get("search_strategy", {})


def get_min_search_per_dimension() -> int:
    """
    获取每个维度最少搜索次数

    Returns:
        搜索次数
    """
    return get_search_strategy_config().get("min_search_per_dimension", 2)


def get_max_search_per_dimension() -> int:
    """
    获取每个维度最多搜索次数

    Returns:
        搜索次数
    """
    return get_search_strategy_config().get("max_search_per_dimension", 5)


def get_total_search_range() -> List[int]:
    """
    获取总搜索次数范围

    Returns:
        [最小, 最大] 列表
    """
    return get_search_strategy_config().get("total_search_range", [18, 25])


# ============ 动态年份计算函数 ============


def get_current_year() -> int:
    """
    获取当前年份

    Returns:
        当前年份（如 2026）
    """
    return datetime.now().year


def get_forecast_start_year() -> int:
    """
    获取预测起始年份（当前年份）

    Returns:
        预测起始年份
    """
    return get_current_year()


def get_forecast_end_year() -> int:
    """
    获取预测结束年份（当前年份 + 5年）

    Returns:
        预测结束年份
    """
    forecast_config = load_config().get("forecast", {})
    offset = forecast_config.get("end_year_offset", 5)
    return get_current_year() + offset


def get_historical_year() -> int:
    """
    获取历史数据年份（当前年份 - 1）

    Returns:
        历史数据年份
    """
    forecast_config = load_config().get("forecast", {})
    offset = forecast_config.get("historical_year_offset", 1)
    return get_current_year() - offset


def get_forecast_years() -> List[int]:
    """
    获取所有预测年份列表（从当前年份到结束年份）

    Returns:
        年份列表，如 [2025, 2026, 2027, 2028, 2029, 2030]
    """
    start_year = get_forecast_start_year()
    end_year = get_forecast_end_year()
    return list(range(start_year, end_year + 1))


def get_forecast_year_range() -> str:
    """
    获取预测年份范围字符串

    Returns:
        如 "2025-2030"
    """
    return f"{get_forecast_start_year()}-{get_forecast_end_year()}"


def format_revenue_key(year: int = None) -> str:
    """
    格式化营收键名

    Args:
        year: 年份，默认为预测结束年份

    Returns:
        如 "revenue_2029"
    """
    if year is None:
        year = get_forecast_end_year()
    return f"revenue_{year}"


def format_annual_forecast() -> Dict[str, int]:
    """
    获取年度预测字典

    Returns:
        如 {"2025": xxx, "2026": xxx, ...}
    """
    years = get_forecast_years()
    return {str(year): None for year in years}


# ============ 路径构建函数 ============


def build_company_cache_dir(company_name: str, base_dir: str = None) -> str:
    """
    构建公司缓存目录路径

    Args:
        company_name: 公司名称
        base_dir: 基础目录，默认为缓存根目录

    Returns:
        公司缓存目录路径
    """
    import re

    if base_dir is None:
        base_dir = get_cache_base_dir()

    # 清理公司名称，生成文件系统安全的目录名
    safe_name = re.sub(r'[\\/:*?"<>|]', "", company_name)
    safe_name = re.sub(r"[\s\-]+", "_", safe_name)
    safe_name = safe_name[:50].strip("_")

    return str(Path(base_dir) / safe_name)


def build_search_results_dir(company_cache_dir: str) -> str:
    """
    构建搜索结果目录路径

    Args:
        company_cache_dir: 公司缓存目录

    Returns:
        搜索结果目录路径
    """
    return str(Path(company_cache_dir) / get_search_results_subdir())


def build_dimension_file_path(company_cache_dir: str, dimension_file: str) -> str:
    """
    构建维度文件完整路径

    Args:
        company_cache_dir: 公司缓存目录
        dimension_file: 维度文件名

    Returns:
        维度文件完整路径
    """
    return str(Path(company_cache_dir) / dimension_file)


def build_output_file_path(
    output_dir: str, company_name: str, file_pattern: str
) -> str:
    """
    构建输出文件路径

    Args:
        output_dir: 输出目录
        company_name: 公司名称
        file_pattern: 文件名模式

    Returns:
        输出文件完整路径
    """
    filename = file_pattern.replace("{company}", company_name)
    return str(Path(output_dir) / filename)


# ============ 验证检查点函数 ============


def get_config_validation_checklist() -> Dict[str, Any]:
    """
    获取配置验证检查清单

    Returns:
        验证检查清单字典
    """
    return {
        "version": get_version(),
        "directories": {
            "cache_base_dir": get_cache_base_dir(),
            "output_dir": get_output_dir(),
            "search_results_subdir": get_search_results_subdir(),
        },
        "company_types": get_all_company_type_keys(),
        "default_dimension_count": get_dimension_count("default"),
        "product_driven_dimension_count": get_dimension_count("product-driven"),
        "has_brand_matrix": has_brand_matrix("product-driven"),
        "modules": list(load_config()["paths"]["modules"].keys()),
        "forecast_range": get_forecast_year_range(),
    }


def print_config_validation() -> str:
    """
    打印配置验证信息

    Returns:
        格式化的验证信息字符串
    """
    checklist = get_config_validation_checklist()
    lines = [
        "=" * 50,
        "[配置验证检查点]",
        "=" * 50,
        f"版本: {checklist['version']}",
        "",
        "目录配置:",
        f"  缓存根目录: {checklist['directories']['cache_base_dir']}",
        f"  输出目录: {checklist['directories']['output_dir']}",
        f"  搜索结果子目录: {checklist['directories']['search_results_subdir']}",
        "",
        "公司类型:",
        f"  支持类型: {', '.join(checklist['company_types'])}",
        "",
        "维度文件:",
        f"  默认维度数: {checklist['default_dimension_count']}",
        f"  产品驱动型维度数: {checklist['product_driven_dimension_count']}",
        f"  品牌矩阵: {'✅ 有' if checklist['has_brand_matrix'] else '❌ 无'}",
        "",
        "模块:",
        f"  {', '.join(checklist['modules'])}",
        "",
        "预测范围:",
        f"  {checklist['forecast_range']}",
        "=" * 50,
    ]
    return "\n".join(lines)


# 便捷别名（向后兼容）
def get_all_module_paths_alias() -> List[str]:
    """获取所有必需模块的路径列表（兼容旧接口）"""
    modules = load_config()["paths"]["modules"]
    return list(modules.values())


# ============ 配置验证 ============


def validate_config() -> tuple[bool, List[str]]:
    """
    验证配置文件完整性

    Returns:
        (是否有效, 错误列表)
    """
    errors = []
    config = load_config()

    # 检查必需的配置节
    required_sections = [
        "version",
        "directories",
        "paths",
        "dimension_files",
        "company_types",
    ]
    for section in required_sections:
        if section not in config:
            errors.append(f"缺少必需配置节: {section}")

    # 检查必需的公司类型
    required_company_types = ["product-driven"]
    for ct in required_company_types:
        if ct not in config.get("company_types", {}):
            errors.append(f"缺少必需公司类型: {ct}")

    return len(errors) == 0, errors


def assert_config_valid() -> None:
    """
    断言配置有效，否则抛出异常

    Raises:
        ValueError: 如果配置无效
    """
    is_valid, errors = validate_config()
    if not is_valid:
        raise ValueError(f"配置验证失败:\n" + "\n".join(errors))
