import re

base = ".planning/2026-09-19-three-project-history-audit/execution_runs/OPEN5-S5-IND-RULING/a20260926-01/_work/extract/"
en = open(base + "s5_ind_attempt08_fitz.txt", encoding="utf-8").read()
print("count 457,286.7 =", en.count("457,286.7"))
idxs = [m.start() for m in re.finditer(re.escape("457,286.7"), en)]
for i in idxs:
    print("ctx:", repr(en[max(0, i - 60):i + 40]))
en2 = en.replace("457,286.7", "457,286.9", 1)
ne = re.sub(r"\s+", " ", en2)
m = re.search(r"Total revenue ([\d,]+\.\d) 100\.0%", ne)
print("after replace, regex match:", m.group(1) if m else None)
m0 = re.search(r"Total revenue ([\d,]+\.\d) 100\.0%", re.sub(r"\s+", " ", en))
print("before replace, regex match:", m0.group(1) if m0 else None)
