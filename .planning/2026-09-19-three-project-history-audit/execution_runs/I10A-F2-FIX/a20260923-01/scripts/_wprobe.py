import os, sys, tempfile, pathlib
base = sys.argv[1]
d = os.path.join(base, "py_created_dir")
os.makedirs(d, exist_ok=True)
try:
    with open(os.path.join(d, "py_file.txt"), "w") as fh:
        fh.write("hello")
    print("python write into python-created dir: OK")
except Exception as e:
    print("python write into python-created dir: FAIL", e)
try:
    td = tempfile.mkdtemp(dir=base)
    with open(os.path.join(td, "tf.txt"), "w") as fh:
        fh.write("x")
    print("tempfile mkdtemp write: OK", td)
except Exception as e:
    print("tempfile mkdtemp write: FAIL", e)
print("cwd writable test:")
try:
    with open(os.path.join(base, "py_root.txt"), "w") as fh:
        fh.write("x")
    print("  OK")
except Exception as e:
    print("  FAIL", e)
