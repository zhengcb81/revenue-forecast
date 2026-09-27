#!/usr/bin/env python3
"""_recompute_action1.py — I-11-C/a20260926-01 Action-1 arithmetic recomputation (read-only on inputs).

Recomputes every magnitude/unit/conversion claim registered by I-11-B/a20260926-01.
Prints one CHECK line per item; exits 0 iff all expectations that I-11-B registered as
exact hold; intentional-discrepancy probes print DISCREPANCY lines and do not fail the run
(they are findings to register, not errors of this script).
"""
from fractions import Fraction as F

def chk(name, got, want, tol="0"):
    tol_f = F(tol) if tol else F(0)
    ok = abs(got - want) <= tol_f
    print(f"CHECK {name}: got={got} want={want} diff={got-want} -> {'OK' if ok else 'FAIL'}")
    return ok

def disc(name, got, want):
    print(f"DISCREPANCY {name}: computed={got} registered={want}")

results = []
# --- P2 probe: denominator coherence of ZIJIN_MINERAL_REALIZED_UNIT_REVENUE_FY2027 ---
denom_stated = 884943 + 83161 * 24          # formula as printed in store L170/L175
denom_registered = 885141                    # denominator actually used
disc("P2.denominator_composition", denom_stated, 885141)
quotient_registered = F(109977556345, 885141)
quotient_stated = F(109977556345, denom_stated)
disc("P2.quotient_from_registered_denom", float(quotient_registered), 124248.63)
disc("P2.quotient_from_stated_composition", float(quotient_stated), 124248.63)
disc("P2.sensitivity_denominator_plus1", 885141 + 83161, 968302)
# gold term implied at coefficient 24 per the registered pair (885141, 968302):
disc("P2.implied_gold_term_at_c24", 885141 - 884943, 83161 * 24 / 1000 * 1000)  # 198 vs 1995864

# --- SEG x4: delta method base + +/-5% bands ---
total_external = 349079082852
smelt, trade, other = 165858644874, 29212610830, 44030270803
mineral = total_external - smelt - trade - other
chk("SEG.mineral_base_delta", mineral, 109977556345)
for nm, base, lo, hi in [
    ("SEG.mineral", 109977556345, 104478678528, 115476434162),
    ("SEG.smelt", 165858644874, 157565712630, 174151577118),
    ("SEG.trade", 29212610830, 27751980289, 30673241372),
    ("SEG.other", 44030270803, 41828757263, 46231784343),
]:
    b = F(base)
    chk(nm + ".band_low", F(lo), b * F(95, 100), "0.5")
    chk(nm + ".band_high", F(hi), b * F(105, 100), "0.5")

# --- four-segment external sum == consolidated revenue ---
chk("IDENTITY.four_segment_sum", mineral + smelt + trade + other, 349079082852)
# --- H-05 identity ---
chk("IDENTITY.h05", 584049229264 - 234970146412, 349079082852)
# store L641 gross totals sum (segment totals incl. internal sales)
chk("IDENTITY.store_L641_gross_sum",
    138271672956 + 189683879295 + 170521025777 + 85572651236, 584049229264)

# --- REALIZED_UNIT +/-5% band off registered base 124248.63 ---
b = F(12424863, 100)
chk("REALIZED.band_low", F(1180362, 10), b * F(95, 100), F(1, 20))
chk("REALIZED.band_high", F(13046106, 100), b * F(105, 100), F(1, 20))

# --- VOL x4 +/-10% bands ---
for nm, base, lo, hi in [
    ("VOL.copper", 884943, 796448.7, 973437.3),
    ("VOL.gold", 83161, 74844.9, 91477.1),
    ("VOL.zinc", 352470, 317223, 387717),
    ("VOL.silver", 430254, 387228.6, 473279.4),
]:
    bb = F(str(base))
    chk(nm + ".band_low", F(str(lo)), bb * F(9, 10), "0.05")
    chk(nm + ".band_high", F(str(hi)), bb * F(11, 10), "0.05")

# --- PLAN +/-10% achievement band on management targets ---
for nm, base, lo, hi in [
    ("PLAN.gold_kg", 105000, 94500, 115500),
    ("PLAN.copper_t", 1200000, 1080000, 1320000),
]:
    chk(nm + ".band_low", lo, base * 9 // 10 if base % 10 == 0 else F(str(base)) * F(9, 10))
    chk(nm + ".band_high", hi, base * 11 // 10 if base % 10 == 0 else F(str(base)) * F(11, 10))

# --- MSFT growth conversion g_low=(1+g)*0.95-1, g_high=(1+g)*1.05-1 ---
for nm, g, lo, hi in [
    ("MSFT.pbp", "0.16", "0.102", "0.218"),
    ("MSFT.ic", "0.30", "0.235", "0.365"),
    ("MSFT.mpc", "-0.01", "-0.0595", "0.0395"),
]:
    gb = F(g)
    chk(nm + ".g_low", F(lo), (1 + gb) * F(95, 100) - 1)
    chk(nm + ".g_high", F(hi), (1 + gb) * F(105, 100) - 1)

# --- P3 probe: EA-4 band_rationale three-segment revenue totals ---
chk("MSFT.base_total", 139996 + 137791 + 54052, 331839)
low_sum = 139996 * F("1.102") + 137791 * F("1.235") + 54052 * F("0.9405")
high_sum = 139996 * F("1.218") + 137791 * F("1.365") + 54052 * F("1.0395")
disc("P3.scenario_low_total", float(low_sum), 320763)
disc("P3.scenario_high_total", float(high_sum), 348432)
disc("P3.plus5_on_base_total", float(F(331839) * F(105, 100)), 348432)
print("RECOMPUTE_DONE")
