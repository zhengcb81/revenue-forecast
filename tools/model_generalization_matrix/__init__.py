"""Model generalization matrix: a finite, repeatable stress-test matrix over the
native revenue engine's cross-mechanism combinations (M01-M08).

Engineering evidence only.  Every case runs the real draft engine and compares
against an independent hand-computed oracle.  ``source_truth_verified`` is always
false and ``economic_reasonableness`` is always ``not_evaluated``: this package
never asserts a buy-side conclusion.
"""

__all__ = ["oracle", "cases", "native", "bootstrap", "runner", "report", "run"]
