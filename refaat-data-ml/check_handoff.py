"""Run the recipient's actual examples, tests and offline reproduction checks. No external packages."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from time import perf_counter

ROOT=Path(__file__).resolve().parent

def sha(path: Path) -> str:
    with path.open("rb") as src:
        return hashlib.file_digest(src, "sha256").hexdigest()

def require(ok: bool, why: str) -> None:
    if not ok:
        raise RuntimeError(why)

def matching_json(first, second, where="root") -> None:
    if isinstance(first,float) and type(second) in (int,float):
        require(math.isclose(first,second,rel_tol=1e-12,abs_tol=1e-12),f"Numeric difference: {where}")
    elif isinstance(first,dict) and isinstance(second,dict):
        require(first.keys()==second.keys(),f"Changed fields: {where}")
        for key in first:
            matching_json(first[key], second[key], where+"."+key)
    elif isinstance(first,list) and isinstance(second,list):
        require(len(first)==len(second),f"Changed length: {where}")
        for i,(lhs,rhs) in enumerate(zip(first,second)):
            matching_json(lhs,rhs,f"{where}[{i}]")
    else:
        require(first==second,f"Difference: {where}")

def guide_example(guide: Path) -> str:
    blocks=re.findall(r"^```python\r?\n(.*?)^```\s*$",guide.read_text(encoding="utf-8"),flags=re.S|re.M)
    require(len(blocks)==1,f"Expected 1 runnable Python example in {guide.name}")
    return blocks[0]

def verify_delivery() -> dict:
    manifest=json.loads((ROOT/"PACKAGE_MANIFEST.json").read_bytes())
    role=manifest["package"]
    require(role in {"project","ml","backend"},"Unrecognized package")
    evidence={"package":role,"dataset_version":manifest["dataset_version"],
              "started_utc":datetime.now(timezone.utc).isoformat(),"python":platform.python_version(),
              "platform":platform.system()+" "+platform.release(),"commands":[],"checks":{}}
    def run(name,args,stdin=None):
        start=perf_counter()
        result=subprocess.run([sys.executable,"-B",*args],cwd=ROOT,env={**os.environ,"PYTHONIOENCODING":"utf-8",
                              "PYTHONPATH":""},input=stdin,capture_output=True,text=True,encoding="utf-8",timeout=180)
        output=(result.stdout+result.stderr).replace(str(ROOT),"<package>")
        command={"name":name,"exit_code":result.returncode,"seconds":round(perf_counter()-start,2)}
        evidence["commands"].append(command)
        require(result.returncode==0,name+" failed:\n"+output[-4500:])
        if "unittest" in args:
            tests=re.findall(r"^test_\w+ \(([^)]+)\) \.\.\. ok\s*$",output,flags=re.M)
            found=re.search(r"Ran (\d+) tests? in ",output)
            require(found is not None and int(found[1])==len(tests) and len(tests)>0 and
                    re.search(r"^OK\s*$",output,flags=re.M) is not None,name+": failed, skipped or unaccounted tests")
            command.update(tests_run=len(tests),failed=0,skipped=0,passed_tests=tests)
        return result.stdout
    with tempfile.TemporaryDirectory(dir=ROOT) as scratch:
        temp=Path(scratch)
        run("verify_package",["verify_package.py"])
        evidence["shipped_files_verified"]=len(manifest["files"])
        run("public_unit_and_consumer_suite",["-m","unittest","discover","-s","tests","-v"])
        if role=="project":
            run("optimized_pipeline_guards",["-O","-m","unittest","discover","-s","tests","-p","test_pipeline.py","-v"])
            build=temp/"rebuilt"
            run("rebuild_from_originals",["rebuild.py","--output",str(build)])
            exact={}
            for name in list((ROOT/"data").glob("*"))+[ROOT/"provenance/source_manifest.json",ROOT/"reports/seasonal_screen_bounds.csv",ROOT/"reports/pipeline.json"]:
                if name.is_file():
                    relative=name.relative_to(ROOT)
                    exact[relative.as_posix()]=sha(name)==sha(build/relative)
            require(all(exact.values()),f"Rebuilt outputs differ from shipped outputs: {exact}")
            evidence["checks"]["byte_identical_rebuilt_files"]=exact
        if role in {"project","ml"}:
            folder=ROOT/"ML_HANDOFF" if role=="project" else ROOT
            run("ml_onboarding_python_example",["-"],guide_example(folder/"START_HERE.md"))
            loaded=json.loads(run("ml_example",["-m","climate_data.ml_example","--data","data"]))
            require((loaded["training_rows"],loaded["validation_rows"],loaded["origins"],loaded["prediction_rows"])==
                    (6574,1096,36,504),"ML handoff input counts differ")
            out=temp/"baseline"
            run("ml_baseline",["-m","climate_data.evaluation","--data","data","--output",str(out)])
            same={}
            for name in ("calendar_reference.csv","scored_predictions.csv","metrics.json"):
                same[name]=sha(out/name)==sha(folder/"reference"/name)
            require(all(same.values()),f"Baseline exports differ from reference: {same}")
            with (out/"scored_predictions.csv").open(encoding="utf-8",newline="") as file:
                dates={(r["issue"],r["target_date"]) for r in csv.DictReader(file)}
            require(len(dates)==252,"Diagnostic dates differ")
            scores=json.loads((out/"metrics.json").read_bytes())["metrics"]
            evidence["checks"]["ml"]={"loader":loaded,"unique_issue_target_date_pairs":len(dates),
                                      "byte_identical_baseline_files":same,"metrics":scores}
        if role in {"project","backend"}:
            run("optimized_kb_guards",["-O","-m","unittest","discover","-s","tests","-p","test_kb.py","-v"])
            folder=ROOT/"BACKEND_HANDOFF" if role=="project" else ROOT
            out=temp/"example.json"
            run("backend_request_response",["-m","climate_data.backend_example","--data","data","--out",str(out)])
            run("backend_onboarding_python_example",["-"],guide_example(folder/"START_HERE.md"))
            generated=json.loads(out.read_bytes())
            matching_json(json.loads((folder/"example_response.json").read_bytes()),generated)
            replay=generated["comparison"]
            require(replay["eligible_anchors"]==[2015,2016] and replay["exclusions"][0]["anchor"]==2024,
                    "Unreproduced example replay")
            evidence["checks"]["backend"]={"matches_shipped_example":True,
                "byte_identical_example":sha(out)==sha(folder/"example_response.json"),
                "eligible_anchors":replay["eligible_anchors"],"excluded_anchors":replay["exclusions"],
                "climate_methods_exercised":7,"application_backend_exercised":False}
            kb_status=json.loads(run("agricultural_kb_loader",["-m","agricultural_kb"]))
            require(kb_status["rules"]==27 and kb_status["scientific_status_counts"]["VERIFIED"]==18,
                    "Agricultural source counts differ")
            require(kb_status["locally_approved_rules"]==0 and kb_status["enforceable_rules"]==0,
                    "Research evidence incorrectly activated")
            consumer=json.loads(run("combined_backend_consumer",["-m","examples.backend_p0"]))
            require(consumer["planner_constraints"]==[] and consumer["kb_status"]==kb_status,
                    "Consumer approval contract differs")
            evidence["checks"]["agricultural_kb"]={"status":kb_status["status"],"rules":27,
                "scientifically_verified":18,"locally_approved":0,"enforceable":0,
                "actual_team_backend_tested":False}
    evidence["status"]="VERIFIED AND TESTED"
    evidence["finished_utc"]=datetime.now(timezone.utc).isoformat()
    return evidence

if __name__=="__main__":
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--output",type=Path,required=True)
    destination=cli.parse_args().output
    if destination.exists():
        raise FileExistsError("Use a new result file")
    result=verify_delivery()
    destination.parent.mkdir(parents=True,exist_ok=True)
    with destination.open("x",encoding="utf-8",newline="\n") as f:
        json.dump(result,f,indent=2,allow_nan=False)
        f.write("\n")
    print(f"{result['package']} • {result['status']} • {len(result['commands'])} commands; evidence: {destination}")

