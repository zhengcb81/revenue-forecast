"""Split lock.py `_process_identity` into a dispatcher + two verbatim platform helpers.

Complexity ratchet (FC-1204, owner §四十二 裁定一, 2026-09-27): split only; behaviour unchanged.
"""
import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

PATH = r"C:\Users\郑曾波\Projects\company-wiki\src\company_wiki\source_catalog\lock.py"
NOTE = ("Complexity ratchet (FC-1204, owner §四十二 裁定一, 2026-09-27): "
        "split only; behaviour unchanged.")

with io.open(PATH, "r", encoding="utf-8", newline="") as fh:
    text = fh.read()

lines = text.splitlines(keepends=True)


def strip_eol(line: str):
    if line.endswith("\r\n"):
        return line[:-2], "\r\n"
    if line.endswith("\n"):
        return line[:-1], "\n"
    return line, ""


def find(pred, start=0):
    for i in range(start, len(lines)):
        if pred(strip_eol(lines[i])[0]):
            return i
    raise SystemExit("marker not found")


eol = "\r\n" if any(strip_eol(l)[1] == "\r\n" for l in lines) else "\n"

i_def = find(lambda s: s == "def _process_identity(pid: int) -> dict[str, object]:")
i_nt = find(lambda s: s == '    if os.name == "nt":', i_def)
i_try = find(lambda s: s == "    try:", i_nt)
i_end = find(lambda s: s.startswith("def _pid_is_live"), i_nt)

win_body = lines[i_nt + 1:i_try]
posix_body = lines[i_try:i_end]
while posix_body and strip_eol(posix_body[-1])[0] == "":
    posix_body.pop()


def dedent4(ls):
    out = []
    for l in ls:
        core, e = strip_eol(l)
        if core.startswith("    "):
            core = core[4:]
        out.append(core + (e or eol))
    return out


win_dedented = dedent4(win_body)

new_block = []
new_block.append("def _process_identity(pid: int) -> dict[str, object]:" + eol)
new_block.append("    # " + NOTE + eol)
new_block.append("    # Platform dispatch only: the former bodies live in the two" + eol)
new_block.append("    # helpers below, verbatim and in the same order." + eol)
new_block.append("    if pid <= 0:" + eol)
new_block.append("        return {" + eol)
new_block.append('            "live": False,' + eol)
new_block.append('            "creation_time": None,' + eol)
new_block.append('            "executable": None,' + eol)
new_block.append('            "verification": "not_live",' + eol)
new_block.append("        }" + eol)
new_block.append('    if os.name == "nt":' + eol)
new_block.append("        return _windows_process_identity(pid)" + eol)
new_block.append("    return _posix_process_identity(pid)" + eol)
new_block.append(eol)
new_block.append(eol)
new_block.append("def _windows_process_identity(pid: int) -> dict[str, object]:" + eol)
new_block.append("    # " + NOTE + eol)
new_block.extend(win_dedented)
new_block.append(eol)
new_block.append(eol)
new_block.append("def _posix_process_identity(pid: int) -> dict[str, object]:" + eol)
new_block.append("    # " + NOTE + eol)
new_block.extend(posix_body)
new_block.append(eol)
new_block.append(eol)

out = lines[:i_def] + new_block + lines[i_end:]

with io.open(PATH, "w", encoding="utf-8", newline="") as fh:
    fh.write("".join(out))
print("lock.py rewritten:", i_def, i_nt, i_try, i_end)
