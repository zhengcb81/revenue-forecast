import os, sys, pathlib
base = sys.argv[1]
def probe(label, maker):
    p = os.path.join(base, label)
    try:
        maker(p)
    except Exception as e:
        print(label, "MKDIR FAIL", e); return
    try:
        with open(os.path.join(p, "f.txt"), "w") as fh:
            fh.write("x")
        print(label, "WRITE OK")
    except Exception as e:
        print(label, "WRITE FAIL", e)
probe("m700", lambda p: os.mkdir(p, 0o700))
probe("m777", lambda p: os.mkdir(p, 0o777))
probe("mdefault", lambda p: os.mkdir(p))
probe("pathlib700", lambda p: pathlib.Path(p).mkdir(mode=0o700))
