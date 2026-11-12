"""One scoped offline regression pass. New evidence only; never a live test runner."""
import contextlib
import importlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE));sys.path.insert(0,str(HERE.parent))
OUT=Path(os.environ['DEREXI_SPRINT_EVIDENCE'])

def child(name):
    # Each suite gets a fresh process and the existing DB/AI tripwire fixture.
    import messaging_fixture
    report={}
    if name=='support':
        m=importlib.import_module('test_support_assistance');m.run();items=m.checks
    elif name=='week10':
        m=importlib.import_module('test_week10_integration');m.run();items=m.checks
    elif name=='governance':
        m=importlib.import_module('test_week8_governance');m.run();items=m.checks
    elif name=='documents':
        m=importlib.import_module('test_document_intake');m.run();items=m.checks
    elif name=='security':
        m=importlib.import_module('test_week9_security');m.OUT=OUT/'security';m.run();items=[{'name':x['name'],'pass':x['status']=='PASS'} for x in m.checks]
    elif name=='jwt':
        m=importlib.import_module('test_week7_auth');items=[]
        for key,fn in sorted(vars(m).items()):
            if key.startswith('test_') and callable(fn):
                try:fn();items.append({'name':key,'pass':True})
                except Exception:items.append({'name':key,'pass':False})
    elif name=='pulse':
        m=importlib.import_module('test_pulse')
        for fn in ['test_date_parsing','test_text_helpers','test_classification','test_normalize','test_combined_feed','test_ranking','test_radar']:getattr(m,fn)()
        items=[{'name':str(x),'pass':True} for x in m.PASSED]+[{'name':str(x),'pass':False} for x in m.FAILED]
    elif name=='messaging':
        m=importlib.import_module('test_week7_messaging');m.main_test();items=[{'name':str(x[0]),'pass':bool(x[1])} for x in m.RESULTS]
    elif name=='edges':
        m=importlib.import_module('test_week7_edges');m.run();items=[{'name':'edge_'+str(i),'pass':bool(x)} for i,x in enumerate(m.RESULTS)]
    elif name=='resource_limits':
        m=importlib.import_module('test_document_limits');suite=unittest.defaultTestLoader.loadTestsFromModule(m)
        result=unittest.TextTestRunner(verbosity=2).run(suite)
        report={'passed':result.testsRun-len(result.failures)-len(result.errors)-len(result.skipped),
                'failed':len(result.failures)+len(result.errors),'blocked':len(result.skipped),
                'skipped':[{'test':str(t),'reason':reason} for t,reason in result.skipped]};items=[]
    else:raise ValueError(name)
    if not report:report={'passed':sum(bool(x['pass']) for x in items),'failed':sum(not x['pass'] for x in items),'blocked':0,'checks':items}
    (OUT/(name+'-results.json')).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return bool(report['failed'])

if __name__=='__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    focused='--support-only' in sys.argv
    if len(sys.argv)>1 and not focused:sys.exit(child(sys.argv[1]))
    results=[]
    for name in (['support'] if focused else ['support','week10','governance','documents','security','jwt','pulse','messaging','edges','resource_limits']):
        with (OUT/(name+'-run.txt')).open('w',encoding='utf-8') as log:
            try:
                p=subprocess.run([sys.executable,str(Path(__file__).resolve()),name],stdout=log,stderr=log,timeout=150)
                code=p.returncode
            except subprocess.TimeoutExpired:code=124
        path=OUT/(name+'-results.json')
        if path.exists():r=json.loads(path.read_text(encoding='utf-8'));r.pop('checks',None)
        else:r={'passed':0,'failed':1,'blocked':0,'error':'Suite interrupted; see isolated log'}
        results.append({'suite':name,'exit_code':code,**r});print(name,json.dumps(r),flush=True)
    summary={'native_platform':sys.platform,'python':sys.version.split()[0],'suites':results,
             'passed':sum(r['passed'] for r in results),'failed':sum(r['failed'] for r in results),'blocked':sum(r.get('blocked',0) for r in results)}
    (OUT/('focused-support-summary.json' if focused else 'regression-summary.json')).write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    sys.exit(1 if summary['failed'] else 0)
