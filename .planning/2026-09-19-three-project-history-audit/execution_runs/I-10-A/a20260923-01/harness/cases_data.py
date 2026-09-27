#!/usr/bin/env python
"""I-10-A harness: disclosure-extracted frozen input table (shared by the probe
runner and the artifact builder).

EVERY number here is extracted verbatim from the three sources' recorded extracts
(see per-field `source` refs: extract file + line span + PDF page). Nothing is
derived from disclosed revenue (oracle R4b). Unit conversions are explicit and
recomputable (raw_value * factor == used value).
"""

SOURCES = {
    "CN": {
        "doc": "紫金矿业集团股份有限公司2025年年度报告",
        "sha256": "01819e1c7daad939d1779a8aa729f50f02151192e609cb28c2c405634a8f343d",
        "extract": "evidence/I-10-A/source_extracts/CN-ZIJIN-2025.txt",
        "available_at": "2026-03-20",
    },
    "HK": {
        "doc": "小米集團－Ｗ 2025年度報告",
        "sha256": "ffd733761633f464d90f6829e9b2d3e089f2dee7054b8ebfe91ef617f222da7c",
        "extract": "evidence/I-10-A/source_extracts/HK-XIAOMI-2025_decoded.txt",
        "available_at": "2026-04-28",
    },
    "US": {
        "doc": "MICROSOFT CORP Form 10-K FY2026",
        "sha256": "e3de0053021c02b033272b55551e383b31dba288c86cc12da2e32375e40ecfff",
        "extract": "evidence/I-10-A/source_extracts/US-MSFT-2026.txt",
        "available_at": "2026-07-29",
    },
}

# quote = exact text; verify = {lines: [start,end], mode: "concat-lines"} means the
# quote equals/contains the concatenation of those 1-based extract lines (HK spans
# split mid-sentence per text span; CN/US lines are whole lines).
CASES = {
    "ZJ-MIN-M09": {
        "company_id": "CN-ZIJIN-2025",
        "segment": "矿产品分部",
        "model_id": "resource",
        "m_card": "M09",
        "period": "FY2025",
        "years": [2025],
        "base_revenue": 0.0,
        "currency": "CNY",
        "instances": [
            {"instance": "gold_ingot", "cn": "矿山产金-金锭",
             "qty_raw": 49074.0, "qty_raw_unit": "千克", "qty_factor": 1000.0, "qty_unit": "克",
             "price": 810.17, "price_unit": "元/克", "other_revenue": 0.0,
             "disclosed_amount_wan_yuan": 3975798.0,
             "qty_src": {"key": "CN", "page": 44, "lines": [3958, 3964],
                         "quote": "矿山产金 金锭 810.17 元/克 49,074 千克 3,975,798"},
             "price_src": {"key": "CN", "page": 44, "lines": [3958, 3964],
                           "quote": "金锭 810.17 元/克 49,074 千克 3,975,798"},
             "disclosed_src": {"key": "CN", "page": 45, "lines": [4137, 4143],
                               "quote": "矿山产金锭 3,975,798 1,638,404 58.79"}},
            {"instance": "gold_concentrate", "cn": "矿山产金-金精矿",
             "qty_raw": 34087.0, "qty_raw_unit": "千克", "qty_factor": 1000.0, "qty_unit": "克",
             "price": 730.98, "price_unit": "元/克", "other_revenue": 0.0,
             "disclosed_amount_wan_yuan": 2491716.0,
             "qty_src": {"key": "CN", "page": 44, "lines": [3971, 3981],
                         "quote": "金精矿 730.98 元/克 34,087 千克 2,491,716"},
             "price_src": {"key": "CN", "page": 44, "lines": [3971, 3976],
                           "quote": "金精矿 730.98 元/克 34,087 千克 2,491,716"},
             "disclosed_src": {"key": "CN", "page": 45, "lines": [4144, 4150],
                               "quote": "矿山产金精矿 2,491,716 650,473 73.89"}},
            {"instance": "copper_concentrate", "cn": "矿山产铜-铜精矿",
             "qty_raw": 666158.0, "qty_raw_unit": "吨", "qty_factor": 1.0, "qty_unit": "吨",
             "price": 63613.0, "price_unit": "元/吨", "other_revenue": 0.0,
             "disclosed_amount_wan_yuan": 4237657.0,
             "qty_src": {"key": "CN", "page": 44, "lines": [3983, 3994],
                         "quote": "铜精矿 63,613 元/吨 666,158 吨 4,237,657"},
             "price_src": {"key": "CN", "page": 44, "lines": [3983, 3989],
                           "quote": "铜精矿 63,613 元/吨 666,158 吨 4,237,657"},
             "disclosed_src": {"key": "CN", "page": 45, "lines": [4151, 4157],
                               "quote": "矿山产铜精矿 4,237,657 1,489,677 64.85"}},
            {"instance": "sxew_copper", "cn": "矿山产铜-电积铜",
             "qty_raw": 95499.0, "qty_raw_unit": "吨", "qty_factor": 1.0, "qty_unit": "吨",
             "price": 69665.0, "price_unit": "元/吨", "other_revenue": 0.0,
             "disclosed_amount_wan_yuan": 665294.0,
             "qty_src": {"key": "CN", "page": 44, "lines": [3996, 4006],
                         "quote": "电积铜 69,665 元/吨 95,499 吨 665,294"},
             "price_src": {"key": "CN", "page": 44, "lines": [3996, 4001],
                           "quote": "电积铜 69,665 元/吨 95,499 吨 665,294"},
             "disclosed_src": {"key": "CN", "page": 45, "lines": [4158, 4164],
                               "quote": "矿山产电积铜 665,294 314,490 52.73"}},
            {"instance": "electrolytic_copper", "cn": "矿山产铜-电解铜",
             "qty_raw": 123286.0, "qty_raw_unit": "吨", "qty_factor": 1.0, "qty_unit": "吨",
             "price": 71422.0, "price_unit": "元/吨", "other_revenue": 0.0,
             "disclosed_amount_wan_yuan": 880537.0,
             "qty_src": {"key": "CN", "page": 44, "lines": [4008, 4018],
                         "quote": "电解铜 71,422 元/吨 123,286 吨 880,537"},
             "price_src": {"key": "CN", "page": 44, "lines": [4008, 4013],
                           "quote": "电解铜 71,422 元/吨 123,286 吨 880,537"},
             "disclosed_src": {"key": "CN", "page": 45, "lines": [4165, 4171],
                               "quote": "矿山产电解铜 880,537 449,025 49.01"}},
            {"instance": "mined_zinc", "cn": "矿山产锌",
             "qty_raw": 352470.0, "qty_raw_unit": "吨", "qty_factor": 1.0, "qty_unit": "吨",
             "price": 14999.0, "price_unit": "元/吨", "other_revenue": 0.0,
             "disclosed_amount_wan_yuan": 528665.0,
             "qty_src": {"key": "CN", "page": 44, "lines": [4020, 4030],
                         "quote": "矿山产锌 14,999 元/吨 352,470 吨 528,665"},
             "price_src": {"key": "CN", "page": 44, "lines": [4020, 4025],
                           "quote": "矿山产锌 14,999 元/吨 352,470 吨 528,665"},
             "disclosed_src": {"key": "CN", "page": 45, "lines": [4172, 4178],
                               "quote": "矿山产锌 528,665 349,679 33.86"}},
            {"instance": "mined_silver", "cn": "矿山产银",
             "qty_raw": 430254.0, "qty_raw_unit": "千克", "qty_factor": 1000.0, "qty_unit": "克",
             "price": 6.88, "price_unit": "元/克", "other_revenue": 0.0,
             "disclosed_amount_wan_yuan": 295801.0,
             "qty_src": {"key": "CN", "page": 44, "lines": [4032, 4042],
                         "quote": "矿山产银 6.88 元/克 430,254 千克 295,801"},
             "price_src": {"key": "CN", "page": 44, "lines": [4032, 4037],
                           "quote": "矿山产银 6.88 元/克 430,254 千克 295,801"},
             "disclosed_src": {"key": "CN", "page": 45, "lines": [4179, 4185],
                               "quote": "矿山产银 295,801 91,249 69.15"}},
            {"instance": "iron_concentrate", "cn": "铁精矿",
             "qty_raw": 111.35, "qty_raw_unit": "万吨", "qty_factor": 10000.0, "qty_unit": "吨",
             "price": 660.0, "price_unit": "元/吨", "other_revenue": 0.0,
             "disclosed_amount_wan_yuan": 73482.0,
             "qty_src": {"key": "CN", "page": 44, "lines": [4044, 4054],
                         "quote": "铁精矿 660 元/吨 111.35 万吨 73,482"},
             "price_src": {"key": "CN", "page": 44, "lines": [4044, 4049],
                           "quote": "铁精矿 660 元/吨 111.35 万吨 73,482"},
             "disclosed_src": {"key": "CN", "page": 45, "lines": [4186, 4192],
                               "quote": "铁精矿 73,482 28,432 61.31"}}
        ],
        "policy_refs": [
            {"key": "CN", "page": 155, "lines": [12281, 12281],
             "quote": "本集团通过向客户交付商品履行履约义务，以商品控制权转移时点确认收入。"},
            {"key": "CN", "page": 254, "lines": [26330, 26332],
             "quote": "本集团将合同中约定的转让矿产品作为单项履约义务，因此，该履约义务属于在某一时点履行的履约义务，本集团在客户取得矿产品控制权的时点确认收入。"},
            {"key": "CN", "page": 325, "lines": [34913, 34935],
             "quote": "矿产品分部的产品为矿山产铜、矿山产金、矿山产锌精矿、矿山产铅精矿、矿山产银"},
            {"key": "CN", "page": 326, "lines": [34990, 35017],
             "quote": "对外销售收入 109,977,556,345 165,858,644,874 29,212,610,830 44,030,270,803 - 349,079,082,852"},
            {"key": "CN", "page": 45, "lines": [4345, 4345], "quote": "单位：万元"}
        ]
    },
    "ZJ-SMT-M09": {
        "company_id": "CN-ZIJIN-2025",
        "segment": "冶炼产品分部",
        "model_id": "resource",
        "m_card": "M09",
        "period": "FY2025",
        "years": [2025],
        "base_revenue": 0.0,
        "currency": "CNY",
        "instances": [
            {"instance": "smelted_gold", "cn": "冶炼加工金",
             "qty_raw": 162950.0, "qty_raw_unit": "千克", "qty_factor": 1000.0, "qty_unit": "克",
             "price": 772.15, "price_unit": "元/克", "other_revenue": 0.0,
             "disclosed_amount_wan_yuan": 12582221.0,
             "qty_src": {"key": "CN", "page": 44, "lines": [4056, 4066],
                         "quote": "冶炼加工金 772.15 元/克 162,950 千克 12,582,221"},
             "price_src": {"key": "CN", "page": 44, "lines": [4056, 4061],
                           "quote": "冶炼加工金 772.15 元/克 162,950 千克 12,582,221"},
             "disclosed_src": {"key": "CN", "page": 45, "lines": [4193, 4199],
                               "quote": "冶炼加工及贸易金 12,582,221 12,452,010 1.03"}},
            {"instance": "smelted_copper", "cn": "冶炼产铜",
             "qty_raw": 697678.0, "qty_raw_unit": "吨", "qty_factor": 1.0, "qty_unit": "吨",
             "price": 71621.0, "price_unit": "元/吨", "other_revenue": 0.0,
             "disclosed_amount_wan_yuan": 4996807.0,
             "qty_src": {"key": "CN", "page": 44, "lines": [4068, 4078],
                         "quote": "冶炼产铜 71,621 元/吨 697,678 吨 4,996,807"},
             "price_src": {"key": "CN", "page": 44, "lines": [4068, 4073],
                           "quote": "冶炼产铜 71,621 元/吨 697,678 吨 4,996,807"},
             "disclosed_src": {"key": "CN", "page": 45, "lines": [4200, 4206],
                               "quote": "冶炼产铜 4,996,807 4,892,676 2.08"}},
            {"instance": "smelted_zinc", "cn": "冶炼产锌",
             "qty_raw": 403324.0, "qty_raw_unit": "吨", "qty_factor": 1.0, "qty_unit": "吨",
             "price": 20327.0, "price_unit": "元/吨", "other_revenue": 0.0,
             "disclosed_amount_wan_yuan": 819823.0,
             "qty_src": {"key": "CN", "page": 44, "lines": [4080, 4090],
                         "quote": "冶炼产锌 20,327 元/吨 403,324 吨 819,823"},
             "price_src": {"key": "CN", "page": 44, "lines": [4080, 4085],
                           "quote": "冶炼产锌 20,327 元/吨 403,324 吨 819,823"},
             "disclosed_src": {"key": "CN", "page": 45, "lines": [4207, 4213],
                               "quote": "冶炼产锌 819,823 836,781 -2.07"}}
        ],
        "policy_refs": [
            {"key": "CN", "page": 155, "lines": [12281, 12281],
             "quote": "本集团通过向客户交付商品履行履约义务，以商品控制权转移时点确认收入。"},
            {"key": "CN", "page": 254, "lines": [26342, 26342],
             "quote": "本集团在客户取得冶炼产品控制权的时点确认收入。"},
            {"key": "CN", "page": 325, "lines": [34927, 34931],
             "quote": "冶炼产品分部的产品为冶炼产铜、冶炼加工金银、冶炼产锌锭、硫酸、电池级碳酸"},
            {"key": "CN", "page": 45, "lines": [4345, 4345], "quote": "单位：万元"}
        ]
    },
    "XM-PHONE-M03": {
        "company_id": "HK-XIAOMI-2025",
        "segment": "智能手機（手機×AIoT 分部產品線）",
        "model_id": "unit_sales",
        "m_card": "M03",
        "period": "FY2025",
        "years": [2025],
        "base_revenue": 0.0,
        "currency": "CNY",
        "instances": [
            {"instance": "smartphones", "cn": "智能手機",
             "qty_raw": 165.2, "qty_raw_unit": "百萬部", "qty_factor": 1000000.0, "qty_unit": "部",
             "price": 1128.7, "price_unit": "元/部", "timing_factor": 1.0, "other_revenue": 0.0,
             "disclosed_amount_qian_yuan": 186439777.0,
             "qty_src": {"key": "HK", "page": 21, "lines": [1387, 1405],
                         "quote": "智能手機出貨量由截至2024年12月31日止年度的168.5百萬部減少2.0%至截至2025年12月31日止年度的165.2百萬部"},
             "price_src": {"key": "HK", "page": 21, "lines": [1417, 1437],
                           "quote": "智能手機的ASP由截至2024年12月31日止年度的每部人民幣1,138.2元輕微下降0.8%至截至2025年12月31日止年度的每部人民幣1,128.7元"},
             "disclosed_src": {"key": "HK", "page": 337, "lines": [17789, 17790],
                               "quote": "分部收入 186,439,777123,200,19137,440,3464,136,860351,217,174106,069,513457,286,687"}}
        ],
        "policy_refs": [
            {"key": "HK", "page": 300, "lines": [16487, 16487],
             "quote": "銷售產品的收入於向客戶轉移貨物控制權時（即客戶驗收產品時）確認。"},
            {"key": "HK", "page": 337, "lines": [17815, 17819],
             "quote": "就根據國際財務報告準則第15號與客戶訂立的合約所產生的收入而言，大部分收入乃於某一時間點確認"},
            {"key": "HK", "page": 301, "lines": [16522, 16528],
             "quote": "本集團根據多項因素的持續評估釐定收入應按總額亦或按淨額呈報"}
        ]
    },
    "XM-EV-M03": {
        "company_id": "HK-XIAOMI-2025",
        "segment": "智能電動汽車及AI等創新業務分部",
        "model_id": "unit_sales",
        "m_card": "M03",
        "period": "FY2025",
        "years": [2025],
        "base_revenue": 0.0,
        "currency": "CNY",
        "instances": [
            {"instance": "smart_ev_segment", "cn": "智能電動汽車及AI等創新業務",
             "qty_raw": 411082.0, "qty_raw_unit": "輛", "qty_factor": 1.0, "qty_unit": "輛",
             "price": 251171.0, "price_unit": "元/輛", "timing_factor": 1.0,
             "other_revenue": 2800000000.0,
             "disclosed_amount_qian_yuan": 106069513.0,
             "qty_src": {"key": "HK", "page": 22, "lines": [1565, 1583],
                         "quote": "汽車交付量由截至2024年12月31日止年度的136,854輛增加200.4%至截至2025年12月31日止年度的411,082輛"},
             "price_src": {"key": "HK", "page": 22, "lines": [1591, 1611],
                           "quote": "智能電動汽車的ASP由截至2024年12月31日止年度的每輛人民幣234,479元上升7.1%至截至2025年12月31日止年度的每輛人民幣251,171元"},
             "other_revenue_src": {"key": "HK", "page": 22, "lines": [1618, 1636],
                                   "quote": "其他相關業務收入由截至2024年12月31日止年度的人民幣7億元增加324.2%至截至2025年12月31日止年度的人民幣28億元，主要是由於售後服務、配件銷售及汽車金融服務收入增加所致。"},
             "disclosed_src": {"key": "HK", "page": 337, "lines": [17789, 17790],
                               "quote": "分部收入 186,439,777123,200,19137,440,3464,136,860351,217,174106,069,513457,286,687"}}
        ],
        "policy_refs": [
            {"key": "HK", "page": 300, "lines": [16487, 16487],
             "quote": "銷售產品的收入於向客戶轉移貨物控制權時（即客戶驗收產品時）確認。"},
            {"key": "HK", "page": 22, "lines": [1525, 1545],
             "quote": "智能電動汽車及AI等創新業務分部收入由截至2024年12月31日止年度的人民幣328億元增加223.8%至截至2025年12月31日止年度的人民幣1,061億元。"}
        ]
    },
    "MS-PBP-M05": {
        "company_id": "US-MSFT-2026",
        "segment": "Productivity and Business Processes",
        "model_id": "subscription",
        "m_card": "M05",
        "period": "FY2026",
        "years": [],
        "base_revenue": 0.0,
        "currency": "USD",
        "instances": [],
        "missing_drivers": ["average_customers", "revenue_per_customer", "timing_factor", "usage_revenue"],
        "missing_evidence": [
            {"key": "US", "page": 36, "lines": [745, 756],
             "quote": "Microsoft 365 Commercial seat growth"},
            {"key": "US", "page": 35, "lines": [734, 734],
             "quote": "In the first quarter of fiscal year 2026, we made updates to our metrics to align with how we manage and monitor certain businesses. As part of these updates, Microsoft 365 Consumer subscribers was removed as a metric."},
            {"key": "US", "page": 84, "lines": [4790, 4845],
             "quote": "Revenue, classified by significant product and service offerings, was as follows:"}
        ],
        "policy_refs": [
            {"key": "US", "page": 55, "lines": [1960, 1967],
             "quote": "Revenue is recognized upon transfer of control of promised products or services to customers in an amount that reflects the consideration we expect to receive in exchange for those products or services."},
            {"key": "US", "page": 34, "lines": [199, 199],
             "quote": "We operate our business and report our financial performance using three segments: Productivity and Business Processes, Intelligent Cloud, and More Personal Computing."}
        ]
    },
    "MS-IC-M06": {
        "company_id": "US-MSFT-2026",
        "segment": "Intelligent Cloud",
        "model_id": "usage_platform",
        "m_card": "M06",
        "period": "FY2026",
        "years": [],
        "base_revenue": 0.0,
        "currency": "USD",
        "instances": [],
        "missing_drivers": ["eligible_activity", "monetization_rate", "fixed_revenue"],
        "missing_evidence": [
            {"key": "US", "page": 36, "lines": [755, 756],
             "quote": "Azure and other cloud services revenue growth"},
            {"key": "US", "page": 22, "lines": [232, 232],
             "quote": "Server products and cloud services, including Azure and other cloud services, comprising cloud and AI consumption-based services, GitHub cloud services, Health and Life Sciences cloud services (formerly Nuance Healthcare cloud services), virtual desktop offerings, and other cloud services; and Server products, comprising SQL Server, Windows Server, Visual Studio, System Center, related Client Access Licenses (“CALs”), and other on-premises offerings."},
            {"key": "US", "page": 83, "lines": [4057, 4057],
             "quote": "Revenue allocated to remaining performance obligations, which includes unearned revenue and amounts expected to be invoiced and recognized as revenue in future periods, was $684 billion as of June 30, 2026."}
        ],
        "policy_refs": [
            {"key": "US", "page": 55, "lines": [1960, 1967],
             "quote": "Revenue is recognized upon transfer of control of promised products or services to customers in an amount that reflects the consideration we expect to receive in exchange for those products or services."}
        ]
    }
}


def driver_spec(model_id: str) -> dict:
    """Model driver roles (mirrors MODEL_REGISTRY specs; verified against the iso copy)."""
    if model_id == "resource":
        return {
            "required": {"saleable_volume": "quantity", "realized_price": "revenue_per_unit"},
            "optional": {"other_revenue": "revenue"},
        }
    if model_id == "unit_sales":
        return {
            "required": {"units": "quantity", "unit_revenue": "revenue_per_unit"},
            "optional": {"timing_factor": "ratio", "other_revenue": "revenue"},
        }
    if model_id == "subscription":
        return {
            "required": {"average_customers": "quantity", "revenue_per_customer": "revenue_per_unit"},
            "optional": {"timing_factor": "ratio", "usage_revenue": "revenue"},
        }
    if model_id == "usage_platform":
        return {
            "required": {"eligible_activity": "activity", "monetization_rate": "revenue_per_activity"},
            "optional": {"fixed_revenue": "revenue"},
        }
    raise KeyError(model_id)
