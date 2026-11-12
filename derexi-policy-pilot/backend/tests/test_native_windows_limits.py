"""Native Windows Job Object probes; no app, database or network imports."""
import json
import os
from pathlib import Path
import subprocess
import sys

out=Path(os.environ['DEREXI_SPRINT_EVIDENCE'])
checks=[]
source=Path(__file__).resolve().parents[1]/'document_limits.py'
def worker(code,timeout=14):
    return subprocess.run([sys.executable,'-I','-c',"import runpy,sys; runpy.run_path(sys.argv[1])['limit_parser'](); "+code,str(source)],capture_output=True,timeout=timeout)
if sys.platform=='win32':
    result=worker("x=bytearray(1024*1024); print('bounded success')")
    checks.append({'name':'Native Windows bounded parser worker succeeds','pass':result.returncode==0 and b'bounded success' in result.stdout})
    result=worker("x=bytearray(512*1024*1024); print('unsafe allocation')")
    checks.append({'name':'Native Windows 256 MiB Job Object blocks excess allocation','pass':result.returncode!=0 and b'unsafe allocation' not in result.stdout})
    try:
        result=worker("exec('while True: pass')")
        checks.append({'name':'Native Windows Job Object stops CPU overrun','pass':result.returncode!=0})
    except subprocess.TimeoutExpired:
        checks.append({'name':'Native Windows Job Object stops CPU overrun','pass':False})
report={'platform':sys.platform,'passed':sum(c['pass'] for c in checks),'failed':sum(not c['pass'] for c in checks),'blocked':0 if checks else 3,'checks':checks}
(out/'windows-native-results.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2));sys.exit(bool(report['failed']))
