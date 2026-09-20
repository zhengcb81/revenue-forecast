"""Independent audit arithmetic. Not a revenue-forecast publication."""
from pathlib import Path
import json

a=Path(__file__).parent
root=a.parent
x=json.loads((root/"XIAOMI/research_assumptions.json").read_text(encoding="utf-8"))
xout=json.loads((root/"XIAOMI/research_scratch_results.json").read_text(encoding="utf-8"))
m=json.loads((root/"MSFT/research_assumptions.draft.json").read_text(encoding="utf-8"))
result={"role":"independent_audit_arithmetic_not_published_forecast","xiaomi":{},"microsoft":{}}
for sc,sv in x["scenarios"].items():
    rev={}
    h2=sv["h2_2026"]
    rev[2026]={"Smartphones":x["actual_h1_2026"]["Smartphones"]+h2["phone_units_million"]*h2["phone_net_asp_cny"],"EVAI":x["actual_h1_2026"]["EVAI"]+h2["ev_deliveries"]*h2["ev_net_asp_cny"]/1e6+h2["ev_other_revenue_million"]}
    for key,field in [("IoT","iot_yoy"),("Internet","internet_yoy"),("SmartphoneOther","smartphone_other_yoy")]:
        rev[2026][key]=x["actual_h1_2026"][key]+(x["reported_base"][key]-x["actual_h1_2025"][key])*(1+h2[field])
    for y in (2027,2028):
        v=sv[f"fy{y}"]
        rev[y]={"Smartphones":v["phone_units_million"]*v["phone_net_asp_cny"],"EVAI":v["ev_deliveries"]*v["ev_net_asp_cny"]/1e6+v["ev_other_revenue_million"]}
        for key,field in [("IoT","iot_yoy"),("Internet","internet_yoy"),("SmartphoneOther","smartphone_other_yoy")]:
            rev[y][key]=rev[y-1][key]*(1+v[field])
    totals={str(y):sum(v.values()) for y,v in rev.items()}
    err={y:totals[y]-xout["scenarios"][sc]["annual_revenue"][y] for y in totals}
    terminal_delta=totals["2028"]-sum(x["reported_base"].values())
    ev_delta=rev[2028]["EVAI"]-x["reported_base"]["EVAI"]
    result["xiaomi"][sc]={"totals":totals,"difference_from_producer":err,"EVAI_terminal_increment":ev_delta,"company_terminal_increment":terminal_delta,"EVAI_share_of_increment":ev_delta/terminal_delta,"h2_ev_monthly_deliveries":h2["ev_deliveries"]/6,"h2_ev_monthly_vs_q2_2026":(h2["ev_deliveries"]/6)/(104199/3)-1}
for sc in ("low","base","high"):
    annual={2027:0,2028:0,2029:0}
    terminals={}
    for curve in m["curves"]:
        r=curve["FY2026_revenue"]
        for y,g in zip((2027,2028,2029),curve["annual_growth_assumptions"][sc]):
            r*=1+g
            annual[y]+=r
        terminals[curve["name"]]=r
    total=annual[2029]
    delta=total-331839
    azure_delta=terminals["Azure"]-101938
    result["microsoft"][sc]={"annual_totals":annual,"terminals":terminals,"company_cagr":(total/331839)**(1/3)-1,"company_increment":delta,"azure_share_of_increment":azure_delta/delta,"azure_terminal":terminals["Azure"],"azure_cloud_combined_share":(terminals["Azure"]+terminals["Microsoft 365 cloud"])/total}
result["microsoft"]["base"]["azure_all_year_growth_minus_5pp_delta"]=101938*(1+.35)*(1+.27)*(1+.20)-result["microsoft"]["base"]["azure_terminal"]
result["xiaomi"]["base"]["terminal_EV_delivery_minus10pct_delta"]=-.1*750000*230000/1e6
target=a/"independent_research_recalculation.json"
if target.exists():
    raise SystemExit("audit record already exists")
target.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(result,ensure_ascii=False,indent=2))
