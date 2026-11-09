import sys,json
from pathlib import Path
from importlib import metadata
sys.path.insert(0,str(Path("derexi-policy-pilot/backend").resolve()))
import schemas
from pydantic import ValidationError
checks=[]
for cls,data in [
(schemas.FeedbackCreate,dict(message_id=1,rating="yes")),
(schemas.FeedbackCreate,dict(message_id=1,rating=True,comment="x"*50000)),
(schemas.IncidentCreate,dict(description="x"*50000)),
(schemas.AskRequest,dict(question=" ")),
(schemas.ClarificationReplyCreate,dict(body="x"*4001))]:
    try:
        cls(**data)
        checks.append(dict(model=cls.__name__,rejected=False))
    except ValidationError:
        checks.append(dict(model=cls.__name__,rejected=True))
packages=sorted([dict(name=d.metadata["Name"],version=d.version,requires=d.requires or []) for d in metadata.distributions()],key=lambda d:d["name"].lower())
Path("cyber_threats_vulnerabilities_2_final/followup/package-inventory.json").write_text(json.dumps(packages,indent=2))
print(json.dumps(dict(schema_checks=checks,packages=len(packages)),indent=2))
assert all(c["rejected"] for c in checks)
