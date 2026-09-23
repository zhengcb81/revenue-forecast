import ast, hashlib, sys, tokenize, io, difflib

before, after = sys.argv[1], sys.argv[2]
b = open(before, "rb").read()
a = open(after, "rb").read()
print("before_sha", hashlib.sha256(b).hexdigest())
print("after_sha ", hashlib.sha256(a).hexdigest())
bt = b.decode("utf-8")
at_ = a.decode("utf-8")
diff = list(difflib.unified_diff(bt.splitlines(keepends=True), at_.splitlines(keepends=True),
                                 fromfile="before(37a3eeae)", tofile="after(91a6dc32)"))
sys.stdout.writelines(diff)
print("DIFF_LINES", len(diff))

# comment-only check: strip COMMENT/NL-style tokens, compare the rest
def norm(src):
    toks = []
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        if tok.type in (tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE,
                        tokenize.INDENT, tokenize.DEDENT, tokenize.ENDMARKER):
            continue
        toks.append((tok.type, tok.string))
    return toks

nb, na = norm(bt), norm(at_)
print("TOKENS_EQUAL_IGNORING_COMMENTS", nb == na, len(nb), len(na))
ab, aa = ast.parse(bt), ast.parse(at_)
print("AST_EQUAL", ast.dump(ab) == ast.dump(aa))
compile(bt, before, "exec")
compile(at_, after, "exec")
print("COMPILE_OK both")
