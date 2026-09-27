# _VALUE IS DEAD CODE (REM-05 / F-REV-D-02; annotated 2026-09-23 by REGISTRY-CLOSURE
# a20260923-01). This constant is referenced NOWHERE at runtime: _AUTH_PATTERN
# inlines `(?P<value>...|_AUTH_SCHEME_SPLIT|_AUTH_BARE_VALUE)` below and the
# assignment path is the hand-written scanner that uses _VALUE_STOP_CHARS.
# The load-bearing C13 narrowing is that scanner loop, NOT this constant.
# Deleting this constant outright is behaviour-neutral (probe evidence:
# execution_runs/REGISTRY-CLOSURE/a20260923-01/evidence/rem05_behavior_identity.txt).
# Do NOT "clean up" _BARE_VALUE/_AUTH_BARE_VALUE/the scanner assuming this
# constant keeps the fix alive: it never had runtime effect (that is F-REV-D-02).
_VALUE = r"(?P<value>" + _QUOTED_VALUE + r"|" + _BARE_VALUE + r")"