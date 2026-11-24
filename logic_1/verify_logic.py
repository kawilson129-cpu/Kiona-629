"""Offline Logic 1 source decisions and existing isolated regression execution."""
import argparse
import ast
from contextlib import redirect_stderr, redirect_stdout
import csv
from datetime import datetime, timezone
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import sys
from types import SimpleNamespace
from unittest.mock import patch
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
EVIDENCE = ROOT / "evidence"
BACKEND = REPO / "derexi-policy-pilot/backend"


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def function(tree, name):
    return next(node for node in tree.body if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name==name)


def source_trees():
    return {name:ast.parse((BACKEND/(name+".py")).read_text(encoding="utf-8-sig")) for name in ("main","security","messaging")}


def branch_node(tree):
    return next(node for node in ast.walk(function(tree,"list_notifications")) if isinstance(node,ast.If) and any(
        isinstance(part,ast.Assign) and any(isinstance(target,ast.Name) and target.id=="kind" for target in part.targets)
        and isinstance(part.value,ast.Constant) and part.value.value=="triage" for part in node.body))


def pure_checks():
    trees = source_trees()
    rows = []
    def record(name, actual, expected, inputs):
        rows.append({"name":name,"status":"PASS" if actual==expected else "FAIL", "inputs":inputs,"expected":expected,"actual":actual})
    guard = function(trees["security"],"require_owner_or_admin").body[0].test
    guard_code = compile(ast.Expression(guard),str(BACKEND/"security.py"),"eval")
    with (ROOT/"assignment_3_boolean_logic/owner-admin-truth-table.csv").open() as file:
        for row in csv.DictReader(file):
            actor = SimpleNamespace(is_admin=bool(int(row["A_admin"])),is_policy_owner=bool(int(row["O_owner"])))
            actual = eval(guard_code,{"identity":actor})
            record("RBAC "+row["A_admin"]+row["O_owner"],
                   {"deny":bool(actual),"allow":not bool(actual),"equivalent_deny":not actor.is_admin and not actor.is_policy_owner},
                   {"deny":bool(int(row["DENY"])),"allow":bool(int(row["ALLOW"])),"equivalent_deny":bool(int(row["DENY"]))},row)
    feedback = function(trees["main"],"create_feedback")
    node = next(node for node in feedback.body if isinstance(node,ast.If) and isinstance(node.test,ast.BoolOp) and isinstance(node.test.op,ast.Or))
    feedback_code = compile(ast.Expression(node.test),str(BACKEND/"main.py"),"eval")
    with (ROOT/"assignment_3_boolean_logic/feedback-access-truth-table.csv").open() as file:
        for row in csv.DictReader(file):
            actor = SimpleNamespace(user_id=8,is_admin=bool(int(row["A_admin"])))
            conversation = SimpleNamespace(user_id=8 if int(row["S_self"]) else 9) if int(row["C_conversation"]) else None
            actual = eval(feedback_code,{"identity":actor,"conversation":conversation})
            record("Feedback "+row["C_conversation"]+row["S_self"]+row["A_admin"],
                   {"deny":bool(actual),"allow":not bool(actual),"equivalent_allow":bool(int(row["C_conversation"])) and
                    (bool(int(row["S_self"])) or actor.is_admin)},
                   {"deny":bool(int(row["DENY"])),"allow":bool(int(row["ALLOW"])),"equivalent_allow":bool(int(row["ALLOW"]))},row)
    chain = branch_node(trees["messaging"])
    chain_code = compile(ast.Module(body=[chain],type_ignores=[]),str(BACKEND/"messaging.py"),"exec")
    samples = [
        ("N1 triage precedence",True,2,None,3,"Responder","Assignee",{"kind":"triage","actor":"Requester"}),
        ("N2 new assignment",False,8,8,None,None,"Assignee",{"kind":"assigned","actor":"Requester"}),
        ("N3 reply sender",False,8,9,2,"Responder","Assignee",{"kind":"reply","actor":"Responder"}),
        ("N4 assignee fallback",False,8,9,1,None,"Assignee",{"kind":"reply","actor":"Assignee"}),
        ("N5 requester fallback",False,8,None,1,None,None,{"kind":"reply","actor":"Requester"}),
        ("N6 admin assigned to self",True,2,2,0,None,"Assignee",{"kind":"assigned","actor":"Requester"}),
    ]
    notification_rows = []
    for name,admin,uid,assigned,count,sender,assignee,expected in samples:
        row={"assigned_to":assigned,"reply_count":count,"requester_name":"Requester","last_reply_sender_name":sender,"assignee_name":assignee}
        namespace={"row":row,"identity":SimpleNamespace(is_admin=admin,user_id=uid)}
        exec(chain_code,namespace)
        actual={"kind":namespace["kind"],"actor":namespace["actor"]}
        inputs={"row":row,"caller":{"is_admin":admin,"user_id":uid},"precondition":"caller-scoped unread row"}
        record(name,actual,expected,inputs)
        notification_rows.append(rows[-1])
    # Execute the actual two-stage /ask confidence gate, not PostgreSQL retrieval.
    main = trees["main"]
    selected = [node for node in main.body if (isinstance(node,ast.Assign) and any(isinstance(target,ast.Name) and target.id in
        {"CONFIDENCE_THRESHOLD","GENERIC_STOPWORDS"} for target in node.targets)) or
        (isinstance(node,ast.FunctionDef) and node.name in {"contains_keyword","substantive_keywords"})]
    namespace={"re":re}
    exec(compile(ast.Module(body=selected,type_ignores=[]),str(BACKEND/"main.py"),"exec"),namespace)
    ask=function(main,"ask")
    numeric=next(node for node in ask.body if isinstance(node,ast.Assign) and any(isinstance(target,ast.Name) and target.id=="confident" for target in node.targets))
    evidence=next(node for node in ask.body if isinstance(node,ast.If) and isinstance(node.test,ast.Name) and node.test.id=="confident")
    gate=compile(ast.Module(body=[numeric,evidence],type_ignores=[]),str(BACKEND/"main.py"),"exec")
    for name,score,title,question,expected in [
        ("P1 boundary evidence",.22,"Protect confidential data","confidential data",True),
        ("P2 below boundary",.21999,"Protect confidential data","confidential data",False),
        ("P3 unrelated high score",.9,"Remote access","wire threshold",False),
        ("P4 generic words only",.9,"Policy guidance","what is the policy",False),
        ("P5 empty results",0,None,"confidential data",False),
    ]:
        top={"title":title,"body":"Synthetic policy text."} if title is not None else None
        namespace.update({"results":[top] if top else [],"top_score":score,"top":top,"question":question})
        exec(gate,namespace)
        record(name,bool(namespace["confident"]),expected,{"score":score,"title":title,"question":question})
    result={"timestamp":datetime.now(timezone.utc).isoformat(),"mode":"Original AST expressions/branch fragment executed unchanged; synthetic inputs; no app import or mocks of decision results",
            "passed":sum(row["status"]=="PASS" for row in rows),"failed":sum(row["status"]=="FAIL" for row in rows),"cases":rows}
    (EVIDENCE/"decision-results.json").write_text(json.dumps(result,indent=2)+"\n")
    (ROOT/"assignment_4_conditional_logic/sample-results.json").write_text(json.dumps({"scope":"Synthetic inputs; actual original classification branch, not HTTP response examples","cases":notification_rows},indent=2)+"\n")
    print(f'Source decisions: {result["passed"]} PASS / {result["failed"]} FAIL')
    return result["failed"]


def child_suite(which):
    # All patches affect this child only; no config files are read or changed.
    environment={"DATABASE_URL":"postgresql+psycopg2://offline:offline@127.0.0.1:1/offline", "OPENAI_API_KEY":"",
                 "DEREXI_ENV":"test","DEREXI_DEV_AUTH":"1","DEREXI_DEV_USER_IDS":"", "DEREXI_INCIDENT_AI":"off","DEREXI_OUTBOUND_EMAIL":"off"}
    os.environ.update(environment)
    attempts=[]
    def network_blocked(*args,**kwargs):
        attempts.append("Network call blocked")
        raise AssertionError("External network forbidden in Logic 1 verification")
    sys.path.insert(0,str(BACKEND/"tests"))
    sys.path.insert(0,str(BACKEND))
    filename="test_week7_messaging.py" if which=="week7" else "test_week10_integration.py"
    stdout,stderr=io.StringIO(),io.StringIO()
    failure=None
    module=None
    try:
        with redirect_stdout(stdout),redirect_stderr(stderr),patch("dotenv.load_dotenv",return_value=False), \
             patch.object(socket.socket,"connect",network_blocked),patch.object(socket.socket,"connect_ex",network_blocked), \
             patch("socket.create_connection",network_blocked):
            spec=importlib.util.spec_from_file_location("logic_existing_suite",BACKEND/"tests"/filename)
            module=importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            code=module.main_test() if which=="week7" else module.run()
            if code not in (None,0):
                failure="Existing suite returned nonzero status"
    except Exception as error:
        failure=type(error).__name__+": "+str(error)
    raw=getattr(module,"RESULTS",[]) if which=="week7" else getattr(module,"checks",[])
    rows=[{"name":row[0],"pass":row[1]} for row in raw] if which=="week7" else [{"name":row["name"],"pass":row["pass"]} for row in raw]
    if failure:
        rows.append({"name":"Suite execution completed: "+failure,"pass":False})
    def redacted(value):
        return re.sub(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+", "[REDACTED TEST TOKEN]",value)
    result={"suite":filename,"timestamp":datetime.now(timezone.utc).isoformat(),"python":sys.version.split()[0],
            "passed":sum(row["pass"] for row in rows),"failed":sum(not row["pass"] for row in rows),"checks":rows,
            "scope":"Existing real in-process routes; isolated SQLite with PostgreSQL syntax adapter; search no-match stub; synthetic development identities; AI/outbound off; dotenv loader mocked; network forbidden",
            "network_attempts":attempts,"stdout":redacted(stdout.getvalue()),"stderr":redacted(stderr.getvalue())}
    print(json.dumps(result))
    return bool(result["failed"] or not rows or attempts)


def regressions():
    interpreter=REPO/"derexi-policy-pilot/.venv/bin/python"
    if not interpreter.exists():
        (EVIDENCE/"regression-summary.json").write_text(json.dumps({"status":"NOT VERIFIED","reason":"Existing project interpreter unavailable; no dependencies installed."},indent=2)+"\n")
        return 0
    results=[]
    for suite in ("week7","week10"):
        process=subprocess.run([str(interpreter),"-B",str(Path(__file__).resolve()),"--child-suite",suite],cwd=REPO,text=True,capture_output=True,timeout=45)
        try:
            result=json.loads(process.stdout)
        except json.JSONDecodeError:
            result={"suite":suite,"passed":0,"failed":1,"status":"FAIL","reason":"Child suite did not produce a result record","stderr":process.stderr[:1000]}
        result["command"]=f"derexi-policy-pilot/.venv/bin/python -B logic_1/verify_logic.py --child-suite {suite}"
        result["exit_code"]=process.returncode
        (EVIDENCE/(suite+"-results.json")).write_text(json.dumps(result,indent=2)+"\n")
        (EVIDENCE/(suite+"-transcript.txt")).write_text(result.get("stdout","")+result.get("stderr",""))
        results.append(result)
        print(f'{suite}: {result["passed"]} PASS / {result["failed"]} FAIL')
    summary={"timestamp":datetime.now(timezone.utc).isoformat(),"status":"PASS" if all(not row["failed"] and not row["exit_code"] for row in results) else "FAIL",
             "passed":sum(row["passed"] for row in results),"failed":sum(row["failed"] for row in results),"suites":[{key:row[key] for key in ("suite","passed","failed","exit_code")} for row in results]}
    (EVIDENCE/"regression-summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    return int(summary["status"]!="PASS")


def artifact_checks():
    checks=[]
    def check(name,condition,detail=None):
        checks.append({"name":name,"status":"PASS" if condition else "FAIL","detail":detail})
    folders=["assignment_1_algorithms","assignment_2_flowcharts","assignment_3_boolean_logic","assignment_4_conditional_logic"]
    check("Four requested course deliverables",sorted(path.name for path in ROOT.glob("assignment_*") if path.is_dir())==folders)
    for folder in folders:
        check(folder+" README and evidence",all((ROOT/folder/name).is_file() and len((ROOT/folder/name).read_text().split())>75 for name in ("README.md","evidence.md")))
    algorithm=(ROOT/folders[0]/"algorithm.md").read_text()
    numbered=[int(value) for value in re.findall(r"^(\d+)\. ",algorithm,re.M)]
    check("Algorithm has fourteen ordered steps, exceeding six",numbered==list(range(1,15)))
    check("Algorithm identifies inputs, outputs, source, branches and cleanup",all(text in algorithm for text in ("Inputs:","Outputs:","Source mapping","Confident branch","Clarification branch","finally","0.22")))
    diagrams={}
    def reaches(start,target,graph):
        seen=set();pending=[start]
        while pending:
            current=pending.pop()
            if current==target:return True
            if current not in seen:
                seen.add(current);pending.extend(graph.get(current,[]))
        return False
    for path in ROOT.glob("assignment_*/*.mmd"):
        declarations={};edges=[];errors=[]
        lines=path.read_text().strip().splitlines()
        if lines[0]!="flowchart TD":errors.append("Unsupported header")
        wrappers=[("([", "])","terminator"),("[[", "]]","predefined_process"),("[(", ")]","data_store"),
                  ("[/", "/]","input_output"),("{", "}","decision"),("[", "]","process")]
        for line in lines[1:]:
            match=re.fullmatch(r"\s*(.*?)\s*-->\s*(?:\|([^|]+)\|\s*)?(.*?)\s*",line)
            if not match:errors.append(line);continue
            endpoints=[]
            for fragment in (match[1],match[3]):
                node=re.fullmatch(r"([A-Za-z][A-Za-z0-9_]*)(.*)",fragment.strip())
                if not node:errors.append(fragment);continue
                identifier,shape=node.groups();endpoints.append(identifier)
                if shape:
                    family=next((family for left,right,family in wrappers if shape.startswith(left) and shape.endswith(right)),None)
                    if not family:errors.append(fragment)
                    if identifier in declarations and declarations[identifier][0]!=shape:errors.append("Conflicting node "+identifier)
                    declarations[identifier]=(shape,family)
            if len(endpoints)==2:edges.append((endpoints[0],endpoints[1],match[2]))
        missing={node for edge in edges for node in edge[:2]}-declarations.keys()
        graph={node:[target for source,target,_ in edges if source==node] for node in declarations}
        check(path.name+" supported structural subset",not errors,errors)
        check(path.name+" declared node references",not missing,sorted(missing))
        check(path.name+" all nodes on a Start-to-Stop path",bool(declarations) and all(reaches("START",node,graph) and reaches(node,"STOP",graph) for node in declarations))
        decisions=[node for node,(_,family) in declarations.items() if family=="decision"]
        check(path.name+" true/false decision branches",bool(decisions) and all(
            {label for source,_,label in edges if source==node}=={"True","False"} for node in decisions))
        diagrams[path.name]={"nodes":len(declarations),"edges":len(edges),"symbol_families":sorted({family for _,family in declarations.values()}),
                             "declarations":declarations,"edges_detail":edges}
    policy=diagrams["policy-assistance.mmd"]
    check("A2 has six distinct symbol families",len(policy["symbol_families"])==6,policy["symbol_families"])
    policy_edges=policy["edges_detail"]
    required_edges=[("SCORE","OWNER","False"),("SCORE","KEYWORDS","True"),("KEYWORDS","OWNER","False"),
                    ("KEYWORDS","CONTEXT","True"),("INCIDENT","SAFETY","True"),("INCIDENT","STAGE","False"),
                    ("USABLE","FALLBACK","False"),("USABLE","ANSWER","True"),("CLEANUP","STOP",None)]
    check("A2 matches A1 evidence, incident, fallback and cleanup paths",all(edge in policy_edges for edge in required_edges))
    check("A2 Start and Stop are actual terminators",all(policy["declarations"][node][1]=="terminator" for node in ("START","STOP")))
    trees=source_trees();chain=branch_node(trees["messaging"])
    check("A4 source genuinely contains if, elif and else",isinstance(chain.orelse[0],ast.If) and bool(chain.orelse[0].orelse))
    original=(BACKEND/"messaging.py").read_text()
    check("A4 source excerpt matches original conditional exactly",ast.get_source_segment(original,chain) in (ROOT/folders[3]/"source-conditional.txt").read_text())
    conditional=(ROOT/folders[3]/"pseudocode.txt").read_text()
    check("A4 pseudocode preserves scoped unread precondition, branch order and fallback",all(text in conditional for text in
          ("PRECONDITION", "IF row.assigned_to IS NONE AND identity.is_admin", "ELIF", "ELSE", "first truthy", "20 items", "100 rows")))
    results=load(EVIDENCE/"decision-results.json")
    check("All 23 source decisions passed in actual execution",results["passed"]==23 and results["failed"]==0)
    check("Twelve Boolean cases include source and equivalent truth decisions",sum(row["name"].startswith(("RBAC","Feedback")) for row in results["cases"])==12 and all(
        row["status"]=="PASS" and any(key.startswith("equivalent_") for key in row["actual"])
        for row in results["cases"] if row["name"].startswith(("RBAC","Feedback"))))
    samples=load(ROOT/folders[3]/"sample-results.json")
    check("Six conditional samples are actual successful extracted-branch cases",len(samples["cases"])==6 and all(row["status"]=="PASS" for row in samples["cases"]))
    regression=load(EVIDENCE/"regression-summary.json")
    check("Existing regression results reconcile: 73 + 42 = 115",regression["status"]=="PASS" and regression["passed"]==115 and regression["failed"]==0)
    for suite in ("week7","week10"):
        record=load(EVIDENCE/(suite+"-results.json"))
        check(suite+" no network attempt and successful process",record["network_attempts"]==[] and record["exit_code"]==0)
    for source in load(EVIDENCE/"source-manifest.json")["sources"]:
        path=REPO/source["path"]
        check("Original hash unchanged: "+source["path"],path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest()==source["sha256"])
    source_map=load(EVIDENCE/"source-map.json")
    check("All source references have valid line ranges",all(1<=reference["start"]<=reference["end"]<=len((REPO/reference["path"]).read_text(encoding="utf-8-sig").splitlines()) for group in source_map.values() for reference in group))
    broken=[];fences=[];total=0
    for path in ROOT.rglob("*.md"):
        text=path.read_text()
        if sum(line.startswith("```") for line in text.splitlines())%2:fences.append(str(path.relative_to(ROOT)))
        for destination in re.findall(r"\[[^\]\n]*\]\(([^)\n]+)\)",text):
            link=urlsplit(destination)
            if link.scheme:continue
            total+=1;target=(path.parent/unquote(link.path)).resolve()
            if not target.exists() and target!=EVIDENCE/"artifact-results.json":broken.append(str(path.relative_to(ROOT))+" -> "+destination)
    check("All local evidence/source/navigation links resolve",not broken,{"checked":total,"broken":broken})
    check("Markdown code fences balanced",not fences,fences)
    syntax=[]
    for path in ROOT.glob("*.py"):
        try:compile(path.read_text(),str(path),"exec")
        except SyntaxError as error:syntax.append(str(error))
    check("Verification script syntax valid without bytecode writes",not syntax,syntax)
    git=subprocess.run(["git","status","--porcelain","-z","--untracked-files=all"],cwd=REPO,text=True,capture_output=True,check=True)
    changed=[entry[3:] for entry in git.stdout.split("\0") if entry]
    check("Changes confined to existing Logic 1 course",all(path.startswith("logic_1/") for path in changed),{"paths":len(changed),"outside_course":[path for path in changed if not path.startswith("logic_1/")]})
    result={"timestamp":datetime.now(timezone.utc).isoformat(),"scope":"Offline file, source, graph-subset and reference checks; not official Mermaid parsing or image export",
            "passed":sum(row["status"]=="PASS" for row in checks),"failed":sum(row["status"]=="FAIL" for row in checks),"checks":checks,
            "diagrams":{name:{key:value for key,value in details.items() if key in ("nodes","edges","symbol_families")} for name,details in diagrams.items()},
            "mermaid_engine_parse":"NOT VERIFIED; unavailable","image_export":"NOT GENERATED; renderer unavailable"}
    (EVIDENCE/"artifact-results.json").write_text(json.dumps(result,indent=2)+"\n")
    print(f'Artifacts: {result["passed"]} PASS / {result["failed"]} FAIL; {total} local links')
    for row in checks:
        if row["status"]=="FAIL":print(row)
    return result["failed"]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--regressions",action="store_true")
    parser.add_argument("--child-suite",choices=("week7","week10"))
    parser.add_argument("--documents-only",action="store_true")
    args=parser.parse_args()
    if args.child_suite:
        raise SystemExit(child_suite(args.child_suite))
    if args.documents_only:
        raise SystemExit(bool(artifact_checks()))
    failed=pure_checks()
    if args.regressions:
        failed+=regressions()
    raise SystemExit(bool(failed))


if __name__=="__main__":
    main()
