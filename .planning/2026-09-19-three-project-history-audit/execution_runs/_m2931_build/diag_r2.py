import io
import os
import sys

attempt = sys.argv[1]
card = sys.argv[2]
wb = io.open(os.path.join(attempt, "scripts", "write_binding.py"), encoding="utf-8").read()
print("M31 CARD-TEXT CONSTANT CORRECTED :", "M31 CARD-TEXT CONSTANT CORRECTED" in wb)
print('"card_text_required_matches_registry": True :', '"card_text_required_matches_registry": True' in wb)
print('net_revenue_per_unit"], :', 'net_revenue_per_unit"],' in wb)
print("count of net_revenue_per_unit :", wb.count("net_revenue_per_unit"))
print("does NOT list :", "does NOT list" in wb)
print("occurrences of 'does NOT list':", wb.count("does NOT list"))
for index, line in enumerate(wb.split("\n"), start=1):
    if "does NOT list" in line:
        print("  line %d: %s" % (index, line))
tc = io.open(os.path.join(attempt, "evidence", card, "verdict_transcription_check.txt"),
             encoding="utf-8").read()
method_line = [line for line in tc.split("\n") if line.startswith("method: ")][0]
print("method line contains 'the report is CRLF':", "the report is CRLF" in method_line)
