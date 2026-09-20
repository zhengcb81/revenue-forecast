"""Reproduce audit-only analyst arithmetic, never publish a revenue-forecast artifact."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
d = json.loads((ROOT / 'research_assumptions.json').read_text(encoding='utf-8'))
base = d['reported_base']
actual = d['actual_h1_2026']
prior_h2 = {k: base[k]-d['actual_h1_2025'][k] for k in base}
assert abs(sum(base.values())-457286.687) < 1e-7
assert abs(sum(actual.values())-208063.227) < 1e-7

def forecast_half(a, prior):
    return {
        'Smartphones': a['phone_units_million'] * a['phone_net_asp_cny'],
        'IoT': prior['IoT'] * (1+a['iot_yoy']),
        'Internet': prior['Internet'] * (1+a['internet_yoy']),
        'SmartphoneOther': prior['SmartphoneOther'] * (1+a['smartphone_other_yoy']),
        'EVAI': a['ev_deliveries'] * a['ev_net_asp_cny'] / 1e6 + a['ev_other_revenue_million'],
    }

out={'artifact_role':d['artifact_role'],'as_of_date':d['as_of_date'], 'unit':'CNY million',
     'formal_output':False,'method':'Analyst scratch arithmetic, not revenue_forecast.py; no publication receipt, no calibrated probability or accuracy claim',
     'scenarios':{}}
for name,s in d['scenarios'].items():
    h2=forecast_half(s['h2_2026'], prior_h2)
    p26={k:actual[k]+h2[k] for k in base}
    p27=forecast_half(s['fy2027'],p26)
    p28=forecast_half(s['fy2028'],p27)
    paths=[p26,p27,p28]
    totals=[sum(p.values()) for p in paths]
    out['scenarios'][name]={'condition':s['condition'],'h2_2026':h2,
        'h2_2026_yoy':{k:h2[k]/prior_h2[k]-1 for k in base},
        'annual_revenue':dict(zip(map(str,d['years']),totals)),
        'segment_paths':dict(zip(map(str,d['years']),paths)),
        'cagr_2025_2028':(totals[-1]/sum(base.values()))**(1/3)-1,
        'fy2026_annual_phone_units_million_rounded':d['actual_h1_2026_phone_units_million_rounded']+s['h2_2026']['phone_units_million'],
        'fy2026_annual_ev_deliveries':d['actual_h1_2026_ev_deliveries']+s['h2_2026']['ev_deliveries'],
        'h2_2026_ev_delivery_yoy':s['h2_2026']['ev_deliveries']/(d['actual_fy2025_ev_deliveries']-d['actual_h1_2025_ev_deliveries'])-1}
out['checks']={'base_reconciles':True,'h1_reconciles':True,
    'annual_order_non_crossing':all(out['scenarios']['low']['annual_revenue'][str(y)]<=out['scenarios']['base']['annual_revenue'][str(y)]<=out['scenarios']['high']['annual_revenue'][str(y)] for y in d['years']),
    'h1_fixed_across_scenarios':True,
    'source_capture_ready':False,'formal_engine_passed':False}
(ROOT / 'research_scratch_results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lines=['# 小米：假设研究算表（非正式预测）','','**未通过 revenue_forecast.py；不可当作发布结果或下游 invest-* 输入。所有未来数值均为待证伪的分析师假设，尚未校准。**', '',
       '此算表只把已实现 H1 锁定，检查 H2 隐含要求、量价乘法和条件路径。金额为 CNY million。','',
       '| 情景 | FY2026 | FY2027 | FY2028 | 2025–2028 CAGR |','|---|---:|---:|---:|---:|']
for n,s in out['scenarios'].items():
    lines.append(f"| {n} | {s['annual_revenue']['2026']:,.1f} | {s['annual_revenue']['2027']:,.1f} | {s['annual_revenue']['2028']:,.1f} | {s['cagr_2025_2028']:.1%} |")
lines += ['', '## 2026 H2 反推与年度约束', '', '| 情景 | 全年手机百万台（近似） | H2手机收入同比 | H2 IoT同比 | H2互联网同比 | 全年EV交付 | H2 EV交付同比 | H2 EV综合收入同比 |', '|---|---:|---:|---:|---:|---:|---:|---:|']
for n,s in out['scenarios'].items():
    y=s['h2_2026_yoy'];lines.append(f"| {n} | {s['fy2026_annual_phone_units_million_rounded']:.1f} | {y['Smartphones']:.1%} | {y['IoT']:.1%} | {y['Internet']:.1%} | {s['fy2026_annual_ev_deliveries']:,} | {s['h2_2026_ev_delivery_yoy']:.1%} | {y['EVAI']:.1%} |")
lines += ['', '## 五曲线逐年候选收入', '', '| 情景 | 年 | 手机 | IoT | 互联网 | 手机其他 | EV/AI |','|---|---|---:|---:|---:|---:|---:|']
for n,s in out['scenarios'].items():
    for y,p in s['segment_paths'].items():
        lines.append(f"| {n} | {y} | "+' | '.join(f'{p[k]:,.1f}' for k in base)+' |')
lines += ['', '## 使用限制', '',
    '- H1金额用官方附注千元换算，不使用管理讨论舍入数；H2与以后期间的量价/增长率是独立标识的分析师假设。',
    '- EV/AI是精确披露的整体曲线；H2开始才显式交付×ASP+其他，未伪造精确基年EV/AI细分。other包括售后、附件、金融及AI，不能全部当AI。',
    '- FY2027/28的海外渠道、车型/工厂爬坡与广告单价缺独立样本、订单/产能和付费数据；当前范围不能称投资委员会可采用的预测。',
    '- low/base/high是条件路径，不代表概率分位数；未来期间区间没有回测覆盖率。',
    '- 未做正式置信评分、敏感性引擎验证、发布注册或不可变快照；已知正式来源阻断另见根代理日志。',
    '- 模板提供六曲线仅用于模型路由；本算表改用五曲线保留已披露的精确基年边界。',
    '- 单期量价压力必须同时考虑销量和价格弹性，不能把所有局部敏感性相加为联合风险。']
(ROOT / 'research_scenarios_NOT_FORMAL.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'written':'research_scratch_results.json + research_scenarios_NOT_FORMAL.md', 'checks':out['checks'], 'annual_totals':{n:s['annual_revenue'] for n,s in out['scenarios'].items()}},ensure_ascii=False))
