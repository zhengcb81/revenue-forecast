from pathlib import Path
import hashlib, json, os, shutil, stat, subprocess, sys, tempfile, time
root=Path(__file__).resolve().parents[3]
out=Path(__file__).resolve().parent
phase=sys.argv[1]
owned=Path(tempfile.mkdtemp(prefix="p7-rf-scope-"+phase+"-"))
env={k:v for k,v in os.environ.items() if not k.startswith("GIT_")}
env.update(PYTHONDONTWRITEBYTECODE="1",PYTEST_DISABLE_PLUGIN_AUTOLOAD="1",PYTHONUTF8="1",REVENUE_PUBLICATION_REGISTRY=str(owned/"registry/publications.jsonl"))
runs=[]
def run(label,args):
    argv=[sys.executable,"-X","utf8","-B",*args]
    start=time.perf_counter()
    result=subprocess.run(argv,cwd=root,env=env,text=True,encoding="utf-8",capture_output=True,timeout=60)
    (out/(label+".log")).write_bytes((result.stdout+result.stderr).encode("utf-8"))
    runs.append({"label":label,"argv":argv,"exit_code":result.returncode,"seconds":time.perf_counter()-start})
    print(label,result.returncode,result.stdout,result.stderr,flush=True)
    return result
receipt={"schema_version":"p7-rf-scope-run/1","phase":phase,"owned_temp":str(owned),"provider_calls":0,"model_calls":0,"new_cost_usd":0}
try:
    pytest_args=["-m","pytest","-p","pytest_timeout","-p","no:cacheprovider","--basetemp",str(owned/"pytest"),"--timeout=60","-q"]
    if phase=="red":
        run("red",pytest_args+["tests/test_research_support_diagnostics.py"])
    elif phase=="green":
        run("ruff",["-m","ruff","check","--no-cache","scripts/research_support_diagnostics.py","tests/test_research_support_diagnostics.py"])
        run("mypy",["-m","mypy","--cache-dir",str(owned/"mypy"),"scripts/research_support_diagnostics.py"])
        run("responsibility",pytest_args+["tests/test_research_support_diagnostics.py","tests/test_scoped_calibration_support.py","tests/test_research_evidence_roles.py"])
    else:
        raise ValueError(phase)
finally:
    def retry(fn,p,err):
        assert Path(p).resolve().is_relative_to(owned.resolve())
        os.chmod(p,stat.S_IWRITE|stat.S_IREAD)
        fn(p)
    assert owned.resolve().is_relative_to(Path(tempfile.gettempdir()).resolve())
    shutil.rmtree(owned,onexc=retry)
    receipt.update(runs=runs,owned_temp_removed=not owned.exists())
    (out/(phase+".json")).write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
