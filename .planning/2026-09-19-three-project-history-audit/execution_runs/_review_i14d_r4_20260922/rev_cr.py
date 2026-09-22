import sys
from pathlib import Path

for p in sys.argv[1:]:
    b = Path(p).read_bytes()
    cr = b.count(b"\x0d")
    lf = b.count(b"\x0a")
    print(f"{p}\n    bytes={len(b)} CR={cr} LF={lf} CRCR={b.count(bytes([13,13]))}")
