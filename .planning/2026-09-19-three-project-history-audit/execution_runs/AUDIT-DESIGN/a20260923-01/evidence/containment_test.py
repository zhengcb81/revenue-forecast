"""AUDIT-DESIGN decisive test for the D1 disposition: is the registered-version byte
sequence preserved VERBATIM inside rulings_transcribed_2026-09-22.md?

- OPEN-4 / OPEN-5: registered hash == live ruling.md hash, so test full-byte containment
  of ruling.md inside the transcription (byte-substring search).
- OPEN-6: live ruling.md has post-registration dated appends; test containment of its
  longest prefix found in the transcription, report divergence offset and the byte
  length of the preserved region.

Read-only; prints to stdout.
Usage: python -X utf8 -B containment_test.py <transcribed.md> <open4.md> <open5.md> <open6.md>
"""
import hashlib
import sys
from pathlib import Path


def first_divergence(a: bytes, b: bytes) -> int:
    n = min(len(a), len(b))
    for i in range(n):
        if a[i] != b[i]:
            return i
    return n


def main() -> int:
    trans = Path(sys.argv[1]).read_bytes()
    print(f"transcription bytes={len(trans)} sha256={hashlib.sha256(trans).hexdigest()}")
    for label, p in (("OPEN-4", sys.argv[2]), ("OPEN-5", sys.argv[3]), ("OPEN-6", sys.argv[4])):
        blob = Path(p).read_bytes()
        h = hashlib.sha256(blob).hexdigest()
        pos = trans.find(blob)
        print(f"\n{label}: file bytes={len(blob)} sha256={h}")
        print(f"  full containment in transcription: {'YES at offset ' + str(pos) if pos >= 0 else 'NO'}")
        if pos < 0:
            # how much of the file is preserved verbatim somewhere? grow the prefix
            lo, hi = 0, len(blob)
            best = 0
            while lo <= hi:
                mid = (lo + hi) // 2
                if trans.find(blob[:mid]) >= 0:
                    best = mid
                    lo = mid + 1
                else:
                    hi = mid - 1
            at = trans.find(blob[:best]) if best else -1
            print(f"  longest verbatim prefix preserved = {best} bytes at transcription offset {at}")
            if best < len(blob):
                dv = first_divergence(blob, trans[at:at + len(blob)]) if at >= 0 else -1
                print(f"  first divergence vs transcription at file-offset {dv}")
                if at >= 0 and best < len(blob):
                    tail_at = trans.find(blob[best + 8 : best + 208]) if best + 208 < len(blob) else -1
                    print(f"  probe of file bytes [{best+8}:{best+208}] found in transcription at: {tail_at}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
