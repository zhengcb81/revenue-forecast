<!-- CORRECTION 2 declared quote-sample mini-GREEN; expected flags [12, 14]; source: authored by REM79-MECHANIZATION implementer; expectations frozen in oracle.md C2.3 before this file existed -->

<!-- payload 4: marker inside paired backticks -> expect NO flag -->
Frozen rule text lives in backticks: `every case must equal declared_expected_exception`.
<!-- payload 6: marker inside paired CJK corner brackets -> expect NO flag -->
引用如下：「全部卡均已登记在册」——照录不改。
<!-- payload 8: marker inside paired double quotes -> expect NO flag -->
Owner wrote: "没有域的断言按未验证处理" — verbatim.
<!-- payload 10: line starts with a quote-open char -> expect NO flag -->
> only the quoted text is repeated here.
<!-- payload 12: CONTROL spaced marker outside any quote, no domain -> expect FLAG -->
Final verdict for this sample: every gate must carry its note on the line.
<!-- payload 14: CONTROL marker after quotes closed, no domain -> expect FLAG -->
After the closing quote below, the reviewer wrote: '...' and all checks remained green.
