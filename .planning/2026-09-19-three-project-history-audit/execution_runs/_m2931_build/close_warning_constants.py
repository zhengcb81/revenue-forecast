import argparse
import hashlib
import os
import py_compile

TARGETS = ("PACK_WARNING", "WRITE_BINDING_WARNING")


def sha256(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", required=True)
    args = parser.parse_args()
    path = os.path.abspath(args.path)
    with open(path, "r", encoding="utf-8") as handle:
        lines = handle.read().split("\n")
    before = sha256(path)
    closed = []
    for index, line in enumerate(lines):
        if line == '"""' and index > 0:
            for back in range(index - 1, max(-1, index - 80), -1):
                for name in TARGETS:
                    if lines[back].startswith(name + " = "):
                        lines[index] = line + "'''"
                        closed.append(name)
                        break
                else:
                    continue
                break
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines))
    print("closed constants:", sorted(set(closed)))
    print("sha256 %s -> %s" % (before[:16], sha256(path)[:16]))
    py_compile.compile(path, doraise=True)
    print("py_compile: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
