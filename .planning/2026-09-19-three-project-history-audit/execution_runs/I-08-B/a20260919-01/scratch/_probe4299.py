import hashlib, sys
from pathlib import Path
review = Path(sys.argv[1]).read_bytes()
B = b"<<<BEGIN REVIEWER VERDICT (verbatim, round 3)>>>\n"
E = b"\n<<<END REVIEWER VERDICT (verbatim, round 3)>>>\n"
raw = review[review.index(B)+len(B): review.index(E)]
print("raw bytes", len(raw), hashlib.sha256(raw).hexdigest()[:8])
cands = {
  "raw_minus_last_byte": raw[:-1],
  "raw_linewise_strip_both": b"\n".join([l for l in raw.split(b"\n")][1:-1]),
  "raw_split_join_drop_first_last_empty": b"\n".join(raw.split(b"\n")[1:-1]),
  "raw_strip_one_leading_and_two_trailing": raw.lstrip(b"\n"),
}
for k,v in cands.items():
    print(k, len(v), hashlib.sha256(v).hexdigest()[:8])
