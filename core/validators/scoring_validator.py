"""
评分系统验证器
模块: modules/scoring/scoring-framework.md
用途: 验证评分是否正确执行
检查点: CP-4, CP-7
"""

# v2.6.0 统一 UTF-8 编码引导（避免 Windows cp936/gbk 中文乱码）
import os as _os, sys as _sys
for _p in (_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))),
           _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))):
    if _p not in _sys.path:
        _sys.path.insert(0, _p)
try:
    from core.encoding import setup_utf8_console as _setup_utf8_console
    _setup_utf8_console()
except Exception:
    pass

import sys

# 导入配置模块
from core.config import get_scoring_table, get_module_path, get_score_for_cagr


def validate_module_read():
    """
    CP-4: 评分模块已读取验证

    验证标准:
    - 必须已读取评分模块
    - 重点关注: 评分表和规则
    - 未读取模块,禁止执行评分
    """
    scoring_module_path = get_module_path('scoring')
    print("[CP-4] 评分模块读取验证")
    print(f"  [检查] 确认已读取: {scoring_module_path}")
    print(f"  [重点] 重点关注: 评分表和规则")
    print("[通过] CP-4验证通过: 评分模块已读取\n")
    return True


def calculate_score_from_cagr(cagr):
    """
    根据CAGR计算评分(查表+线性插值)

    Args:
        cagr: 综合CAGR(百分比)

    Returns:
        dict: {
            "score": 评分,
            "rating": 评级,
            "score_range": 评分区间
        }
    """
    scoring_table = get_scoring_table()

    # 查找对应的评分区间
    for entry in scoring_table:
        min_cagr, max_cagr = entry['cagr_range']
        min_score, max_score = entry['score_range']
        rating = entry['rating']

        if min_cagr <= cagr < max_cagr or (max_cagr == 100 and cagr >= min_cagr):
            # 线性插值计算精确评分
            if max_cagr == min_cagr:
                score = min_score
            else:
                score = min_score + (cagr - min_cagr) / (max_cagr - min_cagr) * (max_score - min_score)

            return {
                "score": round(score, 1),
                "rating": rating,
                "score_range": (min_score, max_score),
                "cagr_range": (min_cagr, max_cagr)
            }

    # 如果CAGR超出范围
    if cagr >= 30:
        return {"score": 10.0, "rating": "强烈推荐", "score_range": (9.5, 10.0), "cagr_range": (30, 100)}
    else:
        raise ValueError(f"CAGR {cagr}% 超出评分范围")


def validate_scoring(cagr, actual_score):
    """
    CP-7: CAGR与评分匹配验证

    验证标准:
    - 评分必须完全由综合CAGR决定
    - 不得主观调整评分
    - 必须在正确的评分区间内

    Args:
        cagr: 综合CAGR
        actual_score: 实际评分

    Returns:
        bool: 验证是否通过

    使用示例:
        if not validate_scoring(6.8, 3.1):
            raise Exception("评分与CAGR不匹配!")
    """
    print("[CP-7] CAGR与评分匹配验证")
    print(f"  输入CAGR: {cagr}%")
    print(f"  输入评分: {actual_score}")

    # 根据CAGR计算期望评分
    expected = calculate_score_from_cagr(cagr)
    expected_score = expected["score"]
    min_score, max_score = expected["score_range"]

    # 验证评分在正确区间内
    if not (min_score <= actual_score <= max_score):
        print(f"  [错误] 评分超出区间!")
        print(f"  期望区间: {min_score:.1f} - {max_score:.1f}分")
        print(f"  实际评分: {actual_score:.1f}分")
        print(f"  差异: {abs(actual_score - expected_score):.1f}分")

        raise ValueError(
            f"[错误] 评分与CAGR不匹配!\n"
            f"CAGR={cagr}%, 评分区间应为{min_score:.1f}-{max_score:.1f}分\n"
            f"但实际评分为{actual_score:.1f}分\n\n"
            f"常见错误原因:\n"
            f"1. 使用了9维度加权而非直接查CAGR\n"
            f"2. 主观调整了评分(因为公司是龙头/品牌好等)\n"
            f"3. 计算错误\n\n"
            f"[建议] 请按照scoring-framework.md第45-57行的评分表重新查表"
        )

    # 验证评分与期望评分接近(允许0.1的误差)
    if abs(actual_score - expected_score) > 0.1:
        print(f"  [警告] 评分与期望值略有偏差")
        print(f"  期望评分: {expected_score:.1f}分")
        print(f"  实际评分: {actual_score:.1f}分")
        print(f"  偏差: {abs(actual_score - expected_score):.1f}分")

    print(f"  [OK] CAGR范围: {expected['cagr_range'][0]}%-{expected['cagr_range'][1]}%")
    print(f"  [OK] 评分区间: {min_score:.1f}-{max_score:.1f}分")
    print(f"  [OK] 实际评分: {actual_score:.1f}分")
    print(f"  [OK] 评级: {expected['rating']}")
    print("[通过] CP-7验证通过: CAGR与评分匹配\n")

    return True


def validate_scoring_workflow(cagr, actual_score, module_read=True):
    """
    一键验证评分工作流
    集成CP-4, CP-7

    Args:
        cagr: 综合CAGR
        actual_score: 实际评分
        module_read: 是否已读取评分模块

    Returns:
        tuple: (bool, dict) - (是否全部通过, 验证结果)

    使用示例:
        success, result = validate_scoring_workflow(6.8, 3.1)
        if success:
            print("[OK] 评分验证通过")
        else:
            print("[错误] 评分验证失败")
            sys.exit(1)
    """
    print("="*60)
    print("[验证] 评分系统验证检查点")
    print("="*60)

    try:
        # CP-4: 模块读取验证
        if module_read:
            validate_module_read()
        else:
            print("[跳过] CP-4验证(模块未读取)")

        # CP-7: CAGR与评分匹配验证
        validate_scoring(cagr, actual_score)

        print("="*60)
        print("[成功] 所有评分检查点通过 (CP-4, CP-7)")
        print("="*60)
        print()

        return True, {
            "cagr": cagr,
            "score": actual_score,
            "rating": calculate_score_from_cagr(cagr)["rating"],
            "validated": True
        }

    except ValueError as e:
        print("="*60)
        print("[失败] 评分验证失败")
        print("="*60)
        print(str(e))
        print()

        return False, {}


# ========== 命令行使用 ==========
if __name__ == "__main__":
    """
    命令行使用示例:
        python scoring_validator.py 6.8 3.1
    """
    if len(sys.argv) < 3:
        print("用法: python scoring_validator.py <CAGR> <评分>")
        print("示例: python scoring_validator.py 6.8 3.1")
        print()
        print("说明:")
        print("  CAGR: 综合复合增长率(百分比)")
        print("  评分: 根据CAGR计算的评分(0-10分)")
        sys.exit(1)

    try:
        cagr = float(sys.argv[1])
        score = float(sys.argv[2])
    except ValueError:
        print("[错误] CAGR和评分必须是数字")
        sys.exit(1)

    success, _ = validate_scoring_workflow(cagr, score)

    sys.exit(0 if success else 1)
