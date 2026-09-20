import io
import os
import sys

attempt = sys.argv[1]
wb = io.open(os.path.join(attempt, "scripts", "write_binding.py"), encoding="utf-8").read()
m31_start = wb.index('"M31": {')
m31_end = wb.index('"declared_optional": []},', m31_start)
block = wb[m31_start:m31_end]
print("m31 block bytes", len(block))
print("block has True:", '"card_text_required_matches_registry": True' in block)
print("block has seven:", 'net_revenue_per_unit"],' in block)
print("file has live False:", '"card_text_required_matches_registry": False' in wb)
print("required_list count:", wb.count('"card_text_required_list"'))
print("banner:", "M31 CARD-TEXT CONSTANT CORRECTED" in wb)
print("--- m31 block tail ---")
print(block[-700:])
