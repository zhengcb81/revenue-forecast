"""Fix the leaked concatenation artifact in the pin prose, then re-pin and verify."""
import hashlib
import os

ATTEMPT = (r"C:\Users\郑曾波\Projects\revenue-forecast\.planning"
           r"\2026-09-19-three-project-history-audit\execution_runs"
           r"\B5-plan-level-remediation\a20260921-01")
REPORT = os.path.join(ATTEMPT, "reviewer_report.md")
MARK = "## 7. Report pin".encode("utf-8")

with open(REPORT, "rb") as fh:
    raw = fh.read()
idx = raw.index(MARK)
payload = raw[:idx]
pbytes = len(payload)
psha = hashlib.sha256(payload).hexdigest()

tail = (
    "## 7. Report pin (self-excluding)\n"
    "\n"
    "The pin covers every byte of this file **before** this section. Verify by hashing\n"
    "`reviewer_report.md[0 : " + str(pbytes) + "]` -- **not** the whole file: a whole-file hash of a\n"
    "document that contains its own hash cannot close.\n"
    "\n"
    "```\n"
    "payload_bytes  " + str(pbytes) + "\n"
    "payload_sha256 " + psha + "\n"
    "```\n"
    "\n"
    "Verification:\n"
    "\n"
    "```python\n"
    "import hashlib\n"
    "raw = open('reviewer_report.md','rb').read()\n"
    "i = raw.index(b'## 7. Report pin')\n"
    "print(len(raw[:i]), hashlib.sha256(raw[:i]).hexdigest())\n"
    "```\n"
    "\n"
    "*(The implementer should re-verify on receipt; if the two values do not reproduce, the\n"
    "report has been altered after review and the verdict is void.)*\n"
)

with open(REPORT, "wb") as fh:
    fh.write(payload + tail.encode("utf-8"))

with open(REPORT, "rb") as fh:
    raw2 = fh.read()
i2 = raw2.index(MARK)
check = hashlib.sha256(raw2[:i2]).hexdigest()
print("leaked concat artifact present:", b"str(pbytes)" in raw2)
print("whole file bytes   = %d" % len(raw2))
print("payload pinned     = %d bytes / %s" % (pbytes, psha))
print("payload recomputed = %d bytes / %s" % (len(raw2[:i2]), check))
print("PIN REPRODUCES     = %s" % (check == psha and len(raw2[:i2]) == pbytes))
