import hashlib
import io
import sys

report_path = sys.argv[1]
review_path = sys.argv[2]
heading = sys.argv[3]

rep = io.open(report_path, encoding="utf-8", newline="").read()
print("report CR count", rep.count("\r"), "LF count", rep.count("\n"))
start = rep.index(heading)
fence = rep.index("```markdown", start)
body_start = rep.index("\n", fence) + 1
body_end = rep.index("```", body_start)
block = rep[body_start:body_end]
print("raw block CR count", block.count("\r"), "ends with newline:", block.endswith("\n"))
norm = block.replace("\r\n", "\n").replace("\r", "\n")
if not norm.endswith("\n"):
    norm += "\n"
print("norm bytes", len(norm.encode("utf-8")))
print("norm sha", hashlib.sha256(norm.encode("utf-8")).hexdigest())
print("norm tail repr:", repr(norm[-40:]))

text = io.open(review_path, encoding="utf-8", newline="").read()
print("review CR count", text.count("\r"), "ends with newline:", text.endswith("\n"))
print("review last 80 repr:", repr(text[-80:]))
