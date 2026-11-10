"""Fresh-process offline regression runner; preserves prior coursework evidence."""
import json,os,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
out=root.parent/'docs/governance-workspace/evidence';out.mkdir(parents=True,exist_ok=True)
env={**os.environ,'DEREXI_TEST_EVIDENCE_DIR':str(out/'regressions')}
results=[]
for name in ('test_document_intake','test_week8_governance','test_week7_messaging','test_week7_edges','test_week7_auth','test_pulse'):
 r=subprocess.run([sys.executable,str(root/'tests'/f'{name}.py')],cwd=root,env=env,capture_output=True,text=True)
 (out/f'{name}.log').write_text(r.stdout+r.stderr,encoding='utf-8')
 result={'suite':name,'exit_code':r.returncode,'tail':(r.stdout+r.stderr).splitlines()[-4:]};results.append(result);print(json.dumps(result),flush=True)
(out/'regression-summary.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
sys.exit(1 if any(r['exit_code'] for r in results) else 0)
