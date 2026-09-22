"""CPU burner for the GATE-TIMEOUT-1200 load arms.

A pure busy loop: it consumes one logical processor at 100% until killed.
No I/O, no allocation growth (integer wraps), no sleep. Exactly 8 of these
run concurrently during each arm, per the card's oracle.
"""

import itertools
import time

_start = time.time()
for i in itertools.count():
    x = i % 1000003
    if x * x > 1 << 62:  # keep the interpreter honest about doing "work"
        pass
