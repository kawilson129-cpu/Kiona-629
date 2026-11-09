import json
from pulse.service import get_feed
feed=get_feed()
print(json.dumps(feed,indent=2))
assert feed["articles"],"No articles"
assert all(s["ok"] for s in feed["sources"].values()),feed["sources"]
assert all(a["url"].startswith("https://") for a in feed["articles"])
assert len({a["url"] for a in feed["articles"]})==len(feed["articles"])
