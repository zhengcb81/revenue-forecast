# pre-correction pack runs (review finding P3-5)

Archive of the ORIGINAL ecovery/precorrection/pack_stdout.txt and pack_stderr.txt.

Observed facts:
- pack_stderr.txt carried mtime 03:46:39-40 and was 0 bytes;
- pack_stdout.txt carried mtime 03:50:24-29, so at least TWO pack invocations happened
  during the r1 evidence build and the earlier stdout was overwritten in place.

Inference (NOT a verified fact): the 03:46 pair is the first pack attempt and the 03:50 pair is
a second, later pack; the earlier stdout content is not recoverable because the file was
overwritten rather than appended. r2 writes pack logs under pack_runs/ with explicit run
indexes (see pack_runs/run*_pack_*.txt) so this cannot recur.

Nothing here affects any expectation, verdict or frozen hash.
